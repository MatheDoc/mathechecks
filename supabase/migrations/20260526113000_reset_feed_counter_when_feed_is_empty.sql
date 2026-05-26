create or replace function public.reset_feed_progress_if_empty()
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    has_active_session boolean := false;
    has_retention_scope boolean := false;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    select exists (
        select 1
        from public.learning_sessions
        where user_id = current_user_id
          and status = 'active'
    )
    into has_active_session;

    select exists (
        select 1
        from public.user_retention_scopes
        where user_id = current_user_id
          and activity_type = 'flashcards'
          and scope_type = 'lernbereich'
    )
    into has_retention_scope;

    if has_active_session or has_retention_scope then
        return;
    end if;

    delete from public.user_feed_activity_counters
    where user_id = current_user_id;
end;
$$;

revoke all on function public.reset_feed_progress_if_empty() from public;
revoke all on function public.reset_feed_progress_if_empty() from anon;
revoke all on function public.reset_feed_progress_if_empty() from authenticated;

create or replace function public.delete_active_learning_session()
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    deleted_session_id uuid;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    select learning_sessions.id
    into deleted_session_id
    from public.learning_sessions
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
    order by learning_sessions.started_at desc
    limit 1
    for update;

    if deleted_session_id is null then
        perform public.reset_feed_progress_if_empty();
        return null;
    end if;

    delete from public.learning_activity_attempts
    where user_id = current_user_id
      and session_id = deleted_session_id;

    delete from public.learning_sessions
    where id = deleted_session_id
      and user_id = current_user_id
      and status = 'active';

    perform public.reset_feed_progress_if_empty();

    return deleted_session_id;
end;
$$;

revoke all on function public.delete_active_learning_session() from public;
revoke all on function public.delete_active_learning_session() from anon;
grant execute on function public.delete_active_learning_session() to authenticated;

create or replace function public.delete_all_retention_data()
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    delete from public.retention_flashcard_rounds
    where user_id = current_user_id;

    delete from public.retention_flashcard_card_state
    where user_id = current_user_id;

    delete from public.user_retention_check_exclusions
    where user_id = current_user_id;

    delete from public.user_retention_scopes
    where user_id = current_user_id
      and activity_type = 'flashcards'
      and scope_type = 'lernbereich';

    perform public.reset_feed_progress_if_empty();
end;
$$;

revoke all on function public.delete_all_retention_data() from public;
revoke all on function public.delete_all_retention_data() from anon;
grant execute on function public.delete_all_retention_data() to authenticated;