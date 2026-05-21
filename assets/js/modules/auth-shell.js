import { loadFeedContentMeta, loadFeedProjection } from "../platform/feed-projection.js?v=20260521-feed-session-gap";
import { buildAccountUrl, formatAuthDisplayName, getCurrentAuthState, getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js?v=20260520-feed-loading";

const FEED_SIDEBAR_ITEM_LIMIT = 5;

let sidebarContentMetaPromise = null;

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function createBadgeMarkup(label, type = "") {
  const safeLabel = escapeHtml(label);
  const safeType = type ? ` type-${escapeHtml(type)}` : "";
  return `<span class="action-badge${safeType}">${safeLabel}</span>`;
}

async function loadSidebarContentMeta(feedSidebar) {
  if (sidebarContentMetaPromise) {
    return sidebarContentMetaPromise;
  }

  sidebarContentMetaPromise = loadFeedContentMeta({
    checksUrl: feedSidebar?.dataset?.feedSidebarChecksUrl || "/checks.json",
    gebieteScriptId: "gebiete-feed-data",
    lernbereicheScriptId: "lernbereiche-feed-data",
  }).catch((error) => {
    sidebarContentMetaPromise = null;
    console.error("Feed-Sidebar: checks.json konnte nicht geladen werden:", error);
    throw error;
  });

  return sidebarContentMetaPromise;
}

function renderSidebarMessage(feedSidebar, {
  title = "Feed",
  description = "",
  badgeLabel = "Feed",
  icon = "→",
  iconStyle = "background:linear-gradient(135deg,var(--accent),var(--teal));color:#fff;",
  actionHref = "",
} = {}) {
  const listNode = feedSidebar?.querySelector("[data-feed-sidebar-list]");
  if (!listNode) return;

  feedSidebar.dataset.feedRenderToken = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

  const safeActionHref = String(actionHref || "").trim();
  const actionHrefMarkup = safeActionHref ? ` data-action-href="${escapeHtml(safeActionHref)}"` : "";
  const cursorStyle = safeActionHref ? "cursor:pointer;" : "cursor:default;";

  listNode.innerHTML = `
    <li class="action-card" data-type="feed"${actionHrefMarkup} style="${cursorStyle}">
      <div class="action-icon" style="${escapeHtml(iconStyle)}">${escapeHtml(icon)}</div>
      <div class="action-body">
        <div class="action-title">${escapeHtml(title)}</div>
        ${description ? `<div class="action-desc">${escapeHtml(description)}</div>` : ""}
        <div class="action-badges">${createBadgeMarkup(badgeLabel)}</div>
      </div>
    </li>
  `;
}

function renderSidebarLoading(feedSidebar) {
  renderSidebarMessage(feedSidebar, {
    title: "Feed wird geladen",
    description: "Deine nächsten Aktivitäten werden vorbereitet.",
    badgeLabel: "Feed",
    icon: "…",
  });
}

function renderSidebarAnonymous(feedSidebar) {
  const nextPath = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  renderSidebarMessage(feedSidebar, {
    title: "Feed nach Anmeldung",
    description: "Melde dich an, um deinen persönlichen Lernfeed zu sehen.",
    badgeLabel: "Konto",
    icon: "↗",
    actionHref: buildAccountUrl(nextPath),
  });
}

function renderSidebarEmpty(feedSidebar) {
  renderSidebarMessage(feedSidebar, {
    title: "Gerade keine Feed-Aktivität",
    description: "Sobald eine Session oder eine fällige Wiederholung ansteht, erscheint sie hier.",
    badgeLabel: "Feed",
  });
}

function renderSidebarError(feedSidebar) {
  renderSidebarMessage(feedSidebar, {
    title: "Feed gerade nicht verfügbar",
    description: "Der Feed konnte gerade nicht geladen werden.",
    badgeLabel: "Feed",
    icon: "!",
  });
}

function renderSidebarItems(feedSidebar, items) {
  const listNode = feedSidebar?.querySelector("[data-feed-sidebar-list]");
  if (!listNode) return;

  if (!Array.isArray(items) || items.length === 0) {
    renderSidebarEmpty(feedSidebar);
    return;
  }

  listNode.innerHTML = items.map((item, index) => {
    const actionHref = item.href ? ` data-action-href="${escapeHtml(item.href)}"` : "";

    return `
      <li class="action-card" data-type="${escapeHtml(item.type)}"${actionHref}>
        <div class="action-icon" style="${escapeHtml(item.iconStyle)}">${escapeHtml(item.icon)}</div>
        <div class="action-body">
          <div class="action-title">${escapeHtml(item.titleText)}</div>
          <div class="action-badges">${item.primaryBadge ? createBadgeMarkup(item.primaryBadge.label, item.primaryBadge.type) : ""}</div>
        </div>
      </li>
    `;
  }).join("");
}

function bindFeedSidebarClicks(feedSidebar) {
  const listNode = feedSidebar?.querySelector("[data-feed-sidebar-list]");
  if (!listNode || listNode.dataset.feedSidebarBound === "true") return;

  listNode.dataset.feedSidebarBound = "true";
  listNode.addEventListener("click", (event) => {
    if (event.target.closest("a, button")) return;

    const card = event.target.closest(".action-card[data-action-href]");
    if (!card || !listNode.contains(card)) return;

    const href = String(card.dataset.actionHref || "").trim();
    if (href) {
      window.location.href = href;
    }
  });
}

async function refreshFeedSidebar(state) {
  const feedSidebar = document.getElementById("feedSidebar");
  if (!feedSidebar || !state?.user) return;

  bindFeedSidebarClicks(feedSidebar);

  const renderToken = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  feedSidebar.dataset.feedRenderToken = renderToken;

  try {
    const [supabase, contentMeta] = await Promise.all([
      getSupabaseClient(),
      loadSidebarContentMeta(feedSidebar),
    ]);

    if (!supabase) {
      if (feedSidebar.dataset.feedRenderToken === renderToken) {
        renderSidebarError(feedSidebar);
      }
      return;
    }

    const projection = await loadFeedProjection({
      supabase,
      contentMeta,
      limit: FEED_SIDEBAR_ITEM_LIMIT,
    });
    const items = Array.isArray(projection?.items) ? projection.items : [];

    if (feedSidebar.dataset.feedRenderToken !== renderToken) return;
    renderSidebarItems(feedSidebar, items);
  } catch (error) {
    console.error("Feed-Sidebar konnte nicht geladen werden:", error);
    if (feedSidebar.dataset.feedRenderToken === renderToken) {
      renderSidebarError(feedSidebar);
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
  const feedSidebar = document.getElementById("feedSidebar");
  if (!feedSidebar) return;

  bindFeedSidebarClicks(feedSidebar);

  if (!state?.configured) {
    feedSidebar.hidden = true;
    return;
  }

  feedSidebar.hidden = false;

  if (state.error) {
    renderSidebarError(feedSidebar);
    return;
  }

  if (!state.user) {
    renderSidebarAnonymous(feedSidebar);
    return;
  }

  renderSidebarLoading(feedSidebar);
  void refreshFeedSidebar(state);
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

  const feedSidebar = document.getElementById("feedSidebar");
  if (config.configured && feedSidebar) {
    feedSidebar.hidden = false;
    renderSidebarLoading(feedSidebar);
  }

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