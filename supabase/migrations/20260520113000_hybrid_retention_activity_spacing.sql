create table if not exists public.system_settings (
    setting_key text primary key,
    value_integer integer not null,
    description text not null,
    updated_at timestamptz not null default now(),
    check (char_length(trim(setting_key)) > 0),
    check (char_length(trim(description)) > 0)
);

drop trigger if exists set_system_settings_updated_at on public.system_settings;
create trigger set_system_settings_updated_at
    before update on public.system_settings
    for each row execute function public.set_updated_at();

insert into public.system_settings (setting_key, value_integer, description)
values
    ('feed.dashboard_item_limit', 5, 'Maximalzahl der Feed-Einträge in Dashboard und Sidebar.'),
    ('feed.retention_activity_base_gap', 5, 'Basisabstand N für Wiederholungs-Flashcards während einer aktiven Session.'),
    ('feed.retention_interleave_lead_session_items', 1, 'Wie viele Session-Aktivitäten im Hybrid-Feed vor dem ersten Wiederholungs-Slot bleiben.'),
    ('feed.retention_interleave_stride', 1, 'Wie viele weitere Session-Aktivitäten zwischen zwei Wiederholungs-Slots liegen.'),
    ('planning.default_session_tempo_days', 1, 'Standard-Tempo in Tagen pro Aktivität, wenn keine andere Session-Vorgabe gespeichert ist.')
on conflict (setting_key) do update
set value_integer = excluded.value_integer,
    description = excluded.description;

grant select on public.system_settings to anon;
grant select on public.system_settings to authenticated;

alter table public.system_settings enable row level security;

drop policy if exists system_settings_select_all_anon on public.system_settings;
create policy system_settings_select_all_anon
    on public.system_settings
    for select
    to anon
    using (true);

drop policy if exists system_settings_select_all_authenticated on public.system_settings;
create policy system_settings_select_all_authenticated
    on public.system_settings
    for select
    to authenticated
    using (true);

create or replace function public.get_system_setting_integer(
    p_setting_key text,
    p_default integer
)
returns integer
language plpgsql
security definer
stable
set search_path = public
as $$
declare
    normalized_setting_key text := nullif(trim(p_setting_key), '');
    configured_value integer;
begin
    if normalized_setting_key is null then
        return p_default;
    end if;

    select value_integer
    into configured_value
    from public.system_settings
    where setting_key = normalized_setting_key;

    return coalesce(configured_value, p_default);
end;
$$;

revoke all on function public.get_system_setting_integer(text, integer) from public;
revoke all on function public.get_system_setting_integer(text, integer) from anon;
grant execute on function public.get_system_setting_integer(text, integer) to authenticated;
grant execute on function public.get_system_setting_integer(text, integer) to anon;

create table if not exists public.user_feed_activity_counters (
    user_id uuid primary key references auth.users(id) on delete cascade,
    completed_activity_count bigint not null default 0 check (completed_activity_count >= 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists set_user_feed_activity_counters_updated_at on public.user_feed_activity_counters;
create trigger set_user_feed_activity_counters_updated_at
    before update on public.user_feed_activity_counters
    for each row execute function public.set_updated_at();

alter table public.user_feed_activity_counters enable row level security;

create or replace function public.get_current_feed_activity_completion_count()
returns bigint
language plpgsql
security definer
stable
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    current_count bigint := 0;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    select coalesce(completed_activity_count, 0)
    into current_count
    from public.user_feed_activity_counters
    where user_id = current_user_id;

    return coalesce(current_count, 0);
end;
$$;

create or replace function public.bump_feed_activity_completion_count()
returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    updated_count bigint;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    insert into public.user_feed_activity_counters (
        user_id,
        completed_activity_count
    )
    values (
        current_user_id,
        1
    )
    on conflict (user_id) do update
    set completed_activity_count = public.user_feed_activity_counters.completed_activity_count + 1
    returning completed_activity_count into updated_count;

    return updated_count;
end;
$$;

revoke all on function public.get_current_feed_activity_completion_count() from public;
revoke all on function public.get_current_feed_activity_completion_count() from anon;
grant execute on function public.get_current_feed_activity_completion_count() to authenticated;

revoke all on function public.bump_feed_activity_completion_count() from public;
revoke all on function public.bump_feed_activity_completion_count() from anon;
grant execute on function public.bump_feed_activity_completion_count() to authenticated;

alter table public.user_retention_scopes
    add column if not exists activity_interval integer not null default 5 check (activity_interval > 0),
    add column if not exists activity_due_exponent integer not null default 0 check (activity_due_exponent >= 0),
    add column if not exists next_due_after_activity_count bigint null check (next_due_after_activity_count >= 0);

create index if not exists user_retention_scopes_activity_due_idx
    on public.user_retention_scopes (user_id, status, next_due_after_activity_count, lernbereich_slug);

insert into public.user_feed_activity_counters (user_id, completed_activity_count)
select distinct scopes.user_id, 0
from public.user_retention_scopes as scopes
on conflict (user_id) do nothing;

update public.user_retention_scopes as scopes
set activity_interval = public.get_system_setting_integer('feed.retention_activity_base_gap', 5),
    activity_due_exponent = 0,
    next_due_after_activity_count = coalesce(counters.completed_activity_count, 0)
        + public.get_system_setting_integer('feed.retention_activity_base_gap', 5)
from public.user_feed_activity_counters as counters
where counters.user_id = scopes.user_id
  and scopes.next_due_after_activity_count is null;

drop function if exists public.save_active_learning_session(text[], text[], integer, text[], date, text);

create function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_tempo_days integer default null,
    p_included_check_ids text[] default array[]::text[],
    p_target_date date default null,
    p_target_source text default null
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
    default_tempo_days integer := public.get_system_setting_integer('planning.default_session_tempo_days', 1);
    normalized_lernbereiche text[];
    normalized_excluded_check_ids text[];
    normalized_included_check_ids text[];
    normalized_target_date date := p_target_date;
    normalized_target_source text := nullif(trim(coalesce(p_target_source, '')), '');
    current_lernbereich_slug text;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_tempo_days is not null and p_tempo_days <= 0 then
        raise exception 'tempo_days must be positive';
    end if;

    if normalized_target_date is not null and normalized_target_date < current_date then
        raise exception 'target_date must be today or later';
    end if;

    if normalized_target_date is null then
        normalized_target_source := null;
    elsif normalized_target_source is null then
        normalized_target_source := 'explicit';
    elsif normalized_target_source not in ('explicit', 'suggested') then
        raise exception 'unsupported target_source';
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

    effective_tempo_days := coalesce(p_tempo_days, active_tempo_days, default_tempo_days);

    if active_session_id is null then
        begin
            insert into public.learning_sessions (
                user_id,
                status,
                tempo_days,
                target_date,
                target_source
            )
            values (
                current_user_id,
                'active',
                effective_tempo_days,
                normalized_target_date,
                normalized_target_source
            )
            returning id into active_session_id;
        exception
            when unique_violation then
                raise exception 'An active learning session already exists';
        end;
    else
        update public.learning_sessions
        set tempo_days = effective_tempo_days,
            target_date = normalized_target_date,
            target_source = normalized_target_source,
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

    perform public.bump_feed_activity_completion_count();

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
                set current_step_key = 'training_2',
                    current_step_status = 'due',
                    last_outcome_key = 'can_do',
                    last_completed_at = inserted_attempt.created_at
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'recall'
                  and current_step_status = 'due';

                did_advance := found;
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
        normalized_lernbereich_slug,
        normalized_status,
        null,
        retention_activity_gap,
        0,
        current_completed_activity_count + retention_activity_gap
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
            when excluded.status = 'active' then current_completed_activity_count + public.user_retention_scopes.activity_interval
            else public.user_retention_scopes.next_due_after_activity_count
        end
    returning * into updated_scope;

    return updated_scope;
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
            where input_cards.input_card_id is not null
              and input_cards.input_check_id is not null
              and public.check_id_lernbereich_slug(input_cards.input_check_id) = normalized_lernbereich_slug
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

    if normalized_decision_key = 'complete' then
        perform public.bump_feed_activity_completion_count();
    end if;

    return updated_activity;
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
    scope_activity_interval integer;
    scope_due_exponent integer;
    next_completed_activity_count bigint;
    next_scope_due_exponent integer;
    next_scope_due_after_activity_count bigint;
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
            next_due_after_activity_count = next_scope_due_after_activity_count
        where user_id = current_user_id
          and activity_type = 'flashcards'
          and scope_type = 'lernbereich'
          and lernbereich_slug = matched_round.lernbereich_slug;
    end if;

    return updated_round;
end;
$$;