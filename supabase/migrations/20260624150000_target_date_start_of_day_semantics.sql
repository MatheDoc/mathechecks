-- Semantics change: target_date now means the TEST DAY (start of that day).
-- Deadline = target_date 00:00, not end-of-day.
--
-- Before: available_day_count = (target_date - today) + 1  (target day itself counted)
-- After:  available_day_count = (target_date - today)       (target day is the test, not prep)
--
-- Example: test on June 25, today June 24 → 1 prep day (today), not 2.

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
    remaining_activity_count integer := 0;
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

    remaining_activity_count := public.get_session_remaining_activity_count(p_session_id);

    if remaining_activity_count <= 0 then
        return null;
    end if;

    -- target_date is the test/exam day; preparation must finish before it starts.
    -- Remaining prep days = target_date - today (no +1).
    available_day_count := greatest((resolved_target_date - current_date), 1);

    return greatest(remaining_activity_count::numeric / available_day_count::numeric, 0.1);
end;
$$;

-- Also update get_session_pressure_ratio: deadline = start of target_date (no +1).
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
    required_activities_per_day   numeric;
    pressure_ratio                numeric;
    resolved_target_date          date := p_target_date;
    remaining_hours_to_target     numeric;
    tight_threshold        numeric := public.get_system_setting_numeric('feed.pressure_tight_threshold',        0.95);
    relaxed_threshold      numeric := public.get_system_setting_numeric('feed.pressure_relaxed_threshold',      1.20);
    very_relaxed_threshold numeric := public.get_system_setting_numeric('feed.pressure_very_relaxed_threshold', 1.45);
    gap_normal_hours       integer := public.get_system_setting_integer('feed.core_gap_normal_hours',           24);
    gap_relaxed_hours      integer := public.get_system_setting_integer('feed.core_gap_relaxed_hours',          36);
    gap_very_relaxed_hours integer := public.get_system_setting_integer('feed.core_gap_very_relaxed_hours',     48);
begin
    if p_session_id is null then
        return 1.0;
    end if;

    select greatest(coalesce(ls.activities_per_day, public.get_default_activities_per_day()), 0.1),
           coalesce(p_target_date, ls.target_date)
    into configured_activities_per_day, resolved_target_date
    from public.learning_sessions ls
    where ls.id = p_session_id;

    required_activities_per_day := public.get_session_required_activities_per_day(p_session_id, p_target_date);

    if required_activities_per_day is null or required_activities_per_day <= 0 then
        pressure_ratio := 1.0;
    else
        pressure_ratio := greatest(configured_activities_per_day / required_activities_per_day, 0.01);
    end if;

    -- Cap: deadline = start of target_date (00:00), not end-of-day.
    if resolved_target_date is not null then
        remaining_hours_to_target := extract(epoch from (
            resolved_target_date::timestamp - now()
        )) / 3600.0;

        if remaining_hours_to_target <= gap_very_relaxed_hours then
            pressure_ratio := least(pressure_ratio, very_relaxed_threshold - 0.01);
        end if;

        if remaining_hours_to_target <= gap_relaxed_hours then
            pressure_ratio := least(pressure_ratio, relaxed_threshold - 0.01);
        end if;

        if remaining_hours_to_target <= gap_normal_hours then
            pressure_ratio := least(pressure_ratio, tight_threshold - 0.01);
        end if;
    end if;

    return pressure_ratio;
end;
$$;

-- Backfill: re-apply corrected available_from for steps that breach the
-- new (stricter) deadline. Deadline is now start of target_date, not end.
update public.session_check_state scs
set    available_from = scs.last_completed_at
                        + public.get_session_core_gap_interval(scs.session_id)
from   public.learning_sessions ls
where  scs.session_id = ls.id
  and  scs.last_completed_at is not null
  and  scs.available_from    is not null
  and  scs.current_step_status in ('due', 'blocked')
  and  ls.target_date is not null
  and  ls.target_source = 'explicit'
  and  scs.available_from >= ls.target_date::timestamp
  and  scs.last_completed_at + public.get_session_core_gap_interval(scs.session_id)
       < scs.available_from;

notify pgrst, 'reload schema';
