-- Migration: manuell aktivierte Wiederholungen sollen sofort im Feed erscheinen.
--
-- Problem:
-- - manage_retention_scopes(...) nutzt fuer neue oder reaktivierte Scopes den
--   allgemeinen Aktivierungspfad set_retention_scope_status(..., 'active').
-- - Dieser setzt next_due_after_activity_count immer auf den aktuellen
--   Aktivitaetszaehler plus Basisabstand. Dadurch erscheinen bewusst manuell
--   aktivierte Wiederholungen waehrend einer laufenden Session erst spaeter.
--
-- Fix:
-- 1. set_retention_scope_status(...) erhaelt eine ueberladene 3-Argument-Variante
--    mit Due-Modus ('scheduled' | 'immediate').
-- 2. Die bestehende 2-Argument-Variante bleibt als Wrapper auf 'scheduled'.
-- 3. manage_retention_scopes(...) nutzt fuer neue oder reaktivierte manuelle
--    Aktivierungen den Due-Modus 'immediate'. Bereits aktive Scopes werden beim
--    erneuten Speichern weiterhin nicht retimed.

create or replace function public.set_retention_scope_status(
    p_lernbereich_slug text,
    p_status text,
    p_due_mode text
)
returns public.user_retention_scopes
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_lernbereich_slug text := nullif(trim(p_lernbereich_slug), '');
    normalized_status text := lower(coalesce(nullif(trim(p_status), ''), ''));
    normalized_due_mode text := lower(coalesce(nullif(trim(p_due_mode), ''), 'scheduled'));
    updated_scope public.user_retention_scopes;
    current_completed_activity_count bigint := public.get_current_feed_activity_completion_count();
    retention_activity_gap integer := public.get_system_setting_integer('feed.retention_activity_base_gap', 5);
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_lernbereich_slug is null then
        raise exception 'lernbereich_slug is required';
    end if;

    if normalized_status not in ('active', 'paused', 'opted_out') then
        raise exception 'Unsupported retention status';
    end if;

    if normalized_due_mode not in ('scheduled', 'immediate') then
        raise exception 'Unsupported retention due mode';
    end if;

    insert into public.user_retention_scopes (
        user_id,
        activity_type,
        scope_type,
        lernbereich_slug,
        status,
        source_session_id,
        activity_interval,
        activity_due_exponent,
        next_due_after_activity_count
    )
    values (
        current_user_id,
        'flashcards',
        'lernbereich',
        normalized_lernbereich_slug,
        normalized_status,
        null,
        retention_activity_gap,
        0,
        case
            when normalized_status = 'active' and normalized_due_mode = 'immediate' then current_completed_activity_count
            else current_completed_activity_count + retention_activity_gap
        end
    )
    on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
    set status = excluded.status,
        activity_interval = case
            when excluded.status = 'active' then excluded.activity_interval
            else public.user_retention_scopes.activity_interval
        end,
        activity_due_exponent = case
            when excluded.status = 'active' then 0
            else public.user_retention_scopes.activity_due_exponent
        end,
        next_due_after_activity_count = case
            when excluded.status = 'active' and normalized_due_mode = 'immediate' then current_completed_activity_count
            when excluded.status = 'active' then current_completed_activity_count + public.user_retention_scopes.activity_interval
            else public.user_retention_scopes.next_due_after_activity_count
        end
    returning * into updated_scope;

    return updated_scope;
end;
$$;

create or replace function public.set_retention_scope_status(
    p_lernbereich_slug text,
    p_status text
)
returns public.user_retention_scopes
language plpgsql
security definer
set search_path = public
as $$
begin
    return public.set_retention_scope_status(p_lernbereich_slug, p_status, 'scheduled');
end;
$$;

revoke all on function public.set_retention_scope_status(text, text, text) from public;
revoke all on function public.set_retention_scope_status(text, text, text) from anon;
grant execute on function public.set_retention_scope_status(text, text, text) to authenticated;

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

    -- Neu oder erneut manuell aktivierte Scopes sofort faellig machen, damit
    -- bewusst ausgewaehlte Wiederholungen direkt im Feed auftauchen. Bereits
    -- aktive Scopes bleiben beim erneuten Speichern unveraendert.
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
            perform public.set_retention_scope_status(selected_lernbereich_slug, 'active', 'immediate');
        end if;
    end loop;

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