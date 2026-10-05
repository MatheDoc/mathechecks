-- Tagespensum auf den Stand zu Tagesbeginn beziehen: heute bereits erledigte Kernschritte
-- zählen zum Restvolumen dazu, weil replan_session sie anschließend als consumed_today abzieht.
-- Vorher wurden sie doppelt abgezogen (z. B. 43 offen + 2 erledigt -> nur 41 für heute geplant).

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
    consumed_today integer := 0;
    available_day_count integer := 1;
    remaining_activity_count integer := 0;
begin
    if p_session_id is null then
        return null;
    end if;

    select coalesce(resolved_target_date, ls.target_date),
           ls.target_source,
           case
               when ls.daily_core_budget_date = current_date then coalesce(ls.daily_core_budget_used, 0)
               else 0
           end
    into resolved_target_date, resolved_target_source, consumed_today
    from public.learning_sessions ls
    where ls.id = p_session_id;

    if resolved_target_date is null or resolved_target_source is distinct from 'explicit' then
        return null;
    end if;

    remaining_activity_count := public.get_session_remaining_activity_count(p_session_id);

    if remaining_activity_count <= 0 then
        return null;
    end if;

    -- target_date ist der Klausurtag; Vorbereitungstage = target_date - heute.
    available_day_count := greatest((resolved_target_date - current_date), 1);

    return greatest((remaining_activity_count + consumed_today)::numeric / available_day_count::numeric, 0.1);
end;
$$;

do $$
declare
    v_session_id uuid;
begin
    for v_session_id in
        select id from public.learning_sessions where status = 'active'
    loop
        perform public.replan_session(v_session_id);
    end loop;
end;
$$;

notify pgrst, 'reload schema';
