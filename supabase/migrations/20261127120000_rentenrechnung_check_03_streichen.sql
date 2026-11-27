-- Lernbereich Rentenrechnung: 7 Checks -> 6 Checks.
--   alt 03 (Vor- oder nachschüssig & Formelauswahl) -> gestrichen
--   alt 04 .. 07                                    -> neu 03 .. 06 (Inhalt unverändert)
--
-- Die Formelauswahl ist vollständig in alt 04 (neu 03, "Rente im Sachkontext") enthalten:
-- Warm-Up und Training dort beginnen jeweils mit der Wahl der passenden Rentenformel.
--
-- Behandlung der Nutzerdaten (wie 20261126100000_binomialverteilung_checks_03_04_streichen.sql):
--   * Verschobene Checks (alt 04..07) sind inhaltlich gleich geblieben. Alle Daten werden 1:1 auf
--     die neue ID umgeschlüsselt: Mitgliedschaft, Ausschlüsse, Abschlüsse, Historie, XP und Lernkarten.
--   * Gestrichener Check (alt 03):
--       - Historie (user_activity_events, learning_activity_attempts, user_xp_awards) bekommt
--         die eindeutige Alt-ID finanzmathematik__rentenrechnung__alt03. XP-Summen bleiben gleich,
--         der Client ignoriert unbekannte check_ids.
--       - Mitgliedschaft, Ausschlüsse und Session-Abschlüsse entfallen.
--       - Lernkarten-Zustände entfallen. Aktive Lernkarten-Runden mit Karten dieses Checks
--         werden verworfen und beim nächsten Aufruf neu erzeugt.
--   * Geteilte Sessions: die gestrichene ID entfällt, verschobene werden umgeschlüsselt.
--
-- Tabellen mit Primärschlüssel auf check_id/card_id/activity_key werden zweistufig umbenannt
-- (alt -> tmp -> neu), damit keine Schlüsselkollision entsteht.

create temporary table renten_check_map (
    old_id text primary key,
    new_id text null,
    tmp_id text null
);

insert into renten_check_map (old_id, new_id)
select
    'finanzmathematik__rentenrechnung__' || lpad(n::text, 2, '0'),
    case when n = 3 then null
         else 'finanzmathematik__rentenrechnung__' || lpad((n - 1)::text, 2, '0')
    end
from generate_series(3, 7) as n;

update renten_check_map
set tmp_id = 'finanzmathematik__rentenrechnung__tmp' || right(new_id, 2)
where new_id is not null;

-- 1. Historie ---------------------------------------------------------------------------------
-- Keine Eindeutigkeit auf check_id, daher einstufig.

update public.user_activity_events t
set check_id = coalesce(m.new_id, 'finanzmathematik__rentenrechnung__alt' || right(m.old_id, 2))
from renten_check_map m
where t.check_id = m.old_id;

update public.learning_activity_attempts t
set check_id = coalesce(m.new_id, 'finanzmathematik__rentenrechnung__alt' || right(m.old_id, 2))
from renten_check_map m
where t.check_id = m.old_id;

update public.user_xp_awards t
set check_id = coalesce(m.new_id, 'finanzmathematik__rentenrechnung__alt' || right(m.old_id, 2))
from renten_check_map m
where t.check_id = m.old_id;

-- 2. Zeilen gestrichener Checks entfernen ------------------------------------------------------

delete from public.session_check_state
where check_id in (select old_id from renten_check_map where new_id is null);

delete from public.session_check_exclusions
where check_id in (select old_id from renten_check_map where new_id is null);

delete from public.user_retention_check_exclusions
where check_id in (select old_id from renten_check_map where new_id is null);

delete from public.session_activity_completions
where check_id in (select old_id from renten_check_map where new_id is null);

-- Aktive Runden mit Karten gestrichener Checks verwerfen (round_cards per Kaskade).
delete from public.session_flashcard_rounds r
where r.status = 'active'
  and exists (
      select 1
      from public.session_flashcard_round_cards rc
      where rc.round_id = r.id
        and rc.check_id in (select old_id from renten_check_map where new_id is null)
  );

delete from public.retention_flashcard_rounds r
where r.status = 'active'
  and exists (
      select 1
      from public.retention_flashcard_round_cards rc
      where rc.round_id = r.id
        and rc.check_id in (select old_id from renten_check_map where new_id is null)
  );

delete from public.session_flashcard_round_cards
where check_id in (select old_id from renten_check_map where new_id is null);

delete from public.retention_flashcard_round_cards
where check_id in (select old_id from renten_check_map where new_id is null);

delete from public.session_flashcard_card_state
where check_id in (select old_id from renten_check_map where new_id is null);

delete from public.retention_flashcard_card_state
where check_id in (select old_id from renten_check_map where new_id is null);

-- 3. Verschobene Checks umschlüsseln: Stufe 1 (alt -> tmp) -----------------------------------

update public.session_check_state t
set check_id = m.tmp_id
from renten_check_map m
where m.new_id is not null and t.check_id = m.old_id;

update public.session_check_exclusions t
set check_id = m.tmp_id
from renten_check_map m
where m.new_id is not null and t.check_id = m.old_id;

update public.user_retention_check_exclusions t
set check_id = m.tmp_id
from renten_check_map m
where m.new_id is not null and t.check_id = m.old_id;

update public.session_activity_completions t
set check_id = m.tmp_id,
    activity_key = replace(t.activity_key, m.old_id, m.tmp_id)
from renten_check_map m
where m.new_id is not null and t.check_id = m.old_id;

update public.session_flashcard_card_state t
set check_id = m.tmp_id,
    card_id = replace(t.card_id, m.old_id, m.tmp_id)
from renten_check_map m
where m.new_id is not null and t.check_id = m.old_id;

update public.retention_flashcard_card_state t
set check_id = m.tmp_id,
    card_id = replace(t.card_id, m.old_id, m.tmp_id)
from renten_check_map m
where m.new_id is not null and t.check_id = m.old_id;

update public.session_flashcard_round_cards t
set check_id = m.tmp_id,
    card_id = replace(t.card_id, m.old_id, m.tmp_id)
from renten_check_map m
where m.new_id is not null and t.check_id = m.old_id;

update public.retention_flashcard_round_cards t
set check_id = m.tmp_id,
    card_id = replace(t.card_id, m.old_id, m.tmp_id)
from renten_check_map m
where m.new_id is not null and t.check_id = m.old_id;

-- 4. Stufe 2 (tmp -> neu) ----------------------------------------------------------------------

update public.session_check_state t
set check_id = m.new_id
from renten_check_map m
where t.check_id = m.tmp_id;

update public.session_check_exclusions t
set check_id = m.new_id
from renten_check_map m
where t.check_id = m.tmp_id;

update public.user_retention_check_exclusions t
set check_id = m.new_id
from renten_check_map m
where t.check_id = m.tmp_id;

update public.session_activity_completions t
set check_id = m.new_id,
    activity_key = replace(t.activity_key, m.tmp_id, m.new_id)
from renten_check_map m
where t.check_id = m.tmp_id;

update public.session_flashcard_card_state t
set check_id = m.new_id,
    card_id = replace(t.card_id, m.tmp_id, m.new_id)
from renten_check_map m
where t.check_id = m.tmp_id;

update public.retention_flashcard_card_state t
set check_id = m.new_id,
    card_id = replace(t.card_id, m.tmp_id, m.new_id)
from renten_check_map m
where t.check_id = m.tmp_id;

update public.session_flashcard_round_cards t
set check_id = m.new_id,
    card_id = replace(t.card_id, m.tmp_id, m.new_id)
from renten_check_map m
where t.check_id = m.tmp_id;

update public.retention_flashcard_round_cards t
set check_id = m.new_id,
    card_id = replace(t.card_id, m.tmp_id, m.new_id)
from renten_check_map m
where t.check_id = m.tmp_id;

-- 5. Geteilte Sessions -------------------------------------------------------------------------

update public.shared_sessions s
set config_json = jsonb_set(
    s.config_json,
    '{check_ids}',
    coalesce(
        (
            select jsonb_agg(mapped.check_id order by mapped.check_id)
            from (
                select distinct
                    case when m.old_id is null then c.value else m.new_id end as check_id
                from jsonb_array_elements_text(s.config_json -> 'check_ids') as c(value)
                left join renten_check_map m on m.old_id = c.value
            ) as mapped
            where mapped.check_id is not null
        ),
        '[]'::jsonb
    )
)
where jsonb_typeof(s.config_json -> 'check_ids') = 'array'
  and exists (
      select 1
      from jsonb_array_elements_text(s.config_json -> 'check_ids') as c(value)
      where c.value in (select old_id from renten_check_map)
  );

drop table renten_check_map;
