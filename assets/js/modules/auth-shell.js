import { loadFeedContentMeta, loadFeedProjection } from "../platform/feed-projection.js?v=20260520-start-feed";
import { buildAccountUrl, formatAuthDisplayName, getCurrentAuthState, getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js";

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

function buildFeaturedCardStyle(item) {
  return [
    `background:linear-gradient(135deg,color-mix(in srgb, ${item.accent} 14%, transparent) 0%,color-mix(in srgb, ${item.accentSoft} 58%, transparent) 100%)`,
    `border-color:color-mix(in srgb, ${item.accent} 30%, var(--border))`,
  ].join(";");
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

function renderSidebarFallback(feedSidebar) {
  const listNode = feedSidebar?.querySelector("[data-feed-sidebar-list]");
  if (!listNode) return;

  listNode.innerHTML = `
    <li class="action-card action-featured" data-type="feed" style="cursor:default;">
      <div class="action-icon action-icon-featured" style="background:linear-gradient(135deg,var(--accent),var(--teal));color:#fff;">→</div>
      <div class="action-body">
        <div class="action-title">Noch kein Feed-Einstieg</div>
        <div class="action-badges">${createBadgeMarkup("Feed")}</div>
      </div>
    </li>
  `;
}

function renderSidebarItems(feedSidebar, items) {
  const listNode = feedSidebar?.querySelector("[data-feed-sidebar-list]");
  if (!listNode) return;

  if (!Array.isArray(items) || items.length === 0) {
    renderSidebarFallback(feedSidebar);
    return;
  }

  listNode.innerHTML = items.map((item, index) => {
    const featured = index === 0;
    const cardClassName = featured ? "action-card action-featured" : "action-card";
    const iconClassName = featured ? "action-icon action-icon-featured" : "action-icon";
    const actionHref = item.href ? ` data-action-href="${escapeHtml(item.href)}"` : "";
    const cardStyle = featured ? ` style="${escapeHtml(buildFeaturedCardStyle(item))}"` : "";
    const arrowMarkup = featured ? "" : '<span class="action-arrow" aria-hidden="true">›</span>';

    return `
      <li class="${cardClassName}" data-type="${escapeHtml(item.type)}"${actionHref}${cardStyle}>
        <div class="${iconClassName}" style="${escapeHtml(item.iconStyle)}">${escapeHtml(item.icon)}</div>
        <div class="action-body">
          <div class="action-title">${escapeHtml(item.titleText)}</div>
          <div class="action-badges">${item.primaryBadge ? createBadgeMarkup(item.primaryBadge.label, item.primaryBadge.type) : ""}</div>
        </div>
        ${arrowMarkup}
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
        renderSidebarFallback(feedSidebar);
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
      renderSidebarFallback(feedSidebar);
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

  feedSidebar.hidden = !state.user;
  if (state.user) {
    void refreshFeedSidebar(state);
  }
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