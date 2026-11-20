-- Lernbereich Hypothesentests: 7 Checks -> 3 Checks.
--   alt 01 + 02 (E-Regel anwenden, links/rechts)        -> neu 01
--   alt 03 + 04 (E-Regel herleiten mit Strukturhilfe)   -> gestrichen
--   alt 05 + 06 (E-Regel herleiten ohne Strukturhilfe)  -> neu 02
--   alt 07      (p oder n aus Fehler-Wkt)               -> neu 03
--
-- Pragmatische Behandlung der Nutzerdaten:
--   * Check-Fortschritt (session_check_state): Pro Session und neuem Check gewinnt der
--     am weitesten fortgeschrittene Stand der Quell-Checks; Zeilen gestrichener Checks entfallen.
--   * Historie (user_activity_events, learning_activity_attempts, user_xp_awards) bleibt erhalten,
--     bekommt aber eindeutige Alt-IDs (stochastik__hypothesentests__alt0N). Damit bleiben XP-Summen
--     exakt gleich, und alte Quoten werden nicht falschen neuen Checks zugeordnet. Der Client
--     ignoriert unbekannte check_ids.
--   * Lernkarten-Zustände (Session + Retention) des Lernbereichs werden zurückgesetzt,
--     da sich Karten und Tipps geändert haben.
--   * Ausschlüsse, Feed-Cursor, Deferrals und geteilte Sessions werden auf die neuen IDs umgestellt.

create temporary table hyp_check_map (
    old_id text primary key,
    new_id text null
);

insert into hyp_check_map (old_id, new_id) values
    ('stochastik__hypothesentests__01', 'stochastik__hypothesentests__01'),
    ('stochastik__hypothesentests__02', 'stochastik__hypothesentests__01'),
    ('stochastik__hypothesentests__03', null),
    ('stochastik__hypothesentests__04', null),
    ('stochastik__hypothesentests__05', 'stochastik__hypothesentests__02'),
    ('stochastik__hypothesentests__06', 'stochastik__hypothesentests__02'),
    ('stochastik__hypothesentests__07', 'stochastik__hypothesentests__03');

-- 1. Historie auf eindeutige Alt-IDs umschlüsseln -------------------------------------------

update public.user_activity_events
set check_id = 'stochastik__hypothesentests__alt' || right(check_id, 2)
where check_id in (select old_id from hyp_check_map);

update public.learning_activity_attempts
set check_id = 'stochastik__hypothesentests__alt' || right(check_id, 2)
where check_id in (select old_id from hyp_check_map);

update public.user_xp_awards
set check_id = 'stochastik__hypothesentests__alt' || right(check_id, 2)
where check_id in (select old_id from hyp_check_map);

-- 2. Check-Fortschritt zusammenführen -------------------------------------------------------

create temporary table hyp_state_winner as
select distinct on (scs.session_id, m.new_id)
    scs.session_id,
    scs.check_id as old_id,
    m.new_id
from public.session_check_state scs
join hyp_check_map m on m.old_id = scs.check_id
where m.new_id is not null
order by
    scs.session_id,
    m.new_id,
    case scs.current_step_key
        when 'check_completed' then 5
        when 'test' then 4
        when 'feynman' then 3
        when 'recall' then 2
        else 1
    end desc,
    case scs.current_step_status
        when 'completed' then 3
        when 'due' then 2
        else 1
    end desc,
    scs.last_completed_at desc nulls last,
    scs.updated_at desc;

-- Ausschlüsse vor dem Umbau merken: Ein neuer Check bleibt ausgeschlossen, wenn die Session
-- ihn über keinen Quell-Check enthält, aber mindestens einen Quell-Check ausgeschlossen hatte.
create temporary table hyp_session_exclusions as
select distinct e.session_id, m.new_id
from public.session_check_exclusions e
join hyp_check_map m on m.old_id = e.check_id
where m.new_id is not null
  and not exists (
      select 1
      from hyp_state_winner w
      where w.session_id = e.session_id
        and w.new_id = m.new_id
  );

delete from public.session_check_state scs
using hyp_check_map m
where scs.check_id = m.old_id
  and not exists (
      select 1
      from hyp_state_winner w
      where w.session_id = scs.session_id
        and w.old_id = scs.check_id
  );

-- Aufsteigend nach neuer ID umbenennen, damit keine Primärschlüssel-Kollision entsteht:
-- Ziel 01 ist frei (alt 01 ist Gewinner oder gelöscht), Ziel 02 ist danach frei
-- (alt 02 umbenannt oder gelöscht), Ziel 03 ebenso (alt 03 gelöscht).
update public.session_check_state scs
set check_id = w.new_id
from hyp_state_winner w
where w.new_id = 'stochastik__hypothesentests__01'
  and scs.session_id = w.session_id
  and scs.check_id = w.old_id;

update public.session_check_state scs
set check_id = w.new_id
from hyp_state_winner w
where w.new_id = 'stochastik__hypothesentests__02'
  and scs.session_id = w.session_id
  and scs.check_id = w.old_id;

update public.session_check_state scs
set check_id = w.new_id
from hyp_state_winner w
where w.new_id = 'stochastik__hypothesentests__03'
  and scs.session_id = w.session_id
  and scs.check_id = w.old_id;

-- 3. Ausschlüsse -----------------------------------------------------------------------------

delete from public.session_check_exclusions
where check_id in (select old_id from hyp_check_map);

insert into public.session_check_exclusions (session_id, check_id)
select session_id, new_id
from hyp_session_exclusions
on conflict (session_id, check_id) do nothing;

-- Retention: neuer Check ausgeschlossen, wenn alle seine Quell-Checks ausgeschlossen waren.
create temporary table hyp_retention_exclusions as
select e.user_id, e.lernbereich_slug, m.new_id
from public.user_retention_check_exclusions e
join hyp_check_map m on m.old_id = e.check_id
where m.new_id is not null
group by e.user_id, e.lernbereich_slug, m.new_id
having count(distinct e.check_id) = (
    select count(*) from hyp_check_map m2 where m2.new_id = m.new_id
);

delete from public.user_retention_check_exclusions
where check_id in (select old_id from hyp_check_map);

insert into public.user_retention_check_exclusions (user_id, lernbereich_slug, check_id)
select user_id, lernbereich_slug, new_id
from hyp_retention_exclusions
on conflict (user_id, lernbereich_slug, check_id) do nothing;

-- 4. Lernkarten des Lernbereichs zurücksetzen -----------------------------------------------

delete from public.session_flashcard_rounds
where lernbereich_slug = 'hypothesentests';

delete from public.session_flashcard_card_state
where lernbereich_slug = 'hypothesentests';

delete from public.retention_flashcard_rounds
where lernbereich_slug = 'hypothesentests';

delete from public.retention_flashcard_card_state
where lernbereich_slug = 'hypothesentests';

-- 5. Feed-Zustand bereinigen -----------------------------------------------------------------

delete from public.user_feed_activity_deferrals
where activity_key like 'check:stochastik\_\_hypothesentests\_\_%';

update public.session_feed_cursor
set current_activity_key = null,
    locked_until = null,
    selection_reason = null
where current_activity_key like 'check:stochastik\_\_hypothesentests\_\_%';

-- 6. Geteilte Sessions: gestrichene Checks 03/04 zählen als neuer Check 02 -------------------

update public.shared_sessions s
set config_json = jsonb_set(
    s.config_json,
    '{check_ids}',
    to_jsonb(array(
        select distinct coalesce(
            case
                when c.value in ('stochastik__hypothesentests__03', 'stochastik__hypothesentests__04')
                    then 'stochastik__hypothesentests__02'
                else m.new_id
            end,
            c.value
        ) as check_id
        from jsonb_array_elements_text(s.config_json -> 'check_ids') as c(value)
        left join hyp_check_map m on m.old_id = c.value
        order by 1
    ))
)
where jsonb_typeof(s.config_json -> 'check_ids') = 'array'
  and exists (
      select 1
      from jsonb_array_elements_text(s.config_json -> 'check_ids') as c(value)
      where c.value in (select old_id from hyp_check_map)
  );

-- 7. Betroffene aktive Sessions neu planen --------------------------------------------------

do $$
declare
    affected_session_id uuid;
begin
    for affected_session_id in
        select distinct sl.session_id
        from public.session_lernbereiche sl
        join public.learning_sessions ls on ls.id = sl.session_id
        where sl.lernbereich_slug = 'hypothesentests'
          and ls.status = 'active'
    loop
        perform public.refresh_flashcard_activity_for_lernbereich(affected_session_id, 'hypothesentests');
        perform public.replan_session(affected_session_id);
    end loop;
end;
$$;

drop table hyp_retention_exclusions;
drop table hyp_session_exclusions;
drop table hyp_state_winner;
drop table hyp_check_map;
