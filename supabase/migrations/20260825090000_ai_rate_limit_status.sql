-- Read-only Statusabfrage fuer das taegliche KI-Anfragelimit.
--
-- Hintergrund: Das Frontend soll VOR der Eingabe (Recall-/Feynman-Textfelder)
-- wissen, ob ein angemeldeter Nutzer sein Tageslimit fuer KI-Auswertungen
-- bereits erreicht hat. `consume_ai_rate_limit(...)` inkrementiert den
-- Zaehler und ist dafuer ungeeignet. Diese Funktion liest denselben Zaehler
-- (`public.user_ai_request_counters`) nur aus, ohne ihn zu veraendern.
--
-- `allowed` ist true, solange mindestens eine weitere Anfrage moeglich ist
-- (Zaehlerstand < Limit); die Semantik passt damit zu consume, das nach dem
-- Increment `count <= limit` prueft.

create or replace function public.get_ai_rate_limit_status(
    p_scope text
)
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
    current_user_id uuid := auth.uid();
    normalized_scope text := nullif(trim(p_scope), '');
    v_limit integer;
    v_day date := (timezone('Europe/Berlin', now()))::date;
    v_count integer := 0;
begin
    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if normalized_scope is null then
        raise exception 'scope is required';
    end if;

    v_limit := public.get_system_setting_integer(normalized_scope || '.daily_request_limit', 30);

    select request_count
      into v_count
      from public.user_ai_request_counters
     where user_id = current_user_id
       and scope = normalized_scope
       and request_date = v_day;

    v_count := coalesce(v_count, 0);

    return jsonb_build_object(
        'allowed', v_count < v_limit,
        'count', v_count,
        'limit', v_limit
    );
end;
$$;

revoke all on function public.get_ai_rate_limit_status(text) from public;
revoke all on function public.get_ai_rate_limit_status(text) from anon;
grant execute on function public.get_ai_rate_limit_status(text) to authenticated;
