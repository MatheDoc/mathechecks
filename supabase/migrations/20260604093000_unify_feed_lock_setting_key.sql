insert into public.system_settings (
    setting_key,
    value_integer,
    value_numeric,
    description
)
select
    'feed.lock_duration_minutes',
    coalesce(legacy.value_integer, floor(legacy.value_numeric)::integer, 30),
    coalesce(legacy.value_numeric, legacy.value_integer::numeric, 30),
    'Wie lange ein aktuelles Feed-Element nach Auswahl als klebriger Cursor gesperrt bleibt.'
from public.system_settings as legacy
where legacy.setting_key = 'feed.current_activity_lock_minutes'
on conflict (setting_key) do update
set value_integer = coalesce(public.system_settings.value_integer, excluded.value_integer),
    value_numeric = coalesce(public.system_settings.value_numeric, excluded.value_numeric),
    description = excluded.description;

insert into public.system_settings (
    setting_key,
    value_integer,
    value_numeric,
    description
)
values (
    'feed.lock_duration_minutes',
    30,
    30,
    'Wie lange ein aktuelles Feed-Element nach Auswahl als klebriger Cursor gesperrt bleibt.'
)
on conflict (setting_key) do update
set description = excluded.description;

delete from public.system_settings
where setting_key = 'feed.current_activity_lock_minutes';

create or replace function public.get_feed_cursor_lock_interval()
returns interval
language sql
stable
set search_path = public
as $$
    select make_interval(mins => greatest(public.get_system_setting_integer('feed.lock_duration_minutes', 30), 1));
$$;