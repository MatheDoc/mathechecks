import { initCardMenuDismiss } from "./ui/card-actions-menu.js";
import {
  FEED_STEP_ORDER,
  buildFeedContentMetaFromLernbereiche as buildSharedFeedContentMeta,
  loadFeedProjection,
  rememberManualRetentionPriority,
} from "../platform/feed-projection.js?v=20260604-manual-retention-head";
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
  if (!node || !user) return;
  node.textContent = formatAuthDisplayName(user);
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

function initActionFeed(root, materialUrl) {
  const listNode = root.querySelector("[data-dashboard-feed-list]");
  bindActionCardList(listNode, materialUrl);
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

function capturePrimaryFeedDefaults(elements) {
  return {
    cardType: elements.primaryFeedCard?.dataset?.type || "training",
    cardHref: elements.primaryFeedCard?.dataset?.actionHref || "",
    title: elements.primaryFeedTitle?.innerHTML || "",
    desc: elements.primaryFeedDesc?.innerHTML || "",
    descHidden: Boolean(elements.primaryFeedDesc?.hidden),
    badges: elements.primaryFeedBadges?.innerHTML || "",
    buttonLabel: elements.primaryFeedButton?.textContent || "",
    buttonHref: elements.primaryFeedButton?.dataset?.actionHref || "",
  };
}

function clearSecondaryFeedCards(context) {
  context.elements.feedList?.querySelectorAll("[data-dashboard-secondary-feed-card]").forEach((node) => {
    node.remove();
  });
}

function restorePrimaryFeedCard(context) {
  const { elements, primaryFeedDefaults } = context;
  if (!elements.primaryFeedCard || !primaryFeedDefaults) return;

  elements.primaryFeedCard.dataset.type = primaryFeedDefaults.cardType;
  elements.primaryFeedCard.dataset.actionHref = primaryFeedDefaults.cardHref;
  if (elements.primaryFeedTitle) elements.primaryFeedTitle.innerHTML = primaryFeedDefaults.title;
  if (elements.primaryFeedDesc) {
    elements.primaryFeedDesc.innerHTML = primaryFeedDefaults.desc;
    elements.primaryFeedDesc.hidden = Boolean(primaryFeedDefaults.descHidden);
  }
  if (elements.primaryFeedBadges) elements.primaryFeedBadges.innerHTML = primaryFeedDefaults.badges;
  if (elements.primaryFeedButton) {
    elements.primaryFeedButton.textContent = primaryFeedDefaults.buttonLabel;
    elements.primaryFeedButton.dataset.actionHref = primaryFeedDefaults.buttonHref;
  }

  clearSecondaryFeedCards(context);
}

function applyPrimaryFeedMessage(context, {
  title = "Feed",
  description = "",
  badgeLabel = "Feed",
} = {}) {
  const { elements } = context;
  if (!elements.primaryFeedCard) return;

  elements.primaryFeedCard.dataset.type = "feed";
  elements.primaryFeedCard.dataset.actionHref = "";

  if (elements.primaryFeedTitle) {
    elements.primaryFeedTitle.textContent = title;
  }
  if (elements.primaryFeedDesc) {
    elements.primaryFeedDesc.textContent = description;
    elements.primaryFeedDesc.hidden = !description;
  }
  if (elements.primaryFeedBadges) {
    elements.primaryFeedBadges.innerHTML = createBadgeMarkup(badgeLabel);
  }

  clearSecondaryFeedCards(context);
}

function applyPrimaryFeedLoadingState(context) {
  applyPrimaryFeedMessage(context, {
    title: "Feed wird geladen",
    description: "Deine nächsten Aktivitäten werden vorbereitet.",
    badgeLabel: "Feed",
  });
}

function applyPrimaryFeedEmptyState(context) {
  applyPrimaryFeedMessage(context, {
    title: "Gerade keine Empfehlung",
    description: "Sobald eine Session oder eine fällige Wiederholung ansteht, erscheint hier der nächste sinnvolle Schritt.",
    badgeLabel: "Feed",
  });
}

function applyPrimaryFeedWaitingState(context, waiting = null) {
  const nextLabel = formatDateTimeLabel(waiting?.nextAvailableFrom);

  applyPrimaryFeedMessage(context, {
    title: "Nächster Schritt später",
    description: nextLabel
      ? `Der nächste geplante Feed-Schritt wird ab ${nextLabel} freigeschaltet.`
      : "Im Moment ist kein Schritt geplant, den du sofort aus dem Feed öffnen solltest.",
    badgeLabel: "Feed",
  });
}

function applyPrimaryFeedErrorState(context) {
  applyPrimaryFeedMessage(context, {
    title: "Feed gerade nicht verfügbar",
    description: "Der nächste sinnvolle Schritt konnte gerade nicht geladen werden.",
    badgeLabel: "Feed",
  });
}

function buildLernbereichStartHref(lernbereichMeta) {
  if (!lernbereichMeta?.gebietKey || !lernbereichMeta?.lernbereichId) return "";
  return `/lernbereiche/${encodeURIComponent(lernbereichMeta.gebietKey)}/${encodeURIComponent(lernbereichMeta.lernbereichId)}/start.html`;
}

function buildProjectionTitleMarkup(item) {
  if (item?.checkIndexLabel && item?.checkKeyword) {
    return [
      `<span class="dashboard-feed__check-index">${escapeHtml(item.checkIndexLabel)}</span>`,
      `<span class="dashboard-feed__check-keyword">${escapeHtml(item.checkKeyword)}</span>`,
    ].join("");
  }

  return escapeHtml(item?.titleText || "");
}

function buildProjectionBadgesMarkup(item) {
  return (Array.isArray(item?.badges) ? item.badges : [])
    .map((badge) => createBadgeMarkup(badge?.label || "", badge?.type || ""))
    .join("");
}

function createFeedCardData({ type, href, titleHtml, descText, badges }) {
  return {
    type,
    href,
    titleHtml,
    descText,
    badges,
  };
}

function buildFeedCardDataFromProjection(item) {
  if (!item?.href) return null;

  return createFeedCardData({
    type: item.type,
    href: item.href,
    titleHtml: buildProjectionTitleMarkup(item),
    descText: item.descText,
    badges: buildProjectionBadgesMarkup(item),
  });
}

function renderSecondaryFeedCards(context, items) {
  clearSecondaryFeedCards(context);
  if (!context.elements.feedList || !context.elements.primaryFeedCard || !Array.isArray(items) || !items.length) return;

  const markup = items.map((item) => `
    <li class="action-card" data-type="${escapeHtml(item.type)}" data-action-href="${escapeHtml(item.href)}" data-dashboard-secondary-feed-card>
      <div class="action-body">
        <div class="action-title">${item.titleHtml}</div>
        ${item.descText ? `<div class="action-desc">${escapeHtml(item.descText)}</div>` : ""}
        <div class="action-badges">${item.badges}</div>
      </div>
    </li>
  `).join("");

  context.elements.primaryFeedCard.insertAdjacentHTML("afterend", markup);
}

function applyPrimaryFeedCardData(context, item) {
  const { elements } = context;
  if (!item || !elements.primaryFeedCard) {
    restorePrimaryFeedCard(context);
    return;
  }

  elements.primaryFeedCard.dataset.type = item.type;
  elements.primaryFeedCard.dataset.actionHref = item.href;

  if (elements.primaryFeedTitle) {
    elements.primaryFeedTitle.innerHTML = item.titleHtml;
  }
  if (elements.primaryFeedDesc) {
    elements.primaryFeedDesc.textContent = item.descText;
    elements.primaryFeedDesc.hidden = !item.descText;
  }
  if (elements.primaryFeedBadges) {
    elements.primaryFeedBadges.innerHTML = item.badges;
  }
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

async function loadRetentionCompletedLernbereiche(context) {
  if (!context.supabase) return [];

  const [{ data: scopeRows, error: scopeError }, { data: exclusionRows, error: exclusionError }] = await Promise.all([
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
  const [activeEntries, retentionEntries] = await Promise.all([
    loadActiveSessionCompletedLernbereiche(context),
    loadRetentionCompletedLernbereiche(context),
  ]);

  const latestByLernbereichId = new Map();
  [...activeEntries, ...retentionEntries].forEach((entry) => {
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
  const selectedCount = Math.max(0, Number(entry?.checkCount) || 0);
  const totalCheckCount = Math.max(selectedCount, Number(entry?.totalCheckCount) || selectedCount || 0);
  const normalizedTotalCount = Math.max(totalCheckCount, selectedCount, 1);
  const progressLabel = `${selectedCount}/${normalizedTotalCount}`;
  const linkAttributes = href
    ? ` data-action-href="${escapeHtml(href)}" role="link" tabindex="0"`
    : "";
  const badgeMarkup = entry?.groupName
    ? `<div class="action-badges">${createBadgeMarkup(entry.groupName)}</div>`
    : "";

  return `
    <li class="action-card dashboard-panel__action-card" data-type="dashboard"${linkAttributes}>
      <div class="action-body">
        <div class="action-title">
          <span class="dashboard-panel__action-name">${escapeHtml(entry.lernbereichName)}</span>
          <span class="dashboard-panel__action-progress">${escapeHtml(progressLabel)}</span>
        </div>
        ${badgeMarkup}
      </div>
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
      clearSecondaryFeedCards(context);
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

  context.lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const lbState = context.state[lb.id];
      if (!lbState?.active) return;

      lernbereichCount += 1;
      lb.checks.forEach((check) => {
        if (!isCheckSelected(lbState, check.id)) return;
        checkCount += 1;
        selectedCheckIds.push(check.id);
      });
    });
  });

  return { lernbereichCount, checkCount, selectedCheckIds };
}

function collectActiveSessionLernbereiche(context) {
  const entries = [];

  context.lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const lbState = context.state[lb.id];
      if (!lbState?.active) return;

      entries.push({
        lernbereichId: lb.id,
        lernbereichName: lb.name,
        gebietKey: lb.gebietKey,
        groupName: group.group,
        checkCount: countSelectedChecks(lb, lbState),
        totalCheckCount: Array.isArray(lb.checks) ? lb.checks.length : 0,
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

  const suggestion = buildSuggestedTargetDate(context, selectedCheckIds);
  basePayload.p_target_date = suggestion.suggestedDateValue || null;
  basePayload.p_target_source = suggestion.suggestedDateValue ? "suggested" : null;
  return basePayload;
}

function buildSessionCheckStateById(context) {
  return new Map(
    (Array.isArray(context.sessionCheckStates) ? context.sessionCheckStates : []).map((row) => [String(row?.check_id || "").trim(), row]),
  );
}

function getRemainingSelectedActivityCount(context, selectedCheckIds) {
  const checkStateById = buildSessionCheckStateById(context);
  return selectedCheckIds.reduce((sum, checkId) => {
    return sum + getRemainingCheckStepCount(checkStateById.get(checkId));
  }, 0);
}

function getConfiguredPositiveNumber(value) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function buildSuggestedTargetDate(context, selectedCheckIds) {
  const remainingSteps = getRemainingSelectedActivityCount(context, selectedCheckIds);
  const activitiesPerDay = getConfiguredPositiveNumber(context.systemSettings?.planningDefaultActivitiesPerDay);
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

  const suggestedDate = workloadDate.getTime() >= earliestCompletionDate.getTime()
    ? workloadDate
    : earliestCompletionDate;

  return {
    suggestedDateValue: toDateOnlyValue(suggestedDate),
    remainingSteps,
    activitiesPerDay,
    didacticGapHours,
  };
}

function buildTargetDateAssessment(context, selectedCheckIds) {
  const defaultActivitiesPerDay = getConfiguredPositiveNumber(context.systemSettings?.planningDefaultActivitiesPerDay);
  const realisticThreshold = defaultActivitiesPerDay;
  const warningThreshold = defaultActivitiesPerDay === null
    ? null
    : Math.max(realisticThreshold + 1, realisticThreshold * 2);
  const targetDateValue = normalizeDateOnlyValue(context.activeSession?.target_date);
  if (!targetDateValue) {
    const suggestion = buildSuggestedTargetDate(context, selectedCheckIds);
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
  const availableDays = dayDelta + 1;

  const remainingSteps = getRemainingSelectedActivityCount(context, selectedCheckIds);

  if (dayDelta < 0) {
    return {
      targetLabel,
      assessmentLabel: "Überfällig",
      assessmentTone: "error",
    };
  }

  if (remainingSteps <= 0) {
    return {
      targetLabel,
      assessmentLabel: "Fertig",
      assessmentTone: "success",
    };
  }

  if (defaultActivitiesPerDay === null || warningThreshold === null) {
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
    if (targetNode) {
      targetNode.hidden = true;
    }
    if (targetLabelNode) {
      targetLabelNode.textContent = "";
    }
    if (assessmentNode) {
      setStatusNode(assessmentNode, "");
    }
    return;
  }

  const { selectedCheckIds } = summarizeActivePlan(context);
  node.textContent = buildActiveLernbereichSummary(activeEntries, SESSION_EMPTY_SUMMARY);

  if (targetNode) {
    const assessment = buildTargetDateAssessment(context, selectedCheckIds);
    targetNode.hidden = false;
    if (targetLabelNode) {
      targetLabelNode.textContent = assessment.targetLabel;
    }
    if (assessmentNode) {
      setStatusNode(assessmentNode, assessment.assessmentLabel, assessment.assessmentTone);
    }
  }
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
    return { state: {}, session: null, checkStates: [] };
  }

  const [{ data: lernbereicheRows, error: lernbereicheError }, { data: exclusionRows, error: exclusionError }, { data: checkStateRows, error: checkStateError }] = await Promise.all([
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
      .select("check_id, current_step_key, current_step_status")
      .eq("session_id", activeSession.id),
  ]);

  if (lernbereicheError) throw lernbereicheError;
  if (exclusionError) throw exclusionError;
  if (checkStateError) throw checkStateError;

  return {
    state: buildStateFromPersisted(lernbereiche, lernbereicheRows, exclusionRows),
    session: activeSession,
    checkStates: Array.isArray(checkStateRows) ? checkStateRows : [],
  };
}

function updateSessionList(context) {
  renderDashboardLernbereichList(
    context.elements.sessionList,
    collectActiveSessionLernbereiche(context),
    SESSION_EMPTY_LIST_MESSAGE,
  );
}

function updateSessionActionButtons(context, disabled) {
  context.elements.openButton.disabled = disabled;
  context.elements.deleteButton.disabled = disabled || !context.activeSession;
}

function updateRetentionActionButtons(context, disabled) {
  context.elements.retentionManageButton.disabled = disabled;
  context.elements.retentionDeleteButton.disabled = disabled || !context.hasRetentionEntries;
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
    updatePlanSummary(context);
    updateSessionList(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
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
    updatePlanSummary(context);
    updateSessionList(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
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
    openButton: document.getElementById("lbOpenBtn"),
    deleteButton: document.getElementById("lbDeleteBtn"),
    closeButton: document.getElementById("lbCloseBtn"),
    saveButton: document.getElementById("lbSaveBtn"),
    resetButton: document.getElementById("lbResetBtn"),
    overlay: document.getElementById("lbOverlay"),
    sessionList: root.querySelector("[data-dashboard-session-list]"),
    planSummary: root.querySelector("[data-dashboard-plan-summary]"),
    planTarget: root.querySelector("[data-dashboard-plan-target]"),
    planTargetLabel: root.querySelector("[data-dashboard-plan-target-label]"),
    planAssessment: root.querySelector("[data-dashboard-plan-assessment]"),
    feedList: root.querySelector("[data-dashboard-feed-list]"),
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
    primaryFeedCard: root.querySelector("[data-dashboard-primary-feed-card]"),
    primaryFeedTitle: root.querySelector("[data-dashboard-primary-feed-title]"),
    primaryFeedDesc: root.querySelector("[data-dashboard-primary-feed-desc]"),
    primaryFeedBadges: root.querySelector("[data-dashboard-primary-feed-badges]"),
    primaryFeedButton: root.querySelector("[data-dashboard-primary-feed-button]"),
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
    sessionCheckStates: [],
    state: {},
    draft: {},
    draftConfig: { targetDate: "" },
    isSaving: false,
    retentionDraft: {},
    retentionPersistedDraft: {},
    retentionIsSaving: false,
    hasRetentionEntries: false,
    elements,
    primaryFeedDefaults: capturePrimaryFeedDefaults(elements),
  };
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
  bindEvents(context);
  updatePlanSummary(context);
  updateSessionList(context);
  updateRetentionSummary(context);
  renderDashboardPanelMessage(context.elements.retentionList, RETENTION_LOADING_MESSAGE);
  updateSessionActionButtons(context, true);
  updateRetentionActionButtons(context, true);
  setBarStatus(context, "");
  applyPrimaryFeedLoadingState(context);

  const authState = await getCurrentAuthState();
  context.authState = authState;
  context.supabase = authState.configured ? await getSupabaseClient() : null;
  context.systemSettings = await loadSystemSettings(context.supabase);

  if (!authState.configured) {
    applyPrimaryFeedErrorState(context);
    updateRetentionSummary(context, [], RETENTION_UNAVAILABLE_MESSAGE);
    renderDashboardPanelMessage(context.elements.retentionList, RETENTION_UNAVAILABLE_MESSAGE);
    setBarStatus(context, "Der Session-Speicher ist noch nicht konfiguriert.");
    return;
  }

  if (authState.error) {
    applyPrimaryFeedErrorState(context);
    updateRetentionSummary(context, [], RETENTION_UNAVAILABLE_MESSAGE);
    renderDashboardPanelMessage(context.elements.retentionList, RETENTION_UNAVAILABLE_MESSAGE);
    setBarStatus(context, "Die Verbindung zur Session-Datenbank konnte nicht aufgebaut werden.", "error");
    return;
  }

  if (!authState.user) {
    redirectToAccount();
    return;
  }

  setGreetingName(authState.user);
  updateSessionActionButtons(context, false);
  updateRetentionActionButtons(context, false);

  try {
    const persisted = await loadPersistedState(context.supabase, lernbereiche);
    context.state = persisted.state;
    context.activeSession = persisted.session;
    context.sessionCheckStates = persisted.checkStates;
    updatePlanSummary(context);
    updateSessionList(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
    ]);
    updateSessionActionButtons(context, false);
    updateRetentionActionButtons(context, false);
    setBarStatus(context, "");
  } catch (error) {
    console.error("Aktive Session konnte nicht geladen werden:", error);
    applyPrimaryFeedErrorState(context);
    setBarStatus(context, "Die aktive Session konnte nicht geladen werden.", "error");
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    void initDashboardModule();
  }, { once: true });
} else {
  void initDashboardModule();
}