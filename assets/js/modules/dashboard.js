import { initCardMenuDismiss } from "./ui/card-actions-menu.js";
import { getUserRecallProficiency, getUserFeynmanProficiency } from "../platform/progress-client.js?v=20260719-feynman-graph-fix";
import {
  FEED_STEP_ORDER,
  buildFeedContentMetaFromLernbereiche as buildSharedFeedContentMeta,
  loadFeedProjection,
  rememberManualRetentionPriority,
} from "../platform/feed-projection.js?v=20260606-retention-status";
import { getDefaultSystemSettings, loadSystemSettings } from "../platform/system-settings.js?v=20260603-activities-cleanup";
import { buildAccountUrl, formatAuthDisplayName, getCurrentAuthState, getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js?v=20260520-feed-loading";

const FEED_BADGE_UPDATE_EVENT = "mathechecks:feed-updated";
const LERNBEREICH_ALIASES = {
  "differentialrechnung-ganzrationaler-funktionen": ["differentialrechnung"],
  "zufallsexperimente-und-wahrscheinlichkeiten": ["zufallsexperimente"],
};

const CHECK_PIPELINE_STEP_COUNT = Object.keys(FEED_STEP_ORDER).length;
const DATE_ONLY_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;
const SESSION_EMPTY_SUMMARY = "Aktuell ist keine Session aktiv.";
const SESSION_EMPTY_LIST_MESSAGE = "Wähle Lernbereiche über Bearbeiten aus.";
const RETENTION_EMPTY_SUMMARY = "Aktuell ist keine Wiederholung aktiv.";
const RETENTION_EMPTY_LIST_MESSAGE = "Wähle Lernbereiche für Wiederholungen über Bearbeiten aus.";
const RETENTION_LOADING_MESSAGE = "Wiederholungen werden geladen.";
const RETENTION_UNAVAILABLE_MESSAGE = "Wiederholungen konnten gerade nicht geladen werden.";
const RETENTION_LOAD_ERROR_MESSAGE = "Der Wiederholungsstand konnte gerade nicht geladen werden.";
const ACTIVITY_SUMMARY_EMPTY = "Sobald du Training, Recall, Feynman oder Flashcards abschließt, erscheinen sie hier accountgebunden.";
const ACTIVITY_UNAVAILABLE_MESSAGE = "Die Aktivitätsstatistik ist gerade nicht verfügbar.";
const ACTIVITY_LOAD_ERROR_MESSAGE = "Die Aktivitätsstatistik konnte gerade nicht geladen werden.";
const ACTIVITY_MAP_SUMMARY_COPY = "Aktivitätskalender dieses Monats";
const ACTIVITY_MAP_EMPTY_SUMMARY = "Dieser Monat erscheint hier als Kalender. Sobald Aktivitäten erfasst werden, füllt sich die Karte automatisch.";
const ACTIVITY_MAP_EMPTY_WINDOW_SUMMARY = "In diesem Kalenderfenster wurden noch keine Aktivitäten erfasst.";
const ACTIVITY_MAP_DEFAULT_WEEKS = 6;
const ACTIVITY_MAP_DAY_LABELS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
const GREETING_TIME_VARIANTS = [
  {
    key: "morning",
    startHour: 4,
    endHour: 12,
    variants: [
      "Hey {name}, so früh schon am Werk?",
      "Guten Morgen {name}.",
      "Hi {name}, was steht heute an?",
    ],
  },
  {
    key: "daytime",
    startHour: 12,
    endHour: 18,
    variants: [
      "Hi {name}, eine Runde Mathe checken?",
      "Guten Tag {name}.",
      "Check am Nachmittag? Gute Idee, {name}.",
    ],
  },
  {
    key: "evening",
    startHour: 18,
    endHour: 23,
    variants: [
      "Guten Abend {name}.",
      "Hey {name}, Mathe am Abend? Gute Wahl.",
      "Heute Abend Mathe checken, {name}?",
    ],
  },
  {
    key: "late-night",
    startHour: 23,
    endHour: 4,
    variants: [
      "Die Nachteule {name} ist aktiv.",
      "Zu später Stunde noch aktiv, {name}? Respekt.",
      "Mathematische Träume, {name}?",
    ],
  },
];
const GREETING_EVENT_VARIANTS = {
  streak1: [
    "Hey {name}, los geht's.",
    "Hey {name}, der Anfang ist gemacht!",
    "Hi {name}, ab jetzt wird Mathe gecheckt.",
  ],
  streak3: [
    "Drei Tage am Stück, {name}. Das ist kein Zufall mehr.",
    "Drei Tage in Folge. Weiter so.",
    "Hi {name}, drei Tage nacheinander. Läuft.",
  ],
  streak7: [
    "Eine Woche, {name}. Aus Vorsatz wird Gewohnheit.",
    "7 Tage am Stück, {name}. Respekt.",
    "Eine volle Woche dran geblieben. Sauber.",
  ],
  streak14: [
    "Zwei Wochen, {name}. Du machst das ernsthaft.",
    "14 Tage am Stück. Das nennt man Routine.",
    "Hey {name}, zwei Wochen drangeblieben. Sehr gut.",
  ],
  streak30: [
    "30 Tage am Stück. Du meinst es wirklich ernst.",
    "Ein Monat Streak, {name}. Schwer, das noch Zufall zu nennen.",
    "30 Tage in Folge {name}, klasse!",
  ],
  streak100: [
    "Hallo {name}, 100 Tage. Wir müssen reden, über deine Zukunft als Mathematiker.",
  ],
  missedYesterday: [
    "Da bist du wieder, {name}. Weiter geht´s.",
    "Hey {name}, gestern war Pause. Heute geht's weiter.",
    "Hi {name}, es ist wieder Zeit, Mathe zu checken.",
  ],
  longPause: [
    "Hallo {name}, schön dich wiederzusehen.",
    "Willkommen zurück, {name}.",
    "{name} ist wieder da!",
  ],
  streakAtRisk: [
    "Hey {name}, halte den Streak am Laufen.",
    "Der Tag läuft, der Streak auch. Noch zumindest.",
    "Heute noch eine Aktivität, {name}, und der Streak lebt weiter.",
  ],
};
const GREETING_PROGRESS_VARIANTS = {
  yesterdayBusy: [
    "Du warst gestern fleißig {name}, weiter so.",
    "Hey {name}, gestern war stark!",
    "Viel erledigt gestern. Ein kleiner Schritt heute hält den Takt.",
  ],
  sessionPressureHigh: [
    "Hi {name}, dein Plan ist gerade recht ambitioniert.",
    "Hallo {name}, das Zieldatum schaut gerade ziemlich ernst.",
    "Heute wird Mathe gecheckt!",
  ],
  sessionPressureMedium: [
    "Dein Plan ist machbar, {name}, aber er wartet nicht.",
    "Hey {name}, gerade ist es eher sportlich als gemütlich.",
    "Heute wäre ein guter Tag für ein paar Aktivitäten.",
  ],
  sessionSmooth: [
    "Alles läuft, {name}. Einfach weitermachen.",
    "Gut im Plan, {name}. Weiter so.",
    "Respekt {name}, du bist gut in der Zeit.",
  ],
  sessionDone: [
    "Glückwunsch {name}, Session abgeschlossen.",
    "Toll {name}, du hast die Session erfolgreich beendet.",
    "Gut gemacht {name}, die Session ist finished.",
  ],
};
const GREETING_FALLBACK_VARIANTS = [
  "Na, {name}. Bereit?",
  "Schön, dass du da bist, {name}.",
  "Hey {name}!",
  "Hallo {name}.",
];
const GREETING_STREAK_MILESTONES = [100, 30, 14, 7];
const GREETING_LONG_PAUSE_DAYS = 7;
const GREETING_BUSY_YESTERDAY_THRESHOLD = 5;
const GREETING_CONFIDENT_PROGRESS_PERCENT = 35;
const GREETING_ROTATION_STEP_HOURS = 3;
const GREETING_STORAGE_PREFIX = "mathechecks:greeting-first-seen";
const WORKLIST_SESSION_ONLY_STORAGE_KEY = "mathechecks:dashboard-worklist-session-only";

function readWorklistSessionOnlyPreference() {
  if (typeof window === "undefined" || !window.localStorage) return true;
  try {
    const storedValue = window.localStorage.getItem(WORKLIST_SESSION_ONLY_STORAGE_KEY);
    if (storedValue === "false") return false;
    if (storedValue === "true") return true;
  } catch {
    // Ignore storage failures and keep the default behavior.
  }
  return true;
}

function writeWorklistSessionOnlyPreference(sessionOnly) {
  if (typeof window === "undefined" || !window.localStorage) return;
  try {
    window.localStorage.setItem(WORKLIST_SESSION_ONLY_STORAGE_KEY, sessionOnly ? "true" : "false");
  } catch {
    // Ignore storage failures; the in-memory toggle still works.
  }
}

function notifyFeedBadgeRefresh() {
  if (typeof window === "undefined" || typeof CustomEvent !== "function") return;
  window.dispatchEvent(new CustomEvent(FEED_BADGE_UPDATE_EVENT));
}

function parseJsonScript(id, fallback) {
  try {
    return JSON.parse(document.getElementById(id)?.textContent || JSON.stringify(fallback));
  } catch {
    return fallback;
  }
}

function normalizeKey(value) {
  return String(value || "")
    .toLowerCase()
    .trim()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function cloneState(state) {
  return JSON.parse(JSON.stringify(state || {}));
}

function buildGreetingCandidate(key, variants) {
  const options = Array.isArray(variants) ? variants.filter(Boolean) : [];
  if (!options.length) return null;

  return {
    key,
    variants: options,
  };
}

function pickRandomInteger(count) {
  const normalizedCount = Math.max(0, Number(count) || 0);
  if (normalizedCount <= 1) return 0;
  return Math.floor(Math.random() * normalizedCount);
}

function createRandomGreetingSelection(key, variants, refreshMode = "rotation-only") {
  const candidate = buildGreetingCandidate(key, variants);
  if (!candidate) return null;

  const variantIndex = pickRandomInteger(candidate.variants.length);
  return {
    key: candidate.key,
    template: candidate.variants[variantIndex] || candidate.variants[0],
    variantCount: candidate.variants.length,
    refreshMode,
  };
}

function pickGreetingVariant(variants, context, todayDateValue, date = new Date()) {
  const options = Array.isArray(variants) ? variants.filter(Boolean) : [];
  if (!options.length) return "";

  const variantIndex = getGreetingVariantIndex(context, todayDateValue, options.length, date);
  return options[variantIndex] || options[0];
}

function renderGreetingTemplate(template, displayName) {
  const safeName = `<span data-dashboard-greeting-name>${escapeHtml(displayName)}</span>`;
  return String(template || "")
    .split("{name}")
    .map((part) => escapeHtml(part))
    .join(safeName);
}

function getGreetingDisplayName(user) {
  const fullName = String(user ? formatAuthDisplayName(user) : "").trim();
  const firstName = fullName.split(/\s+/).find(Boolean) || "";
  return firstName || "Schüler:in";
}

function getBaseClassName(node) {
  if (!node) return "";
  if (!node.dataset.baseClass) {
    node.dataset.baseClass = node.className;
  }
  return node.dataset.baseClass;
}

function setStatusNode(node, message, tone = "neutral") {
  if (!node) return;

  const text = String(message || "").trim();
  node.className = getBaseClassName(node);
  node.hidden = !text;
  node.textContent = text;

  if (!text) return;
  if (tone === "success") node.classList.add("is-success");
  if (tone === "warning") node.classList.add("is-warning");
  if (tone === "error") node.classList.add("is-error");
}

function buildGebietMeta(gebiete) {
  return Object.fromEntries(
    (Array.isArray(gebiete) ? gebiete : []).map((gebiet) => [gebiet.key, {
      group: gebiet.name,
      order: Number.isFinite(Number(gebiet.order)) ? Number(gebiet.order) : 999,
      icon: gebiet.icon,
      iconBg: gebiet.icon_bg,
      iconColor: gebiet.icon_color,
      color: gebiet.chip_color,
    }]),
  );
}

function buildCheckIndex(checks) {
  const index = new Map();

  const add = (rawKey, check) => {
    const key = normalizeKey(rawKey);
    if (!key || !check?.id) return;

    if (!index.has(key)) {
      index.set(key, []);
    }

    const list = index.get(key);
    if (!list.some((entry) => entry.id === check.id)) {
      list.push(check);
    }
  };

  (Array.isArray(checks) ? checks : []).forEach((entry) => {
    const checkId = String(entry?.check_id || "").trim();
    const label = String(entry?.["Ich kann"] || "").trim();
    const shortTitle = String(entry?.Schlagwort || "").trim();
    const numberValue = Number(entry?.Nummer);
    if (!checkId || !label) return;

    const check = {
      id: checkId,
      label,
      shortTitle,
      number: Number.isFinite(numberValue) ? numberValue : null,
    };
    add(entry?.Lernbereich, check);
    add(entry?.LernbereichAnzeigename, check);
  });

  return index;
}

function buildLernbereicheFromData(checks, gebiete, lernbereicheSource) {
  const gebietMeta = buildGebietMeta(gebiete);
  const checkIndex = buildCheckIndex(checks);
  const grouped = new Map();

  (Array.isArray(lernbereicheSource) ? lernbereicheSource : []).forEach((lernbereich) => {
    const meta = gebietMeta[lernbereich.gebiet];
    if (!meta) return;

    if (!grouped.has(lernbereich.gebiet)) {
      grouped.set(lernbereich.gebiet, {
        group: meta.group,
        order: meta.order,
        icon: meta.icon,
        iconBg: meta.iconBg,
        iconColor: meta.iconColor,
        items: [],
      });
    }

    const candidates = [
      lernbereich.slug,
      lernbereich.name,
      ...(LERNBEREICH_ALIASES[lernbereich.slug] || []),
    ]
      .map(normalizeKey)
      .filter(Boolean);

    const checksById = new Map();
    candidates.forEach((candidate) => {
      (checkIndex.get(candidate) || []).forEach((check) => {
        if (!checksById.has(check.id)) {
          checksById.set(check.id, check);
        }
      });
    });

    grouped.get(lernbereich.gebiet).items.push({
      id: lernbereich.slug,
      name: lernbereich.name,
      gebietKey: lernbereich.gebiet,
      gebietOrder: meta.order,
      color: meta.color,
      didacticOrder: lernbereich.didactic_order ?? null,
      checks: Array.from(checksById.values()),
    });
  });

  return Array.from(grouped.values())
    .map((group) => ({
      ...group,
      items: [...group.items].sort((left, right) => {
        const leftOrder = Number.isFinite(Number(left.didacticOrder)) ? Number(left.didacticOrder) : 999;
        const rightOrder = Number.isFinite(Number(right.didacticOrder)) ? Number(right.didacticOrder) : 999;
        if (leftOrder !== rightOrder) return leftOrder - rightOrder;
        return String(left.name || "").localeCompare(String(right.name || ""), "de");
      }),
    }))
    .sort((left, right) => {
      if (left.order !== right.order) return left.order - right.order;
      return String(left.group || "").localeCompare(String(right.group || ""), "de");
    });
}

function isCheckSelected(lbState, checkId) {
  return lbState?.checks?.[checkId] !== false;
}

function countSelectedChecks(lb, lbState) {
  return lb.checks.filter((check) => isCheckSelected(lbState, check.id)).length;
}

function setGreetingName(user) {
  const node = document.querySelector("[data-dashboard-greeting-name]");
  if (!node) return;

  node.textContent = getGreetingDisplayName(user);
}

function setGreetingDate(date = new Date()) {
  const node = document.querySelector("[data-dashboard-current-date]");
  if (!node) return;

  node.textContent = new Intl.DateTimeFormat("de-DE", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(date);
}

function applyStreakBadge(context, date = new Date()) {
  const badgeEl = context?.elements?.streakBadge;
  const countEl = context?.elements?.streakCount;
  if (!badgeEl) return;

  const snapshot = buildGreetingSnapshot(context, date);
  const streak = snapshot.recentStreakLength;

  // Zustand bestimmen
  let state;
  if (streak <= 0) {
    state = "none";
  } else if (snapshot.todayCount > 0) {
    state = "done";
  } else if (snapshot.lastActivityDate === snapshot.yesterdayDateValue) {
    state = "pending";
  } else {
    // Streak > 0 aber letzter Tag liegt weiter zurück → erloschen
    state = "none";
  }

  badgeEl.dataset.streakState = state;
  if (countEl) {
    countEl.textContent = streak > 0 ? String(streak) : "";
  }
  badgeEl.setAttribute("aria-label",
    state === "done" ? `Streak: ${streak} Tage, heute aktiv` :
    state === "pending" ? `Streak: ${streak} Tage, heute noch offen` :
    "Kein aktiver Streak"
  );
}

function shiftDateByDays(date, dayOffset) {
  const nextDate = date instanceof Date ? new Date(date) : new Date();
  nextDate.setDate(nextDate.getDate() + (Number(dayOffset) || 0));
  return nextDate;
}

function isGreetingHourInWindow(hour, startHour, endHour) {
  if (startHour === endHour) return true;
  if (startHour < endHour) {
    return hour >= startHour && hour < endHour;
  }
  return hour >= startHour || hour < endHour;
}

function getGreetingTimeWindow(hour) {
  return GREETING_TIME_VARIANTS.find((entry) => {
    return isGreetingHourInWindow(hour, entry.startHour, entry.endHour);
  }) || null;
}

function getActivityCountByDate(entries, dateValue) {
  const normalizedDateValue = normalizeDateOnlyValue(dateValue);
  if (!normalizedDateValue) return 0;

  return Math.max(
    0,
    Number(
      (Array.isArray(entries) ? entries : []).find((entry) => normalizeDateOnlyValue(entry?.date) === normalizedDateValue)?.count,
    ) || 0,
  );
}

function getStreakLengthEndingOnDate(overview, endDateValue) {
  const normalizedEndDate = normalizeDateOnlyValue(endDateValue);
  if (!normalizedEndDate) return 0;

  const mapData = normalizeActivityMap(overview);
  const countByDate = new Map(
    (Array.isArray(mapData?.days) ? mapData.days : []).map((entry) => [
      normalizeDateOnlyValue(entry?.date),
      Math.max(0, Number(entry?.count) || 0),
    ]),
  );

  let streakLength = 0;
  const cursor = parseDateOnlyValue(normalizedEndDate);
  while (cursor instanceof Date && !Number.isNaN(cursor.getTime())) {
    const dateValue = toDateOnlyValue(cursor);
    if ((countByDate.get(dateValue) || 0) <= 0) break;
    streakLength += 1;
    cursor.setDate(cursor.getDate() - 1);
  }

  const longestStreakEndDate = normalizeDateOnlyValue(overview?.longestStreak?.endDate);
  const longestStreakLength = Math.max(0, Number(overview?.longestStreak?.length) || 0);
  if (longestStreakEndDate === normalizedEndDate) {
    return Math.max(streakLength, longestStreakLength);
  }

  return streakLength;
}

function getGreetingUserSeed(context) {
  const user = context?.authState?.user;
  return String(user?.id || (user ? formatAuthDisplayName(user) : "") || "guest").trim() || "guest";
}

function getGreetingStorageKey(context, todayDateValue) {
  const normalizedDateValue = normalizeDateOnlyValue(todayDateValue) || toDateOnlyValue(new Date());
  return `${GREETING_STORAGE_PREFIX}|${normalizedDateValue}|${getGreetingUserSeed(context)}`;
}

function readGreetingStorageState(context, todayDateValue, date = new Date()) {
  const now = date instanceof Date && !Number.isNaN(date.getTime()) ? new Date(date) : new Date();
  const normalizedDateValue = normalizeDateOnlyValue(todayDateValue) || toDateOnlyValue(now);
  const fallbackState = {
    firstSeenAt: now,
    selections: {},
  };

  if (typeof window === "undefined" || !window.localStorage) {
    return fallbackState;
  }

  try {
    const storageKey = getGreetingStorageKey(context, normalizedDateValue);
    const storedValue = window.localStorage.getItem(storageKey);
    if (storedValue) {
      let parsedValue = null;
      try {
        parsedValue = JSON.parse(storedValue);
      } catch {
        parsedValue = null;
      }

      const firstSeenValue = parsedValue && typeof parsedValue === "object"
        ? parsedValue.firstSeenAt
        : storedValue;
      const firstSeenAt = new Date(String(firstSeenValue || ""));
      if (!Number.isNaN(firstSeenAt.getTime()) && toDateOnlyValue(firstSeenAt) === normalizedDateValue) {
        const selections = parsedValue && typeof parsedValue.selections === "object" && parsedValue.selections
          ? parsedValue.selections
          : {};
        return {
          firstSeenAt,
          selections,
        };
      }
    }

    window.localStorage.setItem(storageKey, JSON.stringify({
      firstSeenAt: now.toISOString(),
      selections: {},
    }));
  } catch {
    return fallbackState;
  }

  return fallbackState;
}

function writeGreetingStorageState(context, todayDateValue, state) {
  if (typeof window === "undefined" || !window.localStorage) {
    return;
  }

  const normalizedDateValue = normalizeDateOnlyValue(todayDateValue) || toDateOnlyValue(new Date());
  const firstSeenAt = state?.firstSeenAt instanceof Date && !Number.isNaN(state.firstSeenAt.getTime())
    ? state.firstSeenAt
    : new Date(String(state?.firstSeenAt || ""));
  if (Number.isNaN(firstSeenAt.getTime())) {
    return;
  }

  const selections = state && typeof state.selections === "object" && state.selections
    ? state.selections
    : {};

  try {
    window.localStorage.setItem(getGreetingStorageKey(context, normalizedDateValue), JSON.stringify({
      firstSeenAt: firstSeenAt.toISOString(),
      selections,
    }));
  } catch {
    // Ignore storage write failures and fall back to in-memory behavior.
  }
}

function getStoredGreetingSelection(context, todayDateValue, selectionKey, date = new Date()) {
  const state = readGreetingStorageState(context, todayDateValue, date);
  const selection = state?.selections?.[selectionKey];
  if (!selection || typeof selection.template !== "string") {
    return null;
  }

  return {
    key: String(selection.key || "").trim(),
    template: selection.template,
    variantCount: Math.max(1, Number(selection.variantCount) || 1),
    refreshMode: String(selection.refreshMode || "rotation-only").trim() || "rotation-only",
  };
}

function storeGreetingSelection(context, todayDateValue, selectionKey, selection, date = new Date()) {
  if (!selectionKey || !selection?.template) {
    return selection;
  }

  const state = readGreetingStorageState(context, todayDateValue, date);
  const nextState = {
    firstSeenAt: state.firstSeenAt,
    selections: {
      ...state.selections,
      [selectionKey]: {
        key: selection.key,
        template: selection.template,
        variantCount: selection.variantCount,
        refreshMode: selection.refreshMode,
      },
    },
  };
  writeGreetingStorageState(context, todayDateValue, nextState);
  return selection;
}

function getGreetingFirstSeenAt(context, todayDateValue, date = new Date()) {
  return readGreetingStorageState(context, todayDateValue, date).firstSeenAt;
}

function getUsedGreetingCategoryKeys(context, todayDateValue, date) {
  const state = readGreetingStorageState(context, todayDateValue, date);
  const keys = new Set();
  for (const sel of Object.values(state.selections || {})) {
    if (sel?.key) keys.add(sel.key);
  }
  return keys;
}

function getGreetingStepIndex(context, todayDateValue, date = new Date()) {
  const now = date instanceof Date && !Number.isNaN(date.getTime()) ? new Date(date) : new Date();
  const firstSeenAt = getGreetingFirstSeenAt(context, todayDateValue, now);
  const stepMs = GREETING_ROTATION_STEP_HOURS * 60 * 60 * 1000;
  if (stepMs <= 0) return 0;

  return Math.max(0, Math.floor(Math.max(0, now.getTime() - firstSeenAt.getTime()) / stepMs));
}

function getGreetingVariantIndex(context, todayDateValue, variantCount, date = new Date()) {
  const count = Math.max(0, Number(variantCount) || 0);
  if (count <= 1) return 0;

  const nextIndex = getGreetingStepIndex(context, todayDateValue, date);

  return Math.min(nextIndex, count - 1);
}

function buildGreetingSelection(context, snapshot, key, variants) {
  const candidate = buildGreetingCandidate(key, variants);
  if (!candidate) return null;

  return {
    key: candidate.key,
    template: pickGreetingVariant(candidate.variants, context, snapshot.todayDateValue, snapshot.now),
    variantCount: candidate.variants.length,
    refreshMode: "default",
  };
}

function buildGreetingSnapshot(context, date = new Date()) {
  const now = date instanceof Date && !Number.isNaN(date.getTime()) ? new Date(date) : new Date();
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);

  const todayDateValue = toDateOnlyValue(today);
  const yesterdayDateValue = toDateOnlyValue(shiftDateByDays(today, -1));
  const dayBeforeYesterdayDateValue = toDateOnlyValue(shiftDateByDays(today, -2));
  const overview = context?.activityOverview;
  const recentEntries = normalizeActivityOverviewDays(overview);
  const todayCount = getActivityCountByDate(recentEntries, todayDateValue);
  const yesterdayCount = getActivityCountByDate(recentEntries, yesterdayDateValue);
  const lastActivityDate = normalizeDateOnlyValue(overview?.lastActivityDate);
  const totalCount = Math.max(0, Number(overview?.totalCount) || 0);
  const progress = buildActiveSessionProgress(context);

  let daysSinceLastActivity = Number.POSITIVE_INFINITY;
  if (lastActivityDate) {
    const lastActivity = parseDateOnlyValue(lastActivityDate);
    if (lastActivity instanceof Date && !Number.isNaN(lastActivity.getTime())) {
      lastActivity.setHours(0, 0, 0, 0);
      daysSinceLastActivity = Math.floor((today.getTime() - lastActivity.getTime()) / 86400000);
    }
  }

  let targetAssessment = null;
  if (context?.activeSession) {
    const { selectedCheckIds, activeLernbereichIds } = summarizeActivePlan(context);
    if (selectedCheckIds.length || activeLernbereichIds.length) {
      targetAssessment = buildTargetDateAssessment(context, selectedCheckIds, activeLernbereichIds);
    }
  }

  return {
    now,
    hour: now.getHours(),
    todayDateValue,
    yesterdayDateValue,
    dayBeforeYesterdayDateValue,
    todayCount,
    yesterdayCount,
    lastActivityDate,
    totalCount,
    daysSinceLastActivity,
    recentStreakLength: getStreakLengthEndingOnDate(overview, lastActivityDate),
    hasActiveSession: Boolean(context?.activeSession),
    progress,
    targetAssessment,
    hasOverdueChecks: (Array.isArray(context?.sessionCheckStates) ? context.sessionCheckStates : []).some(
      (row) => String(row?.current_step_status || "").trim() === "due" && row?.overdue_from && new Date(row.overdue_from).getTime() <= now.getTime(),
    ),
  };
}

function resolveGreetingStreakCandidate(snapshot) {
  if (snapshot.todayCount > 0 && snapshot.lastActivityDate === snapshot.todayDateValue) {
    const milestone = GREETING_STREAK_MILESTONES.find((value) => snapshot.recentStreakLength === value);
    if (milestone) {
      const key = `streak${milestone}`;
      return buildGreetingCandidate(key, GREETING_EVENT_VARIANTS[key]);
    }
  }

  return null;
}

function resolveGreetingSecondaryEventCandidate(snapshot) {
  if (snapshot.totalCount <= 0 || snapshot.todayCount > 0) {
    return null;
  }

  if (snapshot.daysSinceLastActivity >= GREETING_LONG_PAUSE_DAYS) {
    return buildGreetingCandidate("longPause", GREETING_EVENT_VARIANTS.longPause);
  }

  if (snapshot.lastActivityDate === snapshot.dayBeforeYesterdayDateValue) {
    return buildGreetingCandidate("missedYesterday", GREETING_EVENT_VARIANTS.missedYesterday);
  }

  if (
    snapshot.lastActivityDate === snapshot.yesterdayDateValue
    && snapshot.recentStreakLength >= 2
    && snapshot.hour >= 18
  ) {
    return buildGreetingCandidate("streakAtRisk", GREETING_EVENT_VARIANTS.streakAtRisk);
  }

  return null;
}

function resolveGreetingProgressCandidate(snapshot) {
  if (snapshot.hasActiveSession && snapshot.progress && snapshot.progress.remainingStepCount <= 0) {
    return buildGreetingCandidate("sessionDone", GREETING_PROGRESS_VARIANTS.sessionDone);
  }

  if (snapshot.todayCount === 0 && snapshot.yesterdayCount >= GREETING_BUSY_YESTERDAY_THRESHOLD) {
    return buildGreetingCandidate("yesterdayBusy", GREETING_PROGRESS_VARIANTS.yesterdayBusy);
  }

  if (snapshot.targetAssessment?.assessmentTone === "error") {
    return buildGreetingCandidate("sessionPressureHigh", GREETING_PROGRESS_VARIANTS.sessionPressureHigh);
  }

  if (snapshot.targetAssessment?.assessmentTone === "warning") {
    return buildGreetingCandidate("sessionPressureMedium", GREETING_PROGRESS_VARIANTS.sessionPressureMedium);
  }

  if (
    snapshot.targetAssessment?.assessmentTone === "success"
    && snapshot.progress
    && snapshot.progress.remainingStepCount > 0
    && snapshot.progress.percent >= GREETING_CONFIDENT_PROGRESS_PERCENT
    && !snapshot.hasOverdueChecks
  ) {
    return buildGreetingCandidate("sessionSmooth", GREETING_PROGRESS_VARIANTS.sessionSmooth);
  }

  return null;
}

function resolveGreetingTimeCandidate(snapshot) {
  const timeWindow = getGreetingTimeWindow(snapshot.hour);
  if (!timeWindow) return null;

  return buildGreetingCandidate(`time-${timeWindow.key}`, timeWindow.variants);
}

function resolveGreetingFallbackCandidate() {
  return buildGreetingCandidate("fallback", GREETING_FALLBACK_VARIANTS);
}

function resolveGreetingEvent(context, snapshot) {
  const streakCandidate = resolveGreetingStreakCandidate(snapshot);
  if (streakCandidate) {
    return buildGreetingSelection(context, snapshot, streakCandidate.key, streakCandidate.variants);
  }

  const secondaryCandidate = resolveGreetingSecondaryEventCandidate(snapshot);
  return secondaryCandidate
    ? buildGreetingSelection(context, snapshot, secondaryCandidate.key, secondaryCandidate.variants)
    : null;
}

function resolveGreetingNonEvent(context, snapshot) {
  const stepIndex = getGreetingStepIndex(context, snapshot.todayDateValue, snapshot.now);
  const selectionKey = `nonEvent-step-${stepIndex}`;

  const stored = getStoredGreetingSelection(context, snapshot.todayDateValue, selectionKey, snapshot.now);
  if (stored) return stored;

  const candidates = [
    resolveGreetingProgressCandidate(snapshot),
    resolveGreetingTimeCandidate(snapshot),
    resolveGreetingFallbackCandidate(),
  ].filter(Boolean);

  if (!candidates.length) return null;

  const usedKeys = getUsedGreetingCategoryKeys(context, snapshot.todayDateValue, snapshot.now);
  const unused = candidates.filter((c) => !usedKeys.has(c.key));
  const pool = unused.length > 0 ? unused : candidates;

  const picked = pool[pickRandomInteger(pool.length)];
  const selection = createRandomGreetingSelection(picked.key, picked.variants);
  return storeGreetingSelection(context, snapshot.todayDateValue, selectionKey, selection, snapshot.now);
}

function getNextGreetingTimeBoundary(date = new Date()) {
  const now = date instanceof Date && !Number.isNaN(date.getTime()) ? new Date(date) : new Date();
  const boundaryHours = Array.from(new Set(GREETING_TIME_VARIANTS.map((entry) => Number(entry.startHour))))
    .filter((value) => Number.isFinite(value))
    .sort((left, right) => left - right);

  for (const hour of boundaryHours) {
    const boundary = new Date(now);
    boundary.setHours(hour, 0, 0, 0);
    if (boundary.getTime() > now.getTime()) {
      return boundary;
    }
  }

  const nextBoundary = new Date(now);
  nextBoundary.setDate(nextBoundary.getDate() + 1);
  nextBoundary.setHours(boundaryHours[0] || 0, 0, 0, 0);
  return nextBoundary;
}

function getNextGreetingMidnight(date = new Date()) {
  const now = date instanceof Date && !Number.isNaN(date.getTime()) ? new Date(date) : new Date();
  const nextMidnight = new Date(now);
  nextMidnight.setDate(nextMidnight.getDate() + 1);
  nextMidnight.setHours(0, 0, 0, 0);
  return nextMidnight;
}

function getNextGreetingRotationBoundary(context, todayDateValue, variantCount, date = new Date(), force = false) {
  const count = Math.max(0, Number(variantCount) || 0);
  if (!force && count <= 1) return null;

  const now = date instanceof Date && !Number.isNaN(date.getTime()) ? new Date(date) : new Date();
  const firstSeenAt = getGreetingFirstSeenAt(context, todayDateValue, now);
  const stepMs = GREETING_ROTATION_STEP_HOURS * 60 * 60 * 1000;
  const elapsedMs = Math.max(0, now.getTime() - firstSeenAt.getTime());
  const nextIndex = Math.floor(elapsedMs / stepMs) + 1;
  if (!force && nextIndex >= count) return null;

  return new Date(firstSeenAt.getTime() + nextIndex * stepMs);
}

function clearGreetingRefreshTimer(context) {
  if (!context?.greetingRefreshTimerId) return;
  window.clearTimeout(context.greetingRefreshTimerId);
  context.greetingRefreshTimerId = null;
}

function scheduleGreetingRefresh(context, snapshot, greeting) {
  clearGreetingRefreshTimer(context);
  if (!context || context.isGreetingHydrating) return;

  const now = snapshot?.now instanceof Date && !Number.isNaN(snapshot.now.getTime())
    ? new Date(snapshot.now)
    : new Date();
  const usesRotationOnlyRefresh = greeting?.refreshMode === "rotation-only";
  const candidates = (usesRotationOnlyRefresh
    ? [
      getNextGreetingMidnight(now),
      getNextGreetingRotationBoundary(context, snapshot?.todayDateValue, greeting?.variantCount, now, true),
    ]
    : [
      getNextGreetingMidnight(now),
      getNextGreetingTimeBoundary(now),
      getNextGreetingRotationBoundary(context, snapshot?.todayDateValue, greeting?.variantCount, now),
    ]).filter((candidate) => candidate instanceof Date && candidate.getTime() > now.getTime());

  if (!candidates.length || typeof window === "undefined") {
    return;
  }

  const nextRefreshAt = candidates.reduce((earliest, candidate) => {
    return candidate.getTime() < earliest.getTime() ? candidate : earliest;
  });
  const delay = Math.max(250, nextRefreshAt.getTime() - now.getTime() + 50);

  context.greetingRefreshTimerId = window.setTimeout(() => {
    context.greetingRefreshTimerId = null;
    updateGreetingHeading(context);
  }, delay);
}

function updateGreetingHeading(context, date = new Date()) {
  if (context?.isGreetingHydrating) {
    return;
  }

  const headingNode = context?.elements?.greetingHeading;
  if (!headingNode) {
    setGreetingName(context?.authState?.user);
    return;
  }

  const displayName = getGreetingDisplayName(context?.authState?.user);
  const snapshot = buildGreetingSnapshot(context, date);
  const greeting = resolveGreetingEvent(context, snapshot)
    || resolveGreetingNonEvent(context, snapshot)
    || buildGreetingSelection(context, snapshot, "fallback", GREETING_FALLBACK_VARIANTS);

  headingNode.innerHTML = renderGreetingTemplate(greeting.template, displayName);
  headingNode.dataset.greetingVariant = greeting.key;
  headingNode.dataset.dashboardGreetingReady = "true";
  scheduleGreetingRefresh(context, snapshot, greeting);
  applyStreakBadge(context, date);
}

function finalizeGreetingHydration(context, date = new Date()) {
  if (!context) return;
  context.isGreetingHydrating = false;
  updateGreetingHeading(context, date);
}

function buildCheckMetaById(lernbereiche) {
  const map = new Map();

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      lb.checks.forEach((check) => {
        if (map.has(check.id)) return;
        map.set(check.id, {
          checkId: check.id,
          label: check.label,
          shortTitle: check.shortTitle,
          number: check.number,
          lernbereichId: lb.id,
          lernbereichName: lb.name,
          gebietKey: lb.gebietKey,
          groupName: group.group,
        });
      });
    });
  });

  return map;
}

function buildLernbereichMetaById(lernbereiche) {
  const map = new Map();

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      if (map.has(lb.id)) return;
      map.set(lb.id, {
        lernbereichId: lb.id,
        lernbereichName: lb.name,
        gebietKey: lb.gebietKey,
        groupName: group.group,
        totalCheckCount: Array.isArray(lb.checks) ? lb.checks.length : 0,
      });
    });
  });

  return map;
}

function initProgressBars() {
  document.querySelectorAll(".skill-fill").forEach((node) => {
    requestAnimationFrame(() => {
      node.style.width = `${node.dataset.progress || 0}%`;
    });
  });
}

function bindActionCardList(listNode, fallbackHref = "") {
  if (!listNode || listNode.dataset.dashboardActionListBound === "true") return;

  const navigate = (card, event) => {
    const href = String(card?.dataset?.actionHref || fallbackHref || "").trim();
    if (!href) return;
    if (event) event.preventDefault();
    window.location.href = href;
  };

  listNode.dataset.dashboardActionListBound = "true";
  listNode.addEventListener("click", (event) => {
    if (event.target.closest("button, a")) return;

    const card = event.target.closest(".action-card");
    if (!card || !listNode.contains(card)) return;

    navigate(card);
  });

  listNode.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;

    const card = event.target.closest(".action-card");
    if (!card || !listNode.contains(card)) return;

    navigate(card, event);
  });
}

function bindNextActionButton(button, fallbackHref = "") {
  if (!button || button.dataset.dashboardNextActionBound === "true") return;

  button.dataset.dashboardNextActionBound = "true";
  button.addEventListener("click", () => {
    const href = String(button?.dataset?.actionHref || fallbackHref || "").trim();
    if (!href || button.getAttribute("aria-disabled") === "true") return;
    window.location.href = href;
  });
}

function initActionFeed(root, materialUrl) {
  bindNextActionButton(root.querySelector("[data-dashboard-primary-feed-button]"), materialUrl);
}

function createBadgeMarkup(label, type = "") {
  const safeLabel = escapeHtml(label);
  const safeType = type ? ` type-${escapeHtml(type)}` : "";
  return `<span class="action-badge${safeType}">${safeLabel}</span>`;
}

function normalizeDateOnlyValue(value) {
  const text = String(value || "").trim();
  const match = DATE_ONLY_PATTERN.exec(text);
  if (!match) return "";

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const date = new Date(year, month - 1, day);
  if (
    date.getFullYear() !== year
    || date.getMonth() !== month - 1
    || date.getDate() !== day
  ) {
    return "";
  }

  return `${match[1]}-${match[2]}-${match[3]}`;
}

function parseDateOnlyValue(value) {
  const normalized = normalizeDateOnlyValue(value);
  if (!normalized) return null;

  const [year, month, day] = normalized.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function formatDateOnlyLabel(value) {
  const date = parseDateOnlyValue(value);
  if (!date) return "";

  return new Intl.DateTimeFormat("de-DE", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(date);
}

function formatDateTimeLabel(value) {
  const date = new Date(String(value || ""));
  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("de-DE", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function toDateOnlyValue(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return "";

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addCalendarDays(date, dayCount) {
  const nextDate = new Date(date);
  nextDate.setDate(nextDate.getDate() + Math.max(0, Number(dayCount) || 0));
  return nextDate;
}

function formatPlanningRate(value) {
  return new Intl.NumberFormat("de-DE", {
    minimumFractionDigits: value < 10 && !Number.isInteger(value) ? 1 : 0,
    maximumFractionDigits: 1,
  }).format(value);
}

function formatActivityCount(value) {
  return new Intl.NumberFormat("de-DE", {
    maximumFractionDigits: 0,
  }).format(Math.max(0, Number(value) || 0));
}

function formatActivityAverage(value) {
  const numericValue = Number(value) || 0;
  return new Intl.NumberFormat("de-DE", {
    minimumFractionDigits: numericValue > 0 && !Number.isInteger(numericValue) ? 1 : 0,
    maximumFractionDigits: 1,
  }).format(Math.max(0, numericValue));
}

function formatActivityPercent(value) {
  if (!Number.isFinite(Number(value))) return "–";
  const numericValue = Math.max(0, Number(value) || 0);
  const formatted = new Intl.NumberFormat("de-DE", {
    minimumFractionDigits: numericValue > 0 && !Number.isInteger(numericValue) ? 1 : 0,
    maximumFractionDigits: 1,
  }).format(numericValue);
  return `${formatted} %`;
}

function buildEmptyActivityOverviewDays() {
  const today = new Date();
  const entries = [];

  for (let offset = 6; offset >= 0; offset -= 1) {
    const day = new Date(today);
    day.setDate(today.getDate() - offset);
    entries.push({
      date: toDateOnlyValue(day),
      count: 0,
    });
  }

  return entries;
}

function startOfWeekMonday(date) {
  const normalized = date instanceof Date ? new Date(date) : new Date();
  normalized.setHours(0, 0, 0, 0);
  const weekday = (normalized.getDay() + 6) % 7;
  normalized.setDate(normalized.getDate() - weekday);
  return normalized;
}

function getActivityMapMonthKey(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return "";
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function formatActivityMapCalendarLabel(value) {
  const date = parseDateOnlyValue(value);
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("de-DE", { month: "long", year: "numeric" }).format(date);
}

function buildEmptyActivityMapData(weeks = ACTIVITY_MAP_DEFAULT_WEEKS, anchorDateValue = "") {
  const normalizedWeeks = Math.max(1, Number(weeks) || ACTIVITY_MAP_DEFAULT_WEEKS);
  const today = parseDateOnlyValue(anchorDateValue) || new Date();
  today.setHours(0, 0, 0, 0);

  const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
  const startDate = startOfWeekMonday(monthStart);
  const endDate = new Date(startDate);
  endDate.setDate(startDate.getDate() + (normalizedWeeks * 7) - 1);

  const days = [];
  const cursor = new Date(startDate);
  while (cursor <= endDate) {
    days.push({
      date: toDateOnlyValue(cursor),
      count: 0,
    });
    cursor.setDate(cursor.getDate() + 1);
  }

  return {
    weeks: normalizedWeeks,
    todayDate: toDateOnlyValue(today),
    currentMonth: getActivityMapMonthKey(today),
    monthLabel: formatActivityMapCalendarLabel(toDateOnlyValue(today)),
    startDate: toDateOnlyValue(startDate),
    endDate: toDateOnlyValue(endDate),
    days,
  };
}

function normalizeActivityMap(overview) {
  const rawMap = overview?.activityMap && typeof overview.activityMap === "object"
    ? overview.activityMap
    : {};
  const todayDate = normalizeDateOnlyValue(rawMap?.todayDate) || toDateOnlyValue(new Date());
  const fallback = buildEmptyActivityMapData(ACTIVITY_MAP_DEFAULT_WEEKS, todayDate);

  const rawDays = Array.isArray(rawMap?.days) ? rawMap.days : [];
  const countByDate = new Map();
  rawDays.forEach((entry) => {
    const dateValue = normalizeDateOnlyValue(entry?.date);
    if (!dateValue) return;
    countByDate.set(dateValue, Math.max(0, Number(entry?.count) || 0));
  });

  const days = [];
  const start = parseDateOnlyValue(fallback.startDate);
  const end = parseDateOnlyValue(fallback.endDate);
  const cursor = new Date(start);
  while (cursor <= end) {
    const dateValue = toDateOnlyValue(cursor);
    days.push({
      date: dateValue,
      count: countByDate.get(dateValue) || 0,
    });
    cursor.setDate(cursor.getDate() + 1);
  }

  if (days.length !== fallback.weeks * 7) {
    return fallback;
  }

  return {
    weeks: fallback.weeks,
    todayDate: fallback.todayDate,
    currentMonth: fallback.currentMonth,
    monthLabel: fallback.monthLabel,
    startDate: fallback.startDate,
    endDate: fallback.endDate,
    days,
  };
}

function normalizeActivityOverviewDays(overview) {
  const entries = Array.isArray(overview?.last7Days) ? overview.last7Days : [];
  return entries.length ? entries : buildEmptyActivityOverviewDays();
}

function getActivityTypeCount(overview, type) {
  return Math.max(0, Number(overview?.byType?.[type]) || 0);
}

function getActivityMapLevel(count) {
  const normalizedCount = Math.max(0, Number(count) || 0);
  if (normalizedCount <= 0) return 0;
  return Math.min(10, Math.floor(normalizedCount));
}

function formatActivityMapTooltipDate(value) {
  const date = parseDateOnlyValue(value);
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("de-DE", {
    weekday: "long",
    day: "numeric",
    month: "short",
  }).format(date);
}

function formatActivityMapMonthLabel(value) {
  const date = parseDateOnlyValue(value);
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("de-DE", { month: "short" }).format(date).replace(/\.$/, "");
}

function buildActivityMapCellLabel(dateValue, count, state, { isTargetDate = false } = {}) {
  const dateLabel = formatActivityMapTooltipDate(dateValue);
  if (!dateLabel) return "";
  let label = "";
  if (state === "future") {
    label = `${dateLabel}`;
  } else if (count <= 0) {
    label = `Keine Aktivität · ${dateLabel}`;
  } else {
    label = `${formatActivityCount(count)} Aktivität${count === 1 ? "" : "en"} · ${dateLabel}`;
  }

  return isTargetDate ? `${label} · Zieldatum` : label;
}

function setActiveActivityMapCell(context, nextCell = null) {
  const previousCell = context?.activityMapHoveredCell instanceof Element ? context.activityMapHoveredCell : null;
  if (previousCell && previousCell !== nextCell) {
    previousCell.classList.remove("is-hovered");
  }

  if (nextCell instanceof Element) {
    nextCell.classList.add("is-hovered");
    context.activityMapHoveredCell = nextCell;
    return;
  }

  context.activityMapHoveredCell = null;
}

function ensureActivityMapTooltip(context) {
  if (!context?.elements) return null;

  if (context.elements.activityMapTooltip instanceof HTMLElement) {
    const tooltip = context.elements.activityMapTooltip;
    if (tooltip.parentElement !== document.body) {
      document.body.appendChild(tooltip);
    }
    tooltip.style.display = tooltip.hidden ? "none" : "block";
    return tooltip;
  }

  const tooltip = document.createElement("div");
  tooltip.className = "dashboard-activity-map__tooltip";
  tooltip.hidden = true;
  tooltip.style.display = "none";
  document.body.appendChild(tooltip);
  context.elements.activityMapTooltip = tooltip;
  return tooltip;
}

function hideActivityMapTooltip(context) {
  const tooltip = ensureActivityMapTooltip(context);
  setActiveActivityMapCell(context, null);
  if (!tooltip) return;

  tooltip.hidden = true;
  tooltip.style.display = "none";
  tooltip.textContent = "";
}

function positionActivityMapTooltip(tooltip, event) {
  if (!tooltip || !event) return;

  const offsetX = 12;
  const offsetY = -32;
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;

  let left = Number(event.clientX || 0) + offsetX;
  let top = Number(event.clientY || 0) + offsetY;

  const tooltipWidth = tooltip.offsetWidth || 0;
  const tooltipHeight = tooltip.offsetHeight || 0;

  if (viewportWidth > 0) {
    left = Math.min(left, Math.max(12, viewportWidth - tooltipWidth - 12));
  }
  if (viewportHeight > 0) {
    top = Math.max(12, Math.min(top, Math.max(12, viewportHeight - tooltipHeight - 12)));
  }

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

function showActivityMapTooltip(context, cell, event) {
  const tooltip = ensureActivityMapTooltip(context);
  const fallbackLabel = buildActivityMapCellLabel(
    String(cell?.dataset?.date || ""),
    Number(cell?.dataset?.count || 0),
    String(cell?.dataset?.state || ""),
  );
  const label = String(cell?.dataset?.tooltip || fallbackLabel || cell?.getAttribute("aria-label") || "").trim();
  if (!tooltip || !label) {
    hideActivityMapTooltip(context);
    return;
  }

  setActiveActivityMapCell(context, cell);
  tooltip.textContent = label;
  tooltip.hidden = false;
  tooltip.style.display = "block";
  positionActivityMapTooltip(tooltip, event);
}

function bindActivityMapTooltip(context) {
  const board = context?.elements?.activityMapBoard;
  if (!board) return;

  ensureActivityMapTooltip(context);

  if (board.dataset.activityMapTooltipLeaveBound !== "true") {
    board.dataset.activityMapTooltipLeaveBound = "true";
    board.addEventListener("mouseleave", () => {
      hideActivityMapTooltip(context);
    });
  }

  const cells = board.querySelectorAll(".dashboard-activity-map__cell");
  cells.forEach((cell) => {
    if (cell.dataset.activityMapTooltipBound === "true") return;

    cell.dataset.activityMapTooltipBound = "true";
    cell.addEventListener("mouseenter", (event) => {
      showActivityMapTooltip(context, cell, event);
    });
    cell.addEventListener("mousemove", (event) => {
      showActivityMapTooltip(context, cell, event);
    });
    cell.addEventListener("mouseleave", () => {
      if (context.activityMapHoveredCell === cell) {
        hideActivityMapTooltip(context);
      }
    });
  });
}

function renderActivityMapBoard(container, overview, targetDate = "") {
  if (!container) return buildEmptyActivityMapData();

  const mapData = normalizeActivityMap(overview);
  const firstActivityDate = normalizeDateOnlyValue(overview?.firstActivityDate) || "";
  const normalizedTargetDate = normalizeDateOnlyValue(targetDate);
  container.style.setProperty("--activity-map-weeks", String(mapData.weeks));

  const dayLabels = ACTIVITY_MAP_DAY_LABELS.map((label, dayIndex) => `
    <div class="dashboard-activity-map__day-label" style="grid-column:${dayIndex + 1};grid-row:2;">${escapeHtml(label)}</div>
  `);

  const calendarTitle = `
    <div class="dashboard-activity-map__calendar-title" style="grid-column:1 / -1;grid-row:1;">${escapeHtml(mapData.monthLabel || "Aktivitätskalender")}</div>
  `;

  const dayCells = mapData.days.map((entry, index) => {
    const dateValue = normalizeDateOnlyValue(entry?.date) || "";
    const count = Math.max(0, Number(entry?.count) || 0);
    const weekIndex = Math.floor(index / 7);
    const dayIndex = index % 7;
    const date = parseDateOnlyValue(dateValue);
    const dayNumber = date instanceof Date && !Number.isNaN(date.getTime()) ? String(date.getDate()) : "";
    const monthKey = getActivityMapMonthKey(date);
    const isTargetDate = Boolean(normalizedTargetDate && dateValue === normalizedTargetDate);
    let state = "tracked";
    const classes = ["dashboard-activity-map__cell"];

    if (isTargetDate) {
      classes.push("is-target-date");
    }

    if (monthKey && mapData.currentMonth && monthKey !== mapData.currentMonth) {
      classes.push("is-outside-month");
    }

    if (dateValue && mapData.todayDate && dateValue > mapData.todayDate) {
      state = "future";
      classes.push("is-future");
    } else if (firstActivityDate && dateValue && dateValue < firstActivityDate) {
      state = "before-start";
      classes.push("is-before-start");
    } else {
      classes.push(`level-${getActivityMapLevel(count)}`);
    }

    if (dateValue && dateValue === mapData.todayDate) {
      classes.push("is-today");
    }

    const label = buildActivityMapCellLabel(dateValue, count, state, { isTargetDate });
    return `
      <span class="${classes.join(" ")}" style="grid-column:${dayIndex + 1};grid-row:${weekIndex + 3};" data-tooltip="${escapeHtml(label)}" data-date="${escapeHtml(dateValue)}" data-count="${escapeHtml(String(count))}" data-state="${escapeHtml(state)}" aria-label="${escapeHtml(label)}">
        <span class="dashboard-activity-map__date-number" aria-hidden="true">${escapeHtml(dayNumber)}</span>
      </span>
    `;
  });

  container.innerHTML = `${calendarTitle}${dayLabels.join("")}${dayCells.join("")}`;
  return mapData;
}

function applyActivityMap(context, overview = null) {
  const summaryNode = context.elements.activityMapSummary;
  const targetNode = context.elements.activityMapTarget;
  const targetDate = normalizeDateOnlyValue(context.activeSession?.target_date);
  const mapData = renderActivityMapBoard(context.elements.activityMapBoard, overview, targetDate);
  hideActivityMapTooltip(context);
  bindActivityMapTooltip(context);
  const totalCount = Math.max(0, Number(overview?.totalCount) || 0);
  const visibleActivityCount = Array.isArray(mapData?.days)
    ? mapData.days.reduce((sum, entry) => sum + Math.max(0, Number(entry?.count) || 0), 0)
    : 0;

  if (summaryNode) {
    summaryNode.textContent = visibleActivityCount > 0
      ? ACTIVITY_MAP_SUMMARY_COPY
      : totalCount > 0
        ? ACTIVITY_MAP_EMPTY_WINDOW_SUMMARY
        : ACTIVITY_MAP_EMPTY_SUMMARY;
  }

  if (targetNode) {
    if (targetDate) {
      targetNode.hidden = false;
      targetNode.textContent = `Ziel: ${formatDateOnlyLabel(targetDate)}`;
    } else {
      targetNode.hidden = true;
      targetNode.textContent = "";
    }
  }

  setStatusNode(context.elements.activityMapStatusNode, "");
}

function applyActivityOverview(context, overview = null) {
  const summaryNode = context.elements.activitySummary;
  const totalNode = context.elements.activityTotal;
  const metaNode = context.elements.activityMeta;
  const activeDaysNode = context.elements.activityActiveDays;
  const averageNode = context.elements.activityAverage;
  const trainingNode = context.elements.activityTraining;
  const recallNode = context.elements.activityRecall;
  const feynmanNode = context.elements.activityFeynman;
  const flashcardsNode = context.elements.activityFlashcards;

  const totalCount = Math.max(0, Number(overview?.totalCount) || 0);
  const activeDays = Math.max(0, Number(overview?.activeDays) || 0);
  const averagePerActiveDay = Number(overview?.averagePerActiveDay) || 0;
  const firstActivityDate = String(overview?.firstActivityDate || "").trim();

  if (summaryNode) {
    summaryNode.textContent = totalCount > 0
      ? "Gezählt werden abgeschlossene Trainingsaufgaben, Recall-, Feynman- und Flashcard-Durchgänge über Feed und freien Zugriff."
      : ACTIVITY_SUMMARY_EMPTY;
  }
  if (totalNode) totalNode.textContent = formatActivityCount(totalCount);
  if (metaNode) {
    metaNode.textContent = firstActivityDate
      ? `seit ${formatDateOnlyLabel(firstActivityDate)} · ${formatActivityCount(activeDays)} aktive Tage`
      : "Noch keine abgeschlossenen Aktivitäten erfasst.";
  }
  if (activeDaysNode) activeDaysNode.textContent = formatActivityCount(activeDays);
  if (averageNode) averageNode.textContent = formatActivityAverage(averagePerActiveDay);
  if (trainingNode) trainingNode.textContent = formatActivityCount(getActivityTypeCount(overview, "training"));
  if (recallNode) recallNode.textContent = formatActivityCount(getActivityTypeCount(overview, "recall"));
  if (feynmanNode) feynmanNode.textContent = formatActivityCount(getActivityTypeCount(overview, "feynman"));
  if (flashcardsNode) flashcardsNode.textContent = formatActivityCount(getActivityTypeCount(overview, "flashcards"));

  applyProficiencyWorklist(context, overview);
  setStatusNode(context.elements.activityStatusNode, "");
}

function computeSessionActivityRate(checks, selectedCheckIdSet) {
  if (!Array.isArray(checks) || !checks.length || !selectedCheckIdSet.size) return null;

  const rates = checks
    .filter((check) => selectedCheckIdSet.has(String(check?.checkId || "").trim()))
    .map((check) => Number(check?.rate))
    .filter((rate) => Number.isFinite(rate));
  if (!rates.length) return null;

  return rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
}

function computeLifetimeActivityRate(rateEntry) {
  const rate = Number(rateEntry?.rate);
  return Number.isFinite(rate) ? rate : null;
}

function updateWorklistQuotes(context) {
  const trainingSuccessNode = context.elements.worklistTrainingSuccess;
  const recallSuccessNode = context.elements.worklistRecallSuccess;
  const feynmanSuccessNode = context.elements.worklistFeynmanSuccess;
  if (!trainingSuccessNode && !recallSuccessNode && !feynmanSuccessNode) return;

  const overview = context.activityOverview;
  const sessionOnly = context.worklistSessionOnly !== false;

  let trainingRate;
  let recallRate;
  let feynmanRate;

  if (sessionOnly) {
    const { selectedCheckIds } = summarizeActivePlan(context);
    const selectedCheckIdSet = new Set(selectedCheckIds.map((checkId) => String(checkId || "").trim()));
    trainingRate = computeSessionActivityRate(overview?.proficiency?.checks, selectedCheckIdSet);
    recallRate = computeSessionActivityRate(overview?.recallProficiency?.checks, selectedCheckIdSet);
    feynmanRate = computeSessionActivityRate(overview?.feynmanProficiency?.checks, selectedCheckIdSet);
  } else {
    trainingRate = computeLifetimeActivityRate(overview?.trainingSuccess);
    recallRate = computeLifetimeActivityRate(overview?.recallProficiency?.overall);
    feynmanRate = computeLifetimeActivityRate(overview?.feynmanProficiency?.overall);
  }

  const scopeLabel = sessionOnly ? "deiner Session-Checks" : "aller erfassten Checks";
  if (trainingSuccessNode) {
    trainingSuccessNode.textContent = formatActivityPercent(Number.isFinite(trainingRate) ? Math.round(trainingRate) : NaN);
    trainingSuccessNode.title = Number.isFinite(trainingRate)
      ? `Trainingsquote ${scopeLabel}, zusammengesetzt aus den jüngsten Durchgängen je Check.`
      : "Die Quote erscheint, sobald Trainingsaufgaben erfasst wurden.";
  }
  if (recallSuccessNode) {
    recallSuccessNode.textContent = formatActivityPercent(Number.isFinite(recallRate) ? Math.round(recallRate) : NaN);
    recallSuccessNode.title = Number.isFinite(recallRate)
      ? `Recall-Quote ${scopeLabel}, zusammengesetzt aus den jüngsten Durchgängen je Check.`
      : "Die Quote erscheint, sobald Recall-Durchgänge erfasst wurden.";
  }
  if (feynmanSuccessNode) {
    feynmanSuccessNode.textContent = formatActivityPercent(Number.isFinite(feynmanRate) ? Math.round(feynmanRate) : NaN);
    feynmanSuccessNode.title = Number.isFinite(feynmanRate)
      ? `Feynman-Quote ${scopeLabel}, zusammengesetzt aus den jüngsten Durchgängen je Check.`
      : "Die Quote erscheint, sobald Feynman-Durchgänge erfasst wurden.";
  }
}

function buildCheckTrainingHref(checkMeta) {
  if (!checkMeta?.gebietKey || !checkMeta?.lernbereichId || !checkMeta?.checkId) return "";
  const params = new URLSearchParams({ check_id: checkMeta.checkId });
  return `/lernbereiche/${encodeURIComponent(checkMeta.gebietKey)}/${encodeURIComponent(checkMeta.lernbereichId)}/training.html?${params.toString()}`;
}

function toDomIdFragment(value) {
  return String(value || "")
    .toLowerCase()
    .replaceAll(/[^a-z0-9_-]+/g, "-")
    .replaceAll(/^-+|-+$/g, "");
}

function buildCheckRecallHref(checkMeta) {
  if (!checkMeta?.gebietKey || !checkMeta?.lernbereichId || !checkMeta?.checkId) return "";
  return `/lernbereiche/${encodeURIComponent(checkMeta.gebietKey)}/${encodeURIComponent(checkMeta.lernbereichId)}/recall.html#recall-check-${toDomIdFragment(checkMeta.checkId) || "item"}`;
}

function buildCheckFeynmanHref(checkMeta) {
  if (!checkMeta?.gebietKey || !checkMeta?.lernbereichId || !checkMeta?.checkId) return "";
  return `/lernbereiche/${encodeURIComponent(checkMeta.gebietKey)}/${encodeURIComponent(checkMeta.lernbereichId)}/feynman.html#fy-check-${toDomIdFragment(checkMeta.checkId) || "item"}`;
}

function buildProficiencyWorklistEntries(overview = null) {
  const trainingChecks = Array.isArray(overview?.proficiency?.checks) ? overview.proficiency.checks : [];
  const recallChecks = Array.isArray(overview?.recallProficiency?.checks) ? overview.recallProficiency.checks : [];
  const feynmanChecks = Array.isArray(overview?.feynmanProficiency?.checks) ? overview.feynmanProficiency.checks : [];

  return [
    ...trainingChecks.map((check) => ({ ...check, activityType: "training", activityLabel: "Training" })),
    ...recallChecks.map((check) => ({ ...check, activityType: "recall", activityLabel: "Recall" })),
    ...feynmanChecks.map((check) => ({ ...check, activityType: "feynman", activityLabel: "Feynman" })),
  ].sort((left, right) => {
    const leftRate = Number(left?.rate);
    const rightRate = Number(right?.rate);
    const leftSortRate = Number.isFinite(leftRate) ? leftRate : Number.POSITIVE_INFINITY;
    const rightSortRate = Number.isFinite(rightRate) ? rightRate : Number.POSITIVE_INFINITY;
    if (leftSortRate !== rightSortRate) return leftSortRate - rightSortRate;
    return String(left?.checkId || "").localeCompare(String(right?.checkId || ""), "de");
  });
}

function collectProficiencyWorklistGroups(context, checks) {
  const gebiete = new Map();

  checks.forEach((check) => {
    const checkId = String(check?.checkId || "").trim();
    const meta = context.checkMetaById?.get(checkId) || null;
    const group = context.lernbereiche.find((candidate) => {
      return candidate.items.some((lernbereich) => lernbereich.id === meta?.lernbereichId);
    }) || null;
    const lernbereich = group?.items.find((candidate) => candidate.id === meta?.lernbereichId) || null;
    const gebietKey = String(meta?.gebietKey || "other").trim() || "other";
    const lernbereichId = String(meta?.lernbereichId || checkId || "other").trim() || "other";

    if (!gebiete.has(gebietKey)) {
      gebiete.set(gebietKey, {
        name: group?.group || meta?.groupName || "Weitere Checks",
        order: Number.isFinite(Number(group?.order)) ? Number(group.order) : 999,
        lernbereiche: new Map(),
      });
    }

    const gebiet = gebiete.get(gebietKey);
    if (!gebiet.lernbereiche.has(lernbereichId)) {
      gebiet.lernbereiche.set(lernbereichId, {
        name: lernbereich?.name || meta?.lernbereichName || "Weitere Checks",
        order: Number.isFinite(Number(lernbereich?.didacticOrder)) ? Number(lernbereich.didacticOrder) : 999,
        checks: [],
      });
    }

    gebiet.lernbereiche.get(lernbereichId).checks.push(check);
  });

  return Array.from(gebiete.values())
    .map((gebiet) => ({
      ...gebiet,
      lernbereiche: Array.from(gebiet.lernbereiche.values())
        .map((lernbereich) => ({
          ...lernbereich,
          checks: [...lernbereich.checks].sort((left, right) => {
            const leftRate = Number.isFinite(Number(left?.rate)) ? Number(left.rate) : Number.POSITIVE_INFINITY;
            const rightRate = Number.isFinite(Number(right?.rate)) ? Number(right.rate) : Number.POSITIVE_INFINITY;
            if (leftRate !== rightRate) return leftRate - rightRate;
            return String(left?.checkId || "").localeCompare(String(right?.checkId || ""), "de");
          }),
        }))
        .sort((left, right) => left.order - right.order || left.name.localeCompare(right.name, "de")),
    }))
    .sort((left, right) => left.order - right.order || left.name.localeCompare(right.name, "de"));
}

function applyProficiencyWorklist(context, overview = null) {
  const listNode = context.elements.worklistList;
  const summaryNode = context.elements.worklistSummary;
  if (!listNode) return;

  context.activityOverview = overview ?? context.activityOverview ?? null;
  syncWorklistSessionToggle(context);
  updateWorklistQuotes(context);

  const effectiveOverview = context.activityOverview;
  const allChecks = buildProficiencyWorklistEntries(effectiveOverview);
  listNode.innerHTML = "";

  if (!allChecks.length) {
    if (summaryNode) {
      summaryNode.textContent = "Sobald du Training, Recall oder Feynman abschließt, erscheinen hier deine nach Quote sortierten Checks – schwächste zuerst.";
    }
    return;
  }

  const sessionOnly = context.worklistSessionOnly !== false;
  let checks = allChecks;
  if (sessionOnly) {
    const sessionCheckIds = new Set(summarizeActivePlan(context).selectedCheckIds);
    checks = allChecks.filter((check) => sessionCheckIds.has(String(check?.checkId || "").trim()));
  }

  if (!checks.length) {
    if (summaryNode) {
      summaryNode.textContent = sessionOnly
        ? "Noch keine Training-, Recall- oder Feynman-Quoten aus deiner aktiven Session. Schalte den Session-Filter im Menü aus, um alle Checks zu sehen."
        : "Sobald du Training, Recall oder Feynman abschließt, erscheinen hier deine nach Quote sortierten Checks – schwächste zuerst.";
    }
    return;
  }

  if (summaryNode) {
    summaryNode.textContent = sessionOnly
      ? "Checks deiner Session, nach Gebiet und Lernbereich geordnet."
      : "Alle erfassten Quoten, nach Gebiet und Lernbereich geordnet.";
  }

  const groupedChecks = collectProficiencyWorklistGroups(context, checks);
  const worklistEntries = [];
  groupedChecks.forEach((gebiet) => {
    const gebietItem = document.createElement("li");
    gebietItem.className = "dashboard-worklist__gebiet";
    const heading = document.createElement("h3");
    heading.className = "dashboard-worklist__gebiet-heading";
    heading.textContent = gebiet.name;
    const lernbereichList = document.createElement("ul");
    lernbereichList.className = "dashboard-worklist__lernbereiche";

    gebiet.lernbereiche.forEach((lernbereich) => {
      const lernbereichItem = document.createElement("li");
      const details = document.createElement("details");
      details.className = "dashboard-worklist__lernbereich";
      details.open = sessionOnly;
      const summary = document.createElement("summary");
      summary.innerHTML = `<span>${escapeHtml(lernbereich.name)}</span><span>${lernbereich.checks.length} ${lernbereich.checks.length === 1 ? "Check" : "Checks"}</span>`;
      const checkList = document.createElement("ul");
      checkList.className = "dashboard-worklist__checks";
      details.append(summary, checkList);
      lernbereichItem.appendChild(details);
      lernbereichList.appendChild(lernbereichItem);
      lernbereich.checks.forEach((check) => {
        worklistEntries.push({ check, checkList });
      });
    });

    gebietItem.append(heading, lernbereichList);
    listNode.appendChild(gebietItem);
  });

  worklistEntries.forEach(({ check, checkList }) => {
    const checkId = String(check?.checkId || "").trim();
    if (!checkId) return;

    const meta = context.checkMetaById?.get(checkId) || null;
    const rate = Number(check?.rate);
    const hasRate = Number.isFinite(rate);
    const clampedRate = hasRate ? Math.max(0, Math.min(100, rate)) : 0;
    const activityType = String(check?.activityType || "training").trim();
    const activityLabel = String(check?.activityLabel || "Training").trim();
    const href = activityType === "recall"
      ? buildCheckRecallHref(meta ? { ...meta, checkId } : null)
      : activityType === "feynman"
        ? buildCheckFeynmanHref(meta ? { ...meta, checkId } : null)
        : buildCheckTrainingHref(meta ? { ...meta, checkId } : null);

    const label = meta?.shortTitle || meta?.label || `Check ${checkId}`;

    const item = document.createElement("li");
    item.className = "dashboard-worklist__item";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "action-card dashboard-panel__action-card dashboard-worklist__button";

    const titleRow = document.createElement("span");
    titleRow.className = "action-title dashboard-panel__action-title";

    const nameSpan = document.createElement("span");
    nameSpan.className = "dashboard-panel__action-name";
    nameSpan.textContent = label;
    titleRow.appendChild(nameSpan);

    const activitySpan = document.createElement("span");
    activitySpan.className = `action-badge dashboard-worklist__activity-badge dashboard-module-badge--${activityType}`;
    activitySpan.textContent = activityLabel;

    const metaRow = document.createElement("div");
    metaRow.className = "action-badges dashboard-panel__action-meta";
    metaRow.appendChild(activitySpan);

    let reviewBadge = null;
    if (check?.reviewIsDue === true) {
      reviewBadge = document.createElement("span");
      reviewBadge.className = "dashboard-worklist__review-badge";
      reviewBadge.setAttribute("role", "img");
      reviewBadge.setAttribute("aria-label", "Wiederholung fällig");
      reviewBadge.title = "Wiederholung fällig";
      reviewBadge.textContent = "↻";
    }

    // SVG-Fortschrittsring
    const ringSize = 52;
    const ringStroke = 3.5;
    const ringR = (ringSize - ringStroke) / 2;
    const ringCirc = 2 * Math.PI * ringR;
    const ringOffset = ringCirc * (1 - clampedRate / 100);
    const ringLabel = hasRate ? formatActivityPercent(Math.round(rate)) : "–";
    const ringSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    ringSvg.setAttribute("class", "dashboard-worklist__ring");
    ringSvg.setAttribute("width", ringSize);
    ringSvg.setAttribute("height", ringSize);
    ringSvg.setAttribute("viewBox", `0 0 ${ringSize} ${ringSize}`);
    ringSvg.setAttribute("aria-hidden", "true");
    const ringBg = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    ringBg.setAttribute("class", "dashboard-worklist__ring-bg");
    ringBg.setAttribute("cx", ringSize / 2);
    ringBg.setAttribute("cy", ringSize / 2);
    ringBg.setAttribute("r", ringR);
    ringBg.setAttribute("fill", "none");
    ringBg.setAttribute("stroke-width", ringStroke);
    const ringFill = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    ringFill.setAttribute("class", "dashboard-worklist__ring-fill");
    ringFill.setAttribute("cx", ringSize / 2);
    ringFill.setAttribute("cy", ringSize / 2);
    ringFill.setAttribute("r", ringR);
    ringFill.setAttribute("fill", "none");
    ringFill.setAttribute("stroke-width", ringStroke);
    ringFill.setAttribute("stroke-dasharray", ringCirc);
    ringFill.setAttribute("stroke-dashoffset", ringOffset);
    ringFill.setAttribute("stroke-linecap", "round");
    ringSvg.appendChild(ringBg);
    ringSvg.appendChild(ringFill);

    const ringWrap = document.createElement("span");
    ringWrap.className = "dashboard-worklist__ring-wrap dashboard-panel__action-status";
    ringWrap.setAttribute("aria-label", `${ringLabel} Erfolgsquote`);
    const ringText = document.createElement("span");
    ringText.className = "dashboard-worklist__ring-text";
    ringText.textContent = ringLabel;
    ringWrap.appendChild(ringSvg);
    ringWrap.appendChild(ringText);
    if (reviewBadge) {
      ringWrap.appendChild(reviewBadge);
    }

    const body = document.createElement("span");
    body.className = "action-body";
    body.appendChild(titleRow);
    body.appendChild(metaRow);

    button.appendChild(body);
    button.appendChild(ringWrap);

    if (href) {
      button.dataset.actionHref = href;
      button.addEventListener("click", () => {
        window.location.href = href;
      });
    } else {
      button.disabled = true;
    }

    item.appendChild(button);
    checkList.appendChild(item);
  });
}

function syncWorklistSessionToggle(context) {
  const toggle = context.elements.worklistSessionToggle;
  const sessionOnly = context.worklistSessionOnly !== false;
  if (!toggle) return;
  toggle.setAttribute("aria-checked", sessionOnly ? "true" : "false");
  toggle.classList.toggle("is-active", sessionOnly);
}

function setupWorklistSessionToggle(context) {
  const toggle = context.elements.worklistSessionToggle;
  if (!toggle) return;
  toggle.addEventListener("click", () => {
    context.worklistSessionOnly = context.worklistSessionOnly === false;
    writeWorklistSessionOnlyPreference(context.worklistSessionOnly !== false);
    applyProficiencyWorklist(context, context.activityOverview);
  });
  syncWorklistSessionToggle(context);
}

async function refreshActivityOverview(context) {
  if (!context.supabase) {
    context.activityOverview = null;
    applyActivityOverview(context, null);
    applyActivityMap(context, null);
    setStatusNode(context.elements.activityStatusNode, ACTIVITY_UNAVAILABLE_MESSAGE, "warning");
    setStatusNode(context.elements.activityMapStatusNode, ACTIVITY_UNAVAILABLE_MESSAGE, "warning");
    updateGreetingHeading(context);
    return;
  }

  try {
    const [{ data, error }, recallProficiency, feynmanProficiency] = await Promise.all([
      context.supabase.rpc("get_user_activity_overview"),
      getUserRecallProficiency(),
      getUserFeynmanProficiency(),
    ]);
    if (error) throw error;

    const overview = data && typeof data === "object" ? { ...data } : {};
    if (recallProficiency.ok && recallProficiency.data) {
      overview.recallProficiency = recallProficiency.data;
    }
    if (feynmanProficiency.ok && feynmanProficiency.data) {
      overview.feynmanProficiency = feynmanProficiency.data;
    }

    context.activityOverview = overview;
    applyActivityOverview(context, overview);
    applyActivityMap(context, overview);
    updateGreetingHeading(context);
  } catch (error) {
    console.error("Aktivitätsstatistik konnte nicht geladen werden:", error);
    context.activityOverview = null;
    applyActivityOverview(context, null);
    applyActivityMap(context, null);
    setStatusNode(context.elements.activityStatusNode, ACTIVITY_LOAD_ERROR_MESSAGE, "error");
    setStatusNode(context.elements.activityMapStatusNode, ACTIVITY_LOAD_ERROR_MESSAGE, "error");
    updateGreetingHeading(context);
  }
}

function getRemainingCheckStepCount(row) {
  if (!row) return CHECK_PIPELINE_STEP_COUNT;

  const status = String(row?.current_step_status || "").trim();
  const stepKey = String(row?.current_step_key || "").trim();
  if (status === "completed" || stepKey === "check_completed") {
    return 0;
  }

  const order = FEED_STEP_ORDER[stepKey];
  return Number.isFinite(order)
    ? CHECK_PIPELINE_STEP_COUNT - order + 1
    : CHECK_PIPELINE_STEP_COUNT;
}

function getRemainingDidacticGapCount(row) {
  const status = String(row?.current_step_status || "").trim();
  const stepKey = String(row?.current_step_key || "").trim();
  if (status === "completed" || stepKey === "check_completed") {
    return 0;
  }

  switch (stepKey) {
    case "recall":
      return 2;
    case "feynman":
      return 1;
    case "kompetenzliste_gate":
      return 0;
    case "training":
    default:
      return 3;
  }
}

function applyPrimaryFeedButtonState(context, {
  href = "",
  statusMarkup = "",
  title = "Nächste Aktion",
  moduleLabel = "Feed",
  type = "feed",
  accessibleLabel = "Nächste Aktion",
  waiting = false,
  disabled = false,
} = {}) {
  const { elements } = context;
  const button = elements.primaryFeedButton;
  if (!button) return;

  const normalizedHref = String(href || "").trim();
  const normalizedModuleLabel = String(moduleLabel || "").trim();
  button.dataset.actionHref = normalizedHref;
  button.dataset.type = type || "feed";
  button.classList.toggle("is-waiting", waiting);
  button.setAttribute("aria-disabled", disabled || !normalizedHref ? "true" : "false");
  button.setAttribute("aria-label", accessibleLabel || "Nächste Aktion");
  button.title = accessibleLabel || "Nächste Aktion";
  if (elements.primaryFeedStatus) {
    elements.primaryFeedStatus.innerHTML = statusMarkup || buildDashboardClockStatusMarkup(accessibleLabel || "Nächste Aktion", "available");
  }
  if (elements.primaryFeedTitle) {
    elements.primaryFeedTitle.textContent = title || "Nächste Aktion";
  }
  if (elements.primaryFeedModule) {
    const moduleBadgeList = elements.primaryFeedModule.closest(".action-badges");
    elements.primaryFeedModule.className = `action-badge dashboard-next-action-card__module dashboard-module-badge--${type || "feed"}`;
    elements.primaryFeedModule.textContent = normalizedModuleLabel || "Feed";
    elements.primaryFeedModule.hidden = !normalizedModuleLabel;
    if (moduleBadgeList) {
      moduleBadgeList.hidden = !normalizedModuleLabel;
    }
  }
}

function applyPrimaryFeedLoadingState(context) {
  applyPrimaryFeedButtonState(context, {
    title: "Nächste Aktion wird geladen",
    moduleLabel: "Feed",
    type: "feed",
    accessibleLabel: "Nächste Aktion wird geladen",
    disabled: true,
  });
}

function applyPrimaryFeedEmptyState(context) {
  applyPrimaryFeedButtonState(context, {
    title: "Gerade keine Empfehlung",
    moduleLabel: "Feed",
    type: "feed",
    accessibleLabel: "Gerade keine nächste Aktion verfügbar",
    disabled: true,
  });
}

function applyPrimaryFeedWaitingState(context, waiting = null) {
  const nextLabel = formatDateTimeLabel(waiting?.nextAvailableFrom);

  applyPrimaryFeedButtonState(context, {
    title: nextLabel
      ? `Nächste Aktion ab ${nextLabel} verfügbar. Du kannst in der Zwischenzeit Deine Erfolgsquoten verbessern.`
      : "Nächste Aktion wird später freigeschaltet.",
    moduleLabel: "",
    type: "feed",
    accessibleLabel: nextLabel
      ? "Wartend"
      : "Wartend",
    waiting: true,
    disabled: true,
  });
}

function applyPrimaryFeedErrorState(context) {
  applyPrimaryFeedButtonState(context, {
    title: "Feed gerade nicht verfügbar",
    moduleLabel: "Feed",
    type: "feed",
    accessibleLabel: "Nächste Aktion gerade nicht verfügbar",
    disabled: true,
  });
}

function buildLernbereichStartHref(lernbereichMeta) {
  if (!lernbereichMeta?.gebietKey || !lernbereichMeta?.lernbereichId) return "";
  return `/lernbereiche/${encodeURIComponent(lernbereichMeta.gebietKey)}/${encodeURIComponent(lernbereichMeta.lernbereichId)}/start.html`;
}

function buildProjectionTitleMarkup(item) {
  const parts = [
    String(item?.checkIndexLabel || "").trim(),
    String(item?.checkKeyword || item?.titleText || "").trim(),
  ].filter(Boolean);
  const titleText = parts.join(" ").trim();
  if (!titleText) return "";

  return `<span class="dashboard-panel__action-name">${escapeHtml(titleText)}</span>`;
}

function buildProjectionBadgesMarkup(item) {
  return (Array.isArray(item?.badges) ? item.badges : [])
    .map((badge) => createBadgeMarkup(badge?.label || "", badge?.type || ""))
    .join("");
}

function padFeedCheckNumber(value) {
  const digits = String(value || "").replace(/\D+/g, "");
  if (!digits) return "";

  const number = Number(digits);
  return Number.isFinite(number) && number > 0 ? String(number).padStart(2, "0") : "";
}

function resolvePrimaryFeedModuleLabel(item) {
  const itemType = String(item?.type || "").trim();
  if (itemType === "training") return "Aufgabe";

  const primaryLabel = String(item?.primaryBadge?.label || "").trim();
  if (primaryLabel) return primaryLabel;

  return String(item?.titleText || "").trim();
}

function buildPrimaryFeedTitleHtml(item) {
  const titleText = buildPrimaryFeedTitleText(item);
  if (!titleText) return "";

  return `<span class="dashboard-panel__action-name">${escapeHtml(titleText)}</span>`;
}

function buildPrimaryFeedTitleText(item) {
  const moduleLabel = resolvePrimaryFeedModuleLabel(item);
  const checkNumber = padFeedCheckNumber(item?.checkIndexLabel);
  const checkKeyword = String(item?.checkKeyword || "").trim();

  if (checkKeyword) {
    return checkNumber
      ? `${moduleLabel} ${checkNumber} | ${checkKeyword}`
      : `${moduleLabel} | ${checkKeyword}`;
  }

  return moduleLabel || String(item?.titleText || "").trim();
}

function buildPrimaryFeedSubtitleText(item) {
  const explicitText = String(item?.lernbereichText || "").trim();
  if (explicitText) return explicitText;

  if (item?.kind === "session-activity" || item?.kind === "retention") {
    return String(item?.titleText || "").trim();
  }

  return "";
}

function buildPrimaryFeedKeywordText(item) {
  return String(item?.checkKeyword || item?.titleText || "").trim();
}

function buildPrimaryFeedModuleLabel(item) {
  return String(item?.primaryBadge?.label || resolvePrimaryFeedModuleLabel(item) || "").trim();
}

function buildDashboardClockStatusMarkup(label, tone = "available") {
  const accessibleLabel = String(label || "").trim();
  if (!accessibleLabel) return "";

  const normalizedTone = ["available", "due", "overdue"].includes(String(tone || "").trim())
    ? String(tone || "").trim()
    : "available";

  return `
    <span class="dashboard-panel__action-status dashboard-panel__action-status--icon" data-tone="${escapeHtml(normalizedTone)}" role="img" aria-label="${escapeHtml(accessibleLabel)}" title="${escapeHtml(accessibleLabel)}">
      <span class="dashboard-panel__status-clock" aria-hidden="true"></span>
      <span class="dashboard-panel__status-clock-label" aria-hidden="true">${escapeHtml(accessibleLabel)}</span>
    </span>
  `;
}

function buildDashboardCountStatusMarkup(value, accessibleLabel) {
  const count = Math.max(0, Number(value) || 0);
  const compactValue = formatActivityCount(count);
  const description = String(accessibleLabel || "").trim();

  return `
    <span class="dashboard-panel__action-status dashboard-panel__action-status--count" aria-label="${escapeHtml(description)}" title="${escapeHtml(description)}">
      <span class="dashboard-panel__action-status-value">${escapeHtml(compactValue)}</span>
    </span>
  `;
}

function buildDashboardProgressStatusMarkup(progress = null) {
  const totalStepCount = Math.max(0, Number(progress?.totalStepCount) || 0);
  if (totalStepCount <= 0) return "";

  const completedStepCount = Math.max(0, Math.min(totalStepCount, Number(progress?.completedStepCount) || 0));
  const percent = Math.max(0, Math.min(100, Number(progress?.percent) || 0));
  const compactLabel = `${formatActivityCount(completedStepCount)}/${formatActivityCount(totalStepCount)}`;
  const accessibleLabel = `${completedStepCount} von ${totalStepCount} Session-Schritten abgeschlossen`;

  return `
    <span class="dashboard-panel__action-status dashboard-panel__action-status--progress" aria-label="${escapeHtml(accessibleLabel)}" title="${escapeHtml(accessibleLabel)}">
      <span class="dashboard-panel__action-status-value">${escapeHtml(compactLabel)}</span>
      <span class="dashboard-panel__action-status-track" aria-hidden="true">
        <span class="dashboard-panel__action-status-fill" style="width:${percent}%"></span>
      </span>
    </span>
  `;
}

function buildDashboardLernbereichStatusMarkup(entry) {
  const statusKind = String(entry?.statusKind || "").trim();

  if (statusKind === "session-progress") {
    return buildDashboardProgressStatusMarkup(entry?.sessionProgress || null);
  }

  if (statusKind === "flashcard-count") {
    const completedFlashcardCount = Math.max(0, Number(entry?.completedFlashcardCount) || 0);
    const durchgangLabel = completedFlashcardCount === 1 ? "Durchgang" : "Durchgänge";
    return buildDashboardCountStatusMarkup(
      completedFlashcardCount,
      `${completedFlashcardCount} abgeschlossene Flashcard-${durchgangLabel}`,
    );
  }

  return "";
}

function buildPrimaryFeedStatusMarkup(item) {
  const statusBadge = (Array.isArray(item?.badges) ? item.badges : []).find((badge) => {
    const badgeType = String(badge?.type || "").trim();
    return badgeType === "overdue" || badgeType === "due" || badgeType === "available";
  });
  if (!statusBadge?.label) return "";

  return buildDashboardClockStatusMarkup(String(statusBadge.label), statusBadge.type || "available");
}

function createFeedCardData({ type, href, subtitleText, titleHtml, primaryTitleHtml, primaryTitleText, keywordText, moduleLabel, statusMarkup, descText, badges }) {
  return {
    type,
    href,
    subtitleText,
    titleHtml,
    primaryTitleHtml,
    primaryTitleText,
    keywordText,
    moduleLabel,
    statusMarkup,
    descText,
    badges,
  };
}

function buildFeedCardDataFromProjection(item) {
  if (!item?.href) return null;

  return createFeedCardData({
    type: item.type,
    href: item.href,
    subtitleText: buildPrimaryFeedSubtitleText(item),
    titleHtml: buildProjectionTitleMarkup(item),
    primaryTitleHtml: buildPrimaryFeedTitleHtml(item),
    primaryTitleText: buildPrimaryFeedTitleText(item),
    keywordText: buildPrimaryFeedKeywordText(item),
    moduleLabel: buildPrimaryFeedModuleLabel(item),
    statusMarkup: buildPrimaryFeedStatusMarkup(item),
    descText: item.descText,
    badges: buildProjectionBadgesMarkup(item),
  });
}

function applyPrimaryFeedCardData(context, item) {
  if (!item) {
    applyPrimaryFeedEmptyState(context);
    return;
  }

  applyPrimaryFeedButtonState(context, {
    href: item.href,
    statusMarkup: item.statusMarkup,
    title: item.keywordText || item.primaryTitleText || "Nächste Aktion",
    moduleLabel: item.moduleLabel || "Feed",
    type: item.type || "feed",
    accessibleLabel: item.primaryTitleText ? `Nächste Aktion: ${item.primaryTitleText}` : "Nächste Aktion öffnen",
  });
}

function sortCompletedLernbereiche(entries) {
  return [...entries].sort((left, right) => {
    const completedDelta = String(right.lastCompletedAt || "").localeCompare(String(left.lastCompletedAt || ""));
    if (completedDelta !== 0) return completedDelta;
    return String(left.lernbereichName || "").localeCompare(String(right.lernbereichName || ""), "de");
  });
}

async function loadActiveSessionCompletedLernbereiche(context) {
  if (!context.supabase || !context.activeSession?.id) return [];

  const { data, error } = await context.supabase
    .from("session_check_state")
    .select("check_id, current_step_status, last_completed_at")
    .eq("session_id", context.activeSession.id);

  if (error) throw error;

  const statusByCheckId = new Map();
  (Array.isArray(data) ? data : []).forEach((row) => {
    const checkId = String(row?.check_id || "").trim();
    if (!checkId) return;
    statusByCheckId.set(checkId, row);
  });

  const completedLernbereiche = [];

  context.lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const lbState = context.state[lb.id];
      if (!lbState?.active) return;

      const selectedChecks = lb.checks.filter((check) => isCheckSelected(lbState, check.id));
      if (!selectedChecks.length) return;

      const rows = selectedChecks.map((check) => statusByCheckId.get(check.id));
      const allCompleted = rows.every((row) => row?.current_step_status === "completed");
      if (!allCompleted) return;

      const completionDates = rows
        .map((row) => String(row?.last_completed_at || ""))
        .filter(Boolean)
        .sort((left, right) => right.localeCompare(left));

      completedLernbereiche.push({
        lernbereichId: lb.id,
        lernbereichName: lb.name,
        gebietKey: lb.gebietKey,
        groupName: group.group,
        checkCount: selectedChecks.length,
        totalCheckCount: lb.checks.length,
        lastCompletedAt: completionDates[0] || "",
      });
    });
  });

  return completedLernbereiche;
}

async function loadFlashcardCompletionStatsByLernbereich(context) {
  if (!context.supabase) return new Map();

  const statsBySlug = new Map();
  const pageSize = 1000;
  let fromIndex = 0;

  while (true) {
    const { data, error } = await context.supabase
      .from("user_activity_events")
      .select("lernbereich_slug, created_at")
      .eq("activity_type", "flashcards")
      .not("lernbereich_slug", "is", null)
      .order("created_at", { ascending: false })
      .range(fromIndex, fromIndex + pageSize - 1);

    if (error) throw error;

    const rows = Array.isArray(data) ? data : [];
    rows.forEach((row) => {
      const slug = String(row?.lernbereich_slug || "").trim();
      const createdAt = String(row?.created_at || "").trim();
      if (!slug) return;

      const current = statsBySlug.get(slug) || { count: 0, lastCompletedAt: "" };
      current.count += 1;
      if (createdAt && createdAt.localeCompare(current.lastCompletedAt) > 0) {
        current.lastCompletedAt = createdAt;
      }
      statsBySlug.set(slug, current);
    });

    if (rows.length < pageSize) break;
    fromIndex += pageSize;
  }

  return statsBySlug;
}

function applyFlashcardCompletionStats(entries, statsBySlug) {
  const sourceEntries = Array.isArray(entries) ? entries : [];

  return sourceEntries.map((entry) => {
    const slug = String(entry?.lernbereichId || "").trim();
    const stats = slug ? statsBySlug.get(slug) : null;
    const existingLastCompletedAt = String(entry?.lastCompletedAt || "").trim();
    const statsLastCompletedAt = String(stats?.lastCompletedAt || "").trim();

    return {
      ...entry,
      completedFlashcardCount: Math.max(0, Number(stats?.count) || 0),
      lastCompletedAt: statsLastCompletedAt || existingLastCompletedAt,
      statusKind: "flashcard-count",
    };
  });
}

async function loadRetentionCompletedLernbereiche(context) {
  if (!context.supabase) return [];

  const [
    { data: scopeRows, error: scopeError },
    { data: exclusionRows, error: exclusionError },
  ] = await Promise.all([
    context.supabase
      .from("user_retention_scopes")
      .select("lernbereich_slug, updated_at")
      .eq("activity_type", "flashcards")
      .eq("scope_type", "lernbereich")
      .eq("status", "active"),
    context.supabase
      .from("user_retention_check_exclusions")
      .select("lernbereich_slug, check_id"),
  ]);

  if (scopeError) throw scopeError;
  if (exclusionError) throw exclusionError;

  const activeBySlug = new Map(
    (Array.isArray(scopeRows) ? scopeRows : [])
      .filter((row) => String(row?.lernbereich_slug || "").trim())
      .map((row) => [String(row.lernbereich_slug).trim(), String(row.updated_at || "")]),
  );

  if (!activeBySlug.size) return [];

  const exclusionsBySlug = new Map();
  (Array.isArray(exclusionRows) ? exclusionRows : []).forEach((row) => {
    const slug = String(row?.lernbereich_slug || "").trim();
    const checkId = String(row?.check_id || "").trim();
    if (!slug || !checkId) return;
    if (!exclusionsBySlug.has(slug)) exclusionsBySlug.set(slug, new Set());
    exclusionsBySlug.get(slug).add(checkId);
  });

  const result = [];
  context.lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      if (!activeBySlug.has(lb.id)) return;
      const excluded = exclusionsBySlug.get(lb.id) || new Set();
      const totalCheckCount = lb.checks.length;
      const checkCount = Math.max(0, totalCheckCount - excluded.size);
      result.push({
        lernbereichId: lb.id,
        lernbereichName: lb.name,
        gebietKey: lb.gebietKey,
        groupName: group.group,
        checkCount,
        totalCheckCount,
        lastCompletedAt: activeBySlug.get(lb.id),
      });
    });
  });

  return result;
}

async function loadCompletedLernbereiche(context) {
  const [activeEntries, retentionEntries, flashcardCompletionStatsBySlug] = await Promise.all([
    loadActiveSessionCompletedLernbereiche(context),
    loadRetentionCompletedLernbereiche(context),
    loadFlashcardCompletionStatsByLernbereich(context),
  ]);

  const decoratedActiveEntries = applyFlashcardCompletionStats(activeEntries, flashcardCompletionStatsBySlug);
  const decoratedRetentionEntries = applyFlashcardCompletionStats(retentionEntries, flashcardCompletionStatsBySlug);

  const latestByLernbereichId = new Map();
  [...decoratedActiveEntries, ...decoratedRetentionEntries].forEach((entry) => {
    const key = String(entry?.lernbereichId || "").trim();
    if (!key) return;

    const current = latestByLernbereichId.get(key);
    if (!current || String(entry.lastCompletedAt || "").localeCompare(String(current.lastCompletedAt || "")) > 0) {
      latestByLernbereichId.set(key, entry);
    }
  });

  return {
    items: sortCompletedLernbereiche(latestByLernbereichId.values()),
    hasRetentionEntries: retentionEntries.length > 0,
  };
}

function buildActiveLernbereichSummary(entries, emptyMessage) {
  const activeEntries = Array.isArray(entries) ? entries : [];
  if (!activeEntries.length) {
    return emptyMessage;
  }

  const lernbereichCount = activeEntries.length;
  const checkCount = activeEntries.reduce((sum, entry) => sum + Math.max(0, Number(entry?.checkCount) || 0), 0);
  const lernbereichLabel = lernbereichCount === 1 ? "Lernbereich" : "Lernbereiche";
  const checkLabel = checkCount === 1 ? "Check" : "Checks";
  const verb = lernbereichCount === 1 ? "ist" : "sind";
  return `Aktuell ${verb} ${lernbereichCount} ${lernbereichLabel} mit ${checkCount} ${checkLabel} aktiv.`;
}

function renderDashboardLernbereichCard(entry) {
  const href = buildLernbereichStartHref(entry);
  const linkAttributes = href
    ? ` data-action-href="${escapeHtml(href)}" role="link" tabindex="0"`
    : "";
  const badgeMarkup = entry?.groupName
    ? `<div class="action-badges dashboard-panel__action-meta">${createBadgeMarkup(entry.groupName)}</div>`
    : "";
  const statusMarkup = buildDashboardLernbereichStatusMarkup(entry);

  return `
    <li class="action-card dashboard-panel__action-card" data-type="dashboard"${linkAttributes}>
      <div class="action-body">
        <div class="action-title dashboard-panel__action-title">
          <span class="dashboard-panel__action-name">${escapeHtml(entry.lernbereichName)}</span>
        </div>
        ${badgeMarkup}
      </div>
      ${statusMarkup}
    </li>
  `;
}

function renderDashboardPanelMessage(listNode, message) {
  if (!listNode) return;

  const text = String(message || "").trim();
  if (!text) {
    listNode.hidden = true;
    listNode.setAttribute("aria-hidden", "true");
    listNode.innerHTML = "";
    return;
  }

  listNode.hidden = false;
  listNode.setAttribute("aria-hidden", "false");
  listNode.innerHTML = `<li class="dashboard-panel__empty">${escapeHtml(text)}</li>`;
}

function renderDashboardLernbereichList(listNode, entries, emptyMessage) {
  if (!listNode) return;

  const activeEntries = Array.isArray(entries) ? entries : [];
  if (!activeEntries.length) {
    renderDashboardPanelMessage(listNode, emptyMessage);
    return;
  }

  listNode.hidden = false;
  listNode.setAttribute("aria-hidden", "false");
  listNode.innerHTML = activeEntries.map((entry) => renderDashboardLernbereichCard(entry)).join("");
}

function updateRetentionSummary(context, entries = [], fallbackMessage = "") {
  const node = context.elements.retentionSummary;
  if (!node) return;

  const explicitMessage = String(fallbackMessage || "").trim();
  if (explicitMessage) {
    node.textContent = explicitMessage;
    return;
  }

  node.textContent = buildActiveLernbereichSummary(entries, RETENTION_EMPTY_SUMMARY);
}

async function refreshCompletedPanel(context) {
  const listNode = context.elements.retentionList;
  if (!listNode) return;

  if (!context.supabase) {
    context.hasRetentionEntries = false;
    updateRetentionActionButtons(context, false);
    updateRetentionSummary(context, [], RETENTION_UNAVAILABLE_MESSAGE);
    renderDashboardPanelMessage(listNode, RETENTION_UNAVAILABLE_MESSAGE);
    return;
  }

  try {
    const { items: completedLernbereiche, hasRetentionEntries } = await loadCompletedLernbereiche(context);
    context.hasRetentionEntries = hasRetentionEntries;
    updateRetentionActionButtons(context, false);
    updateRetentionSummary(context, completedLernbereiche);
    renderDashboardLernbereichList(listNode, completedLernbereiche, RETENTION_EMPTY_LIST_MESSAGE);
  } catch (error) {
    context.hasRetentionEntries = false;
    updateRetentionActionButtons(context, false);
    console.error("Abgeschlossene Lernbereiche konnten nicht geladen werden:", error);
    updateRetentionSummary(context, [], RETENTION_LOAD_ERROR_MESSAGE);
    renderDashboardPanelMessage(listNode, RETENTION_LOAD_ERROR_MESSAGE);
  }
}

async function refreshPrimaryFeedCard(context) {
  if (!context.supabase) {
    applyPrimaryFeedEmptyState(context);
    return;
  }

  try {
    const projection = await loadFeedProjection({
      supabase: context.supabase,
      contentMeta: context.feedContentMeta,
      limit: 1,
    });
    const [feedItem] = (Array.isArray(projection?.items) ? projection.items : [])
      .map((item) => buildFeedCardDataFromProjection(item))
      .filter(Boolean);

    if (feedItem) {
      applyPrimaryFeedCardData(context, feedItem);
      return;
    }

    if (projection?.waiting?.nextAvailableFrom) {
      applyPrimaryFeedWaitingState(context, projection.waiting);
      return;
    }

    applyPrimaryFeedEmptyState(context);
  } catch (error) {
    console.error("Feed-Einstieg konnte nicht geladen werden:", error);
    applyPrimaryFeedErrorState(context);
  }
}

function redirectToAccount() {
  const nextPath = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  window.location.replace(buildAccountUrl(nextPath));
}

function buildStateFromPersisted(lernbereiche, lernbereichRows, exclusionRows) {
  const activeLernbereiche = new Set(
    (Array.isArray(lernbereichRows) ? lernbereichRows : [])
      .map((row) => String(row?.lernbereich_slug || "").trim())
      .filter(Boolean),
  );
  const excludedChecks = new Set(
    (Array.isArray(exclusionRows) ? exclusionRows : [])
      .map((row) => String(row?.check_id || "").trim())
      .filter(Boolean),
  );
  const nextState = {};

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      if (!activeLernbereiche.has(lb.id)) return;

      const lbState = { active: true, checks: {} };
      lb.checks.forEach((check) => {
        if (excludedChecks.has(check.id)) {
          lbState.checks[check.id] = false;
        }
      });
      nextState[lb.id] = lbState;
    });
  });

  return nextState;
}

function buildSessionPayloadBase(draft, lernbereiche) {
  const activeLernbereiche = [];
  const excludedChecks = new Set();
  const includedChecks = new Set();
  const lernbereicheMeta = [];

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const lbState = draft[lb.id];
      if (!lbState?.active) return;

      activeLernbereiche.push(lb.id);
      lernbereicheMeta.push({
        slug: lb.id,
        gebiet: lb.gebietKey,
        gebiet_order: lb.gebietOrder ?? 999,
        sort_index: lb.didacticOrder ?? 0,
      });
      lb.checks.forEach((check) => {
        if (lbState.checks?.[check.id] === false) {
          excludedChecks.add(check.id);
          return;
        }

        includedChecks.add(check.id);
      });
    });
  });

  return {
    p_lernbereiche: activeLernbereiche,
    p_excluded_check_ids: Array.from(excludedChecks),
    p_activities_per_day: null,
    p_included_check_ids: Array.from(includedChecks),
    p_lernbereiche_meta: lernbereicheMeta,
  };
}

function summarizeActivePlan(context) {
  let lernbereichCount = 0;
  let checkCount = 0;
  const selectedCheckIds = [];
  const activeLernbereichIds = [];

  context.lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const lbState = context.state[lb.id];
      if (!lbState?.active) return;

      lernbereichCount += 1;
      activeLernbereichIds.push(lb.id);
      lb.checks.forEach((check) => {
        if (!isCheckSelected(lbState, check.id)) return;
        checkCount += 1;
        selectedCheckIds.push(check.id);
      });
    });
  });

  return { lernbereichCount, checkCount, selectedCheckIds, activeLernbereichIds };
}

function buildActiveSessionProgress(context) {
  if (!context.activeSession) return null;

  const { selectedCheckIds, activeLernbereichIds } = summarizeActivePlan(context);
  const totalStepCount = activeLernbereichIds.length + (selectedCheckIds.length * CHECK_PIPELINE_STEP_COUNT);
  if (totalStepCount <= 0) {
    return null;
  }

  const remainingStepCount = Math.max(
    0,
    Math.min(totalStepCount, getRemainingSelectedSessionActivityCount(context, selectedCheckIds, activeLernbereichIds)),
  );
  const completedStepCount = Math.max(0, totalStepCount - remainingStepCount);
  const percent = Math.round((completedStepCount / totalStepCount) * 100);

  return {
    totalStepCount,
    completedStepCount,
    remainingStepCount,
    percent,
  };
}

function setPlanProgressFill(node, percent) {
  if (!node) return;

  const normalizedPercent = Math.max(0, Math.min(100, Number(percent) || 0));
  node.dataset.progress = String(normalizedPercent);

  requestAnimationFrame(() => {
    node.style.width = `${normalizedPercent}%`;
  });
}

function updatePlanProgress(context) {
  const container = context.elements.planProgress;
  if (!container) return;

  const fillNode = context.elements.planProgressFill;
  const barNode = context.elements.planProgressBar;
  const percentNode = context.elements.planProgressPercent;
  const completedNode = context.elements.planProgressCompleted;
  const remainingNode = context.elements.planProgressRemaining;
  const progress = buildActiveSessionProgress(context);

  if (!progress) {
    container.hidden = true;
    if (fillNode) {
      fillNode.dataset.progress = "0";
      fillNode.style.width = "0%";
    }
    if (barNode) {
      barNode.setAttribute("aria-valuenow", "0");
      barNode.setAttribute("aria-valuetext", "0 Prozent der aktuellen Session abgeschlossen");
    }
    return;
  }

  container.hidden = false;

  const percentLabel = `${progress.percent}%`;
  if (percentNode) {
    percentNode.textContent = percentLabel;
  }
  if (completedNode) {
    completedNode.textContent = `${progress.completedStepCount} / ${progress.totalStepCount} abgeschlossen`;
  }
  if (remainingNode) {
    remainingNode.textContent = `${progress.remainingStepCount} verbleibend`;
  }
  if (barNode) {
    barNode.setAttribute("aria-valuenow", String(progress.percent));
    barNode.setAttribute("aria-valuetext", `${percentLabel} der aktuellen Session abgeschlossen`);
  }

  setPlanProgressFill(fillNode, progress.percent);
}

function buildSessionLernbereichProgressData(selectedCheckIds, checkStateById, startState) {
  const normalizedCheckIds = Array.isArray(selectedCheckIds)
    ? selectedCheckIds.map((checkId) => String(checkId || "").trim()).filter(Boolean)
    : [];
  const totalStepCount = 1 + (normalizedCheckIds.length * CHECK_PIPELINE_STEP_COUNT);
  if (totalStepCount <= 0) return null;

  const remainingCheckStepCount = normalizedCheckIds.reduce((sum, checkId) => {
    return sum + getRemainingCheckStepCount(checkStateById.get(checkId));
  }, 0);
  const startStepCompleted = String(startState?.status || "").trim() === "completed";
  const remainingStepCount = Math.max(
    0,
    Math.min(totalStepCount, remainingCheckStepCount + (startStepCompleted ? 0 : 1)),
  );
  const completedStepCount = Math.max(0, totalStepCount - remainingStepCount);
  const percent = Math.round((completedStepCount / totalStepCount) * 100);

  return {
    totalStepCount,
    completedStepCount,
    remainingStepCount,
    percent,
  };
}

function collectActiveSessionLernbereiche(context) {
  const entries = [];
  const checkStateById = buildSessionCheckStateById(context);
  const startStateByLernbereichId = buildSessionStartStateByLernbereichId(context);

  context.lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const lbState = context.state[lb.id];
      if (!lbState?.active) return;

      const selectedChecks = lb.checks.filter((check) => isCheckSelected(lbState, check.id));
      const selectedCheckIds = selectedChecks.map((check) => check.id);

      entries.push({
        lernbereichId: lb.id,
        lernbereichName: lb.name,
        gebietKey: lb.gebietKey,
        groupName: group.group,
        checkCount: selectedCheckIds.length,
        totalCheckCount: Array.isArray(lb.checks) ? lb.checks.length : 0,
        statusKind: "session-progress",
        sessionProgress: buildSessionLernbereichProgressData(
          selectedCheckIds,
          checkStateById,
          startStateByLernbereichId.get(lb.id),
        ),
      });
    });
  });

  return entries;
}

function buildPayloadFromState(context, draft, lernbereiche, draftConfig) {
  const basePayload = {
    ...buildSessionPayloadBase(draft, lernbereiche),
  };

  const selectedCheckIds = Array.isArray(basePayload.p_included_check_ids)
    ? basePayload.p_included_check_ids
    : [];
  const targetDate = normalizeDateOnlyValue(draftConfig?.targetDate);
  if (targetDate) {
    basePayload.p_target_date = targetDate;
    basePayload.p_target_source = "explicit";
    return basePayload;
  }

  const hasActiveSelection = Array.isArray(basePayload.p_lernbereiche)
    && basePayload.p_lernbereiche.length > 0
    && selectedCheckIds.length > 0;
  if (!hasActiveSelection) {
    basePayload.p_target_date = null;
    basePayload.p_target_source = null;
    return basePayload;
  }

  const suggestion = buildSuggestedTargetDate(context, selectedCheckIds, basePayload.p_lernbereiche || []);
  basePayload.p_target_date = suggestion.suggestedDateValue || null;
  basePayload.p_target_source = suggestion.suggestedDateValue ? "suggested" : null;
  return basePayload;
}

function buildSessionCheckStateById(context) {
  return new Map(
    (Array.isArray(context.sessionCheckStates) ? context.sessionCheckStates : []).map((row) => [String(row?.check_id || "").trim(), row]),
  );
}

function buildSessionStartStateByLernbereichId(context) {
  return new Map(
    (Array.isArray(context.sessionActivityStates) ? context.sessionActivityStates : [])
      .filter((row) => String(row?.activity_type || "").trim() === "start")
      .map((row) => [String(row?.lernbereich_slug || "").trim(), row]),
  );
}

function getRemainingSelectedActivityCount(context, selectedCheckIds) {
  const checkStateById = buildSessionCheckStateById(context);
  return selectedCheckIds.reduce((sum, checkId) => {
    return sum + getRemainingCheckStepCount(checkStateById.get(checkId));
  }, 0);
}

function getRemainingSelectedStartActivityCount(context, selectedLernbereichIds) {
  const startStateByLernbereichId = buildSessionStartStateByLernbereichId(context);
  return selectedLernbereichIds.reduce((sum, lernbereichId) => {
    const row = startStateByLernbereichId.get(String(lernbereichId || "").trim());
    const status = String(row?.status || "").trim();
    return sum + (status === "completed" ? 0 : 1);
  }, 0);
}

function getRemainingSelectedSessionActivityCount(context, selectedCheckIds, selectedLernbereichIds) {
  return getRemainingSelectedActivityCount(context, selectedCheckIds)
    + getRemainingSelectedStartActivityCount(context, selectedLernbereichIds);
}

function getConfiguredPositiveNumber(value) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function buildSuggestedTargetDate(context, selectedCheckIds, selectedLernbereichIds) {
  const remainingSteps = getRemainingSelectedSessionActivityCount(context, selectedCheckIds, selectedLernbereichIds);
  const activitiesPerDay = getConfiguredPositiveNumber(context.activeSession?.activities_per_day)
    ?? getConfiguredPositiveNumber(context.systemSettings?.planningDefaultActivitiesPerDay);
  const didacticGapHours = getConfiguredPositiveNumber(context.systemSettings?.feedCoreGapNormalHours);

  if (!activitiesPerDay || !didacticGapHours) {
    return {
      suggestedDateValue: "",
      remainingSteps,
      activitiesPerDay: null,
      didacticGapHours: null,
    };
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const now = new Date();
  const checkStateById = buildSessionCheckStateById(context);

  const workloadDate = addCalendarDays(today, remainingSteps > 0 ? Math.floor((remainingSteps - 1) / activitiesPerDay) : 0);
  const earliestCompletionTimestamp = selectedCheckIds.reduce((latestTimestamp, checkId) => {
    const gapCount = getRemainingDidacticGapCount(checkStateById.get(checkId));
    return Math.max(latestTimestamp, now.getTime() + (gapCount * didacticGapHours * 60 * 60 * 1000));
  }, today.getTime());
  const earliestCompletionDate = new Date(earliestCompletionTimestamp);
  earliestCompletionDate.setHours(0, 0, 0, 0);

  // target_date = test day (start of day); last prep day must be the day BEFORE.
  // So suggest the day after the last activity.
  const lastActivityDate = workloadDate.getTime() >= earliestCompletionDate.getTime()
    ? workloadDate
    : earliestCompletionDate;
  const suggestedDate = addCalendarDays(lastActivityDate, 1);

  return {
    suggestedDateValue: toDateOnlyValue(suggestedDate),
    remainingSteps,
    activitiesPerDay,
    didacticGapHours,
  };
}

function buildTargetDateAssessment(context, selectedCheckIds, selectedLernbereichIds) {
  const defaultActivitiesPerDay = getConfiguredPositiveNumber(context.systemSettings?.planningDefaultActivitiesPerDay);
  const sessionActivitiesPerDay = getConfiguredPositiveNumber(context.activeSession?.activities_per_day);
  const realisticThreshold = sessionActivitiesPerDay ?? defaultActivitiesPerDay;
  const warningThreshold = realisticThreshold === null
    ? null
    : Math.max(realisticThreshold + 1, realisticThreshold * 2);
  const targetDateValue = normalizeDateOnlyValue(context.activeSession?.target_date);
  if (!targetDateValue) {
    const suggestion = buildSuggestedTargetDate(context, selectedCheckIds, selectedLernbereichIds);
    const targetLabel = suggestion.suggestedDateValue
      ? `Zieldatum: ${formatDateOnlyLabel(suggestion.suggestedDateValue)}`
      : "Zieldatum: nicht gesetzt.";

    if (suggestion.remainingSteps <= 0) {
      return {
        targetLabel,
        assessmentLabel: "Fertig",
        assessmentTone: "success",
      };
    }

    return {
      targetLabel,
      assessmentLabel: suggestion.suggestedDateValue ? "Offen" : "",
      assessmentTone: "neutral",
    };
  }

  const targetDate = parseDateOnlyValue(targetDateValue);
  const targetLabel = `Zieldatum: ${formatDateOnlyLabel(targetDateValue)}`;
  if (!targetDate) {
    return {
      targetLabel,
      assessmentLabel: "Fehler",
      assessmentTone: "error",
    };
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const dayDelta = Math.floor((targetDate.getTime() - today.getTime()) / 86400000);
  // target_date = test day; prep days = days strictly before it.
  const availableDays = Math.max(dayDelta, 1);

  const remainingSteps = getRemainingSelectedSessionActivityCount(context, selectedCheckIds, selectedLernbereichIds);

  if (remainingSteps <= 0) {
    return {
      targetLabel,
      assessmentLabel: "Fertig",
      assessmentTone: "success",
    };
  }

  if (dayDelta < 0) {
    return {
      targetLabel,
      assessmentLabel: "Verstrichen",
      assessmentTone: "error",
    };
  }

  const targetEndMs = targetDate.getTime(); // deadline = start of target day (00:00)
  const checkStateById = buildSessionCheckStateById(context);
  const hasTimingConflict = (Array.isArray(selectedCheckIds) ? selectedCheckIds : []).some((checkId) => {
    const row = checkStateById.get(checkId);
    if (!row || String(row?.current_step_status || "").trim() !== "due") return false;
    const af = row?.available_from ? new Date(row.available_from).getTime() : NaN;
    return Number.isFinite(af) && af >= targetEndMs;
  });
  if (hasTimingConflict) {
    return {
      targetLabel,
      assessmentLabel: "Unrealistisch",
      assessmentTone: "error",
    };
  }

  if (realisticThreshold === null || warningThreshold === null) {
    return {
      targetLabel,
      assessmentLabel: "",
      assessmentTone: "neutral",
    };
  }

  const stepsPerDay = remainingSteps / availableDays;

  if (stepsPerDay <= realisticThreshold) {
    return {
      targetLabel,
      assessmentLabel: "Realistisch",
      assessmentTone: "success",
    };
  }

  if (stepsPerDay <= warningThreshold) {
    return {
      targetLabel,
      assessmentLabel: "Sportlich",
      assessmentTone: "warning",
    };
  }

  return {
    targetLabel,
    assessmentLabel: "Unrealistisch",
    assessmentTone: "error",
  };
}

function syncPlanningInputs(context) {
  if (!context.elements.targetDateInput) return;
  context.elements.targetDateInput.value = normalizeDateOnlyValue(context.draftConfig?.targetDate);
}

function updatePlanSummary(context) {
  const node = context.elements.planSummary;
  if (!node) return;

  const targetNode = context.elements.planTarget;
  const targetLabelNode = context.elements.planTargetLabel;
  const assessmentNode = context.elements.planAssessment;
  const activeEntries = collectActiveSessionLernbereiche(context);

  if (!context.activeSession || !activeEntries.length) {
    node.textContent = SESSION_EMPTY_SUMMARY;
    updatePlanProgress(context);
    if (targetNode) {
      targetNode.hidden = true;
    }
    if (targetLabelNode) {
      targetLabelNode.textContent = "";
    }
    if (assessmentNode) {
      setStatusNode(assessmentNode, "");
    }
    updateGreetingHeading(context);
    return;
  }

  const { selectedCheckIds, activeLernbereichIds } = summarizeActivePlan(context);
  node.textContent = buildActiveLernbereichSummary(activeEntries, SESSION_EMPTY_SUMMARY);
  updatePlanProgress(context);

  if (targetNode) {
    const assessment = buildTargetDateAssessment(context, selectedCheckIds, activeLernbereichIds);
    targetNode.hidden = false;
    if (targetLabelNode) {
      targetLabelNode.textContent = assessment.targetLabel;
    }
    if (assessmentNode) {
      setStatusNode(assessmentNode, assessment.assessmentLabel, assessment.assessmentTone);
    }
  }

  updateGreetingHeading(context);
}

async function loadPersistedState(supabase, lernbereiche) {
  const { data: sessions, error: sessionError } = await supabase
    .from("learning_sessions")
    .select("id, activities_per_day, started_at, target_date, target_source")
    .eq("status", "active")
    .order("started_at", { ascending: false })
    .limit(1);

  if (sessionError) {
    throw sessionError;
  }

  const activeSession = Array.isArray(sessions) ? sessions[0] || null : null;
  if (!activeSession?.id) {
    return { state: {}, session: null, checkStates: [], activityStates: [] };
  }

  const [
    { data: lernbereicheRows, error: lernbereicheError },
    { data: exclusionRows, error: exclusionError },
    { data: checkStateRows, error: checkStateError },
    { data: activityStateRows, error: activityStateError },
  ] = await Promise.all([
    supabase
      .from("session_lernbereiche")
      .select("lernbereich_slug")
      .eq("session_id", activeSession.id),
    supabase
      .from("session_check_exclusions")
      .select("check_id")
      .eq("session_id", activeSession.id),
    supabase
      .from("session_check_state")
      .select("check_id, current_step_key, current_step_status, overdue_from, available_from")
      .eq("session_id", activeSession.id),
    supabase
      .from("session_activity_state")
      .select("lernbereich_slug, activity_type, status")
      .eq("session_id", activeSession.id)
      .eq("activity_type", "start"),
  ]);

  if (lernbereicheError) throw lernbereicheError;
  if (exclusionError) throw exclusionError;
  if (checkStateError) throw checkStateError;
  if (activityStateError) throw activityStateError;

  return {
    state: buildStateFromPersisted(lernbereiche, lernbereicheRows, exclusionRows),
    session: activeSession,
    checkStates: Array.isArray(checkStateRows) ? checkStateRows : [],
    activityStates: Array.isArray(activityStateRows) ? activityStateRows : [],
  };
}

function updateSessionList(context) {
  renderDashboardLernbereichList(
    context.elements.sessionList,
    collectActiveSessionLernbereiche(context),
    SESSION_EMPTY_LIST_MESSAGE,
  );
}

function setDashboardMenuItemDisabledState(button, disabled) {
  if (!button) return;
  const isDisabled = Boolean(disabled);
  button.disabled = isDisabled;
  button.classList.toggle("check-card__actions-item--disabled", isDisabled);
}

function updateSessionActionButtons(context, disabled) {
  setDashboardMenuItemDisabledState(context.elements.openButton, disabled);
  setDashboardMenuItemDisabledState(context.elements.deleteButton, disabled || !context.activeSession);
}

function updateRetentionActionButtons(context, disabled) {
  setDashboardMenuItemDisabledState(context.elements.retentionManageButton, disabled);
  setDashboardMenuItemDisabledState(context.elements.retentionDeleteButton, disabled || !context.hasRetentionEntries);
}

function setBarStatus(context, message, tone = "neutral") {
  setStatusNode(context.elements.statusNode, message, tone);
}

function setModalStatus(context, message, tone = "neutral") {
  setStatusNode(context.elements.modalStatusNode, message, tone);
}

function setRetentionBarStatus(context, message, tone = "neutral") {
  setStatusNode(context.elements.retentionStatusNode, message, tone);
}

function closeModal(context) {
  context.elements.overlay.classList.remove("open");
  document.body.style.overflow = "";
  setModalStatus(context, "");
}

function updateCount(item, lb, draft) {
  const lbState = draft[lb.id] || { active: false, checks: {} };
  const total = lb.checks.length;
  const selected = countSelectedChecks(lb, lbState);
  item.querySelector(".lb-accord-count").textContent = `${lbState.active ? `${selected}/${total}` : total} Checks`;
}

function buildModal(context) {
  const { container } = context.elements;
  container.innerHTML = "";

  context.lernbereiche.forEach((group) => {
    const divider = document.createElement("div");
    divider.className = "lb-group-divider";
    divider.innerHTML = `<div class="lb-group-div-icon" style="background:${escapeHtml(group.iconBg)};color:${escapeHtml(group.iconColor)};">${escapeHtml(group.icon)}</div><span>${escapeHtml(group.group)}</span>`;
    container.appendChild(divider);

    group.items.forEach((lb) => {
      const lbState = context.draft[lb.id] || { active: false, checks: {} };
      const item = document.createElement("div");
      item.className = `lb-accord-item${lbState.active ? " active" : ""}`;
      item.dataset.id = lb.id;

      const total = lb.checks.length;
      const selected = countSelectedChecks(lb, lbState);

      item.innerHTML = `
        <div class="lb-accord-head">
          <label class="lb-toggle">
            <input type="checkbox" ${lbState.active ? "checked" : ""}>
            <span class="lb-toggle-slider"></span>
          </label>
          <span class="lb-accord-title">${escapeHtml(lb.name)}</span>
          <span class="lb-accord-count">${lbState.active ? `${selected}/${total}` : total} Checks</span>
          <span class="lb-accord-arrow">›</span>
        </div>
        <div class="lb-accord-body">
          <div class="lb-kompetenz-actions">
            <button class="btn-ghost btn-xs" data-action="all" type="button">Alle auswählen</button>
            <button class="btn-ghost btn-xs" data-action="none" type="button">Alle abwählen</button>
          </div>
          <div class="lb-kompetenz-list">
            ${lb.checks.map((check) => {
              const checked = isCheckSelected(lbState, check.id);
              const disabled = !lbState.active;
              return `<label class="lb-kompetenz${disabled ? " disabled" : ""}">
                <input type="checkbox" ${checked ? "checked" : ""} ${disabled ? "disabled" : ""} data-check-id="${escapeHtml(check.id)}">
                ${escapeHtml(check.label)}
              </label>`;
            }).join("")}
          </div>
        </div>`;

      const toggleLabel = item.querySelector(".lb-toggle");
      const toggle = item.querySelector(".lb-toggle input");

      toggleLabel?.addEventListener("click", (event) => {
        event.stopPropagation();
      });

      toggle.addEventListener("change", () => {
        const isActive = toggle.checked;
        if (!context.draft[lb.id]) {
          context.draft[lb.id] = { active: false, checks: {} };
        }

        context.draft[lb.id].active = isActive;
        if (isActive) {
          lb.checks.forEach((check) => {
            if (context.draft[lb.id].checks[check.id] === undefined) {
              context.draft[lb.id].checks[check.id] = true;
            }
          });
          item.classList.add("active");
        } else {
          item.classList.remove("active");
        }

        const checkboxes = Array.from(item.querySelectorAll(".lb-kompetenz input"));
        const labels = Array.from(item.querySelectorAll(".lb-kompetenz"));
        checkboxes.forEach((checkbox, index) => {
          checkbox.disabled = !isActive;
          if (isActive && context.draft[lb.id].checks[lb.checks[index].id] !== false) {
            checkbox.checked = true;
          }
          labels[index].classList.toggle("disabled", !isActive);
        });

        updateCount(item, lb, context.draft);
      });

      item.querySelector(".lb-accord-head")?.addEventListener("click", (event) => {
        if (event.target.closest(".lb-toggle")) return;
        item.classList.toggle("open");
      });

      item.querySelectorAll(".lb-kompetenz input").forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
          if (!context.draft[lb.id]) {
            context.draft[lb.id] = { active: true, checks: {} };
          }

          context.draft[lb.id].checks[checkbox.dataset.checkId] = checkbox.checked;
          updateCount(item, lb, context.draft);
        });
      });

      item.querySelector('[data-action="all"]')?.addEventListener("click", () => {
        if (!context.draft[lb.id]?.active) return;
        item.querySelectorAll(".lb-kompetenz input").forEach((checkbox) => {
          checkbox.checked = true;
          context.draft[lb.id].checks[checkbox.dataset.checkId] = true;
        });
        updateCount(item, lb, context.draft);
      });

      item.querySelector('[data-action="none"]')?.addEventListener("click", () => {
        if (!context.draft[lb.id]?.active) return;
        item.querySelectorAll(".lb-kompetenz input").forEach((checkbox) => {
          checkbox.checked = false;
          context.draft[lb.id].checks[checkbox.dataset.checkId] = false;
        });
        updateCount(item, lb, context.draft);
      });

      container.appendChild(item);
    });
  });
}

function openModal(context) {
  if (!context.authState?.user || !context.lernbereiche.length) return;
  context.draft = cloneState(context.state);
  context.draftConfig = {
    targetDate: normalizeDateOnlyValue(context.activeSession?.target_date),
  };
  setModalStatus(context, "");
  buildModal(context);
  syncPlanningInputs(context);
  context.elements.overlay.classList.add("open");
  document.body.style.overflow = "hidden";
}

function setMutationBusy(context, busy, mode = "save") {
  context.isSaving = busy;
  context.elements.saveButton.disabled = busy;
  context.elements.resetButton.disabled = busy;
  context.elements.closeButton.disabled = busy;
  context.elements.saveButton.textContent = busy && mode === "save" ? "Speichern ..." : "Übernehmen";
  updateSessionActionButtons(context, busy);
}

function mapSessionError(error) {
  const code = String(error?.code || error?.error_code || "").trim().toUpperCase();
  const message = String(error?.message || "").trim();
  const normalized = message.toLowerCase();

  if (code === "PGRST202") {
     return "Die Session-Funktion ist noch nicht im API-Schema verfügbar. Seite neu laden und erneut versuchen.";
  }
  if (message.includes("Authentication required")) {
     return "Bitte melde dich zuerst an, um deine Session zu speichern.";
  }
    if (message.includes("activities_per_day must be positive")) {
     return "Die Session konnte mit diesem Tempo nicht gespeichert werden.";
  }
    if (message.includes("target_date must be today or later")) {
      return "Das Zieldatum muss heute oder später liegen.";
    }
    if (message.includes("unsupported target_source")) {
      return "Das Zieldatum konnte mit dieser Quelle nicht gespeichert werden.";
    }
  if (normalized.includes("an active learning session already exists")) {
     return "Für dieses Konto existiert bereits eine aktive Session. Wenn die Meldung bleibt, liegt vermutlich eine Inkonsistenz im Session-Stand vor.";
  }
  if (normalized.includes("query returned more than one row")) {
     return "Für dieses Konto wurden mehrere aktive Sessions gefunden. Das ist eine Dateninkonsistenz und blockiert das Speichern.";
  }
  if (
    code === "42P01"
    || code === "42703"
    || normalized.includes("session_check_state")
    || normalized.includes("session_activity_state")
    || normalized.includes("session_flashcard")
    || normalized.includes("refresh_flashcard_activity_for_lernbereich")
  ) {
     return "Die Session-/Feed-Migrationen sind im Supabase-Projekt noch nicht vollständig aktiv. Bitte die aktuellen Migrationen deployen und dann erneut speichern.";
  }
  if (message) {
     return `Die aktive Session konnte nicht gespeichert werden. Detail: ${message}`;
  }

    return "Die aktive Session konnte nicht gespeichert werden.";
}

function mapDeleteSessionError(error) {
  const code = String(error?.code || error?.error_code || "").trim();
  const message = String(error?.message || "").trim();

  if (code === "PGRST202") {
    return "Die Löschfunktion für die aktive Session ist noch nicht im API-Schema verfügbar. Seite neu laden und erneut versuchen.";
  }
  if (message.includes("Authentication required")) {
     return "Bitte melde dich zuerst an, um deine Session zu löschen.";
  }

  if (
   code === "42P01"
   || code === "42703"
   || message.toLowerCase().includes("learning_activity_attempts")
  ) {
    return "Die Session-Löschlogik ist im Supabase-Projekt noch nicht vollständig aktiv. Bitte die aktuellen Migrationen deployen und erneut versuchen.";
  }

   return "Die aktive Session konnte nicht gelöscht werden.";
}

function mapDeleteRetentionError(error) {
  const code = String(error?.code || error?.error_code || "").trim();
  const message = String(error?.message || "").trim();
  const normalized = message.toLowerCase();

  if (code === "PGRST202") {
    return "Die Löschfunktion für Wiederholungen ist noch nicht im API-Schema verfügbar. Seite neu laden und erneut versuchen.";
  }
  if (message.includes("Authentication required")) {
    return "Bitte melde dich zuerst an, um deine Wiederholungen zu löschen.";
  }
  if (
   code === "42P01"
   || code === "42703"
   || normalized.includes("user_retention_scopes")
   || normalized.includes("retention_flashcard")
   || normalized.includes("user_retention_check_exclusions")
  ) {
    return "Die Retention-Löschlogik ist im Supabase-Projekt noch nicht vollständig aktiv. Bitte die aktuellen Migrationen deployen und erneut versuchen.";
  }

   return "Die Wiederholungen konnten nicht gelöscht werden.";
}

async function handleSave(context) {
  if (context.isSaving) return;
  if (!context.supabase || !context.authState?.user) {
    setModalStatus(context, "Bitte melde dich zuerst an, um deine Session zu speichern.", "error");
    setBarStatus(context, "Bitte melde dich zuerst an, um deine Session zu speichern.", "error");
    return;
  }

  const payload = buildPayloadFromState(context, context.draft, context.lernbereiche, context.draftConfig);

  setMutationBusy(context, true, "save");
  setModalStatus(context, "Speichere Session ...");

  try {
    const { error } = await context.supabase.rpc("save_active_learning_session", payload);
    if (error) throw error;

    const persisted = await loadPersistedState(context.supabase, context.lernbereiche);
    context.state = persisted.state;
    context.activeSession = persisted.session;
    context.sessionCheckStates = persisted.checkStates;
    context.sessionActivityStates = persisted.activityStates;
    updatePlanSummary(context);
    updateSessionList(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
      refreshActivityOverview(context),
    ]);
    notifyFeedBadgeRefresh();
    closeModal(context);
    setBarStatus(context, "");
  } catch (error) {
    console.error("Aktive Session konnte nicht gespeichert werden:", error);
    const mappedError = mapSessionError(error);
    setModalStatus(context, mappedError, "error");
    setBarStatus(context, mappedError, "error");
  } finally {
    setMutationBusy(context, false);
  }
}

async function handleDelete(context) {
  if (context.isSaving) return;
  if (!context.supabase || !context.authState?.user) {
    setBarStatus(context, "Bitte melde dich zuerst an, um deine Session zu löschen.", "error");
    return;
  }
  if (!context.activeSession?.id) {
    return;
  }

  const confirmed = window.confirm(
    "Aktive Session wirklich löschen? Das entfernt die aktive Session mit ihren sessionbezogenen Schritten, Versuchen und Feed-Einträgen. Wiederholungen bleiben unverändert.",
  );
  if (!confirmed) return;

  setMutationBusy(context, true, "delete");
  setBarStatus(context, "");

  try {
    const { error } = await context.supabase.rpc("delete_active_learning_session");
    if (error) throw error;

    context.state = {};
    context.draft = {};
    context.draftConfig = { targetDate: "" };
    context.activeSession = null;
    context.sessionCheckStates = [];
    context.sessionActivityStates = [];
    updatePlanSummary(context);
    updateSessionList(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
      refreshActivityOverview(context),
    ]);
    notifyFeedBadgeRefresh();
    closeModal(context);
    setBarStatus(context, "Aktive Session gelöscht. Wiederholungen bleiben unverändert.", "success");
  } catch (error) {
    console.error("Aktive Session konnte nicht gelöscht werden:", error);
    setBarStatus(context, mapDeleteSessionError(error), "error");
  } finally {
    setMutationBusy(context, false);
  }
}

async function handleRetentionDelete(context) {
  if (context.retentionIsSaving) return;
  if (!context.supabase || !context.authState?.user) {
    setRetentionBarStatus(context, "Bitte melde dich zuerst an, um deine Wiederholungen zu löschen.", "error");
    return;
  }

  const confirmed = window.confirm(
    "Alle Wiederholungen wirklich löschen? Das entfernt alle Retention-Lernbereiche mit Check-Auswahl, Flashcard-Ständen, laufenden Durchgängen und retentionbezogenen Feed-Einträgen. Die aktuelle Session bleibt unverändert.",
  );
  if (!confirmed) return;

  setRetentionMutationBusy(context, true);
  setRetentionBarStatus(context, "");

  try {
    const { error } = await context.supabase.rpc("delete_all_retention_data");
    if (error) throw error;

    if (context.elements.retentionOverlay?.classList.contains("open")) {
      closeRetentionModal(context);
    }

    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
    ]);
    notifyFeedBadgeRefresh();
    setRetentionBarStatus(context, "Wiederholungen gelöscht. Die aktuelle Session bleibt unverändert.", "success");
  } catch (error) {
    console.error("Wiederholungen konnten nicht gelöscht werden:", error);
    setRetentionBarStatus(context, mapDeleteRetentionError(error), "error");
  } finally {
    setRetentionMutationBusy(context, false);
  }
}

function bindEvents(context) {
  context.elements.openButton.addEventListener("click", () => {
    openModal(context);
  });

  context.elements.deleteButton.addEventListener("click", () => {
    void handleDelete(context);
  });

  context.elements.retentionDeleteButton?.addEventListener("click", () => {
    void handleRetentionDelete(context);
  });

  context.elements.closeButton.addEventListener("click", () => {
    if (context.isSaving) return;
    closeModal(context);
  });

  context.elements.overlay.addEventListener("click", (event) => {
    if (context.isSaving) return;
    if (event.target === context.elements.overlay) {
      closeModal(context);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && context.elements.overlay.classList.contains("open") && !context.isSaving) {
      closeModal(context);
    }
  });

  context.elements.targetDateInput?.addEventListener("input", () => {
    if (!context.draftConfig) {
      context.draftConfig = { targetDate: "" };
    }
    context.draftConfig.targetDate = normalizeDateOnlyValue(context.elements.targetDateInput.value);
  });

  context.elements.resetButton.addEventListener("click", () => {
    if (context.isSaving) return;
    context.draft = {};
    context.draftConfig = { targetDate: "" };
    buildModal(context);
    syncPlanningInputs(context);
    setModalStatus(context, "Auswahl lokal zurückgesetzt. Mit Übernehmen speicherst du sie dauerhaft.");
  });

  context.elements.saveButton.addEventListener("click", () => {
    void handleSave(context);
  });

  // Retention-Modal Events
  context.elements.retentionManageButton?.addEventListener("click", () => {
    void openRetentionModal(context);
  });

  context.elements.retentionCloseButton?.addEventListener("click", () => {
    if (context.retentionIsSaving) return;
    closeRetentionModal(context);
  });

  context.elements.retentionOverlay?.addEventListener("click", (event) => {
    if (context.retentionIsSaving) return;
    if (event.target === context.elements.retentionOverlay) {
      closeRetentionModal(context);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      context.elements.retentionOverlay?.classList.contains("open") &&
      !context.retentionIsSaving
    ) {
      closeRetentionModal(context);
    }
  });

  context.elements.retentionResetButton?.addEventListener("click", () => {
    if (context.retentionIsSaving) return;
    void openRetentionModal(context);
  });

  context.elements.retentionSaveButton?.addEventListener("click", () => {
    void handleRetentionSave(context);
  });
}

// ─── Retention-Modal ───────────────────────────────────────────────────────

function buildRetentionStateFromPersisted(lernbereiche, scopeRows, exclusionRows) {
  const activeBySlug = new Set(
    (Array.isArray(scopeRows) ? scopeRows : [])
      .map((row) => String(row?.lernbereich_slug || "").trim())
      .filter(Boolean),
  );
  const exclusionsBySlug = new Map();
  (Array.isArray(exclusionRows) ? exclusionRows : []).forEach((row) => {
    const slug = String(row?.lernbereich_slug || "").trim();
    const checkId = String(row?.check_id || "").trim();
    if (!slug || !checkId) return;
    if (!exclusionsBySlug.has(slug)) exclusionsBySlug.set(slug, new Set());
    exclusionsBySlug.get(slug).add(checkId);
  });

  const state = {};
  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const isActive = activeBySlug.has(lb.id);
      const excluded = exclusionsBySlug.get(lb.id) || new Set();
      const lbState = { active: isActive, checks: {} };
      lb.checks.forEach((check) => {
        if (excluded.has(check.id)) {
          lbState.checks[check.id] = false;
        }
      });
      state[lb.id] = lbState;
    });
  });
  return state;
}

function buildRetentionDraftPayload(retentionDraft, lernbereiche) {
  const activeLernbereiche = [];
  const excludedChecksBySlug = {};

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const lbState = retentionDraft[lb.id];
      if (!lbState?.active) return;
      activeLernbereiche.push(lb.id);
      const excluded = lb.checks
        .filter((check) => lbState.checks?.[check.id] === false)
        .map((check) => check.id);
      if (excluded.length) {
        excludedChecksBySlug[lb.id] = excluded;
      }
    });
  });

  return {
    p_active_lernbereiche: activeLernbereiche,
    p_excluded_check_ids: Object.keys(excludedChecksBySlug).length ? excludedChecksBySlug : {},
  };
}

function collectNewlyActivatedRetentionLernbereiche(retentionDraft, persistedRetentionDraft, lernbereiche) {
  const newlyActivated = [];

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const wasActive = Boolean(persistedRetentionDraft?.[lb.id]?.active);
      const isActive = Boolean(retentionDraft?.[lb.id]?.active);
      if (!wasActive && isActive) {
        newlyActivated.push(lb.id);
      }
    });
  });

  return newlyActivated;
}

function setRetentionModalStatus(context, message, tone = "neutral") {
  setStatusNode(context.elements.retentionModalStatusNode, message, tone);
}

function closeRetentionModal(context) {
  context.elements.retentionOverlay.classList.remove("open");
  document.body.style.overflow = "";
  setRetentionModalStatus(context, "");
}

function updateRetentionCount(item, lb, retentionDraft) {
  const lbState = retentionDraft[lb.id] || { active: false, checks: {} };
  const total = lb.checks.length;
  const selected = countSelectedChecks(lb, lbState);
  item.querySelector(".lb-accord-count").textContent = `${lbState.active ? `${selected}/${total}` : total} Checks`;
}

function buildRetentionModal(context) {
  const { retentionContainer } = context.elements;
  retentionContainer.innerHTML = "";

  context.lernbereiche.forEach((group) => {
    const divider = document.createElement("div");
    divider.className = "lb-group-divider";
    divider.innerHTML = `<div class="lb-group-div-icon" style="background:${escapeHtml(group.iconBg)};color:${escapeHtml(group.iconColor)};">${escapeHtml(group.icon)}</div><span>${escapeHtml(group.group)}</span>`;
    retentionContainer.appendChild(divider);

    group.items.forEach((lb) => {
      const lbState = context.retentionDraft[lb.id] || { active: false, checks: {} };
      const item = document.createElement("div");
      item.className = `lb-accord-item${lbState.active ? " active" : ""}`;
      item.dataset.id = lb.id;

      const total = lb.checks.length;
      const selected = countSelectedChecks(lb, lbState);

      item.innerHTML = `
        <div class="lb-accord-head">
          <label class="lb-toggle">
            <input type="checkbox" ${lbState.active ? "checked" : ""}>
            <span class="lb-toggle-slider"></span>
          </label>
          <span class="lb-accord-title">${escapeHtml(lb.name)}</span>
          <span class="lb-accord-count">${lbState.active ? `${selected}/${total}` : total} Checks</span>
          <span class="lb-accord-arrow">›</span>
        </div>
        <div class="lb-accord-body">
          <div class="lb-kompetenz-actions">
            <button class="btn-ghost btn-xs" data-action="all" type="button">Alle auswählen</button>
            <button class="btn-ghost btn-xs" data-action="none" type="button">Alle abwählen</button>
          </div>
          <div class="lb-kompetenz-list">
            ${lb.checks.map((check) => {
              const checked = isCheckSelected(lbState, check.id);
              const disabled = !lbState.active;
              return `<label class="lb-kompetenz${disabled ? " disabled" : ""}">
                <input type="checkbox" ${checked ? "checked" : ""} ${disabled ? "disabled" : ""} data-check-id="${escapeHtml(check.id)}">
                ${escapeHtml(check.label)}
              </label>`;
            }).join("")}
          </div>
        </div>`;

      const toggleLabel = item.querySelector(".lb-toggle");
      const toggle = item.querySelector(".lb-toggle input");

      toggleLabel?.addEventListener("click", (event) => {
        event.stopPropagation();
      });

      toggle.addEventListener("change", () => {
        const isActive = toggle.checked;
        if (!context.retentionDraft[lb.id]) {
          context.retentionDraft[lb.id] = { active: false, checks: {} };
        }
        context.retentionDraft[lb.id].active = isActive;
        if (isActive) {
          lb.checks.forEach((check) => {
            if (context.retentionDraft[lb.id].checks[check.id] === undefined) {
              context.retentionDraft[lb.id].checks[check.id] = true;
            }
          });
          item.classList.add("active");
        } else {
          item.classList.remove("active");
        }
        const checkboxes = Array.from(item.querySelectorAll(".lb-kompetenz input"));
        const labels = Array.from(item.querySelectorAll(".lb-kompetenz"));
        checkboxes.forEach((checkbox, index) => {
          checkbox.disabled = !isActive;
          if (isActive && context.retentionDraft[lb.id].checks[lb.checks[index].id] !== false) {
            checkbox.checked = true;
          }
          labels[index].classList.toggle("disabled", !isActive);
        });
        updateRetentionCount(item, lb, context.retentionDraft);
      });

      item.querySelector(".lb-accord-head")?.addEventListener("click", (event) => {
        if (event.target.closest(".lb-toggle")) return;
        item.classList.toggle("open");
      });

      item.querySelectorAll(".lb-kompetenz input").forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
          if (!context.retentionDraft[lb.id]) {
            context.retentionDraft[lb.id] = { active: true, checks: {} };
          }
          context.retentionDraft[lb.id].checks[checkbox.dataset.checkId] = checkbox.checked;
          updateRetentionCount(item, lb, context.retentionDraft);
        });
      });

      item.querySelector('[data-action="all"]')?.addEventListener("click", () => {
        if (!context.retentionDraft[lb.id]?.active) return;
        item.querySelectorAll(".lb-kompetenz input").forEach((checkbox) => {
          checkbox.checked = true;
          context.retentionDraft[lb.id].checks[checkbox.dataset.checkId] = true;
        });
        updateRetentionCount(item, lb, context.retentionDraft);
      });

      item.querySelector('[data-action="none"]')?.addEventListener("click", () => {
        if (!context.retentionDraft[lb.id]?.active) return;
        item.querySelectorAll(".lb-kompetenz input").forEach((checkbox) => {
          checkbox.checked = false;
          context.retentionDraft[lb.id].checks[checkbox.dataset.checkId] = false;
        });
        updateRetentionCount(item, lb, context.retentionDraft);
      });

      retentionContainer.appendChild(item);
    });
  });
}

async function openRetentionModal(context) {
  if (!context.authState?.user || !context.lernbereiche.length || !context.supabase) return;

  setRetentionModalStatus(context, "");
  context.retentionDraft = {};
  context.retentionPersistedDraft = {};
  context.elements.retentionOverlay.classList.add("open");
  document.body.style.overflow = "hidden";

  try {
    const [{ data: scopeRows, error: scopeError }, { data: exclusionRows, error: exclusionError }] = await Promise.all([
      context.supabase
        .from("user_retention_scopes")
        .select("lernbereich_slug")
        .eq("activity_type", "flashcards")
        .eq("scope_type", "lernbereich")
        .eq("status", "active"),
      context.supabase
        .from("user_retention_check_exclusions")
        .select("lernbereich_slug, check_id"),
    ]);

    if (scopeError) throw scopeError;
    if (exclusionError) throw exclusionError;

    context.retentionDraft = buildRetentionStateFromPersisted(context.lernbereiche, scopeRows, exclusionRows);
    context.retentionPersistedDraft = cloneState(context.retentionDraft);
    buildRetentionModal(context);
  } catch (error) {
    console.error("Retention-Scopes konnten nicht geladen werden:", error);
    setRetentionModalStatus(context, "Der aktuelle Wiederholungsstand konnte nicht geladen werden.", "error");
  }
}

function setRetentionMutationBusy(context, busy) {
  context.retentionIsSaving = busy;
  updateRetentionActionButtons(context, busy);
  context.elements.retentionSaveButton.disabled = busy;
  context.elements.retentionResetButton.disabled = busy;
  context.elements.retentionCloseButton.disabled = busy;
  context.elements.retentionSaveButton.textContent = busy ? "Speichern ..." : "Übernehmen";
}

function mapRetentionError(error) {
  const code = String(error?.code || error?.error_code || "").trim().toUpperCase();
  const message = String(error?.message || "").trim();

  if (code === "PGRST202") {
    return "Die Retention-Funktion ist noch nicht im API-Schema verfügbar. Seite neu laden und erneut versuchen.";
  }
  if (message.includes("Authentication required")) {
    return "Bitte melde dich zuerst an.";
  }
  if (code === "42P01" || code === "42703") {
    return "Die Retention-Migrationen sind noch nicht vollständig aktiv. Bitte deployen und erneut versuchen.";
  }
  if (message) {
    return `Wiederholungen konnten nicht gespeichert werden. Detail: ${message}`;
  }
  return "Wiederholungen konnten nicht gespeichert werden.";
}

async function handleRetentionSave(context) {
  if (context.retentionIsSaving) return;
  if (!context.supabase || !context.authState?.user) {
    setRetentionModalStatus(context, "Bitte melde dich zuerst an.", "error");
    return;
  }

  const payload = buildRetentionDraftPayload(context.retentionDraft, context.lernbereiche);
  const newlyActivatedLernbereiche = collectNewlyActivatedRetentionLernbereiche(
    context.retentionDraft,
    context.retentionPersistedDraft,
    context.lernbereiche,
  );

  setRetentionMutationBusy(context, true);
  setRetentionModalStatus(context, "Speichere Wiederholungen ...");

  try {
    const { error } = await context.supabase.rpc("manage_retention_scopes", payload);
    if (error) throw error;

    if (newlyActivatedLernbereiche.length) {
      rememberManualRetentionPriority(newlyActivatedLernbereiche);
    }

    context.retentionPersistedDraft = cloneState(context.retentionDraft);

    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
    ]);
    notifyFeedBadgeRefresh();
    closeRetentionModal(context);
  } catch (error) {
    console.error("Retention-Scopes konnten nicht gespeichert werden:", error);
    setRetentionModalStatus(context, mapRetentionError(error), "error");
  } finally {
    setRetentionMutationBusy(context, false);
  }
}

// ─── Ende Retention-Modal ──────────────────────────────────────────────────

function createContext(root, lernbereiche) {
  const elements = {
    greetingHeading: root.querySelector("[data-dashboard-greeting-heading]"),
    openButton: document.getElementById("lbOpenBtn"),
    deleteButton: document.getElementById("lbDeleteBtn"),
    closeButton: document.getElementById("lbCloseBtn"),
    saveButton: document.getElementById("lbSaveBtn"),
    resetButton: document.getElementById("lbResetBtn"),
    overlay: document.getElementById("lbOverlay"),
    sessionList: root.querySelector("[data-dashboard-session-list]"),
    planSummary: root.querySelector("[data-dashboard-plan-summary]"),
    planProgress: root.querySelector("[data-dashboard-plan-progress]"),
    planProgressBar: root.querySelector("[data-dashboard-plan-progress-bar]"),
    planProgressFill: root.querySelector("[data-dashboard-plan-progress-fill]"),
    planProgressPercent: root.querySelector("[data-dashboard-plan-progress-percent]"),
    planProgressCompleted: root.querySelector("[data-dashboard-plan-progress-completed]"),
    planProgressRemaining: root.querySelector("[data-dashboard-plan-progress-remaining]"),
    planTarget: root.querySelector("[data-dashboard-plan-target]"),
    planTargetLabel: root.querySelector("[data-dashboard-plan-target-label]"),
    planAssessment: root.querySelector("[data-dashboard-plan-assessment]"),
    primaryFeedButton: root.querySelector("[data-dashboard-primary-feed-button]"),
    primaryFeedTitle: root.querySelector("[data-dashboard-primary-feed-title]"),
    primaryFeedModule: root.querySelector("[data-dashboard-primary-feed-module]"),
    container: document.getElementById("lbAccordionContainer"),
    targetDateInput: document.getElementById("lbTargetDateInput"),
    statusNode: document.getElementById("lbSessionStatus"),
    modalStatusNode: document.getElementById("lbModalStatus"),
    retentionList: root.querySelector("[data-dashboard-retention-list]"),
    retentionSummary: root.querySelector("[data-dashboard-retention-summary]"),
    retentionManageButton: document.getElementById("retentionOpenBtn"),
    retentionDeleteButton: document.getElementById("retentionDeleteBtn"),
    retentionOverlay: document.getElementById("retentionOverlay"),
    retentionContainer: document.getElementById("retentionAccordionContainer"),
    retentionCloseButton: document.getElementById("retentionCloseBtn"),
    retentionSaveButton: document.getElementById("retentionSaveBtn"),
    retentionResetButton: document.getElementById("retentionResetBtn"),
    retentionModalStatusNode: document.getElementById("retentionModalStatus"),
    retentionStatusNode: document.getElementById("retentionStatus"),
    activitySummary: root.querySelector("[data-dashboard-activity-summary]"),
    activityTotal: root.querySelector("[data-dashboard-activity-total]"),
    activityMeta: root.querySelector("[data-dashboard-activity-meta]"),
    activityActiveDays: root.querySelector("[data-dashboard-activity-active-days]"),
    activityAverage: root.querySelector("[data-dashboard-activity-average]"),
    activityTraining: root.querySelector("[data-dashboard-activity-training]"),
    activityRecall: root.querySelector("[data-dashboard-activity-recall]"),
    activityFeynman: root.querySelector("[data-dashboard-activity-feynman]"),
    activityFlashcards: root.querySelector("[data-dashboard-activity-flashcards]"),
    activityStatusNode: document.getElementById("activityStatsStatus"),
    worklistPanel: root.querySelector("[data-dashboard-worklist-panel]"),
    worklistSummary: root.querySelector("[data-dashboard-worklist-summary]"),
    worklistList: root.querySelector("[data-dashboard-worklist-list]"),
    worklistSessionToggle: root.querySelector("[data-dashboard-worklist-session-toggle]"),
    worklistTrainingSuccess: root.querySelector("[data-dashboard-worklist-training-success]"),
    worklistRecallSuccess: root.querySelector("[data-dashboard-worklist-recall-success]"),
    worklistFeynmanSuccess: root.querySelector("[data-dashboard-worklist-feynman-success]"),
    worklistStatusNode: document.getElementById("worklistStatus"),
    activityMapSummary: root.querySelector("[data-dashboard-activity-map-summary]"),
    activityMapBoard: root.querySelector("[data-dashboard-activity-map-board]"),
    activityMapTooltip: root.querySelector("[data-dashboard-activity-map-tooltip]"),
    activityMapTarget: root.querySelector("[data-dashboard-activity-map-target]"),
    activityMapStatusNode: document.getElementById("activityMapStatus"),
    streakBadge: root.querySelector("[data-dashboard-streak-badge]"),
    streakCount: root.querySelector("[data-dashboard-streak-count]"),
    primaryFeedStatus: root.querySelector("[data-dashboard-primary-feed-status]"),
  };

  return {
    root,
    lernbereiche,
    systemSettings: getDefaultSystemSettings(),
    feedContentMeta: buildSharedFeedContentMeta(lernbereiche),
    checkMetaById: buildCheckMetaById(lernbereiche),
    lernbereichMetaById: buildLernbereichMetaById(lernbereiche),
    supabase: null,
    authState: null,
    activeSession: null,
    activityOverview: null,
    sessionCheckStates: [],
    sessionActivityStates: [],
    state: {},
    draft: {},
    draftConfig: { targetDate: "" },
    isGreetingHydrating: true,
    greetingRefreshTimerId: null,
    isSaving: false,
    retentionDraft: {},
    retentionPersistedDraft: {},
    retentionIsSaving: false,
    hasRetentionEntries: false,
    worklistSessionOnly: readWorklistSessionOnlyPreference(),
    elements,
  };
}

function initDashboardPanelHelp(root) {
  if (!root) return;

  const helpPanels = Array.from(root.querySelectorAll(".dashboard-panel__help"));
  if (!helpPanels.length) return;

  helpPanels.forEach((helpPanel) => {
    helpPanel.addEventListener("toggle", () => {
      if (!helpPanel.open) return;

      helpPanels.forEach((otherPanel) => {
        if (otherPanel !== helpPanel) {
          otherPanel.removeAttribute("open");
        }
      });
    });
  });

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Node)) return;

    helpPanels.forEach((helpPanel) => {
      if (helpPanel.open && !helpPanel.contains(target)) {
        helpPanel.removeAttribute("open");
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;

    const openHelpPanels = helpPanels.filter((helpPanel) => helpPanel.open);
    if (!openHelpPanels.length) return;

    event.preventDefault();
    openHelpPanels.forEach((helpPanel) => {
      helpPanel.removeAttribute("open");
    });
    openHelpPanels[0]?.querySelector("summary")?.focus();
  });
}

export async function initDashboardModule() {
  const root = document.querySelector("[data-dashboard-root]");
  if (!root) return;

  const materialUrl = root.dataset.dashboardMaterialUrl || "/material.html";
  const checksUrl = root.dataset.dashboardChecksUrl || "/checks.json";

  initProgressBars();
  initActionFeed(root, materialUrl);
  bindActionCardList(root.querySelector("[data-dashboard-session-list]"));
  bindActionCardList(root.querySelector("[data-dashboard-retention-list]"));
  initCardMenuDismiss(root);
  initDashboardPanelHelp(root);

  const gebiete = parseJsonScript("gebiete-dashboard-data", []);
  const lernbereicheSource = parseJsonScript("lernbereiche-dashboard-data", []);

  let checks = [];
  try {
    const response = await fetch(checksUrl, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`checks.json konnte nicht geladen werden (${response.status})`);
    }
    checks = await response.json();
  } catch (error) {
    console.error("Lernbereichsdaten konnten nicht geladen werden:", error);
  }

  const lernbereiche = buildLernbereicheFromData(checks, gebiete, lernbereicheSource);
  const context = createContext(root, lernbereiche);

  setGreetingDate();
  updateGreetingHeading(context);
  bindEvents(context);
  setupWorklistSessionToggle(context);
  updatePlanSummary(context);
  updateSessionList(context);
  updateRetentionSummary(context);
  renderDashboardPanelMessage(context.elements.retentionList, RETENTION_LOADING_MESSAGE);
  updateSessionActionButtons(context, true);
  updateRetentionActionButtons(context, true);
  setBarStatus(context, "");
  applyPrimaryFeedLoadingState(context);
  applyActivityOverview(context, null);
  applyActivityMap(context, null);

  const authState = await getCurrentAuthState();
  context.authState = authState;
  context.supabase = authState.configured ? await getSupabaseClient() : null;
  context.systemSettings = await loadSystemSettings(context.supabase);

  if (!authState.configured) {
    applyPrimaryFeedErrorState(context);
    updateRetentionSummary(context, [], RETENTION_UNAVAILABLE_MESSAGE);
    renderDashboardPanelMessage(context.elements.retentionList, RETENTION_UNAVAILABLE_MESSAGE);
    setStatusNode(context.elements.activityStatusNode, ACTIVITY_UNAVAILABLE_MESSAGE, "warning");
    setStatusNode(context.elements.activityMapStatusNode, ACTIVITY_UNAVAILABLE_MESSAGE, "warning");
    setBarStatus(context, "Der Session-Speicher ist noch nicht konfiguriert.");
    finalizeGreetingHydration(context);
    return;
  }

  if (authState.error) {
    applyPrimaryFeedErrorState(context);
    updateRetentionSummary(context, [], RETENTION_UNAVAILABLE_MESSAGE);
    renderDashboardPanelMessage(context.elements.retentionList, RETENTION_UNAVAILABLE_MESSAGE);
    setStatusNode(context.elements.activityStatusNode, ACTIVITY_UNAVAILABLE_MESSAGE, "error");
    setStatusNode(context.elements.activityMapStatusNode, ACTIVITY_UNAVAILABLE_MESSAGE, "error");
    setBarStatus(context, "Die Verbindung zur Session-Datenbank konnte nicht aufgebaut werden.", "error");
    finalizeGreetingHydration(context);
    return;
  }

  if (!authState.user) {
    context.isGreetingHydrating = false;
    redirectToAccount();
    return;
  }

  updateGreetingHeading(context);
  updateSessionActionButtons(context, false);
  updateRetentionActionButtons(context, false);

  try {
    const persisted = await loadPersistedState(context.supabase, lernbereiche);
    context.state = persisted.state;
    context.activeSession = persisted.session;
    context.sessionCheckStates = persisted.checkStates;
    context.sessionActivityStates = persisted.activityStates;
    updatePlanSummary(context);
    updateSessionList(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
      refreshActivityOverview(context),
    ]);
    updateSessionActionButtons(context, false);
    updateRetentionActionButtons(context, false);
    setBarStatus(context, "");
  } catch (error) {
    console.error("Aktive Session konnte nicht geladen werden:", error);
    applyPrimaryFeedErrorState(context);
    setBarStatus(context, "Die aktive Session konnte nicht geladen werden.", "error");
  } finally {
    finalizeGreetingHydration(context);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    void initDashboardModule();
  }, { once: true });
} else {
  void initDashboardModule();
}