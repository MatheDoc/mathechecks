-- Feed-Vereinfachung: "Fortschritt ist ein Fakt, der Feed ist nur eine Empfehlung."
--
-- 1) session_activity_completions: genau ein Abschluss je (Session, Aktivitaet). Jede einmal
--    durchgemachte Aktivitaet zaehlt, egal ob aus dem Feed oder aus der freien Navigation.
--    Schritte einer Check-Kette zaehlen unabhaengig von ihrer Reihenfolge.
-- 2) Einziger Schreibweg: record_user_activity (Module) bzw. complete_session_start (Start)
--    rufen credit_session_activity auf. Kein activity_key-Abgleich, kein Feed-Cursor.
-- 3) get_feed_recommendation: zustandslose Empfehlung der naechsten Aktivitaet
--    (reife Folgeschritte > neuer Stoff > vorgezogene Folgeschritte).
-- 4) feed_attention_summary: Badge = Tagesziel - heute erledigt (Europe/Berlin).
-- 5) session_check_state bleibt nur Mitgliedschaft (welche Checks gehoeren zur Session).
--    Cursor, Sticky-Lock, Zeitfenster und Replan werden fuer den Feed nicht mehr gelesen.
--
-- Kettenreihenfolge: training -> test -> recall -> feynman, Abstand G zwischen zwei Schritten
-- einer Kette (system_settings 'feed.recommendation_gap_hours').

create table if not exists public.session_activity_completions (
    session_id uuid not null references public.learning_sessions(id) on delete cascade,
    activity_key text not null check (char_length(trim(activity_key)) > 0),
    activity_type text not null check (activity_type in ('start', 'training', 'test', 'recall', 'feynman', 'flashcards')),
    lernbereich_slug text not null check (char_length(trim(lernbereich_slug)) > 0),
    check_id text null,
    completed_at timestamptz not null default now(),
    primary key (session_id, activity_key)
);

create index if not exists session_activity_completions_session_completed_idx
    on public.session_activity_completions (session_id, completed_at);

grant select on public.session_activity_completions to authenticated;

alter table public.session_activity_completions enable row level security;

drop policy if exists session_activity_completions_select_own on public.session_activity_completions;
create policy session_activity_completions_select_own
    on public.session_activity_completions
    for select
    to authenticated
    using (
        exists (
            select 1
            from public.learning_sessions
            where learning_sessions.id = session_activity_completions.session_id
              and learning_sessions.user_id = (select auth.uid())
        )
    );

insert into public.system_settings (setting_key, value_integer, value_numeric, description)
values (
    'feed.recommendation_gap_hours',
    20,
    20,
    'Empfohlener Abstand G in Stunden zwischen zwei Schritten derselben Check-Kette (Feed-Empfehlung).'
)
on conflict (setting_key) do nothing;

-- Backfill aus dem bisherigen Pipeline-Stand (alte Reihenfolge training -> recall -> feynman -> test).
-- Fruehere Schritte bekommen gestaffelte Zeitstempel, damit sie nicht alle als "heute erledigt" zaehlen.
with old_steps(step_key, old_rank) as (
    values ('training', 1), ('recall', 2), ('feynman', 3), ('test', 4)
),
state_ranks as (
    select
        scs.session_id,
        scs.check_id,
        public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
        coalesce(scs.last_completed_at, scs.updated_at, now()) as base_completed_at,
        case
            when scs.current_step_key = 'check_completed' or scs.current_step_status = 'completed' then 5
            when scs.current_step_key = 'training' then 1
            when scs.current_step_key = 'recall' then 2
            when scs.current_step_key = 'feynman' then 3
            when scs.current_step_key = 'test' then 4
            else 1
        end as current_rank
    from public.session_check_state scs
    join public.learning_sessions ls
      on ls.id = scs.session_id
     and ls.status = 'active'
)
insert into public.session_activity_completions (session_id, activity_key, activity_type, lernbereich_slug, check_id, completed_at)
select
    sr.session_id,
    'check:' || sr.check_id || ':' || os.step_key,
    os.step_key,
    sr.lernbereich_slug,
    sr.check_id,
    sr.base_completed_at - ((sr.current_rank - 1 - os.old_rank) * interval '1 day')
from state_ranks sr
join old_steps os
  on os.old_rank < sr.current_rank
where sr.lernbereich_slug is not null
on conflict (session_id, activity_key) do nothing;

insert into public.session_activity_completions (session_id, activity_key, activity_type, lernbereich_slug, check_id, completed_at)
select
    sas.session_id,
    'lernbereich:' || sas.lernbereich_slug || ':' || sas.activity_type,
    sas.activity_type,
    sas.lernbereich_slug,
    null,
    coalesce(sas.updated_at, now())
from public.session_activity_state sas
join public.learning_sessions ls
  on ls.id = sas.session_id
 and ls.status = 'active'
where sas.activity_type in ('start', 'flashcards')
  and sas.status = 'completed'
  and nullif(trim(coalesce(sas.lernbereich_slug, '')), '') is not null
on conflict (session_id, activity_key) do nothing;

create or replace function public.feed_chain_step_rank(p_step_key text)
returns integer
language sql
immutable
set search_path = public
as $$
    select case lower(trim(coalesce(p_step_key, '')))
        when 'training' then 1
        when 'test' then 2
        when 'recall' then 3
        when 'feynman' then 4
        else 0
    end;
$$;

-- Alle Aktivitaeten einer Session mit Abschlusszeitpunkt (null = offen).
-- start und flashcards je Lernbereich, training/test/recall/feynman je Check.
create or replace function public.session_activity_items(p_session_id uuid)
returns table (
    activity_key text,
    activity_type text,
    lernbereich_slug text,
    check_id text,
    lernbereich_order integer,
    check_order integer,
    step_rank integer,
    completed_at timestamptz
)
language sql
stable
security definer
set search_path = public
as $$
with session_checks as (
    select
        scs.check_id,
        public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug
    from public.session_check_state scs
    where scs.session_id = p_session_id
      and not exists (
          select 1
          from public.session_check_exclusions sce
          where sce.session_id = scs.session_id
            and sce.check_id = scs.check_id
      )
),
session_lbs as (
    select
        slb.lernbereich_slug,
        coalesce(slb.gebiet_order, 0) * 100000 + coalesce(slb.sort_index, 0) as lernbereich_order
    from public.session_lernbereiche slb
    where slb.session_id = p_session_id
),
items as (
    select
        'lernbereich:' || sl.lernbereich_slug || ':start' as activity_key,
        'start'::text as activity_type,
        sl.lernbereich_slug,
        null::text as check_id,
        sl.lernbereich_order,
        0 as check_order,
        0 as step_rank
    from session_lbs sl

    union all

    select
        'lernbereich:' || sl.lernbereich_slug || ':flashcards',
        'flashcards'::text,
        sl.lernbereich_slug,
        null::text,
        sl.lernbereich_order,
        0,
        9
    from session_lbs sl
    where exists (
        select 1
        from session_checks sc
        where sc.lernbereich_slug = sl.lernbereich_slug
    )

    union all

    select
        'check:' || sc.check_id || ':' || steps.step_key,
        steps.step_key,
        sc.lernbereich_slug,
        sc.check_id,
        coalesce(sl.lernbereich_order, 0),
        public.feed_check_sequence_number(sc.check_id),
        public.feed_chain_step_rank(steps.step_key)
    from session_checks sc
    left join session_lbs sl
      on sl.lernbereich_slug = sc.lernbereich_slug
    cross join (values ('training'), ('test'), ('recall'), ('feynman')) as steps(step_key)
    where sc.lernbereich_slug is not null
)
select
    items.activity_key,
    items.activity_type,
    items.lernbereich_slug,
    items.check_id,
    items.lernbereich_order,
    items.check_order,
    items.step_rank,
    sac.completed_at
from items
left join public.session_activity_completions sac
  on sac.session_id = p_session_id
 and sac.activity_key = items.activity_key;
$$;

revoke all on function public.session_activity_items(uuid) from public;
revoke all on function public.session_activity_items(uuid) from anon;
revoke all on function public.session_activity_items(uuid) from authenticated;

-- Startet die Flashcards-Wiederholung, sobald alle Check-Schritte eines Lernbereichs erledigt sind
-- (bisher in complete_test_step).
create or replace function public.handle_session_lernbereich_completion(
    p_session_id uuid,
    p_user_id uuid,
    p_lernbereich_slug text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    open_check_steps integer := 0;
    current_completed_activity_count bigint := 0;
    retention_activity_gap integer;
begin
    if p_session_id is null or p_user_id is null or p_lernbereich_slug is null then
        return;
    end if;

    select count(*)
    into open_check_steps
    from public.session_activity_items(p_session_id) as items
    where items.lernbereich_slug = p_lernbereich_slug
      and items.check_id is not null
      and items.completed_at is null;

    if open_check_steps > 0 then
        return;
    end if;

    select coalesce(counters.completed_activity_count, 0)
    into current_completed_activity_count
    from public.user_feed_activity_counters counters
    where counters.user_id = p_user_id;

    current_completed_activity_count := coalesce(current_completed_activity_count, 0);
    retention_activity_gap := public.get_system_setting_integer('feed.retention_activity_base_gap', 5);

    delete from public.user_retention_check_exclusions
    where user_id = p_user_id
      and lernbereich_slug = p_lernbereich_slug;

    insert into public.user_retention_scopes (
        user_id,
        activity_type,
        scope_type,
        lernbereich_slug,
        status,
        source_session_id,
        activity_interval,
        activity_due_exponent,
        next_due_after_activity_count,
        feed_queue_entry_activity_count
    )
    values (
        p_user_id,
        'flashcards',
        'lernbereich',
        p_lernbereich_slug,
        'active',
        p_session_id,
        retention_activity_gap,
        0,
        current_completed_activity_count,
        current_completed_activity_count
    )
    on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
    set status = 'active',
        source_session_id = excluded.source_session_id,
        activity_interval = excluded.activity_interval,
        activity_due_exponent = excluded.activity_due_exponent,
        next_due_after_activity_count = excluded.next_due_after_activity_count,
        feed_queue_entry_activity_count = excluded.feed_queue_entry_activity_count,
        updated_at = now();
end;
$$;

revoke all on function public.handle_session_lernbereich_completion(uuid, uuid, text) from public;
revoke all on function public.handle_session_lernbereich_completion(uuid, uuid, text) from anon;
revoke all on function public.handle_session_lernbereich_completion(uuid, uuid, text) from authenticated;

-- Schreibt einen Abschluss in die aktive Session des Users, falls die Aktivitaet dazugehoert
-- und noch offen ist. Gibt true zurueck, wenn der Abschluss neu ist.
create or replace function public.credit_session_activity(
    p_user_id uuid,
    p_activity_type text,
    p_lernbereich_slug text,
    p_check_id text
)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
    normalized_activity_type text := lower(coalesce(nullif(trim(p_activity_type), ''), ''));
    normalized_lernbereich_slug text := nullif(trim(coalesce(p_lernbereich_slug, '')), '');
    normalized_check_id text := nullif(trim(coalesce(p_check_id, '')), '');
    target_activity_key text;
    active_session_id uuid;
    item_lernbereich_slug text;
    item_check_id text;
    item_completed_at timestamptz;
    inserted_count integer := 0;
begin
    if p_user_id is null then
        return false;
    end if;

    if normalized_activity_type in ('training', 'test', 'recall', 'feynman') then
        if normalized_check_id is null then
            return false;
        end if;
        target_activity_key := 'check:' || normalized_check_id || ':' || normalized_activity_type;
    elsif normalized_activity_type in ('start', 'flashcards') then
        if normalized_lernbereich_slug is null then
            return false;
        end if;
        target_activity_key := 'lernbereich:' || normalized_lernbereich_slug || ':' || normalized_activity_type;
    else
        return false;
    end if;

    select ls.id
    into active_session_id
    from public.learning_sessions ls
    where ls.user_id = p_user_id
      and ls.status = 'active'
    order by ls.started_at desc
    limit 1;

    if active_session_id is null then
        return false;
    end if;

    select items.lernbereich_slug, items.check_id, items.completed_at
    into item_lernbereich_slug, item_check_id, item_completed_at
    from public.session_activity_items(active_session_id) as items
    where items.activity_key = target_activity_key;

    if not found or item_completed_at is not null then
        return false;
    end if;

    insert into public.session_activity_completions (
        session_id,
        activity_key,
        activity_type,
        lernbereich_slug,
        check_id
    )
    values (
        active_session_id,
        target_activity_key,
        normalized_activity_type,
        item_lernbereich_slug,
        item_check_id
    )
    on conflict on constraint session_activity_completions_pkey do nothing;

    get diagnostics inserted_count = row_count;
    if inserted_count = 0 then
        return false;
    end if;

    -- Takt der Retention-Wiederholungen (zaehlt abgeschlossene Session-Aktivitaeten).
    insert into public.user_feed_activity_counters (user_id, completed_activity_count)
    values (p_user_id, 1)
    on conflict (user_id) do update
    set completed_activity_count = public.user_feed_activity_counters.completed_activity_count + 1;

    if item_check_id is not null then
        perform public.handle_session_lernbereich_completion(active_session_id, p_user_id, item_lernbereich_slug);
    end if;

    return true;
end;
$$;

revoke all on function public.credit_session_activity(uuid, text, text, text) from public;
revoke all on function public.credit_session_activity(uuid, text, text, text) from anon;
revoke all on function public.credit_session_activity(uuid, text, text, text) from authenticated;

-- Quelle: 20261103120000_xp_and_warmup_activity.sql, ergaenzt um die Session-Gutschrift.
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

    perform public.credit_session_activity(
        current_user_id,
        normalized_activity_type,
        normalized_lernbereich_slug,
        normalized_check_id
    );

    return inserted_row;
end;
$$;

create or replace function public.complete_session_start(p_lernbereich_slug text)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if nullif(trim(coalesce(p_lernbereich_slug, '')), '') is null then
        raise exception 'lernbereich_slug is required';
    end if;

    return public.credit_session_activity(current_user_id, 'start', p_lernbereich_slug, null);
end;
$$;

revoke all on function public.complete_session_start(text) from public;
revoke all on function public.complete_session_start(text) from anon;
grant execute on function public.complete_session_start(text) to authenticated;

-- Zustandslose Empfehlung der naechsten Aktivitaet.
-- Klasse 1: reife Folgeschritte (letzter Abschluss der Kette >= G her); weiter fortgeschrittene
--           Ketten zuerst, dann aeltester Anker. Flashcards, sobald alle Trainings des
--           Lernbereichs >= G her sind.
-- Klasse 2: neuer Stoff in Lernbereichs-Reihenfolge (Start vor Trainings, Checks nach Nummer).
-- Klasse 3: Folgeschritte mit laufendem Abstand (vorziehen), frueheste Reife zuerst.
create or replace function public.session_feed_recommendations(p_session_id uuid)
returns table (
    activity_key text,
    activity_type text,
    lernbereich_slug text,
    check_id text,
    priority_class integer,
    ready_at timestamptz
)
language sql
stable
security definer
set search_path = public
as $$
with params as (
    select make_interval(
        secs => greatest(public.get_system_setting_numeric('feed.recommendation_gap_hours', 20), 0) * 3600
    ) as gap
),
items as (
    select *
    from public.session_activity_items(p_session_id)
),
chain_state as (
    select
        i.check_id,
        max(i.completed_at) as anchor_at,
        count(i.completed_at)::integer as done_count
    from items i
    where i.check_id is not null
    group by i.check_id
),
next_check_steps as (
    select distinct on (i.check_id)
        i.*
    from items i
    where i.check_id is not null
      and i.completed_at is null
    order by i.check_id, i.step_rank
),
lb_training as (
    select
        i.lernbereich_slug,
        bool_and(i.completed_at is not null) as all_trained,
        max(i.completed_at) as last_training_at
    from items i
    where i.activity_type = 'training'
    group by i.lernbereich_slug
),
candidates as (
    select
        i.activity_key,
        i.activity_type,
        i.lernbereich_slug,
        i.check_id,
        2 as priority_class,
        null::timestamptz as ready_at,
        0 as done_count,
        i.lernbereich_order,
        i.check_order,
        i.step_rank
    from items i
    where i.activity_type = 'start'
      and i.completed_at is null

    union all

    select
        ns.activity_key,
        ns.activity_type,
        ns.lernbereich_slug,
        ns.check_id,
        case
            when cs.anchor_at is null then 2
            when cs.anchor_at + params.gap <= now() then 1
            else 3
        end,
        cs.anchor_at + params.gap,
        cs.done_count,
        ns.lernbereich_order,
        ns.check_order,
        ns.step_rank
    from next_check_steps ns
    join chain_state cs
      on cs.check_id = ns.check_id
    cross join params

    union all

    select
        i.activity_key,
        i.activity_type,
        i.lernbereich_slug,
        i.check_id,
        case
            when lt.last_training_at + params.gap <= now() then 1
            else 3
        end,
        lt.last_training_at + params.gap,
        0,
        i.lernbereich_order,
        i.check_order,
        i.step_rank
    from items i
    join lb_training lt
      on lt.lernbereich_slug = i.lernbereich_slug
     and lt.all_trained
    cross join params
    where i.activity_type = 'flashcards'
      and i.completed_at is null
)
select
    c.activity_key,
    c.activity_type,
    c.lernbereich_slug,
    c.check_id,
    c.priority_class,
    c.ready_at
from candidates c
order by
    c.priority_class,
    case when c.priority_class = 1 then -c.done_count else 0 end,
    case when c.priority_class <> 2 then c.ready_at end nulls last,
    c.lernbereich_order,
    c.step_rank = 9,
    c.check_order,
    c.step_rank,
    c.activity_key;
$$;

revoke all on function public.session_feed_recommendations(uuid) from public;
revoke all on function public.session_feed_recommendations(uuid) from anon;
revoke all on function public.session_feed_recommendations(uuid) from authenticated;

create or replace function public.get_feed_recommendation(p_session_id uuid default null)
returns table (
    session_id uuid,
    activity_key text,
    activity_type text,
    lernbereich_slug text,
    check_id text,
    priority_class integer,
    ready_at timestamptz
)
language plpgsql
stable
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    select ls.id
    into resolved_session_id
    from public.learning_sessions ls
    where ls.user_id = current_user_id
      and ls.status = 'active'
      and (p_session_id is null or ls.id = p_session_id)
    order by ls.started_at desc
    limit 1;

    if resolved_session_id is null then
        return;
    end if;

    return query
    select
        resolved_session_id,
        rec.activity_key,
        rec.activity_type,
        rec.lernbereich_slug,
        rec.check_id,
        rec.priority_class,
        rec.ready_at
    from public.session_feed_recommendations(resolved_session_id) as rec
    limit 1;
end;
$$;

revoke all on function public.get_feed_recommendation(uuid) from public;
revoke all on function public.get_feed_recommendation(uuid) from anon;
grant execute on function public.get_feed_recommendation(uuid) to authenticated;

-- Badge "heute noch empfohlen": Tagesziel - heute erledigt, hoechstens alle offenen Aktivitaeten.
-- Tagesziel = ceil(max(activities_per_day, erforderliches Tempo bei explizitem Zieldatum)),
-- erforderliches Tempo bezogen auf den Stand zu Tagesbeginn (offen + heute erledigt).
-- overdue_count bleibt aus Kompatibilitaetsgruenden im Rueckgabetyp und ist immer 0.
create or replace function public.feed_attention_summary(p_session_id uuid default null)
returns table (
    session_id uuid,
    overdue_count integer,
    due_count integer
)
language plpgsql
stable
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid;
    resolved_target_date date;
    resolved_target_source text;
    configured_activities_per_day numeric;
    required_activities_per_day numeric := null;
    berlin_today date := (now() at time zone 'Europe/Berlin')::date;
    berlin_day_start timestamptz := (((now() at time zone 'Europe/Berlin')::date)::timestamp at time zone 'Europe/Berlin');
    open_count integer := 0;
    done_today integer := 0;
    daily_goal integer := 0;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    select ls.id,
           ls.target_date,
           ls.target_source,
           greatest(coalesce(ls.activities_per_day, public.get_default_activities_per_day()), 0.1)
    into resolved_session_id, resolved_target_date, resolved_target_source, configured_activities_per_day
    from public.learning_sessions ls
    where ls.user_id = current_user_id
      and ls.status = 'active'
      and (p_session_id is null or ls.id = p_session_id)
    order by ls.started_at desc
    limit 1;

    if resolved_session_id is null then
        return query select null::uuid, 0, 0;
        return;
    end if;

    select count(*)::integer
    into open_count
    from public.session_activity_items(resolved_session_id) as items
    where items.completed_at is null;

    select count(*)::integer
    into done_today
    from public.session_activity_completions sac
    where sac.session_id = resolved_session_id
      and sac.completed_at >= berlin_day_start;

    if resolved_target_date is not null and resolved_target_source = 'explicit' then
        required_activities_per_day :=
            (open_count + done_today)::numeric
            / greatest(resolved_target_date - berlin_today, 1)::numeric;
    end if;

    daily_goal := ceil(greatest(configured_activities_per_day, coalesce(required_activities_per_day, 0), 0.1))::integer;

    return query
    select
        resolved_session_id,
        0,
        least(greatest(daily_goal - done_today, 0), open_count)::integer;
end;
$$;

revoke all on function public.feed_attention_summary(uuid) from public;
revoke all on function public.feed_attention_summary(uuid) from anon;
grant execute on function public.feed_attention_summary(uuid) to authenticated;

-- Bisherige Feed-Schreibwege mit activity_key-/Cursor-Pflicht entfallen.
drop function if exists public.complete_current_training_step(text, text);
drop function if exists public.record_check_module_attempt(text, text, text, text, text);
drop function if exists public.complete_test_step(text, text);
drop function if exists public.complete_start_activity(text, text);
drop function if exists public.keep_current_feed_activity(text);
drop function if exists public.release_current_feed_activity(text);

-- Zeitfenster in session_check_state werden nicht mehr gepflegt.
drop trigger if exists set_session_check_state_timing_fields on public.session_check_state;

notify pgrst, 'reload schema';
