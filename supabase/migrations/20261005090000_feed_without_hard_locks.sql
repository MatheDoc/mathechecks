-- Feed ohne harte Sperren:
-- 1) Keine Sperre mehr zwischen Lernbereichen: jeder Start ist sofort fällig.
-- 2) Der didaktische Abstand (available_from) ist nur noch eine Empfehlung.
--    Check-Schritte mit laufendem Abstand erscheinen im Feed als 'available'
--    (vorgezogen) und dürfen abgeschlossen werden.
-- 3) Feed-Badge zählt zusätzlich heute eingeplante Schritte mit laufendem Abstand.

create or replace function public.is_lernbereich_start_ready(
    p_session_id uuid,
    p_lernbereich_slug text
)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
    select exists (
        select 1
        from public.session_lernbereiche slb
        where slb.session_id = p_session_id
          and slb.lernbereich_slug = nullif(trim(coalesce(p_lernbereich_slug, '')), '')
    );
$$;

revoke all on function public.is_lernbereich_start_ready(uuid, text) from public;
revoke all on function public.is_lernbereich_start_ready(uuid, text) from anon;

-- Quelle: 20260826090000_test_step_replaces_kompetenzliste_gate.sql (ohne available_from-Filter)
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
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and exists (
          select 1
          from public.session_check_state
          where session_check_state.session_id = learning_sessions.id
            and session_check_state.check_id = normalized_check_id
            and session_check_state.current_step_key = normalized_module_key
            and session_check_state.current_step_status = 'due'
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

    perform public.require_current_feed_cursor(matched_session_id, expected_activity_key);

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
              and current_step_status = 'due';

            did_advance := found;

            if not did_advance then
                raise exception 'Due feed activity not found';
            end if;
        else
            update public.session_check_state
            set last_outcome_key = 'repeat'
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'recall'
              and current_step_status = 'due';

            if not found then
                raise exception 'Due feed activity not found';
            end if;
        end if;
    elsif normalized_module_key = 'feynman' then
        if normalized_outcome_key = 'can_do' then
            update public.session_check_state
            set current_step_key = 'test',
                current_step_status = 'due',
                last_outcome_key = 'can_do',
                last_completed_at = inserted_attempt.created_at
            where session_id = matched_session_id
              and check_id = normalized_check_id
              and current_step_key = 'feynman'
              and current_step_status = 'due';

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
              and current_step_status = 'due';

            if not found then
                raise exception 'Due feed activity not found';
            end if;
        end if;
    end if;

    if did_advance then
        perform public.bump_feed_activity_completion_count();
        perform public.bump_session_daily_core_budget_used(matched_session_id);
        perform public.clear_current_feed_cursor(matched_session_id, expected_activity_key);
        perform public.replan_session(matched_session_id);
    end if;

    return inserted_attempt;
end;
$$;

create or replace function public.feed_cursor_open_items(p_session_id uuid)
returns table (
    activity_key text,
    activity_kind text,
    activity_type text,
    lernbereich_slug text,
    check_id text,
    step_key text,
    target_module_key text,
    available_from timestamptz,
    planned_from timestamptz,
    overdue_from timestamptz,
    effective_planned_from timestamptz,
    class_rank integer,
    urgency_rank integer,
    order_timestamp timestamptz,
    lernbereich_sort_index integer,
    step_depth integer,
    check_order integer,
    sort_bucket integer,
    sort_index integer
)
language sql
stable
set search_path = public
as $$
with now_ref as (
    select now() as current_time
)
select
    sas.activity_key,
    'start'::text as activity_kind,
    sas.activity_type,
    sas.lernbereich_slug,
    null::text as check_id,
    'start'::text as step_key,
    sas.target_module_key,
    sas.due_at as available_from,
    sas.planned_from,
    sas.overdue_from,
    case
        when sas.planned_from is null then sas.due_at
        else greatest(sas.due_at, sas.planned_from)
    end as effective_planned_from,
    10 as class_rank,
    case
        when sas.overdue_from is not null and sas.overdue_from <= now_ref.current_time then 0
        when (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        ) <= now_ref.current_time then 1
        else 2
    end as urgency_rank,
    case
        when sas.overdue_from is not null and sas.overdue_from <= now_ref.current_time then sas.overdue_from
        when (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        ) <= now_ref.current_time then (
            case
                when sas.planned_from is null then sas.due_at
                else greatest(sas.due_at, sas.planned_from)
            end
        )
        else sas.due_at
    end as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
    0 as step_depth,
    0 as check_order,
    coalesce(sas.sort_bucket, 5) as sort_bucket,
    coalesce(slb.sort_index, sas.sort_index, 0) as sort_index
from public.session_activity_state sas
left join public.session_lernbereiche slb
  on slb.session_id = sas.session_id
 and slb.lernbereich_slug = sas.lernbereich_slug
cross join now_ref
where sas.session_id = p_session_id
  and sas.activity_type = 'start'
  and sas.status = 'due'
  and sas.due_at <= now_ref.current_time

union all

select
    'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
    'check'::text as activity_kind,
    scs.current_step_key as activity_type,
    public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
    scs.check_id,
    scs.current_step_key as step_key,
    scs.current_step_key as target_module_key,
    scs.available_from,
    scs.planned_from,
    scs.overdue_from,
    case
        when scs.planned_from is null then scs.available_from
        when scs.available_from is null then scs.planned_from
        else greatest(scs.available_from, scs.planned_from)
    end as effective_planned_from,
    20 as class_rank,
    case
        when scs.overdue_from is not null and scs.overdue_from <= now_ref.current_time then 0
        when (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        ) <= now_ref.current_time then 1
        else 2
    end as urgency_rank,
    case
        when scs.overdue_from is not null and scs.overdue_from <= now_ref.current_time then scs.overdue_from
        when (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        ) <= now_ref.current_time then (
            case
                when scs.planned_from is null then scs.available_from
                when scs.available_from is null then scs.planned_from
                else greatest(scs.available_from, scs.planned_from)
            end
        )
        else scs.available_from
    end as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, 0) as lernbereich_sort_index,
    public.feed_step_depth_rank(scs.current_step_key) as step_depth,
    public.feed_check_sequence_number(scs.check_id) as check_order,
    20 as sort_bucket,
    public.feed_check_sequence_number(scs.check_id) as sort_index
from public.session_check_state scs
left join public.session_lernbereiche slb
  on slb.session_id = scs.session_id
 and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
cross join now_ref
where scs.session_id = p_session_id
  and scs.current_step_status = 'due'
  and scs.current_step_key in ('training', 'recall', 'feynman', 'test')

union all

select
    sas.activity_key,
    'flashcards'::text as activity_kind,
    sas.activity_type,
    sas.lernbereich_slug,
    sas.check_id,
    sas.activity_type as step_key,
    sas.target_module_key,
    sas.due_at as available_from,
    null::timestamptz as planned_from,
    null::timestamptz as overdue_from,
    sas.due_at as effective_planned_from,
    30 as class_rank,
    1 as urgency_rank,
    sas.due_at as order_timestamp,
    coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
    0 as step_depth,
    0 as check_order,
    coalesce(sas.sort_bucket, 50) as sort_bucket,
    coalesce(sas.sort_index, 0) as sort_index
from public.session_activity_state sas
left join public.session_lernbereiche slb
  on slb.session_id = sas.session_id
 and slb.lernbereich_slug = sas.lernbereich_slug
cross join now_ref
where sas.session_id = p_session_id
  and sas.activity_type = 'flashcards'
  and sas.status = 'due'
  and sas.due_at <= now_ref.current_time;
$$;

create or replace function public.complete_test_step(
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

    expected_activity_key := 'check:' || normalized_check_id || ':test';

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
      and session_check_state.current_step_key = 'test'
      and session_check_state.current_step_status = 'due'
    returning session_check_state.* into updated_state;

    if updated_state.session_id is null then
        raise exception 'Due test step not found';
    end if;

    perform public.require_current_feed_cursor(updated_state.session_id, expected_activity_key);
    perform public.bump_feed_activity_completion_count();
    perform public.bump_session_daily_core_budget_used(updated_state.session_id);

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
            0,
            current_completed_activity_count,
            current_completed_activity_count
        )
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
        set status = 'active',
            source_session_id = excluded.source_session_id,
            activity_interval = excluded.activity_interval,
            activity_due_exponent = excluded.activity_due_exponent,
            next_due_after_activity_count = excluded.next_due_after_activity_count,
            feed_queue_entry_activity_count = excluded.feed_queue_entry_activity_count,
            updated_at = now();

        perform public.unlock_successor_lernbereiche(updated_state.session_id, completed_lernbereich_slug);
    end if;

    select count(*)
    into remaining_open_checks
    from public.session_check_state
    where session_id = updated_state.session_id
      and current_step_key <> 'check_completed';

    perform public.clear_current_feed_cursor(updated_state.session_id, expected_activity_key);

    if remaining_open_checks > 0 then
        perform public.replan_session(updated_state.session_id);
    end if;

    return updated_state;
end;
$$;

-- Quelle: 20260606120000_feed_attention_summary_server_timing.sql
-- due_count enthält jetzt auch heute eingeplante Schritte, deren empfohlener Abstand noch läuft.

create or replace function public.feed_attention_summary(p_session_id uuid default null)
returns table (
    session_id uuid,
    overdue_count integer,
    due_count integer
)
language plpgsql
stable
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid := p_session_id;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if resolved_session_id is null then
        select id
        into resolved_session_id
        from public.learning_sessions
        where user_id = current_user_id
          and status = 'active'
        order by started_at desc
        limit 1;
    else
        perform 1
        from public.learning_sessions
        where id = resolved_session_id
          and user_id = current_user_id
          and status = 'active';

        if not found then
            raise exception 'No active learning session found';
        end if;
    end if;

    if resolved_session_id is null then
        return query select null::uuid, 0, 0;
        return;
    end if;

    return query
    select
        resolved_session_id,
        coalesce(sum(case when oi.urgency_rank = 0 then 1 else 0 end), 0)::integer as overdue_count,
        coalesce(sum(case
            when oi.urgency_rank = 1 then 1
            when oi.urgency_rank = 2 and oi.planned_from is not null and oi.planned_from <= now() then 1
            else 0
        end), 0)::integer as due_count
    from public.feed_cursor_open_items(resolved_session_id) as oi;
end;
$$;

revoke all on function public.feed_attention_summary(uuid) from public;
revoke all on function public.feed_attention_summary(uuid) from anon;
grant execute on function public.feed_attention_summary(uuid) to authenticated;

-- Bestehende, wegen Lernbereichsreihenfolge gesperrte Starts freigeben.

update public.session_activity_state sas
set status = 'due',
    due_at = now(),
    planned_from = null,
    overdue_from = null
from public.learning_sessions ls
where ls.id = sas.session_id
  and ls.status = 'active'
  and sas.activity_type = 'start'
  and sas.status = 'blocked';

do $$
declare
    v_session_id uuid;
begin
    for v_session_id in
        select id from public.learning_sessions where status = 'active'
    loop
        perform public.replan_session(v_session_id);
    end loop;
end;
$$;

grant execute on function public.record_check_module_attempt(text, text, text, text, text) to authenticated;
grant execute on function public.complete_test_step(text, text) to authenticated;

notify pgrst, 'reload schema';