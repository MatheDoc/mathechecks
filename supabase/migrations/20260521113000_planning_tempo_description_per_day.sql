update public.system_settings
set description = 'Standard-Tempo als offene Aktivitäten pro Tag, wenn keine andere Session-Vorgabe gespeichert ist.'
where setting_key = 'planning.default_session_tempo_days';