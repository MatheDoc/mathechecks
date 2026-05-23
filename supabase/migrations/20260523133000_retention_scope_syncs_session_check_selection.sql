-- Migration: Retention-Scopes übernehmen die Session-Check-Auswahl konsistent.
--
-- Problem:
-- - Der per-Lernbereich-Retention-Pfad legt zwar user_retention_scopes an,
--   spiegelt aber session_check_exclusions noch nicht in
--   user_retention_check_exclusions.
-- - Der Retention-Flashcard-Round-RPC berücksichtigt user-scoped
--   Check-Ausschlüsse noch nicht und nimmt dadurch weiterhin alle
--   Lernbereichs-Karten an.
--
-- Fix:
-- 1. complete_kompetenzliste_gate synchronisiert die Check-Ausschlüsse des
--    abgeschlossenen Lernbereichs aus der aktiven Session nach Retention.
-- 2. finish_learning_session synchronisiert die Ausschlüsse aller
--    Session-Lernbereiche erneut als Abschluss-Fallback.
-- 3. get_or_create_retention_flashcard_round filtert ausgeschlossene Checks
--    serverseitig heraus.

create or replace function public.complete_kompetenzliste_gate(
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
    remaining_open_checks integer := 0;
    remaining_lernbereich_open_checks integer := 0;
    completed_lernbereich_slug text;
    current_completed_activity_count bigint;
    retention_activity_gap integer;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    update public.session_check_state
    set current_step_key = 'check_completed',
        current_step_status = 'completed',
        last_outcome_key = 'complete',
        last_completed_at = now()
    from public.learning_sessions
    where learning_sessions.id = session_check_state.session_id
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and session_check_state.check_id = normalized_check_id
      and session_check_state.current_step_key = 'kompetenzliste_gate'
      and session_check_state.current_step_status = 'due'
    returning session_check_state.* into updated_state;

    if updated_state.session_id is null then
        raise exception 'Due kompetenzliste gate not found';
    end if;

    perform public.bump_feed_activity_completion_count();

    current_completed_activity_count := public.get_current_feed_activity_completion_count();
    retention_activity_gap := public.get_system_setting_integer('feed.retention_activity_base_gap', 5);
    completed_lernbereich_slug := public.check_id_lernbereich_slug(updated_state.check_id);

    select count(*)
    into remaining_lernbereich_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and public.check_id_lernbereich_slug(check_id) = completed_lernbereich_slug
      and current_step_key <> 'check_completed';

    if remaining_lernbereich_open_checks = 0 then
        delete from public.user_retention_check_exclusions
        where user_id = current_user_id
          and lernbereich_slug = completed_lernbereich_slug;

        insert into public.user_retention_check_exclusions (
            user_id,
            lernbereich_slug,
            check_id
        )
        select
            current_user_id,
            completed_lernbereich_slug,
            session_check_exclusions.check_id
        from public.session_check_exclusions
        where session_check_exclusions.session_id = updated_state.session_id
          and public.check_id_lernbereich_slug(session_check_exclusions.check_id) = completed_lernbereich_slug
        on conflict do nothing;

        insert into public.user_retention_scopes (
            user_id,
            activity_type,
            scope_type,
            lernbereich_slug,
            status,
            source_session_id,
            activity_interval,
            activity_due_exponent,
            next_due_after_activity_count
        )
        values (
            current_user_id,
            'flashcards',
            'lernbereich',
            completed_lernbereich_slug,
            'active',
            updated_state.session_id,
            retention_activity_gap,
            0,
            current_completed_activity_count + retention_activity_gap
        )
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set source_session_id = excluded.source_session_id,
            activity_interval = excluded.activity_interval,
            activity_due_exponent = 0,
            next_due_after_activity_count = excluded.next_due_after_activity_count,
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
            sfcs.lernbereich_slug,
            sfcs.card_id,
            sfcs.check_id,
            sfcs.seen_count,
            sfcs.level,
            sfcs.next_due_at,
            sfcs.last_rating_key,
            sfcs.last_reviewed_at,
            updated_state.session_id
        from public.session_flashcard_card_state as sfcs
        where sfcs.session_id = updated_state.session_id
          and sfcs.lernbereich_slug = completed_lernbereich_slug
        on conflict (user_id, lernbereich_slug, card_id) do update
        set check_id = excluded.check_id,
            seen_count = excluded.seen_count,
            level = excluded.level,
            next_due_at = excluded.next_due_at,
            last_rating_key = excluded.last_rating_key,
            last_reviewed_at = excluded.last_reviewed_at,
            source_session_id = excluded.source_session_id;
    end if;

    select count(*)
    into remaining_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and current_step_key <> 'check_completed';

    if remaining_open_checks = 0 then
        perform public.finish_learning_session(updated_state.session_id, 'completed');
    end if;

    return updated_state;
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
    current_completed_activity_count bigint := public.get_current_feed_activity_completion_count();
    retention_activity_gap integer := public.get_system_setting_integer('feed.retention_activity_base_gap', 5);
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
        delete from public.user_retention_check_exclusions as retention_exclusions
        where retention_exclusions.user_id = current_user_id
          and retention_exclusions.lernbereich_slug in (
              select session_lernbereiche.lernbereich_slug
              from public.session_lernbereiche
              where session_lernbereiche.session_id = updated_session.id
          );

        insert into public.user_retention_check_exclusions (
            user_id,
            lernbereich_slug,
            check_id
        )
        select
            current_user_id,
            public.check_id_lernbereich_slug(session_check_exclusions.check_id),
            session_check_exclusions.check_id
        from public.session_check_exclusions
        where session_check_exclusions.session_id = updated_session.id
          and public.check_id_lernbereich_slug(session_check_exclusions.check_id) is not null
        on conflict do nothing;

        insert into public.user_retention_scopes (
            user_id,
            activity_type,
            scope_type,
            lernbereich_slug,
            status,
            source_session_id,
            activity_interval,
            activity_due_exponent,
            next_due_after_activity_count
        )
        select
            current_user_id,
            'flashcards',
            'lernbereich',
            session_lernbereiche.lernbereich_slug,
            'active',
            updated_session.id,
            retention_activity_gap,
            0,
            current_completed_activity_count + retention_activity_gap
        from public.session_lernbereiche
        where session_lernbereiche.session_id = updated_session.id
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set source_session_id = excluded.source_session_id,
            activity_interval = excluded.activity_interval,
            activity_due_exponent = case
                when public.user_retention_scopes.status = 'active' then public.user_retention_scopes.activity_due_exponent
                else 0
            end,
            next_due_after_activity_count = case
                when public.user_retention_scopes.status = 'active' then public.user_retention_scopes.next_due_after_activity_count
                else excluded.next_due_after_activity_count
            end,
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

create or replace function public.get_or_create_retention_flashcard_round(
    p_lernbereich_slug text,
    p_card_ids text[],
    p_check_ids text[],
    p_task_indices integer[] default array[]::integer[],
    p_card_limit integer default 20
)
returns table (
    round_id uuid,
    activity_key text,
    round_status text,
    card_id text,
    check_id text,
    card_position integer,
    task_index integer,
    rating_key text,
    reviewed_at timestamptz,
    total_cards integer,
    reviewed_count integer
)
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    active_activity_key text;
    active_round_id uuid;
    active_session_id uuid;
    card_count integer := coalesce(array_length(p_card_ids, 1), 0);
    check_count integer := coalesce(array_length(p_check_ids, 1), 0);
    effective_limit integer := greatest(1, least(coalesce(p_card_limit, 20), 50));
    next_round_index integer;
    current_completed_activity_count bigint := public.get_current_feed_activity_completion_count();
    scope_next_due_after_activity_count bigint;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if card_count = 0 or card_count <> check_count then
        raise exception 'card_ids and check_ids must have the same non-empty length';
    end if;

    select scopes.next_due_after_activity_count
    into scope_next_due_after_activity_count
    from public.user_retention_scopes as scopes
    where scopes.user_id = current_user_id
      and scopes.activity_type = 'flashcards'
      and scopes.scope_type = 'lernbereich'
      and scopes.lernbereich_slug = normalized_lernbereich_slug
      and scopes.status = 'active';

    if not found then
        raise exception 'Active flashcard retention scope not found';
    end if;

    select learning_sessions.id
    into active_session_id
    from public.learning_sessions
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
    order by learning_sessions.started_at desc
    limit 1;

    if active_session_id is not null
      and (scope_next_due_after_activity_count is null or scope_next_due_after_activity_count > current_completed_activity_count) then
        raise exception 'Flashcard retention is not due';
    end if;

    active_activity_key := 'retention:lernbereich:' || normalized_lernbereich_slug || ':flashcards';

    select rounds.id
    into active_round_id
    from public.retention_flashcard_rounds as rounds
    where rounds.user_id = current_user_id
      and rounds.activity_key = active_activity_key
      and rounds.status = 'active'
    order by rounds.started_at desc
    limit 1;

    if active_round_id is null then
        select coalesce(max(rounds.round_index), 0) + 1
        into next_round_index
        from public.retention_flashcard_rounds as rounds
        where rounds.user_id = current_user_id
          and rounds.activity_key = active_activity_key;

        insert into public.retention_flashcard_rounds (
            user_id,
            activity_key,
            lernbereich_slug,
            round_index,
            status,
            card_limit
        )
        values (
            current_user_id,
            active_activity_key,
            normalized_lernbereich_slug,
            next_round_index,
            'active',
            effective_limit
        )
        returning id into active_round_id;

        with input_cards as (
            select
                nullif(trim(p_card_ids[card_index.ord]), '') as input_card_id,
                nullif(trim(p_check_ids[card_index.ord]), '') as input_check_id,
                greatest(coalesce(p_task_indices[card_index.ord], 0), 0) as input_task_index,
                card_index.ord
            from generate_subscripts(p_card_ids, 1) as card_index(ord)
        ),
        allowed_cards as (
            select distinct on (input_cards.input_card_id)
                input_cards.input_card_id as card_id,
                input_cards.input_check_id as check_id,
                input_cards.input_task_index as task_index,
                input_cards.ord,
                card_state.next_due_at
            from input_cards
            left join public.retention_flashcard_card_state as card_state
              on card_state.user_id = current_user_id
             and card_state.lernbereich_slug = normalized_lernbereich_slug
             and card_state.card_id = input_cards.input_card_id
            left join public.user_retention_check_exclusions as check_exclusions
              on check_exclusions.user_id = current_user_id
             and check_exclusions.lernbereich_slug = normalized_lernbereich_slug
             and check_exclusions.check_id = input_cards.input_check_id
            where input_cards.input_card_id is not null
              and input_cards.input_check_id is not null
              and public.check_id_lernbereich_slug(input_cards.input_check_id) = normalized_lernbereich_slug
              and check_exclusions.check_id is null
            order by input_cards.input_card_id, input_cards.ord
        ),
        ranked_cards as (
            select
                allowed_cards.card_id,
                allowed_cards.check_id,
                allowed_cards.task_index,
                allowed_cards.ord,
                coalesce(allowed_cards.next_due_at, '-infinity'::timestamptz) as next_due_at,
                case
                    when active_session_id is not null and allowed_cards.next_due_at is null then 0
                    when active_session_id is not null then 1
                    when allowed_cards.next_due_at is null then 0
                    when allowed_cards.next_due_at <= now() then 1
                    else 2
                end as due_priority,
                random() as random_sort
            from allowed_cards
        ),
        selected_cards as (
            select
                ranked_cards.card_id,
                ranked_cards.check_id,
                ranked_cards.task_index,
                ranked_cards.due_priority,
                ranked_cards.next_due_at,
                ranked_cards.random_sort
            from ranked_cards
            where ranked_cards.due_priority < 2
            order by ranked_cards.due_priority, ranked_cards.next_due_at, ranked_cards.random_sort
            limit effective_limit
        ),
        positioned_cards as (
            select
                selected_cards.card_id,
                selected_cards.check_id,
                selected_cards.task_index,
                row_number() over (
                    order by selected_cards.due_priority, selected_cards.next_due_at, selected_cards.random_sort
                )::integer as card_position
            from selected_cards
        )
        insert into public.retention_flashcard_round_cards (
            user_id,
            round_id,
            card_id,
            check_id,
            position,
            task_index
        )
        select
            current_user_id,
            active_round_id,
            positioned_cards.card_id,
            positioned_cards.check_id,
            positioned_cards.card_position,
            positioned_cards.task_index
        from positioned_cards;

        if not exists (
            select 1
            from public.retention_flashcard_round_cards as round_cards
            where round_cards.round_id = active_round_id
        ) then
            raise exception 'No due retention flashcards available';
        end if;
    end if;

    return query
    select
        rounds.id as round_id,
        rounds.activity_key as activity_key,
        rounds.status as round_status,
        round_cards.card_id as card_id,
        round_cards.check_id as check_id,
        round_cards.position as card_position,
        round_cards.task_index as task_index,
        round_cards.rating_key as rating_key,
        round_cards.reviewed_at as reviewed_at,
        (count(*) over ())::integer as total_cards,
        (count(round_cards.reviewed_at) over ())::integer as reviewed_count
    from public.retention_flashcard_rounds as rounds
    join public.retention_flashcard_round_cards as round_cards
      on round_cards.round_id = rounds.id
    where rounds.id = active_round_id
      and rounds.user_id = current_user_id
    order by round_cards.position;
end;
$$;