-- Add the missing very_tight cap level to get_session_pressure_ratio.
-- Without it, when remaining time <= gap_tight_hours (18h), the function
-- still returns tight profile (G=18h) even though only very_tight (G=12h)
-- would fit within the remaining window.

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
    very_tight_threshold   numeric := public.get_system_setting_numeric('feed.pressure_very_tight_threshold',   0.80);
    tight_threshold        numeric := public.get_system_setting_numeric('feed.pressure_tight_threshold',        0.95);
    relaxed_threshold      numeric := public.get_system_setting_numeric('feed.pressure_relaxed_threshold',      1.20);
    very_relaxed_threshold numeric := public.get_system_setting_numeric('feed.pressure_very_relaxed_threshold', 1.45);
    gap_very_tight_hours   integer := public.get_system_setting_integer('feed.core_gap_very_tight_hours',       12);
    gap_tight_hours        integer := public.get_system_setting_integer('feed.core_gap_tight_hours',            18);
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

    -- Deadline cap: prevent selecting a G-profile whose gap exceeds the
    -- remaining time to the target date (start of that day = 00:00).
    -- All five profile levels are covered so no level is skipped.
    if resolved_target_date is not null then
        remaining_hours_to_target := extract(epoch from (
            resolved_target_date::timestamp - now()
        )) / 3600.0;

        -- remaining <= 48h: must not use very_relaxed (G=48h)
        if remaining_hours_to_target <= gap_very_relaxed_hours then
            pressure_ratio := least(pressure_ratio, very_relaxed_threshold - 0.01);
        end if;

        -- remaining <= 36h: must not use relaxed (G=36h)
        if remaining_hours_to_target <= gap_relaxed_hours then
            pressure_ratio := least(pressure_ratio, relaxed_threshold - 0.01);
        end if;

        -- remaining <= 24h: must not use normal (G=24h)
        if remaining_hours_to_target <= gap_normal_hours then
            pressure_ratio := least(pressure_ratio, tight_threshold - 0.01);
        end if;

        -- remaining <= 18h: must not use tight (G=18h) — was missing before
        if remaining_hours_to_target <= gap_tight_hours then
            pressure_ratio := least(pressure_ratio, very_tight_threshold - 0.01);
        end if;
    end if;

    return pressure_ratio;
end;
$$;

-- Re-run backfill with the corrected function for all steps that still land
-- past the target deadline.
update public.session_check_state scs
set    available_from = scs.last_completed_at
                        + public.get_session_core_gap_interval(scs.session_id)
from   public.learning_sessions ls
where  scs.session_id = ls.id
  and  scs.last_completed_at is not null
  and  scs.available_from    is not null
  and  scs.current_step_status in ('due', 'blocked')
  and  ls.target_date is not null
  and  scs.available_from >= ls.target_date::timestamp
  and  scs.last_completed_at + public.get_session_core_gap_interval(scs.session_id)
       < scs.available_from;

notify pgrst, 'reload schema';
