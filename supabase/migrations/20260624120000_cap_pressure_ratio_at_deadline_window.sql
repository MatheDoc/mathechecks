-- Fix: cap the pressure ratio so that the chosen G-profile stays within
-- the remaining time window when an explicit target date is set.
--
-- Problem: with activities_per_day=2 and few remaining steps, the ratio
-- p = apd / required_apd can be very large (e.g. 4.0), selecting the
-- "very relaxed" G = 48h. If the target deadline is only 33h away,
-- available_from lands beyond the target date despite the session being
-- flagged "Realistisch" by count-based math.
--
-- Fix: after computing the raw pressure ratio, cap it so that any G-profile
-- whose gap exceeds the remaining hours to target is not selected.
-- G profiles (system defaults): normal=24h, relaxed=36h, very_relaxed=48h.

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
    resolved_target_source        text;
    remaining_hours_to_target     numeric;
    very_tight_threshold   numeric := public.get_system_setting_numeric('feed.pressure_very_tight_threshold',   0.80);
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
           coalesce(p_target_date, ls.target_date),
           ls.target_source
    into configured_activities_per_day, resolved_target_date, resolved_target_source
    from public.learning_sessions ls
    where ls.id = p_session_id;

    required_activities_per_day := public.get_session_required_activities_per_day(p_session_id, p_target_date);

    if required_activities_per_day is null or required_activities_per_day <= 0 then
        pressure_ratio := 1.0;
    else
        pressure_ratio := greatest(configured_activities_per_day / required_activities_per_day, 0.01);
    end if;

    -- When an explicit target date is set, prevent a G-profile from being
    -- selected whose gap would push available_from beyond the deadline.
    -- remaining_hours_to_target is the time from now to the end of the target day.
    if resolved_target_date is not null and resolved_target_source = 'explicit' then
        remaining_hours_to_target := extract(epoch from (
            (resolved_target_date + 1)::timestamp - now()
        )) / 3600.0;

        -- If deadline is closer than very_relaxed gap (default 48h),
        -- the very_relaxed profile must not be chosen.
        if remaining_hours_to_target <= gap_very_relaxed_hours then
            pressure_ratio := least(pressure_ratio, very_relaxed_threshold - 0.01);
        end if;

        -- If deadline is closer than relaxed gap (default 36h),
        -- the relaxed profile must not be chosen either.
        if remaining_hours_to_target <= gap_relaxed_hours then
            pressure_ratio := least(pressure_ratio, relaxed_threshold - 0.01);
        end if;

        -- If deadline is closer than normal gap (default 24h),
        -- force tight or very tight profile.
        if remaining_hours_to_target <= gap_normal_hours then
            pressure_ratio := least(pressure_ratio, tight_threshold - 0.01);
        end if;
    end if;

    return pressure_ratio;
end;
$$;

notify pgrst, 'reload schema';
