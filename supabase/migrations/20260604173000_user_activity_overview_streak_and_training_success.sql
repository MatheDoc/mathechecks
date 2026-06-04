create or replace function public.get_user_activity_overview()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    overview jsonb;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

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
        select
            coalesce((details ->> 'correctCount')::integer, 0) as correct_count,
            coalesce((details ->> 'totalCount')::integer, 0) as total_count
        from base
        where activity_type = 'training'
          and jsonb_typeof(details) = 'object'
          and details ? 'correctCount'
          and details ? 'totalCount'
          and coalesce((details ->> 'solutionsShown')::boolean, false) = false
    ),
    training_summary as (
        select
            count(*)::integer as scored_task_count,
            coalesce(sum(correct_count), 0)::integer as correct_answer_count,
            coalesce(sum(total_count), 0)::integer as total_answer_count
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
            'rate', case
                when coalesce(training_summary.total_answer_count, 0) > 0 then round(training_summary.correct_answer_count::numeric * 100 / training_summary.total_answer_count, 1)
                else null
            end,
            'scoredTaskCount', coalesce(training_summary.scored_task_count, 0),
            'correctAnswerCount', coalesce(training_summary.correct_answer_count, 0),
            'totalAnswerCount', coalesce(training_summary.total_answer_count, 0)
        ),
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
                'scoredTaskCount', 0,
                'correctAnswerCount', 0,
                'totalAnswerCount', 0
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
