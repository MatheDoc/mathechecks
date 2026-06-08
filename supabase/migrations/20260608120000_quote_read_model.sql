-- Quoten-Read-Model: Trefferquote als Kompetenzinstrument
-- Kanonische Spezifikation: .github/quoten.md
--
-- Diese Migration ist additiv/idempotent:
--   * legt die proficiency.*-Parameter in system_settings an (ohne bestehende Werte zu ueberschreiben)
--   * fuegt eine Task-Score-Hilfsfunktion hinzu (neues Rohschema + Legacy-Fallback)
--   * fuegt die user-scoped Check-Quoten-Projektion get_user_check_proficiency() hinzu
--   * baut get_user_activity_overview() auf das neue Quotenmodell um

-- 1) Zentrale Stellschrauben ------------------------------------------------

insert into public.system_settings (setting_key, value_integer, description)
values
    ('proficiency.window_size', 3, 'Quoten: Anzahl der juengsten Taskscores je Check im Recency-Fenster (N).')
on conflict (setting_key) do nothing;

insert into public.system_settings (setting_key, value_numeric, description)
values
    ('proficiency.recency_decay', 0.5, 'Quoten: Recency-Decay d je Position im Fenster (juengere Taskscores zaehlen staerker).'),
    ('proficiency.retry_penalty', 0.5, 'Quoten: Versuchsabzug p je zusaetzlichem Versuch einer Frage.')
on conflict (setting_key) do nothing;

-- 2) Task-Score aus einem einzelnen Trainings-Event -------------------------
--
-- Neues Rohschema in details:
--   checkable_count   : Anzahl pruefbarer Fragen
--   question_attempts : Array der Versuchszahlen n je beantworteter Frage
--   revealed_count    : Anzahl aufgeloester Fragen (Fragescore 0)
-- Fragescore beantwortet: max(0, 1 - (n - 1) * p); aufgeloest: 0.
-- Taskscore: Summe der Fragescores / checkable_count.
--
-- Legacy-Fallback (Alt-Events): correctCount/totalCount mit globalem
-- solutionsShown-Gate (solutionsShown = true => ungewertet => null).

create or replace function public._compute_training_task_score(
    p_details jsonb,
    p_retry_penalty numeric
)
returns numeric
language plpgsql
immutable
as $$
declare
    v_answered_sum numeric := 0;
    v_answered_count integer := 0;
    v_revealed_count integer := 0;
    v_checkable integer;
    v_n numeric;
    v_elem jsonb;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    -- Neues Rohschema
    if (p_details ? 'question_attempts')
        or (p_details ? 'revealed_count')
        or (p_details ? 'checkable_count') then

        if jsonb_typeof(p_details -> 'question_attempts') = 'array' then
            for v_elem in
                select value from jsonb_array_elements(p_details -> 'question_attempts') as t(value)
            loop
                v_n := greatest(coalesce(nullif(v_elem #>> '{}', '')::numeric, 1), 1);
                v_answered_sum := v_answered_sum
                    + greatest(0, 1 - (v_n - 1) * coalesce(p_retry_penalty, 0.5));
                v_answered_count := v_answered_count + 1;
            end loop;
        end if;

        v_revealed_count := greatest(coalesce((p_details ->> 'revealed_count')::integer, 0), 0);
        v_checkable := coalesce((p_details ->> 'checkable_count')::integer, v_answered_count + v_revealed_count);

        if v_checkable > 0 then
            return v_answered_sum / v_checkable;
        end if;
        return null;
    end if;

    -- Legacy-Fallback
    if (p_details ? 'correctCount') and (p_details ? 'totalCount') then
        if coalesce((p_details ->> 'solutionsShown')::boolean, false) then
            return null;
        end if;
        if coalesce((p_details ->> 'totalCount')::integer, 0) > 0 then
            return (p_details ->> 'correctCount')::numeric / (p_details ->> 'totalCount')::numeric;
        end if;
        return null;
    end if;

    return null;
end;
$$;

-- 3) Check-Quoten-Projektion (Read-Model) -----------------------------------
--
-- Genau eine user-scoped Quote je check_id (recency-gewichtetes Mittel der
-- letzten N Taskscores). Lernbereichs- und Gesamtquote sind Kompositionen
-- ueber dieselbe Check-Quote.

create or replace function public.get_user_check_proficiency()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    v_window integer := greatest(public.get_system_setting_integer('proficiency.window_size', 3), 1);
    v_decay numeric := public.get_system_setting_numeric('proficiency.recency_decay', 0.5);
    v_penalty numeric := public.get_system_setting_numeric('proficiency.retry_penalty', 0.5);
    result jsonb;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    with scored as (
        select
            check_id,
            lernbereich_slug,
            created_at,
            public._compute_training_task_score(details, v_penalty) as task_score
        from public.user_activity_events
        where user_id = current_user_id
          and activity_type = 'training'
          and check_id is not null
    ),
    filtered as (
        select * from scored where task_score is not null
    ),
    ranked as (
        select
            check_id,
            lernbereich_slug,
            created_at,
            task_score,
            row_number() over (partition by check_id order by created_at desc) as rn
        from filtered
    ),
    windowed as (
        select * from ranked where rn <= v_window
    ),
    check_quotes as (
        select
            check_id,
            max(lernbereich_slug) as lernbereich_slug,
            sum(power(v_decay, rn - 1) * task_score)
                / nullif(sum(power(v_decay, rn - 1)), 0) as quote,
            count(*)::integer as window_count,
            max(created_at) as last_trained_at
        from windowed
        group by check_id
    )
    select jsonb_build_object(
        'overall', (
            select jsonb_build_object(
                'rate', case when count(*) > 0 then round(avg(quote) * 100, 1) else null end,
                'checkCount', count(*)::integer
            )
            from check_quotes
        ),
        'checks', coalesce((
            select jsonb_agg(
                jsonb_build_object(
                    'checkId', check_id,
                    'lernbereichSlug', lernbereich_slug,
                    'rate', round(quote * 100, 1),
                    'windowCount', window_count,
                    'lastTrainedAt', last_trained_at
                )
                order by quote asc, last_trained_at desc
            )
            from check_quotes
        ), '[]'::jsonb),
        'byLernbereich', coalesce((
            select jsonb_object_agg(lernbereich_slug, lb_obj)
            from (
                select
                    lernbereich_slug,
                    jsonb_build_object(
                        'rate', round(avg(quote) * 100, 1),
                        'checkCount', count(*)::integer
                    ) as lb_obj
                from check_quotes
                where lernbereich_slug is not null
                group by lernbereich_slug
            ) as lb
        ), '{}'::jsonb)
    )
    into result;

    return coalesce(result, jsonb_build_object(
        'overall', jsonb_build_object('rate', null, 'checkCount', 0),
        'checks', '[]'::jsonb,
        'byLernbereich', '{}'::jsonb
    ));
end;
$$;

revoke all on function public.get_user_check_proficiency() from public;
revoke all on function public.get_user_check_proficiency() from anon;
grant execute on function public.get_user_check_proficiency() to authenticated;

-- 4) Aktivitaetsuebersicht auf das neue Quotenmodell umbauen ----------------

create or replace function public.get_user_activity_overview()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    v_penalty numeric := public.get_system_setting_numeric('proficiency.retry_penalty', 0.5);
    v_proficiency jsonb;
    overview jsonb;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    v_proficiency := public.get_user_check_proficiency();

    with local_clock as (
        select timezone('Europe/Berlin', now())::date as today_local
    ),
    base as (
        select
            activity_type,
            timezone('Europe/Berlin', created_at)::date as activity_date,
            created_at,
            details
        from public.user_activity_events
        where user_id = current_user_id
    ),
    summary as (
        select
            count(*)::integer as total_count,
            count(distinct activity_date)::integer as active_days,
            min(activity_date) as first_activity_date,
            max(activity_date) as last_activity_date
        from base
    ),
    distinct_activity_days as (
        select distinct activity_date
        from base
        where activity_date is not null
    ),
    streak_groups as (
        select
            activity_date,
            activity_date - (row_number() over (order by activity_date))::integer as streak_group
        from distinct_activity_days
    ),
    longest_streak as (
        select
            count(*)::integer as streak_length,
            min(activity_date) as start_date,
            max(activity_date) as end_date
        from streak_groups
        group by streak_group
        order by streak_length desc, end_date desc
        limit 1
    ),
    counts_by_type as (
        select
            activity_type,
            count(*)::integer as activity_count
        from base
        group by activity_type
    ),
    training_scored as (
        select public._compute_training_task_score(details, v_penalty) as task_score
        from base
        where activity_type = 'training'
    ),
    training_summary as (
        select count(*) filter (where task_score is not null)::integer as scored_task_count
        from training_scored
    ),
    last_7_days as (
        select
            series.activity_date,
            coalesce(count(base.activity_date), 0)::integer as activity_count
        from (
            select generate_series(
                (select today_local from local_clock) - 6,
                (select today_local from local_clock),
                interval '1 day'
            )::date as activity_date
        ) as series
        left join base
            on base.activity_date = series.activity_date
        group by series.activity_date
        order by series.activity_date
    )
    select jsonb_build_object(
        'totalCount', coalesce(summary.total_count, 0),
        'activeDays', coalesce(summary.active_days, 0),
        'firstActivityDate', summary.first_activity_date,
        'lastActivityDate', summary.last_activity_date,
        'averagePerActiveDay', case
            when coalesce(summary.active_days, 0) > 0 then round(summary.total_count::numeric / summary.active_days, 1)
            else 0
        end,
        'longestStreak', jsonb_build_object(
            'length', coalesce(longest_streak.streak_length, 0),
            'startDate', longest_streak.start_date,
            'endDate', longest_streak.end_date
        ),
        'trainingSuccess', jsonb_build_object(
            'rate', v_proficiency -> 'overall' -> 'rate',
            'checkCount', coalesce((v_proficiency -> 'overall' ->> 'checkCount')::integer, 0),
            'scoredTaskCount', coalesce(training_summary.scored_task_count, 0)
        ),
        'proficiency', v_proficiency,
        'byType', jsonb_build_object(
            'training', coalesce((select activity_count from counts_by_type where activity_type = 'training'), 0),
            'recall', coalesce((select activity_count from counts_by_type where activity_type = 'recall'), 0),
            'feynman', coalesce((select activity_count from counts_by_type where activity_type = 'feynman'), 0),
            'flashcards', coalesce((select activity_count from counts_by_type where activity_type = 'flashcards'), 0)
        ),
        'last7Days', coalesce(
            (
                select jsonb_agg(
                    jsonb_build_object(
                        'date', activity_date,
                        'count', activity_count
                    )
                    order by activity_date
                )
                from last_7_days
            ),
            '[]'::jsonb
        )
    )
    into overview
    from summary
    left join longest_streak on true
    left join training_summary on true;

    return coalesce(
        overview,
        jsonb_build_object(
            'totalCount', 0,
            'activeDays', 0,
            'firstActivityDate', null,
            'lastActivityDate', null,
            'averagePerActiveDay', 0,
            'longestStreak', jsonb_build_object(
                'length', 0,
                'startDate', null,
                'endDate', null
            ),
            'trainingSuccess', jsonb_build_object(
                'rate', null,
                'checkCount', 0,
                'scoredTaskCount', 0
            ),
            'proficiency', jsonb_build_object(
                'overall', jsonb_build_object('rate', null, 'checkCount', 0),
                'checks', '[]'::jsonb,
                'byLernbereich', '{}'::jsonb
            ),
            'byType', jsonb_build_object(
                'training', 0,
                'recall', 0,
                'feynman', 0,
                'flashcards', 0
            ),
            'last7Days', '[]'::jsonb
        )
    );
end;
$$;
