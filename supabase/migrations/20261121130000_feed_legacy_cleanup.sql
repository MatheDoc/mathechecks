-- Aufräumen nach der Feed-Vereinfachung (20261121120000_feed_simplification.sql):
-- Cursor, Sticky-Lock, Zeitfenster, Replanning, Druckprofile, Start-Freischaltung und
-- session-scoped Flashcard-Runden werden vom Feed nicht mehr genutzt und entfernt.
--
-- Bleibt bestehen:
-- - session_check_state als reine Mitgliedschaft (session_id, check_id)
-- - session_flashcard_card_state / -rounds / -round_cards als historische Kartenstände
--   (finish_learning_session übernimmt sie weiterhin in die Retention)
-- - learning_activity_attempts als historische Rohdaten

-- 1) Session speichern ohne Altlasten (Signatur unverändert)
create or replace function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_activities_per_day numeric default null,
    p_included_check_ids text[] default array[]::text[],
    p_target_date date default null,
    p_target_source text default null,
    p_lernbereiche_meta jsonb default null,
    p_name text default null
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    active_session_id uuid;
    current_activities_per_day numeric;
    effective_activities_per_day numeric;
    default_activities_per_day numeric := public.get_default_activities_per_day();
    normalized_lernbereiche text[];
    normalized_excluded_check_ids text[];
    normalized_included_check_ids text[];
    normalized_target_date date := p_target_date;
    normalized_target_source text := nullif(trim(coalesce(p_target_source, '')), '');
    normalized_name text := left(nullif(trim(coalesce(p_name, '')), ''), 80);
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_activities_per_day is not null and p_activities_per_day <= 0 then
        raise exception 'activities_per_day must be positive';
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

    select id, activities_per_day
    into active_session_id, current_activities_per_day
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

    effective_activities_per_day := round(greatest(coalesce(p_activities_per_day, current_activities_per_day, default_activities_per_day), 0.1), 2);

    if active_session_id is null then
        begin
            insert into public.learning_sessions (
                user_id,
                status,
                activities_per_day,
                target_date,
                target_source,
                name
            )
            values (
                current_user_id,
                'active',
                effective_activities_per_day,
                normalized_target_date,
                normalized_target_source,
                normalized_name
            )
            returning id into active_session_id;
        exception
            when unique_violation then
                raise exception 'An active learning session already exists';
        end;
    else
        update public.learning_sessions
        set activities_per_day = effective_activities_per_day,
            target_date = normalized_target_date,
            target_source = normalized_target_source,
            name = coalesce(normalized_name, name),
            planning_revision = planning_revision + 1
        where id = active_session_id;

        delete from public.session_check_exclusions
        where session_id = active_session_id;

        delete from public.session_lernbereiche
        where session_id = active_session_id;
    end if;

    insert into public.session_lernbereiche (session_id, lernbereich_slug, sort_index, gebiet, gebiet_order)
    select
        active_session_id,
        lb.slug,
        coalesce((meta_elem.val->>'sort_index')::integer, 0),
        coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), ''),
        coalesce(
            (meta_elem.val->>'gebiet_order')::integer,
            case coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), '')
                when 'analysis' then 1
                when 'stochastik' then 2
                when 'lineare-algebra' then 3
                else 0
            end
        )
    from unnest(normalized_lernbereiche) as lb(slug)
    left join lateral (
        select elem as val
        from jsonb_array_elements(coalesce(p_lernbereiche_meta, '[]'::jsonb)) as elem
        where elem->>'slug' = lb.slug
        limit 1
    ) as meta_elem on true;

    if coalesce(array_length(normalized_excluded_check_ids, 1), 0) > 0 then
        insert into public.session_check_exclusions (session_id, check_id)
        select active_session_id, check_id
        from unnest(normalized_excluded_check_ids) as excluded_checks(check_id);
    end if;

    -- Mitgliedschaft der Checks synchronisieren; Abschlüsse in session_activity_completions bleiben stabil.
    delete from public.session_check_state
    where session_id = active_session_id
      and not (check_id = any(coalesce(normalized_included_check_ids, array[]::text[])));

    if coalesce(array_length(normalized_included_check_ids, 1), 0) > 0 then
        insert into public.session_check_state (session_id, check_id)
        select active_session_id, included_check_id
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    return active_session_id;
end;
$$;

revoke all on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb, text) from public;
revoke all on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb, text) from anon;
grant execute on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb, text) to authenticated;

-- 2) Funktionen des alten Cursor-/Replan-Feeds entfernen (alle Überladungen)
do $$
declare
    fn record;
begin
    for fn in
        select p.oid::regprocedure as signature
        from pg_proc p
        join pg_namespace n on n.oid = p.pronamespace
        where n.nspname = 'public'
          and p.proname = any (array[
              'pick_feed_cursor',
              'require_current_feed_cursor',
              'clear_current_feed_cursor',
              'renew_current_feed_cursor',
              'get_feed_cursor_lock_interval',
              'feed_cursor_open_items',
              'replan_session',
              'get_session_remaining_activity_count',
              'get_session_required_activities_per_day',
              'get_session_pressure_ratio',
              'get_session_core_gap_hours',
              'get_session_core_gap_interval',
              'get_core_feed_gap_interval',
              'apply_session_check_timing_fields',
              'bump_session_daily_core_budget_used',
              'derive_learning_session_tempo_days',
              'feed_step_depth_rank',
              'is_lernbereich_start_ready',
              'unlock_successor_lernbereiche',
              'refresh_flashcard_activity_for_lernbereich',
              'get_or_create_flashcard_round',
              'record_flashcard_review',
              'resolve_flashcard_round',
              'complete_kompetenzliste_gate',
              'defer_feed_activity',
              'clear_feed_activity_deferral'
          ])
    loop
        execute 'drop function ' || fn.signature;
    end loop;
end;
$$;

-- 3) Tabellen des alten Feeds
drop table if exists public.session_feed_cursor;
drop table if exists public.session_activity_state;
drop table if exists public.user_feed_activity_deferrals;

-- 4) session_check_state auf Mitgliedschaft reduzieren
alter table public.session_check_state
    drop constraint if exists session_check_state_current_step_key_check;

alter table public.session_check_state
    drop column if exists current_step_key,
    drop column if exists current_step_status,
    drop column if exists last_outcome_key,
    drop column if exists last_completed_at,
    drop column if exists available_from,
    drop column if exists planned_from,
    drop column if exists overdue_from;

-- 5) Tagesbudget des alten Feeds
alter table public.learning_sessions
    drop column if exists daily_core_budget_date,
    drop column if exists daily_core_budget_used;

-- 6) Systemwerte des alten Feeds
delete from public.system_settings
where setting_key in (
    'feed.lock_duration_minutes',
    'feed.weight_start',
    'feed.weight_training',
    'feed.weight_recall',
    'feed.weight_feynman',
    'feed.weight_test',
    'feed.weight_kompetenzliste',
    'feed.core_gap_very_tight_hours',
    'feed.core_gap_tight_hours',
    'feed.core_gap_normal_hours',
    'feed.core_gap_relaxed_hours',
    'feed.core_gap_very_relaxed_hours',
    'feed.pressure_very_tight_threshold',
    'feed.pressure_tight_threshold',
    'feed.pressure_relaxed_threshold',
    'feed.pressure_very_relaxed_threshold'
);

notify pgrst, 'reload schema';
