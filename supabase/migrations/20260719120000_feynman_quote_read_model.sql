-- Feynman-Quote: eigenes, zur Trainings- und Recall-Quote paralleles Read-Model.
--
-- Rohschema in user_activity_events.details fuer activity_type = 'feynman':
--   rawItemScores  : jsonb-Array der KI-Scores je Teilfrage (0..1)
--   itemAttempts   : jsonb-Array der Pruefversuche je Teilfrage
--   itemRevealed   : jsonb-Array, fuer spaetere optionale Erklaerungsanzeige
--   checkableCount : Anzahl auswertbarer Teilfragen
--
-- Feynman bleibt unabhaengig von Training und Recall. Die Quote misst, ob
-- Schuelererklärungen zu konkreten Aufgaben den Loesungsweg tragfaehig
-- beschreiben, nicht ob eine numerische Trainingsantwort direkt geloest wurde.

insert into public.system_settings (setting_key, value_integer, description)
values
    ('feynman_proficiency.window_size', 3, 'Feynman-Quote: Anzahl der juengsten Feynman-Taskscores je Check im Recency-Fenster (N).'),
    ('feynman_evaluate.daily_request_limit', 30, 'Feynman-KI-Bewertung: maximale Anzahl Anfragen pro Nutzer und Tag an feynman-evaluate.')
on conflict (setting_key) do nothing;

insert into public.system_settings (setting_key, value_numeric, description)
values
    ('feynman_proficiency.recency_decay', 0.5, 'Feynman-Quote: Recency-Decay d je Position im Fenster (juengere Taskscores zaehlen staerker).'),
    ('feynman_proficiency.retry_penalty', 0.5, 'Feynman-Quote: Versuchsabzug p je zusaetzlichem Pruefen einer Feynman-Erklaerung.')
on conflict (setting_key) do nothing;

create or replace function public._compute_feynman_task_score(
    p_details jsonb,
    p_retry_penalty numeric
)
returns numeric
language plpgsql
immutable
as $$
declare
    v_sum numeric := 0;
    v_count integer := 0;
    v_checkable integer;
    v_elem jsonb;
    v_scores jsonb;
    v_attempts jsonb;
    v_revealed jsonb;
    v_score numeric;
    v_attempt_count numeric;
    v_is_revealed boolean;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    if jsonb_typeof(p_details -> 'rawItemScores') = 'array' then
        v_scores := p_details -> 'rawItemScores';
        v_attempts := p_details -> 'itemAttempts';
        v_revealed := p_details -> 'itemRevealed';
        v_count := jsonb_array_length(v_scores);
        v_checkable := greatest(coalesce((p_details ->> 'checkableCount')::integer, v_count), v_count);

        if v_count = 0 then
            return null;
        end if;

        for v_index in 0..(v_count - 1) loop
            v_is_revealed := jsonb_typeof(v_revealed) = 'array'
                and coalesce((v_revealed ->> v_index)::boolean, false);

            if v_is_revealed then
                continue;
            end if;

            v_score := greatest(0, least(1, coalesce(nullif(v_scores ->> v_index, '')::numeric, 0)));
            v_attempt_count := greatest(1, coalesce(nullif(v_attempts ->> v_index, '')::numeric, 1));
            v_sum := v_sum
                + v_score * greatest(0, 1 - (v_attempt_count - 1) * coalesce(p_retry_penalty, 0.5));
        end loop;

        if v_checkable > 0 then
            return v_sum / v_checkable;
        end if;
        return null;
    end if;

    -- Legacy-/Fallback-Schema: itemScores sind bereits finale Item-Scores.
    if jsonb_typeof(p_details -> 'itemScores') <> 'array' then
        return null;
    end if;

    v_count := 0;
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

create or replace function public._compute_feynman_task_score(
    p_details jsonb
)
returns numeric
language plpgsql
immutable
as $$
begin
    return public._compute_feynman_task_score(p_details, 0.5);
end;
$$;

create or replace function public.get_user_feynman_proficiency()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    v_window integer := greatest(public.get_system_setting_integer('feynman_proficiency.window_size', 3), 1);
    v_decay numeric := public.get_system_setting_numeric('feynman_proficiency.recency_decay', 0.5);
    v_retry_penalty numeric := public.get_system_setting_numeric('feynman_proficiency.retry_penalty', 0.5);
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
            public._compute_feynman_task_score(details, v_retry_penalty) as task_score
        from public.user_activity_events
        where user_id = current_user_id
          and activity_type = 'feynman'
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
            max(created_at) as last_feynman_at
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
                    'lastFeynmanAt', last_feynman_at
                )
                order by quote asc, last_feynman_at desc
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

revoke all on function public.get_user_feynman_proficiency() from public;
revoke all on function public.get_user_feynman_proficiency() from anon;
grant execute on function public.get_user_feynman_proficiency() to authenticated;
