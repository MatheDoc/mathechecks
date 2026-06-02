alter table public.session_check_state
    add column if not exists available_from timestamptz null,
    add column if not exists overdue_from timestamptz null;

create index if not exists session_check_state_session_feed_timing_idx
    on public.session_check_state (session_id, current_step_status, available_from, overdue_from, current_step_key);

create or replace function public.get_core_feed_gap_interval()
returns interval
language sql
stable
set search_path = public
as $$
    select make_interval(hours => greatest(public.get_system_setting_integer('feed.core_gap_normal_hours', 24), 1));
$$;

create or replace function public.apply_session_check_timing_fields()
returns trigger
language plpgsql
set search_path = public
as $$
declare
    core_gap interval := public.get_core_feed_gap_interval();
begin
    if new.current_step_key = 'check_completed' or new.current_step_status = 'completed' then
        new.available_from := null;
        new.overdue_from := null;
        return new;
    end if;

    if new.current_step_key = 'training' then
        new.available_from := coalesce(new.available_from, old.available_from, now());
        new.overdue_from := null;
        return new;
    end if;

    if new.current_step_key in ('recall', 'feynman', 'kompetenzliste_gate') then
        if new.last_completed_at is null then
            new.available_from := coalesce(new.available_from, old.available_from, now());
            new.overdue_from := coalesce(new.overdue_from, old.overdue_from);
            return new;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.available_from is null
           or new.overdue_from is null then
            new.available_from := new.last_completed_at + core_gap;
            new.overdue_from := new.last_completed_at + core_gap + core_gap;
        end if;

        return new;
    end if;

    return new;
end;
$$;

drop trigger if exists set_session_check_state_timing_fields on public.session_check_state;
create trigger set_session_check_state_timing_fields
    before insert or update on public.session_check_state
    for each row execute function public.apply_session_check_timing_fields();

update public.session_check_state
set available_from = case
        when current_step_key = 'training' and current_step_status <> 'completed'
            then coalesce(available_from, created_at, now())
        when current_step_key in ('recall', 'feynman', 'kompetenzliste_gate') and current_step_status <> 'completed'
            then coalesce(last_completed_at, updated_at, now()) + public.get_core_feed_gap_interval()
        else null
    end,
    overdue_from = case
        when current_step_key in ('recall', 'feynman', 'kompetenzliste_gate') and current_step_status <> 'completed'
            then coalesce(last_completed_at, updated_at, now()) + public.get_core_feed_gap_interval() + public.get_core_feed_gap_interval()
        else null
    end;

create or replace function public.complete_current_training_step(
    p_check_id text,
    p_activity_key text
)
returns public.session_check_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_check_id text := nullif(trim(p_check_id), '');
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
    updated_state public.session_check_state;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'check:' || normalized_check_id || ':training';

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    update public.session_check_state
    set current_step_key = 'recall',
        current_step_status = 'due',
        last_outcome_key = 'complete',
        last_completed_at = completion_timestamp
    from public.learning_sessions
    where learning_sessions.id = session_check_state.session_id
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and session_check_state.check_id = normalized_check_id
      and session_check_state.current_step_key = 'training'
      and session_check_state.current_step_status = 'due'
      and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
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
    p_outcome_key text,
    p_activity_key text
)
returns public.learning_activity_attempts
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    normalized_check_id text := nullif(trim(coalesce(p_check_id, '')), '');
    normalized_module_key text := lower(coalesce(nullif(trim(p_module_key), ''), ''));
    normalized_outcome_key text := lower(coalesce(nullif(trim(p_outcome_key), ''), ''));
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
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

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'check:' || normalized_check_id || ':' || normalized_module_key;

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    select learning_sessions.id
    into matched_session_id
    from public.learning_sessions
    join public.session_check_state
      on session_check_state.session_id = learning_sessions.id
     and session_check_state.check_id = normalized_check_id
     and session_check_state.current_step_key = normalized_module_key
     and session_check_state.current_step_status = 'due'
     and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
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

    if matched_session_id is null then
        raise exception 'Due feed activity not found';
    end if;

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
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            did_advance := found;

            if not did_advance then
                raise exception 'Due feed activity not found';
            end if;

            perform public.unlock_successor_lernbereiche(matched_session_id, normalized_lernbereich_slug);
        else
            update public.session_check_state
            set last_outcome_key = 'repeat'
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'recall'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            if not found then
                raise exception 'Due feed activity not found';
            end if;
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
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            did_advance := found;

            if not did_advance then
                raise exception 'Due feed activity not found';
            end if;
        else
            update public.session_check_state
            set last_outcome_key = 'repeat'
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'feynman'
              and current_step_status = 'due'
              and coalesce(available_from, '-infinity'::timestamptz) <= completion_timestamp;

            if not found then
                raise exception 'Due feed activity not found';
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
    p_check_id text,
    p_activity_key text
)
returns public.session_check_state
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_check_id text := nullif(trim(coalesce(p_check_id, '')), '');
    normalized_activity_key text := nullif(trim(coalesce(p_activity_key, '')), '');
    expected_activity_key text;
    completion_timestamp timestamptz := now();
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

    if normalized_activity_key is null then
        raise exception 'activity_key is required';
    end if;

    expected_activity_key := 'check:' || normalized_check_id || ':kompetenzliste_gate';

    if normalized_activity_key <> expected_activity_key then
        raise exception 'Feed activity mismatch';
    end if;

    update public.session_check_state
    set current_step_key = 'check_completed',
        current_step_status = 'completed',
        last_outcome_key = 'complete',
        last_completed_at = completion_timestamp
    from public.learning_sessions
    where learning_sessions.id = session_check_state.session_id
      and learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and session_check_state.check_id = normalized_check_id
      and session_check_state.current_step_key = 'kompetenzliste_gate'
      and session_check_state.current_step_status = 'due'
      and coalesce(session_check_state.available_from, '-infinity'::timestamptz) <= completion_timestamp
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
            1,
            current_completed_activity_count + retention_activity_gap,
            current_completed_activity_count + retention_activity_gap
        )
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set status = 'active',
            source_session_id = excluded.source_session_id,
            activity_interval = excluded.activity_interval,
            activity_due_exponent = excluded.activity_due_exponent,
            next_due_after_activity_count = case
                when public.user_retention_scopes.status = 'active' then public.user_retention_scopes.next_due_after_activity_count
                else excluded.next_due_after_activity_count
            end,
            feed_queue_entry_activity_count = case
                when public.user_retention_scopes.status = 'active' then public.user_retention_scopes.feed_queue_entry_activity_count
                when public.user_retention_scopes.status in ('paused', 'opted_out') then null
                else excluded.feed_queue_entry_activity_count
            end,
            updated_at = now();
    end if;

    select count(*)
    into remaining_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and current_step_key <> 'check_completed';

    if remaining_open_checks = 0 then
        update public.learning_sessions
        set status = 'completed',
            ended_at = coalesce(ended_at, completion_timestamp)
        where id = updated_state.session_id
          and status = 'active';
    end if;

    return updated_state;
end;
$$;