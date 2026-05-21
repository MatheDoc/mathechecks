insert into public.system_settings (setting_key, value_integer, description)
values
    ('feed.retention_interleave_lead_session_items', 5, 'Wie viele Session-Aktivitäten im Hybrid-Feed vor dem ersten Wiederholungs-Slot bleiben.'),
    ('feed.retention_interleave_stride', 4, 'Wie viele weitere Session-Aktivitäten zwischen zwei Wiederholungs-Slots liegen.'),
    ('feed.session_follow_up_max_gap', 3, 'Maximalzahl frischer Training-1-Aktivitäten zwischen zwei Folgeaktivitäten laufender Check-Ketten.')
on conflict (setting_key) do update
set value_integer = excluded.value_integer,
    description = excluded.description;