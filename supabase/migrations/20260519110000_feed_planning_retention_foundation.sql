alter table public.learning_sessions
    add column target_date date null,
    add column target_source text null check (target_source in ('explicit', 'suggested')),
    add column planning_timezone text not null default 'Europe/Berlin' check (char_length(trim(planning_timezone)) > 0),
    add column daily_new_release_limit integer not null default 3 check (daily_new_release_limit > 0),
    add column max_parallel_check_streams integer not null default 4 check (max_parallel_check_streams > 0),
    add column planning_revision integer not null default 1 check (planning_revision > 0);

alter table public.learning_sessions
    add constraint learning_sessions_target_date_source_check
    check (
        (target_date is null and target_source is null)
        or (target_date is not null and target_source in ('explicit', 'suggested'))
    );

alter table public.session_check_state
    add column last_completed_at timestamptz null;

update public.session_check_state
set last_completed_at = updated_at
where last_completed_at is null
  and last_outcome_key in ('complete', 'can_do');

create table public.user_retention_scopes (
    user_id uuid not null references auth.users(id) on delete cascade,
    activity_type text not null check (activity_type in ('flashcards')),
    scope_type text not null check (scope_type in ('lernbereich')),
    lernbereich_slug text not null check (char_length(trim(lernbereich_slug)) > 0),
    status text not null check (status in ('active', 'paused', 'opted_out')),
    source_session_id uuid null references public.learning_sessions(id) on delete set null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (user_id, activity_type, scope_type, lernbereich_slug)
);

create index user_retention_scopes_status_idx
    on public.user_retention_scopes (user_id, status, activity_type, scope_type, lernbereich_slug);

drop trigger if exists set_user_retention_scopes_updated_at on public.user_retention_scopes;
create trigger set_user_retention_scopes_updated_at
    before update on public.user_retention_scopes
    for each row execute function public.set_updated_at();

grant select on public.user_retention_scopes to authenticated;

alter table public.user_retention_scopes enable row level security;

create policy user_retention_scopes_select_own
    on public.user_retention_scopes
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create table public.retention_flashcard_card_state (
    user_id uuid not null references auth.users(id) on delete cascade,
    lernbereich_slug text not null check (char_length(trim(lernbereich_slug)) > 0),
    card_id text not null check (char_length(trim(card_id)) > 0),
    check_id text not null check (char_length(trim(check_id)) > 0),
    seen_count integer not null default 0 check (seen_count >= 0),
    level integer not null default 0 check (level >= 0),
    next_due_at timestamptz not null default now(),
    last_rating_key text null check (last_rating_key in ('hard', 'medium', 'easy')),
    last_reviewed_at timestamptz null,
    source_session_id uuid null references public.learning_sessions(id) on delete set null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (user_id, lernbereich_slug, card_id)
);

create index retention_flashcard_card_state_due_idx
    on public.retention_flashcard_card_state (user_id, lernbereich_slug, next_due_at);

drop trigger if exists set_retention_flashcard_card_state_updated_at on public.retention_flashcard_card_state;
create trigger set_retention_flashcard_card_state_updated_at
    before update on public.retention_flashcard_card_state
    for each row execute function public.set_updated_at();

grant select on public.retention_flashcard_card_state to authenticated;

alter table public.retention_flashcard_card_state enable row level security;

create policy retention_flashcard_card_state_select_own
    on public.retention_flashcard_card_state
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

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
    current_lernbereich_slug text;
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
        set tempo_days = effective_tempo_days,
            planning_revision = planning_revision + 1
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

    delete from public.session_flashcard_card_state
    where session_id = active_session_id
      and not (check_id = any(coalesce(normalized_included_check_ids, array[]::text[])));

    delete from public.session_flashcard_rounds
    where session_id = active_session_id
      and exists (
          select 1
          from public.session_flashcard_round_cards
          where session_flashcard_round_cards.round_id = session_flashcard_rounds.id
            and not (session_flashcard_round_cards.check_id = any(coalesce(normalized_included_check_ids, array[]::text[])))
      );

    delete from public.session_activity_state as activity
    where activity.session_id = active_session_id
      and activity.activity_type = 'flashcards'
      and activity.scope_type = 'lernbereich'
      and not (activity.lernbereich_slug = any(coalesce(normalized_lernbereiche, array[]::text[])));

    if coalesce(array_length(normalized_included_check_ids, 1), 0) > 0 then
        insert into public.session_check_state (
            session_id,
            check_id,
            current_step_key,
            current_step_status,
            last_outcome_key,
            last_completed_at
        )
        select
            active_session_id,
            included_check_id,
            'training_1',
            'due',
            null,
            null
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    foreach current_lernbereich_slug in array normalized_lernbereiche loop
        perform public.refresh_flashcard_activity_for_lernbereich(active_session_id, current_lernbereich_slug);
    end loop;

    return active_session_id;
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

    if p_status = 'completed' then
        insert into public.user_retention_scopes (
            user_id,
            activity_type,
            scope_type,
            lernbereich_slug,
            status,
            source_session_id
        )
        select
            current_user_id,
            'flashcards',
            'lernbereich',
            session_lernbereiche.lernbereich_slug,
            'active',
            updated_session.id
        from public.session_lernbereiche
        where session_lernbereiche.session_id = updated_session.id
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set source_session_id = excluded.source_session_id,
            status = case
                when public.user_retention_scopes.status in ('paused', 'opted_out') then public.user_retention_scopes.status
                else 'active'
            end;

        insert into public.retention_flashcard_card_state (
            user_id,
            lernbereich_slug,
            card_id,
            check_id,
            seen_count,
            level,
            next_due_at,
            last_rating_key,
            last_reviewed_at,
            source_session_id
        )
        select
            current_user_id,
            session_flashcard_card_state.lernbereich_slug,
            session_flashcard_card_state.card_id,
            session_flashcard_card_state.check_id,
            session_flashcard_card_state.seen_count,
            session_flashcard_card_state.level,
            session_flashcard_card_state.next_due_at,
            session_flashcard_card_state.last_rating_key,
            session_flashcard_card_state.last_reviewed_at,
            updated_session.id
        from public.session_flashcard_card_state
        where session_flashcard_card_state.session_id = updated_session.id
        on conflict (user_id, lernbereich_slug, card_id) do update
        set check_id = excluded.check_id,
            seen_count = excluded.seen_count,
            level = excluded.level,
            next_due_at = excluded.next_due_at,
            last_rating_key = excluded.last_rating_key,
            last_reviewed_at = excluded.last_reviewed_at,
            source_session_id = excluded.source_session_id;
    end if;

    return updated_session;
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
    updated_lernbereich_slug text;
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
        last_outcome_key = 'complete',
        last_completed_at = now()
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

    updated_lernbereich_slug := public.check_id_lernbereich_slug(updated_state.check_id);
    if updated_state.current_step_key = 'kompetenzliste_gate' and updated_lernbereich_slug is not null then
        perform public.refresh_flashcard_activity_for_lernbereich(updated_state.session_id, updated_lernbereich_slug);
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
                    last_outcome_key = 'can_do',
                    last_completed_at = inserted_attempt.created_at
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
                    last_outcome_key = 'can_do',
                    last_completed_at = inserted_attempt.created_at
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

create or replace function public.set_retention_scope_status(
    p_lernbereich_slug text,
    p_status text
)
returns public.user_retention_scopes
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    normalized_status text := lower(coalesce(nullif(trim(p_status), ''), ''));
    updated_scope public.user_retention_scopes;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if normalized_status not in ('active', 'paused', 'opted_out') then
        raise exception 'Unsupported retention status';
    end if;

    insert into public.user_retention_scopes (
        user_id,
        activity_type,
        scope_type,
        lernbereich_slug,
        status,
        source_session_id
    )
    values (
        current_user_id,
        'flashcards',
        'lernbereich',
        normalized_lernbereich_slug,
        normalized_status,
        null
    )
    on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
    set status = excluded.status
    returning * into updated_scope;

    return updated_scope;
end;
$$;

revoke all on function public.save_active_learning_session(text[], text[], integer, text[]) from public;
revoke all on function public.save_active_learning_session(text[], text[], integer, text[]) from anon;
revoke all on function public.finish_learning_session(uuid, text) from public;
revoke all on function public.finish_learning_session(uuid, text) from anon;
revoke all on function public.complete_current_training_step(text) from public;
revoke all on function public.complete_current_training_step(text) from anon;
revoke all on function public.record_check_module_attempt(text, text, text, text) from public;
revoke all on function public.record_check_module_attempt(text, text, text, text) from anon;
revoke all on function public.set_retention_scope_status(text, text) from public;
revoke all on function public.set_retention_scope_status(text, text) from anon;

grant execute on function public.save_active_learning_session(text[], text[], integer, text[]) to authenticated;
grant execute on function public.finish_learning_session(uuid, text) to authenticated;
grant execute on function public.complete_current_training_step(text) to authenticated;
grant execute on function public.record_check_module_attempt(text, text, text, text) to authenticated;
grant execute on function public.set_retention_scope_status(text, text) to authenticated;