-- Simple rule: if the computed available_from would land past the target
-- date (= test day, start of day), make the step available immediately.
-- This handles "crunch" scenarios where even the minimum G-gap (12h) would
-- push the next step past the deadline.

create or replace function public.apply_session_check_timing_fields()
returns trigger
language plpgsql
set search_path = public
as $$
declare
    core_gap             interval;
    computed_available   timestamptz;
    session_target_date  date;
begin
    if new.current_step_key = 'check_completed' or new.current_step_status = 'completed' then
        new.available_from := null;
        new.planned_from   := null;
        new.overdue_from   := null;
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
            new.overdue_from   := coalesce(new.overdue_from,   old.overdue_from);
            return new;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.available_from is null then

            core_gap           := public.get_session_core_gap_interval(new.session_id);
            computed_available := new.last_completed_at + core_gap;

            -- If the computed slot lands past the target date (start of day),
            -- unlock the step immediately so the user can still attempt it.
            select ls.target_date
            into   session_target_date
            from   public.learning_sessions ls
            where  ls.id = new.session_id;

            if session_target_date is not null
               and computed_available >= session_target_date::timestamp then
                new.available_from := new.last_completed_at;
            else
                new.available_from := computed_available;
            end if;
        end if;

        if tg_op = 'INSERT'
           or new.current_step_key is distinct from old.current_step_key
           or new.last_completed_at is distinct from old.last_completed_at
           or new.overdue_from is null then
            core_gap         := coalesce(core_gap, public.get_session_core_gap_interval(new.session_id));
            new.overdue_from := coalesce(new.available_from, new.last_completed_at + core_gap) + core_gap;
        end if;

        return new;
    end if;

    return new;
end;
$$;

-- Backfill: for steps that were set with a gap past the deadline, unlock now.
update public.session_check_state scs
set    available_from = scs.last_completed_at
from   public.learning_sessions ls
where  scs.session_id         = ls.id
  and  scs.last_completed_at  is not null
  and  scs.available_from     is not null
  and  scs.current_step_status in ('due', 'blocked')
  and  ls.target_date         is not null
  and  scs.available_from     >= ls.target_date::timestamp;

notify pgrst, 'reload schema';
