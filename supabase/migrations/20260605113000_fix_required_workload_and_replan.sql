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
    weight_start numeric := public.get_system_setting_numeric('feed.weight_start', 1.0);
    weight_training numeric := public.get_system_setting_numeric('feed.weight_training', 1.0);
    weight_recall numeric := public.get_system_setting_numeric('feed.weight_recall', 0.7);
    weight_feynman numeric := public.get_system_setting_numeric('feed.weight_feynman', 1.0);
    weight_kompetenzliste numeric := public.get_system_setting_numeric('feed.weight_kompetenzliste', 0.5);
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
        select count(*)::numeric * weight_start as open_weight
        from public.session_activity_state sas
        where sas.session_id = p_session_id
          and sas.activity_type = 'start'
          and sas.status in ('due', 'blocked')
    ) as start_items
    cross join (
        select coalesce(sum(
            case scs.current_step_key
                when 'training' then weight_training + weight_recall + weight_feynman + weight_kompetenzliste
                when 'recall' then weight_recall + weight_feynman + weight_kompetenzliste
                when 'feynman' then weight_feynman + weight_kompetenzliste
                when 'kompetenzliste_gate' then weight_kompetenzliste
                else 0::numeric
            end
        ), 0) as open_weight
        from public.session_check_state scs
        where scs.session_id = p_session_id
          and scs.current_step_key in ('training', 'recall', 'feynman', 'kompetenzliste_gate')
          and scs.current_step_status in ('due', 'blocked')
    ) as check_items;

    if open_weight <= 0 then
        return null;
    end if;

    available_day_count := greatest((resolved_target_date - current_date) + 1, 1);

    return greatest(open_weight / available_day_count::numeric, 0.1);
end;
$$;

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
            coalesce(slb.gebiet_order, 0) as gebiet_order,
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
            coalesce(slb.gebiet_order, 0) as gebiet_order,
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
                    gebiet_order,
                    lernbereich_sort_index,
                    gebiet_key,
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
            coalesce(slb.gebiet_order, 0) as gebiet_order,
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
            coalesce(slb.gebiet_order, 0) as gebiet_order,
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
                    gebiet_order,
                    lernbereich_sort_index,
                    gebiet_key,
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

notify pgrst, 'reload schema';