-- Migration: Didactic Lernbereich ordering
--
-- When a session contains multiple Lernbereiche from the same Gebiet,
-- those with a higher sort_index start blocked and are unlocked only after
-- all non-excluded checks of all lower-or-equal sort_index Lernbereiche
-- in the same Gebiet have passed the recall step.
--
-- Lernbereiche from different Gebiete always run fully in parallel.
-- Sort index values come from didactic_order in lernbereiche.yml (frontend passes them).
-- If no ordering is configured (gebiet = '' or all sort_index = 0), the behaviour
-- is identical to before this migration.


-- 1. Add sort_index and gebiet to session_lernbereiche
-- -----------------------------------------------------
alter table public.session_lernbereiche
    add column if not exists sort_index integer not null default 0,
    add column if not exists gebiet text not null default '';


-- 2. Drop previous save_active_learning_session signature
-- -------------------------------------------------------
drop function if exists public.save_active_learning_session(text[], text[], integer, text[], date, text);


-- 3. save_active_learning_session (extended with p_lernbereiche_meta)
-- -------------------------------------------------------------------
-- p_lernbereiche_meta: optional JSON array [{slug, gebiet, sort_index}, ...]
-- When provided, sort_index and gebiet are stored in session_lernbereiche and
-- used to block checks / start activities for non-first tiers.
create or replace function public.save_active_learning_session(
    p_lernbereiche text[],
    p_excluded_check_ids text[] default array[]::text[],
    p_tempo_days integer default null,
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
    effective_tempo_days integer;
    default_tempo_days integer := public.get_system_setting_integer('planning.default_session_tempo_days', 3);
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

    if p_tempo_days is not null and p_tempo_days <= 0 then
        raise exception 'tempo_days must be positive';
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

    select id
    into active_session_id
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
        end if;

        return null;
    end if;

    effective_tempo_days := coalesce(p_tempo_days, default_tempo_days);

    if active_session_id is null then
        begin
            insert into public.learning_sessions (
                user_id,
                status,
                tempo_days,
                target_date,
                target_source
            )
            values (
                current_user_id,
                'active',
                effective_tempo_days,
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
        set tempo_days = effective_tempo_days,
            target_date = normalized_target_date,
            target_source = normalized_target_source,
            planning_revision = planning_revision + 1
        where id = active_session_id;

        delete from public.session_check_exclusions
        where session_id = active_session_id;

        delete from public.session_lernbereiche
        where session_id = active_session_id;
    end if;

    -- Insert session_lernbereiche with sort_index and gebiet from meta.
    -- Meta lookup is done via a lateral join; defaults to 0 / '' when absent.
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
            'training_1',
            'due',
            null,
            null
        from unnest(normalized_included_check_ids) as included_checks(included_check_id)
        on conflict (session_id, check_id) do nothing;
    end if;

    -- Block training_1/due checks for non-first Lernbereiche in their Gebiet.
    -- "First" means having the minimum sort_index among all session_lernbereiche
    -- in the same Gebiet. Checks with gebiet = '' are never blocked.
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
      and scs.current_step_key = 'training_1'
      and scs.current_step_status = 'due';

    -- Unblock training_1/blocked checks that now belong to the first tier
    -- (relevant when ordering changes on a re-save).
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
      and scs.current_step_key = 'training_1'
      and scs.current_step_status = 'blocked';

    foreach current_lernbereich_slug in array normalized_lernbereiche loop
        -- Determine start status based on didactic ordering.
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

    return active_session_id;
end;
$$;


-- 4. unlock_successor_lernbereiche
-- ---------------------------------
-- Called internally after a successful recall to check whether the next
-- Lernbereich tier in the same Gebiet can now be unblocked.
--
-- Unlock condition: all non-excluded checks from all session_lernbereiche
-- with the same Gebiet and sort_index <= the current Lernbereich's sort_index
-- have moved past recall (current_step_key NOT IN ('training_1', 'recall'),
-- or are still blocked — meaning they belong to a higher tier themselves,
-- which cannot happen for sort_index <= current by construction).
create or replace function public.unlock_successor_lernbereiche(
    p_session_id uuid,
    p_lernbereich_slug text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    v_gebiet text;
    v_sort_index integer;
    v_next_sort_index integer;
    v_remaining_recalls integer;
begin
    -- Get gebiet and sort_index of the Lernbereich that just had a recall complete.
    select slb.gebiet, slb.sort_index
    into v_gebiet, v_sort_index
    from public.session_lernbereiche slb
    where slb.session_id = p_session_id
      and slb.lernbereich_slug = p_lernbereich_slug;

    -- No ordering configured for this Gebiet — nothing to unlock.
    if v_gebiet is null or v_gebiet = '' then
        return;
    end if;

    -- Count checks still at or before the recall step across all prerequisite
    -- tiers (sort_index <= current) in the same Gebiet.
    -- Excluded checks and checks that are still blocked (= belong to a later tier
    -- that hasn't been unblocked yet, which cannot occur for sort_index <=
    -- v_sort_index) are excluded from the count.
    select count(*)
    into v_remaining_recalls
    from public.session_check_state scs
    join public.session_lernbereiche slb
        on slb.session_id = scs.session_id
        and slb.lernbereich_slug = split_part(scs.check_id, '__', 2)
    where scs.session_id = p_session_id
      and slb.gebiet = v_gebiet
      and slb.sort_index <= v_sort_index
      and scs.current_step_key in ('training_1', 'recall')
      and scs.current_step_status <> 'blocked'
      and not exists (
          select 1
          from public.session_check_exclusions sce
          where sce.session_id = p_session_id
            and sce.check_id = scs.check_id
      );

    -- Still recalls outstanding — do not unlock anything yet.
    if v_remaining_recalls > 0 then
        return;
    end if;

    -- Find the next tier to unlock (minimum sort_index above the current level).
    select min(slb2.sort_index)
    into v_next_sort_index
    from public.session_lernbereiche slb2
    where slb2.session_id = p_session_id
      and slb2.gebiet = v_gebiet
      and slb2.sort_index > v_sort_index;

    -- No further tiers — nothing to unlock.
    if v_next_sort_index is null then
        return;
    end if;

    -- Unlock check states for the next tier.
    update public.session_check_state scs
    set current_step_status = 'due'
    from public.session_lernbereiche slb
    where scs.session_id = p_session_id
      and slb.session_id = p_session_id
      and slb.lernbereich_slug = split_part(scs.check_id, '__', 2)
      and slb.gebiet = v_gebiet
      and slb.sort_index = v_next_sort_index
      and scs.current_step_key = 'training_1'
      and scs.current_step_status = 'blocked';

    -- Unlock start activities for the next tier.
    update public.session_activity_state sas
    set status = 'due',
        due_at = now()
    from public.session_lernbereiche slb
    where sas.session_id = p_session_id
      and slb.session_id = p_session_id
      and slb.lernbereich_slug = sas.lernbereich_slug
      and sas.activity_type = 'start'
      and slb.gebiet = v_gebiet
      and slb.sort_index = v_next_sort_index
      and sas.status = 'blocked';
end;
$$;


-- 5. record_check_module_attempt (extended with unlock call after recall)
-- -----------------------------------------------------------------------
create or replace function public.record_check_module_attempt(
    p_lernbereich_slug text,
    p_check_id text,
    p_module_key text,
    p_outcome_key text
)
returns public.learning_activity_attempts
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    normalized_check_id text := nullif(trim(p_check_id), '');
    normalized_module_key text := lower(coalesce(nullif(trim(p_module_key), ''), ''));
    normalized_outcome_key text := lower(coalesce(nullif(trim(p_outcome_key), ''), ''));
    matched_session_id uuid;
    inserted_attempt public.learning_activity_attempts;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if normalized_check_id is null then
        raise exception 'check_id is required';
    end if;

    if normalized_module_key not in ('recall', 'feynman') then
        raise exception 'Unsupported module_key';
    end if;

    if normalized_outcome_key not in ('can_do', 'repeat') then
        raise exception 'Unsupported outcome_key';
    end if;

    select learning_sessions.id
    into matched_session_id
    from public.learning_sessions
    where learning_sessions.user_id = current_user_id
      and learning_sessions.status = 'active'
      and exists (
          select 1
          from public.session_lernbereiche
          where session_lernbereiche.session_id = learning_sessions.id
            and session_lernbereiche.lernbereich_slug = normalized_lernbereich_slug
      )
      and not exists (
          select 1
          from public.session_check_exclusions
          where session_check_exclusions.session_id = learning_sessions.id
            and session_check_exclusions.check_id = normalized_check_id
      )
    limit 1;

    insert into public.learning_activity_attempts (
        user_id,
        session_id,
        lernbereich_slug,
        check_id,
        module_key,
        outcome_key
    )
    values (
        current_user_id,
        matched_session_id,
        normalized_lernbereich_slug,
        normalized_check_id,
        normalized_module_key,
        normalized_outcome_key
    )
    returning * into inserted_attempt;

    if matched_session_id is not null then
        if normalized_module_key = 'recall' then
            if normalized_outcome_key = 'can_do' then
                update public.session_check_state
                set current_step_key = 'training_2',
                    current_step_status = 'due',
                    last_outcome_key = 'can_do'
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'recall'
                  and current_step_status = 'due';

                -- Check whether this recall completion unlocks the next Lernbereich tier.
                perform public.unlock_successor_lernbereiche(matched_session_id, normalized_lernbereich_slug);
            else
                update public.session_check_state
                set last_outcome_key = 'repeat'
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'recall'
                  and current_step_status = 'due';
            end if;
        elsif normalized_module_key = 'feynman' then
            if normalized_outcome_key = 'can_do' then
                update public.session_check_state
                set current_step_key = 'training_3',
                    current_step_status = 'due',
                    last_outcome_key = 'can_do'
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'feynman'
                  and current_step_status = 'due';
            else
                update public.session_check_state
                set last_outcome_key = 'repeat'
                where session_id = matched_session_id
                  and check_id = normalized_check_id
                  and current_step_key = 'feynman'
                  and current_step_status = 'due';
            end if;
        end if;
    end if;

    return inserted_attempt;
end;
$$;


-- 6. Permissions
-- ---------------
revoke all on function public.save_active_learning_session(text[], text[], integer, text[], date, text, jsonb) from public;
revoke all on function public.unlock_successor_lernbereiche(uuid, text) from public;
revoke all on function public.record_check_module_attempt(text, text, text, text) from public;

grant execute on function public.save_active_learning_session(text[], text[], integer, text[], date, text, jsonb) to authenticated;
-- unlock_successor_lernbereiche is internal (called from record_check_module_attempt); no user grant needed.
grant execute on function public.record_check_module_attempt(text, text, text, text) to authenticated;
