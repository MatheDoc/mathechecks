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

  select id
    into deleted_session_id
    from public.learning_sessions
   where user_id = current_user_id
     and status = 'active'
   order by started_at desc
   limit 1
   for update;

  if deleted_session_id is null then
    return null;
  end if;

  delete from public.learning_sessions
   where id = deleted_session_id
     and user_id = current_user_id
     and status = 'active';

  return deleted_session_id;
end;
$$;

revoke all on function public.delete_active_learning_session() from public;
grant execute on function public.delete_active_learning_session() to authenticated;