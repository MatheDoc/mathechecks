create or replace function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_tempo_days integer default null,
    p_included_check_ids text[] default array[]::text[],
    p_target_date date default null,
    p_target_source text default null,
    p_lernbereiche_meta jsonb default null
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    active_session_id uuid;
    effective_tempo_days integer;
    default_tempo_days integer := public.get_system_setting_integer('planning.default_session_tempo_days', 3);
    normalized_lernbereiche text[];
    normalized_excluded_check_ids text[];
    normalized_included_check_ids text[];
    normalized_target_date date := p_target_date;
    normalized_target_source text := nullif(trim(coalesce(p_target_source, '')), '');
    current_lernbereich_slug text;
    v_sort_index integer;
    v_gebiet text;
    v_start_status text;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_tempo_days is not null and p_tempo_days <= 0 then
        raise exception 'tempo_days must be positive';
    end if;

    if normalized_target_date is not null and normalized_target_date < current_date then
        raise exception 'target_date must be today or later';
    end if;

    if normalized_target_date is null then
        normalized_target_source := null;
    elsif normalized_target_source is null then
        normalized_target_source := 'explicit';
    elsif normalized_target_source not in ('explicit', 'suggested') then
        raise exception 'unsupported target_source';
    end if;

    select id
    into active_session_id
    from public.learning_sessions
    where user_id = current_user_id
      and status = 'active'
    for update;

    normalized_lernbereiche := array(
        select distinct slug
        from (
            select nullif(trim(lb.value), '') as slug
            from unnest(coalesce(p_lernbereiche, array[]::text[])) as lb(value)
        ) normalized
        where slug is not null
    );

    normalized_excluded_check_ids := array(
        select distinct check_id
        from (
            select nullif(trim(excluded.value), '') as check_id
            from unnest(coalesce(p_excluded_check_ids, array[]::text[])) as excluded(value)
        ) normalized
        where check_id is not null
    );

    normalized_included_check_ids := array(
        select distinct check_id
        from (
            select nullif(trim(included.value), '') as check_id
            from unnest(coalesce(p_included_check_ids, array[]::text[])) as included(value)
        ) normalized
        where check_id is not null
    );

    if coalesce(array_length(normalized_lernbereiche, 1), 0) = 0 then
        if active_session_id is not null then
            update public.learning_sessions
            set status = 'aborted',
                ended_at = coalesce(ended_at, now())
            where id = active_session_id
              and status = 'active';

            delete from public.session_feed_cursor
            where session_id = active_session_id;
        end if;

        return null;
    end if;

    effective_tempo_days := coalesce(p_tempo_days, default_tempo_days);

    if active_session_id is null then
        begin
            insert into public.learning_sessions (
                user_id,
                status,
                tempo_days,
                target_date,
                target_source
            )
            values (
                current_user_id,
                'active',
                effective_tempo_days,
                normalized_target_date,
                normalized_target_source
            )
            returning id into active_session_id;
        exception
            when unique_violation then
                raise exception 'An active learning session already exists';
        end;
    else
        update public.learning_sessions
        set tempo_days = effective_tempo_days,
            target_date = normalized_target_date,
            target_source = normalized_target_source,
            planning_revision = planning_revision + 1
        where id = active_session_id;

        delete from public.session_check_exclusions
        where session_id = active_session_id;

        delete from public.session_lernbereiche
        where session_id = active_session_id;

        perform public.clear_current_feed_cursor(active_session_id);
    end if;

    insert into public.session_lernbereiche (session_id, lernbereich_slug, sort_index, gebiet)
    select
        active_session_id,
        lb.slug,
        coalesce((meta_elem.val->>'sort_index')::integer, 0),
        coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), '')
    from unnest(normalized_lernbereiche) as lb(slug)
    left join lateral (
        select elem as val
        from jsonb_array_elements(coalesce(p_lernbereiche_meta, '[]'::jsonb)) as elem
        where elem->>'slug' = lb.slug
        limit 1
    ) as meta_elem on true;

    if coalesce(array_length(normalized_excluded_check_ids, 1), 0) > 0 then
        insert into public.session_check_exclusions (session_id, check_id)
        select active_session_id, check_id
        from unnest(normalized_excluded_check_ids) as excluded_checks(check_id);
    end if;

    delete from public.session_check_state
    where session_id = active_session_id
      and not (check_id = any(coalesce(normalized_included_check_ids, array[]::text[])));

    delete from public.session_flashcard_card_state
    where session_id = active_session_id
      and not (check_id = any(coalesce(normalized_included_check_ids, array[]::text[])));

    delete from public.session_flashcard_rounds
    where session_id = active_session_id
      and exists (
          select 1
          from public.session_flashcard_round_cards
          where session_flashcard_round_cards.round_id = session_flashcard_rounds.id
            and not (session_flashcard_round_cards.check_id = any(coalesce(normalized_included_check_ids, array[]::text[])))
      );

    delete from public.session_activity_state as activity
    where activity.session_id = active_session_id
      and activity.scope_type = 'lernbereich'
      and activity.activity_type in ('flashcards', 'start')
      and not (activity.lernbereich_slug = any(coalesce(normalized_lernbereiche, array[]::text[])));

    if coalesce(array_length(normalized_included_check_ids, 1), 0) > 0 then
        insert into public.session_check_state (
            session_id,
            check_id,
            current_step_key,
            current_step_status,
            last_outcome_key,
            last_completed_at
        )
        select
            active_session_id,
            included_check_id,
            'training',
            'due',
            null,
            null
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    update public.session_check_state scs
    set current_step_status = 'blocked'
    from public.session_lernbereiche slb
    where scs.session_id = active_session_id
      and slb.session_id = active_session_id
      and slb.lernbereich_slug = split_part(scs.check_id, '__', 2)
      and slb.gebiet <> ''
      and slb.sort_index > (
          select min(slb2.sort_index)
          from public.session_lernbereiche slb2
          where slb2.session_id = active_session_id
            and slb2.gebiet = slb.gebiet
      )
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'due';

    update public.session_check_state scs
    set current_step_status = 'due'
    from public.session_lernbereiche slb
    where scs.session_id = active_session_id
      and slb.session_id = active_session_id
      and slb.lernbereich_slug = split_part(scs.check_id, '__', 2)
      and (
          slb.gebiet = ''
          or slb.sort_index = (
              select min(slb2.sort_index)
              from public.session_lernbereiche slb2
              where slb2.session_id = active_session_id
                and slb2.gebiet = slb.gebiet
          )
      )
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'blocked';

    foreach current_lernbereich_slug in array normalized_lernbereiche loop
        select slb.sort_index, slb.gebiet
        into v_sort_index, v_gebiet
        from public.session_lernbereiche slb
        where slb.session_id = active_session_id
          and slb.lernbereich_slug = current_lernbereich_slug;

        if v_gebiet is null or v_gebiet = '' then
            v_start_status := 'due';
        elsif v_sort_index = (
            select min(slb2.sort_index)
            from public.session_lernbereiche slb2
            where slb2.session_id = active_session_id
              and slb2.gebiet = v_gebiet
        ) then
            v_start_status := 'due';
        else
            v_start_status := 'blocked';
        end if;

        insert into public.session_activity_state (
            session_id,
            activity_key,
            activity_type,
            scope_type,
            lernbereich_slug,
            target_module_key,
            status,
            due_at,
            sort_bucket,
            sort_index,
            last_outcome_key
        )
        values (
            active_session_id,
            'lernbereich:' || current_lernbereich_slug || ':start',
            'start',
            'lernbereich',
            current_lernbereich_slug,
            'start',
            v_start_status,
            now(),
            5,
            0,
            null
        )
        on conflict (session_id, activity_key) do update
            set status = case
                    when session_activity_state.status = 'completed' then 'completed'
                    else excluded.status
                end,
                due_at = case
                    when session_activity_state.status = 'completed' then session_activity_state.due_at
                    else excluded.due_at
                end;

        perform public.refresh_flashcard_activity_for_lernbereich(active_session_id, current_lernbereich_slug);
    end loop;

    effective_tempo_days := case
        when p_tempo_days is not null then greatest(p_tempo_days, 1)
        when normalized_target_source = 'explicit' and normalized_target_date is not null
            then public.derive_learning_session_tempo_days(active_session_id, normalized_target_date, default_tempo_days)
        else greatest(default_tempo_days, 1)
    end;

    update public.learning_sessions
    set tempo_days = effective_tempo_days
    where id = active_session_id;

    perform public.replan_session(active_session_id);

    return active_session_id;
end;
$$;

drop function if exists public.pick_feed_cursor(uuid);

create function public.pick_feed_cursor(p_session_id uuid default null)
returns table (
    session_id uuid,
    current_activity_key text,
    activity_kind text,
    activity_type text,
    lernbereich_slug text,
    check_id text,
    step_key text,
    target_module_key text,
    available_from timestamptz,
    planned_from timestamptz,
    overdue_from timestamptz,
    effective_planned_from timestamptz,
    locked_until timestamptz,
    selected_at timestamptz,
    selection_reason text,
    next_available_from timestamptz,
    timing_status text
)
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid := p_session_id;
    cursor_row public.session_feed_cursor;
    current_item record;
    next_item record;
    has_current_item boolean := false;
    has_next_item boolean := false;
    next_waiting_from timestamptz;
    next_selection_reason text;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if resolved_session_id is null then
        select id
        into resolved_session_id
        from public.learning_sessions
        where user_id = current_user_id
          and status = 'active'
        order by started_at desc
        limit 1;
    else
        perform 1
        from public.learning_sessions
        where id = resolved_session_id
          and user_id = current_user_id
          and status = 'active';

        if not found then
            raise exception 'No active learning session found';
        end if;
    end if;

    if resolved_session_id is null then
        return;
    end if;

    perform public.replan_session(resolved_session_id);

    insert into public.session_feed_cursor (session_id)
    values (resolved_session_id)
    on conflict on constraint session_feed_cursor_pkey do nothing;

    select sfc.*
    into cursor_row
    from public.session_feed_cursor as sfc
    where sfc.session_id = resolved_session_id
    for update;

    if cursor_row.current_activity_key is not null then
        select *
        into current_item
        from public.feed_cursor_open_items(resolved_session_id)
        where activity_key = cursor_row.current_activity_key
        limit 1;

        has_current_item := found;

        if has_current_item
           and cursor_row.locked_until is not null
           and cursor_row.locked_until > now() then
            return query
            select
                resolved_session_id,
                current_item.activity_key,
                current_item.activity_kind,
                current_item.activity_type,
                current_item.lernbereich_slug,
                current_item.check_id,
                current_item.step_key,
                current_item.target_module_key,
                current_item.available_from,
                current_item.planned_from,
                current_item.overdue_from,
                current_item.effective_planned_from,
                cursor_row.locked_until,
                cursor_row.selected_at,
                cursor_row.selection_reason,
                null::timestamptz,
                case current_item.urgency_rank
                    when 0 then 'overdue'
                    when 1 then 'due'
                    else 'available'
                end::text;
            return;
        end if;
    end if;

    select *
    into next_item
    from public.feed_cursor_open_items(resolved_session_id)
    order by
        urgency_rank,
        coalesce(order_timestamp, 'infinity'::timestamptz),
        class_rank,
        step_depth desc,
        lernbereich_sort_index,
        check_order,
        sort_bucket,
        sort_index,
        activity_key
    limit 1;

    has_next_item := found;

    if has_next_item then
        next_selection_reason := case
            when cursor_row.current_activity_key is null then
                case when cursor_row.selected_at is null then 'initial' else 'auto_pick' end
            when not has_current_item then 'invalidated'
            when cursor_row.locked_until is not null and cursor_row.locked_until <= now() then 'lock_expired'
            else 'auto_pick'
        end;

        update public.session_feed_cursor as sfc
        set current_activity_key = next_item.activity_key,
            locked_until = now() + public.get_feed_cursor_lock_interval(),
            selected_at = now(),
            selection_reason = next_selection_reason
        where sfc.session_id = resolved_session_id;

        select sfc.*
        into cursor_row
        from public.session_feed_cursor as sfc
        where sfc.session_id = resolved_session_id;

        return query
        select
            resolved_session_id,
            next_item.activity_key,
            next_item.activity_kind,
            next_item.activity_type,
            next_item.lernbereich_slug,
            next_item.check_id,
            next_item.step_key,
            next_item.target_module_key,
            next_item.available_from,
            next_item.planned_from,
            next_item.overdue_from,
            next_item.effective_planned_from,
            cursor_row.locked_until,
            cursor_row.selected_at,
            cursor_row.selection_reason,
            null::timestamptz,
            case next_item.urgency_rank
                when 0 then 'overdue'
                when 1 then 'due'
                else 'available'
            end::text;
        return;
    end if;

    if cursor_row.current_activity_key is not null then
        perform public.clear_current_feed_cursor(resolved_session_id);
    end if;

    select min(next_core.effective_planned_from)
    into next_waiting_from
    from (
        select
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end as effective_planned_from
        from public.session_activity_state sas
        where sas.session_id = resolved_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'

        union all

        select
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end as effective_planned_from
        from public.session_check_state scs
        where scs.session_id = resolved_session_id
          and scs.current_step_status = 'due'
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
    ) as next_core
    where next_core.effective_planned_from is not null
      and next_core.effective_planned_from > now();

    if next_waiting_from is not null then
        return query
        select
            resolved_session_id,
            null::text,
            'waiting'::text,
            'waiting'::text,
            null::text,
            null::text,
            null::text,
            null::text,
            null::timestamptz,
            null::timestamptz,
            null::timestamptz,
            null::timestamptz,
            null::timestamptz,
            cursor_row.selected_at,
            cursor_row.selection_reason,
            next_waiting_from,
            null::text;
        return;
    end if;

    return;
end;
$$;

revoke all on function public.pick_feed_cursor(uuid) from public;
revoke all on function public.pick_feed_cursor(uuid) from anon;
grant execute on function public.pick_feed_cursor(uuid) to authenticated;