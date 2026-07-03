-- Recall-Quote: Versuchszahlen und angezeigte Loesungen wie beim Training werten.

insert into public.system_settings (setting_key, value_numeric, description)
values
    ('recall_proficiency.retry_penalty', 0.5, 'Recall-Quote: Versuchsabzug p je zusaetzlichem Pruefen eines Recall-Items.')
on conflict (setting_key) do nothing;

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
    v_attempts jsonb;
    v_revealed jsonb;
    v_index integer;
    v_score numeric;
    v_attempt_count numeric;
    v_is_revealed boolean;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    -- Neues Rohschema:
    -- rawItemScores + itemAttempts + itemRevealed, optional checkableCount.
    -- Angezeigte Loesungen zaehlen als 0; zusaetzliche Pruefversuche senken
    -- den Itemscore analog zur Trainingsquote.
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

    -- Fallback fuer bisherige Recall-Events: itemScores sind bereits final.
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

create or replace function public._compute_recall_task_score(
    p_details jsonb
)
returns numeric
language plpgsql
immutable
as $$
begin
    return public._compute_recall_task_score(p_details, 0.5);
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
    check_quotes as (
        select
            check_id,
            max(lernbereich_slug) as lernbereich_slug,
            sum(power(v_decay, rn - 1) * task_score)
                / nullif(sum(power(v_decay, rn - 1)), 0) as quote,
            count(*)::integer as window_count,
            max(created_at) as last_recalled_at
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
                    'lastRecalledAt', last_recalled_at
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

revoke all on function public.get_user_recall_proficiency() from public;
revoke all on function public.get_user_recall_proficiency() from anon;
grant execute on function public.get_user_recall_proficiency() to authenticated;