-- Migration: Retention-Check-Ausschlüsse und manage_retention_scopes RPC
--
-- Neu: user_retention_check_exclusions
--   Analogon zu session_check_exclusions, aber user-scoped (kein session-Bezug).
--   Ermöglicht Check-Granularität in Retention-Scopes.
--
-- Neu: manage_retention_scopes(p_active_lernbereiche, p_excluded_check_ids)
--   Verwaltungs-RPC für das Retention-Modal im Dashboard.
--   Schreibt user_retention_scopes (upsert active/opted_out) und
--   user_retention_check_exclusions (delete+insert) atomar.


-- 1. Tabelle user_retention_check_exclusions
-- ------------------------------------------
create table public.user_retention_check_exclusions (
    user_id uuid not null references auth.users(id) on delete cascade,
    lernbereich_slug text not null check (char_length(trim(lernbereich_slug)) > 0),
    check_id text not null check (char_length(trim(check_id)) > 0),
    created_at timestamptz not null default now(),
    primary key (user_id, lernbereich_slug, check_id)
);

create index user_retention_check_exclusions_user_idx
    on public.user_retention_check_exclusions (user_id, lernbereich_slug);

alter table public.user_retention_check_exclusions enable row level security;

create policy user_retention_check_exclusions_select_own
    on public.user_retention_check_exclusions
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

grant select on public.user_retention_check_exclusions to authenticated;


-- 2. RPC manage_retention_scopes
-- --------------------------------
-- p_active_lernbereiche: Slugs der gewünschten aktiven Retention-Scopes.
--   Alle anderen bestehenden aktiven Scopes werden auf 'opted_out' gesetzt.
-- p_excluded_check_ids: JSONB-Objekt { "lernbereich-slug": ["check_id_1", ...] }
--   Alle bestehenden Ausschlüsse des Users werden ersetzt.
--
-- Sicherheit: SECURITY DEFINER + auth.uid()-Prüfung.
-- source_session_id wird bei manuellen Änderungen nicht berührt.

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

    -- Aktive Scopes upserten
    if coalesce(array_length(normalized_lernbereiche, 1), 0) > 0 then
        insert into public.user_retention_scopes (
            user_id, activity_type, scope_type, lernbereich_slug, status
        )
        select current_user_id, 'flashcards', 'lernbereich', slug, 'active'
        from unnest(normalized_lernbereiche) as slugs(slug)
        on conflict (user_id, activity_type, scope_type, lernbereich_slug) do update
            set status = 'active';
    end if;

    -- Nicht mehr gewählte aktive Scopes auf opted_out setzen
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

    -- Check-Ausschlüsse des Users komplett ersetzen
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

grant execute on function public.manage_retention_scopes(text[], jsonb) to authenticated;
