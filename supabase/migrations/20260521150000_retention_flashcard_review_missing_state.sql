create or replace function public.record_retention_flashcard_review(
    p_round_id uuid,
    p_card_id text,
    p_rating_key text
)
returns public.retention_flashcard_round_cards
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_card_id text := nullif(trim(p_card_id), '');
    normalized_rating_key text := lower(coalesce(nullif(trim(p_rating_key), ''), ''));
    matched_round public.retention_flashcard_rounds;
    matched_tempo_days integer := 1;
    matched_card public.retention_flashcard_round_cards;
    previous_level integer := 0;
    interval_days integer := 0;
    next_level integer := 0;
    matched_scope_source_session_id uuid;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_round_id is null then
        raise exception 'round_id is required';
    end if;

    if normalized_card_id is null then
        raise exception 'card_id is required';
    end if;

    if normalized_rating_key not in ('hard', 'medium', 'easy') then
        raise exception 'Unsupported rating_key';
    end if;

    select rounds.*
    into matched_round
    from public.retention_flashcard_rounds as rounds
    where rounds.id = p_round_id
      and rounds.user_id = current_user_id
      and rounds.status = 'active'
    for update of rounds;

    if matched_round.id is null then
        raise exception 'Active retention flashcard round not found';
    end if;

    update public.retention_flashcard_round_cards
    set rating_key = normalized_rating_key,
        reviewed_at = now()
    where round_id = matched_round.id
      and card_id = normalized_card_id
    returning * into matched_card;

    if matched_card.round_id is null then
        raise exception 'Flashcard not found in current retention round';
    end if;

    select
        scopes.source_session_id,
        greatest(coalesce(source_session.tempo_days, 1), 1)
    into matched_scope_source_session_id, matched_tempo_days
    from public.user_retention_scopes as scopes
    left join public.learning_sessions as source_session
      on source_session.id = scopes.source_session_id
    where scopes.user_id = current_user_id
      and scopes.activity_type = 'flashcards'
      and scopes.scope_type = 'lernbereich'
      and scopes.lernbereich_slug = matched_round.lernbereich_slug
      and scopes.status = 'active';

    if not found then
        raise exception 'Active flashcard retention scope not found';
    end if;

    select
        coalesce(card_state.level, 0),
        greatest(coalesce(source_session.tempo_days, matched_tempo_days, 1), 1)
    into previous_level, matched_tempo_days
    from public.retention_flashcard_card_state as card_state
    left join public.learning_sessions as source_session
      on source_session.id = card_state.source_session_id
    where card_state.user_id = current_user_id
      and card_state.lernbereich_slug = matched_round.lernbereich_slug
      and card_state.card_id = matched_card.card_id;

    if not found then
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
        values (
            current_user_id,
            matched_round.lernbereich_slug,
            matched_card.card_id,
            matched_card.check_id,
            0,
            0,
            now(),
            null,
            null,
            matched_scope_source_session_id
        )
        on conflict (user_id, lernbereich_slug, card_id) do nothing;

        previous_level := 0;
    end if;

    if normalized_rating_key = 'hard' then
        next_level := 0;
        interval_days := 0;
    elsif normalized_rating_key = 'medium' then
        next_level := greatest(previous_level, 1);
        interval_days := matched_tempo_days;
    else
        next_level := least(previous_level + 1, 8);
        interval_days := matched_tempo_days * power(2, next_level)::integer;
    end if;

    update public.retention_flashcard_card_state
    set seen_count = retention_flashcard_card_state.seen_count + 1,
        level = next_level,
        next_due_at = now() + make_interval(days => interval_days),
        last_rating_key = normalized_rating_key,
        last_reviewed_at = now(),
        check_id = matched_card.check_id,
        source_session_id = coalesce(retention_flashcard_card_state.source_session_id, matched_scope_source_session_id)
    where user_id = current_user_id
      and lernbereich_slug = matched_round.lernbereich_slug
      and card_id = matched_card.card_id;

    return matched_card;
end;
$$;

grant execute on function public.record_retention_flashcard_review(uuid, text, text) to authenticated;