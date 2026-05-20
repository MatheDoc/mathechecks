create table public.session_activity_state (
    session_id uuid not null references public.learning_sessions(id) on delete cascade,
    activity_key text not null check (char_length(trim(activity_key)) > 0),
    activity_type text not null check (activity_type in ('flashcards')),
    scope_type text not null check (scope_type in ('lernbereich')),
    lernbereich_slug text null,
    check_id text null,
    target_module_key text not null check (char_length(trim(target_module_key)) > 0),
    status text not null check (status in ('blocked', 'due', 'completed')),
    due_at timestamptz not null default now(),
    sort_bucket integer not null default 50,
    sort_index integer not null default 0,
    last_outcome_key text null check (last_outcome_key in ('complete', 'keep_open')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (session_id, activity_key)
);

create index session_activity_state_due_idx
    on public.session_activity_state (session_id, status, due_at, sort_bucket, sort_index);

create index session_activity_state_lernbereich_idx
    on public.session_activity_state (session_id, activity_type, lernbereich_slug);

drop trigger if exists set_session_activity_state_updated_at on public.session_activity_state;
create trigger set_session_activity_state_updated_at
    before update on public.session_activity_state
    for each row execute function public.set_updated_at();

create table public.session_flashcard_card_state (
    session_id uuid not null references public.learning_sessions(id) on delete cascade,
    lernbereich_slug text not null check (char_length(trim(lernbereich_slug)) > 0),
    card_id text not null check (char_length(trim(card_id)) > 0),
    check_id text not null check (char_length(trim(check_id)) > 0),
    seen_count integer not null default 0 check (seen_count >= 0),
    level integer not null default 0 check (level >= 0),
    next_due_at timestamptz not null default now(),
    last_rating_key text null check (last_rating_key in ('hard', 'medium', 'easy')),
    last_reviewed_at timestamptz null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (session_id, card_id)
);

create index session_flashcard_card_state_due_idx
    on public.session_flashcard_card_state (session_id, lernbereich_slug, next_due_at);

drop trigger if exists set_session_flashcard_card_state_updated_at on public.session_flashcard_card_state;
create trigger set_session_flashcard_card_state_updated_at
    before update on public.session_flashcard_card_state
    for each row execute function public.set_updated_at();

create table public.session_flashcard_rounds (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references public.learning_sessions(id) on delete cascade,
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

create unique index session_flashcard_rounds_active_idx
    on public.session_flashcard_rounds (session_id, activity_key)
    where status = 'active';

create index session_flashcard_rounds_session_idx
    on public.session_flashcard_rounds (session_id, activity_key, status, started_at desc);

drop trigger if exists set_session_flashcard_rounds_updated_at on public.session_flashcard_rounds;
create trigger set_session_flashcard_rounds_updated_at
    before update on public.session_flashcard_rounds
    for each row execute function public.set_updated_at();

create table public.session_flashcard_round_cards (
    session_id uuid not null references public.learning_sessions(id) on delete cascade,
    round_id uuid not null references public.session_flashcard_rounds(id) on delete cascade,
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

create index session_flashcard_round_cards_session_idx
    on public.session_flashcard_round_cards (session_id, round_id, position);

drop trigger if exists set_session_flashcard_round_cards_updated_at on public.session_flashcard_round_cards;
create trigger set_session_flashcard_round_cards_updated_at
    before update on public.session_flashcard_round_cards
    for each row execute function public.set_updated_at();

grant select on public.session_activity_state to authenticated;
grant select on public.session_flashcard_card_state to authenticated;
grant select on public.session_flashcard_rounds to authenticated;
grant select on public.session_flashcard_round_cards to authenticated;

alter table public.session_activity_state enable row level security;
alter table public.session_flashcard_card_state enable row level security;
alter table public.session_flashcard_rounds enable row level security;
alter table public.session_flashcard_round_cards enable row level security;

create policy session_activity_state_select_own
    on public.session_activity_state
    for select
    to authenticated
    using (
        exists (
            select 1
            from public.learning_sessions
            where learning_sessions.id = session_activity_state.session_id
              and learning_sessions.user_id = (select auth.uid())
        )
    );

create policy session_flashcard_card_state_select_own
    on public.session_flashcard_card_state
    for select
    to authenticated
    using (
        exists (
            select 1
            from public.learning_sessions
            where learning_sessions.id = session_flashcard_card_state.session_id
              and learning_sessions.user_id = (select auth.uid())
        )
    );

create policy session_flashcard_rounds_select_own
    on public.session_flashcard_rounds
    for select
    to authenticated
    using (
        exists (
            select 1
            from public.learning_sessions
            where learning_sessions.id = session_flashcard_rounds.session_id
              and learning_sessions.user_id = (select auth.uid())
        )
    );

create policy session_flashcard_round_cards_select_own
    on public.session_flashcard_round_cards
    for select
    to authenticated
    using (
        exists (
            select 1
            from public.learning_sessions
            where learning_sessions.id = session_flashcard_round_cards.session_id
              and learning_sessions.user_id = (select auth.uid())
        )
    );

create or replace function public.check_id_lernbereich_slug(p_check_id text)
returns text
language sql
immutable
as $$
    select nullif(split_part(trim(coalesce(p_check_id, '')), '__', 2), '')
$$;

create or replace function public.refresh_flashcard_activity_for_lernbereich(
    p_session_id uuid,
    p_lernbereich_slug text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    normalized_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    normalized_activity_key text;
    included_count integer;
    ready_count integer;
begin
    if p_session_id is null or normalized_lernbereich_slug is null then
        return;
    end if;

    normalized_activity_key := 'lernbereich:' || normalized_lernbereich_slug || ':flashcards';

    select count(*)
    into included_count
    from public.session_check_state
    where session_id = p_session_id
      and public.check_id_lernbereich_slug(check_id) = normalized_lernbereich_slug;

    select count(*)
    into ready_count
    from public.session_check_state
    where session_id = p_session_id
      and public.check_id_lernbereich_slug(check_id) = normalized_lernbereich_slug
      and current_step_key in ('kompetenzliste_gate', 'check_completed');

    if included_count > 0 and ready_count = included_count then
        insert into public.session_activity_state (
            session_id,
            activity_key,
            activity_type,
            scope_type,
            lernbereich_slug,
            check_id,
            target_module_key,
            status,
            due_at,
            sort_bucket,
            sort_index,
            last_outcome_key
        )
        values (
            p_session_id,
            normalized_activity_key,
            'flashcards',
            'lernbereich',
            normalized_lernbereich_slug,
            null,
            'flashcards',
            'due',
            now(),
            60,
            0,
            null
        )
        on conflict (session_id, activity_key) do update
        set status = case
                when session_activity_state.due_at <= now() then 'due'
                else session_activity_state.status
            end,
            target_module_key = 'flashcards',
            sort_bucket = 60,
            sort_index = 0;
        return;
    end if;

    delete from public.session_activity_state
    where session_id = p_session_id
      and activity_type = 'flashcards'
      and scope_type = 'lernbereich'
      and lernbereich_slug = normalized_lernbereich_slug;
end;
$$;

drop function if exists public.save_active_learning_session(text[], text[], integer, text[]);

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
    lernbereich_slug text;
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

    delete from public.session_activity_state
    where session_id = active_session_id
      and activity_type = 'flashcards'
      and scope_type = 'lernbereich'
      and not (lernbereich_slug = any(coalesce(normalized_lernbereiche, array[]::text[])));

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

    foreach lernbereich_slug in array normalized_lernbereiche loop
        perform public.refresh_flashcard_activity_for_lernbereich(active_session_id, lernbereich_slug);
    end loop;

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

    updated_lernbereich_slug := public.check_id_lernbereich_slug(updated_state.check_id);
    if updated_state.current_step_key = 'kompetenzliste_gate' and updated_lernbereich_slug is not null then
        perform public.refresh_flashcard_activity_for_lernbereich(updated_state.session_id, updated_lernbereich_slug);
    end if;

    return updated_state;
end;
$$;

create or replace function public.get_or_create_flashcard_round(
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
    active_session_id uuid;
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

    select learning_sessions.id
    into active_session_id
    from public.learning_sessions
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and exists (
          select 1
          from public.session_lernbereiche
          where session_lernbereiche.session_id = learning_sessions.id
            and session_lernbereiche.lernbereich_slug = normalized_lernbereich_slug
      )
    limit 1;

    if active_session_id is null then
        raise exception 'Active learning session not found';
    end if;

    perform public.refresh_flashcard_activity_for_lernbereich(active_session_id, normalized_lernbereich_slug);
    active_activity_key := 'lernbereich:' || normalized_lernbereich_slug || ':flashcards';

    update public.session_activity_state
    set status = 'due'
    where session_id = active_session_id
      and activity_key = active_activity_key
      and activity_type = 'flashcards'
      and due_at <= now();

    if not exists (
        select 1
        from public.session_activity_state
        where session_id = active_session_id
          and activity_key = active_activity_key
          and activity_type = 'flashcards'
          and scope_type = 'lernbereich'
          and lernbereich_slug = normalized_lernbereich_slug
          and status = 'due'
    ) then
        raise exception 'Flashcard activity is not due';
    end if;

    select id
    into active_round_id
    from public.session_flashcard_rounds
    where session_id = active_session_id
      and activity_key = active_activity_key
      and status = 'active'
    order by started_at desc
    limit 1;

    if active_round_id is null then
        select coalesce(max(round_index), 0) + 1
        into next_round_index
        from public.session_flashcard_rounds
        where session_id = active_session_id
          and activity_key = active_activity_key;

        insert into public.session_flashcard_rounds (
            session_id,
            activity_key,
            lernbereich_slug,
            round_index,
            status,
            card_limit
        )
        values (
            active_session_id,
            active_activity_key,
            normalized_lernbereich_slug,
            next_round_index,
            'active',
            effective_limit
        )
        returning id into active_round_id;

        with input_cards as (
            select
                nullif(trim(p_card_ids[ord]), '') as input_card_id,
                nullif(trim(p_check_ids[ord]), '') as input_check_id,
                greatest(coalesce(p_task_indices[ord], 0), 0) as input_task_index,
                ord
            from generate_subscripts(p_card_ids, 1) as card_index(ord)
        ),
        allowed_cards as (
            select distinct on (input_cards.input_card_id)
                input_cards.input_card_id as card_id,
                input_cards.input_check_id as check_id,
                input_cards.input_task_index as task_index,
                input_cards.ord
            from input_cards
            join public.session_check_state
              on session_check_state.session_id = active_session_id
             and session_check_state.check_id = input_cards.input_check_id
            where input_cards.input_card_id is not null
              and input_cards.input_check_id is not null
              and public.check_id_lernbereich_slug(input_cards.input_check_id) = normalized_lernbereich_slug
            order by input_cards.input_card_id, input_cards.ord
        ),
        ranked_cards as (
            select
                allowed_cards.*,
                coalesce(card_state.next_due_at, '-infinity'::timestamptz) as next_due_at,
                case
                    when card_state.card_id is null then 0
                    when card_state.next_due_at <= now() then 1
                    else 2
                end as due_priority,
                random() as random_sort
            from allowed_cards
            left join public.session_flashcard_card_state as card_state
              on card_state.session_id = active_session_id
             and card_state.card_id = allowed_cards.card_id
        ),
        selected_cards as (
            select *
            from ranked_cards
            order by due_priority, next_due_at, random_sort
            limit effective_limit
        ),
        positioned_cards as (
            select
                selected_cards.*,
                row_number() over (order by due_priority, next_due_at, random_sort)::integer as card_position
            from selected_cards
        )
        insert into public.session_flashcard_round_cards (
            session_id,
            round_id,
            card_id,
            check_id,
            position,
            task_index
        )
        select
            active_session_id,
            active_round_id,
            card_id,
            check_id,
            card_position,
            task_index
        from positioned_cards;

        if not exists (
            select 1
            from public.session_flashcard_round_cards
            where round_id = active_round_id
        ) then
            raise exception 'No flashcards available for selected checks';
        end if;
    end if;

    return query
    select
        rounds.id as round_id,
        rounds.activity_key,
        rounds.status as round_status,
        round_cards.card_id,
        round_cards.check_id,
        round_cards.position as card_position,
        round_cards.task_index,
        round_cards.rating_key,
        round_cards.reviewed_at,
        count(*) over ()::integer as total_cards,
        count(round_cards.reviewed_at) over ()::integer as reviewed_count
    from public.session_flashcard_rounds as rounds
    join public.session_flashcard_round_cards as round_cards
      on round_cards.round_id = rounds.id
    where rounds.id = active_round_id
      and rounds.session_id = active_session_id
    order by round_cards.position;
end;
$$;

create or replace function public.record_flashcard_review(
    p_round_id uuid,
    p_card_id text,
    p_rating_key text
)
returns public.session_flashcard_round_cards
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_card_id text := nullif(trim(p_card_id), '');
    normalized_rating_key text := lower(coalesce(nullif(trim(p_rating_key), ''), ''));
    matched_round public.session_flashcard_rounds;
    matched_tempo_days integer;
    matched_card public.session_flashcard_round_cards;
    previous_level integer := 0;
    next_level integer := 0;
    interval_days integer := 0;
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
    from public.session_flashcard_rounds as rounds
    join public.learning_sessions
      on learning_sessions.id = rounds.session_id
    where rounds.id = p_round_id
      and rounds.status = 'active'
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
    for update of rounds;

    if matched_round.id is null then
        raise exception 'Active flashcard round not found';
    end if;

    select tempo_days
    into matched_tempo_days
    from public.learning_sessions
    where id = matched_round.session_id;

    update public.session_flashcard_round_cards
    set rating_key = normalized_rating_key,
        reviewed_at = now()
    where round_id = matched_round.id
      and card_id = normalized_card_id
    returning * into matched_card;

    if matched_card.round_id is null then
        raise exception 'Flashcard not found in current round';
    end if;

    select level
    into previous_level
    from public.session_flashcard_card_state
    where session_id = matched_round.session_id
      and card_id = matched_card.card_id;

    previous_level := coalesce(previous_level, 0);

    if normalized_rating_key = 'hard' then
        next_level := 0;
        interval_days := 0;
    elsif normalized_rating_key = 'medium' then
        next_level := greatest(previous_level, 1);
        interval_days := greatest(coalesce(matched_tempo_days, 1), 1);
    else
        next_level := least(previous_level + 1, 8);
        interval_days := greatest(coalesce(matched_tempo_days, 1), 1) * power(2, next_level)::integer;
    end if;

    insert into public.session_flashcard_card_state (
        session_id,
        lernbereich_slug,
        card_id,
        check_id,
        seen_count,
        level,
        next_due_at,
        last_rating_key,
        last_reviewed_at
    )
    values (
        matched_round.session_id,
        matched_round.lernbereich_slug,
        matched_card.card_id,
        matched_card.check_id,
        1,
        next_level,
        now() + make_interval(days => interval_days),
        normalized_rating_key,
        now()
    )
    on conflict (session_id, card_id) do update
    set seen_count = session_flashcard_card_state.seen_count + 1,
        level = excluded.level,
        next_due_at = excluded.next_due_at,
        last_rating_key = excluded.last_rating_key,
        last_reviewed_at = excluded.last_reviewed_at,
        lernbereich_slug = excluded.lernbereich_slug,
        check_id = excluded.check_id;

    return matched_card;
end;
$$;

create or replace function public.resolve_flashcard_round(
    p_round_id uuid,
    p_decision_key text
)
returns public.session_activity_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_decision_key text := lower(coalesce(nullif(trim(p_decision_key), ''), ''));
    matched_round public.session_flashcard_rounds;
    reviewed_count integer;
    total_count integer;
    next_activity_due_at timestamptz;
    next_activity_status text;
    updated_activity public.session_activity_state;
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
    from public.session_flashcard_rounds as rounds
    join public.learning_sessions
      on learning_sessions.id = rounds.session_id
    where rounds.id = p_round_id
      and rounds.status = 'active'
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
    for update of rounds;

    if matched_round.id is null then
        raise exception 'Active flashcard round not found';
    end if;

    select count(*), count(reviewed_at)
    into total_count, reviewed_count
    from public.session_flashcard_round_cards
    where round_id = matched_round.id;

    if total_count = 0 or reviewed_count < total_count then
        raise exception 'Flashcard round is not fully reviewed';
    end if;

    update public.session_flashcard_rounds
    set status = 'completed',
        completed_at = now()
    where id = matched_round.id;

    if normalized_decision_key = 'keep_open' then
        next_activity_due_at := now();
        next_activity_status := 'due';
    else
        select min(card_state.next_due_at)
        into next_activity_due_at
        from public.session_flashcard_round_cards as round_cards
        join public.session_flashcard_card_state as card_state
          on card_state.session_id = matched_round.session_id
         and card_state.card_id = round_cards.card_id
        where round_cards.round_id = matched_round.id;

        next_activity_due_at := coalesce(next_activity_due_at, now());
        next_activity_status := case when next_activity_due_at <= now() then 'due' else 'completed' end;
    end if;

    update public.session_activity_state
    set status = next_activity_status,
        due_at = next_activity_due_at,
        last_outcome_key = normalized_decision_key
    where session_id = matched_round.session_id
      and activity_key = matched_round.activity_key
    returning * into updated_activity;

    if updated_activity.session_id is null then
        raise exception 'Flashcard activity not found';
    end if;

    return updated_activity;
end;
$$;

revoke all on function public.save_active_learning_session(text[], text[], integer, text[]) from public;
revoke all on function public.complete_current_training_step(text) from public;
revoke all on function public.get_or_create_flashcard_round(text, text[], text[], integer[], integer) from public;
revoke all on function public.record_flashcard_review(uuid, text, text) from public;
revoke all on function public.resolve_flashcard_round(uuid, text) from public;

revoke all on function public.save_active_learning_session(text[], text[], integer, text[]) from anon;
revoke all on function public.complete_current_training_step(text) from anon;
revoke all on function public.get_or_create_flashcard_round(text, text[], text[], integer[], integer) from anon;
revoke all on function public.record_flashcard_review(uuid, text, text) from anon;
revoke all on function public.resolve_flashcard_round(uuid, text) from anon;

grant execute on function public.save_active_learning_session(text[], text[], integer, text[]) to authenticated;
grant execute on function public.complete_current_training_step(text) to authenticated;
grant execute on function public.get_or_create_flashcard_round(text, text[], text[], integer[], integer) to authenticated;
grant execute on function public.record_flashcard_review(uuid, text, text) to authenticated;
grant execute on function public.resolve_flashcard_round(uuid, text) to authenticated;
