create table public.retention_flashcard_rounds (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    activity_key text not null check (char_length(trim(activity_key)) > 0),
    lernbereich_slug text not null check (char_length(trim(lernbereich_slug)) > 0),
    round_index integer not null check (round_index > 0),
    status text not null check (status in ('active', 'completed')),
    card_limit integer not null default 20 check (card_limit > 0),
    started_at timestamptz not null default now(),
    completed_at timestamptz null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index retention_flashcard_rounds_active_idx
    on public.retention_flashcard_rounds (user_id, activity_key)
    where status = 'active';

create index retention_flashcard_rounds_user_idx
    on public.retention_flashcard_rounds (user_id, activity_key, status, started_at desc);

drop trigger if exists set_retention_flashcard_rounds_updated_at on public.retention_flashcard_rounds;
create trigger set_retention_flashcard_rounds_updated_at
    before update on public.retention_flashcard_rounds
    for each row execute function public.set_updated_at();

create table public.retention_flashcard_round_cards (
    user_id uuid not null references auth.users(id) on delete cascade,
    round_id uuid not null references public.retention_flashcard_rounds(id) on delete cascade,
    card_id text not null check (char_length(trim(card_id)) > 0),
    check_id text not null check (char_length(trim(check_id)) > 0),
    position integer not null check (position > 0),
    task_index integer not null default 0 check (task_index >= 0),
    rating_key text null check (rating_key in ('hard', 'medium', 'easy')),
    reviewed_at timestamptz null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (round_id, card_id),
    unique (round_id, position)
);

create index retention_flashcard_round_cards_user_idx
    on public.retention_flashcard_round_cards (user_id, round_id, position);

drop trigger if exists set_retention_flashcard_round_cards_updated_at on public.retention_flashcard_round_cards;
create trigger set_retention_flashcard_round_cards_updated_at
    before update on public.retention_flashcard_round_cards
    for each row execute function public.set_updated_at();

grant select on public.retention_flashcard_rounds to authenticated;
grant select on public.retention_flashcard_round_cards to authenticated;

alter table public.retention_flashcard_rounds enable row level security;
alter table public.retention_flashcard_round_cards enable row level security;

create policy retention_flashcard_rounds_select_own
    on public.retention_flashcard_rounds
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy retention_flashcard_round_cards_select_own
    on public.retention_flashcard_round_cards
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

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
    card_count integer := coalesce(array_length(p_card_ids, 1), 0);
    check_count integer := coalesce(array_length(p_check_ids, 1), 0);
    effective_limit integer := greatest(1, least(coalesce(p_card_limit, 20), 50));
    next_round_index integer;
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

    if not exists (
        select 1
        from public.user_retention_scopes as scopes
        where scopes.user_id = current_user_id
          and scopes.activity_type = 'flashcards'
          and scopes.scope_type = 'lernbereich'
          and scopes.lernbereich_slug = normalized_lernbereich_slug
          and scopes.status = 'active'
    ) then
        raise exception 'Active flashcard retention scope not found';
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
        if not exists (
            select 1
            from public.retention_flashcard_card_state as card_state
            where card_state.user_id = current_user_id
              and card_state.lernbereich_slug = normalized_lernbereich_slug
              and card_state.next_due_at <= now()
        ) then
            raise exception 'Flashcard retention is not due';
        end if;

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
            join public.retention_flashcard_card_state as card_state
              on card_state.user_id = current_user_id
             and card_state.lernbereich_slug = normalized_lernbereich_slug
             and card_state.card_id = input_cards.input_card_id
            where input_cards.input_card_id is not null
              and input_cards.input_check_id is not null
              and public.check_id_lernbereich_slug(input_cards.input_check_id) = normalized_lernbereich_slug
              and card_state.next_due_at <= now()
            order by input_cards.input_card_id, input_cards.ord
        ),
        selected_cards as (
            select
                allowed_cards.card_id,
                allowed_cards.check_id,
                allowed_cards.task_index,
                allowed_cards.next_due_at,
                allowed_cards.ord
            from allowed_cards
            order by allowed_cards.next_due_at, allowed_cards.ord
            limit effective_limit
        ),
        positioned_cards as (
            select
                selected_cards.card_id,
                selected_cards.check_id,
                selected_cards.task_index,
                row_number() over (order by selected_cards.next_due_at, selected_cards.ord)::integer as card_position
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
        coalesce(card_state.level, 0),
        greatest(coalesce(source_session.tempo_days, 1), 1)
    into previous_level, matched_tempo_days
    from public.retention_flashcard_card_state as card_state
    left join public.learning_sessions as source_session
      on source_session.id = card_state.source_session_id
    where card_state.user_id = current_user_id
      and card_state.lernbereich_slug = matched_round.lernbereich_slug
      and card_state.card_id = matched_card.card_id;

    if not found then
        raise exception 'Retention flashcard state not found';
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
    set seen_count = seen_count + 1,
        level = next_level,
        next_due_at = now() + make_interval(days => interval_days),
        last_rating_key = normalized_rating_key,
        last_reviewed_at = now(),
        check_id = matched_card.check_id
    where user_id = current_user_id
      and lernbereich_slug = matched_round.lernbereich_slug
      and card_id = matched_card.card_id;

    return matched_card;
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
    reviewed_count integer;
    total_count integer;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_round_id is null then
        raise exception 'round_id is required';
    end if;

    if normalized_decision_key not in ('complete', 'keep_open') then
        raise exception 'Unsupported decision_key';
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

    return updated_round;
end;
$$;

revoke all on function public.get_or_create_retention_flashcard_round(text, text[], text[], integer[], integer) from public;
revoke all on function public.record_retention_flashcard_review(uuid, text, text) from public;
revoke all on function public.resolve_retention_flashcard_round(uuid, text) from public;

revoke all on function public.get_or_create_retention_flashcard_round(text, text[], text[], integer[], integer) from anon;
revoke all on function public.record_retention_flashcard_review(uuid, text, text) from anon;
revoke all on function public.resolve_retention_flashcard_round(uuid, text) from anon;

grant execute on function public.get_or_create_retention_flashcard_round(text, text[], text[], integer[], integer) to authenticated;
grant execute on function public.record_retention_flashcard_review(uuid, text, text) to authenticated;
grant execute on function public.resolve_retention_flashcard_round(uuid, text) to authenticated;