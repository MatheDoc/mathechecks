-- Session-Name + Teilen von Session-Konfigurationen per Link.
-- 1) learning_sessions.name (frei waehlbar, kein Uniqueness-Constraint)
-- 2) save_active_learning_session(...) bekommt p_name (Signatur-Wechsel -> drop + create)
-- 3) shared_sessions: Zugriff ausschliesslich ueber RPCs (keine Policies -> kein Listing)

alter table public.learning_sessions
    add column if not exists name text null;

alter table public.learning_sessions
    drop constraint if exists learning_sessions_name_length_check;

alter table public.learning_sessions
    add constraint learning_sessions_name_length_check
    check (name is null or char_length(name) <= 80);

drop function if exists public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb);
create function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_activities_per_day numeric default null,
    p_included_check_ids text[] default array[]::text[],
    p_target_date date default null,
    p_target_source text default null,
    p_lernbereiche_meta jsonb default null,
    p_name text default null
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    active_session_id uuid;
    current_activities_per_day numeric;
    effective_activities_per_day numeric;
    default_activities_per_day numeric := public.get_default_activities_per_day();
    normalized_lernbereiche text[];
    normalized_excluded_check_ids text[];
    normalized_included_check_ids text[];
    normalized_target_date date := p_target_date;
    normalized_target_source text := nullif(trim(coalesce(p_target_source, '')), '');
    current_lernbereich_slug text;
    v_start_status text;
    normalized_name text := left(nullif(trim(coalesce(p_name, '')), ''), 80);
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if p_activities_per_day is not null and p_activities_per_day <= 0 then
        raise exception 'activities_per_day must be positive';
    end if;

    if normalized_target_date is not null and normalized_target_date < current_date then
        raise exception 'target_date must be today or later';
    end if;

    if normalized_target_date is null then
        normalized_target_source := null;
    elsif normalized_target_source is null then
        normalized_target_source := 'explicit';
    elsif normalized_target_source not in ('explicit', 'suggested') then
        raise exception 'unsupported target_source';
    end if;

    select id, activities_per_day
    into active_session_id, current_activities_per_day
    from public.learning_sessions
    where user_id = current_user_id
      and status = 'active'
    for update;

    normalized_lernbereiche := array(
        select distinct slug
        from (
            select nullif(trim(lb.value), '') as slug
            from unnest(coalesce(p_lernbereiche, array[]::text[])) as lb(value)
        ) normalized
        where slug is not null
    );

    normalized_excluded_check_ids := array(
        select distinct check_id
        from (
            select nullif(trim(excluded.value), '') as check_id
            from unnest(coalesce(p_excluded_check_ids, array[]::text[])) as excluded(value)
        ) normalized
        where check_id is not null
    );

    normalized_included_check_ids := array(
        select distinct check_id
        from (
            select nullif(trim(included.value), '') as check_id
            from unnest(coalesce(p_included_check_ids, array[]::text[])) as included(value)
        ) normalized
        where check_id is not null
    );

    if coalesce(array_length(normalized_lernbereiche, 1), 0) = 0 then
        if active_session_id is not null then
            update public.learning_sessions
            set status = 'aborted',
                ended_at = coalesce(ended_at, now())
            where id = active_session_id
              and status = 'active';

            delete from public.session_feed_cursor
            where session_id = active_session_id;
        end if;

        return null;
    end if;

    effective_activities_per_day := round(greatest(coalesce(p_activities_per_day, current_activities_per_day, default_activities_per_day), 0.1), 2);

    if active_session_id is null then
        begin
            insert into public.learning_sessions (
                user_id,
                status,
                activities_per_day,
                target_date,
                target_source,
                name
            )
            values (
                current_user_id,
                'active',
                effective_activities_per_day,
                normalized_target_date,
                normalized_target_source,
                normalized_name
            )
            returning id into active_session_id;
        exception
            when unique_violation then
                raise exception 'An active learning session already exists';
        end;
    else
        update public.learning_sessions
        set activities_per_day = effective_activities_per_day,
            target_date = normalized_target_date,
            target_source = normalized_target_source,
            name = coalesce(normalized_name, name),
            planning_revision = planning_revision + 1
        where id = active_session_id;

        delete from public.session_check_exclusions
        where session_id = active_session_id;

        delete from public.session_lernbereiche
        where session_id = active_session_id;

        perform public.clear_current_feed_cursor(active_session_id);
    end if;

    insert into public.session_lernbereiche (session_id, lernbereich_slug, sort_index, gebiet, gebiet_order)
    select
        active_session_id,
        lb.slug,
        coalesce((meta_elem.val->>'sort_index')::integer, 0),
        coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), ''),
        coalesce(
            (meta_elem.val->>'gebiet_order')::integer,
            case coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), '')
                when 'analysis' then 1
                when 'stochastik' then 2
                when 'lineare-algebra' then 3
                else 0
            end
        )
    from unnest(normalized_lernbereiche) as lb(slug)
    left join lateral (
        select elem as val
        from jsonb_array_elements(coalesce(p_lernbereiche_meta, '[]'::jsonb)) as elem
        where elem->>'slug' = lb.slug
        limit 1
    ) as meta_elem on true;

    if coalesce(array_length(normalized_excluded_check_ids, 1), 0) > 0 then
        insert into public.session_check_exclusions (session_id, check_id)
        select active_session_id, check_id
        from unnest(normalized_excluded_check_ids) as excluded_checks(check_id);
    end if;

    delete from public.session_check_state
    where session_id = active_session_id
      and not (check_id = any(coalesce(normalized_included_check_ids, array[]::text[])));

    delete from public.session_flashcard_card_state
    where session_id = active_session_id
      and not (check_id = any(coalesce(normalized_included_check_ids, array[]::text[])));

    delete from public.session_flashcard_rounds
    where session_id = active_session_id
      and exists (
          select 1
          from public.session_flashcard_round_cards
          where session_flashcard_round_cards.round_id = session_flashcard_rounds.id
            and not (session_flashcard_round_cards.check_id = any(coalesce(normalized_included_check_ids, array[]::text[])))
      );

    delete from public.session_activity_state as activity
    where activity.session_id = active_session_id
      and activity.scope_type = 'lernbereich'
      and activity.activity_type in ('flashcards', 'start')
      and not (activity.lernbereich_slug = any(coalesce(normalized_lernbereiche, array[]::text[])));

    if coalesce(array_length(normalized_included_check_ids, 1), 0) > 0 then
        insert into public.session_check_state (
            session_id,
            check_id,
            current_step_key,
            current_step_status,
            last_outcome_key,
            last_completed_at
        )
        select
            active_session_id,
            included_check_id,
            'training',
            'blocked',
            null,
            null
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    foreach current_lernbereich_slug in array normalized_lernbereiche loop
        if public.is_lernbereich_start_ready(active_session_id, current_lernbereich_slug) then
            v_start_status := 'due';
        else
            v_start_status := 'blocked';
        end if;

        insert into public.session_activity_state (
            session_id,
            activity_key,
            activity_type,
            scope_type,
            lernbereich_slug,
            target_module_key,
            status,
            due_at,
            sort_bucket,
            sort_index,
            last_outcome_key
        )
        values (
            active_session_id,
            'lernbereich:' || current_lernbereich_slug || ':start',
            'start',
            'lernbereich',
            current_lernbereich_slug,
            'start',
            v_start_status,
            now(),
            5,
            0,
            null
        )
        on conflict (session_id, activity_key) do update
            set status = case
                    when session_activity_state.status = 'completed' then 'completed'
                    else excluded.status
                end,
                due_at = case
                    when session_activity_state.status = 'completed' then session_activity_state.due_at
                    else excluded.due_at
                end;

        perform public.refresh_flashcard_activity_for_lernbereich(active_session_id, current_lernbereich_slug);
    end loop;

    update public.session_check_state scs
    set current_step_status = 'blocked'
    from public.session_activity_state sas
    where scs.session_id = active_session_id
      and sas.session_id = active_session_id
      and sas.activity_type = 'start'
      and sas.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
      and sas.status <> 'completed'
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'due';

    update public.session_check_state scs
    set current_step_status = 'due',
        available_from = now(),
        planned_from = null,
        overdue_from = null
    from public.session_activity_state sas
    where scs.session_id = active_session_id
      and sas.session_id = active_session_id
      and sas.activity_type = 'start'
      and sas.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
      and sas.status = 'completed'
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'blocked';

    perform public.replan_session(active_session_id);

    return active_session_id;
end;
$$;

revoke all on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb, text) from public;
revoke all on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb, text) from anon;
grant execute on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb, text) to authenticated;

-- ─── Geteilte Session-Konfigurationen ──────────────────────────────────────

insert into public.system_settings (setting_key, value_integer, description)
values
    ('share_session.daily_request_limit', 30, 'Session teilen: maximale Anzahl erzeugter Teilen-Links pro Nutzer und Tag.')
on conflict (setting_key) do nothing;

create table if not exists public.shared_sessions (
    id text primary key check (id ~ '^[A-Za-z0-9]{8}$'),
    config_json jsonb not null,
    created_at timestamptz not null default now()
);

alter table public.shared_sessions enable row level security;
-- Bewusst keine Policies: Lesen nur per Code ueber get_shared_session(...), kein Listing.
revoke all on table public.shared_sessions from anon, authenticated;

create or replace function public.create_shared_session(
    p_name text,
    p_target_date date default null,
    p_check_ids text[] default array[]::text[]
)
returns text
language plpgsql
security definer
set search_path = public
as $$
declare
    v_alphabet constant text := '23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ';
    v_name text := left(nullif(trim(coalesce(p_name, '')), ''), 80);
    v_check_ids text[];
    v_config jsonb;
    v_rate jsonb;
    v_bytes bytea;
    v_code text;
begin
    if auth.uid() is null then
        raise exception 'Authentication required';
    end if;

    v_check_ids := array(
        select distinct check_id
        from (
            select nullif(trim(raw.value), '') as check_id
            from unnest(coalesce(p_check_ids, array[]::text[])) as raw(value)
        ) normalized
        where check_id is not null
        order by check_id
    );

    if coalesce(array_length(v_check_ids, 1), 0) = 0 then
        raise exception 'check_ids must not be empty';
    end if;

    if array_length(v_check_ids, 1) > 500
        or exists (select 1 from unnest(v_check_ids) as c(value) where c.value !~ '^[A-Za-z0-9_-]{1,120}$') then
        raise exception 'invalid check_ids';
    end if;

    v_rate := public.consume_ai_rate_limit('share_session');
    if not coalesce((v_rate->>'allowed')::boolean, false) then
        raise exception 'share rate limit exceeded';
    end if;

    v_config := jsonb_build_object(
        'name', coalesce(v_name, 'Meine Session'),
        'zieldatum', p_target_date,
        'check_ids', to_jsonb(v_check_ids)
    );

    for v_attempt in 1..5 loop
        v_bytes := extensions.gen_random_bytes(8);
        v_code := '';
        for v_index in 0..7 loop
            v_code := v_code || substr(v_alphabet, (get_byte(v_bytes, v_index) % length(v_alphabet)) + 1, 1);
        end loop;

        begin
            insert into public.shared_sessions (id, config_json)
            values (v_code, v_config);
            return v_code;
        exception
            when unique_violation then
                null;
        end;
    end loop;

    raise exception 'could not allocate share code';
end;
$$;

revoke all on function public.create_shared_session(text, date, text[]) from public;
revoke all on function public.create_shared_session(text, date, text[]) from anon;
grant execute on function public.create_shared_session(text, date, text[]) to authenticated;

create or replace function public.get_shared_session(p_code text)
returns jsonb
language sql
stable
security definer
set search_path = public
as $$
    select s.config_json
    from public.shared_sessions s
    where p_code ~ '^[A-Za-z0-9]{8}$'
      and s.id = p_code;
$$;

revoke all on function public.get_shared_session(text) from public;
grant execute on function public.get_shared_session(text) to anon, authenticated;
