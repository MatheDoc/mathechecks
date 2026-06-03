import { loadFeedAttentionSummary, loadFeedContentMeta, loadFeedProjection } from "../platform/feed-projection.js?v=20260603-topbar-feed-badge";
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
    return `${overdueCount} überfällig, ${dueCount} fällig`;
  }
  if (overdueCount > 0) {
    return `${overdueCount} überfällig`;
  }
  if (dueCount > 0) {
    return `${dueCount} fällig`;
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

async function refreshFeedLauncher(state) {
  const button = document.getElementById("feedLaunchBtn");
  if (!button) return;

  if (!state?.configured || state?.error || !state?.user) {
    applyFeedLauncherState(button, null, null);
    return;
  }

  const renderToken = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  button.dataset.feedRenderToken = renderToken;

  try {
    const supabase = await getSupabaseClient();

    if (!supabase) {
      if (button.dataset.feedRenderToken === renderToken) {
        applyFeedLauncherState(button, null, null);
      }
      return;
    }

    const [attentionSummary, contentMeta] = await Promise.all([
      loadFeedAttentionSummary({ supabase }).catch(() => ({ overdueCount: 0, dueCount: 0, totalCount: 0 })),
      loadSharedFeedContentMeta().catch(() => null),
    ]);

    let item = null;
    if (contentMeta) {
      const projection = await loadFeedProjection({
        supabase,
        contentMeta,
        limit: 1,
      });
      item = Array.isArray(projection?.items) ? projection.items[0] || null : null;
    }

    if (button.dataset.feedRenderToken !== renderToken) return;
    applyFeedLauncherState(button, item, attentionSummary);
  } catch {
    if (button.dataset.feedRenderToken === renderToken) {
      applyFeedLauncherState(button, null, null);
    }
  }
}

function bindFeedLauncherRefreshListener() {
  if (feedLauncherRefreshBound || typeof window === "undefined") return;

  feedLauncherRefreshBound = true;
  window.addEventListener(FEED_BADGE_UPDATE_EVENT, () => {
    void refreshFeedLauncher(currentAuthState);
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
  void refreshFeedLauncher(state);
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