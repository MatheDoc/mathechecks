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
        return null;
    end if;

    delete from public.learning_activity_attempts
    where user_id = current_user_id
      and session_id = deleted_session_id;

    delete from public.user_feed_activity_deferrals as deferrals
    where deferrals.user_id = current_user_id
      and (
          exists (
              select 1
              from public.session_activity_state as activity_state
              where activity_state.session_id = deleted_session_id
                and activity_state.activity_key = deferrals.activity_key
          )
          or exists (
              select 1
              from public.session_check_state as check_state
              where check_state.session_id = deleted_session_id
                and deferrals.activity_key like 'check:' || check_state.check_id || ':%'
          )
      );

    delete from public.learning_sessions
    where id = deleted_session_id
      and user_id = current_user_id
      and status = 'active';

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

    delete from public.user_feed_activity_deferrals
    where user_id = current_user_id
      and activity_key like 'retention:%';

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
end;
$$;

revoke all on function public.delete_all_retention_data() from public;
revoke all on function public.delete_all_retention_data() from anon;
grant execute on function public.delete_all_retention_data() to authenticated;