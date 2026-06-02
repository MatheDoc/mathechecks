-- Fix: `pick_feed_cursor` darf bei fehlenden Rows weder auf ein nicht
-- initialisiertes `current_item` noch auf ein nicht initialisiertes
-- `next_item`-Record zugreifen. Das tritt vor allem bei frischen Sessions auf,
-- wenn noch kein Cursor gesetzt ist oder aktuell kein sofort offenes Element
-- existiert und erst der Waiting-Pfad greifen soll.

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
    on conflict (session_id) do nothing;

    select *
    into cursor_row
    from public.session_feed_cursor
    where session_id = resolved_session_id
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
                null::timestamptz;
            return;
        end if;
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

    has_next_item := found;

    if has_next_item then
        next_selection_reason := case
            when cursor_row.current_activity_key is null then
                case when cursor_row.selected_at is null then 'initial' else 'auto_pick' end
            when not has_current_item then 'invalidated'
            when cursor_row.locked_until is not null and cursor_row.locked_until <= now() then 'lock_expired'
            else 'auto_pick'
        end;

        update public.session_feed_cursor
        set current_activity_key = next_item.activity_key,
            locked_until = now() + public.get_feed_cursor_lock_interval(),
            selected_at = now(),
            selection_reason = next_selection_reason
        where session_id = resolved_session_id;

        select *
        into cursor_row
        from public.session_feed_cursor
        where session_id = resolved_session_id;

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