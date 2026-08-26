-- Test-Quote: Read-Model fuer die neue Test-Aktivitaet (Single-Choice, 10 Fragen je Check).
--
-- Rohschema in user_activity_events.details fuer activity_type = 'test':
--   questionResults : jsonb-Array je Frage: { correct: boolean, answerIndex: int, timeMs: int }
--   correctCount    : Anzahl richtig beantworteter Fragen
--   totalCount      : Anzahl gestellter Fragen (regulaer 10)
--
-- Score eines Durchgangs = correctCount / totalCount (kein Retry-Penalty:
-- Single-Choice mit genau einem Versuch je Frage).

alter table public.user_activity_events
    drop constraint if exists user_activity_events_activity_type_check;

alter table public.user_activity_events
    add constraint user_activity_events_activity_type_check
    check (activity_type in ('training', 'recall', 'feynman', 'flashcards', 'test'));

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

    if normalized_activity_type not in ('training', 'recall', 'feynman', 'flashcards', 'test') then
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

insert into public.system_settings (setting_key, value_integer, description)
values
    ('test_proficiency.window_size', 3, 'Test-Quote: Anzahl der juengsten Test-Durchgaenge je Check im Recency-Fenster (N).')
on conflict (setting_key) do nothing;

insert into public.system_settings (setting_key, value_numeric, description)
values
    ('test_proficiency.recency_decay', 0.5, 'Test-Quote: Recency-Decay d je Position im Fenster (juengere Durchgaenge zaehlen staerker).')
on conflict (setting_key) do nothing;

create or replace function public._compute_test_task_score(
    p_details jsonb
)
returns numeric
language plpgsql
immutable
as $$
declare
    v_correct numeric;
    v_total numeric;
    v_sum numeric := 0;
    v_count integer := 0;
    v_elem jsonb;
begin
    if p_details is null or jsonb_typeof(p_details) <> 'object' then
        return null;
    end if;

    v_correct := nullif(p_details ->> 'correctCount', '')::numeric;
    v_total := nullif(p_details ->> 'totalCount', '')::numeric;

    if v_correct is not null and v_total is not null and v_total > 0 then
        return greatest(0, least(1, v_correct / v_total));
    end if;

    if jsonb_typeof(p_details -> 'questionResults') <> 'array' then
        return null;
    end if;

    for v_elem in
        select value from jsonb_array_elements(p_details -> 'questionResults') as t(value)
    loop
        v_count := v_count + 1;
        if coalesce((v_elem ->> 'correct')::boolean, false) then
            v_sum := v_sum + 1;
        end if;
    end loop;

    if v_count = 0 then
        return null;
    end if;

    return v_sum / v_count;
end;
$$;

create or replace function public.get_user_test_proficiency()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    v_window integer := greatest(public.get_system_setting_integer('test_proficiency.window_size', 3), 1);
    v_decay numeric := public.get_system_setting_numeric('test_proficiency.recency_decay', 0.5);
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
            public._compute_test_task_score(details) as task_score
        from public.user_activity_events
        where user_id = current_user_id
          and activity_type = 'test'
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
            max(created_at) as last_test_at
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
                    'lastTestAt', last_test_at
                )
                order by quote asc, last_test_at desc
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

revoke all on function public.get_user_test_proficiency() from public;
revoke all on function public.get_user_test_proficiency() from anon;
grant execute on function public.get_user_test_proficiency() to authenticated;
