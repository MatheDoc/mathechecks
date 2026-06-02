-- Fix: Wenn das Frontend eine gueltige Feed-Aktivitaet ueber den lokalen
-- Session-Fallback geoeffnet hat, kann der persistierte Cursor trotzdem leer
-- oder veraltet sein. Bevor Abschluesse abgelehnt werden, soll der Server
-- daher einmal selbst `pick_feed_cursor(...)` ausfuehren und nur dann
-- ablehnen, wenn die Aktivitaet auch danach nicht der aktuelle Cursor ist.

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
    picked_cursor record;
begin
    if p_session_id is null or normalized_activity_key is null then
        raise exception 'Current feed cursor is required';
    end if;

    if exists (
        select 1
        from public.session_feed_cursor
        where session_id = p_session_id
          and current_activity_key = normalized_activity_key
    ) then
        return;
    end if;

    select *
    into picked_cursor
    from public.pick_feed_cursor(p_session_id)
    limit 1;

    if coalesce(picked_cursor.current_activity_key, '') = normalized_activity_key then
        return;
    end if;

    raise exception 'Feed activity is not the current cursor';
end;
$$;