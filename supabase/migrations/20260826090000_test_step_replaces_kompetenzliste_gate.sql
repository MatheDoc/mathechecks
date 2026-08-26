-- Test-Modul ersetzt das Kompetenzlisten-Gate als letztes Glied der Check-Kette.
-- Step-Key 'kompetenzliste_gate' -> 'test' (Constraint, Daten, Cursor-Keys, Setting)
-- und alle aktuellen Funktionsversionen, die den Step referenzieren, werden mit
-- 'test' neu angelegt. complete_kompetenzliste_gate wird zu complete_test_step.

alter table public.session_check_state
    drop constraint if exists session_check_state_current_step_key_check;

update public.session_check_state
set current_step_key = 'test'
where current_step_key = 'kompetenzliste_gate';

alter table public.session_check_state
    add constraint session_check_state_current_step_key_check
    check (current_step_key in (
        'training',
        'recall',
        'feynman',
        'test',
        'check_completed'
    ));

update public.session_feed_cursor
set current_activity_key = replace(current_activity_key, ':kompetenzliste_gate', ':test')
where current_activity_key like '%:kompetenzliste_gate';

update public.system_settings
set setting_key = 'feed.weight_test',
    description = 'Gewicht eines offenen Test-Schritts fuer die Druckberechnung.'
where setting_key = 'feed.weight_kompetenzliste'
  and not exists (
    select 1 from public.system_settings where setting_key = 'feed.weight_test'
  );

-- Quelle: 20260624170000_immediate_unlock_past_target_date.sql

create or replace function public.apply_session_check_timing_fields()
returns trigger
language plpgsql
set search_path = public
as $$
declare
    core_gap             interval;
    computed_available   timestamptz;
    session_target_date  date;
begin
    if new.current_step_key = 'check_completed' or new.current_step_status = 'completed' then
        new.available_from := null;
        new.planned_from   := null;
        new.overdue_from   := null;
        return new;
    end if;

    if tg_op = 'UPDATE' and new.current_step_key is distinct from old.current_step_key then
        new.planned_from := null;
    end if;

    if new.current_step_key = 'training' then
        new.available_from := coalesce(new.available_from, old.available_from, now());

        if tg_op = 'INSERT' or new.current_step_key is distinct from old.current_step_key then
            new.overdue_from := null;
        end if;

        return new;
    end if;

    if new.current_step_key in ('recall', 'feynman', 'test') then
        if new.last_completed_at is null then
            new.available_from := coalesce(new.available_from, old.available_from, now());
            new.overdue_from   := coalesce(new.overdue_from,   old.overdue_from);
            return new;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.available_from is null then

            core_gap           := public.get_session_core_gap_interval(new.session_id);
            computed_available := new.last_completed_at + core_gap;

            -- If the computed slot lands past the target date (start of day),
            -- unlock the step immediately so the user can still attempt it.
            select ls.target_date
            into   session_target_date
            from   public.learning_sessions ls
            where  ls.id = new.session_id;

            if session_target_date is not null
               and computed_available >= session_target_date::timestamp then
                new.available_from := new.last_completed_at;
            else
                new.available_from := computed_available;
            end if;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.overdue_from is null then
            core_gap         := coalesce(core_gap, public.get_session_core_gap_interval(new.session_id));
            new.overdue_from := coalesce(new.available_from, new.last_completed_at + core_gap) + core_gap;
        end if;

        return new;
    end if;

    return new;
end;
$$;

-- Quelle: 20260602150000_session_feed_cursor_and_replanning.sql

create or replace function public.feed_step_depth_rank(p_step_key text)
returns integer
language sql
immutable
set search_path = public
as $$
    select case lower(trim(coalesce(p_step_key, '')))
        when 'training' then 1
        when 'recall' then 2
        when 'feynman' then 3
        when 'test' then 4
        else 0
    end;
$$;

-- Quelle: 20260603154000_fix_feed_cursor_regression_and_derive_session_tempo.sql

create or replace function public.derive_learning_session_tempo_days(
    p_session_id uuid,
    p_target_date date default null,
    p_fallback_tempo_days integer default null
)
returns integer
language plpgsql
stable
set search_path = public
as $$
declare
    resolved_target_date date := p_target_date;
    fallback_tempo_days integer := greatest(coalesce(p_fallback_tempo_days, public.get_system_setting_integer('planning.default_session_tempo_days', 3)), 1);
    remaining_activity_count integer := 0;
    available_day_count integer := 1;
begin
    if p_session_id is null then
        return fallback_tempo_days;
    end if;

    if resolved_target_date is null then
        select ls.target_date
        into resolved_target_date
        from public.learning_sessions ls
        where ls.id = p_session_id;
    end if;

    select
        coalesce(start_items.remaining_start_count, 0)
        + coalesce(check_items.remaining_step_count, 0)
    into remaining_activity_count
    from (
        select count(*)::integer as remaining_start_count
        from public.session_activity_state sas
        where sas.session_id = p_session_id
          and sas.activity_type = 'start'
          and sas.status <> 'completed'
    ) as start_items
    cross join (
        select coalesce(sum(
            case scs.current_step_key
                when 'training' then 4
                when 'recall' then 3
                when 'feynman' then 2
                when 'test' then 1
                else 0
            end
        ), 0)::integer as remaining_step_count
        from public.session_check_state scs
        where scs.session_id = p_session_id
          and scs.current_step_key in ('training', 'recall', 'feynman', 'test')
          and scs.current_step_status <> 'completed'
    ) as check_items;

    if remaining_activity_count <= 0 then
        return fallback_tempo_days;
    end if;

    if resolved_target_date is null then
        return fallback_tempo_days;
    end if;

    available_day_count := greatest((resolved_target_date - current_date) + 1, 1);

    return greatest(ceil(remaining_activity_count::numeric / available_day_count)::integer, 1);
end;
$$;

-- Quelle: 20260516130000_flashcards_feed_rounds.sql

create or replace function public.refresh_flashcard_activity_for_lernbereich(
    p_session_id uuid,
    p_lernbereich_slug text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    normalized_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    normalized_activity_key text;
    included_count integer;
    ready_count integer;
begin
    if p_session_id is null or normalized_lernbereich_slug is null then
        return;
    end if;

    normalized_activity_key := 'lernbereich:' || normalized_lernbereich_slug || ':flashcards';

    select count(*)
    into included_count
    from public.session_check_state
    where session_id = p_session_id
      and public.check_id_lernbereich_slug(check_id) = normalized_lernbereich_slug;

    select count(*)
    into ready_count
    from public.session_check_state
    where session_id = p_session_id
      and public.check_id_lernbereich_slug(check_id) = normalized_lernbereich_slug
      and current_step_key in ('test', 'check_completed');

    if included_count > 0 and ready_count = included_count then
        insert into public.session_activity_state (
            session_id,
            activity_key,
            activity_type,
            scope_type,
            lernbereich_slug,
            check_id,
            target_module_key,
            status,
            due_at,
            sort_bucket,
            sort_index,
            last_outcome_key
        )
        values (
            p_session_id,
            normalized_activity_key,
            'flashcards',
            'lernbereich',
            normalized_lernbereich_slug,
            null,
            'flashcards',
            'due',
            now(),
            60,
            0,
            null
        )
        on conflict (session_id, activity_key) do update
        set status = case
                when session_activity_state.due_at <= now() then 'due'
                else session_activity_state.status
            end,
            target_module_key = 'flashcards',
            sort_bucket = 60,
            sort_index = 0;
        return;
    end if;

    delete from public.session_activity_state
    where session_id = p_session_id
      and activity_type = 'flashcards'
      and scope_type = 'lernbereich'
      and lernbereich_slug = normalized_lernbereich_slug;
end;
$$;

-- Quelle: 20260605132000_replan_from_actual_remaining_activity_count.sql

create or replace function public.get_session_remaining_activity_count(p_session_id uuid)
returns integer
language sql
stable
set search_path = public
as $$
select
    coalesce(start_items.remaining_count, 0) + coalesce(check_items.remaining_count, 0)
from (
    select count(*)::integer as remaining_count
    from public.session_activity_state sas
    where sas.session_id = p_session_id
      and sas.activity_type = 'start'
      and sas.status in ('due', 'blocked')
) as start_items
cross join (
    select coalesce(sum(
        case scs.current_step_key
            when 'training' then 4
            when 'recall' then 3
            when 'feynman' then 2
            when 'test' then 1
            else 0
        end
    ), 0)::integer as remaining_count
    from public.session_check_state scs
    where scs.session_id = p_session_id
      and scs.current_step_key in ('training', 'recall', 'feynman', 'test')
      and scs.current_step_status in ('due', 'blocked')
) as check_items;
$$;

-- Quelle: 20260605132000_replan_from_actual_remaining_activity_count.sql

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
    planning_activity_capacity integer := 1;
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
    planning_activity_capacity := greatest(ceil(planning_activities_per_day)::integer, 1);
    remaining_today_item_capacity := greatest(planning_activity_capacity - consumed_today_core_items, 0);
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
          and scs.current_step_key in ('training', 'recall', 'feynman', 'test')

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
                    + make_interval(days => greatest(ceil((greatest(row_number_in_plan - remaining_today_item_capacity, 0))::numeric / planning_activity_capacity), 1)::integer)
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
          and scs.current_step_key in ('training', 'recall', 'feynman', 'test')
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
                    + make_interval(days => greatest(ceil((greatest(row_number_in_plan - remaining_today_item_capacity, 0))::numeric / planning_activity_capacity), 1)::integer)
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
            when current_step_key in ('recall', 'feynman', 'test') then overdue_from
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

-- Quelle: 20260604113000_start_gate_gebiet_order_and_retention_head.sql

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
            set current_step_key = 'test',
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

-- Quelle: 20260604113000_start_gate_gebiet_order_and_retention_head.sql

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
  and scs.current_step_key in ('training', 'recall', 'feynman', 'test')
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

-- Quelle: 20260721110000_prioritize_training_steps_within_same_urgency.sql

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
        class_rank,
        step_depth asc,
        coalesce(order_timestamp, 'infinity'::timestamptz),
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
          and scs.current_step_key in ('training', 'recall', 'feynman', 'test')
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

drop function if exists public.complete_kompetenzliste_gate(text, text);

drop function if exists public.complete_kompetenzliste_gate(text);

-- Quelle: 20260709123000_keep_completed_session_active.sql

create or replace function public.complete_test_step(
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

    expected_activity_key := 'check:' || normalized_check_id || ':test';

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
      and session_check_state.current_step_key = 'test'
      and session_check_state.current_step_status = 'due'
      and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
    returning session_check_state.* into updated_state;

    if updated_state.session_id is null then
        raise exception 'Due test step not found';
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

    perform public.clear_current_feed_cursor(updated_state.session_id, expected_activity_key);

    if remaining_open_checks > 0 then
        perform public.replan_session(updated_state.session_id);
    end if;

    return updated_state;
end;
$$;

grant execute on function public.pick_feed_cursor(uuid) to authenticated;
grant execute on function public.complete_test_step(text, text) to authenticated;
