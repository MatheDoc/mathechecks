-- Recall/Feynman: zweite Chancen honorieren Verbesserungen, ohne den Erstversuch
-- vollstaendig zu ersetzen. Historische Events ohne firstItemScores/bestItemScores
-- behalten die bisherige Retry-Berechnung.

update public.system_settings
set description = 'Recall-Quote: Anteil der Verbesserung zwischen Erst- und Bestscore eines Recall-Items.'
where setting_key = 'recall_proficiency.retry_penalty';

update public.system_settings
set description = 'Feynman-Quote: Anteil der Verbesserung zwischen Erst- und Bestscore einer Feynman-Erklaerung.'
where setting_key = 'feynman_proficiency.retry_penalty';

create or replace function public._compute_recall_task_score(
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
    v_first_scores jsonb;
    v_best_scores jsonb;
    v_attempts jsonb;
    v_revealed jsonb;
    v_score numeric;
    v_first_score numeric;
    v_best_score numeric;
    v_attempt_count numeric;
    v_is_revealed boolean;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    if jsonb_typeof(p_details -> 'firstItemScores') = 'array'
        and jsonb_typeof(p_details -> 'bestItemScores') = 'array' then
        v_first_scores := p_details -> 'firstItemScores';
        v_best_scores := p_details -> 'bestItemScores';
        v_revealed := p_details -> 'itemRevealed';
        v_count := least(jsonb_array_length(v_first_scores), jsonb_array_length(v_best_scores));
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

            v_first_score := greatest(0, least(1, coalesce(nullif(v_first_scores ->> v_index, '')::numeric, 0)));
            v_best_score := greatest(v_first_score, least(1, coalesce(nullif(v_best_scores ->> v_index, '')::numeric, v_first_score)));
            v_sum := v_sum + v_first_score
                + (v_best_score - v_first_score) * greatest(0, least(1, coalesce(p_retry_penalty, 0.5)));
        end loop;

        return case when v_checkable > 0 then v_sum / v_checkable else null end;
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
            v_sum := v_sum + v_score * greatest(0, 1 - (v_attempt_count - 1) * coalesce(p_retry_penalty, 0.5));
        end loop;

        return case when v_checkable > 0 then v_sum / v_checkable else null end;
    end if;

    if jsonb_typeof(p_details -> 'itemScores') <> 'array' then
        return null;
    end if;

    for v_elem in select value from jsonb_array_elements(p_details -> 'itemScores') as t(value) loop
        v_score := nullif(v_elem #>> '{}', '')::numeric;
        if v_score is not null then
            v_sum := v_sum + greatest(0, least(1, v_score));
            v_count := v_count + 1;
        end if;
    end loop;

    return case when v_count > 0 then v_sum / v_count else null end;
end;
$$;

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
    v_first_scores jsonb;
    v_best_scores jsonb;
    v_attempts jsonb;
    v_revealed jsonb;
    v_score numeric;
    v_first_score numeric;
    v_best_score numeric;
    v_attempt_count numeric;
    v_is_revealed boolean;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    if jsonb_typeof(p_details -> 'firstItemScores') = 'array'
        and jsonb_typeof(p_details -> 'bestItemScores') = 'array' then
        v_first_scores := p_details -> 'firstItemScores';
        v_best_scores := p_details -> 'bestItemScores';
        v_revealed := p_details -> 'itemRevealed';
        v_count := least(jsonb_array_length(v_first_scores), jsonb_array_length(v_best_scores));
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

            v_first_score := greatest(0, least(1, coalesce(nullif(v_first_scores ->> v_index, '')::numeric, 0)));
            v_best_score := greatest(v_first_score, least(1, coalesce(nullif(v_best_scores ->> v_index, '')::numeric, v_first_score)));
            v_sum := v_sum + v_first_score
                + (v_best_score - v_first_score) * greatest(0, least(1, coalesce(p_retry_penalty, 0.5)));
        end loop;

        return case when v_checkable > 0 then v_sum / v_checkable else null end;
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
            v_sum := v_sum + v_score * greatest(0, 1 - (v_attempt_count - 1) * coalesce(p_retry_penalty, 0.5));
        end loop;

        return case when v_checkable > 0 then v_sum / v_checkable else null end;
    end if;

    if jsonb_typeof(p_details -> 'itemScores') <> 'array' then
        return null;
    end if;

    for v_elem in select value from jsonb_array_elements(p_details -> 'itemScores') as t(value) loop
        v_score := nullif(v_elem #>> '{}', '')::numeric;
        if v_score is not null then
            v_sum := v_sum + greatest(0, least(1, v_score));
            v_count := v_count + 1;
        end if;
    end loop;

    return case when v_count > 0 then v_sum / v_count else null end;
end;
$$;
