alter table public.session_check_state
    add column if not exists planned_from timestamptz null;

alter table public.session_activity_state
    add column if not exists planned_from timestamptz null,
    add column if not exists overdue_from timestamptz null;

create index if not exists session_check_state_session_feed_planning_idx
    on public.session_check_state (session_id, current_step_status, planned_from, available_from, overdue_from, current_step_key);

create index if not exists session_activity_state_session_feed_planning_idx
    on public.session_activity_state (session_id, status, planned_from, due_at, overdue_from, activity_type);

create table if not exists public.session_feed_cursor (
    session_id uuid primary key references public.learning_sessions(id) on delete cascade,
    current_activity_key text null check (
        current_activity_key is null
        or char_length(trim(current_activity_key)) > 0
    ),
    locked_until timestamptz null,
    selected_at timestamptz null,
    selection_reason text null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists session_feed_cursor_current_activity_idx
    on public.session_feed_cursor (current_activity_key)
    where current_activity_key is not null;

drop trigger if exists set_session_feed_cursor_updated_at on public.session_feed_cursor;
create trigger set_session_feed_cursor_updated_at
    before update on public.session_feed_cursor
    for each row execute function public.set_updated_at();

insert into public.system_settings (
    setting_key,
    value_integer,
    description
)
values (
    'feed.current_activity_lock_minutes',
    30,
    'Wie lange ein aktuelles Feed-Element nach Auswahl als klebriger Cursor gesperrt bleibt.'
)
on conflict (setting_key) do update
set value_integer = excluded.value_integer,
    description = excluded.description;

create or replace function public.get_feed_cursor_lock_interval()
returns interval
language sql
stable
set search_path = public
as $$
    select make_interval(mins => greatest(public.get_system_setting_integer('feed.current_activity_lock_minutes', 30), 1));
$$;

create or replace function public.feed_check_sequence_number(p_check_id text)
returns integer
language sql
immutable
set search_path = public
as $$
    select case
        when split_part(trim(coalesce(p_check_id, '')), '__', 3) ~ '^[0-9]+$'
            then split_part(trim(coalesce(p_check_id, '')), '__', 3)::integer
        else 2147483647
    end;
$$;

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
        when 'kompetenzliste_gate' then 4
        else 0
    end;
$$;

create or replace function public.apply_session_check_timing_fields()
returns trigger
language plpgsql
set search_path = public
as $$
declare
    core_gap interval := public.get_core_feed_gap_interval();
begin
    if new.current_step_key = 'check_completed' or new.current_step_status = 'completed' then
        new.available_from := null;
        new.planned_from := null;
        new.overdue_from := null;
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

    if new.current_step_key in ('recall', 'feynman', 'kompetenzliste_gate') then
        if new.last_completed_at is null then
            new.available_from := coalesce(new.available_from, old.available_from, now());
            new.overdue_from := coalesce(new.overdue_from, old.overdue_from);
            return new;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.available_from is null then
            new.available_from := new.last_completed_at + core_gap;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.overdue_from is null then
            new.overdue_from := coalesce(new.available_from, new.last_completed_at + core_gap) + core_gap;
        end if;

        return new;
    end if;

    return new;
end;
$$;

create or replace function public.clear_current_feed_cursor(
    p_session_id uuid,
    p_activity_key text default null
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
begin
    update public.session_feed_cursor
    set current_activity_key = null,
        locked_until = null,
        selection_reason = null
    where session_id = p_session_id
      and (normalized_activity_key is null or current_activity_key = normalized_activity_key);
end;
$$;

create or replace function public.renew_current_feed_cursor(
    p_session_id uuid,
    p_activity_key text,
    p_selection_reason text default 'repeat_request'
)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    normalized_selection_reason text := nullif(trim(coalesce(p_selection_reason, '')), '');
begin
    if p_session_id is null or normalized_activity_key is null then
        return false;
    end if;

    update public.session_feed_cursor
    set locked_until = now() + public.get_feed_cursor_lock_interval(),
        selected_at = coalesce(selected_at, now()),
        selection_reason = coalesce(normalized_selection_reason, 'repeat_request')
    where session_id = p_session_id
      and current_activity_key = normalized_activity_key;

    return found;
end;
$$;

create or replace function public.require_current_feed_cursor(
    p_session_id uuid,
    p_activity_key text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
begin
    if p_session_id is null or normalized_activity_key is null then
        raise exception 'Current feed cursor is required';
    end if;

    if not exists (
        select 1
        from public.session_feed_cursor
        where session_id = p_session_id
          and current_activity_key = normalized_activity_key
    ) then
        raise exception 'Feed activity is not the current cursor';
    end if;
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

    select coalesce(target_date, current_date),
           greatest(coalesce(tempo_days, public.get_system_setting_integer('planning.default_session_tempo_days', 3)), 1)
    into resolved_target_date, base_activities_per_day
    from public.learning_sessions
    where id = resolved_session_id;

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
                when floor((row_number_in_plan - 1)::numeric / effective_activities_per_day)::integer <= 0
                    then now()
                else date_trunc('day', now())
                    + make_interval(days => floor((row_number_in_plan - 1)::numeric / effective_activities_per_day)::integer)
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
                when floor((row_number_in_plan - 1)::numeric / effective_activities_per_day)::integer <= 0
                    then now()
                else date_trunc('day', now())
                    + make_interval(days => floor((row_number_in_plan - 1)::numeric / effective_activities_per_day)::integer)
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
      and (
          current_step_status <> 'due'
          or current_step_key not in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
      )
      and (
          planned_from is not null
          or (
              current_step_key = 'training'
              and overdue_from is not null
          )
      );

    update public.session_activity_state
    set planned_from = null,
        overdue_from = null
    where session_id = resolved_session_id
      and (
          activity_type <> 'start'
          or status <> 'due'
      )
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
    case when sas.overdue_from is not null and sas.overdue_from <= now_ref.current_time then 0 else 1 end as urgency_rank,
    case
        when sas.overdue_from is not null and sas.overdue_from <= now_ref.current_time then sas.overdue_from
        when sas.planned_from is null then sas.due_at
        else greatest(sas.due_at, sas.planned_from)
    end as order_timestamp,
    coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
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
    case when scs.overdue_from is not null and scs.overdue_from <= now_ref.current_time then 0 else 1 end as urgency_rank,
    case
        when scs.overdue_from is not null and scs.overdue_from <= now_ref.current_time then scs.overdue_from
        when scs.planned_from is null then scs.available_from
        when scs.available_from is null then scs.planned_from
        else greatest(scs.available_from, scs.planned_from)
    end as order_timestamp,
    coalesce(slb.sort_index, 0) as lernbereich_sort_index,
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
    coalesce(sas.sort_index, 0) as lernbereich_sort_index,
    0 as step_depth,
    0 as check_order,
    coalesce(sas.sort_bucket, 50) as sort_bucket,
    coalesce(sas.sort_index, 0) as sort_index
from public.session_activity_state sas
cross join now_ref
where sas.session_id = p_session_id
  and sas.activity_type = 'flashcards'
  and sas.status = 'due'
  and sas.due_at <= now_ref.current_time;
$$;

create or replace function public.pick_feed_cursor(p_session_id uuid default null)
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
    next_available_from timestamptz
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
    end if;

    if current_item.activity_key is not null
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
            null::timestamptz;
        return;
    end if;

    select *
    into next_item
    from public.feed_cursor_open_items(resolved_session_id)
    where urgency_rank = 0
       or coalesce(order_timestamp, '-infinity'::timestamptz) <= now()
    order by
        class_rank,
        urgency_rank,
        coalesce(order_timestamp, '-infinity'::timestamptz),
        step_depth desc,
        lernbereich_sort_index,
        check_order,
        sort_bucket,
        sort_index,
        activity_key
    limit 1;

    if next_item.activity_key is not null then
        next_selection_reason := case
            when cursor_row.current_activity_key is null then
                case when cursor_row.selected_at is null then 'initial' else 'auto_pick' end
            when current_item.activity_key is null then 'invalidated'
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
            null::timestamptz;
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
            next_waiting_from;
        return;
    end if;

    return;
end;
$$;

create or replace function public.keep_current_feed_activity(p_activity_key text)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid;
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    picked_cursor record;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_activity_key is null then
        return false;
    end if;

    select id
    into resolved_session_id
    from public.learning_sessions
    where user_id = current_user_id
      and status = 'active'
    order by started_at desc
    limit 1;

    if resolved_session_id is null then
        return false;
    end if;

    select *
    into picked_cursor
    from public.pick_feed_cursor(resolved_session_id)
    limit 1;

    if coalesce(picked_cursor.current_activity_key, '') <> normalized_activity_key then
        return false;
    end if;

    return public.renew_current_feed_cursor(resolved_session_id, normalized_activity_key, 'repeat_request');
end;
$$;

create or replace function public.release_current_feed_activity(p_activity_key text)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid;
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    picked_cursor record;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_activity_key is null then
        return false;
    end if;

    select id
    into resolved_session_id
    from public.learning_sessions
    where user_id = current_user_id
      and status = 'active'
    order by started_at desc
    limit 1;

    if resolved_session_id is null then
        return false;
    end if;

    select *
    into picked_cursor
    from public.pick_feed_cursor(resolved_session_id)
    limit 1;

    if coalesce(picked_cursor.current_activity_key, '') <> normalized_activity_key then
        return false;
    end if;

    perform public.clear_current_feed_cursor(resolved_session_id, normalized_activity_key);
    return true;
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

    perform public.replan_session(active_session_id);

    return active_session_id;
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
    v_remaining_recalls integer;
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
    into v_remaining_recalls
    from public.session_check_state scs
    join public.session_lernbereiche slb
        on slb.session_id = scs.session_id
        and slb.lernbereich_slug = split_part(scs.check_id, '__', 2)
    where scs.session_id = p_session_id
      and slb.gebiet = v_gebiet
      and slb.sort_index <= v_sort_index
      and scs.current_step_key in ('training', 'recall')
      and scs.current_step_status <> 'blocked'
      and not exists (
          select 1
          from public.session_check_exclusions sce
          where sce.session_id = p_session_id
            and sce.check_id = scs.check_id
      );

    if v_remaining_recalls > 0 then
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

    update public.session_check_state scs
    set current_step_status = 'due'
    from public.session_lernbereiche slb
    where scs.session_id = p_session_id
      and slb.session_id = p_session_id
      and slb.lernbereich_slug = split_part(scs.check_id, '__', 2)
      and slb.gebiet = v_gebiet
      and slb.sort_index = v_next_sort_index
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'blocked';

    update public.session_activity_state sas
    set status = 'due',
        due_at = now()
    from public.session_lernbereiche slb
    where sas.session_id = p_session_id
      and slb.session_id = p_session_id
      and slb.lernbereich_slug = sas.lernbereich_slug
      and sas.activity_type = 'start'
      and slb.gebiet = v_gebiet
      and slb.sort_index = v_next_sort_index
      and sas.status = 'blocked';

    perform public.replan_session(p_session_id);
end;
$$;

create or replace function public.resolve_flashcard_round(
    p_round_id uuid,
    p_decision_key text
)
returns public.session_activity_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_decision_key text := lower(coalesce(nullif(trim(p_decision_key), ''), ''));
    matched_round public.session_flashcard_rounds;
    reviewed_count integer;
    total_count integer;
    next_activity_due_at timestamptz;
    next_activity_status text;
    updated_activity public.session_activity_state;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_round_id is null then
        raise exception 'round_id is required';
    end if;

    if normalized_decision_key not in ('complete', 'keep_open') then
        raise exception 'Unsupported decision_key';
    end if;

    select rounds.*
    into matched_round
    from public.session_flashcard_rounds as rounds
    join public.learning_sessions
      on learning_sessions.id = rounds.session_id
    where rounds.id = p_round_id
      and rounds.status = 'active'
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
    for update of rounds;

    if matched_round.id is null then
        raise exception 'Active flashcard round not found';
    end if;

    select count(*), count(reviewed_at)
    into total_count, reviewed_count
    from public.session_flashcard_round_cards
    where round_id = matched_round.id;

    if total_count = 0 or reviewed_count < total_count then
        raise exception 'Flashcard round is not fully reviewed';
    end if;

    update public.session_flashcard_rounds
    set status = 'completed',
        completed_at = now()
    where id = matched_round.id;

    if normalized_decision_key = 'keep_open' then
        next_activity_due_at := now();
        next_activity_status := 'due';
    else
        select min(card_state.next_due_at)
        into next_activity_due_at
        from public.session_flashcard_round_cards as round_cards
        join public.session_flashcard_card_state as card_state
          on card_state.session_id = matched_round.session_id
         and card_state.card_id = round_cards.card_id
        where round_cards.round_id = matched_round.id;

        next_activity_due_at := coalesce(next_activity_due_at, now());
        next_activity_status := case when next_activity_due_at <= now() then 'due' else 'completed' end;
    end if;

    update public.session_activity_state
    set status = next_activity_status,
        due_at = next_activity_due_at,
        last_outcome_key = normalized_decision_key
    where session_id = matched_round.session_id
      and activity_key = matched_round.activity_key
    returning * into updated_activity;

    if updated_activity.session_id is null then
        raise exception 'Flashcard activity not found';
    end if;

    if normalized_decision_key = 'complete' then
        perform public.bump_feed_activity_completion_count();
        perform public.clear_current_feed_cursor(matched_round.session_id, matched_round.activity_key);
    else
        perform public.renew_current_feed_cursor(matched_round.session_id, matched_round.activity_key, 'repeat_request');
    end if;

    return updated_activity;
end;
$$;

select public.replan_session(id)
from public.learning_sessions
where status = 'active';

revoke all on function public.get_feed_cursor_lock_interval() from public;
revoke all on function public.get_feed_cursor_lock_interval() from anon;
revoke all on function public.feed_check_sequence_number(text) from public;
revoke all on function public.feed_check_sequence_number(text) from anon;
revoke all on function public.feed_step_depth_rank(text) from public;
revoke all on function public.feed_step_depth_rank(text) from anon;
revoke all on function public.clear_current_feed_cursor(uuid, text) from public;
revoke all on function public.clear_current_feed_cursor(uuid, text) from anon;
revoke all on function public.renew_current_feed_cursor(uuid, text, text) from public;
revoke all on function public.renew_current_feed_cursor(uuid, text, text) from anon;
revoke all on function public.require_current_feed_cursor(uuid, text) from public;
revoke all on function public.require_current_feed_cursor(uuid, text) from anon;
revoke all on function public.replan_session(uuid) from public;
revoke all on function public.replan_session(uuid) from anon;
revoke all on function public.feed_cursor_open_items(uuid) from public;
revoke all on function public.feed_cursor_open_items(uuid) from anon;
revoke all on function public.pick_feed_cursor(uuid) from public;
revoke all on function public.pick_feed_cursor(uuid) from anon;
revoke all on function public.keep_current_feed_activity(text) from public;
revoke all on function public.keep_current_feed_activity(text) from anon;
revoke all on function public.release_current_feed_activity(text) from public;
revoke all on function public.release_current_feed_activity(text) from anon;

grant execute on function public.pick_feed_cursor(uuid) to authenticated;
grant execute on function public.keep_current_feed_activity(text) to authenticated;
grant execute on function public.release_current_feed_activity(text) to authenticated;
