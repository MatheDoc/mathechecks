-- Migration: manage_retention_scopes nutzt denselben Aktivierungspfad wie
-- set_retention_scope_status(...), ohne bestehende aktive Due-Zeitpunkte beim
-- bloßen Resave des Modals zurückzusetzen.

create or replace function public.manage_retention_scopes(
    p_active_lernbereiche text[],
    p_excluded_check_ids jsonb default '{}'::jsonb
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereiche text[];
    selected_lernbereich_slug text;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    normalized_lernbereiche := array(
        select distinct slug
        from (
            select nullif(trim(lb.value), '') as slug
            from unnest(coalesce(p_active_lernbereiche, array[]::text[])) as lb(value)
        ) normalized
        where slug is not null
    );

    -- Neue oder reaktivierte Scopes über den bestehenden Aktivierungs-RPC
    -- anlegen, damit Taktung und Due-Counter an genau einer Stelle definiert
    -- bleiben. Bereits aktive Scopes bleiben unverändert, damit ein erneutes
    -- Speichern im Modal keine bestehende Fälligkeit nach hinten verschiebt.
    foreach selected_lernbereich_slug in array coalesce(normalized_lernbereiche, array[]::text[]) loop
        if not exists (
            select 1
            from public.user_retention_scopes
            where user_id = current_user_id
              and activity_type = 'flashcards'
              and scope_type = 'lernbereich'
              and lernbereich_slug = selected_lernbereich_slug
              and status = 'active'
        ) then
            perform public.set_retention_scope_status(selected_lernbereich_slug, 'active');
        end if;
    end loop;

    -- Nicht mehr gewählte aktive Scopes auf opted_out setzen.
    update public.user_retention_scopes
    set status = 'opted_out'
    where user_id = current_user_id
      and activity_type = 'flashcards'
      and scope_type = 'lernbereich'
      and status = 'active'
      and (
          coalesce(array_length(normalized_lernbereiche, 1), 0) = 0
          or not (lernbereich_slug = any(normalized_lernbereiche))
      );

    -- Check-Ausschlüsse des Users komplett ersetzen.
    delete from public.user_retention_check_exclusions
    where user_id = current_user_id;

    if p_excluded_check_ids is not null and p_excluded_check_ids != '{}'::jsonb then
        insert into public.user_retention_check_exclusions (user_id, lernbereich_slug, check_id)
        select
            current_user_id,
            trim(kv.key),
            trim(check_id_value)
        from jsonb_each(p_excluded_check_ids) as kv(key, value),
             jsonb_array_elements_text(kv.value) as check_id_value
        where nullif(trim(kv.key), '') is not null
          and nullif(trim(check_id_value), '') is not null
        on conflict do nothing;
    end if;
end;
$$;
