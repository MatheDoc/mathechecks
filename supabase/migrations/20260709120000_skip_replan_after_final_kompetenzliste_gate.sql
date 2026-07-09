-- Avoid rolling back the final Kompetenzlisten gate: after the last open check,
-- the session is marked completed, so replan_session(session_id) must no longer
-- be called for that session.

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

    if remaining_open_checks = 0 then
        update public.learning_sessions
        set status = 'completed',
            ended_at = coalesce(ended_at, completion_timestamp)
        where id = updated_state.session_id
          and status = 'active';
    else
        perform public.replan_session(updated_state.session_id);
    end if;

    return updated_state;
end;
$$;

revoke all on function public.complete_kompetenzliste_gate(text, text) from public;
revoke all on function public.complete_kompetenzliste_gate(text, text) from anon;
grant execute on function public.complete_kompetenzliste_gate(text, text) to authenticated;