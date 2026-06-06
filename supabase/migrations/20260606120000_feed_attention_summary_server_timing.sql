-- Serverseitige Aggregation des Feed-Badge-Werts.
--
-- Das Badge zeigt rein overdue + due. Bisher rekonstruierte das Frontend die
-- Zeitklasse aus Browser-Zeitstempeln; kleine Uhrabweichungen zwischen Client
-- und Server konnten frisch geplante (server-fällige) Schritte fälschlich als
-- nur `available` einstufen und so aus dem Badge fallen lassen.
--
-- Diese RPC nutzt dieselbe serverseitige Zeitklasse wie `pick_feed_cursor`
-- (über `feed_cursor_open_items.urgency_rank`) und zählt offene Core-Schritte
-- nach Dringlichkeit:
--   urgency_rank = 0  -> overdue
--   urgency_rank = 1  -> due
--   urgency_rank = 2  -> available (zählt nicht zum Badge)
--
-- Retention-Flashcards bleiben ein eigener user-scoped Kopf außerhalb des
-- Core-Feeds und werden weiterhin getrennt im Frontend gezählt.

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

    return query
    select
        resolved_session_id,
        coalesce(sum(case when oi.urgency_rank = 0 then 1 else 0 end), 0)::integer as overdue_count,
        coalesce(sum(case when oi.urgency_rank = 1 then 1 else 0 end), 0)::integer as due_count
    from public.feed_cursor_open_items(resolved_session_id) as oi;
end;
$$;

revoke all on function public.feed_attention_summary(uuid) from public;
revoke all on function public.feed_attention_summary(uuid) from anon;
grant execute on function public.feed_attention_summary(uuid) to authenticated;
