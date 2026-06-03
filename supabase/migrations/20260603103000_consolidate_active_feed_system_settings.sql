-- Canonical active feed settings.
--
-- Source of truth for feed tuning lives in public.system_settings on Supabase.
-- The frontend only reads the tiny subset it actually needs; everything else,
-- especially cursor locking and planning pressure, is evaluated server-side.

delete from public.system_settings
where setting_key in (
    'feed.retention_new_item_position'
);

insert into public.system_settings (
    setting_key,
    value_integer,
    description
)
values
    (
        'feed.retention_activity_base_gap',
        5,
        'Basisabstand N fuer Retention-Flashcards; weitere Wiedereinblendungen wachsen linear als N, 2N, 3N, ...'
    ),
    (
        'feed.core_gap_normal_hours',
        24,
        'Basisabstand in Stunden fuer didaktische Folgeaktivitaeten im Core-Feed und deren Ueberfaelligkeitslogik.'
    ),
    (
        'feed.current_activity_lock_minutes',
        30,
        'Wie lange ein aktuelles Feed-Element nach Auswahl als klebriger Cursor gesperrt bleibt.'
    ),
    (
        'planning.default_session_tempo_days',
        3,
        'Standardannahme fuer offene Aktivitaeten pro Kalendertag in Session-Planung und Replan-Druck.'
    )
on conflict (setting_key) do update
set value_integer = excluded.value_integer,
    description = excluded.description;