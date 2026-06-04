create table if not exists public.user_activity_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    activity_type text not null check (activity_type in ('training', 'recall', 'feynman', 'flashcards')),
    lernbereich_slug text null check (
        lernbereich_slug is null or char_length(trim(lernbereich_slug)) > 0
    ),
    check_id text null check (
        check_id is null or char_length(trim(check_id)) > 0
    ),
    context_key text null check (
        context_key is null or char_length(trim(context_key)) > 0
    ),
    details jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists user_activity_events_user_created_idx
    on public.user_activity_events (user_id, created_at desc);

create index if not exists user_activity_events_user_type_created_idx
    on public.user_activity_events (user_id, activity_type, created_at desc);

grant select on public.user_activity_events to authenticated;

alter table public.user_activity_events enable row level security;

drop policy if exists user_activity_events_select_own on public.user_activity_events;
create policy user_activity_events_select_own
    on public.user_activity_events
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

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

    if normalized_activity_type not in ('training', 'recall', 'feynman', 'flashcards') then
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

create or replace function public.get_user_activity_overview()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    overview jsonb;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    with local_clock as (
        select timezone('Europe/Berlin', now())::date as today_local
    ),
    base as (
        select
            activity_type,
            timezone('Europe/Berlin', created_at)::date as activity_date,
            created_at
        from public.user_activity_events
        where user_id = current_user_id
    ),
    summary as (
        select
            count(*)::integer as total_count,
            count(distinct activity_date)::integer as active_days,
            min(activity_date) as first_activity_date,
            max(activity_date) as last_activity_date
        from base
    ),
    best_day as (
        select
            activity_date,
            count(*)::integer as activity_count
        from base
        group by activity_date
        order by activity_count desc, activity_date desc
        limit 1
    ),
    counts_by_type as (
        select
            activity_type,
            count(*)::integer as activity_count
        from base
        group by activity_type
    ),
    last_7_days as (
        select
            series.activity_date,
            coalesce(count(base.activity_date), 0)::integer as activity_count
        from (
            select generate_series(
                (select today_local from local_clock) - 6,
                (select today_local from local_clock),
                interval '1 day'
            )::date as activity_date
        ) as series
        left join base
            on base.activity_date = series.activity_date
        group by series.activity_date
        order by series.activity_date
    )
    select jsonb_build_object(
        'totalCount', coalesce(summary.total_count, 0),
        'activeDays', coalesce(summary.active_days, 0),
        'firstActivityDate', summary.first_activity_date,
        'lastActivityDate', summary.last_activity_date,
        'averagePerActiveDay', case
            when coalesce(summary.active_days, 0) > 0 then round(summary.total_count::numeric / summary.active_days, 1)
            else 0
        end,
        'bestDay', case
            when best_day.activity_date is null then null
            else jsonb_build_object(
                'date', best_day.activity_date,
                'count', best_day.activity_count
            )
        end,
        'byType', jsonb_build_object(
            'training', coalesce((select activity_count from counts_by_type where activity_type = 'training'), 0),
            'recall', coalesce((select activity_count from counts_by_type where activity_type = 'recall'), 0),
            'feynman', coalesce((select activity_count from counts_by_type where activity_type = 'feynman'), 0),
            'flashcards', coalesce((select activity_count from counts_by_type where activity_type = 'flashcards'), 0)
        ),
        'last7Days', coalesce(
            (
                select jsonb_agg(
                    jsonb_build_object(
                        'date', activity_date,
                        'count', activity_count
                    )
                    order by activity_date
                )
                from last_7_days
            ),
            '[]'::jsonb
        )
    )
    into overview
    from summary
    left join best_day on true;

    return coalesce(
        overview,
        jsonb_build_object(
            'totalCount', 0,
            'activeDays', 0,
            'firstActivityDate', null,
            'lastActivityDate', null,
            'averagePerActiveDay', 0,
            'bestDay', null,
            'byType', jsonb_build_object(
                'training', 0,
                'recall', 0,
                'feynman', 0,
                'flashcards', 0
            ),
            'last7Days', '[]'::jsonb
        )
    );
end;
$$;

revoke all on function public.record_user_activity(text, text, text, text, jsonb) from public;
revoke all on function public.record_user_activity(text, text, text, text, jsonb) from anon;
grant execute on function public.record_user_activity(text, text, text, text, jsonb) to authenticated;

revoke all on function public.get_user_activity_overview() from public;
revoke all on function public.get_user_activity_overview() from anon;
grant execute on function public.get_user_activity_overview() to authenticated;