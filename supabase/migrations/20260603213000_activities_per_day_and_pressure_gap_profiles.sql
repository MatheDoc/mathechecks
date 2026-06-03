alter table public.system_settings
    add column if not exists value_numeric numeric null;

alter table public.system_settings
    alter column value_integer drop not null;

alter table public.system_settings
    drop constraint if exists system_settings_has_value_check;

alter table public.system_settings
    add constraint system_settings_has_value_check
    check (value_integer is not null or value_numeric is not null);

create or replace function public.get_system_setting_numeric(
    p_setting_key text,
    p_default numeric
)
returns numeric
language plpgsql
security definer
stable
set search_path = public
as $$
declare
    normalized_setting_key text := nullif(trim(p_setting_key), '');
    configured_value numeric;
begin
    if normalized_setting_key is null then
        return p_default;
    end if;

    select coalesce(value_numeric, value_integer::numeric)
    into configured_value
    from public.system_settings
    where setting_key = normalized_setting_key;

    return coalesce(configured_value, p_default);
end;
$$;

revoke all on function public.get_system_setting_numeric(text, numeric) from public;
revoke all on function public.get_system_setting_numeric(text, numeric) from anon;
grant execute on function public.get_system_setting_numeric(text, numeric) to authenticated;
grant execute on function public.get_system_setting_numeric(text, numeric) to anon;

update public.system_settings
set value_numeric = coalesce(value_numeric, value_integer::numeric),
    description = 'Legacy-Kompatibilitaetswert fuer die fruehere ganzzahlige Session-Geschwindigkeit; aktive Laufzeit nutzt planning.default_activities_per_day.'
where setting_key = 'planning.default_session_tempo_days';

insert into public.system_settings (setting_key, value_integer, value_numeric, description)
values
    (
        'planning.default_activities_per_day',
        null,
        coalesce(
            (select value_numeric from public.system_settings where setting_key = 'planning.default_session_tempo_days'),
            (select value_integer::numeric from public.system_settings where setting_key = 'planning.default_session_tempo_days'),
            3.0
        ),
        'Standardgeschwindigkeit einer Session in Aktivitaeten pro Tag, wenn keine andere Session-Vorgabe gespeichert ist.'
    ),
    (
        'feed.core_gap_very_tight_hours',
        12,
        12,
        'Didaktischer Basisabstand G fuer sehr engen Druck.'
    ),
    (
        'feed.core_gap_tight_hours',
        18,
        18,
        'Didaktischer Basisabstand G fuer engen Druck.'
    ),
    (
        'feed.core_gap_normal_hours',
        24,
        24,
        'Didaktischer Basisabstand G fuer normales Druckniveau.'
    ),
    (
        'feed.core_gap_relaxed_hours',
        36,
        36,
        'Didaktischer Basisabstand G fuer entspannten Druck.'
    ),
    (
        'feed.core_gap_very_relaxed_hours',
        48,
        48,
        'Didaktischer Basisabstand G fuer sehr entspannten Druck.'
    ),
    (
        'feed.pressure_very_tight_threshold',
        null,
        0.80,
        'Unterhalb dieses Druckverhaeltnisses gilt eine Session als sehr eng.'
    ),
    (
        'feed.pressure_tight_threshold',
        null,
        0.95,
        'Unterhalb dieses Druckverhaeltnisses gilt eine Session als eng.'
    ),
    (
        'feed.pressure_relaxed_threshold',
        null,
        1.20,
        'Ab diesem Druckverhaeltnis gilt eine Session als entspannt.'
    ),
    (
        'feed.pressure_very_relaxed_threshold',
        null,
        1.45,
        'Ab diesem Druckverhaeltnis gilt eine Session als sehr entspannt.'
    ),
    (
        'feed.weight_start',
        null,
        1.0,
        'Gewicht einer offenen Start-Aktivitaet fuer die Druckberechnung.'
    ),
    (
        'feed.weight_training',
        null,
        1.0,
        'Gewicht eines offenen Trainingsschritts fuer die Druckberechnung.'
    ),
    (
        'feed.weight_recall',
        null,
        0.7,
        'Gewicht eines offenen Recall-Schritts fuer die Druckberechnung.'
    ),
    (
        'feed.weight_feynman',
        null,
        1.0,
        'Gewicht eines offenen Feynman-Schritts fuer die Druckberechnung.'
    ),
    (
        'feed.weight_kompetenzliste',
        null,
        0.5,
        'Gewicht eines offenen Kompetenzlisten-Schritts fuer die Druckberechnung.'
    )
on conflict (setting_key) do update
set value_integer = excluded.value_integer,
    value_numeric = excluded.value_numeric,
    description = excluded.description;

do $$
begin
    if exists (
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'learning_sessions'
          and column_name = 'tempo_days'
    ) and not exists (
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'learning_sessions'
          and column_name = 'activities_per_day'
    ) then
        execute 'alter table public.learning_sessions rename column tempo_days to activities_per_day';
    end if;
end;
$$;

alter table public.learning_sessions
    alter column activities_per_day type numeric(6,2)
    using activities_per_day::numeric(6,2);

alter table public.learning_sessions
    alter column activities_per_day set default 1.00;

alter table public.learning_sessions
    drop constraint if exists learning_sessions_tempo_days_check;

alter table public.learning_sessions
    drop constraint if exists learning_sessions_activities_per_day_check;

alter table public.learning_sessions
    add constraint learning_sessions_activities_per_day_check
    check (activities_per_day > 0);

do $$
begin
    if not exists (
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'learning_sessions'
          and column_name = 'tempo_days'
    ) then
        execute '
            alter table public.learning_sessions
            add column tempo_days integer generated always as (
                greatest(ceil(activities_per_day)::integer, 1)
            ) stored
        ';
    end if;
end;
$$;

create or replace function public.get_default_activities_per_day()
returns numeric
language sql
stable
set search_path = public
as $$
    select greatest(public.get_system_setting_numeric('planning.default_activities_per_day', 3.0), 0.1);
$$;

create or replace function public.get_session_required_activities_per_day(
    p_session_id uuid,
    p_target_date date default null
)
returns numeric
language plpgsql
stable
set search_path = public
as $$
declare
    resolved_target_date date := p_target_date;
    resolved_target_source text;
    available_day_count integer := 1;
    open_weight numeric := 0;
begin
    if p_session_id is null then
        return null;
    end if;

        select coalesce(resolved_target_date, ls.target_date),
           ls.target_source
    into resolved_target_date, resolved_target_source
    from public.learning_sessions ls
    where ls.id = p_session_id;

    if resolved_target_date is null or resolved_target_source is distinct from 'explicit' then
        return null;
    end if;

    select
        coalesce(start_items.open_weight, 0)
        + coalesce(check_items.open_weight, 0)
    into open_weight
    from (
        select count(*)::numeric * public.get_system_setting_numeric('feed.weight_start', 1.0) as open_weight
        from public.session_activity_state sas
        where sas.session_id = p_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'
    ) as start_items
    cross join (
        select coalesce(sum(
            case scs.current_step_key
                when 'training' then public.get_system_setting_numeric('feed.weight_training', 1.0)
                when 'recall' then public.get_system_setting_numeric('feed.weight_recall', 0.7)
                when 'feynman' then public.get_system_setting_numeric('feed.weight_feynman', 1.0)
                when 'kompetenzliste_gate' then public.get_system_setting_numeric('feed.weight_kompetenzliste', 0.5)
                else 0::numeric
            end
        ), 0) as open_weight
        from public.session_check_state scs
        where scs.session_id = p_session_id
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
          and scs.current_step_status = 'due'
    ) as check_items;

    if open_weight <= 0 then
        return null;
    end if;

    available_day_count := greatest((resolved_target_date - current_date) + 1, 1);

    return greatest(open_weight / available_day_count::numeric, 0.1);
end;
$$;

create or replace function public.get_session_pressure_ratio(
    p_session_id uuid,
    p_target_date date default null
)
returns numeric
language plpgsql
stable
set search_path = public
as $$
declare
    configured_activities_per_day numeric := public.get_default_activities_per_day();
    required_activities_per_day numeric;
begin
    if p_session_id is null then
        return 1.0;
    end if;

    select greatest(coalesce(ls.activities_per_day, public.get_default_activities_per_day()), 0.1)
    into configured_activities_per_day
    from public.learning_sessions ls
    where ls.id = p_session_id;

    required_activities_per_day := public.get_session_required_activities_per_day(p_session_id, p_target_date);

    if required_activities_per_day is null or required_activities_per_day <= 0 then
        return 1.0;
    end if;

    return greatest(configured_activities_per_day / required_activities_per_day, 0.01);
end;
$$;

create or replace function public.get_session_core_gap_hours(
    p_session_id uuid,
    p_target_date date default null
)
returns integer
language plpgsql
stable
set search_path = public
as $$
declare
    pressure_ratio numeric := public.get_session_pressure_ratio(p_session_id, p_target_date);
    very_tight_threshold numeric := public.get_system_setting_numeric('feed.pressure_very_tight_threshold', 0.80);
    tight_threshold numeric := public.get_system_setting_numeric('feed.pressure_tight_threshold', 0.95);
    relaxed_threshold numeric := public.get_system_setting_numeric('feed.pressure_relaxed_threshold', 1.20);
    very_relaxed_threshold numeric := public.get_system_setting_numeric('feed.pressure_very_relaxed_threshold', 1.45);
begin
    if pressure_ratio < very_tight_threshold then
        return greatest(public.get_system_setting_integer('feed.core_gap_very_tight_hours', 12), 1);
    end if;

    if pressure_ratio < tight_threshold then
        return greatest(public.get_system_setting_integer('feed.core_gap_tight_hours', 18), 1);
    end if;

    if pressure_ratio < relaxed_threshold then
        return greatest(public.get_system_setting_integer('feed.core_gap_normal_hours', 24), 1);
    end if;

    if pressure_ratio < very_relaxed_threshold then
        return greatest(public.get_system_setting_integer('feed.core_gap_relaxed_hours', 36), 1);
    end if;

    return greatest(public.get_system_setting_integer('feed.core_gap_very_relaxed_hours', 48), 1);
end;
$$;

create or replace function public.get_session_core_gap_interval(
    p_session_id uuid,
    p_target_date date default null
)
returns interval
language sql
stable
set search_path = public
as $$
    select make_interval(hours => public.get_session_core_gap_hours(p_session_id, p_target_date));
$$;

create or replace function public.get_core_feed_gap_interval()
returns interval
language sql
stable
set search_path = public
as $$
    select make_interval(hours => greatest(public.get_system_setting_integer('feed.core_gap_normal_hours', 24), 1));
$$;

create or replace function public.apply_session_check_timing_fields()
returns trigger
language plpgsql
set search_path = public
as $$
declare
    core_gap interval := public.get_session_core_gap_interval(new.session_id);
begin
    if new.current_step_key = 'check_completed' or new.current_step_status = 'completed' then
        new.available_from := null;
        new.planned_from := null;
        new.overdue_from := null;
        return new;
    end if;

    if tg_op = 'UPDATE' and new.current_step_key is distinct from old.current_step_key then
        new.planned_from := null;
    end if;

    if new.current_step_key = 'training' then
        new.available_from := coalesce(new.available_from, old.available_from, now());

        if tg_op = 'INSERT' or new.current_step_key is distinct from old.current_step_key then
            new.overdue_from := null;
        end if;

        return new;
    end if;

    if new.current_step_key in ('recall', 'feynman', 'kompetenzliste_gate') then
        if new.last_completed_at is null then
            new.available_from := coalesce(new.available_from, old.available_from, now());
            new.overdue_from := coalesce(new.overdue_from, old.overdue_from);
            return new;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.available_from is null then
            core_gap := public.get_session_core_gap_interval(new.session_id);
            new.available_from := new.last_completed_at + core_gap;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.overdue_from is null then
            core_gap := public.get_session_core_gap_interval(new.session_id);
            new.overdue_from := coalesce(new.available_from, new.last_completed_at + core_gap) + core_gap;
        end if;

        return new;
    end if;

    return new;
end;
$$;

create or replace function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_activities_per_day numeric default null,
    p_included_check_ids text[] default array[]::text[],
    p_target_date date default null,
    p_target_source text default null,
    p_lernbereiche_meta jsonb default null
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
    v_sort_index integer;
    v_gebiet text;
    v_start_status text;
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
                target_source
            )
            values (
                current_user_id,
                'active',
                effective_activities_per_day,
                normalized_target_date,
                normalized_target_source
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
            planning_revision = planning_revision + 1
        where id = active_session_id;

        delete from public.session_check_exclusions
        where session_id = active_session_id;

        delete from public.session_lernbereiche
        where session_id = active_session_id;

        perform public.clear_current_feed_cursor(active_session_id);
    end if;

    insert into public.session_lernbereiche (session_id, lernbereich_slug, sort_index, gebiet)
    select
        active_session_id,
        lb.slug,
        coalesce((meta_elem.val->>'sort_index')::integer, 0),
        coalesce(nullif(trim(meta_elem.val->>'gebiet'), ''), '')
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
            'due',
            null,
            null
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    update public.session_check_state scs
    set current_step_status = 'blocked'
    from public.session_lernbereiche slb
    where scs.session_id = active_session_id
      and slb.session_id = active_session_id
      and slb.lernbereich_slug = split_part(scs.check_id, '__', 2)
      and slb.gebiet <> ''
      and slb.sort_index > (
          select min(slb2.sort_index)
          from public.session_lernbereiche slb2
          where slb2.session_id = active_session_id
            and slb2.gebiet = slb.gebiet
      )
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'due';

    update public.session_check_state scs
    set current_step_status = 'due'
    from public.session_lernbereiche slb
    where scs.session_id = active_session_id
      and slb.session_id = active_session_id
      and slb.lernbereich_slug = split_part(scs.check_id, '__', 2)
      and (
          slb.gebiet = ''
          or slb.sort_index = (
              select min(slb2.sort_index)
              from public.session_lernbereiche slb2
              where slb2.session_id = active_session_id
                and slb2.gebiet = slb.gebiet
          )
      )
      and scs.current_step_key = 'training'
      and scs.current_step_status = 'blocked';

    foreach current_lernbereich_slug in array normalized_lernbereiche loop
        select slb.sort_index, slb.gebiet
        into v_sort_index, v_gebiet
        from public.session_lernbereiche slb
        where slb.session_id = active_session_id
          and slb.lernbereich_slug = current_lernbereich_slug;

        if v_gebiet is null or v_gebiet = '' then
            v_start_status := 'due';
        elsif v_sort_index = (
            select min(slb2.sort_index)
            from public.session_lernbereiche slb2
            where slb2.session_id = active_session_id
              and slb2.gebiet = v_gebiet
        ) then
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

    perform public.replan_session(active_session_id);

    return active_session_id;
end;
$$;

drop function if exists public.save_active_learning_session(text[], text[], integer, text[], date, text, jsonb);

revoke all on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb) from public;
revoke all on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb) from anon;
grant execute on function public.save_active_learning_session(text[], text[], numeric, text[], date, text, jsonb) to authenticated;

create or replace function public.replan_session(p_session_id uuid default null)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    resolved_session_id uuid := p_session_id;
    resolved_target_date date := current_date;
    configured_activities_per_day numeric := public.get_default_activities_per_day();
    required_activities_per_day numeric := null;
    planning_activities_per_day numeric := 1.0;
    remaining_today_item_capacity integer := 0;
    consumed_today_core_items integer := 0;
    core_gap interval := public.get_session_core_gap_interval(resolved_session_id);
begin
    if resolved_session_id is null then
        if current_user_id is null then
            return null;
        end if;

        select id
        into resolved_session_id
        from public.learning_sessions
        where user_id = current_user_id
          and status = 'active'
        order by started_at desc
        limit 1
        for update;
    elsif current_user_id is null then
        perform 1
        from public.learning_sessions
        where id = resolved_session_id
          and status = 'active'
        for update;

        if not found then
            return null;
        end if;
    else
        perform 1
        from public.learning_sessions
        where id = resolved_session_id
          and user_id = current_user_id
          and status = 'active'
        for update;

        if not found then
            raise exception 'No active learning session found';
        end if;
    end if;

    if resolved_session_id is null then
        return null;
    end if;

    select coalesce(ls.target_date, current_date),
           greatest(coalesce(ls.activities_per_day, public.get_default_activities_per_day()), 0.1),
           case
               when ls.daily_core_budget_date = current_date then coalesce(ls.daily_core_budget_used, 0)
               else 0
           end
    into resolved_target_date, configured_activities_per_day, consumed_today_core_items
    from public.learning_sessions ls
    where ls.id = resolved_session_id;

    required_activities_per_day := public.get_session_required_activities_per_day(resolved_session_id, resolved_target_date);
    planning_activities_per_day := greatest(configured_activities_per_day, coalesce(required_activities_per_day, configured_activities_per_day), 0.1);
    remaining_today_item_capacity := greatest(floor(planning_activities_per_day - consumed_today_core_items)::integer, 0);
    core_gap := public.get_session_core_gap_interval(resolved_session_id, resolved_target_date);

    with open_core_items as (
        select
            'check'::text as item_kind,
            'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
            public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
            scs.check_id,
            scs.current_step_key as step_key,
            coalesce(slb.sort_index, 0) as lernbereich_sort_index,
            coalesce(nullif(trim(slb.gebiet), ''), public.check_id_lernbereich_slug(scs.check_id), '') as gebiet_key,
            public.feed_step_depth_rank(scs.current_step_key) as step_depth,
            public.feed_check_sequence_number(scs.check_id) as check_order,
            coalesce(scs.available_from, now()) as available_from
        from public.session_check_state scs
        left join public.session_lernbereiche slb
          on slb.session_id = scs.session_id
         and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
        where scs.session_id = resolved_session_id
          and scs.current_step_status = 'due'
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')

        union all

        select
            'start'::text as item_kind,
            sas.activity_key,
            sas.lernbereich_slug,
            null::text as check_id,
            'start'::text as step_key,
            coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
            coalesce(nullif(trim(slb.gebiet), ''), sas.lernbereich_slug, '') as gebiet_key,
            0 as step_depth,
            0 as check_order,
            coalesce(sas.due_at, now()) as available_from
        from public.session_activity_state sas
        left join public.session_lernbereiche slb
          on slb.session_id = sas.session_id
         and slb.lernbereich_slug = sas.lernbereich_slug
        where sas.session_id = resolved_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'
    ), ranked_core_items as (
        select
            item_kind,
            activity_key,
            lernbereich_slug,
            check_id,
            step_key,
            row_number() over (
                order by
                    case when item_kind = 'start' then 0 else 1 end,
                    available_from,
                    step_depth desc,
                    gebiet_key,
                    lernbereich_sort_index,
                    check_order,
                    activity_key
            ) as row_number_in_plan
        from open_core_items
    ), scheduled_core_items as (
        select
            item_kind,
            activity_key,
            lernbereich_slug,
            check_id,
            step_key,
            case
                when remaining_today_item_capacity > 0 and row_number_in_plan <= remaining_today_item_capacity then now()
                else date_trunc('day', now())
                    + make_interval(days => greatest(ceil((greatest(row_number_in_plan - remaining_today_item_capacity, 0))::numeric / planning_activities_per_day), 1)::integer)
            end as scheduled_from
        from ranked_core_items
    )
    update public.session_check_state scs
    set planned_from = scheduled_core_items.scheduled_from,
        overdue_from = case
            when scs.current_step_key = 'training' then (
                case
                    when scs.available_from is null then scheduled_core_items.scheduled_from
                    when scheduled_core_items.scheduled_from is null then scs.available_from
                    else greatest(scs.available_from, scheduled_core_items.scheduled_from)
                end
            ) + core_gap
            else scs.overdue_from
        end
    from scheduled_core_items
    where scheduled_core_items.item_kind = 'check'
      and scs.session_id = resolved_session_id
      and scs.check_id = scheduled_core_items.check_id
      and scs.current_step_key = scheduled_core_items.step_key
      and (
          scs.planned_from is distinct from scheduled_core_items.scheduled_from
          or (
              scs.current_step_key = 'training'
              and scs.overdue_from is distinct from (
                  case
                      when scs.available_from is null then scheduled_core_items.scheduled_from
                      when scheduled_core_items.scheduled_from is null then scs.available_from
                      else greatest(scs.available_from, scheduled_core_items.scheduled_from)
                  end
              ) + core_gap
          )
      );

    with open_core_items as (
        select
            'start'::text as item_kind,
            sas.activity_key,
            sas.lernbereich_slug,
            null::text as check_id,
            'start'::text as step_key,
            coalesce(slb.sort_index, sas.sort_index, 0) as lernbereich_sort_index,
            coalesce(nullif(trim(slb.gebiet), ''), sas.lernbereich_slug, '') as gebiet_key,
            0 as step_depth,
            0 as check_order,
            coalesce(sas.due_at, now()) as available_from
        from public.session_activity_state sas
        left join public.session_lernbereiche slb
          on slb.session_id = sas.session_id
         and slb.lernbereich_slug = sas.lernbereich_slug
        where sas.session_id = resolved_session_id
          and sas.activity_type = 'start'
          and sas.status = 'due'

        union all

        select
            'check'::text as item_kind,
            'check:' || scs.check_id || ':' || scs.current_step_key as activity_key,
            public.check_id_lernbereich_slug(scs.check_id) as lernbereich_slug,
            scs.check_id,
            scs.current_step_key,
            coalesce(slb.sort_index, 0) as lernbereich_sort_index,
            coalesce(nullif(trim(slb.gebiet), ''), public.check_id_lernbereich_slug(scs.check_id), '') as gebiet_key,
            public.feed_step_depth_rank(scs.current_step_key) as step_depth,
            public.feed_check_sequence_number(scs.check_id) as check_order,
            coalesce(scs.available_from, now()) as available_from
        from public.session_check_state scs
        left join public.session_lernbereiche slb
          on slb.session_id = scs.session_id
         and slb.lernbereich_slug = public.check_id_lernbereich_slug(scs.check_id)
        where scs.session_id = resolved_session_id
          and scs.current_step_status = 'due'
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
    ), ranked_core_items as (
        select
            item_kind,
            activity_key,
            row_number() over (
                order by
                    case when item_kind = 'start' then 0 else 1 end,
                    available_from,
                    step_depth desc,
                    gebiet_key,
                    lernbereich_sort_index,
                    check_order,
                    activity_key
            ) as row_number_in_plan
        from open_core_items
    ), scheduled_core_items as (
        select
            item_kind,
            activity_key,
            case
                when remaining_today_item_capacity > 0 and row_number_in_plan <= remaining_today_item_capacity then now()
                else date_trunc('day', now())
                    + make_interval(days => greatest(ceil((greatest(row_number_in_plan - remaining_today_item_capacity, 0))::numeric / planning_activities_per_day), 1)::integer)
            end as scheduled_from
        from ranked_core_items
    )
    update public.session_activity_state sas
    set planned_from = scheduled_core_items.scheduled_from,
        overdue_from = (
            case
                when sas.due_at is null then scheduled_core_items.scheduled_from
                when scheduled_core_items.scheduled_from is null then sas.due_at
                else greatest(sas.due_at, scheduled_core_items.scheduled_from)
            end
        ) + core_gap
    from scheduled_core_items
    where sas.session_id = resolved_session_id
      and scheduled_core_items.item_kind = 'start'
      and sas.activity_key = scheduled_core_items.activity_key
      and (
          sas.planned_from is distinct from scheduled_core_items.scheduled_from
          or sas.overdue_from is distinct from (
              case
                  when sas.due_at is null then scheduled_core_items.scheduled_from
                  when scheduled_core_items.scheduled_from is null then sas.due_at
                  else greatest(sas.due_at, scheduled_core_items.scheduled_from)
              end
          ) + core_gap
      );

    update public.session_check_state
    set planned_from = null,
        overdue_from = case
            when current_step_key = 'training' then overdue_from
            when current_step_key in ('recall', 'feynman', 'kompetenzliste_gate') then overdue_from
            else null
        end
    where session_id = resolved_session_id
      and current_step_status <> 'due'
      and planned_from is not null;

    update public.session_activity_state
    set planned_from = null,
        overdue_from = null
    where session_id = resolved_session_id
      and activity_type = 'start'
      and status <> 'due'
      and (
          planned_from is not null
          or overdue_from is not null
      );

    return resolved_session_id;
end;
$$;