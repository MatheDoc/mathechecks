create extension if not exists pgcrypto with schema extensions;

create table public.profiles (
    user_id uuid primary key references auth.users(id) on delete cascade,
    display_name text null,
    role text not null default 'user' check (role in ('user', 'admin')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.learning_sessions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    status text not null check (status in ('active', 'completed', 'aborted')),
    tempo_days integer not null default 1 check (tempo_days > 0),
    started_at timestamptz not null default now(),
    ended_at timestamptz null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint learning_sessions_status_ended_at_check check (
        (status = 'active' and ended_at is null)
        or (status in ('completed', 'aborted') and ended_at is not null)
    )
);

create table public.session_lernbereiche (
    session_id uuid not null references public.learning_sessions(id) on delete cascade,
    lernbereich_slug text not null check (char_length(trim(lernbereich_slug)) > 0),
    created_at timestamptz not null default now(),
    primary key (session_id, lernbereich_slug)
);

create table public.session_check_exclusions (
    session_id uuid not null references public.learning_sessions(id) on delete cascade,
    check_id text not null check (char_length(trim(check_id)) > 0),
    created_at timestamptz not null default now(),
    primary key (session_id, check_id)
);

create unique index learning_sessions_one_active_per_user_idx
    on public.learning_sessions (user_id)
    where status = 'active';

create index learning_sessions_user_id_idx
    on public.learning_sessions (user_id);

create index session_lernbereiche_session_id_idx
    on public.session_lernbereiche (session_id);

create index session_check_exclusions_session_id_idx
    on public.session_check_exclusions (session_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at := now();
    return new;
end;
$$;

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (user_id, display_name, role)
    values (
        new.id,
        nullif(trim(coalesce(new.raw_user_meta_data ->> 'display_name', '')), ''),
        'user'
    )
    on conflict (user_id) do nothing;

    return new;
end;
$$;

create or replace function public.update_own_profile(p_display_name text)
returns public.profiles
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    updated_profile public.profiles;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    update public.profiles
    set display_name = nullif(trim(p_display_name), '')
    where user_id = current_user_id
    returning * into updated_profile;

    if updated_profile.user_id is null then
        raise exception 'Profile not found';
    end if;

    return updated_profile;
end;
$$;

create or replace function public.create_learning_session(
    p_tempo_days integer,
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[]
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    new_session_id uuid;
    normalized_lernbereiche text[];
    normalized_excluded_check_ids text[];
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_tempo_days is null or p_tempo_days <= 0 then
        raise exception 'tempo_days must be positive';
    end if;

    normalized_lernbereiche := array(
        select distinct slug
        from (
            select nullif(trim(lb.value), '') as slug
            from unnest(coalesce(p_lernbereiche, array[]::text[])) as lb(value)
        ) normalized
        where slug is not null
    );

    if coalesce(array_length(normalized_lernbereiche, 1), 0) = 0 then
        raise exception 'At least one lernbereich is required';
    end if;

    normalized_excluded_check_ids := array(
        select distinct check_id
        from (
            select nullif(trim(excluded.value), '') as check_id
            from unnest(coalesce(p_excluded_check_ids, array[]::text[])) as excluded(value)
        ) normalized
        where check_id is not null
    );

    if exists (
        select 1
        from public.learning_sessions
        where user_id = current_user_id
          and status = 'active'
    ) then
        raise exception 'An active learning session already exists';
    end if;

    insert into public.learning_sessions (user_id, status, tempo_days)
    values (current_user_id, 'active', p_tempo_days)
    returning id into new_session_id;

    insert into public.session_lernbereiche (session_id, lernbereich_slug)
    select new_session_id, slug
    from unnest(normalized_lernbereiche) as lernbereiche(slug);

    if coalesce(array_length(normalized_excluded_check_ids, 1), 0) > 0 then
        insert into public.session_check_exclusions (session_id, check_id)
        select new_session_id, check_id
        from unnest(normalized_excluded_check_ids) as excluded_checks(check_id);
    end if;

    return new_session_id;
end;
$$;

create or replace function public.finish_learning_session(
    p_session_id uuid,
    p_status text
)
returns public.learning_sessions
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    updated_session public.learning_sessions;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_status not in ('completed', 'aborted') then
        raise exception 'Unsupported session status';
    end if;

    update public.learning_sessions
    set status = p_status,
        ended_at = coalesce(ended_at, now())
    where id = p_session_id
      and user_id = current_user_id
      and status = 'active'
    returning * into updated_session;

    if updated_session.id is null then
        raise exception 'Active learning session not found';
    end if;

    return updated_session;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

drop trigger if exists set_profiles_updated_at on public.profiles;
create trigger set_profiles_updated_at
    before update on public.profiles
    for each row execute function public.set_updated_at();

drop trigger if exists set_learning_sessions_updated_at on public.learning_sessions;
create trigger set_learning_sessions_updated_at
    before update on public.learning_sessions
    for each row execute function public.set_updated_at();

grant select on public.profiles to authenticated;
grant select on public.learning_sessions to authenticated;
grant select on public.session_lernbereiche to authenticated;
grant select on public.session_check_exclusions to authenticated;

alter table public.profiles enable row level security;
alter table public.learning_sessions enable row level security;
alter table public.session_lernbereiche enable row level security;
alter table public.session_check_exclusions enable row level security;

create policy profiles_select_own
    on public.profiles
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy learning_sessions_select_own
    on public.learning_sessions
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy session_lernbereiche_select_own
    on public.session_lernbereiche
    for select
    to authenticated
    using (
        exists (
            select 1
            from public.learning_sessions
            where learning_sessions.id = session_lernbereiche.session_id
              and learning_sessions.user_id = (select auth.uid())
        )
    );

create policy session_check_exclusions_select_own
    on public.session_check_exclusions
    for select
    to authenticated
    using (
        exists (
            select 1
            from public.learning_sessions
            where learning_sessions.id = session_check_exclusions.session_id
              and learning_sessions.user_id = (select auth.uid())
        )
    );

revoke all on function public.update_own_profile(text) from public;
revoke all on function public.create_learning_session(integer, text[], text[]) from public;
revoke all on function public.finish_learning_session(uuid, text) from public;

grant execute on function public.update_own_profile(text) to authenticated;
grant execute on function public.create_learning_session(integer, text[], text[]) to authenticated;
grant execute on function public.finish_learning_session(uuid, text) to authenticated;