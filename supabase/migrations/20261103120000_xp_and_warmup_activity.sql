-- XP (Erfahrungspunkte) und Warm-Up-Ereignisse.
--
-- XP sind ein Read-Model ueber user_activity_events (kein eigener Speicher):
--   XP je Ereignis = round(Gewicht[Typ] * Score * Faktor)
--   Score    = Aufgaben-Score des Ereignisses (0..1), dieselben Funktionen wie fuer die Quoten.
--   Schluessel fuer Wiederholungen = Typ + Check (+ taskIndex bei Training).
--   Faktor   = xp.first_success_factor, solange fuer den Schluessel noch kein erfolgreicher
--              Durchgang (Score >= xp.success_threshold) existiert ("erstmals");
--              1, wenn im Zeitraum xp.repeat_gap_hours davor kein erfolgreicher Durchgang liegt
--              (zeitlich getrennte Wiederholung);
--              sonst xp.repeat_factor bzw. ab xp.repeat_late_after Wiederholungen im Zeitraum
--              xp.repeat_late_factor (gehaeufte Wiederholung).
-- Die Gewichte steuern bewusst Richtung Recall und Feynman. Aenderungen an den Einstellungen
-- wirken rueckwirkend auf alle Summen (gewollt).
-- Flashcards (nur Selbsteinschaetzung) zaehlen nicht.
-- Stufen: Stufe L beginnt bei xp.level_step * L * (L - 1) / 2 XP (Stufe 1 bei 0 XP).
--
-- Warm-Up: ein Ereignis je abgeschlossenem Warm-Up (activity_type = 'warmup'), details:
--   steps         : jsonb-Array je bewertetem Schritt: { typ: text, attempts: int, revealed: bool }
--   gradedCount   : Anzahl bewerteter Schritte
--   firstTryCount : im ersten Versuch richtig geloeste Schritte
--   revealedCount : Schritte mit eingeblendeter Loesung
-- Schritt-Score = max(0, 1 - (attempts - 1) * p) bzw. 0 bei eingeblendeter Loesung.

alter table public.user_activity_events
    drop constraint if exists user_activity_events_activity_type_check;

alter table public.user_activity_events
    add constraint user_activity_events_activity_type_check
    check (activity_type in ('training', 'recall', 'feynman', 'flashcards', 'test', 'warmup'));

create or replace function public.record_user_activity(
    p_activity_type text,
    p_lernbereich_slug text default null,
    p_check_id text default null,
    p_context_key text default null,
    p_details jsonb default '{}'::jsonb
)
returns public.user_activity_events
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_activity_type text := lower(coalesce(nullif(trim(p_activity_type), ''), ''));
    normalized_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    normalized_check_id text := nullif(trim(p_check_id), '');
    normalized_context_key text := nullif(trim(p_context_key), '');
    normalized_details jsonb := coalesce(p_details, '{}'::jsonb);
    inserted_row public.user_activity_events;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_activity_type not in ('training', 'recall', 'feynman', 'flashcards', 'test', 'warmup') then
        raise exception 'Unsupported activity type';
    end if;

    if jsonb_typeof(normalized_details) <> 'object' then
        raise exception 'details must be a JSON object';
    end if;

    insert into public.user_activity_events (
        user_id,
        activity_type,
        lernbereich_slug,
        check_id,
        context_key,
        details
    )
    values (
        current_user_id,
        normalized_activity_type,
        normalized_lernbereich_slug,
        normalized_check_id,
        normalized_context_key,
        normalized_details
    )
    returning * into inserted_row;

    return inserted_row;
end;
$$;

create or replace function public._compute_warmup_score(
    p_details jsonb,
    p_retry_penalty numeric
)
returns numeric
language plpgsql
immutable
as $$
declare
    v_step jsonb;
    v_sum numeric := 0;
    v_count integer := 0;
    v_attempts numeric;
    v_graded numeric;
    v_first numeric;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    if jsonb_typeof(p_details -> 'steps') = 'array' then
        for v_step in
            select value from jsonb_array_elements(p_details -> 'steps') as steps(value)
        loop
            if jsonb_typeof(v_step) is distinct from 'object' then
                continue;
            end if;
            v_count := v_count + 1;
            if v_step -> 'revealed' = 'true'::jsonb then
                continue;
            end if;
            v_attempts := case
                when jsonb_typeof(v_step -> 'attempts') = 'number' then greatest((v_step ->> 'attempts')::numeric, 1)
                else 1
            end;
            v_sum := v_sum + greatest(0, 1 - (v_attempts - 1) * coalesce(p_retry_penalty, 0.5));
        end loop;

        return case when v_count > 0 then v_sum / v_count else null end;
    end if;

    if jsonb_typeof(p_details -> 'gradedCount') = 'number'
        and jsonb_typeof(p_details -> 'firstTryCount') = 'number' then
        v_graded := (p_details ->> 'gradedCount')::numeric;
        v_first := (p_details ->> 'firstTryCount')::numeric;
        if v_graded > 0 then
            return greatest(0, least(1, v_first / v_graded));
        end if;
    end if;

    return null;
end;
$$;

insert into public.system_settings (setting_key, value_numeric, description)
values
    ('warmup_proficiency.retry_penalty', 0.5, 'Warm-Up: Abzug je weiterem Versuch eines bewerteten Schritts.'),
    ('xp.weight.warmup', 10, 'XP: Gewicht eines vollstaendig richtigen Warm-Ups.'),
    ('xp.weight.training', 5, 'XP: Gewicht einer vollstaendig richtigen Trainingsaufgabe.'),
    ('xp.weight.test', 8, 'XP: Gewicht eines vollstaendig richtigen Test-Durchgangs.'),
    ('xp.weight.recall', 25, 'XP: Gewicht eines vollstaendig richtigen Recall-Durchgangs.'),
    ('xp.weight.feynman', 40, 'XP: Gewicht einer vollstaendig richtigen Feynman-Erklaerung.'),
    ('xp.first_success_factor', 1.5, 'XP: Faktor, solange fuer Typ+Check(+Aufgabe) noch kein erfolgreicher Durchgang existiert.'),
    ('xp.success_threshold', 0.5, 'XP: Mindest-Score, ab dem ein Durchgang als erfolgreich gilt.'),
    ('xp.repeat_factor', 0.5, 'XP: Faktor fuer gehaeufte Wiederholungen innerhalb von xp.repeat_gap_hours.'),
    ('xp.repeat_late_factor', 0.25, 'XP: Faktor ab xp.repeat_late_after gehaeuften Wiederholungen.'),
    ('xp.level_step', 20, 'XP: Stufe L beginnt bei level_step * L * (L - 1) / 2 XP.')
on conflict (setting_key) do nothing;

insert into public.system_settings (setting_key, value_integer, description)
values
    ('xp.repeat_gap_hours', 20, 'XP: Abstand in Stunden, ab dem eine Wiederholung wieder voll zaehlt.'),
    ('xp.repeat_late_after', 3, 'XP: Ab so vielen erfolgreichen Durchgaengen im Abstandsfenster gilt xp.repeat_late_factor.')
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
    v_level_step numeric := greatest(public.get_system_setting_numeric('xp.level_step', 20), 1);
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
        'warmup', public.get_system_setting_numeric('xp.weight.warmup', 10),
        'training', public.get_system_setting_numeric('xp.weight.training', 5),
        'test', public.get_system_setting_numeric('xp.weight.test', 8),
        'recall', public.get_system_setting_numeric('xp.weight.recall', 25),
        'feynman', public.get_system_setting_numeric('xp.weight.feynman', 40)
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
    )
    select
        coalesce((select sum(xp_events.xp) from xp_events), 0)::integer,
        coalesce((
            select jsonb_object_agg(by_type.activity_type, by_type.type_xp)
            from (
                select xp_events.activity_type, sum(xp_events.xp)::integer as type_xp
                from xp_events
                group by xp_events.activity_type
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
            'weights', v_weights,
            'firstSuccessFactor', v_first_factor,
            'repeatGapHours', v_gap_hours,
            'repeatFactor', v_repeat_factor,
            'repeatLateAfter', v_late_after,
            'repeatLateFactor', v_late_factor
        )
    );
end;
$$;

revoke all on function public.get_user_xp_summary(uuid) from public;
revoke all on function public.get_user_xp_summary(uuid) from anon;
grant execute on function public.get_user_xp_summary(uuid) to authenticated;
