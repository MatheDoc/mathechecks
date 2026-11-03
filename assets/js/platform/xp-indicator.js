// XP-Anzeige in der Kopfzeile: Ring mit Stufe (XP im Tooltip), Popover mit Regeln und "+x"-Einblendung.
// Berechnung serverseitig (award_xp, get_user_xp_summary); hier nur Anzeige. Nur für angemeldete Nutzer.
import {
  XP_AWARDED_EVENT,
  getUserXpSummary,
} from "./progress-client.js?v=20261103-xp-runs";

const TYPE_LABELS = {
  feynman: "Feynman",
  recall: "Recall",
  warmup: "Warm-Up",
  test: "Test",
  training: "Training",
};

const TYPE_UNITS = {
  feynman: "je Erklärung",
  recall: "je Durchgang",
  warmup: "je Schritt",
  test: "je Frage",
  training: "je Teilantwort",
};

// Bei Recall und Feynman steht der Aktivitätsname im "+x", weil dort größere Beträge auf einmal kommen.
const LABELED_TYPES = new Set(["recall", "feynman"]);

const FACTOR_LABELS = {
  first: "erstmals",
  spaced: "",
  repeat: "Wiederholung",
  repeat_late: "Wiederholung",
};

const REFRESH_ON_FOCUS_MS = 60_000;
// Gleicher Schlüssel wie im Inline-Skript in _includes/topbar.html.
const CACHE_KEY = "mathechecks.xpIndicator.v1";

let currentUserId = null;
let summary = null;
let lastLoadedAt = 0;
let queue = Promise.resolve();
let listenersBound = false;

function readCache() {
  try {
    return JSON.parse(window.localStorage.getItem(CACHE_KEY) || "null");
  } catch {
    return null;
  }
}

function writeCache(entry) {
  try {
    if (entry) window.localStorage.setItem(CACHE_KEY, JSON.stringify(entry));
    else window.localStorage.removeItem(CACHE_KEY);
  } catch {
    // Ohne Storage erscheint die Anzeige erst nach dem Laden.
  }
}

function formatInt(value) {
  return Math.round(Number(value) || 0).toLocaleString("de-DE");
}

function formatFactor(value) {
  return `×${Number(value).toLocaleString("de-DE", { maximumFractionDigits: 2 })}`;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;",
  }[char]));
}

function getRoot() {
  return document.querySelector("[data-xp-indicator]");
}

function levelProgress(data) {
  const start = Number(data?.levelStartXp) || 0;
  const next = Number(data?.nextLevelXp) || start + 1;
  const total = Number(data?.totalXp) || 0;
  const span = Math.max(next - start, 1);
  return {
    ratio: Math.min(Math.max((total - start) / span, 0), 1),
    remaining: Math.max(next - total, 0),
  };
}

function renderPopover(root, data) {
  const popover = root.querySelector("[data-xp-popover]");
  if (!popover) return;
  const { ratio, remaining } = levelProgress(data);
  const level = Number(data.level) || 1;
  const rules = data.rules || {};
  const weights = rules.weights || {};
  const byType = data.byType || {};

  const ruleItems = Object.keys(TYPE_LABELS)
    .filter((type) => Number(weights[type]) > 0)
    .map((type) => {
      const own = Number(byType[type]) || 0;
      return `<li><span>${TYPE_LABELS[type]}</span><span>bis ${formatInt(weights[type])} ${TYPE_UNITS[type]}</span><span class="topbar-xp-popover__own">${formatInt(own)}</span></li>`;
    })
    .join("");

  const gap = Number(rules.repeatGapHours) || 20;
  const lateAfter = Number(rules.repeatLateAfter) || 3;

  popover.innerHTML = `
    <div class="topbar-xp-popover__head">
      <strong>Stufe ${level}</strong>
      <span>${formatInt(data.totalXp)} XP</span>
    </div>
    <div class="topbar-xp-popover__bar" aria-hidden="true"><span style="width:${(ratio * 100).toFixed(1)}%"></span></div>
    <p class="topbar-xp-popover__hint">Noch ${formatInt(remaining)} XP bis Stufe ${level + 1}</p>
    <p class="topbar-xp-popover__title">So gibt es XP <span>deine XP</span></p>
    <ul class="topbar-xp-popover__rules">${ruleItems}</ul>
    <p class="topbar-xp-popover__note">
      Erstmals geschafft: ${escapeHtml(formatFactor(rules.firstSuccessFactor ?? 1.5))}.
      Wiederholung innerhalb von ${gap}&nbsp;h: ${escapeHtml(formatFactor(rules.repeatFactor ?? 0.5))},
      ab der ${lateAfter}.: ${escapeHtml(formatFactor(rules.repeatLateFactor ?? 0.25))}.
      Wiederholungen nach ${gap}&nbsp;h zählen wieder voll.
    </p>`;
}

function render(root, data) {
  const { ratio, remaining } = levelProgress(data);
  const level = Number(data.level) || 1;
  const total = Number(data.totalXp) || 0;
  const ring = root.querySelector("[data-xp-ring]");
  const dash = `${(ratio * 100).toFixed(2)} 100`;
  if (ring) ring.style.strokeDasharray = dash;
  const levelNode = root.querySelector("[data-xp-level]");
  if (levelNode) levelNode.textContent = String(level);

  const summaryNode = root.querySelector("summary");
  const label = `Stufe ${level} · ${formatInt(total)} XP · noch ${formatInt(remaining)} XP bis Stufe ${level + 1}`;
  summaryNode?.setAttribute("aria-label", label);
  summaryNode?.setAttribute("title", label);
  renderPopover(root, data);
  root.hidden = false;
  if (currentUserId) writeCache({ userId: currentUserId, level, dash, label });
}

function getToastStack(root) {
  let stack = document.querySelector(".xp-toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "xp-toast-stack";
    stack.setAttribute("role", "status");
    stack.setAttribute("aria-live", "polite");
    document.body.appendChild(stack);
  }
  // Direkt unter dem Ring; ist die Kopfzeile ausgeblendet (Vollbild), oben rechts.
  const ringRect = root?.querySelector(".topbar-xp__ring")?.getBoundingClientRect();
  if (ringRect && ringRect.width > 0) {
    stack.style.top = `${Math.round(ringRect.bottom + 6)}px`;
    stack.style.left = `${Math.round(ringRect.left + ringRect.width / 2)}px`;
    stack.style.right = "auto";
    stack.classList.add("is-anchored");
  } else {
    stack.style.top = "";
    stack.style.left = "";
    stack.style.right = "";
    stack.classList.remove("is-anchored");
  }
  return stack;
}

function showToast(root, html, variant = "gain") {
  const toast = document.createElement("div");
  toast.className = `xp-toast xp-toast--${variant}`;
  toast.innerHTML = html;
  getToastStack(root).appendChild(toast);
  window.setTimeout(() => toast.remove(), variant === "level" ? 3600 : 2000);
}

function pulse(root, className) {
  root.classList.remove(className);
  void root.offsetWidth;
  root.classList.add(className);
  window.setTimeout(() => root.classList.remove(className), 1200);
}

function announce(root, previous, next, gain) {
  const gained = Number(gain?.xp) || 0;
  if (gained > 0) {
    const kindLabel = FACTOR_LABELS[gain.factorKind] || "";
    const factorText = kindLabel && gain.factor != null ? `${kindLabel} ${formatFactor(gain.factor)}` : "";
    const typeLabel = LABELED_TYPES.has(gain.activityType) ? TYPE_LABELS[gain.activityType] : "";
    const meta = [typeLabel, factorText].filter(Boolean).join(" · ");
    showToast(root, `<strong>+${formatInt(gained)}</strong>${meta ? `<span>${escapeHtml(meta)}</span>` : ""}`);
    pulse(root, "is-gaining");
  }
  const newLevel = Number(next?.level) || 1;
  if (previous && newLevel > (Number(previous.level) || 1)) {
    showToast(root, `<strong>Stufe ${newLevel}!</strong>`, "level");
    pulse(root, "is-leveling");
  }
}

function applySummary(data, gain = null) {
  const root = getRoot();
  if (!root || !data) return;
  const previous = summary;
  // Antworten können sich überholen; die Summe wächst nur, ein älterer Stand wird nicht angezeigt.
  if (previous && (Number(data.totalXp) || 0) < (Number(previous.totalXp) || 0)) {
    announce(root, null, data, gain);
    return;
  }
  summary = data;
  lastLoadedAt = Date.now();
  render(root, data);
  if (previous) announce(root, previous, data, gain);
}

async function load() {
  const root = getRoot();
  if (!root || !currentUserId) return;
  const userAtStart = currentUserId;
  const result = await getUserXpSummary();
  if (userAtStart !== currentUserId) return;
  if (!result.ok || !result.data) {
    if (!summary && readCache()?.userId !== currentUserId) root.hidden = true;
    return;
  }
  applySummary(result.data);
}

function enqueue(task) {
  queue = queue.then(task).catch(() => {});
  return queue;
}

function bindListeners() {
  if (listenersBound) return;
  listenersBound = true;

  window.addEventListener(XP_AWARDED_EVENT, (event) => {
    if (!currentUserId) return;
    const data = event?.detail;
    if (!data || typeof data !== "object") return;
    enqueue(() => applySummary(data, data.award || null));
  });

  window.addEventListener("focus", () => {
    if (!currentUserId || Date.now() - lastLoadedAt < REFRESH_ON_FOCUS_MS) return;
    enqueue(() => load());
  });

  document.addEventListener("click", (event) => {
    const root = getRoot();
    if (root?.open && !root.contains(event.target)) root.open = false;
  });

  document.addEventListener("keydown", (event) => {
    const root = getRoot();
    if (event.key === "Escape" && root?.open) root.open = false;
  });
}

export function syncXpIndicator(authState) {
  const root = getRoot();
  if (!root) return;
  bindListeners();

  // Anmeldedienst nicht erreichbar: zwischengespeicherten Stand stehen lassen.
  if (authState?.error) return;

  const userId = authState?.user?.id || null;
  if (!userId) {
    currentUserId = null;
    summary = null;
    writeCache(null);
    root.hidden = true;
    root.open = false;
    return;
  }
  if (userId === currentUserId && summary) return;

  // Stand eines anderen Kontos aus dem Zwischenspeicher nicht anzeigen.
  if (readCache()?.userId !== userId) root.hidden = true;
  currentUserId = userId;
  summary = null;
  enqueue(() => load());
}
