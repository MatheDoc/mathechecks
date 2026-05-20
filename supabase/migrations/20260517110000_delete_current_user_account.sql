create or replace function public.delete_current_user_account(p_confirmation text)
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

    if upper(trim(coalesce(p_confirmation, ''))) <> 'LÖSCHEN' then
        raise exception 'Confirmation required';
    end if;

    delete from auth.users
    where id = current_user_id;

    if not found then
        raise exception 'Account not found';
    end if;
end;
$$;

revoke all on function public.delete_current_user_account(text) from public;
grant execute on function public.delete_current_user_account(text) to authenticated;