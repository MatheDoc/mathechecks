import { loadFeedContentMeta, loadFeedProjection } from "../platform/feed-projection.js?v=20260602-feed-cursor-clean";
import { buildAccountUrl, formatAuthDisplayName, getCurrentAuthState, getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js?v=20260520-feed-loading";

let feedContentMetaPromise = null;

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

function buildFeedLauncherLabel(item) {
  const badgeLabel = String(item?.primaryBadge?.label || item?.type || "Feed").trim();
  const checkIndexLabel = String(item?.checkIndexLabel || "").trim();
  const checkKeyword = String(item?.checkKeyword || "").trim();
  const titleText = String(item?.titleText || "").trim();
  const title = checkKeyword
    ? [checkIndexLabel, checkKeyword].filter(Boolean).join(" ")
    : titleText;

  return title
    ? `Aktuelles Feed-Element öffnen: ${badgeLabel}, ${title}`
    : `Aktuelles Feed-Element öffnen: ${badgeLabel}`;
}

function applyFeedLauncherState(button, item = null) {
  if (!button) return;

  const labelNode = button.querySelector("[data-feed-launcher-label]");

  if (!item?.href) {
    button.hidden = true;
    button.dataset.feedReady = "false";
    button.setAttribute("href", buildAccountUrl("/dashboard.html"));
    button.setAttribute("aria-label", "Aktuelles Feed-Element öffnen");
    button.title = "Aktuelles Feed-Element öffnen";
    if (labelNode) labelNode.textContent = "Aktuelles Feed-Element öffnen";
    return;
  }

  const label = buildFeedLauncherLabel(item);
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
    applyFeedLauncherState(button, null);
    return;
  }

  const renderToken = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  button.dataset.feedRenderToken = renderToken;

  try {
    const [supabase, contentMeta] = await Promise.all([
      getSupabaseClient(),
      loadSharedFeedContentMeta(),
    ]);

    if (!supabase) {
      if (button.dataset.feedRenderToken === renderToken) {
        applyFeedLauncherState(button, null);
      }
      return;
    }

    const projection = await loadFeedProjection({
      supabase,
      contentMeta,
      limit: 1,
    });
    const item = Array.isArray(projection?.items) ? projection.items[0] || null : null;

    if (button.dataset.feedRenderToken !== renderToken) return;
    applyFeedLauncherState(button, item);
  } catch {
    if (button.dataset.feedRenderToken === renderToken) {
      applyFeedLauncherState(button, null);
    }
  }
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