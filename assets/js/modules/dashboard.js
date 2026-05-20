import { initCardMenuDismiss } from "./ui/card-actions-menu.js";
import { FEED_STEP_ORDER, buildFeedContentMetaFromLernbereiche as buildSharedFeedContentMeta, loadFeedProjection } from "../platform/feed-projection.js?v=20260520-start-feed";
import { getDefaultSystemSettings, loadSystemSettings } from "../platform/system-settings.js?v=20260520-hybrid-retention";
import { buildAccountUrl, formatAuthDisplayName, getCurrentAuthState, getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js?v=20260520-feed-loading";

const LERNBEREICH_ALIASES = {
  "differentialrechnung-ganzrationaler-funktionen": ["differentialrechnung"],
  "zufallsexperimente-und-wahrscheinlichkeiten": ["zufallsexperimente"],
};

const CHECK_PIPELINE_STEP_COUNT = Object.keys(FEED_STEP_ORDER).length;
const DATE_ONLY_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;

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
  if (tone === "error") node.classList.add("is-error");
}

function buildGebietMeta(gebiete) {
  return Object.fromEntries(
    (Array.isArray(gebiete) ? gebiete : []).map((gebiet) => [gebiet.key, {
      group: gebiet.name,
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
      color: meta.color,
      checks: Array.from(checksById.values()),
    });
  });

  return Array.from(grouped.values());
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

function initActionFeed(root, materialUrl) {
  const listNode = root.querySelector("[data-dashboard-feed-list]");
  if (!listNode || listNode.dataset.dashboardFeedBound === "true") return;

  listNode.dataset.dashboardFeedBound = "true";
  listNode.addEventListener("click", (event) => {
    if (event.target.closest("button, a")) return;

    const card = event.target.closest(".action-card");
    if (!card || !listNode.contains(card)) return;

    window.location.href = card.dataset.actionHref || materialUrl;
  });
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

function capturePrimaryFeedDefaults(elements) {
  return {
    cardType: elements.primaryFeedCard?.dataset?.type || "training",
    cardHref: elements.primaryFeedCard?.dataset?.actionHref || "",
    title: elements.primaryFeedTitle?.innerHTML || "",
    desc: elements.primaryFeedDesc?.innerHTML || "",
    badges: elements.primaryFeedBadges?.innerHTML || "",
    icon: elements.primaryFeedIcon?.textContent || "",
    iconStyle: elements.primaryFeedIcon?.getAttribute("style") || "",
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
  if (elements.primaryFeedDesc) elements.primaryFeedDesc.innerHTML = primaryFeedDefaults.desc;
  if (elements.primaryFeedBadges) elements.primaryFeedBadges.innerHTML = primaryFeedDefaults.badges;
  if (elements.primaryFeedIcon) {
    elements.primaryFeedIcon.textContent = primaryFeedDefaults.icon;
    elements.primaryFeedIcon.setAttribute("style", primaryFeedDefaults.iconStyle);
  }
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
  icon = "→",
  iconStyle = "background:linear-gradient(135deg, var(--accent), var(--teal));color:#fff;",
} = {}) {
  const { elements } = context;
  if (!elements.primaryFeedCard) return;

  elements.primaryFeedCard.dataset.type = "feed";
  elements.primaryFeedCard.dataset.actionHref = "";

  if (elements.primaryFeedIcon) {
    elements.primaryFeedIcon.textContent = icon;
    elements.primaryFeedIcon.setAttribute("style", iconStyle);
  }
  if (elements.primaryFeedTitle) {
    elements.primaryFeedTitle.textContent = title;
  }
  if (elements.primaryFeedDesc) {
    elements.primaryFeedDesc.textContent = description;
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
    icon: "…",
  });
}

function applyPrimaryFeedEmptyState(context) {
  applyPrimaryFeedMessage(context, {
    title: "Gerade keine Empfehlung",
    description: "Sobald eine Session oder eine fällige Wiederholung ansteht, erscheint hier der nächste sinnvolle Schritt.",
    badgeLabel: "Feed",
  });
}

function applyPrimaryFeedErrorState(context) {
  applyPrimaryFeedMessage(context, {
    title: "Feed gerade nicht verfügbar",
    description: "Der nächste sinnvolle Schritt konnte gerade nicht geladen werden.",
    badgeLabel: "Feed",
    icon: "!",
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

function createFeedCardData({ type, href, icon, iconStyle, titleHtml, descText, badges }) {
  return {
    type,
    href,
    icon,
    iconStyle,
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
    icon: item.icon,
    iconStyle: item.iconStyle,
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
      <div class="action-icon" style="${escapeHtml(item.iconStyle)}">${escapeHtml(item.icon)}</div>
      <div class="action-body">
        <div class="action-title">${item.titleHtml}</div>
        <div class="action-desc">${escapeHtml(item.descText)}</div>
        <div class="action-badges">${item.badges}</div>
      </div>
      <div class="action-arrow" aria-hidden="true">→</div>
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

  if (elements.primaryFeedIcon) {
    elements.primaryFeedIcon.textContent = item.icon;
    elements.primaryFeedIcon.setAttribute("style", item.iconStyle);
  }
  if (elements.primaryFeedTitle) {
    elements.primaryFeedTitle.innerHTML = item.titleHtml;
  }
  if (elements.primaryFeedDesc) {
    elements.primaryFeedDesc.textContent = item.descText;
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
        lastCompletedAt: completionDates[0] || "",
      });
    });
  });

  return completedLernbereiche;
}

async function loadRetentionCompletedLernbereiche(context) {
  if (!context.supabase) return [];

  const { data: scopeRows, error: scopeError } = await context.supabase
    .from("user_retention_scopes")
    .select("lernbereich_slug, source_session_id, updated_at")
    .eq("activity_type", "flashcards")
    .eq("scope_type", "lernbereich")
    .not("source_session_id", "is", null);

  if (scopeError) throw scopeError;

  const scopes = (Array.isArray(scopeRows) ? scopeRows : []).filter((row) => {
    return String(row?.lernbereich_slug || "").trim() && String(row?.source_session_id || "").trim();
  });
  if (!scopes.length) return [];

  const sessionIds = [...new Set(scopes.map((row) => String(row.source_session_id).trim()).filter(Boolean))];
  const [{ data: sessions, error: sessionsError }, { data: states, error: statesError }] = await Promise.all([
    context.supabase
      .from("learning_sessions")
      .select("id, ended_at")
      .in("id", sessionIds),
    context.supabase
      .from("session_check_state")
      .select("session_id, check_id, current_step_status, last_completed_at")
      .in("session_id", sessionIds)
      .eq("current_step_status", "completed"),
  ]);

  if (sessionsError) throw sessionsError;
  if (statesError) throw statesError;

  const sessionById = new Map(
    (Array.isArray(sessions) ? sessions : []).map((session) => [String(session?.id || "").trim(), session]),
  );
  const completedRowsBySessionId = new Map();

  (Array.isArray(states) ? states : []).forEach((row) => {
    const sessionId = String(row?.session_id || "").trim();
    if (!sessionId) return;
    if (!completedRowsBySessionId.has(sessionId)) {
      completedRowsBySessionId.set(sessionId, []);
    }
    completedRowsBySessionId.get(sessionId).push(row);
  });

  return scopes.map((scope) => {
    const lernbereichId = String(scope?.lernbereich_slug || "").trim();
    const sessionId = String(scope?.source_session_id || "").trim();
    const lernbereichMeta = context.lernbereichMetaById.get(lernbereichId);
    if (!lernbereichMeta || !sessionId) return null;

    const matchingRows = (completedRowsBySessionId.get(sessionId) || []).filter((row) => {
      const checkMeta = context.checkMetaById.get(row?.check_id);
      return checkMeta?.lernbereichId === lernbereichId;
    });
    if (!matchingRows.length) return null;

    const completionDates = matchingRows
      .map((row) => String(row?.last_completed_at || ""))
      .filter(Boolean)
      .sort((left, right) => right.localeCompare(left));
    const session = sessionById.get(sessionId);

    return {
      lernbereichId,
      lernbereichName: lernbereichMeta.lernbereichName,
      gebietKey: lernbereichMeta.gebietKey,
      groupName: lernbereichMeta.groupName,
      checkCount: matchingRows.length,
      lastCompletedAt: completionDates[0] || String(session?.ended_at || scope?.updated_at || ""),
    };
  }).filter(Boolean);
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

  return sortCompletedLernbereiche(latestByLernbereichId.values());
}

function renderCompletedLernbereichCard(entry) {
  const checkLabel = entry.checkCount === 1 ? "Check" : "Checks";
  const href = buildLernbereichStartHref(entry);
  const linkMarkup = href
    ? `<a class="dashboard-completed-card__link" href="${escapeHtml(href)}">Lernbereich öffnen</a>`
    : "";

  return `
    <article class="dashboard-completed-card">
      <div class="dashboard-completed-card__top">
        <div class="dashboard-completed-card__title-wrap">
          <div class="dashboard-completed-card__title">${escapeHtml(entry.lernbereichName)}</div>
          <div class="dashboard-completed-card__meta">${escapeHtml(entry.groupName)}</div>
        </div>
        <div class="dashboard-completed-card__badges">
          ${createBadgeMarkup("Abgeschlossen", "kompetenzliste")}
          ${createBadgeMarkup(`${entry.checkCount} ${checkLabel}`)}
        </div>
      </div>
      <p class="dashboard-completed-card__desc">Alle ausgewählten Checks dieses Lernbereichs wurden im letzten Kompetenzlisten-Schritt bestätigt.</p>
      ${linkMarkup}
    </article>
  `;
}

async function refreshCompletedPanel(context) {
  const listNode = context.elements.completedList;
  if (!listNode) return;

  if (!context.supabase) {
    listNode.innerHTML = '<p class="dashboard-completed__empty">Abgeschlossene Lernbereiche konnten gerade nicht geladen werden.</p>';
    return;
  }

  try {
    const completedLernbereiche = await loadCompletedLernbereiche(context);
    if (!completedLernbereiche.length) {
      listNode.innerHTML = '<p class="dashboard-completed__empty">Bisher wurde noch kein Lernbereich vollständig abgeschlossen.</p>';
      return;
    }

    listNode.innerHTML = completedLernbereiche.map((entry) => renderCompletedLernbereichCard(entry)).join("");
  } catch (error) {
    console.error("Abgeschlossene Lernbereiche konnten nicht geladen werden:", error);
    listNode.innerHTML = '<p class="dashboard-completed__empty">Der Abschlussstand der Session konnte gerade nicht geladen werden.</p>';
  }
}

async function refreshPrimaryFeedCard(context) {
  if (!context.supabase) {
    applyPrimaryFeedEmptyState(context);
    return;
  }

  try {
    const feedItemLimit = Math.max(1, Number.parseInt(context.systemSettings?.feedDashboardItemLimit, 10) || 5);
    const projection = await loadFeedProjection({
      supabase: context.supabase,
      contentMeta: context.feedContentMeta,
      limit: feedItemLimit,
    });
    const feedItems = (Array.isArray(projection?.items) ? projection.items : [])
      .map((item) => buildFeedCardDataFromProjection(item))
      .filter(Boolean);

    if (feedItems.length) {
      applyPrimaryFeedCardData(context, feedItems[0]);
      renderSecondaryFeedCards(context, feedItems.slice(1));
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

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      const lbState = draft[lb.id];
      if (!lbState?.active) return;

      activeLernbereiche.push(lb.id);
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
    p_tempo_days: null,
    p_included_check_ids: Array.from(includedChecks),
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

function buildPayloadFromState(draft, lernbereiche, draftConfig) {
  const basePayload = {
    ...buildSessionPayloadBase(draft, lernbereiche),
  };

  const targetDate = normalizeDateOnlyValue(draftConfig?.targetDate);
  basePayload.p_target_date = targetDate || null;
  basePayload.p_target_source = targetDate ? "explicit" : null;
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

function buildSuggestedTargetDate(context, selectedCheckIds) {
  const remainingSteps = getRemainingSelectedActivityCount(context, selectedCheckIds);
  const defaultTempoDays = Math.max(1, Number.parseInt(context.systemSettings?.planningDefaultSessionTempoDays, 10) || 1);
  const tempoDays = Math.max(1, Number.parseInt(context.activeSession?.tempo_days, 10) || defaultTempoDays);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const suggestedDate = addCalendarDays(today, remainingSteps > 0 ? (remainingSteps - 1) * tempoDays : 0);

  return {
    suggestedDateValue: toDateOnlyValue(suggestedDate),
    remainingSteps,
    tempoDays,
  };
}

function buildTargetDateAssessment(context, selectedCheckIds) {
  const targetDateValue = normalizeDateOnlyValue(context.activeSession?.target_date);
  if (!targetDateValue) {
    const suggestion = buildSuggestedTargetDate(context, selectedCheckIds);
    const targetLabel = suggestion.suggestedDateValue
      ? `Zieldatum: ${formatDateOnlyLabel(suggestion.suggestedDateValue)} (Vorschlag)`
      : "Zieldatum: nicht gesetzt.";

    if (suggestion.remainingSteps <= 0) {
      return {
        targetLabel,
        assessmentMessage: "Kein Zieldatum gesetzt. Die aktuellen Aktivitäten sind bereits vollständig abgeschlossen.",
        assessmentTone: "success",
      };
    }

    const paceHint = suggestion.tempoDays === 1
      ? "etwa einer offenen Aktivität pro Tag"
      : `etwa einer offenen Aktivität alle ${suggestion.tempoDays} Tage`;

    return {
      targetLabel,
      assessmentMessage: `Kein Zieldatum gesetzt. Vorschlag auf Basis von ${paceHint}.`,
      assessmentTone: "neutral",
    };
  }

  const targetDate = parseDateOnlyValue(targetDateValue);
  const targetLabel = `Zieldatum: ${formatDateOnlyLabel(targetDateValue)}`;
  if (!targetDate) {
    return {
      targetLabel,
      assessmentMessage: "Das gespeicherte Zieldatum konnte nicht gelesen werden.",
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
      assessmentMessage: "Das Zieldatum liegt bereits in der Vergangenheit.",
      assessmentTone: "error",
    };
  }

  if (remainingSteps <= 0) {
    return {
      targetLabel,
      assessmentMessage: "Die aktuellen Aktivitäten sind bereits vollständig abgeschlossen.",
      assessmentTone: "success",
    };
  }

  const stepsPerDay = remainingSteps / availableDays;
  const dayLabel = availableDays === 1 ? "Kalendertag" : "Kalendertage";
  const stepLabel = remainingSteps === 1 ? "offene Aktivität" : "offene Aktivitäten";
  const workloadText = `Noch ${remainingSteps} ${stepLabel} in ${availableDays} ${dayLabel}, also rund ${formatPlanningRate(stepsPerDay)} pro Tag.`;

  if (stepsPerDay <= 1) {
    return {
      targetLabel,
      assessmentMessage: `Rechnerisch wirkt das Zieldatum realistisch. ${workloadText}`,
      assessmentTone: "success",
    };
  }

  if (stepsPerDay <= 2) {
    return {
      targetLabel,
      assessmentMessage: `Das Zieldatum ist sportlich, aber noch plausibel. ${workloadText}`,
      assessmentTone: "neutral",
    };
  }

  return {
    targetLabel,
    assessmentMessage: `Das Zieldatum wirkt aktuell eher unrealistisch. ${workloadText}`,
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
  const assessmentNode = context.elements.planAssessment;

  if (!context.activeSession) {
    node.textContent = "Aktuell ist keine Session aktiv. Im Feed können dann nur fällige Wiederholungen aus früheren Sessions auftauchen.";
    if (targetNode) {
      targetNode.hidden = true;
      targetNode.textContent = "";
    }
    if (assessmentNode) {
      setStatusNode(assessmentNode, "");
    }
    return;
  }

  const { lernbereichCount, checkCount, selectedCheckIds } = summarizeActivePlan(context);
  const lernbereichLabel = lernbereichCount === 1 ? "Lernbereich" : "Lernbereiche";
  const checkLabel = checkCount === 1 ? "Check" : "Checks";
  node.textContent = `${lernbereichCount} ${lernbereichLabel} mit ${checkCount} ${checkLabel} sind aktuell in der Session aktiv.`;

  if (targetNode) {
    const assessment = buildTargetDateAssessment(context, selectedCheckIds);
    targetNode.hidden = false;
    targetNode.textContent = assessment.targetLabel;
    if (assessmentNode) {
      setStatusNode(assessmentNode, assessment.assessmentMessage, assessment.assessmentTone);
    }
  }
}

async function loadPersistedState(supabase, lernbereiche) {
  const { data: sessions, error: sessionError } = await supabase
    .from("learning_sessions")
    .select("id, tempo_days, started_at, target_date, target_source")
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

function updateChipSummary(context) {
  const { chipsBox } = context.elements;
  if (!chipsBox) return;

  const activeItems = [];

  context.lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      if (context.state[lb.id]?.active) {
        activeItems.push(lb);
      }
    });
  });

  if (!activeItems.length) {
    chipsBox.hidden = true;
    chipsBox.setAttribute("aria-hidden", "true");
    chipsBox.innerHTML = '<span class="lb-chip-empty">Noch keine Lernbereiche gewählt - klicke auf Bearbeiten.</span>';
    return;
  }

  chipsBox.hidden = false;
  chipsBox.setAttribute("aria-hidden", "false");
  chipsBox.innerHTML = "";
  activeItems.forEach((lb) => {
    const lbState = context.state[lb.id];
    const total = lb.checks.length;
    const selected = countSelectedChecks(lb, lbState);
    const chip = document.createElement("span");
    chip.className = "lb-chip";
    chip.innerHTML = `<span class="lb-chip-dot" style="background:${escapeHtml(lb.color)}"></span>${escapeHtml(lb.name)} <span style="opacity:.5;font-size:0.72em;">${selected}/${total}</span>`;
    context.elements.chipsBox.appendChild(chip);
  });
}

function updateSessionActionButtons(context, disabled) {
  context.elements.openButton.disabled = disabled;
  context.elements.deleteButton.disabled = disabled || !context.activeSession;
}

function setBarStatus(context, message, tone = "neutral") {
  setStatusNode(context.elements.statusNode, message, tone);
}

function setModalStatus(context, message, tone = "neutral") {
  setStatusNode(context.elements.modalStatusNode, message, tone);
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
  if (message.includes("tempo_days must be positive")) {
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
     return "Die Löschfunktion für die Session ist noch nicht im API-Schema verfügbar. Seite neu laden und erneut versuchen.";
  }
  if (message.includes("Authentication required")) {
     return "Bitte melde dich zuerst an, um deine Session zu löschen.";
  }

    return "Die aktive Session konnte nicht gelöscht werden.";
}

async function handleSave(context) {
  if (context.isSaving) return;
  if (!context.supabase || !context.authState?.user) {
    setModalStatus(context, "Bitte melde dich zuerst an, um deine Session zu speichern.", "error");
    setBarStatus(context, "Bitte melde dich zuerst an, um deine Session zu speichern.", "error");
    return;
  }

  const payload = buildPayloadFromState(context.draft, context.lernbereiche, context.draftConfig);

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
    updateChipSummary(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
    ]);
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

  const confirmed = window.confirm("Aktive Session und die dazugehörigen sessionbezogenen Schritte wirklich löschen?");
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
    updateChipSummary(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
    ]);
    closeModal(context);
    setBarStatus(context, "");
  } catch (error) {
    console.error("Aktive Session konnte nicht gelöscht werden:", error);
    setBarStatus(context, mapDeleteSessionError(error), "error");
  } finally {
    setMutationBusy(context, false);
  }
}

function bindEvents(context) {
  context.elements.openButton.addEventListener("click", () => {
    openModal(context);
  });

  context.elements.deleteButton.addEventListener("click", () => {
    void handleDelete(context);
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
}

function createContext(root, lernbereiche) {
  const elements = {
    openButton: document.getElementById("lbOpenBtn"),
    deleteButton: document.getElementById("lbDeleteBtn"),
    closeButton: document.getElementById("lbCloseBtn"),
    saveButton: document.getElementById("lbSaveBtn"),
    resetButton: document.getElementById("lbResetBtn"),
    overlay: document.getElementById("lbOverlay"),
    chipsBox: document.getElementById("lbChips"),
    planSummary: root.querySelector("[data-dashboard-plan-summary]"),
    planTarget: root.querySelector("[data-dashboard-plan-target]"),
    planAssessment: root.querySelector("[data-dashboard-plan-assessment]"),
    feedList: root.querySelector("[data-dashboard-feed-list]"),
    container: document.getElementById("lbAccordionContainer"),
    targetDateInput: document.getElementById("lbTargetDateInput"),
    statusNode: document.getElementById("lbSessionStatus"),
    modalStatusNode: document.getElementById("lbModalStatus"),
    completedList: root.querySelector("[data-dashboard-completed-list]"),
    primaryFeedCard: root.querySelector("[data-dashboard-primary-feed-card]"),
    primaryFeedIcon: root.querySelector("[data-dashboard-primary-feed-icon]"),
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
  updateChipSummary(context);
  updateSessionActionButtons(context, true);
  setBarStatus(context, "");
  applyPrimaryFeedLoadingState(context);

  const authState = await getCurrentAuthState();
  context.authState = authState;
  context.supabase = authState.configured ? await getSupabaseClient() : null;
  context.systemSettings = await loadSystemSettings(context.supabase);

  if (!authState.configured) {
    applyPrimaryFeedErrorState(context);
    setBarStatus(context, "Der Session-Speicher ist noch nicht konfiguriert.");
    return;
  }

  if (authState.error) {
    applyPrimaryFeedErrorState(context);
    setBarStatus(context, "Die Verbindung zur Session-Datenbank konnte nicht aufgebaut werden.", "error");
    return;
  }

  if (!authState.user) {
    redirectToAccount();
    return;
  }

  setGreetingName(authState.user);
  updateSessionActionButtons(context, false);

  try {
    const persisted = await loadPersistedState(context.supabase, lernbereiche);
    context.state = persisted.state;
    context.activeSession = persisted.session;
    context.sessionCheckStates = persisted.checkStates;
    updatePlanSummary(context);
    updateChipSummary(context);
    await Promise.all([
      refreshPrimaryFeedCard(context),
      refreshCompletedPanel(context),
    ]);
    updateSessionActionButtons(context, false);
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