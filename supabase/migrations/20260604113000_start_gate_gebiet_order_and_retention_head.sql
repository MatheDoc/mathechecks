alter table public.session_lernbereiche
    add column if not exists gebiet_order integer not null default 0;

update public.session_lernbereiche
set gebiet_order = case gebiet
    when 'analysis' then 1
    when 'stochastik' then 2
    when 'lineare-algebra' then 3
    else 0
end
where gebiet_order = 0;

create or replace function public.is_lernbereich_start_ready(
    p_session_id uuid,
    p_lernbereich_slug text
)
returns boolean
language plpgsql
stable
security definer
set search_path = public
as $$
declare
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    current_gebiet text;
    current_sort_index integer;
begin
    if p_session_id is null or normalized_lernbereich_slug is null then
        return false;
    end if;

    select slb.gebiet, slb.sort_index
    into current_gebiet, current_sort_index
    from public.session_lernbereiche slb
    where slb.session_id = p_session_id
      and slb.lernbereich_slug = normalized_lernbereich_slug;

    if not found then
        return false;
    end if;

    if current_gebiet is null or current_gebiet = '' then
        return true;
    end if;

    if not exists (
        select 1
        from public.session_lernbereiche predecessor_lernbereiche
        where predecessor_lernbereiche.session_id = p_session_id
          and predecessor_lernbereiche.gebiet = current_gebiet
          and predecessor_lernbereiche.sort_index < current_sort_index
    ) then
        return true;
    end if;

    return not exists (
        select 1
        from public.session_lernbereiche predecessor_lernbereiche
        join public.session_check_state scs
          on scs.session_id = p_session_id
         and public.check_id_lernbereich_slug(scs.check_id) = predecessor_lernbereiche.lernbereich_slug
        where predecessor_lernbereiche.session_id = p_session_id
          and predecessor_lernbereiche.gebiet = current_gebiet
          and predecessor_lernbereiche.sort_index < current_sort_index
          and scs.current_step_key <> 'check_completed'
          and not exists (
              select 1
              from public.session_check_exclusions sce
              where sce.session_id = p_session_id
                and sce.check_id = scs.check_id
          )
    );
end;
$$;

create or replace function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_activities_per_day numeric default null,
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
    current_activities_per_day numeric;
    effective_activities_per_day numeric;
    default_activities_per_day numeric := public.get_default_activities_per_day();
    normalized_lernbereiche text[];
    normalized_excluded_check_ids text[];
    normalized_included_check_ids text[];
    normalized_target_date date := p_target_date;
    normalized_target_source text := nullif(trim(coalesce(p_target_source, '')), '');
    current_lernbereich_slug text;
    v_start_status text;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_activities_per_day is not null and p_activities_per_day <= 0 then
        raise exception 'activities_per_day must be positive';
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

    select id, activities_per_day
    into active_session_id, current_activities_per_day
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

    effective_activities_per_day := round(greatest(coalesce(p_activities_per_day, current_activities_per_day, default_activities_per_day), 0.1), 2);

    if active_session_id is null then
        begin
            insert into public.learning_sessions (
                user_id,
                status,
                activities_per_day,
                target_date,
                target_source
            )
            values (
                current_user_id,
                'active',
                effective_activities_per_day,
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
        set activities_per_day = effective_activities_per_day,
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

    insert into public.session_lernbereiche (session_id, lernbereich_slug, sort_index, gebiet, gebiet_order)
    select
        active_session_id,
        lb.slug,
        coalesce((meta_elem.val->>'sort_index')::integer, 0),
        coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), ''),
        coalesce(
            (meta_elem.val->>'gebiet_order')::integer,
            case coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), '')
                when 'analysis' then 1
                when 'stochastik' then 2
                when 'lineare-algebra' then 3
                else 0
            end
        )
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
            'blocked',
            null,
            null
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    foreach current_lernbereich_slug in array normalized_lernbereiche loop
        if public.is_lernbereich_start_ready(active_session_id, current_lernbereich_slug) then
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

    update public.session_check_state scs
    set current_step_status = 'blocked'
    from public.session_activity_state sas
    where scs.session_id = active_session_id
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'due'
      and sas.session_id = active_session_id
      and sas.activity_type = 'start'
      and sas.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
      and sas.status <> 'completed';

    update public.session_check_state scs
    set current_step_status = 'due',
        available_from = now(),
        planned_from = null,
        overdue_from = null
    from public.session_activity_state sas
    where scs.session_id = active_session_id
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'blocked'
      and sas.session_id = active_session_id
      and sas.activity_type = 'start'
      and sas.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
      and sas.status = 'completed';

    perform public.replan_session(active_session_id);

    return active_session_id;
end;
$$;

create or replace function public.replan_session(p_session_id uuid default null)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid := p_session_id;
    resolved_target_date date := current_date;
    configured_activities_per_day numeric := public.get_default_activities_per_day();
    required_activities_per_day numeric := null;
    planning_activities_per_day numeric := 1.0;
    remaining_today_item_capacity integer := 0;
    consumed_today_core_items integer := 0;
    core_gap interval := public.get_session_core_gap_interval(resolved_session_id);
begin
    if resolved_session_id is null then
        if current_user_id is null then
            return null;
        end if;

        select id
        into resolved_session_id
        from public.learning_sessions
        where user_id = current_user_id
          and status = 'active'
        order by started_at desc
        limit 1
        for update;
    elsif current_user_id is null then
        perform 1
        from public.learning_sessions
        where id = resolved_session_id
          and status = 'active'
        for update;

        if not found then
            return null;
        end if;
    else
        perform 1
        from public.learning_sessions
        where id = resolved_session_id
          and user_id = current_user_id
          and status = 'active'
        for update;

        if not found then
            raise exception 'No active learning session found';
        end if;
    end if;

    if resolved_session_id is null then
        return null;
    end if;

    select coalesce(ls.target_date, current_date),
           greatest(coalesce(ls.activities_per_day, public.get_default_activities_per_day()), 0.1),
           case
               when ls.daily_core_budget_date = current_date then coalesce(ls.daily_core_budget_used, 0)
               else 0
           end
    into resolved_target_date, configured_activities_per_day, consumed_today_core_items
    from public.learning_sessions ls
    where ls.id = resolved_session_id;

    required_activities_per_day := public.get_session_required_activities_per_day(resolved_session_id, resolved_target_date);
    planning_activities_per_day := greatest(configured_activities_per_day, coalesce(required_activities_per_day, configured_activities_per_day), 0.1);
    remaining_today_item_capacity := greatest(floor(planning_activities_per_day - consumed_today_core_items)::integer, 0);
    core_gap := public.get_session_core_gap_interval(resolved_session_id, resolved_target_date);

    with open_core_items as (
        select
            'check'::text as item_kind,
            'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
            public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
            scs.check_id,
            scs.current_step_key as step_key,
            coalesce(slb.sort_index, 0) as lernbereich_sort_index,
            coalesce(slb.gebiet_order, 0) as gebiet_order,
            coalesce(nullif(trim(slb.gebiet), ''), public.check_id_lernbereich_slug(scs.check_id), '') as gebiet_key,
            public.feed_step_depth_rank(scs.current_step_key) as step_depth,
            public.feed_check_sequence_number(scs.check_id) as check_order,
            coalesce(scs.available_from, now()) as available_from
        from public.session_check_state scs
        left join public.session_lernbereiche slb
          on slb.session_id = scs.session_id
         and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
        where scs.session_id = resolved_session_id
          and scs.current_step_status = 'due'
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')

        union all

        select
            'start'::text as item_kind,
            sas.activity_key,
            sas.lernbereich_slug,
            null::text as check_id,
            'start'::text as step_key,
            coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
            coalesce(slb.gebiet_order, 0) as gebiet_order,
            coalesce(nullif(trim(slb.gebiet), ''), sas.lernbereich_slug, '') as gebiet_key,
            0 as step_depth,
            0 as check_order,
            coalesce(sas.due_at, now()) as available_from
        from public.session_activity_state sas
        left join public.session_lernbereiche slb
          on slb.session_id = sas.session_id
         and slb.lernbereich_slug = sas.lernbereich_slug
        where sas.session_id = resolved_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'
    ), ranked_core_items as (
        select
            item_kind,
            activity_key,
            lernbereich_slug,
            check_id,
            step_key,
            row_number() over (
                order by
                    case when item_kind = 'start' then 0 else 1 end,
                    available_from,
                    step_depth desc,
                    gebiet_order,
                    lernbereich_sort_index,
                    gebiet_key,
                    check_order,
                    activity_key
            ) as row_number_in_plan
        from open_core_items
    ), scheduled_core_items as (
        select
            item_kind,
            activity_key,
            lernbereich_slug,
            check_id,
            step_key,
            case
                when remaining_today_item_capacity > 0 and row_number_in_plan <= remaining_today_item_capacity then now()
                else date_trunc('day', now())
                    + make_interval(days => greatest(ceil((greatest(row_number_in_plan - remaining_today_item_capacity, 0))::numeric / planning_activities_per_day), 1)::integer)
            end as scheduled_from
        from ranked_core_items
    )
    update public.session_check_state scs
    set planned_from = scheduled_core_items.scheduled_from,
        overdue_from = case
            when scs.current_step_key = 'training' then (
                case
                    when scs.available_from is null then scheduled_core_items.scheduled_from
                    when scheduled_core_items.scheduled_from is null then scs.available_from
                    else greatest(scs.available_from, scheduled_core_items.scheduled_from)
                end
            ) + core_gap
            else scs.overdue_from
        end
    from scheduled_core_items
    where scheduled_core_items.item_kind = 'check'
      and scs.session_id = resolved_session_id
      and scs.check_id = scheduled_core_items.check_id
      and scs.current_step_key = scheduled_core_items.step_key
      and (
          scs.planned_from is distinct from scheduled_core_items.scheduled_from
          or (
              scs.current_step_key = 'training'
              and scs.overdue_from is distinct from (
                  case
                      when scs.available_from is null then scheduled_core_items.scheduled_from
                      when scheduled_core_items.scheduled_from is null then scs.available_from
                      else greatest(scs.available_from, scheduled_core_items.scheduled_from)
                  end
              ) + core_gap
          )
      );

    with open_core_items as (
        select
            'start'::text as item_kind,
            sas.activity_key,
            sas.lernbereich_slug,
            null::text as check_id,
            'start'::text as step_key,
            coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
            coalesce(slb.gebiet_order, 0) as gebiet_order,
            coalesce(nullif(trim(slb.gebiet), ''), sas.lernbereich_slug, '') as gebiet_key,
            0 as step_depth,
            0 as check_order,
            coalesce(sas.due_at, now()) as available_from
        from public.session_activity_state sas
        left join public.session_lernbereiche slb
          on slb.session_id = sas.session_id
         and slb.lernbereich_slug = sas.lernbereich_slug
        where sas.session_id = resolved_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'

        union all

        select
            'check'::text as item_kind,
            'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
            public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
            scs.check_id,
            scs.current_step_key,
            coalesce(slb.sort_index, 0) as lernbereich_sort_index,
            coalesce(slb.gebiet_order, 0) as gebiet_order,
            coalesce(nullif(trim(slb.gebiet), ''), public.check_id_lernbereich_slug(scs.check_id), '') as gebiet_key,
            public.feed_step_depth_rank(scs.current_step_key) as step_depth,
            public.feed_check_sequence_number(scs.check_id) as check_order,
            coalesce(scs.available_from, now()) as available_from
        from public.session_check_state scs
        left join public.session_lernbereiche slb
          on slb.session_id = scs.session_id
         and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
        where scs.session_id = resolved_session_id
          and scs.current_step_status = 'due'
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
    ), ranked_core_items as (
        select
            item_kind,
            activity_key,
            row_number() over (
                order by
                    case when item_kind = 'start' then 0 else 1 end,
                    available_from,
                    step_depth desc,
                    gebiet_order,
                    lernbereich_sort_index,
                    gebiet_key,
                    check_order,
                    activity_key
            ) as row_number_in_plan
        from open_core_items
    ), scheduled_core_items as (
        select
            item_kind,
            activity_key,
            case
                when remaining_today_item_capacity > 0 and row_number_in_plan <= remaining_today_item_capacity then now()
                else date_trunc('day', now())
                    + make_interval(days => greatest(ceil((greatest(row_number_in_plan - remaining_today_item_capacity, 0))::numeric / planning_activities_per_day), 1)::integer)
            end as scheduled_from
        from ranked_core_items
    )
    update public.session_activity_state sas
    set planned_from = scheduled_core_items.scheduled_from,
        overdue_from = (
            case
                when sas.due_at is null then scheduled_core_items.scheduled_from
                when scheduled_core_items.scheduled_from is null then sas.due_at
                else greatest(sas.due_at, scheduled_core_items.scheduled_from)
            end
        ) + core_gap
    from scheduled_core_items
    where sas.session_id = resolved_session_id
      and scheduled_core_items.item_kind = 'start'
      and sas.activity_key = scheduled_core_items.activity_key
      and (
          sas.planned_from is distinct from scheduled_core_items.scheduled_from
          or sas.overdue_from is distinct from (
              case
                  when sas.due_at is null then scheduled_core_items.scheduled_from
                  when scheduled_core_items.scheduled_from is null then sas.due_at
                  else greatest(sas.due_at, scheduled_core_items.scheduled_from)
              end
          ) + core_gap
      );

    update public.session_check_state
    set planned_from = null,
        overdue_from = case
            when current_step_key = 'training' then overdue_from
            when current_step_key in ('recall', 'feynman', 'kompetenzliste_gate') then overdue_from
            else null
        end
    where session_id = resolved_session_id
      and current_step_status <> 'due'
      and planned_from is not null;

    update public.session_activity_state
    set planned_from = null,
        overdue_from = null
    where session_id = resolved_session_id
      and activity_type = 'start'
      and status <> 'due'
      and (
          planned_from is not null
          or overdue_from is not null
      );

    return resolved_session_id;
end;
$$;

create or replace function public.feed_cursor_open_items(p_session_id uuid)
returns table (
    activity_key text,
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
    class_rank integer,
    urgency_rank integer,
    order_timestamp timestamptz,
    lernbereich_sort_index integer,
    step_depth integer,
    check_order integer,
    sort_bucket integer,
    sort_index integer
)
language sql
stable
set search_path = public
as $$
with now_ref as (
    select now() as current_time
)
select
    sas.activity_key,
    'start'::text as activity_kind,
    sas.activity_type,
    sas.lernbereich_slug,
    null::text as check_id,
    'start'::text as step_key,
    sas.target_module_key,
    sas.due_at as available_from,
    sas.planned_from,
    sas.overdue_from,
    case
        when sas.planned_from is null then sas.due_at
        else greatest(sas.due_at, sas.planned_from)
    end as effective_planned_from,
    10 as class_rank,
    case
        when sas.overdue_from is not null and sas.overdue_from <= now_ref.current_time then 0
        when (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        ) <= now_ref.current_time then 1
        else 2
    end as urgency_rank,
    case
        when sas.overdue_from is not null and sas.overdue_from <= now_ref.current_time then sas.overdue_from
        when (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        ) <= now_ref.current_time then (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        )
        else sas.due_at
    end as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
    0 as step_depth,
    0 as check_order,
    coalesce(sas.sort_bucket, 5) as sort_bucket,
    coalesce(sas.sort_index, 0) as sort_index
from public.session_activity_state sas
left join public.session_lernbereiche slb
  on slb.session_id = sas.session_id
 and slb.lernbereich_slug = sas.lernbereich_slug
cross join now_ref
where sas.session_id = p_session_id
  and sas.activity_type = 'start'
  and sas.status = 'due'
  and sas.due_at <= now_ref.current_time

union all

select
    'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
    'check'::text as activity_kind,
    scs.current_step_key as activity_type,
    public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
    scs.check_id,
    scs.current_step_key as step_key,
    scs.current_step_key as target_module_key,
    scs.available_from,
    scs.planned_from,
    scs.overdue_from,
    case
        when scs.planned_from is null then scs.available_from
        when scs.available_from is null then scs.planned_from
        else greatest(scs.available_from, scs.planned_from)
    end as effective_planned_from,
    20 as class_rank,
    case
        when scs.overdue_from is not null and scs.overdue_from <= now_ref.current_time then 0
        when (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        ) <= now_ref.current_time then 1
        else 2
    end as urgency_rank,
    case
        when scs.overdue_from is not null and scs.overdue_from <= now_ref.current_time then scs.overdue_from
        when (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        ) <= now_ref.current_time then (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        )
        else scs.available_from
    end as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, 0) as lernbereich_sort_index,
    public.feed_step_depth_rank(scs.current_step_key) as step_depth,
    public.feed_check_sequence_number(scs.check_id) as check_order,
    20 as sort_bucket,
    public.feed_check_sequence_number(scs.check_id) as sort_index
from public.session_check_state scs
left join public.session_lernbereiche slb
  on slb.session_id = scs.session_id
 and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
cross join now_ref
where scs.session_id = p_session_id
  and scs.current_step_status = 'due'
  and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
  and coalesce(scs.available_from, '-infinity'::timestamptz) <= now_ref.current_time

union all

select
    sas.activity_key,
    'flashcards'::text as activity_kind,
    sas.activity_type,
    sas.lernbereich_slug,
    sas.check_id,
    sas.activity_type as step_key,
    sas.target_module_key,
    sas.due_at as available_from,
    null::timestamptz as planned_from,
    null::timestamptz as overdue_from,
    sas.due_at as effective_planned_from,
    30 as class_rank,
    1 as urgency_rank,
    sas.due_at as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
    0 as step_depth,
    0 as check_order,
    coalesce(sas.sort_bucket, 50) as sort_bucket,
    coalesce(sas.sort_index, 0) as sort_index
from public.session_activity_state sas
left join public.session_lernbereiche slb
  on slb.session_id = sas.session_id
 and slb.lernbereich_slug = sas.lernbereich_slug
cross join now_ref
where sas.session_id = p_session_id
  and sas.activity_type = 'flashcards'
  and sas.status = 'due'
  and sas.due_at <= now_ref.current_time;
$$;

create or replace function public.complete_start_activity(
    p_lernbereich_slug text,
    p_activity_key text
)
returns public.session_activity_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
    active_session_id uuid;
    updated_activity public.session_activity_state;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'lernbereich:' || normalized_lernbereich_slug || ':start';

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    select id
    into active_session_id
    from public.learning_sessions
    where user_id = current_user_id
      and status = 'active'
    for update;

    if active_session_id is null then
        raise exception 'No active learning session found';
    end if;

    perform public.require_current_feed_cursor(active_session_id, expected_activity_key);

    update public.session_activity_state
    set status = 'completed',
        planned_from = null,
        overdue_from = null,
        last_outcome_key = 'complete',
        updated_at = completion_timestamp
    where session_id = active_session_id
      and activity_type = 'start'
      and scope_type = 'lernbereich'
      and lernbereich_slug = normalized_lernbereich_slug
      and activity_key = expected_activity_key
      and status = 'due'
    returning * into updated_activity;

    if updated_activity.session_id is null then
        raise exception 'No due start activity found';
    end if;

    update public.session_check_state
    set current_step_status = 'due',
        available_from = completion_timestamp,
        planned_from = null,
        overdue_from = null
    where session_id = active_session_id
      and public.check_id_lernbereich_slug(check_id) = normalized_lernbereich_slug
      and current_step_key = 'training'
      and current_step_status = 'blocked';

    perform public.bump_feed_activity_completion_count();
    perform public.bump_session_daily_core_budget_used(active_session_id);
    perform public.clear_current_feed_cursor(active_session_id, expected_activity_key);
    perform public.replan_session(active_session_id);

    return updated_activity;
end;
$$;

create or replace function public.record_check_module_attempt(
    p_lernbereich_slug text,
    p_check_id text,
    p_module_key text,
    p_outcome_key text,
    p_activity_key text
)
returns public.learning_activity_attempts
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    normalized_check_id text := nullif(trim(coalesce(p_check_id, '')), '');
    normalized_module_key text := lower(coalesce(nullif(trim(p_module_key), ''), ''));
    normalized_outcome_key text := lower(coalesce(nullif(trim(p_outcome_key), ''), ''));
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
    matched_session_id uuid;
    inserted_attempt public.learning_activity_attempts;
    did_advance boolean := false;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    if normalized_module_key not in ('recall', 'feynman') then
        raise exception 'Unsupported module_key';
    end if;

    if normalized_outcome_key not in ('can_do', 'repeat') then
        raise exception 'Unsupported outcome_key';
    end if;

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'check:' || normalized_check_id || ':' || normalized_module_key;

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    select learning_sessions.id
    into matched_session_id
    from public.learning_sessions
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and exists (
          select 1
          from public.session_check_state
          where session_check_state.session_id = learning_sessions.id
            and session_check_state.check_id = normalized_check_id
            and session_check_state.current_step_key = normalized_module_key
            and session_check_state.current_step_status = 'due'
            and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
      )
      and not exists (
          select 1
          from public.session_check_exclusions
          where session_check_exclusions.session_id = learning_sessions.id
            and session_check_exclusions.check_id = normalized_check_id
      )
    limit 1;

    if matched_session_id is null then
        raise exception 'Due feed activity not found';
    end if;

    perform public.require_current_feed_cursor(matched_session_id, expected_activity_key);

    insert into public.learning_activity_attempts (
        user_id,
        session_id,
        lernbereich_slug,
        check_id,
        module_key,
        outcome_key
    )
    values (
        current_user_id,
        matched_session_id,
        normalized_lernbereich_slug,
        normalized_check_id,
        normalized_module_key,
        normalized_outcome_key
    )
    returning * into inserted_attempt;

    if normalized_module_key = 'recall' then
        if normalized_outcome_key = 'can_do' then
            update public.session_check_state
            set current_step_key = 'feynman',
                current_step_status = 'due',
                last_outcome_key = 'can_do',
                last_completed_at = inserted_attempt.created_at
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'recall'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            did_advance := found;

            if not did_advance then
                raise exception 'Due feed activity not found';
            end if;
        else
            update public.session_check_state
            set last_outcome_key = 'repeat'
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'recall'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            if not found then
                raise exception 'Due feed activity not found';
            end if;
        end if;
    elsif normalized_module_key = 'feynman' then
        if normalized_outcome_key = 'can_do' then
            update public.session_check_state
            set current_step_key = 'kompetenzliste_gate',
                current_step_status = 'due',
                last_outcome_key = 'can_do',
                last_completed_at = inserted_attempt.created_at
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'feynman'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            did_advance := found;

            if not did_advance then
                raise exception 'Due feed activity not found';
            end if;
        else
            update public.session_check_state
            set last_outcome_key = 'repeat'
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'feynman'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            if not found then
                raise exception 'Due feed activity not found';
            end if;
        end if;
    end if;

    if did_advance then
        perform public.bump_feed_activity_completion_count();
        perform public.bump_session_daily_core_budget_used(matched_session_id);
        perform public.clear_current_feed_cursor(matched_session_id, expected_activity_key);
        perform public.replan_session(matched_session_id);
    end if;

    return inserted_attempt;
end;
$$;

create or replace function public.complete_kompetenzliste_gate(
    p_check_id text,
    p_activity_key text
)
returns public.session_check_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_check_id text := nullif(trim(coalesce(p_check_id, '')), '');
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
    updated_state public.session_check_state;
    remaining_open_checks integer := 0;
    remaining_lernbereich_open_checks integer := 0;
    completed_lernbereich_slug text;
    current_completed_activity_count bigint;
    retention_activity_gap integer;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'check:' || normalized_check_id || ':kompetenzliste_gate';

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    update public.session_check_state
    set current_step_key = 'check_completed',
        current_step_status = 'completed',
        last_outcome_key = 'complete',
        last_completed_at = completion_timestamp
    from public.learning_sessions
    where learning_sessions.id = session_check_state.session_id
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and session_check_state.check_id = normalized_check_id
      and session_check_state.current_step_key = 'kompetenzliste_gate'
      and session_check_state.current_step_status = 'due'
      and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
    returning session_check_state.* into updated_state;

    if updated_state.session_id is null then
        raise exception 'Due kompetenzliste gate not found';
    end if;

    perform public.require_current_feed_cursor(updated_state.session_id, expected_activity_key);
    perform public.bump_feed_activity_completion_count();
    perform public.bump_session_daily_core_budget_used(updated_state.session_id);

    current_completed_activity_count := public.get_current_feed_activity_completion_count();
    retention_activity_gap := public.get_system_setting_integer('feed.retention_activity_base_gap', 5);
    completed_lernbereich_slug := public.check_id_lernbereich_slug(updated_state.check_id);

    select count(*)
    into remaining_lernbereich_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and public.check_id_lernbereich_slug(check_id) = completed_lernbereich_slug
      and current_step_key <> 'check_completed';

    if remaining_lernbereich_open_checks = 0 then
        delete from public.user_retention_check_exclusions
        where user_id = current_user_id
          and lernbereich_slug = completed_lernbereich_slug;

        insert into public.user_retention_scopes (
            user_id,
            activity_type,
            scope_type,
            lernbereich_slug,
            status,
            source_session_id,
            activity_interval,
            activity_due_exponent,
            next_due_after_activity_count,
            feed_queue_entry_activity_count
        )
        values (
            current_user_id,
            'flashcards',
            'lernbereich',
            completed_lernbereich_slug,
            'active',
            updated_state.session_id,
            retention_activity_gap,
            0,
            current_completed_activity_count,
            current_completed_activity_count
        )
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set status = case
                when public.user_retention_scopes.status in ('paused', 'opted_out') then public.user_retention_scopes.status
                else 'active'
            end,
            source_session_id = excluded.source_session_id,
            activity_interval = excluded.activity_interval,
            activity_due_exponent = case
                when public.user_retention_scopes.status in ('paused', 'opted_out') then public.user_retention_scopes.activity_due_exponent
                else excluded.activity_due_exponent
            end,
            next_due_after_activity_count = case
                when public.user_retention_scopes.status in ('paused', 'opted_out') then public.user_retention_scopes.next_due_after_activity_count
                else excluded.next_due_after_activity_count
            end,
            feed_queue_entry_activity_count = case
                when public.user_retention_scopes.status in ('paused', 'opted_out') then public.user_retention_scopes.feed_queue_entry_activity_count
                else excluded.feed_queue_entry_activity_count
            end,
            updated_at = now();

        perform public.unlock_successor_lernbereiche(updated_state.session_id, completed_lernbereich_slug);
    end if;

    select count(*)
    into remaining_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and current_step_key <> 'check_completed';

    if remaining_open_checks = 0 then
        update public.learning_sessions
        set status = 'completed',
            ended_at = coalesce(ended_at, completion_timestamp)
        where id = updated_state.session_id
          and status = 'active';
    end if;

    perform public.clear_current_feed_cursor(updated_state.session_id, expected_activity_key);
    perform public.replan_session(updated_state.session_id);

    return updated_state;
end;
$$;

create or replace function public.unlock_successor_lernbereiche(
    p_session_id uuid,
    p_lernbereich_slug text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    v_gebiet text;
    v_sort_index integer;
    v_next_sort_index integer;
    v_remaining_open_checks integer;
begin
    select slb.gebiet, slb.sort_index
    into v_gebiet, v_sort_index
    from public.session_lernbereiche slb
    where slb.session_id = p_session_id
      and slb.lernbereich_slug = p_lernbereich_slug;

    if v_gebiet is null or v_gebiet = '' then
        return;
    end if;

    select count(*)
    into v_remaining_open_checks
    from public.session_check_state scs
    join public.session_lernbereiche slb
      on slb.session_id = scs.session_id
     and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
    where scs.session_id = p_session_id
      and slb.gebiet = v_gebiet
      and slb.sort_index <= v_sort_index
      and scs.current_step_key <> 'check_completed'
      and not exists (
          select 1
          from public.session_check_exclusions sce
          where sce.session_id = p_session_id
            and sce.check_id = scs.check_id
      );

    if v_remaining_open_checks > 0 then
        return;
    end if;

    select min(slb2.sort_index)
    into v_next_sort_index
    from public.session_lernbereiche slb2
    where slb2.session_id = p_session_id
      and slb2.gebiet = v_gebiet
      and slb2.sort_index > v_sort_index;

    if v_next_sort_index is null then
        return;
    end if;

    update public.session_activity_state sas
    set status = 'due',
        due_at = now(),
        planned_from = null,
        overdue_from = null
    from public.session_lernbereiche slb
    where sas.session_id = p_session_id
      and slb.session_id = p_session_id
      and slb.lernbereich_slug = sas.lernbereich_slug
      and sas.activity_type = 'start'
      and slb.gebiet = v_gebiet
      and slb.sort_index = v_next_sort_index
      and sas.status = 'blocked';
end;
$$;

drop function if exists public.create_learning_session(integer, text[], text[]);

revoke all on function public.is_lernbereich_start_ready(uuid, text) from public;
revoke all on function public.is_lernbereich_start_ready(uuid, text) from anon;alter table public.session_lernbereiche
    add column if not exists gebiet_order integer not null default 0;

update public.session_lernbereiche
set gebiet_order = case gebiet
    when 'analysis' then 1
    when 'stochastik' then 2
    when 'lineare-algebra' then 3
    else 0
end
where gebiet_order = 0;

create or replace function public.is_lernbereich_start_ready(
    p_session_id uuid,
    p_lernbereich_slug text
)
returns boolean
language plpgsql
stable
security definer
set search_path = public
as $$
declare
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    current_gebiet text;
    current_sort_index integer;
begin
    if p_session_id is null or normalized_lernbereich_slug is null then
        return false;
    end if;

    select slb.gebiet, slb.sort_index
    into current_gebiet, current_sort_index
    from public.session_lernbereiche slb
    where slb.session_id = p_session_id
      and slb.lernbereich_slug = normalized_lernbereich_slug;

    if not found then
        return false;
    end if;

    if current_gebiet is null or current_gebiet = '' then
        return true;
    end if;

    if not exists (
        select 1
        from public.session_lernbereiche predecessor
        where predecessor.session_id = p_session_id
          and predecessor.gebiet = current_gebiet
          and predecessor.sort_index < current_sort_index
    ) then
        return true;
    end if;

    return not exists (
        select 1
        from public.session_lernbereiche predecessor
        join public.session_check_state scs
          on scs.session_id = p_session_id
         and public.check_id_lernbereich_slug(scs.check_id) = predecessor.lernbereich_slug
        where predecessor.session_id = p_session_id
          and predecessor.gebiet = current_gebiet
          and predecessor.sort_index < current_sort_index
          and scs.current_step_key <> 'check_completed'
          and not exists (
              select 1
              from public.session_check_exclusions sce
              where sce.session_id = p_session_id
                and sce.check_id = scs.check_id
          )
    );
end;
$$;

revoke all on function public.is_lernbereich_start_ready(uuid, text) from public;
revoke all on function public.is_lernbereich_start_ready(uuid, text) from anon;

create or replace function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_activities_per_day numeric default null,
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
    current_activities_per_day numeric;
    effective_activities_per_day numeric;
    default_activities_per_day numeric := public.get_default_activities_per_day();
    normalized_lernbereiche text[];
    normalized_excluded_check_ids text[];
    normalized_included_check_ids text[];
    normalized_target_date date := p_target_date;
    normalized_target_source text := nullif(trim(coalesce(p_target_source, '')), '');
    current_lernbereich_slug text;
    v_start_status text;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_activities_per_day is not null and p_activities_per_day <= 0 then
        raise exception 'activities_per_day must be positive';
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

    select id, activities_per_day
    into active_session_id, current_activities_per_day
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

    effective_activities_per_day := round(greatest(coalesce(p_activities_per_day, current_activities_per_day, default_activities_per_day), 0.1), 2);

    if active_session_id is null then
        begin
            insert into public.learning_sessions (
                user_id,
                status,
                activities_per_day,
                target_date,
                target_source
            )
            values (
                current_user_id,
                'active',
                effective_activities_per_day,
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
        set activities_per_day = effective_activities_per_day,
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

    insert into public.session_lernbereiche (session_id, lernbereich_slug, sort_index, gebiet, gebiet_order)
    select
        active_session_id,
        lb.slug,
        coalesce((meta_elem.val->>'sort_index')::integer, 0),
        coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), ''),
        coalesce(
            (meta_elem.val->>'gebiet_order')::integer,
            case coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), '')
                when 'analysis' then 1
                when 'stochastik' then 2
                when 'lineare-algebra' then 3
                else 0
            end
        )
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
            'blocked',
            null,
            null
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    foreach current_lernbereich_slug in array normalized_lernbereiche loop
        if public.is_lernbereich_start_ready(active_session_id, current_lernbereich_slug) then
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

    update public.session_check_state scs
    set current_step_status = 'blocked'
    from public.session_activity_state sas
    where scs.session_id = active_session_id
      and sas.session_id = active_session_id
      and sas.activity_type = 'start'
      and sas.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
      and sas.status <> 'completed'
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'due';

    update public.session_check_state scs
    set current_step_status = 'due',
        available_from = now(),
        planned_from = null,
        overdue_from = null
    from public.session_activity_state sas
    where scs.session_id = active_session_id
      and sas.session_id = active_session_id
      and sas.activity_type = 'start'
      and sas.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
      and sas.status = 'completed'
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'blocked';

    perform public.replan_session(active_session_id);

    return active_session_id;
end;
$$;

create or replace function public.replan_session(p_session_id uuid default null)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid := p_session_id;
    resolved_target_date date := current_date;
    configured_activities_per_day numeric := public.get_default_activities_per_day();
    required_activities_per_day numeric := null;
    planning_activities_per_day numeric := 1.0;
    remaining_today_item_capacity integer := 0;
    consumed_today_core_items integer := 0;
    core_gap interval := public.get_session_core_gap_interval(resolved_session_id);
begin
    if resolved_session_id is null then
        if current_user_id is null then
            return null;
        end if;

        select id
        into resolved_session_id
        from public.learning_sessions
        where user_id = current_user_id
          and status = 'active'
        order by started_at desc
        limit 1
        for update;
    elsif current_user_id is null then
        perform 1
        from public.learning_sessions
        where id = resolved_session_id
          and status = 'active'
        for update;

        if not found then
            return null;
        end if;
    else
        perform 1
        from public.learning_sessions
        where id = resolved_session_id
          and user_id = current_user_id
          and status = 'active'
        for update;

        if not found then
            raise exception 'No active learning session found';
        end if;
    end if;

    if resolved_session_id is null then
        return null;
    end if;

    select coalesce(ls.target_date, current_date),
           greatest(coalesce(ls.activities_per_day, public.get_default_activities_per_day()), 0.1),
           case
               when ls.daily_core_budget_date = current_date then coalesce(ls.daily_core_budget_used, 0)
               else 0
           end
    into resolved_target_date, configured_activities_per_day, consumed_today_core_items
    from public.learning_sessions ls
    where ls.id = resolved_session_id;

    required_activities_per_day := public.get_session_required_activities_per_day(resolved_session_id, resolved_target_date);
    planning_activities_per_day := greatest(configured_activities_per_day, coalesce(required_activities_per_day, configured_activities_per_day), 0.1);
    remaining_today_item_capacity := greatest(floor(planning_activities_per_day - consumed_today_core_items)::integer, 0);
    core_gap := public.get_session_core_gap_interval(resolved_session_id, resolved_target_date);

    with open_core_items as (
        select
            'check'::text as item_kind,
            'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
            public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
            scs.check_id,
            scs.current_step_key as step_key,
            coalesce(slb.sort_index, 0) as lernbereich_sort_index,
            coalesce(slb.gebiet_order, 0) as gebiet_order,
            coalesce(nullif(trim(slb.gebiet), ''), public.check_id_lernbereich_slug(scs.check_id), '') as gebiet_key,
            public.feed_step_depth_rank(scs.current_step_key) as step_depth,
            public.feed_check_sequence_number(scs.check_id) as check_order,
            coalesce(scs.available_from, now()) as available_from
        from public.session_check_state scs
        left join public.session_lernbereiche slb
          on slb.session_id = scs.session_id
         and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
        where scs.session_id = resolved_session_id
          and scs.current_step_status = 'due'
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')

        union all

        select
            'start'::text as item_kind,
            sas.activity_key,
            sas.lernbereich_slug,
            null::text as check_id,
            'start'::text as step_key,
            coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
            coalesce(slb.gebiet_order, 0) as gebiet_order,
            coalesce(nullif(trim(slb.gebiet), ''), sas.lernbereich_slug, '') as gebiet_key,
            0 as step_depth,
            0 as check_order,
            coalesce(sas.due_at, now()) as available_from
        from public.session_activity_state sas
        left join public.session_lernbereiche slb
          on slb.session_id = sas.session_id
         and slb.lernbereich_slug = sas.lernbereich_slug
        where sas.session_id = resolved_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'
    ), ranked_core_items as (
        select
            item_kind,
            activity_key,
            lernbereich_slug,
            check_id,
            step_key,
            row_number() over (
                order by
                    case when item_kind = 'start' then 0 else 1 end,
                    available_from,
                    step_depth desc,
                    gebiet_order,
                    lernbereich_sort_index,
                    gebiet_key,
                    check_order,
                    activity_key
            ) as row_number_in_plan
        from open_core_items
    ), scheduled_core_items as (
        select
            item_kind,
            activity_key,
            lernbereich_slug,
            check_id,
            step_key,
            case
                when remaining_today_item_capacity > 0 and row_number_in_plan <= remaining_today_item_capacity then now()
                else date_trunc('day', now())
                    + make_interval(days => greatest(ceil((greatest(row_number_in_plan - remaining_today_item_capacity, 0))::numeric / planning_activities_per_day), 1)::integer)
            end as scheduled_from
        from ranked_core_items
    )
    update public.session_check_state scs
    set planned_from = scheduled_core_items.scheduled_from,
        overdue_from = case
            when scs.current_step_key = 'training' then (
                case
                    when scs.available_from is null then scheduled_core_items.scheduled_from
                    when scheduled_core_items.scheduled_from is null then scs.available_from
                    else greatest(scs.available_from, scheduled_core_items.scheduled_from)
                end
            ) + core_gap
            else scs.overdue_from
        end
    from scheduled_core_items
    where scheduled_core_items.item_kind = 'check'
      and scs.session_id = resolved_session_id
      and scs.check_id = scheduled_core_items.check_id
      and scs.current_step_key = scheduled_core_items.step_key
      and (
          scs.planned_from is distinct from scheduled_core_items.scheduled_from
          or (
              scs.current_step_key = 'training'
              and scs.overdue_from is distinct from (
                  case
                      when scs.available_from is null then scheduled_core_items.scheduled_from
                      when scheduled_core_items.scheduled_from is null then scs.available_from
                      else greatest(scs.available_from, scheduled_core_items.scheduled_from)
                  end
              ) + core_gap
          )
      );

    with open_core_items as (
        select
            'start'::text as item_kind,
            sas.activity_key,
            sas.lernbereich_slug,
            null::text as check_id,
            'start'::text as step_key,
            coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
            coalesce(slb.gebiet_order, 0) as gebiet_order,
            coalesce(nullif(trim(slb.gebiet), ''), sas.lernbereich_slug, '') as gebiet_key,
            0 as step_depth,
            0 as check_order,
            coalesce(sas.due_at, now()) as available_from
        from public.session_activity_state sas
        left join public.session_lernbereiche slb
          on slb.session_id = sas.session_id
         and slb.lernbereich_slug = sas.lernbereich_slug
        where sas.session_id = resolved_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'

        union all

        select
            'check'::text as item_kind,
            'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
            public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
            scs.check_id,
            scs.current_step_key,
            coalesce(slb.sort_index, 0) as lernbereich_sort_index,
            coalesce(slb.gebiet_order, 0) as gebiet_order,
            coalesce(nullif(trim(slb.gebiet), ''), public.check_id_lernbereich_slug(scs.check_id), '') as gebiet_key,
            public.feed_step_depth_rank(scs.current_step_key) as step_depth,
            public.feed_check_sequence_number(scs.check_id) as check_order,
            coalesce(scs.available_from, now()) as available_from
        from public.session_check_state scs
        left join public.session_lernbereiche slb
          on slb.session_id = scs.session_id
         and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
        where scs.session_id = resolved_session_id
          and scs.current_step_status = 'due'
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
    ), ranked_core_items as (
        select
            item_kind,
            activity_key,
            row_number() over (
                order by
                    case when item_kind = 'start' then 0 else 1 end,
                    available_from,
                    step_depth desc,
                    gebiet_order,
                    lernbereich_sort_index,
                    gebiet_key,
                    check_order,
                    activity_key
            ) as row_number_in_plan
        from open_core_items
    ), scheduled_core_items as (
        select
            item_kind,
            activity_key,
            case
                when remaining_today_item_capacity > 0 and row_number_in_plan <= remaining_today_item_capacity then now()
                else date_trunc('day', now())
                    + make_interval(days => greatest(ceil((greatest(row_number_in_plan - remaining_today_item_capacity, 0))::numeric / planning_activities_per_day), 1)::integer)
            end as scheduled_from
        from ranked_core_items
    )
    update public.session_activity_state sas
    set planned_from = scheduled_core_items.scheduled_from,
        overdue_from = (
            case
                when sas.due_at is null then scheduled_core_items.scheduled_from
                when scheduled_core_items.scheduled_from is null then sas.due_at
                else greatest(sas.due_at, scheduled_core_items.scheduled_from)
            end
        ) + core_gap
    from scheduled_core_items
    where sas.session_id = resolved_session_id
      and scheduled_core_items.item_kind = 'start'
      and sas.activity_key = scheduled_core_items.activity_key
      and (
          sas.planned_from is distinct from scheduled_core_items.scheduled_from
          or sas.overdue_from is distinct from (
              case
                  when sas.due_at is null then scheduled_core_items.scheduled_from
                  when scheduled_core_items.scheduled_from is null then sas.due_at
                  else greatest(sas.due_at, scheduled_core_items.scheduled_from)
              end
          ) + core_gap
      );

    update public.session_check_state
    set planned_from = null,
        overdue_from = case
            when current_step_key = 'training' then overdue_from
            when current_step_key in ('recall', 'feynman', 'kompetenzliste_gate') then overdue_from
            else null
        end
    where session_id = resolved_session_id
      and current_step_status <> 'due'
      and planned_from is not null;

    update public.session_activity_state
    set planned_from = null,
        overdue_from = null
    where session_id = resolved_session_id
      and activity_type = 'start'
      and status <> 'due'
      and (
          planned_from is not null
          or overdue_from is not null
      );

    return resolved_session_id;
end;
$$;

create or replace function public.feed_cursor_open_items(p_session_id uuid)
returns table (
    activity_key text,
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
    class_rank integer,
    urgency_rank integer,
    order_timestamp timestamptz,
    lernbereich_sort_index integer,
    step_depth integer,
    check_order integer,
    sort_bucket integer,
    sort_index integer
)
language sql
stable
set search_path = public
as $$
with now_ref as (
    select now() as current_time
)
select
    sas.activity_key,
    'start'::text as activity_kind,
    sas.activity_type,
    sas.lernbereich_slug,
    null::text as check_id,
    'start'::text as step_key,
    sas.target_module_key,
    sas.due_at as available_from,
    sas.planned_from,
    sas.overdue_from,
    case
        when sas.planned_from is null then sas.due_at
        else greatest(sas.due_at, sas.planned_from)
    end as effective_planned_from,
    10 as class_rank,
    case
        when sas.overdue_from is not null and sas.overdue_from <= now_ref.current_time then 0
        when (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        ) <= now_ref.current_time then 1
        else 2
    end as urgency_rank,
    case
        when sas.overdue_from is not null and sas.overdue_from <= now_ref.current_time then sas.overdue_from
        when (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        ) <= now_ref.current_time then (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        )
        else sas.due_at
    end as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
    0 as step_depth,
    0 as check_order,
    coalesce(sas.sort_bucket, 5) as sort_bucket,
    coalesce(slb.sort_index, sas.sort_index, 0) as sort_index
from public.session_activity_state sas
left join public.session_lernbereiche slb
  on slb.session_id = sas.session_id
 and slb.lernbereich_slug = sas.lernbereich_slug
cross join now_ref
where sas.session_id = p_session_id
  and sas.activity_type = 'start'
  and sas.status = 'due'
  and sas.due_at <= now_ref.current_time

union all

select
    'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
    'check'::text as activity_kind,
    scs.current_step_key as activity_type,
    public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
    scs.check_id,
    scs.current_step_key as step_key,
    scs.current_step_key as target_module_key,
    scs.available_from,
    scs.planned_from,
    scs.overdue_from,
    case
        when scs.planned_from is null then scs.available_from
        when scs.available_from is null then scs.planned_from
        else greatest(scs.available_from, scs.planned_from)
    end as effective_planned_from,
    20 as class_rank,
    case
        when scs.overdue_from is not null and scs.overdue_from <= now_ref.current_time then 0
        when (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        ) <= now_ref.current_time then 1
        else 2
    end as urgency_rank,
    case
        when scs.overdue_from is not null and scs.overdue_from <= now_ref.current_time then scs.overdue_from
        when (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        ) <= now_ref.current_time then (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        )
        else scs.available_from
    end as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, 0) as lernbereich_sort_index,
    public.feed_step_depth_rank(scs.current_step_key) as step_depth,
    public.feed_check_sequence_number(scs.check_id) as check_order,
    20 as sort_bucket,
    public.feed_check_sequence_number(scs.check_id) as sort_index
from public.session_check_state scs
left join public.session_lernbereiche slb
  on slb.session_id = scs.session_id
 and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
cross join now_ref
where scs.session_id = p_session_id
  and scs.current_step_status = 'due'
  and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
  and coalesce(scs.available_from, '-infinity'::timestamptz) <= now_ref.current_time

union all

select
    sas.activity_key,
    'flashcards'::text as activity_kind,
    sas.activity_type,
    sas.lernbereich_slug,
    sas.check_id,
    sas.activity_type as step_key,
    sas.target_module_key,
    sas.due_at as available_from,
    null::timestamptz as planned_from,
    null::timestamptz as overdue_from,
    sas.due_at as effective_planned_from,
    30 as class_rank,
    1 as urgency_rank,
    sas.due_at as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
    0 as step_depth,
    0 as check_order,
    coalesce(sas.sort_bucket, 50) as sort_bucket,
    coalesce(sas.sort_index, 0) as sort_index
from public.session_activity_state sas
left join public.session_lernbereiche slb
  on slb.session_id = sas.session_id
 and slb.lernbereich_slug = sas.lernbereich_slug
cross join now_ref
where sas.session_id = p_session_id
  and sas.activity_type = 'flashcards'
  and sas.status = 'due'
  and sas.due_at <= now_ref.current_time;
$$;

create or replace function public.complete_start_activity(
    p_lernbereich_slug text,
    p_activity_key text
)
returns public.session_activity_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
    active_session_id uuid;
    updated_activity public.session_activity_state;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'lernbereich:' || normalized_lernbereich_slug || ':start';

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    select id
    into active_session_id
    from public.learning_sessions
    where user_id = current_user_id
      and status = 'active'
    for update;

    if active_session_id is null then
        raise exception 'No active learning session found';
    end if;

    perform public.require_current_feed_cursor(active_session_id, expected_activity_key);

    update public.session_activity_state
    set status = 'completed',
        planned_from = null,
        overdue_from = null,
        last_outcome_key = 'complete',
        updated_at = completion_timestamp
    where session_id = active_session_id
      and activity_type = 'start'
      and scope_type = 'lernbereich'
      and lernbereich_slug = normalized_lernbereich_slug
      and activity_key = expected_activity_key
      and status = 'due'
    returning * into updated_activity;

    if updated_activity.session_id is null then
        raise exception 'No due start activity found';
    end if;

    update public.session_check_state scs
    set current_step_status = 'due',
        available_from = completion_timestamp,
        planned_from = null,
        overdue_from = null
    where scs.session_id = active_session_id
      and public.check_id_lernbereich_slug(scs.check_id) = normalized_lernbereich_slug
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'blocked';

    perform public.bump_feed_activity_completion_count();
    perform public.bump_session_daily_core_budget_used(active_session_id);
    perform public.clear_current_feed_cursor(active_session_id, expected_activity_key);
    perform public.replan_session(active_session_id);

    return updated_activity;
end;
$$;

create or replace function public.record_check_module_attempt(
    p_lernbereich_slug text,
    p_check_id text,
    p_module_key text,
    p_outcome_key text,
    p_activity_key text
)
returns public.learning_activity_attempts
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    normalized_check_id text := nullif(trim(coalesce(p_check_id, '')), '');
    normalized_module_key text := lower(coalesce(nullif(trim(p_module_key), ''), ''));
    normalized_outcome_key text := lower(coalesce(nullif(trim(p_outcome_key), ''), ''));
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
    matched_session_id uuid;
    inserted_attempt public.learning_activity_attempts;
    did_advance boolean := false;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    if normalized_module_key not in ('recall', 'feynman') then
        raise exception 'Unsupported module_key';
    end if;

    if normalized_outcome_key not in ('can_do', 'repeat') then
        raise exception 'Unsupported outcome_key';
    end if;

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'check:' || normalized_check_id || ':' || normalized_module_key;

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    select learning_sessions.id
    into matched_session_id
    from public.learning_sessions
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and exists (
          select 1
          from public.session_check_state
          where session_check_state.session_id = learning_sessions.id
            and session_check_state.check_id = normalized_check_id
            and session_check_state.current_step_key = normalized_module_key
            and session_check_state.current_step_status = 'due'
            and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
      )
      and not exists (
          select 1
          from public.session_check_exclusions
          where session_check_exclusions.session_id = learning_sessions.id
            and session_check_exclusions.check_id = normalized_check_id
      )
    limit 1;

    if matched_session_id is null then
        raise exception 'Due feed activity not found';
    end if;

    perform public.require_current_feed_cursor(matched_session_id, expected_activity_key);

    insert into public.learning_activity_attempts (
        user_id,
        session_id,
        lernbereich_slug,
        check_id,
        module_key,
        outcome_key
    )
    values (
        current_user_id,
        matched_session_id,
        normalized_lernbereich_slug,
        normalized_check_id,
        normalized_module_key,
        normalized_outcome_key
    )
    returning * into inserted_attempt;

    if normalized_module_key = 'recall' then
        if normalized_outcome_key = 'can_do' then
            update public.session_check_state
            set current_step_key = 'feynman',
                current_step_status = 'due',
                last_outcome_key = 'can_do',
                last_completed_at = inserted_attempt.created_at
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'recall'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            did_advance := found;

            if not did_advance then
                raise exception 'Due feed activity not found';
            end if;
        else
            update public.session_check_state
            set last_outcome_key = 'repeat'
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'recall'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            if not found then
                raise exception 'Due feed activity not found';
            end if;
        end if;
    elsif normalized_module_key = 'feynman' then
        if normalized_outcome_key = 'can_do' then
            update public.session_check_state
            set current_step_key = 'kompetenzliste_gate',
                current_step_status = 'due',
                last_outcome_key = 'can_do',
                last_completed_at = inserted_attempt.created_at
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'feynman'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            did_advance := found;

            if not did_advance then
                raise exception 'Due feed activity not found';
            end if;
        else
            update public.session_check_state
            set last_outcome_key = 'repeat'
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'feynman'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            if not found then
                raise exception 'Due feed activity not found';
            end if;
        end if;
    end if;

    if did_advance then
        perform public.bump_feed_activity_completion_count();
        perform public.bump_session_daily_core_budget_used(matched_session_id);
        perform public.clear_current_feed_cursor(matched_session_id, expected_activity_key);
        perform public.replan_session(matched_session_id);
    end if;

    return inserted_attempt;
end;
$$;

create or replace function public.complete_kompetenzliste_gate(
    p_check_id text,
    p_activity_key text
)
returns public.session_check_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_check_id text := nullif(trim(coalesce(p_check_id, '')), '');
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
    updated_state public.session_check_state;
    remaining_open_checks integer := 0;
    remaining_lernbereich_open_checks integer := 0;
    completed_lernbereich_slug text;
    current_completed_activity_count bigint;
    retention_activity_gap integer;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'check:' || normalized_check_id || ':kompetenzliste_gate';

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    update public.session_check_state
    set current_step_key = 'check_completed',
        current_step_status = 'completed',
        last_outcome_key = 'complete',
        last_completed_at = completion_timestamp
    from public.learning_sessions
    where learning_sessions.id = session_check_state.session_id
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and session_check_state.check_id = normalized_check_id
      and session_check_state.current_step_key = 'kompetenzliste_gate'
      and session_check_state.current_step_status = 'due'
      and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
    returning session_check_state.* into updated_state;

    if updated_state.session_id is null then
        raise exception 'Due kompetenzliste gate not found';
    end if;

    perform public.require_current_feed_cursor(updated_state.session_id, expected_activity_key);
    perform public.bump_feed_activity_completion_count();
    perform public.bump_session_daily_core_budget_used(updated_state.session_id);

    current_completed_activity_count := public.get_current_feed_activity_completion_count();
    retention_activity_gap := public.get_system_setting_integer('feed.retention_activity_base_gap', 5);
    completed_lernbereich_slug := public.check_id_lernbereich_slug(updated_state.check_id);

    select count(*)
    into remaining_lernbereich_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and public.check_id_lernbereich_slug(check_id) = completed_lernbereich_slug
      and current_step_key <> 'check_completed';

    if remaining_lernbereich_open_checks = 0 then
        delete from public.user_retention_check_exclusions
        where user_id = current_user_id
          and lernbereich_slug = completed_lernbereich_slug;

        insert into public.user_retention_scopes (
            user_id,
            activity_type,
            scope_type,
            lernbereich_slug,
            status,
            source_session_id,
            activity_interval,
            activity_due_exponent,
            next_due_after_activity_count,
            feed_queue_entry_activity_count
        )
        values (
            current_user_id,
            'flashcards',
            'lernbereich',
            completed_lernbereich_slug,
            'active',
            updated_state.session_id,
            retention_activity_gap,
            0,
            current_completed_activity_count,
            current_completed_activity_count
        )
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set status = 'active',
            source_session_id = excluded.source_session_id,
            activity_interval = excluded.activity_interval,
            activity_due_exponent = excluded.activity_due_exponent,
            next_due_after_activity_count = excluded.next_due_after_activity_count,
            feed_queue_entry_activity_count = excluded.feed_queue_entry_activity_count,
            updated_at = now();

        perform public.unlock_successor_lernbereiche(updated_state.session_id, completed_lernbereich_slug);
    end if;

    select count(*)
    into remaining_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and current_step_key <> 'check_completed';

    if remaining_open_checks = 0 then
        update public.learning_sessions
        set status = 'completed',
            ended_at = coalesce(ended_at, completion_timestamp)
        where id = updated_state.session_id
          and status = 'active';
    end if;

    perform public.clear_current_feed_cursor(updated_state.session_id, expected_activity_key);
    perform public.replan_session(updated_state.session_id);

    return updated_state;
end;
$$;

create or replace function public.unlock_successor_lernbereiche(
    p_session_id uuid,
    p_lernbereich_slug text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    v_gebiet text;
    v_sort_index integer;
    v_next_sort_index integer;
    v_remaining_predecessor_checks integer;
begin
    select slb.gebiet, slb.sort_index
    into v_gebiet, v_sort_index
    from public.session_lernbereiche slb
    where slb.session_id = p_session_id
      and slb.lernbereich_slug = p_lernbereich_slug;

    if v_gebiet is null or v_gebiet = '' then
        return;
    end if;

    select count(*)
    into v_remaining_predecessor_checks
    from public.session_check_state scs
    join public.session_lernbereiche slb
      on slb.session_id = scs.session_id
     and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
    where scs.session_id = p_session_id
      and slb.gebiet = v_gebiet
      and slb.sort_index <= v_sort_index
      and scs.current_step_key <> 'check_completed'
      and not exists (
          select 1
          from public.session_check_exclusions sce
          where sce.session_id = p_session_id
            and sce.check_id = scs.check_id
      );

    if v_remaining_predecessor_checks > 0 then
        return;
    end if;

    select min(slb2.sort_index)
    into v_next_sort_index
    from public.session_lernbereiche slb2
    where slb2.session_id = p_session_id
      and slb2.gebiet = v_gebiet
      and slb2.sort_index > v_sort_index;

    if v_next_sort_index is null then
        return;
    end if;

    update public.session_activity_state sas
    set status = 'due',
        due_at = now(),
        planned_from = null,
        overdue_from = null
    from public.session_lernbereiche slb
    where sas.session_id = p_session_id
      and slb.session_id = p_session_id
      and slb.lernbereich_slug = sas.lernbereich_slug
      and sas.activity_type = 'start'
      and slb.gebiet = v_gebiet
      and slb.sort_index = v_next_sort_index
      and sas.status = 'blocked';
end;
$$;

drop function if exists public.create_learning_session(integer, text[], text[]);