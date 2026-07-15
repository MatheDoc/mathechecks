-- Wiederholungslevel wachsen nur durch zeitlich getrennte Wiederholungen.
-- Mehrere Abschlüsse vor derselben Fälligkeit verschieben den Abstand, erhöhen
-- ihn aber nicht: N, 2N, 3N, ... wird erst nach einer fälligen Wiederholung erreicht.

create or replace function public.get_user_activity_review_schedule(
    p_activity_type text,
    p_base_gap_days integer
)
returns table (
    check_id text,
    last_completed_at timestamptz,
    review_level integer,
    review_due_at timestamptz
)
language sql
security definer
set search_path = public
as $$
    with recursive events as (
        select
            activity.check_id,
            activity.created_at,
            activity.id,
            row_number() over (
                partition by activity.check_id
                order by activity.created_at, activity.id
            ) as event_number
        from public.user_activity_events as activity
        where activity.user_id = auth.uid()
          and activity.activity_type = p_activity_type
          and activity.check_id is not null
    ),
    review_chain as (
        select
            events.check_id,
            events.created_at as last_completed_at,
            events.event_number,
            1::integer as review_level,
            events.created_at + make_interval(days => greatest(p_base_gap_days, 1)) as review_due_at
        from events
        where events.event_number = 1

        union all

        select
            events.check_id,
            events.created_at as last_completed_at,
            events.event_number,
            case
                when events.created_at >= review_chain.review_due_at then review_chain.review_level + 1
                else review_chain.review_level
            end as review_level,
            events.created_at + make_interval(
                days => greatest(p_base_gap_days, 1) * case
                    when events.created_at >= review_chain.review_due_at then review_chain.review_level + 1
                    else review_chain.review_level
                end
            ) as review_due_at
        from review_chain
        join events
          on events.check_id = review_chain.check_id
         and events.event_number = review_chain.event_number + 1
    )
    select distinct on (review_chain.check_id)
        review_chain.check_id,
        review_chain.last_completed_at,
        review_chain.review_level,
        review_chain.review_due_at
    from review_chain
    order by review_chain.check_id, review_chain.event_number desc;
$$;

revoke all on function public.get_user_activity_review_schedule(text, integer) from public;
revoke all on function public.get_user_activity_review_schedule(text, integer) from anon;
grant execute on function public.get_user_activity_review_schedule(text, integer) to authenticated;

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
    if current_user_id is null then raise exception 'Authentication required'; end if;
    with scored as (
        select check_id, lernbereich_slug, created_at,
            public._compute_training_task_score(details, v_penalty) as task_score
        from public.user_activity_events
        where user_id = current_user_id and activity_type = 'training' and check_id is not null
    ), filtered as (
        select * from scored where task_score is not null
    ), ranked as (
        select check_id, lernbereich_slug, created_at, task_score,
            row_number() over (partition by check_id order by created_at desc) as rn
        from filtered
    ), windowed as (
        select * from ranked where rn <= v_window
    ), review_schedule as (
        select * from public.get_user_activity_review_schedule('training', v_review_base_gap_days)
    ), check_quotes as (
        select windowed.check_id, max(windowed.lernbereich_slug) as lernbereich_slug,
            sum(power(v_decay, rn - 1) * task_score) / nullif(sum(power(v_decay, rn - 1)), 0) as quote,
            count(*)::integer as window_count, max(created_at) as last_trained_at,
            review_schedule.last_completed_at, review_schedule.review_level, review_schedule.review_due_at
        from windowed left join review_schedule using (check_id)
        group by windowed.check_id, review_schedule.last_completed_at, review_schedule.review_level, review_schedule.review_due_at
    )
    select jsonb_build_object(
        'overall', (select jsonb_build_object('rate', case when count(*) > 0 then round(avg(quote) * 100, 1) else null end, 'checkCount', count(*)::integer) from check_quotes),
        'checks', coalesce((select jsonb_agg(jsonb_build_object(
            'checkId', check_id, 'lernbereichSlug', lernbereich_slug, 'rate', round(quote * 100, 1),
            'windowCount', window_count, 'lastTrainedAt', last_trained_at,
            'lastCompletedAt', last_completed_at, 'reviewLevel', review_level,
            'reviewDueAt', review_due_at, 'reviewIsDue', review_due_at <= now()
        ) order by quote asc, last_trained_at desc) from check_quotes), '[]'::jsonb),
        'byLernbereich', coalesce((select jsonb_object_agg(lernbereich_slug, lb_obj) from (
            select lernbereich_slug, jsonb_build_object('rate', round(avg(quote) * 100, 1), 'checkCount', count(*)::integer) as lb_obj
            from check_quotes where lernbereich_slug is not null group by lernbereich_slug
        ) as lb), '{}'::jsonb)
    ) into result;
    return coalesce(result, jsonb_build_object('overall', jsonb_build_object('rate', null, 'checkCount', 0), 'checks', '[]'::jsonb, 'byLernbereich', '{}'::jsonb));
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
    if current_user_id is null then raise exception 'Authentication required'; end if;
    with scored as (
        select check_id, lernbereich_slug, created_at,
            public._compute_recall_task_score(details, v_retry_penalty) as task_score
        from public.user_activity_events
        where user_id = current_user_id and activity_type = 'recall' and check_id is not null
    ), filtered as (
        select * from scored where task_score is not null
    ), ranked as (
        select check_id, lernbereich_slug, created_at, task_score,
            row_number() over (partition by check_id order by created_at desc) as rn
        from filtered
    ), windowed as (
        select * from ranked where rn <= v_window
    ), review_schedule as (
        select * from public.get_user_activity_review_schedule('recall', v_review_base_gap_days)
    ), check_quotes as (
        select windowed.check_id, max(windowed.lernbereich_slug) as lernbereich_slug,
            sum(power(v_decay, rn - 1) * task_score) / nullif(sum(power(v_decay, rn - 1)), 0) as quote,
            count(*)::integer as window_count, max(created_at) as last_recalled_at,
            review_schedule.last_completed_at, review_schedule.review_level, review_schedule.review_due_at
        from windowed left join review_schedule using (check_id)
        group by windowed.check_id, review_schedule.last_completed_at, review_schedule.review_level, review_schedule.review_due_at
    )
    select jsonb_build_object(
        'overall', (select jsonb_build_object('rate', case when count(*) > 0 then round(avg(quote) * 100, 1) else null end, 'checkCount', count(*)::integer) from check_quotes),
        'checks', coalesce((select jsonb_agg(jsonb_build_object(
            'checkId', check_id, 'lernbereichSlug', lernbereich_slug, 'rate', round(quote * 100, 1),
            'windowCount', window_count, 'lastRecalledAt', last_recalled_at,
            'lastCompletedAt', last_completed_at, 'reviewLevel', review_level,
            'reviewDueAt', review_due_at, 'reviewIsDue', review_due_at <= now()
        ) order by quote asc, last_recalled_at desc) from check_quotes), '[]'::jsonb),
        'byLernbereich', coalesce((select jsonb_object_agg(lernbereich_slug, lb_obj) from (
            select lernbereich_slug, jsonb_build_object('rate', round(avg(quote) * 100, 1), 'checkCount', count(*)::integer) as lb_obj
            from check_quotes where lernbereich_slug is not null group by lernbereich_slug
        ) as lb), '{}'::jsonb)
    ) into result;
    return coalesce(result, jsonb_build_object('overall', jsonb_build_object('rate', null, 'checkCount', 0), 'checks', '[]'::jsonb, 'byLernbereich', '{}'::jsonb));
end;
$$;
