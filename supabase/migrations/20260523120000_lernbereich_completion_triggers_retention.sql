-- Migration: 20260523120000_lernbereich_completion_triggers_retention
--
-- Problem: user_retention_scopes wird erst beim Abschluss der gesamten Session
-- befüllt (finish_learning_session), nicht beim Abschluss eines einzelnen Lernbereichs.
-- Dadurch fallen Lernbereiche nicht in Retention, solange andere Checks der Session
-- noch offen sind.
--
-- Fix:
-- 1. complete_kompetenzliste_gate prüft nach jedem Gate-Abschluss, ob alle Checks
--    des betreffenden Lernbereichs in der Session nun check_completed sind.
--    Falls ja: user_retention_scopes und retention_flashcard_card_state werden
--    direkt für diesen Lernbereich aktualisiert.
-- 2. finish_learning_session überschreibt next_due_after_activity_count nicht,
--    wenn der Scope bereits active ist (per-Lernbereich-Logik hat schon korrekt
--    getaktet), damit der Zeitpunkt nicht zurückgesetzt wird.

-- 1. complete_kompetenzliste_gate: per-Lernbereich-Retention

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

    -- Prüfen ob alle Checks dieses Lernbereichs in der Session abgeschlossen sind
    select count(*)
    into remaining_lernbereich_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and public.check_id_lernbereich_slug(check_id) = completed_lernbereich_slug
      and current_step_key <> 'check_completed';

    if remaining_lernbereich_open_checks = 0 then
        -- Retention-Scope für diesen Lernbereich anlegen/aktualisieren
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

        -- Flashcard-Kartenstände für diesen Lernbereich in Retention übertragen
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

    -- Prüfen ob alle Checks der gesamten Session abgeschlossen sind
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

-- 2. finish_learning_session: next_due_after_activity_count nicht zurücksetzen
--    wenn Scope bereits active ist (per-Lernbereich-Logik hat schon korrekt getaktet)

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
            -- Scope bereits active: Zeitpunkt nicht zurücksetzen (per-Lernbereich-
            -- Logik in complete_kompetenzliste_gate hat bereits korrekt getaktet)
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
