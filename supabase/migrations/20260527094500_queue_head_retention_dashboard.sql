-- Migration: sichtbare Retention-Eintraege verhalten sich wie eine Queue am
-- Feed-Kopf statt wie feste Interleave-Slots.
--
-- Fix:
-- 1. user_retention_scopes bekommt einen persistenten Queue-Anker pro Scope.
-- 2. Neue oder neu aktivierte Retention-Scopes steigen am sichtbaren Feed-Kopf
--    auf einer festen Position ein und ruecken bei abgeschlossenen
--    Feed-Aktivitaeten davor nach oben.
-- 3. Der Feed-Abschlusszaehler wird wieder konsistent von start, training,
--    erfolgreichen recall/feynman-Schritten, kompetenzliste und retention
--    fortgeschrieben.

alter table public.user_retention_scopes
    add column if not exists feed_queue_entry_activity_count bigint;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'user_retention_scopes_feed_queue_entry_activity_count_check'
    ) then
        alter table public.user_retention_scopes
            add constraint user_retention_scopes_feed_queue_entry_activity_count_check
            check (
                feed_queue_entry_activity_count is null
                or feed_queue_entry_activity_count >= 0
            );
    end if;
end;
$$;

insert into public.system_settings (
    setting_key,
    value_integer,
    description
)
values (
    'feed.retention_new_item_position',
    5,
    'Sichtbare Einstiegsposition neuer oder neu sichtbarer Retention-Eintraege im Dashboard-Feed.'
)
on conflict (setting_key) do update
set value_integer = excluded.value_integer,
    description = excluded.description;

delete from public.system_settings
where setting_key in (
    'feed.retention_interleave_lead_session_items',
    'feed.retention_interleave_stride'
);

create or replace function public.complete_start_activity(
    p_lernbereich_slug text
)
returns public.session_activity_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    active_session_id uuid;
    updated_activity public.session_activity_state;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    select id
    into active_session_id
    from public.learning_sessions
    where user_id = current_user_id
      and status = 'active'
    for update;

    if active_session_id is null then
        raise exception 'No active learning session found';
    end if;

    update public.session_activity_state
    set status = 'completed',
        last_outcome_key = 'complete',
        updated_at = now()
    where session_id = active_session_id
      and activity_type = 'start'
      and scope_type = 'lernbereich'
      and lernbereich_slug = normalized_lernbereich_slug
    returning * into updated_activity;

    if updated_activity.session_id is null then
        raise exception 'No due start activity found';
    end if;

    perform public.bump_feed_activity_completion_count();

    return updated_activity;
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
    set current_step_key = 'recall',
        current_step_status = 'due',
        last_outcome_key = 'complete',
        last_completed_at = now()
    from public.learning_sessions
    where learning_sessions.id = session_check_state.session_id
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and session_check_state.check_id = normalized_check_id
      and session_check_state.current_step_key = 'training'
      and session_check_state.current_step_status = 'due'
    returning session_check_state.* into updated_state;

    if updated_state.session_id is null then
        raise exception 'Due training step not found';
    end if;

    perform public.bump_feed_activity_completion_count();

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
    did_advance boolean := false;
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
                set current_step_key = 'feynman',
                    current_step_status = 'due',
                    last_outcome_key = 'can_do',
                    last_completed_at = inserted_attempt.created_at
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'recall'
                  and current_step_status = 'due';

                did_advance := found;
                perform public.unlock_successor_lernbereiche(matched_session_id, normalized_lernbereich_slug);
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
                set current_step_key = 'kompetenzliste_gate',
                    current_step_status = 'due',
                    last_outcome_key = 'can_do',
                    last_completed_at = inserted_attempt.created_at
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'feynman'
                  and current_step_status = 'due';

                did_advance := found;
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

    if did_advance then
        perform public.bump_feed_activity_completion_count();
    end if;

    return inserted_attempt;
end;
$$;

create or replace function public.set_retention_scope_status(
    p_lernbereich_slug text,
    p_status text,
    p_due_mode text
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
    normalized_due_mode text := lower(coalesce(nullif(trim(p_due_mode), ''), 'scheduled'));
    updated_scope public.user_retention_scopes;
    current_completed_activity_count bigint := public.get_current_feed_activity_completion_count();
    retention_activity_gap integer := public.get_system_setting_integer('feed.retention_activity_base_gap', 5);
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

    if normalized_due_mode not in ('scheduled', 'immediate') then
        raise exception 'Unsupported retention due mode';
    end if;

    insert into public.user_retention_scopes (
        user_id,
        activity_type,
        scope_type,
        lernbereich_slug,
        status,
        source_session_id,
        activity_interval,
        activity_due_exponent,
        next_due_after_activity_count,
        feed_queue_entry_activity_count
    )
    values (
        current_user_id,
        'flashcards',
        'lernbereich',
        normalized_lernbereich_slug,
        normalized_status,
        null,
        retention_activity_gap,
        0,
        case
            when normalized_status = 'active' and normalized_due_mode = 'immediate' then current_completed_activity_count
            else current_completed_activity_count + retention_activity_gap
        end,
        case
            when normalized_status = 'active' then current_completed_activity_count
            else null
        end
    )
    on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
    set status = excluded.status,
        activity_interval = case
            when excluded.status = 'active' then excluded.activity_interval
            else public.user_retention_scopes.activity_interval
        end,
        activity_due_exponent = case
            when excluded.status = 'active' then 0
            else public.user_retention_scopes.activity_due_exponent
        end,
        next_due_after_activity_count = case
            when excluded.status = 'active' and normalized_due_mode = 'immediate' then current_completed_activity_count
            when excluded.status = 'active' then current_completed_activity_count + public.user_retention_scopes.activity_interval
            else public.user_retention_scopes.next_due_after_activity_count
        end,
        feed_queue_entry_activity_count = case
            when excluded.status = 'active' then current_completed_activity_count
            else null
        end
    returning * into updated_scope;

    return updated_scope;
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
begin
    return public.set_retention_scope_status(p_lernbereich_slug, p_status, 'scheduled');
end;
$$;

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
            next_due_after_activity_count,
            feed_queue_entry_activity_count
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
            current_completed_activity_count + retention_activity_gap,
            current_completed_activity_count
        )
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set source_session_id = excluded.source_session_id,
            activity_interval = excluded.activity_interval,
            activity_due_exponent = 0,
            next_due_after_activity_count = excluded.next_due_after_activity_count,
            feed_queue_entry_activity_count = case
                when public.user_retention_scopes.status = 'active' then public.user_retention_scopes.feed_queue_entry_activity_count
                when public.user_retention_scopes.status in ('paused', 'opted_out') then null
                else excluded.feed_queue_entry_activity_count
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
            next_due_after_activity_count,
            feed_queue_entry_activity_count
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
            current_completed_activity_count + retention_activity_gap,
            current_completed_activity_count
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
            feed_queue_entry_activity_count = case
                when public.user_retention_scopes.status = 'active' then public.user_retention_scopes.feed_queue_entry_activity_count
                when public.user_retention_scopes.status in ('paused', 'opted_out') then null
                else excluded.feed_queue_entry_activity_count
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

create or replace function public.resolve_retention_flashcard_round(
    p_round_id uuid,
    p_decision_key text
)
returns public.retention_flashcard_rounds
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_decision_key text := lower(coalesce(nullif(trim(p_decision_key), ''), ''));
    matched_round public.retention_flashcard_rounds;
    updated_round public.retention_flashcard_rounds;
    scope_activity_interval integer;
    scope_due_exponent integer;
    total_count integer;
    reviewed_count integer;
    next_completed_activity_count bigint;
    next_scope_due_exponent integer;
    next_scope_due_after_activity_count bigint;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_decision_key not in ('complete', 'keep_open') then
        raise exception 'Unsupported decision_key';
    end if;

    select *
    into matched_round
    from public.retention_flashcard_rounds
    where id = p_round_id
      and user_id = current_user_id
      and status = 'active'
    for update;

    if matched_round.id is null then
        raise exception 'Active retention flashcard round not found';
    end if;

    select scopes.activity_interval, scopes.activity_due_exponent
    into scope_activity_interval, scope_due_exponent
    from public.user_retention_scopes as scopes
    where scopes.user_id = current_user_id
      and scopes.activity_type = 'flashcards'
      and scopes.scope_type = 'lernbereich'
      and scopes.lernbereich_slug = matched_round.lernbereich_slug
    for update of scopes;

    if not found then
        raise exception 'Retention flashcard scope not found';
    end if;

    select count(*), count(reviewed_at)
    into total_count, reviewed_count
    from public.retention_flashcard_round_cards
    where round_id = matched_round.id;

    if total_count = 0 or reviewed_count < total_count then
        raise exception 'Retention flashcard round is not fully reviewed';
    end if;

    if normalized_decision_key = 'keep_open' then
        update public.retention_flashcard_card_state as card_state
        set next_due_at = now()
        from public.retention_flashcard_round_cards as round_cards
        where round_cards.round_id = matched_round.id
          and card_state.user_id = current_user_id
          and card_state.lernbereich_slug = matched_round.lernbereich_slug
          and card_state.card_id = round_cards.card_id;
    end if;

    update public.retention_flashcard_rounds
    set status = 'completed',
        completed_at = now()
    where id = matched_round.id
    returning * into updated_round;

    if normalized_decision_key = 'complete' then
        next_completed_activity_count := public.bump_feed_activity_completion_count();
        next_scope_due_exponent := least(coalesce(scope_due_exponent, 0) + 1, 8);
        next_scope_due_after_activity_count := next_completed_activity_count
            + (greatest(coalesce(scope_activity_interval, 1), 1)::bigint * cast(power(2, next_scope_due_exponent) as bigint));

        update public.user_retention_scopes
        set activity_due_exponent = next_scope_due_exponent,
            next_due_after_activity_count = next_scope_due_after_activity_count,
            feed_queue_entry_activity_count = null
        where user_id = current_user_id
          and activity_type = 'flashcards'
          and scope_type = 'lernbereich'
          and lernbereich_slug = matched_round.lernbereich_slug;
    end if;

    return updated_round;
end;
$$;