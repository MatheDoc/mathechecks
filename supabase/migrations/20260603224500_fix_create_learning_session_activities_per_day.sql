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
        raise exception 'activities_per_day must be positive';
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

    insert into public.learning_sessions (user_id, status, activities_per_day)
    values (current_user_id, 'active', p_tempo_days::numeric)
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

grant execute on function public.create_learning_session(integer, text[], text[]) to authenticated;