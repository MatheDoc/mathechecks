alter table public.learning_sessions
    add column if not exists daily_core_budget_date date not null default current_date,
    add column if not exists daily_core_budget_used integer not null default 0 check (daily_core_budget_used >= 0);

with today_ref as (
    select date_trunc('day', now()) as today_start
), session_budget_usage as (
    select
        ls.id as session_id,
        coalesce(start_items.completed_count, 0) + coalesce(check_items.completed_count, 0) as used_count
    from public.learning_sessions ls
    cross join today_ref
    left join lateral (
        select count(*)::integer as completed_count
        from public.session_activity_state sas
        where sas.session_id = ls.id
          and sas.activity_type = 'start'
          and sas.status = 'completed'
          and sas.updated_at >= today_ref.today_start
    ) as start_items on true
    left join lateral (
        select count(*)::integer as completed_count
        from public.session_check_state scs
        where scs.session_id = ls.id
          and scs.last_completed_at >= today_ref.today_start
          and (
              scs.current_step_key in ('recall', 'feynman', 'kompetenzliste_gate', 'check_completed')
              or scs.current_step_status = 'completed'
          )
    ) as check_items on true
    where ls.status = 'active'
)
update public.learning_sessions ls
set daily_core_budget_date = current_date,
    daily_core_budget_used = session_budget_usage.used_count
from session_budget_usage
where ls.id = session_budget_usage.session_id;

create or replace function public.bump_session_daily_core_budget_used(p_session_id uuid)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
    next_used integer;
begin
    if p_session_id is null then
        raise exception 'session_id is required';
    end if;

    update public.learning_sessions ls
    set daily_core_budget_date = current_date,
        daily_core_budget_used = case
            when ls.daily_core_budget_date = current_date then ls.daily_core_budget_used + 1
            else 1
        end
    where ls.id = p_session_id
      and ls.status = 'active'
    returning ls.daily_core_budget_used into next_used;

    if next_used is null then
        raise exception 'Active learning session not found';
    end if;

    return next_used;
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
    base_activities_per_day integer := greatest(public.get_system_setting_integer('planning.default_session_tempo_days', 3), 1);
    total_open_core_items integer := 0;
    available_day_count integer := 1;
    effective_activities_per_day integer := 1;
    remaining_today_capacity integer := 0;
    consumed_today_core_items integer := 0;
    core_gap interval := public.get_core_feed_gap_interval();
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
           greatest(coalesce(ls.tempo_days, public.get_system_setting_integer('planning.default_session_tempo_days', 3)), 1),
           case
               when ls.daily_core_budget_date = current_date then coalesce(ls.daily_core_budget_used, 0)
               else 0
           end
    into resolved_target_date, base_activities_per_day, consumed_today_core_items
    from public.learning_sessions ls
    where ls.id = resolved_session_id;

    select count(*)
    into total_open_core_items
    from (
        select sas.activity_key
        from public.session_activity_state sas
        where sas.session_id = resolved_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'

        union all

        select 'check:' || scs.check_id || ':' || scs.current_step_key
        from public.session_check_state scs
        where scs.session_id = resolved_session_id
          and scs.current_step_status = 'due'
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
    ) as open_items;

    available_day_count := greatest((coalesce(resolved_target_date, current_date) - current_date) + 1, 1);
    effective_activities_per_day := greatest(
        base_activities_per_day,
        case
            when total_open_core_items > 0 then ceil(total_open_core_items::numeric / available_day_count)::integer
            else base_activities_per_day
        end
    );
    remaining_today_capacity := greatest(effective_activities_per_day - consumed_today_core_items, 0);

    with open_core_items as (
        select
            'check'::text as item_kind,
            'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
            public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
            scs.check_id,
            scs.current_step_key as step_key,
            coalesce(slb.sort_index, 0) as lernbereich_sort_index,
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
                    gebiet_key,
                    lernbereich_sort_index,
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
                when remaining_today_capacity > 0 and row_number_in_plan <= remaining_today_capacity then now()
                else date_trunc('day', now())
                    + make_interval(days => 1 + floor(greatest(row_number_in_plan - remaining_today_capacity - 1, 0)::numeric / effective_activities_per_day)::integer)
            end as scheduled_from
        from ranked_core_items
    )
    update public.session_check_state scs
    set planned_from = scheduled_core_items.scheduled_from,
        overdue_from = (
            case
                when scs.available_from is null then scheduled_core_items.scheduled_from
                when scheduled_core_items.scheduled_from is null then scs.available_from
                else greatest(scs.available_from, scheduled_core_items.scheduled_from)
            end
        ) + core_gap
    from scheduled_core_items
    where scheduled_core_items.item_kind = 'check'
      and scs.session_id = resolved_session_id
      and scs.check_id = scheduled_core_items.check_id
      and scs.current_step_key = scheduled_core_items.step_key
      and (
          scs.planned_from is distinct from scheduled_core_items.scheduled_from
          or scs.overdue_from is distinct from (
              case
                  when scs.available_from is null then scheduled_core_items.scheduled_from
                  when scheduled_core_items.scheduled_from is null then scs.available_from
                  else greatest(scs.available_from, scheduled_core_items.scheduled_from)
              end
          ) + core_gap
      );

    with open_core_items as (
        select
            'start'::text as item_kind,
            sas.activity_key,
            sas.lernbereich_slug,
            null::text as check_id,
            'start'::text as step_key,
            coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
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
                    gebiet_key,
                    lernbereich_sort_index,
                    check_order,
                    activity_key
            ) as row_number_in_plan
        from open_core_items
    ), scheduled_core_items as (
        select
            item_kind,
            activity_key,
            case
                when remaining_today_capacity > 0 and row_number_in_plan <= remaining_today_capacity then now()
                else date_trunc('day', now())
                    + make_interval(days => 1 + floor(greatest(row_number_in_plan - remaining_today_capacity - 1, 0)::numeric / effective_activities_per_day)::integer)
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
            when current_step_key in ('recall', 'feynman', 'kompetenzliste_gate')
                then coalesce(available_from, now()) + core_gap
            else null
        end
    where session_id = resolved_session_id
      and current_step_status <> 'due'
      and (
          planned_from is not null
          or overdue_from is distinct from case
              when current_step_key in ('recall', 'feynman', 'kompetenzliste_gate')
                  then coalesce(available_from, now()) + core_gap
              else null
          end
      );

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
        updated_at = now()
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

    perform public.bump_feed_activity_completion_count();
    perform public.bump_session_daily_core_budget_used(active_session_id);
    perform public.clear_current_feed_cursor(active_session_id, expected_activity_key);
    perform public.replan_session(active_session_id);

    return updated_activity;
end;
$$;

create or replace function public.complete_current_training_step(
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
    normalized_check_id text := nullif(trim(p_check_id), '');
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
    updated_state public.session_check_state;
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

    expected_activity_key := 'check:' || normalized_check_id || ':training';

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    update public.session_check_state
    set current_step_key = 'recall',
        current_step_status = 'due',
        last_outcome_key = 'complete',
        last_completed_at = completion_timestamp
    from public.learning_sessions
    where learning_sessions.id = session_check_state.session_id
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and session_check_state.check_id = normalized_check_id
      and session_check_state.current_step_key = 'training'
      and session_check_state.current_step_status = 'due'
      and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
    returning session_check_state.* into updated_state;

    if updated_state.session_id is null then
        raise exception 'Due training step not found';
    end if;

    perform public.require_current_feed_cursor(updated_state.session_id, expected_activity_key);
    perform public.bump_feed_activity_completion_count();
    perform public.bump_session_daily_core_budget_used(updated_state.session_id);
    perform public.clear_current_feed_cursor(updated_state.session_id, expected_activity_key);
    perform public.replan_session(updated_state.session_id);

    return updated_state;
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
    join public.session_check_state
      on session_check_state.session_id = learning_sessions.id
     and session_check_state.check_id = normalized_check_id
     and session_check_state.current_step_key = normalized_module_key
     and session_check_state.current_step_status = 'due'
     and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and exists (
          select 1
          from public.session_lernbereiche
          where session_lernbereiche.session_id = learning_sessions.id
            and session_lernbereiche.lernbereich_slug = normalized_lernbereich_slug
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

            perform public.unlock_successor_lernbereiche(matched_session_id, normalized_lernbereich_slug);
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
            1,
            current_completed_activity_count + retention_activity_gap,
            current_completed_activity_count + retention_activity_gap
        )
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set status = 'active',
            source_session_id = excluded.source_session_id,
            activity_interval = excluded.activity_interval,
            activity_due_exponent = excluded.activity_due_exponent,
            next_due_after_activity_count = excluded.next_due_after_activity_count,
            feed_queue_entry_activity_count = excluded.feed_queue_entry_activity_count,
            updated_at = now();
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