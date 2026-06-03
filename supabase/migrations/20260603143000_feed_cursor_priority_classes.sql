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
    end if;

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
            null::timestamptz;
        return;
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