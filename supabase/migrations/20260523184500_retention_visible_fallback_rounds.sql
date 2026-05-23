-- Visible retention fallback cards in the feed must be executable even when
-- their activity-count release is not reached yet.
--
-- The feed projection still controls visibility. This migration only opens a
-- dedicated server-side start path for visible fallback cards.

create or replace function public.get_or_create_retention_flashcard_round_with_options(
    p_lernbereich_slug text,
    p_card_ids text[],
    p_check_ids text[],
    p_task_indices integer[] default array[]::integer[],
    p_card_limit integer default 20,
    p_allow_early_start boolean default false
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
    allow_early_start boolean := coalesce(p_allow_early_start, false);
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
      and not allow_early_start
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
begin
    return query
    select *
    from public.get_or_create_retention_flashcard_round_with_options(
        p_lernbereich_slug,
        p_card_ids,
        p_check_ids,
        p_task_indices,
        p_card_limit,
        false
    );
end;
$$;

revoke all on function public.get_or_create_retention_flashcard_round_with_options(text, text[], text[], integer[], integer, boolean) from public;
revoke all on function public.get_or_create_retention_flashcard_round_with_options(text, text[], text[], integer[], integer, boolean) from anon;
grant execute on function public.get_or_create_retention_flashcard_round_with_options(text, text[], text[], integer[], integer, boolean) to authenticated;