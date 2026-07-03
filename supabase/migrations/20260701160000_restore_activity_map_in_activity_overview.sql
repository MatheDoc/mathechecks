-- Fix: 20260701090000_recall_quote_read_model.sql hat get_user_activity_overview()
-- neu aufgebaut und dabei das Feld 'activityMap' verloren (zuvor wiederhergestellt in
-- 20260609101500_restore_activity_map_in_user_activity_overview.sql). Das Frontend
-- (assets/js/modules/dashboard.js: normalizeActivityMap / getStreakLengthEndingOnDate)
-- liest die Streak-Laenge fuer die Flammen-Anzeige ausschliesslich aus 'activityMap',
-- daher blieb die Streak-Flamme trotz aktivem Streak unbeleuchtet.
--
-- Diese Migration baut get_user_activity_overview() erneut vollstaendig nach
-- (Stand 20260701090000_recall_quote_read_model.sql) und ergaenzt 'activityMap' wieder.
-- Alle anderen Felder (inkl. 'recallProficiency') bleiben unveraendert erhalten.

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
        select
            timezone('Europe/Berlin', now())::date as today_local,
            date_trunc('week', timezone('Europe/Berlin', now()))::date as current_week_start
    ),
    map_window as (
        select
            (current_week_start - interval '11 weeks')::date as start_date,
            (current_week_start + interval '6 days')::date as end_date,
            today_local
        from local_clock
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
    daily_counts as (
        select
            activity_date,
            count(*)::integer as activity_count
        from base
        group by activity_date
    ),
    last_7_days as (
        select
            series.activity_date,
            coalesce(daily_counts.activity_count, 0)::integer as activity_count
        from (
            select generate_series(
                (select today_local from local_clock) - 6,
                (select today_local from local_clock),
                interval '1 day'
            )::date as activity_date
        ) as series
        left join daily_counts
            on daily_counts.activity_date = series.activity_date
        order by series.activity_date
    ),
    activity_map_days as (
        select
            series.activity_date,
            coalesce(daily_counts.activity_count, 0)::integer as activity_count
        from map_window
        cross join lateral (
            select generate_series(
                map_window.start_date,
                map_window.end_date,
                interval '1 day'
            )::date as activity_date
        ) as series
        left join daily_counts
            on daily_counts.activity_date = series.activity_date
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
        ),
        'activityMap', jsonb_build_object(
            'weeks', 12,
            'todayDate', map_window.today_local,
            'startDate', map_window.start_date,
            'endDate', map_window.end_date,
            'days', coalesce(
                (
                    select jsonb_agg(
                        jsonb_build_object(
                            'date', activity_date,
                            'count', activity_count
                        )
                        order by activity_date
                    )
                    from activity_map_days
                ),
                '[]'::jsonb
            )
        )
    )
    into overview
    from summary
    left join longest_streak on true
    left join training_summary on true
    left join map_window on true;

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
            'last7Days', '[]'::jsonb,
            'activityMap', jsonb_build_object(
                'weeks', 12,
                'todayDate', null,
                'startDate', null,
                'endDate', null,
                'days', '[]'::jsonb
            )
        )
    );
end;
$$;
