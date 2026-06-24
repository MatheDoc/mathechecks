-- Fix: remove target_source = 'explicit' guard from the deadline-based cap.
-- The G-cap must apply whenever a target_date is set, regardless of how it
-- was derived. With the guard, sessions whose target_source != 'explicit'
-- get pressure_ratio = 1.0 (default) and G = 24h even when the deadline is
-- only hours away.

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

    -- Cap: if the remaining time to the target deadline is shorter than the
    -- G-gap of the currently selected profile, force a shorter profile.
    -- Applied whenever a target_date is set, regardless of target_source.
    if resolved_target_date is not null then
        remaining_hours_to_target := extract(epoch from (
            (resolved_target_date + 1)::timestamp - now()
        )) / 3600.0;

        -- Deadline closer than very_relaxed gap (default 48 h):
        -- must not select very_relaxed → cap below very_relaxed_threshold.
        if remaining_hours_to_target <= gap_very_relaxed_hours then
            pressure_ratio := least(pressure_ratio, very_relaxed_threshold - 0.01);
        end if;

        -- Deadline closer than relaxed gap (default 36 h):
        -- must not select relaxed → cap below relaxed_threshold.
        if remaining_hours_to_target <= gap_relaxed_hours then
            pressure_ratio := least(pressure_ratio, relaxed_threshold - 0.01);
        end if;

        -- Deadline closer than normal gap (default 24 h):
        -- must not select normal → cap below tight_threshold.
        if remaining_hours_to_target <= gap_normal_hours then
            pressure_ratio := least(pressure_ratio, tight_threshold - 0.01);
        end if;
    end if;

    return pressure_ratio;
end;
$$;

notify pgrst, 'reload schema';
