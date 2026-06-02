delete from public.system_settings
where setting_key = 'feed.dashboard_item_limit';

delete from public.system_settings
where setting_key = 'feed.session_follow_up_max_gap';

insert into public.system_settings (setting_key, value_integer, description)
values (
    'feed.core_gap_normal_hours',
    24,
    'Basisabstand in Stunden fuer didaktische Folgeaktivitaeten im Core-Feed (training -> recall, recall -> feynman, feynman -> kompetenzliste).'
)
on conflict (setting_key) do update
set value_integer = excluded.value_integer,
    description = excluded.description;