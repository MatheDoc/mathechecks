create table public.session_check_state (
    session_id uuid not null references public.learning_sessions(id) on delete cascade,
    check_id text not null check (char_length(trim(check_id)) > 0),
    current_step_key text not null check (
        current_step_key in (
            'training_1',
            'recall',
            'training_2',
            'feynman',
            'training_3',
            'kompetenzliste_gate',
            'check_completed'
        )
    ),
    current_step_status text not null check (current_step_status in ('blocked', 'due', 'completed')),
    last_outcome_key text null check (last_outcome_key in ('complete', 'keep_open', 'can_do', 'repeat')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (session_id, check_id)
);

create index session_check_state_session_status_idx
    on public.session_check_state (session_id, current_step_status, current_step_key);

drop trigger if exists set_session_check_state_updated_at on public.session_check_state;
create trigger set_session_check_state_updated_at
    before update on public.session_check_state
    for each row execute function public.set_updated_at();

grant select on public.session_check_state to authenticated;

alter table public.session_check_state enable row level security;

create policy session_check_state_select_own
    on public.session_check_state
    for select
    to authenticated
    using (
        exists (
            select 1
            from public.learning_sessions
            where learning_sessions.id = session_check_state.session_id
              and learning_sessions.user_id = (select auth.uid())
        )
    );

drop function if exists public.save_active_learning_session(text[], text[], integer);

create or replace function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_tempo_days integer default null,
    p_included_check_ids text[] default array[]::text[]
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    active_session_id uuid;
    active_tempo_days integer;
    effective_tempo_days integer;
    normalized_lernbereiche text[];
    normalized_excluded_check_ids text[];
    normalized_included_check_ids text[];
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_tempo_days is not null and p_tempo_days <= 0 then
        raise exception 'tempo_days must be positive';
    end if;

    select id, tempo_days
    into active_session_id, active_tempo_days
    from public.learning_sessions
    where user_id = current_user_id
      and status = 'active'
    for update;

    normalized_lernbereiche := array(
        select distinct slug
        from (
            select nullif(trim(lb.value), '') as slug
            from unnest(coalesce(p_lernbereiche, array[]::text[])) as lb(value)
        ) normalized
        where slug is not null
    );

    normalized_excluded_check_ids := array(
        select distinct check_id
        from (
            select nullif(trim(excluded.value), '') as check_id
            from unnest(coalesce(p_excluded_check_ids, array[]::text[])) as excluded(value)
        ) normalized
        where check_id is not null
    );

    normalized_included_check_ids := array(
        select distinct check_id
        from (
            select nullif(trim(included.value), '') as check_id
            from unnest(coalesce(p_included_check_ids, array[]::text[])) as included(value)
        ) normalized
        where check_id is not null
    );

    if coalesce(array_length(normalized_lernbereiche, 1), 0) = 0 then
        if active_session_id is not null then
            update public.learning_sessions
            set status = 'aborted',
                ended_at = coalesce(ended_at, now())
            where id = active_session_id
              and status = 'active';
        end if;

        return null;
    end if;

    effective_tempo_days := coalesce(p_tempo_days, active_tempo_days, 1);

    if active_session_id is null then
        begin
            insert into public.learning_sessions (user_id, status, tempo_days)
            values (current_user_id, 'active', effective_tempo_days)
            returning id into active_session_id;
        exception
            when unique_violation then
                raise exception 'An active learning session already exists';
        end;
    else
        update public.learning_sessions
        set tempo_days = effective_tempo_days
        where id = active_session_id;

        delete from public.session_check_exclusions
        where session_id = active_session_id;

        delete from public.session_lernbereiche
        where session_id = active_session_id;
    end if;

    insert into public.session_lernbereiche (session_id, lernbereich_slug)
    select active_session_id, slug
    from unnest(normalized_lernbereiche) as lernbereiche(slug);

    if coalesce(array_length(normalized_excluded_check_ids, 1), 0) > 0 then
        insert into public.session_check_exclusions (session_id, check_id)
        select active_session_id, check_id
        from unnest(normalized_excluded_check_ids) as excluded_checks(check_id);
    end if;

    delete from public.session_check_state
    where session_id = active_session_id
      and not (check_id = any(coalesce(normalized_included_check_ids, array[]::text[])));

    if coalesce(array_length(normalized_included_check_ids, 1), 0) > 0 then
        insert into public.session_check_state (
            session_id,
            check_id,
            current_step_key,
            current_step_status,
            last_outcome_key
        )
        select
            active_session_id,
            included_check_id,
            'training_1',
            'due',
            null
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    return active_session_id;
end;
$$;

create or replace function public.complete_current_training_step(
    p_check_id text
)
returns public.session_check_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_check_id text := nullif(trim(p_check_id), '');
    updated_state public.session_check_state;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    update public.session_check_state
    set current_step_key = case current_step_key
            when 'training_1' then 'recall'
            when 'training_2' then 'feynman'
            when 'training_3' then 'kompetenzliste_gate'
            else current_step_key
        end,
        current_step_status = case current_step_key
            when 'training_1' then 'due'
            when 'training_2' then 'due'
            when 'training_3' then 'due'
            else current_step_status
        end,
        last_outcome_key = 'complete'
    from public.learning_sessions
    where learning_sessions.id = session_check_state.session_id
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and session_check_state.check_id = normalized_check_id
      and session_check_state.current_step_key in ('training_1', 'training_2', 'training_3')
      and session_check_state.current_step_status = 'due'
    returning session_check_state.* into updated_state;

    if updated_state.session_id is null then
        raise exception 'Due training step not found';
    end if;

    return updated_state;
end;
$$;

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

    if matched_session_id is not null then
        if normalized_module_key = 'recall' then
            if normalized_outcome_key = 'can_do' then
                update public.session_check_state
                set current_step_key = 'training_2',
                    current_step_status = 'due',
                    last_outcome_key = 'can_do'
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'recall'
                  and current_step_status = 'due';
            else
                update public.session_check_state
                set last_outcome_key = 'repeat'
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'recall'
                  and current_step_status = 'due';
            end if;
        elsif normalized_module_key = 'feynman' then
            if normalized_outcome_key = 'can_do' then
                update public.session_check_state
                set current_step_key = 'training_3',
                    current_step_status = 'due',
                    last_outcome_key = 'can_do'
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'feynman'
                  and current_step_status = 'due';
            else
                update public.session_check_state
                set last_outcome_key = 'repeat'
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'feynman'
                  and current_step_status = 'due';
            end if;
        end if;
    end if;

    return inserted_attempt;
end;
$$;

revoke all on function public.save_active_learning_session(text[], text[], integer, text[]) from public;
revoke all on function public.complete_current_training_step(text) from public;
revoke all on function public.record_check_module_attempt(text, text, text, text) from public;

grant execute on function public.save_active_learning_session(text[], text[], integer, text[]) to authenticated;
grant execute on function public.complete_current_training_step(text) to authenticated;
grant execute on function public.record_check_module_attempt(text, text, text, text) to authenticated;