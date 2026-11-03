-- Recall und Feynman: XP sofort nach jeder KI-Auswertung statt erst beim gespeicherten Abschluss.
--
-- Einheit = Item eines Durchgangs, unit_key "r<Durchgang>:i<Item>". Der Client meldet den aktuellen
-- Beitrag des Items (Erstscore + Anteil der Verbesserung, wie in der Quote) und die Item-Anzahl;
-- vergeben wird nur der Zuwachs gegenueber dem bisher gemeldeten Beitrag:
--   XP = round(xp.weight.<Typ> / Itemanzahl * Zuwachs * Faktor)
-- Der Wiederholungsfaktor gilt je Durchgang (alle Items teilen ihn) und richtet sich nach frueheren
-- Durchgaengen desselben Checks.
-- Abschluss-Ereignisse zaehlen je Typ nur noch vor der ersten Einzelvergabe dieses Typs (Altbestand).

alter table public.user_xp_awards
    drop constraint if exists user_xp_awards_activity_type_check;

alter table public.user_xp_awards
    add constraint user_xp_awards_activity_type_check
    check (activity_type in ('training', 'test', 'warmup', 'recall', 'feynman'));

alter table public.user_xp_awards
    add column if not exists factor_kind text null;

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
          -- Ab der ersten Einzelvergabe eines Typs zaehlen dessen Abschluesse nicht mehr (sonst doppelt).
          and not exists (
              select 1
              from public.user_xp_awards as award
              where award.user_id = current_user_id
                and award.activity_type = activity.activity_type
                and award.created_at <= activity.created_at
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

create or replace function public.award_xp(
    p_activity_type text,
    p_check_id text,
    p_units jsonb,
    p_lernbereich_slug text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    v_type text := lower(coalesce(nullif(trim(p_activity_type), ''), ''));
    v_check_id text := nullif(trim(p_check_id), '');
    v_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    v_first_factor numeric := public.get_system_setting_numeric('xp.first_success_factor', 1.5);
    v_repeat_factor numeric := public.get_system_setting_numeric('xp.repeat_factor', 0.5);
    v_late_factor numeric := public.get_system_setting_numeric('xp.repeat_late_factor', 0.25);
    v_late_after integer := greatest(public.get_system_setting_integer('xp.repeat_late_after', 3), 1);
    v_gap interval := make_interval(hours => greatest(public.get_system_setting_integer('xp.repeat_gap_hours', 20), 1));
    v_weight numeric;
    v_penalty numeric;
    v_unit jsonb;
    v_key text;
    v_attempts integer;
    v_score numeric;
    v_prior integer;
    v_recent integer;
    v_kind text;
    v_factor numeric;
    v_xp integer;
    v_gained integer := 0;
    v_count integer := 0;
    v_kinds text[] := array[]::text[];
    v_factors numeric[] := array[]::numeric[];
    v_summary jsonb;
    v_run_based boolean;
    v_run text;
    v_item_count integer;
    v_previous numeric;
    v_delta numeric;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if v_type not in ('training', 'test', 'warmup', 'recall', 'feynman') then
        raise exception 'Unsupported activity type';
    end if;
    v_run_based := v_type in ('recall', 'feynman');

    if v_check_id is null then
        raise exception 'check_id required';
    end if;

    if jsonb_typeof(p_units) is distinct from 'array'
        or jsonb_array_length(p_units) = 0
        or jsonb_array_length(p_units) > 50 then
        raise exception 'units must be a non-empty array';
    end if;

    v_weight := case
        when v_run_based then public.get_system_setting_numeric(
            'xp.weight.' || v_type,
            case v_type when 'feynman' then 160 else 100 end
        )
        else public.get_system_setting_numeric(
            'xp.unit_weight.' || v_type,
            case v_type when 'training' then 8 else 4 end
        )
    end;
    v_penalty := case v_type
        when 'training' then public.get_system_setting_numeric('proficiency.retry_penalty', 0.5)
        when 'warmup' then public.get_system_setting_numeric('warmup_proficiency.retry_penalty', 0.5)
        else 0
    end;

    for v_unit in
        select value from jsonb_array_elements(p_units) as units(value)
    loop
        if jsonb_typeof(v_unit) is distinct from 'object' then
            continue;
        end if;
        v_key := nullif(trim(v_unit ->> 'key'), '');
        if v_key is null or char_length(v_key) > 120 then
            continue;
        end if;

        if v_run_based then
            -- Recall/Feynman: Beitrag des Items kommt vom Client (KI-Score), vergeben wird der Zuwachs.
            if jsonb_typeof(v_unit -> 'score') is distinct from 'number' then
                continue;
            end if;
            v_attempts := 1;
            v_score := greatest(0, least(1, (v_unit ->> 'score')::numeric));
            v_item_count := case
                when jsonb_typeof(v_unit -> 'itemCount') = 'number'
                    then greatest(1, least(50, floor((v_unit ->> 'itemCount')::numeric)::integer))
                else 1
            end;
            v_run := split_part(v_key, ':', 1);

            select max(award.score)
            into v_previous
            from public.user_xp_awards as award
            where award.user_id = current_user_id
              and award.activity_type = v_type
              and award.check_id = v_check_id
              and award.unit_key = v_key;
            v_delta := v_score - coalesce(v_previous, 0);
            if v_delta <= 0 then
                continue;
            end if;

            -- Alle Items eines Durchgangs teilen den Faktor der ersten Vergabe dieses Durchgangs.
            select award.factor, award.factor_kind
            into v_factor, v_kind
            from public.user_xp_awards as award
            where award.user_id = current_user_id
              and award.activity_type = v_type
              and award.check_id = v_check_id
              and split_part(award.unit_key, ':', 1) = v_run
            order by award.created_at
            limit 1;

            if v_factor is null then
                select
                    count(*)::integer,
                    count(distinct split_part(award.unit_key, ':', 1))
                        filter (where award.created_at > now() - v_gap)::integer
                into v_prior, v_recent
                from public.user_xp_awards as award
                where award.user_id = current_user_id
                  and award.activity_type = v_type
                  and award.check_id = v_check_id;

                v_kind := case
                    when v_prior = 0 then 'first'
                    when v_recent = 0 then 'spaced'
                    when v_recent < v_late_after then 'repeat'
                    else 'repeat_late'
                end;
                v_factor := case v_kind
                    when 'first' then v_first_factor
                    when 'spaced' then 1
                    when 'repeat' then v_repeat_factor
                    else v_late_factor
                end;
            end if;

            v_xp := greatest(0, round(v_weight / v_item_count * v_delta * v_factor))::integer;

            insert into public.user_xp_awards (
                user_id, activity_type, lernbereich_slug, check_id, unit_key, attempts, score, factor, factor_kind, xp
            )
            values (
                current_user_id, v_type, v_lernbereich_slug, v_check_id, v_key, 1, v_score, v_factor, v_kind, v_xp
            );

            v_gained := v_gained + v_xp;
            v_count := v_count + 1;
            v_kinds := array_append(v_kinds, v_kind);
            v_factors := array_append(v_factors, v_factor);
            v_factor := null;
            v_kind := null;
            continue;
        end if;

        v_attempts := case
            when v_type = 'test' then 1
            when jsonb_typeof(v_unit -> 'attempts') = 'number'
                then greatest(1, least(100, floor((v_unit ->> 'attempts')::numeric)::integer))
            else 1
        end;
        v_score := greatest(0, 1 - (v_attempts - 1) * coalesce(v_penalty, 0.5));
        if v_score <= 0 then
            continue;
        end if;

        select
            count(*)::integer,
            count(*) filter (where award.created_at > now() - v_gap)::integer
        into v_prior, v_recent
        from public.user_xp_awards as award
        where award.user_id = current_user_id
          and award.activity_type = v_type
          and award.check_id = v_check_id
          and award.unit_key = v_key;

        v_kind := case
            when v_prior = 0 then 'first'
            when v_recent = 0 then 'spaced'
            when v_recent < v_late_after then 'repeat'
            else 'repeat_late'
        end;
        v_factor := case v_kind
            when 'first' then v_first_factor
            when 'spaced' then 1
            when 'repeat' then v_repeat_factor
            else v_late_factor
        end;
        v_xp := greatest(0, round(v_weight * v_score * v_factor))::integer;

        insert into public.user_xp_awards (
            user_id, activity_type, lernbereich_slug, check_id, unit_key, attempts, score, factor, factor_kind, xp
        )
        values (
            current_user_id, v_type, v_lernbereich_slug, v_check_id, v_key, v_attempts, v_score, v_factor, v_kind, v_xp
        );

        v_gained := v_gained + v_xp;
        v_count := v_count + 1;
        v_kinds := array_append(v_kinds, v_kind);
        v_factors := array_append(v_factors, v_factor);
    end loop;

    v_summary := public.get_user_xp_summary();

    return v_summary || jsonb_build_object(
        'award', jsonb_build_object(
            'activityType', v_type,
            'xp', v_gained,
            'count', v_count,
            -- Einheitlicher Faktor nur, wenn alle Teilantworten gleich eingestuft wurden.
            'factorKind', case
                when v_count > 0 and (select count(distinct kind) from unnest(v_kinds) as kinds(kind)) = 1
                    then v_kinds[1]
                else null
            end,
            'factor', case
                when v_count > 0 and (select count(distinct kind) from unnest(v_kinds) as kinds(kind)) = 1
                    then v_factors[1]
                else null
            end
        )
    );
end;
$$;

revoke all on function public.award_xp(text, text, jsonb, text) from public;
revoke all on function public.award_xp(text, text, jsonb, text) from anon;
grant execute on function public.award_xp(text, text, jsonb, text) to authenticated;
