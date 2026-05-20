create table public.learning_activity_attempts (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    session_id uuid null references public.learning_sessions(id) on delete set null,
    lernbereich_slug text not null check (char_length(trim(lernbereich_slug)) > 0),
    check_id text null check (check_id is null or char_length(trim(check_id)) > 0),
    module_key text not null check (module_key in ('recall', 'feynman')),
    outcome_key text not null check (outcome_key in ('can_do', 'repeat')),
    created_at timestamptz not null default now()
);

create index learning_activity_attempts_user_created_at_idx
    on public.learning_activity_attempts (user_id, created_at desc);

create index learning_activity_attempts_session_created_at_idx
    on public.learning_activity_attempts (session_id, created_at desc)
    where session_id is not null;

create index learning_activity_attempts_check_lookup_idx
    on public.learning_activity_attempts (user_id, lernbereich_slug, check_id, module_key, created_at desc);

create or replace function public.record_check_module_attempt(
    p_lernbereich_slug text,
    p_check_id text,
    p_module_key text,
    p_outcome_key text
)
returns public.learning_activity_attempts
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    normalized_check_id text := nullif(trim(p_check_id), '');
    normalized_module_key text := lower(coalesce(nullif(trim(p_module_key), ''), ''));
    normalized_outcome_key text := lower(coalesce(nullif(trim(p_outcome_key), ''), ''));
    matched_session_id uuid;
    inserted_attempt public.learning_activity_attempts;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    if normalized_module_key not in ('recall', 'feynman') then
        raise exception 'Unsupported module_key';
    end if;

    if normalized_outcome_key not in ('can_do', 'repeat') then
        raise exception 'Unsupported outcome_key';
    end if;

    select learning_sessions.id
    into matched_session_id
    from public.learning_sessions
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and exists (
          select 1
          from public.session_lernbereiche
          where session_lernbereiche.session_id = learning_sessions.id
            and session_lernbereiche.lernbereich_slug = normalized_lernbereich_slug
      )
      and not exists (
          select 1
          from public.session_check_exclusions
          where session_check_exclusions.session_id = learning_sessions.id
            and session_check_exclusions.check_id = normalized_check_id
      )
    limit 1;

    insert into public.learning_activity_attempts (
        user_id,
        session_id,
        lernbereich_slug,
        check_id,
        module_key,
        outcome_key
    )
    values (
        current_user_id,
        matched_session_id,
        normalized_lernbereich_slug,
        normalized_check_id,
        normalized_module_key,
        normalized_outcome_key
    )
    returning * into inserted_attempt;

    return inserted_attempt;
end;
$$;

grant select on public.learning_activity_attempts to authenticated;

alter table public.learning_activity_attempts enable row level security;

create policy learning_activity_attempts_select_own
    on public.learning_activity_attempts
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

revoke all on function public.record_check_module_attempt(text, text, text, text) from public;

grant execute on function public.record_check_module_attempt(text, text, text, text) to authenticated;