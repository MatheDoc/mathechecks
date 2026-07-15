-- Wiederholungsbadge fuer Training- und Recall-Quoten.
-- Die Fälligkeit wird unabhängig vom Feed direkt aus abgeschlossenen Activity-Events
-- berechnet: nach dem k-ten Abschluss ist sie k * N Tage nach diesem Abschluss erreicht.

insert into public.system_settings (setting_key, value_integer, value_numeric, description)
values (
    'proficiency.review_base_gap_days',
    7,
    null,
    'Basisabstand N in Tagen für Wiederholungsbadges der Erfolgsquoten; weitere abgeschlossene Durchgänge wachsen linear als N, 2N, 3N, ...'
)
on conflict (setting_key) do nothing;

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
    v_review_base_gap_days integer := greatest(public.get_system_setting_integer('proficiency.review_base_gap_days', 7), 1);
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
    completion_history as (
        select
            check_id,
            max(created_at) as last_completed_at,
            count(*)::integer as completed_attempt_count
        from scored
        group by check_id
    ),
    check_quotes as (
        select
            windowed.check_id,
            max(windowed.lernbereich_slug) as lernbereich_slug,
            sum(power(v_decay, rn - 1) * task_score)
                / nullif(sum(power(v_decay, rn - 1)), 0) as quote,
            count(*)::integer as window_count,
            max(created_at) as last_trained_at,
            completion_history.last_completed_at,
            coalesce(completion_history.completed_attempt_count, 0) as completed_attempt_count
        from windowed
        left join completion_history using (check_id)
        group by windowed.check_id, completion_history.last_completed_at, completion_history.completed_attempt_count
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
                    'lastTrainedAt', last_trained_at,
                    'lastCompletedAt', last_completed_at,
                    'completedAttemptCount', completed_attempt_count,
                    'reviewDueAt', last_completed_at + make_interval(days => v_review_base_gap_days * completed_attempt_count),
                    'reviewIsDue', last_completed_at + make_interval(days => v_review_base_gap_days * completed_attempt_count) <= now()
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
    v_retry_penalty numeric := public.get_system_setting_numeric('recall_proficiency.retry_penalty', 0.5);
    v_review_base_gap_days integer := greatest(public.get_system_setting_integer('proficiency.review_base_gap_days', 7), 1);
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
            public._compute_recall_task_score(details, v_retry_penalty) as task_score
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
    completion_history as (
        select
            check_id,
            max(created_at) as last_completed_at,
            count(*)::integer as completed_attempt_count
        from scored
        group by check_id
    ),
    check_quotes as (
        select
            windowed.check_id,
            max(windowed.lernbereich_slug) as lernbereich_slug,
            sum(power(v_decay, rn - 1) * task_score)
                / nullif(sum(power(v_decay, rn - 1)), 0) as quote,
            count(*)::integer as window_count,
            max(created_at) as last_recalled_at,
            completion_history.last_completed_at,
            coalesce(completion_history.completed_attempt_count, 0) as completed_attempt_count
        from windowed
        left join completion_history using (check_id)
        group by windowed.check_id, completion_history.last_completed_at, completion_history.completed_attempt_count
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
                    'lastRecalledAt', last_recalled_at,
                    'lastCompletedAt', last_completed_at,
                    'completedAttemptCount', completed_attempt_count,
                    'reviewDueAt', last_completed_at + make_interval(days => v_review_base_gap_days * completed_attempt_count),
                    'reviewIsDue', last_completed_at + make_interval(days => v_review_base_gap_days * completed_attempt_count) <= now()
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