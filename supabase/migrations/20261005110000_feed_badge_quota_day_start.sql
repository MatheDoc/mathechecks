-- Fix: Tagespensum im Badge auf den Stand zu Tagesbeginn beziehen.
-- get_session_required_activities_per_day rechnet mit den AKTUELL offenen Schritten,
-- in denen heute Erledigtes schon fehlt; consumed_today davon nochmals abzuziehen
-- zählte heutige Schritte doppelt (z. B. 43 offen -> Badge 41).

create or replace function public.feed_attention_summary(p_session_id uuid default null)
returns table (
    session_id uuid,
    overdue_count integer,
    due_count integer
)
language plpgsql
stable
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid := p_session_id;
    resolved_target_date date;
    resolved_target_source text;
    configured_activities_per_day numeric;
    required_activities_per_day numeric;
    consumed_today integer := 0;
    remaining_activity_count integer := 0;
    remaining_today_quota integer := 0;
    v_overdue_count integer := 0;
    v_due_count integer := 0;
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
        return query select null::uuid, 0, 0;
        return;
    end if;

    select
        coalesce(sum(case when oi.urgency_rank = 0 then 1 else 0 end), 0)::integer,
        coalesce(sum(case
            when oi.urgency_rank = 1 then 1
            when oi.urgency_rank = 2 and oi.planned_from is not null and oi.planned_from <= now() then 1
            else 0
        end), 0)::integer
    into v_overdue_count, v_due_count
    from public.feed_cursor_open_items(resolved_session_id) as oi;

    select ls.target_date,
           ls.target_source,
           greatest(coalesce(ls.activities_per_day, public.get_default_activities_per_day()), 0.1),
           case
               when ls.daily_core_budget_date = current_date then coalesce(ls.daily_core_budget_used, 0)
               else 0
           end
    into resolved_target_date, resolved_target_source, configured_activities_per_day, consumed_today
    from public.learning_sessions ls
    where ls.id = resolved_session_id;

    remaining_activity_count := coalesce(public.get_session_remaining_activity_count(resolved_session_id), 0);

    if resolved_target_date is not null and resolved_target_source = 'explicit' then
        required_activities_per_day :=
            (remaining_activity_count + consumed_today)::numeric
            / greatest(resolved_target_date - current_date, 1)::numeric;
    end if;

    remaining_today_quota := least(
        greatest(
            ceil(greatest(configured_activities_per_day, coalesce(required_activities_per_day, 0), 0.1))::integer
            - consumed_today,
            0
        ),
        remaining_activity_count
    );

    return query
    select
        resolved_session_id,
        v_overdue_count,
        greatest(v_due_count, remaining_today_quota - v_overdue_count, 0)::integer;
end;
$$;

revoke all on function public.feed_attention_summary(uuid) from public;
revoke all on function public.feed_attention_summary(uuid) from anon;
grant execute on function public.feed_attention_summary(uuid) to authenticated;

notify pgrst, 'reload schema';
