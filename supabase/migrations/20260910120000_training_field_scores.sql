begin;

create or replace function public._compute_training_task_score(
    p_details jsonb,
    p_retry_penalty numeric
)
returns numeric
language plpgsql
immutable
as $$
declare
    v_answered_sum numeric := 0;
    v_answered_count integer := 0;
    v_revealed_count integer := 0;
    v_checkable integer;
    v_n numeric;
    v_elem jsonb;
    v_question jsonb;
    v_field_sum numeric;
    v_field_count integer;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    if p_details ? 'question_fields' then
        if jsonb_typeof(p_details -> 'question_fields') is distinct from 'array' then
            return null;
        end if;

        for v_question in
            select value from jsonb_array_elements(p_details -> 'question_fields') as questions(value)
        loop
            if jsonb_typeof(v_question) is distinct from 'array' then
                return null;
            end if;
            v_field_sum := 0;
            v_field_count := jsonb_array_length(v_question);
            if v_field_count = 0 then
                return null;
            end if;

            for v_elem in
                select value from jsonb_array_elements(v_question) as fields(value)
            loop
                if v_elem -> 'revealed' = 'true'::jsonb then
                    continue;
                end if;
                if (v_elem -> 'correct') is distinct from 'true'::jsonb
                    or jsonb_typeof(v_elem -> 'attempts') is distinct from 'number' then
                    return null;
                end if;
                v_n := (v_elem ->> 'attempts')::numeric;
                if v_n < 1 or v_n <> trunc(v_n) then
                    return null;
                end if;
                v_field_sum := v_field_sum
                    + greatest(0, 1 - (v_n - 1) * coalesce(p_retry_penalty, 0.5));
            end loop;

            v_answered_sum := v_answered_sum + v_field_sum / v_field_count;
            v_answered_count := v_answered_count + 1;
        end loop;

        return v_answered_sum / nullif(v_answered_count, 0);
    end if;

    if (p_details ? 'question_attempts')
        or (p_details ? 'revealed_count')
        or (p_details ? 'checkable_count') then

        if jsonb_typeof(p_details -> 'question_attempts') = 'array' then
            for v_elem in
                select value from jsonb_array_elements(p_details -> 'question_attempts') as t(value)
            loop
                v_n := greatest(coalesce(nullif(v_elem #>> '{}', '')::numeric, 1), 1);
                v_answered_sum := v_answered_sum
                    + greatest(0, 1 - (v_n - 1) * coalesce(p_retry_penalty, 0.5));
                v_answered_count := v_answered_count + 1;
            end loop;
        end if;

        v_revealed_count := greatest(coalesce((p_details ->> 'revealed_count')::integer, 0), 0);
        v_checkable := coalesce((p_details ->> 'checkable_count')::integer, v_answered_count + v_revealed_count);

        if v_checkable > 0 then
            return v_answered_sum / v_checkable;
        end if;
        return null;
    end if;

    if (p_details ? 'correctCount') and (p_details ? 'totalCount') then
        if coalesce((p_details ->> 'solutionsShown')::boolean, false) then
            return null;
        end if;
        if coalesce((p_details ->> 'totalCount')::integer, 0) > 0 then
            return (p_details ->> 'correctCount')::numeric / (p_details ->> 'totalCount')::numeric;
        end if;
        return null;
    end if;

    return null;
end;
$$;

do $$
declare
    v_case record;
    v_actual numeric;
begin
    for v_case in
        select * from (values
            ('both correct', '{"question_fields":[[{"correct":true,"attempts":1},{"correct":true,"attempts":1}]]}', 0.5, 1.0),
            ('correct plus revealed', '{"question_fields":[[{"correct":true,"attempts":1},{"revealed":true}]]}', 0.5, 0.5),
            ('correct plus retry', '{"question_fields":[[{"correct":true,"attempts":1},{"correct":true,"attempts":2}]]}', 0.5, 0.75),
            ('third attempt', '{"question_fields":[[{"correct":true,"attempts":1},{"correct":true,"attempts":3}]]}', 0.5, 0.5),
            ('custom penalty', '{"question_fields":[[{"correct":true,"attempts":1},{"correct":true,"attempts":2}]]}', 0.2, 0.9),
            ('equal question weights', '{"question_fields":[[{"correct":true,"attempts":1},{"revealed":true}],[{"revealed":true}]]}', 0.5, 0.25),
            ('all revealed', '{"question_fields":[[{"revealed":true},{"revealed":true}]]}', 0.5, 0.0),
            ('open field', '{"question_fields":[[{"correct":false,"revealed":false,"attempts":1}]]}', 0.5, null),
            ('empty fields', '{"question_fields":[[]]}', 0.5, null),
            ('empty task', '{"question_fields":[]}', 0.5, null),
            ('legacy questions', '{"checkable_count":2,"question_attempts":[2],"revealed_count":1}', 0.5, 0.25),
            ('legacy counts', '{"correctCount":1,"totalCount":2}', 0.5, 0.5),
            ('legacy global reveal', '{"correctCount":1,"totalCount":2,"solutionsShown":true}', 0.5, null)
        ) as cases(label, details, penalty, expected)
    loop
        v_actual := public._compute_training_task_score(v_case.details::jsonb, v_case.penalty);
        if v_actual is distinct from v_case.expected then
            raise exception 'Training score regression: %, expected %, got %',
                v_case.label, v_case.expected, v_actual;
        end if;
    end loop;
end;
$$;

commit;