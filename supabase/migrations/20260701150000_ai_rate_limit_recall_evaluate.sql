-- Schlankes, pro Nutzer und Tag gefuehrtes Anfragelimit fuer KI-Endpunkte.
--
-- Hintergrund: `supabase/functions/recall-evaluate` rief bisher direkt Gemini
-- auf, sobald ein gueltiges Supabase-Projekt-JWT vorlag. Der oeffentliche
-- anonKey ist selbst ein gueltiges JWT -> die Function war faktisch nicht an
-- einen eingeloggten Nutzer gebunden. Ein einzelner Nutzer (oder ein Skript
-- mit dem oeffentlichen anonKey) konnte dadurch das gemeinsame Gemini-
-- Tageskontingent fuer alle anderen Nutzer aufbrauchen.
--
-- Diese Migration fuehrt einen minimalen, wiederverwendbaren Zaehler ein:
-- pro (user_id, scope, Tag) wird ein Request-Count gefuehrt. Der Scope
-- erlaubt spaetere weitere KI-Endpunkte, ohne die Tabelle zu aendern.
--
-- WICHTIG: Fuer `auth.uid()` in `consume_ai_rate_limit(...)` muss der
-- Aufrufer sein echtes Supabase-Session-Token mitschicken, nicht den
-- oeffentlichen anonKey. `assets/js/modules/recall.js` wurde entsprechend
-- angepasst (Bearer = Access-Token der aktiven Session).

insert into public.system_settings (setting_key, value_integer, description)
values
    ('recall_evaluate.daily_request_limit', 30, 'Recall-KI-Bewertung: maximale Anzahl Anfragen pro Nutzer und Tag an recall-evaluate.')
on conflict (setting_key) do nothing;

create table if not exists public.user_ai_request_counters (
    user_id uuid not null references auth.users(id) on delete cascade,
    scope text not null,
    request_date date not null,
    request_count integer not null default 0,
    last_request_at timestamptz not null default now(),
    primary key (user_id, scope, request_date)
);

alter table public.user_ai_request_counters enable row level security;
-- Bewusst keine Policies: Lesen/Schreiben ausschliesslich ueber die
-- SECURITY DEFINER-Funktion unten, niemals direkt per PostgREST-Tabellenzugriff.

create or replace function public.consume_ai_rate_limit(
    p_scope text,
    p_daily_limit integer default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_scope text := nullif(trim(p_scope), '');
    v_limit integer;
    v_day date := (timezone('Europe/Berlin', now()))::date;
    v_count integer;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_scope is null then
        raise exception 'scope is required';
    end if;

    v_limit := coalesce(
        p_daily_limit,
        public.get_system_setting_integer(normalized_scope || '.daily_request_limit', 30)
    );

    insert into public.user_ai_request_counters (user_id, scope, request_date, request_count, last_request_at)
    values (current_user_id, normalized_scope, v_day, 1, now())
    on conflict (user_id, scope, request_date)
        do update set
            request_count = public.user_ai_request_counters.request_count + 1,
            last_request_at = now()
    returning request_count into v_count;

    return jsonb_build_object(
        'allowed', v_count <= v_limit,
        'count', v_count,
        'limit', v_limit
    );
end;
$$;

revoke all on function public.consume_ai_rate_limit(text, integer) from public;
revoke all on function public.consume_ai_rate_limit(text, integer) from anon;
grant execute on function public.consume_ai_rate_limit(text, integer) to authenticated;
