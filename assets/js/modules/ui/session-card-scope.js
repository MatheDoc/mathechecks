import { getSupabaseClient, getSupabaseRuntimeConfig } from "../../platform/supabase-client.js?v=20260520-feed-loading";

const CARD_SELECTOR = ".check-card";
const REFRESH_MIN_INTERVAL_MS = 30000;

let sessionCheckIds = null;
let observer = null;
let scanScheduled = false;
let lastLoadAt = 0;

async function loadSessionCheckIds() {
  if (!getSupabaseRuntimeConfig().configured) return null;
  const supabase = await getSupabaseClient();
  if (!supabase) return null;

  const { data: authData } = await supabase.auth.getSession();
  if (!authData?.session?.user) return null;

  const { data: sessions, error: sessionError } = await supabase
    .from("learning_sessions")
    .select("id")
    .eq("status", "active")
    .order("started_at", { ascending: false })
    .limit(1);
  if (sessionError) throw sessionError;

  const sessionId = Array.isArray(sessions) ? sessions[0]?.id : null;
  if (!sessionId) return null;

  const { data: rows, error: rowsError } = await supabase
    .from("session_check_state")
    .select("check_id")
    .eq("session_id", sessionId);
  if (rowsError) throw rowsError;

  const ids = new Set(
    (Array.isArray(rows) ? rows : []).map((row) => String(row?.check_id || "").trim()).filter(Boolean),
  );
  return ids.size ? ids : null;
}

function resolveCardCheckId(card) {
  return String(card.dataset.checkId || card.closest("[data-check-id]")?.dataset.checkId || "").trim();
}

function applyScope(card) {
  const checkId = resolveCardCheckId(card);
  const outside = Boolean(sessionCheckIds && checkId && !sessionCheckIds.has(checkId));
  if (outside) {
    if (card.dataset.sessionScope !== "outside") card.dataset.sessionScope = "outside";
  } else if (card.hasAttribute("data-session-scope")) {
    card.removeAttribute("data-session-scope");
  }
}

function scanCards() {
  scanScheduled = false;
  document.querySelectorAll(CARD_SELECTOR).forEach(applyScope);
}

function scheduleScan() {
  if (scanScheduled) return;
  scanScheduled = true;
  window.requestAnimationFrame(scanCards);
}

function ensureObserver() {
  if (observer || !document.body) return;
  // Karten entstehen asynchron (Training, Skript, Flashcard-Wechsel) -> neu markieren.
  observer = new MutationObserver(scheduleScan);
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["data-check-id"],
  });
}

async function refreshSessionCheckIds() {
  lastLoadAt = Date.now();
  try {
    sessionCheckIds = await loadSessionCheckIds();
  } catch (error) {
    console.warn("MatheChecks: Session-Checks für Kartenmarkierung konnten nicht geladen werden.", error);
    sessionCheckIds = null;
  }
  if (sessionCheckIds) ensureObserver();
  scheduleScan();
}

export function initSessionCardScope() {
  if (typeof window === "undefined" || typeof document === "undefined") return;

  void refreshSessionCheckIds();
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState !== "visible") return;
    if (Date.now() - lastLoadAt < REFRESH_MIN_INTERVAL_MS) return;
    void refreshSessionCheckIds();
  });
}
