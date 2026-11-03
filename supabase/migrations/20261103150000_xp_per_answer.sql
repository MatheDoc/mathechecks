-- XP pro richtiger Teilantwort (Training: Antwortfeld, Test: Frage, Warm-Up: Schritt).
--
-- Statt erst beim Abschluss eines Durchgangs vergibt award_xp die XP sofort serverseitig und
-- speichert sie in user_xp_awards (unveraenderlich, "nichts geht zurueck"). Recall und Feynman
-- bleiben durchgangsbasiert (KI-Bewertung am Ende) und werden weiter aus user_activity_events
-- berechnet. Training/Test/Warm-Up-Ereignisse zaehlen nur noch vor der ersten Einzelvergabe
-- eines Nutzers (Altbestand), damit nichts doppelt zaehlt.
--
-- XP je Teilantwort = round(Einheitsgewicht * Score * Faktor)
--   Score  = max(0, 1 - (Versuche - 1) * p) mit p aus der jeweiligen Quote (Test: immer 1).
--   Faktor = erstmals (keine fruehere Vergabe fuer denselben Schluessel) xp.first_success_factor,
--            sonst 1, wenn innerhalb von xp.repeat_gap_hours keine Vergabe liegt,
--            sonst xp.repeat_factor bzw. ab xp.repeat_late_after Vergaben xp.repeat_late_factor.
--   Schluessel = Typ + Check + unit_key (Training "t<Aufgabe>:q<Frage>:f<Feld>", Test "q<Quelle>",
--            Warm-Up "p<Seite>:s<Schritt>").
-- Alle Gewichte werden mit Faktor 4 skaliert, damit auch Wiederholungsfaktoren ganze XP ergeben.

create table if not exists public.user_xp_awards (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    activity_type text not null check (activity_type in ('training', 'test', 'warmup')),
    lernbereich_slug text null,
    check_id text not null check (char_length(trim(check_id)) > 0),
    unit_key text not null check (char_length(trim(unit_key)) between 1 and 120),
    attempts integer not null default 1 check (attempts >= 1),
    score numeric not null,
    factor numeric not null,
    xp integer not null check (xp >= 0),
    created_at timestamptz not null default now()
);

create index if not exists user_xp_awards_unit_idx
    on public.user_xp_awards (user_id, activity_type, check_id, unit_key, created_at desc);

create index if not exists user_xp_awards_user_created_idx
    on public.user_xp_awards (user_id, created_at);

grant select on public.user_xp_awards to authenticated;

alter table public.user_xp_awards enable row level security;

drop policy if exists user_xp_awards_select_own on public.user_xp_awards;
create policy user_xp_awards_select_own
    on public.user_xp_awards
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

update public.system_settings set value_numeric = 40, description = 'XP: Gewicht eines vollstaendig richtigen Warm-Ups (nur Altbestand vor Einzelvergabe).' where setting_key = 'xp.weight.warmup';
update public.system_settings set value_numeric = 20, description = 'XP: Gewicht einer vollstaendig richtigen Trainingsaufgabe (nur Altbestand vor Einzelvergabe).' where setting_key = 'xp.weight.training';
update public.system_settings set value_numeric = 32, description = 'XP: Gewicht eines vollstaendig richtigen Test-Durchgangs (nur Altbestand vor Einzelvergabe).' where setting_key = 'xp.weight.test';
update public.system_settings set value_numeric = 100 where setting_key = 'xp.weight.recall';
update public.system_settings set value_numeric = 160 where setting_key = 'xp.weight.feynman';
update public.system_settings set value_numeric = 80 where setting_key = 'xp.level_step';

insert into public.system_settings (setting_key, value_numeric, description)
values
    ('xp.unit_weight.training', 8, 'XP: Gewicht eines richtigen Antwortfelds im Training.'),
    ('xp.unit_weight.test', 4, 'XP: Gewicht einer richtigen Test-Frage.'),
    ('xp.unit_weight.warmup', 4, 'XP: Gewicht eines richtigen Warm-Up-Schritts.')
on conflict (setting_key) do nothing;

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
    v_level_step numeric := greatest(public.get_system_setting_numeric('xp.level_step', 80), 1);
    v_first_award_at timestamptz;
    v_gap interval;
    v_weights jsonb;
    v_total integer := 0;
    v_by_type jsonb := '{}'::jsonb;
    v_event jsonb := null;
    v_level integer;
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

    v_level := greatest(1, floor((1 + sqrt(1 + 8 * v_total / v_level_step)) / 2)::integer);
    while v_level_step * (v_level + 1) * v_level / 2 <= v_total loop
        v_level := v_level + 1;
    end loop;
    while v_level > 1 and v_level_step * v_level * (v_level - 1) / 2 > v_total loop
        v_level := v_level - 1;
    end loop;

    return jsonb_build_object(
        'totalXp', v_total,
        'level', v_level,
        'levelStartXp', ceil(v_level_step * v_level * (v_level - 1) / 2)::integer,
        'nextLevelXp', ceil(v_level_step * (v_level + 1) * v_level / 2)::integer,
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
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if v_type not in ('training', 'test', 'warmup') then
        raise exception 'Unsupported activity type';
    end if;

    if v_check_id is null then
        raise exception 'check_id required';
    end if;

    if jsonb_typeof(p_units) is distinct from 'array'
        or jsonb_array_length(p_units) = 0
        or jsonb_array_length(p_units) > 50 then
        raise exception 'units must be a non-empty array';
    end if;

    v_weight := public.get_system_setting_numeric(
        'xp.unit_weight.' || v_type,
        case v_type when 'training' then 8 else 4 end
    );
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
            user_id, activity_type, lernbereich_slug, check_id, unit_key, attempts, score, factor, xp
        )
        values (
            current_user_id, v_type, v_lernbereich_slug, v_check_id, v_key, v_attempts, v_score, v_factor, v_xp
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
