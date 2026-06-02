-- Fix: Cursor-Helper sollen nach `pick_feed_cursor(...)` nicht auf ein
-- moeglicherweise uninitialisiertes `record` zugreifen. Stattdessen wird der
-- serverseitige Cursor aktualisiert und danach direkt gegen
-- `session_feed_cursor.current_activity_key` geprueft.

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

    if exists (
        select 1
        from public.session_feed_cursor
        where session_id = p_session_id
          and current_activity_key = normalized_activity_key
    ) then
        return;
    end if;

    perform public.pick_feed_cursor(p_session_id);

    if exists (
        select 1
        from public.session_feed_cursor
        where session_id = p_session_id
          and current_activity_key = normalized_activity_key
    ) then
        return;
    end if;

    raise exception 'Feed activity is not the current cursor';
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

    perform public.pick_feed_cursor(resolved_session_id);

    if not exists (
        select 1
        from public.session_feed_cursor
        where session_id = resolved_session_id
          and current_activity_key = normalized_activity_key
    ) then
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

    perform public.pick_feed_cursor(resolved_session_id);

    if not exists (
        select 1
        from public.session_feed_cursor
        where session_id = resolved_session_id
          and current_activity_key = normalized_activity_key
    ) then
        return false;
    end if;

    perform public.clear_current_feed_cursor(resolved_session_id, normalized_activity_key);
    return true;
end;
$$;