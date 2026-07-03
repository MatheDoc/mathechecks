-- Recall-Quote-Read-Model: eigenstaendige, zur Trainings-Quote parallele Projektion.
-- Kanonische Spezifikation: .github/quoten.md (Abschnitt "Recall-Quote").
--
-- Bewusst getrennt vom Trainings-Quotenmodell (public._compute_training_task_score /
-- public.get_user_check_proficiency): recall/feynman bleiben ausserhalb der
-- Trainings-Quote (siehe quoten.md). Diese Migration ist additiv/idempotent.

-- 1) Eigene Stellschrauben (unabhaengig von proficiency.*) ------------------

insert into public.system_settings (setting_key, value_integer, description)
values
    ('recall_proficiency.window_size', 3, 'Recall-Quote: Anzahl der juengsten Recall-Taskscores je Check im Recency-Fenster (N).')
on conflict (setting_key) do nothing;

insert into public.system_settings (setting_key, value_numeric, description)
values
    ('recall_proficiency.recency_decay', 0.5, 'Recall-Quote: Recency-Decay d je Position im Fenster (juengere Taskscores zaehlen staerker).')
on conflict (setting_key) do nothing;

-- 2) Task-Score aus einem einzelnen Recall-Event -----------------------------
--
-- Rohschema in details (geschrieben von record_user_activity('recall', ...)
-- nach Abschluss des Selbstchecks):
--   itemScores : jsonb-Array der finalen KI-/Retry-Scores (0..1) je Cue/Response-Item
-- Taskscore: Mittel der itemScores. Events ohne dieses Feld (z.B. das fruehere,
-- rein diagnostische "self_check_start"-Tracking) liefern null und zaehlen nicht.

create or replace function public._compute_recall_task_score(
    p_details jsonb
)
returns numeric
language plpgsql
immutable
as $$
declare
    v_sum numeric := 0;
    v_count integer := 0;
    v_elem jsonb;
    v_score numeric;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    if jsonb_typeof(p_details -> 'itemScores') <> 'array' then
        return null;
    end if;

    for v_elem in
        select value from jsonb_array_elements(p_details -> 'itemScores') as t(value)
    loop
        v_score := nullif(v_elem #>> '{}', '')::numeric;
        if v_score is not null then
            v_sum := v_sum + greatest(0, least(1, v_score));
            v_count := v_count + 1;
        end if;
    end loop;

    if v_count = 0 then
        return null;
    end if;

    return v_sum / v_count;
end;
$$;

-- 3) Check-Recall-Quoten-Projektion (Read-Model) -----------------------------

create or replace function public.get_user_recall_proficiency()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    v_window integer := greatest(public.get_system_setting_integer('recall_proficiency.window_size', 3), 1);
    v_decay numeric := public.get_system_setting_numeric('recall_proficiency.recency_decay', 0.5);
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
            public._compute_recall_task_score(details) as task_score
        from public.user_activity_events
        where user_id = current_user_id
          and activity_type = 'recall'
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
            max(created_at) as last_recalled_at
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
                    'lastRecalledAt', last_recalled_at
                )
                order by quote asc, last_recalled_at desc
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

revoke all on function public.get_user_recall_proficiency() from public;
revoke all on function public.get_user_recall_proficiency() from anon;
grant execute on function public.get_user_recall_proficiency() to authenticated;

-- 4) Aktivitaetsuebersicht um recallProficiency ergaenzen --------------------
-- Vollstaendiger Nachbau von get_user_activity_overview() (Stand
-- 20260608120000_quote_read_model.sql) plus zusaetzlichem Feld 'recallProficiency'.
-- Alle bisherigen Felder bleiben unveraendert erhalten.

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
    v_recall_proficiency jsonb;
    overview jsonb;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    v_proficiency := public.get_user_check_proficiency();
    v_recall_proficiency := public.get_user_recall_proficiency();

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
        'recallProficiency', v_recall_proficiency,
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
            'recallProficiency', jsonb_build_object(
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
