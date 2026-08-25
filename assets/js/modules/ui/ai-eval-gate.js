// Gemeinsames Zugangs-Gate fuer die KI-Auswertung in Recall und Feynman.
//
// Grundprinzip: Nicht angemeldete Nutzer (oder Nutzer am Tageslimit) sehen
// statt der Antwort-Textfelder einen Hinweis und koennen gar nicht erst
// Antworten verfassen, die anschliessend nicht auswertbar waeren.
import { buildAccountUrl, getCurrentAuthState, getSupabaseClient } from "../../platform/supabase-client.js?v=20260520-feed-loading";

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// Liefert { state: "ok" | "anonymous" | "limited", count?, limit? }.
// Fehler beim Statusabruf werden bewusst als "ok" behandelt (fail-open):
// die bestehende Laufzeit-Fehlerbehandlung der Evaluate-Aufrufe greift dann.
export async function resolveAiEvaluationAccess(scope) {
  try {
    const auth = await getCurrentAuthState();
    if (!auth.configured) return { state: "ok" };
    if (!auth.user) return { state: "anonymous" };

    const supabase = await getSupabaseClient();
    if (!supabase) return { state: "ok" };

    const { data, error } = await supabase.rpc("get_ai_rate_limit_status", { p_scope: scope });
    if (error || !data || typeof data !== "object") return { state: "ok" };

    const count = Number(data.count);
    const limit = Number(data.limit);
    if (data.allowed === false) {
      return { state: "limited", count, limit };
    }
    return { state: "ok", count, limit };
  } catch {
    return { state: "ok" };
  }
}

export function isAiEvaluationBlocked(access) {
  return Boolean(access && access.state !== "ok");
}

export function renderAiEvaluationGateMarkup(access) {
  if (!isAiEvaluationBlocked(access)) return "";

  if (access.state === "limited") {
    return `
      <div class="ai-eval-gate-inline" data-ai-eval-gate="limited">
        <span class="ai-eval-gate-inline__icon" aria-hidden="true">⏳</span>
        <span class="ai-eval-gate-inline__text">Tageslimit für KI-Auswertungen erreicht.</span>
      </div>
    `;
  }

  const nextPath = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  const loginUrl = buildAccountUrl(nextPath);
  return `
    <div class="ai-eval-gate-inline" data-ai-eval-gate="anonymous">
      <span class="ai-eval-gate-inline__icon" aria-hidden="true">🔒</span>
      <span class="ai-eval-gate-inline__text">Für die KI-Auswertung bitte <a class="ai-eval-gate-inline__link" href="${escapeHtml(loginUrl)}">anmelden</a>.</span>
    </div>
  `;
}
