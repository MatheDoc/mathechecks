-- Stufen: XP pro Stufe steigen bis Stufe xp.level_ramp_levels an und bleiben danach konstant.
--   Schritt von Stufe L zu L+1 = xp.level_step * min(L, xp.level_ramp_levels)
--   Standard: 40, 80, ..., 400 XP; ab Stufe 10 je 400 XP.
-- Da XP je Aktivitaet nicht mit der Stufe wachsen, bleibt so "eine Stufe ~ eine Lernsitzung" planbar.
-- Die XP selbst aendern sich nicht; Stufen koennen durch die Umstellung nur steigen.

update public.system_settings
set value_numeric = 40,
    description = 'XP: Grundschritt; Schritt von Stufe L zu L+1 = level_step * min(L, level_ramp_levels).'
where setting_key = 'xp.level_step';

insert into public.system_settings (setting_key, value_integer, description)
values ('xp.level_ramp_levels', 10, 'XP: Bis zu dieser Stufe wachsen die XP pro Stufe, danach bleiben sie konstant.')
on conflict (setting_key) do nothing;

create or replace function public._xp_level_threshold(
    p_level integer,
    p_step numeric,
    p_ramp integer
)
returns numeric
language sql
immutable
as $$
    select case
        when p_level <= p_ramp + 1 then p_step * p_level * (p_level - 1) / 2
        else p_step * p_ramp * (p_ramp + 1) / 2 + (p_level - 1 - p_ramp) * p_step * p_ramp
    end;
$$;

create or replace function public._xp_level_info(
    p_total numeric,
    p_step numeric,
    p_ramp integer
)
returns jsonb
language plpgsql
immutable
as $$
declare
    v_step numeric := greatest(coalesce(p_step, 40), 1);
    v_ramp integer := greatest(coalesce(p_ramp, 10), 1);
    v_total numeric := greatest(coalesce(p_total, 0), 0);
    v_ramp_end numeric;
    v_level integer;
begin
    v_ramp_end := public._xp_level_threshold(v_ramp + 1, v_step, v_ramp);
    if v_total >= v_ramp_end then
        v_level := v_ramp + 1 + floor((v_total - v_ramp_end) / (v_step * v_ramp))::integer;
    else
        v_level := greatest(1, floor((1 + sqrt(1 + 8 * v_total / v_step)) / 2)::integer);
    end if;

    -- Korrektur moeglicher Rundungsfehler der Wurzel.
    while public._xp_level_threshold(v_level + 1, v_step, v_ramp) <= v_total loop
        v_level := v_level + 1;
    end loop;
    while v_level > 1 and public._xp_level_threshold(v_level, v_step, v_ramp) > v_total loop
        v_level := v_level - 1;
    end loop;

    return jsonb_build_object(
        'level', v_level,
        'levelStartXp', ceil(public._xp_level_threshold(v_level, v_step, v_ramp))::integer,
        'nextLevelXp', ceil(public._xp_level_threshold(v_level + 1, v_step, v_ramp))::integer
    );
end;
$$;

create or replace function public.get_user_xp_summary(
    p_event_id uuid default null
)
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    v_training_penalty numeric := public.get_system_setting_numeric('proficiency.retry_penalty', 0.5);
    v_recall_penalty numeric := public.get_system_setting_numeric('recall_proficiency.retry_penalty', 0.5);
    v_feynman_penalty numeric := public.get_system_setting_numeric('feynman_proficiency.retry_penalty', 0.5);
    v_warmup_penalty numeric := public.get_system_setting_numeric('warmup_proficiency.retry_penalty', 0.5);
    v_first_factor numeric := public.get_system_setting_numeric('xp.first_success_factor', 1.5);
    v_success numeric := public.get_system_setting_numeric('xp.success_threshold', 0.5);
    v_repeat_factor numeric := public.get_system_setting_numeric('xp.repeat_factor', 0.5);
    v_late_factor numeric := public.get_system_setting_numeric('xp.repeat_late_factor', 0.25);
    v_late_after integer := greatest(public.get_system_setting_integer('xp.repeat_late_after', 3), 1);
    v_gap_hours integer := greatest(public.get_system_setting_integer('xp.repeat_gap_hours', 20), 1);
    v_level_step numeric := greatest(public.get_system_setting_numeric('xp.level_step', 40), 1);
    v_level_ramp integer := greatest(public.get_system_setting_integer('xp.level_ramp_levels', 10), 1);
    v_first_award_at timestamptz;
    v_gap interval;
    v_weights jsonb;
    v_total integer := 0;
    v_by_type jsonb := '{}'::jsonb;
    v_event jsonb := null;
    v_level_info jsonb;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    v_gap := make_interval(hours => v_gap_hours);
    v_weights := jsonb_build_object(
        'warmup', public.get_system_setting_numeric('xp.weight.warmup', 40),
        'training', public.get_system_setting_numeric('xp.weight.training', 20),
        'test', public.get_system_setting_numeric('xp.weight.test', 32),
        'recall', public.get_system_setting_numeric('xp.weight.recall', 100),
        'feynman', public.get_system_setting_numeric('xp.weight.feynman', 160)
    );

    select min(award.created_at)
    into v_first_award_at
    from public.user_xp_awards as award
    where award.user_id = current_user_id;

    with scored as (
        select
            activity.id,
            activity.activity_type,
            activity.check_id,
            activity.created_at,
            case
                when activity.activity_type = 'training' then coalesce(activity.details ->> 'taskIndex', '')
                else ''
            end as xp_key,
            greatest(0, least(1, coalesce(case activity.activity_type
                when 'training' then public._compute_training_task_score(activity.details, v_training_penalty)
                when 'recall' then public._compute_recall_task_score(activity.details, v_recall_penalty)
                when 'feynman' then public._compute_feynman_task_score(activity.details, v_feynman_penalty)
                when 'test' then public._compute_test_task_score(activity.details)
                when 'warmup' then public._compute_warmup_score(activity.details, v_warmup_penalty)
            end, 0))) as score
        from public.user_activity_events as activity
        where activity.user_id = current_user_id
          and activity.check_id is not null
          and activity.activity_type in ('warmup', 'training', 'test', 'recall', 'feynman')
          and (
              activity.activity_type in ('recall', 'feynman')
              or v_first_award_at is null
              or activity.created_at < v_first_award_at
          )
    ),
    flagged as (
        select scored.*, (scored.score >= v_success)::integer as success_flag
        from scored
    ),
    counted as (
        select
            flagged.*,
            coalesce(sum(flagged.success_flag) over (
                partition by flagged.activity_type, flagged.check_id, flagged.xp_key
                order by flagged.created_at, flagged.id
                rows between unbounded preceding and 1 preceding
            ), 0) as prior_successes,
            coalesce(sum(flagged.success_flag) over (
                partition by flagged.activity_type, flagged.check_id, flagged.xp_key
                order by flagged.created_at
                range between v_gap preceding and current row
            ), 0) - flagged.success_flag as recent_successes
        from flagged
    ),
    classified as (
        select
            counted.*,
            case
                when counted.prior_successes = 0 then 'first'
                when counted.recent_successes = 0 then 'spaced'
                when counted.recent_successes < v_late_after then 'repeat'
                else 'repeat_late'
            end as factor_kind
        from counted
    ),
    xp_events as (
        select
            classified.id,
            classified.activity_type,
            classified.score,
            classified.factor_kind,
            case classified.factor_kind
                when 'first' then v_first_factor
                when 'spaced' then 1
                when 'repeat' then v_repeat_factor
                else v_late_factor
            end as factor,
            round(
                coalesce((v_weights ->> classified.activity_type)::numeric, 0)
                * classified.score
                * case classified.factor_kind
                    when 'first' then v_first_factor
                    when 'spaced' then 1
                    when 'repeat' then v_repeat_factor
                    else v_late_factor
                end
            )::integer as xp
        from classified
    ),
    xp_all as (
        select xp_events.activity_type, xp_events.xp from xp_events
        union all
        select award.activity_type, award.xp
        from public.user_xp_awards as award
        where award.user_id = current_user_id
    )
    select
        coalesce((select sum(xp_all.xp) from xp_all), 0)::integer,
        coalesce((
            select jsonb_object_agg(by_type.activity_type, by_type.type_xp)
            from (
                select xp_all.activity_type, sum(xp_all.xp)::integer as type_xp
                from xp_all
                group by xp_all.activity_type
            ) as by_type
        ), '{}'::jsonb),
        (
            select jsonb_build_object(
                'id', xp_events.id,
                'activityType', xp_events.activity_type,
                'xp', xp_events.xp,
                'score', round(xp_events.score, 3),
                'factor', xp_events.factor,
                'factorKind', xp_events.factor_kind
            )
            from xp_events
            where p_event_id is not null and xp_events.id = p_event_id
        )
    into v_total, v_by_type, v_event;

    v_level_info := public._xp_level_info(v_total, v_level_step, v_level_ramp);

    return jsonb_build_object(
        'totalXp', v_total,
        'level', v_level_info -> 'level',
        'levelStartXp', v_level_info -> 'levelStartXp',
        'nextLevelXp', v_level_info -> 'nextLevelXp',
        'byType', v_by_type,
        'event', v_event,
        'rules', jsonb_build_object(
            'weights', jsonb_build_object(
                'feynman', v_weights -> 'feynman',
                'recall', v_weights -> 'recall',
                'training', public.get_system_setting_numeric('xp.unit_weight.training', 8),
                'test', public.get_system_setting_numeric('xp.unit_weight.test', 4),
                'warmup', public.get_system_setting_numeric('xp.unit_weight.warmup', 4)
            ),
            'firstSuccessFactor', v_first_factor,
            'repeatGapHours', v_gap_hours,
            'repeatFactor', v_repeat_factor,
            'repeatLateAfter', v_late_after,
            'repeatLateFactor', v_late_factor
        )
    );
end;
$$;
