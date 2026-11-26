-- Lernbereich Binomialverteilung: 16 Checks -> 9 Checks.
--   01 .. 05                                                   -> unverändert
--   06 npk-n, 07 npk-p, 08 npk-k                               -> neu 06 (npk, gemischt)
--   09 kennzahlen-n-p, 10 kennzahlen-n-mu, 11 kennzahlen-p-mu  -> neu 07 (kennzahlen-mu, gemischt)
--   12 kennzahlen-mu-sigma, 13 kennzahlen-p-sigma              -> neu 08 (kennzahlen-sigma, gemischt)
--   14 umgebungen-absolut, 15 -relativ, 16 -sigma              -> neu 09 (umgebungen, drei Teilfragen)
--
-- Behandlung der Nutzerdaten (wie 20261120090000_hypothesentests_checks_zusammenlegen.sql):
--   * Historie (user_activity_events, learning_activity_attempts, user_xp_awards) bleibt erhalten,
--     bekommt aber eindeutige Alt-IDs nach Sammlung (stochastik__binomialverteilung__alt-<sammlung>).
--     XP-Summen bleiben gleich, alte Quoten werden nicht den gemischten Checks zugeordnet.
--     Der Client ignoriert unbekannte check_ids.
--   * Mitgliedschaft: Ein neuer Check gehört zur Session, wenn mindestens ein Quell-Check dazugehörte.
--   * Session-Abschlüsse: Je Session, neuem Check und Aktivitätstyp zählt der früheste Abschluss
--     eines Quell-Checks.
--   * Ausschlüsse: Session-Ausschluss bleibt, wenn die Session den neuen Check über keinen Quell-Check
--     enthält, aber mindestens einen Quell-Check ausgeschlossen hatte. Retention-Ausschluss bleibt,
--     wenn alle Quell-Checks ausgeschlossen waren.
--   * Lernkarten der Quell-Checks werden zurückgesetzt, weil sich die Aufgabensammlungen geändert haben.
--     Aktive Runden mit solchen Karten werden verworfen und beim nächsten Aufruf neu erzeugt.
--     Die Checks 01 .. 05 behalten ihre Kartenstände.
--   * Geteilte Sessions werden auf die neuen IDs umgestellt.
--
-- Weil neue IDs (06 .. 09) mit alten IDs zusammenfallen, werden die Quellzeilen zuerst auf
-- eindeutige tmp-IDs umbenannt, dann zusammengeführt und am Ende entfernt.

create temporary table binom_merge_map (
    old_id text primary key,
    new_id text not null,
    tmp_id text not null,
    alt_id text not null
);

insert into binom_merge_map (old_id, new_id, tmp_id, alt_id)
select
    'stochastik__binomialverteilung__' || lpad(v.old_n::text, 2, '0'),
    'stochastik__binomialverteilung__' || lpad(v.new_n::text, 2, '0'),
    'stochastik__binomialverteilung__src' || lpad(v.old_n::text, 2, '0'),
    'stochastik__binomialverteilung__alt-' || v.sammlung
from (values
    (6,  6, 'npk-n'),
    (7,  6, 'npk-p'),
    (8,  6, 'npk-k'),
    (9,  7, 'kennzahlen-n-p-gegeben'),
    (10, 7, 'kennzahlen-n-mu-gegeben'),
    (11, 7, 'kennzahlen-p-mu-gegeben'),
    (12, 8, 'kennzahlen-mu-sigma-gegeben'),
    (13, 8, 'kennzahlen-p-sigma-gegeben'),
    (14, 9, 'umgebungen-absolut'),
    (15, 9, 'umgebungen-relativ'),
    (16, 9, 'umgebungen-sigma')
) as v(old_n, new_n, sammlung);

-- 1. Historie auf Alt-IDs ---------------------------------------------------------------------

update public.user_activity_events t
set check_id = m.alt_id
from binom_merge_map m
where t.check_id = m.old_id;

update public.learning_activity_attempts t
set check_id = m.alt_id
from binom_merge_map m
where t.check_id = m.old_id;

update public.user_xp_awards t
set check_id = m.alt_id
from binom_merge_map m
where t.check_id = m.old_id;

-- 2. Lernkarten der Quell-Checks zurücksetzen -------------------------------------------------

delete from public.session_flashcard_rounds r
where r.status = 'active'
  and exists (
      select 1
      from public.session_flashcard_round_cards rc
      where rc.round_id = r.id
        and rc.check_id in (select old_id from binom_merge_map)
  );

delete from public.retention_flashcard_rounds r
where r.status = 'active'
  and exists (
      select 1
      from public.retention_flashcard_round_cards rc
      where rc.round_id = r.id
        and rc.check_id in (select old_id from binom_merge_map)
  );

delete from public.session_flashcard_round_cards
where check_id in (select old_id from binom_merge_map);

delete from public.retention_flashcard_round_cards
where check_id in (select old_id from binom_merge_map);

delete from public.session_flashcard_card_state
where check_id in (select old_id from binom_merge_map);

delete from public.retention_flashcard_card_state
where check_id in (select old_id from binom_merge_map);

-- 3. Quellzeilen auf tmp-IDs ------------------------------------------------------------------

update public.session_check_state t
set check_id = m.tmp_id
from binom_merge_map m
where t.check_id = m.old_id;

update public.session_check_exclusions t
set check_id = m.tmp_id
from binom_merge_map m
where t.check_id = m.old_id;

update public.user_retention_check_exclusions t
set check_id = m.tmp_id
from binom_merge_map m
where t.check_id = m.old_id;

update public.session_activity_completions t
set check_id = m.tmp_id,
    activity_key = replace(t.activity_key, m.old_id, m.tmp_id)
from binom_merge_map m
where t.check_id = m.old_id;

-- 4. Zusammenführen ---------------------------------------------------------------------------

-- Mitgliedschaft
insert into public.session_check_state (session_id, check_id)
select distinct t.session_id, m.new_id
from public.session_check_state t
join binom_merge_map m on m.tmp_id = t.check_id
on conflict (session_id, check_id) do nothing;

-- Session-Ausschlüsse
insert into public.session_check_exclusions (session_id, check_id)
select distinct e.session_id, m.new_id
from public.session_check_exclusions e
join binom_merge_map m on m.tmp_id = e.check_id
where not exists (
    select 1
    from public.session_check_state s
    join binom_merge_map m2 on m2.tmp_id = s.check_id
    where s.session_id = e.session_id
      and m2.new_id = m.new_id
)
on conflict (session_id, check_id) do nothing;

-- Retention-Ausschlüsse: nur wenn alle Quell-Checks ausgeschlossen waren
insert into public.user_retention_check_exclusions (user_id, lernbereich_slug, check_id)
select e.user_id, e.lernbereich_slug, m.new_id
from public.user_retention_check_exclusions e
join binom_merge_map m on m.tmp_id = e.check_id
group by e.user_id, e.lernbereich_slug, m.new_id
having count(distinct e.check_id) = (
    select count(*) from binom_merge_map m2 where m2.new_id = m.new_id
)
on conflict (user_id, lernbereich_slug, check_id) do nothing;

-- Session-Abschlüsse: frühester Abschluss je Session, neuem Check und Aktivitätstyp
insert into public.session_activity_completions (
    session_id, activity_key, activity_type, lernbereich_slug, check_id, completed_at
)
select
    c.session_id,
    'check:' || m.new_id || ':' || c.activity_type,
    c.activity_type,
    min(c.lernbereich_slug),
    m.new_id,
    min(c.completed_at)
from public.session_activity_completions c
join binom_merge_map m on m.tmp_id = c.check_id
group by c.session_id, m.new_id, c.activity_type
on conflict (session_id, activity_key) do nothing;

-- 5. tmp-Zeilen entfernen ---------------------------------------------------------------------

delete from public.session_check_state
where check_id in (select tmp_id from binom_merge_map);

delete from public.session_check_exclusions
where check_id in (select tmp_id from binom_merge_map);

delete from public.user_retention_check_exclusions
where check_id in (select tmp_id from binom_merge_map);

delete from public.session_activity_completions
where check_id in (select tmp_id from binom_merge_map);

-- 6. Geteilte Sessions ------------------------------------------------------------------------

update public.shared_sessions s
set config_json = jsonb_set(
    s.config_json,
    '{check_ids}',
    coalesce(
        (
            select jsonb_agg(mapped.check_id order by mapped.check_id)
            from (
                select distinct coalesce(m.new_id, c.value) as check_id
                from jsonb_array_elements_text(s.config_json -> 'check_ids') as c(value)
                left join binom_merge_map m on m.old_id = c.value
            ) as mapped
        ),
        '[]'::jsonb
    )
)
where jsonb_typeof(s.config_json -> 'check_ids') = 'array'
  and exists (
      select 1
      from jsonb_array_elements_text(s.config_json -> 'check_ids') as c(value)
      where c.value in (select old_id from binom_merge_map)
  );

drop table binom_merge_map;
