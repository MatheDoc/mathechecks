-- Feynman-Quote: PL/pgSQL-Lint-Fix fuer die Score-Funktion.
-- Entfernt die explizite Deklaration der Integer-Loop-Variable, da PL/pgSQL
-- diese im FOR-Loop selbst anlegt und sonst eine Shadowing-Warnung ausgibt.

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
