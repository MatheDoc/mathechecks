import { loadFeedAttentionSummary, loadFeedContentMeta, loadFeedProjection } from "../platform/feed-projection.js?v=20260606-feed-badge-server-timing";
import { buildAccountUrl, formatAuthDisplayName, getCurrentAuthState, getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js?v=20260520-feed-loading";

const FEED_BADGE_UPDATE_EVENT = "mathechecks:feed-updated";

let feedContentMetaPromise = null;
let currentAuthState = {
  configured: false,
  session: null,
  user: null,
  error: null,
};
let feedLauncherRefreshBound = false;
let feedLauncherRefreshTimer = null;
let feedLauncherDayChangeTimer = null;
let lastFeedLauncherState = {
  item: null,
  attentionSummary: null,
};

function createEmptyAttentionSummary() {
  return { overdueCount: 0, dueCount: 0, totalCount: 0 };
}

function normalizeFeedAttentionSummary(attentionSummary = null) {
  const overdueCount = Math.max(0, Number(attentionSummary?.overdueCount) || 0);
  const dueCount = Math.max(0, Number(attentionSummary?.dueCount) || 0);
  return {
    overdueCount,
    dueCount,
    totalCount: overdueCount + dueCount,
  };
}

function queueFeedLauncherRefresh(state, { delay = 180 } = {}) {
  if (typeof window === "undefined") {
    void refreshFeedLauncher(state);
    return;
  }

  if (feedLauncherRefreshTimer) {
    window.clearTimeout(feedLauncherRefreshTimer);
    feedLauncherRefreshTimer = null;
  }

  const effectiveDelay = Math.max(0, Number(delay) || 0);
  const refreshState = state || currentAuthState;
  feedLauncherRefreshTimer = window.setTimeout(() => {
    feedLauncherRefreshTimer = null;
    void refreshFeedLauncher(refreshState?.configured ? refreshState : currentAuthState);
  }, effectiveDelay);
}

function scheduleFeedLauncherDayRefresh() {
  if (typeof window === "undefined") return;

  if (feedLauncherDayChangeTimer) {
    window.clearTimeout(feedLauncherDayChangeTimer);
    feedLauncherDayChangeTimer = null;
  }

  const nextMidnight = new Date();
  nextMidnight.setHours(24, 0, 1, 0);
  const delay = Math.max(1000, nextMidnight.getTime() - Date.now());

  feedLauncherDayChangeTimer = window.setTimeout(() => {
    feedLauncherDayChangeTimer = null;
    queueFeedLauncherRefresh(currentAuthState, { delay: 0 });
    scheduleFeedLauncherDayRefresh();
  }, delay);
}

async function loadSharedFeedContentMeta() {
  if (feedContentMetaPromise) {
    return feedContentMetaPromise;
  }

  feedContentMetaPromise = loadFeedContentMeta({
    checksUrl: "/checks.json",
    gebieteScriptId: "gebiete-feed-data",
    lernbereicheScriptId: "lernbereiche-feed-data",
  }).catch((error) => {
    feedContentMetaPromise = null;
    throw error;
  });

  return feedContentMetaPromise;
}

function formatFeedBadgeCount(count) {
  const normalizedCount = Math.max(0, Number(count) || 0);
  return normalizedCount > 99 ? "99+" : String(normalizedCount);
}

function buildFeedAttentionLabel(attentionSummary) {
  const overdueCount = Math.max(0, Number(attentionSummary?.overdueCount) || 0);
  const dueCount = Math.max(0, Number(attentionSummary?.dueCount) || 0);

  if (overdueCount > 0 && dueCount > 0) {
    return `${overdueCount} Überfällig, ${dueCount} fällig`;
  }
  if (overdueCount > 0) {
    return `${overdueCount} Überfällig`;
  }
  if (dueCount > 0) {
    return `${dueCount} Fällig`;
  }

  return "";
}

async function syncFeedAppBadge(attentionSummary) {
  try {
    const totalCount = Math.max(0, Number(attentionSummary?.totalCount) || 0);
    if (typeof navigator === "undefined") {
      return;
    }

    if (totalCount > 0 && typeof navigator.setAppBadge === "function") {
      await navigator.setAppBadge(totalCount);
      return;
    }

    if (typeof navigator.clearAppBadge === "function") {
      await navigator.clearAppBadge();
    }
  } catch {
    // Some browsers only expose badging in installed-app contexts.
  }
}

function buildFeedLauncherLabel(item, attentionSummary = null) {
  const badgeLabel = String(item?.primaryBadge?.label || item?.type || "Feed").trim();
  const checkIndexLabel = String(item?.checkIndexLabel || "").trim();
  const checkKeyword = String(item?.checkKeyword || "").trim();
  const titleText = String(item?.titleText || "").trim();
  const attentionLabel = buildFeedAttentionLabel(attentionSummary);
  const title = checkKeyword
    ? [checkIndexLabel, checkKeyword].filter(Boolean).join(" ")
    : titleText;

  if (title) {
    return attentionLabel
      ? `Aktuelles Feed-Element öffnen: ${badgeLabel}, ${title}. ${attentionLabel}.`
      : `Aktuelles Feed-Element öffnen: ${badgeLabel}, ${title}`;
  }

  return attentionLabel
    ? `Aktuelles Feed-Element öffnen: ${badgeLabel}. ${attentionLabel}.`
    : `Aktuelles Feed-Element öffnen: ${badgeLabel}`;
}

function applyFeedLauncherAttention(button, attentionSummary = null) {
  if (!button) return 0;

  const badgeNode = button.querySelector("[data-feed-launcher-badge]");
  const totalCount = Math.max(0, Number(attentionSummary?.totalCount) || 0);

  if (badgeNode) {
    if (totalCount > 0) {
      badgeNode.hidden = false;
      badgeNode.textContent = formatFeedBadgeCount(totalCount);
    } else {
      badgeNode.hidden = true;
      badgeNode.textContent = "";
    }
  }

  void syncFeedAppBadge(attentionSummary);
  return totalCount;
}

function applyFeedLauncherState(button, item = null, attentionSummary = null) {
  if (!button) return;

  const labelNode = button.querySelector("[data-feed-launcher-label]");
  const totalCount = applyFeedLauncherAttention(button, attentionSummary);
  const attentionLabel = buildFeedAttentionLabel(attentionSummary);

  if (!item?.href) {
    const fallbackLabel = attentionLabel
      ? `Feed öffnen. ${attentionLabel}.`
      : "Aktuelles Feed-Element öffnen";
    button.hidden = totalCount <= 0;
    button.dataset.feedReady = totalCount > 0 ? "attention" : "false";
    button.setAttribute("href", buildAccountUrl("/dashboard.html"));
    button.setAttribute("aria-label", fallbackLabel);
    button.title = fallbackLabel;
    if (labelNode) labelNode.textContent = fallbackLabel;
    return;
  }

  const label = buildFeedLauncherLabel(item, attentionSummary);
  button.hidden = false;
  button.dataset.feedReady = "true";
  button.setAttribute("href", item.href);
  button.setAttribute("aria-label", label);
  button.title = label;
  if (labelNode) labelNode.textContent = label;
}

function resetFeedLauncherSnapshot() {
  lastFeedLauncherState = {
    item: null,
    attentionSummary: null,
  };
}

async function refreshFeedLauncher(state) {
  const button = document.getElementById("feedLaunchBtn");
  if (!button) return;

  if (!state?.configured || state?.error || !state?.user) {
    resetFeedLauncherSnapshot();
    applyFeedLauncherState(button, null, null);
    return;
  }

  const renderToken = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  button.dataset.feedRenderToken = renderToken;

  try {
    const supabase = await getSupabaseClient();

    if (!supabase) {
      if (button.dataset.feedRenderToken === renderToken) {
        resetFeedLauncherSnapshot();
        applyFeedLauncherState(button, null, null);
      }
      return;
    }

    // Zuerst die Feed-Projektion laden: pick_feed_cursor ruft serverseitig
    // replan_session auf und aktualisiert dabei die due/overdue-Status in den
    // Projektionen. Die Aufmerksamkeitszahl muss danach gelesen werden, sonst
    // zählt sie den nicht neu geplanten Vorstand und stimmt erst nach einem
    // Seiten-Reload.
    const contentMeta = await loadSharedFeedContentMeta().catch(() => null);

    let itemLoaded = false;
    let item = null;
    if (contentMeta) {
      try {
        const projection = await loadFeedProjection({
          supabase,
          contentMeta,
          limit: 1,
        });
        item = Array.isArray(projection?.items) ? projection.items[0] || null : null;
        itemLoaded = true;
      } catch (error) {
        console.error("Feed-Projektion für den Header-Badge konnte nicht geladen werden:", error);
      }
    }

    const attentionSummaryResult = await loadFeedAttentionSummary({ supabase })
      .then((value) => ({ ok: true, value }))
      .catch((error) => ({ ok: false, error }));

    if (button.dataset.feedRenderToken !== renderToken) return;

    // Das Launcher-Item nur dann aus dem letzten Snapshot übernehmen, wenn die
    // Projektion fehlgeschlagen ist. Eine erfolgreich leere Projektion bedeutet,
    // dass der Feed wirklich leer ist und das alte Item nicht weiterleben darf.
    const resolvedItem = itemLoaded
      ? (item?.href ? item : null)
      : (lastFeedLauncherState.item?.href ? lastFeedLauncherState.item : null);

    // Der Badge-Wert ist die einfach berechenbare Summe aus überfälligen und
    // fälligen Feed-Schritten. Nur bei einem fehlgeschlagenen Laden greift der
    // letzte bekannte Stand als Fallback.
    const resolvedAttentionSummary = attentionSummaryResult?.ok
      ? normalizeFeedAttentionSummary(attentionSummaryResult.value)
      : lastFeedLauncherState.attentionSummary
        ? normalizeFeedAttentionSummary(lastFeedLauncherState.attentionSummary)
        : normalizeFeedAttentionSummary(createEmptyAttentionSummary());

    lastFeedLauncherState = {
      item: resolvedItem?.href ? resolvedItem : null,
      attentionSummary: resolvedAttentionSummary,
    };

    applyFeedLauncherState(button, resolvedItem, resolvedAttentionSummary);
  } catch {
    if (button.dataset.feedRenderToken === renderToken) {
      const fallbackItem = lastFeedLauncherState.item?.href ? lastFeedLauncherState.item : null;
      const fallbackAttentionSummary = lastFeedLauncherState.attentionSummary
        ? normalizeFeedAttentionSummary(lastFeedLauncherState.attentionSummary)
        : null;
      applyFeedLauncherState(button, fallbackItem, fallbackAttentionSummary);
    }
  }
}

function bindFeedLauncherRefreshListener() {
  if (feedLauncherRefreshBound || typeof window === "undefined") return;

  feedLauncherRefreshBound = true;
  scheduleFeedLauncherDayRefresh();
  window.addEventListener(FEED_BADGE_UPDATE_EVENT, () => {
    queueFeedLauncherRefresh(currentAuthState);
  });
  window.addEventListener("focus", () => {
    queueFeedLauncherRefresh(currentAuthState, { delay: 0 });
  });
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState !== "visible") return;
    queueFeedLauncherRefresh(currentAuthState, { delay: 0 });
  });
}

function updateDashboardNavItem(state) {
  const dashboardItem = document.querySelector("[data-dashboard-nav-item]");
  if (!dashboardItem) return;

  const targetHref = String(dashboardItem.dataset.dashboardHref || "").trim();
  const signInHref = buildAccountUrl(targetHref || "/dashboard.html");

  dashboardItem.classList.remove("is-disabled");
  dashboardItem.setAttribute("aria-disabled", "false");
  dashboardItem.tabIndex = 0;

  if (!state.user) {
    dashboardItem.setAttribute("href", signInHref);
    dashboardItem.title = "Zum Anmelden zur Konto-Seite";
    return;
  }

  if (targetHref) {
    dashboardItem.setAttribute("href", targetHref);
  }
  dashboardItem.title = "Dashboard";
}

function updateFeedSidebar(state) {
  queueFeedLauncherRefresh(state);
}

function updateTopbarButton(button, state) {
  if (!button) return;

  currentAuthState = {
    configured: Boolean(state?.configured),
    session: state?.session || null,
    user: state?.user || null,
    error: state?.error || null,
  };

  const labelNode = button.querySelector("[data-auth-label]") || button.querySelector("span:last-child");
  const statusNode = document.querySelector("[data-auth-status]");

  if (!state.configured) {
    button.disabled = false;
    button.dataset.authState = "unconfigured";
    button.setAttribute("aria-label", "Benutzerkonto vorbereiten");
    button.title = "Supabase noch nicht konfiguriert";
    if (labelNode) labelNode.textContent = "Konto vorbereiten";
    if (statusNode) statusNode.textContent = "Auth nicht konfiguriert";
    updateDashboardNavItem(state);
    updateFeedSidebar(state);
    return;
  }

  if (state.error) {
    button.disabled = false;
    button.dataset.authState = "error";
    button.setAttribute("aria-label", "Konto öffnen");
    button.title = "Supabase ist konfiguriert, aber aktuell nicht erreichbar";
    if (labelNode) labelNode.textContent = "Konto";
    if (statusNode) statusNode.textContent = "Auth-Fehler";
    updateDashboardNavItem(state);
    updateFeedSidebar(state);
    return;
  }

  if (state.user) {
    const name = formatAuthDisplayName(state.user);
    button.disabled = false;
    button.dataset.authState = "authenticated";
    button.setAttribute("aria-label", "Benutzerkonto öffnen");
    button.title = `Angemeldet als ${name}`;
    if (labelNode) labelNode.textContent = name;
    if (statusNode) statusNode.textContent = "Angemeldet";
    updateDashboardNavItem(state);
    updateFeedSidebar(state);
    return;
  }

  button.disabled = false;
  button.dataset.authState = "anonymous";
  button.setAttribute("aria-label", "Anmelden oder registrieren");
  button.title = "Anmelden oder registrieren";
  if (labelNode) labelNode.textContent = "Anmelden";
  if (statusNode) statusNode.textContent = "Nicht angemeldet";
  updateDashboardNavItem(state);
  updateFeedSidebar(state);
}

function bindTopbarButton(button, accountPath) {
  if (!button || button.dataset.authBound === "true") return;
  button.dataset.authBound = "true";

  button.addEventListener("click", () => {
    window.location.href = accountPath;
  });
}

async function bindAuthStateListener() {
  const config = getSupabaseRuntimeConfig();
  if (!config.configured) return;

  try {
    const supabase = await getSupabaseClient();
    if (!supabase) return;

    supabase.auth.onAuthStateChange((event, session) => {
      const button = document.getElementById("avatarMenuBtn");
      if (!button) return;

      if (event === "SIGNED_OUT") {
        updateTopbarButton(button, {
          configured: true,
          session: null,
          user: null,
          error: null,
        });
        return;
      }

      updateTopbarButton(button, {
        configured: true,
        session: session || null,
        user: session?.user || null,
        error: null,
      });
    });
  } catch {
    // Keep navigation usable even if auth listener setup fails.
  }
}

async function initAuthShell() {
  const button = document.getElementById("avatarMenuBtn");
  if (!button) return;

  const config = getSupabaseRuntimeConfig();
  bindTopbarButton(button, config.accountPath);
  bindFeedLauncherRefreshListener();

  const state = await getCurrentAuthState();
  updateTopbarButton(button, state);
  await bindAuthStateListener();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    initAuthShell();
  }, { once: true });
} else {
  initAuthShell();
}