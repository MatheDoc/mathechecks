-- Migration: Retention-Wiederkehr im Feed ueber lineare Aktivitaetsabstaende.
--
-- Ziel:
-- - Nach dem ersten sichtbaren Einstieg ueber den Queue-Kopf soll eine erledigte
--   Retention nicht sofort wieder erscheinen.
-- - Die Wiedereinblendung folgt fuer den Scope ueber lineare Vielfache des
--   Basisabstands: N, 2N, 3N, 4N, ... statt exponentiell  N, 2N, 4N, 8N, ...

update public.system_settings
set description = 'Basisabstand N fuer Retention-Flashcards; Wiederkehr im Feed ueber lineare Aktivitaetsabstaende N, 2N, 3N, ...'
where setting_key = 'feed.retention_activity_base_gap';

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
        next_scope_due_exponent := coalesce(scope_due_exponent, 0) + 1;
        next_scope_due_after_activity_count := next_completed_activity_count
            + (greatest(coalesce(scope_activity_interval, 1), 1)::bigint * greatest(next_scope_due_exponent + 1, 1)::bigint);

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