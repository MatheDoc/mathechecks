import { keepCurrentFeedCursor, releaseCurrentFeedCursor } from "../../platform/feed-actions.js?v=20260603-topbar-feed-badge";
import { clearManualRetentionPriority, loadFeedContentMeta, loadFeedProjection } from "../../platform/feed-projection.js?v=20260604-manual-retention-head";
import { getSupabaseClient } from "../../platform/supabase-client.js";
import { confirmFeedActivityAbort, disableFeedActivityGuard } from "./feed-activity-guard.js?v=20260516-feed-dialog-polish";

const FEED_ICON_SVG = `
  <svg class="feed-card-menu__svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path d="M4 12h3l2-5 4 10 2-5h5" />
    <circle cx="19" cy="5" r="2" />
  </svg>
`;
const DIALOG_DRAG_BLOCK_SELECTOR = "button, a, input, textarea, select, summary, [data-dialog-drag-block]";
const FEED_CONTENT_META_OPTIONS = {
  checksUrl: "/checks.json",
  gebieteScriptId: "gebiete-feed-data",
  lernbereicheScriptId: "lernbereiche-feed-data",
};

function createIcon(label) {
  const node = document.createElement("span");
  node.className = "check-card__actions-icon";
  node.setAttribute("aria-hidden", "true");
  node.textContent = label;
  return node;
}

function createLabel(label) {
  const node = document.createElement("span");
  node.textContent = label;
  return node;
}

function ensureHeaderActions(card) {
  const header = card?.querySelector?.(".check-card__header");
  if (!header) return null;

  let actions = header.querySelector(".check-card__header-actions");
  if (!actions) {
    actions = document.createElement("div");
    actions.className = "check-card__header-actions";
    header.appendChild(actions);
  }
  return actions;
}

function closeExistingDecisionDialogs() {
  document.querySelectorAll(".feed-decision-dialog").forEach((node) => {
    node.dispatchEvent(new CustomEvent("feed-dialog:request-close"));
    if (node.isConnected) node.remove();
  });
}

function getCurrentFeedActivityKey() {
  try {
    return new URL(window.location.href).searchParams.get("activity_key") || "";
  } catch {
    return "";
  }
}

async function keepCurrentFeedSelection() {
  const currentActivityKey = String(getCurrentFeedActivityKey() || "").trim();
  if (!currentActivityKey) return;
  await keepCurrentFeedCursor({ activityKey: currentActivityKey });
}

async function releaseCurrentFeedSelection() {
  const currentActivityKey = String(getCurrentFeedActivityKey() || "").trim();
  if (!currentActivityKey) return;
  await releaseCurrentFeedCursor({ activityKey: currentActivityKey });
}

function clampNumber(value, min, max) {
  if (max < min) return min;
  return Math.min(Math.max(value, min), max);
}

function getViewportSize() {
  return {
    width: document.documentElement.clientWidth || window.innerWidth || 0,
    height: document.documentElement.clientHeight || window.innerHeight || 0,
  };
}

function getConstrainedDialogPosition(panel, left, top) {
  const viewport = getViewportSize();
  const rect = panel.getBoundingClientRect();
  const margin = 12;
  const maxLeft = Math.max(margin, viewport.width - rect.width - margin);
  const maxTop = Math.max(margin, viewport.height - rect.height - margin);

  return {
    left: clampNumber(left, margin, maxLeft),
    top: clampNumber(top, margin, maxTop),
  };
}

function positionDecisionPanel(panel, left, top) {
  const position = getConstrainedDialogPosition(panel, left, top);
  panel.style.transform = "none";
  panel.style.left = `${position.left}px`;
  panel.style.top = `${position.top}px`;
}

function centerDecisionPanel(panel) {
  const viewport = getViewportSize();
  const rect = panel.getBoundingClientRect();
  positionDecisionPanel(panel, (viewport.width - rect.width) / 2, (viewport.height - rect.height) / 2);
}

function isDialogDragBlocked(target) {
  return Boolean(target?.closest?.(DIALOG_DRAG_BLOCK_SELECTOR));
}

function makeDecisionDialogDraggable(panel) {
  let dragState = null;

  const endDrag = (event) => {
    if (!dragState || (event && event.pointerId !== dragState.pointerId)) return;

    try {
      panel.releasePointerCapture(dragState.pointerId);
    } catch {
      // The pointer may already have been released by the browser.
    }

    panel.classList.remove("is-dragging");
    dragState = null;
  };

  const onPointerDown = (event) => {
    if (event.button !== 0 || isDialogDragBlocked(event.target)) return;

    const rect = panel.getBoundingClientRect();
    dragState = {
      pointerId: event.pointerId,
      offsetX: event.clientX - rect.left,
      offsetY: event.clientY - rect.top,
    };

    panel.classList.add("is-dragging");
    try {
      panel.setPointerCapture(event.pointerId);
    } catch {
      // Dragging still works when pointer capture is unavailable.
    }
    event.preventDefault();
  };

  const onPointerMove = (event) => {
    if (!dragState || event.pointerId !== dragState.pointerId) return;
    positionDecisionPanel(panel, event.clientX - dragState.offsetX, event.clientY - dragState.offsetY);
  };

  panel.addEventListener("pointerdown", onPointerDown);
  panel.addEventListener("pointermove", onPointerMove);
  panel.addEventListener("pointerup", endDrag);
  panel.addEventListener("pointercancel", endDrag);

  return () => {
    panel.removeEventListener("pointerdown", onPointerDown);
    panel.removeEventListener("pointermove", onPointerMove);
    panel.removeEventListener("pointerup", endDrag);
    panel.removeEventListener("pointercancel", endDrag);
  };
}

function setDialogBusy(dialog, busy) {
  dialog.querySelectorAll("button").forEach((button) => {
    button.disabled = Boolean(busy);
  });
  dialog.dataset.busy = busy ? "true" : "false";
}

function createDecisionButton({ className, icon, label, detail = "" }) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;

  const iconNode = document.createElement("span");
  iconNode.className = "feed-decision-dialog__button-icon";
  iconNode.setAttribute("aria-hidden", "true");
  iconNode.textContent = icon;

  const copyNode = document.createElement("span");
  copyNode.className = "feed-decision-dialog__button-copy";

  const labelNode = document.createElement("span");
  labelNode.className = "feed-decision-dialog__button-label";
  labelNode.textContent = label;

  copyNode.appendChild(labelNode);

  if (detail) {
    const detailNode = document.createElement("span");
    detailNode.className = "feed-decision-dialog__button-detail";
    detailNode.textContent = detail;
    copyNode.appendChild(detailNode);
  }

  button.appendChild(iconNode);
  button.appendChild(copyNode);
  return button;
}

export async function goToNextFeedActivity({ currentActivityKey } = {}) {
  const resolvedActivityKey = String(currentActivityKey || getCurrentFeedActivityKey() || "").trim();
  try {
    const supabase = await getSupabaseClient();
    if (!supabase) {
      goToDashboard();
      return;
    }

    disableFeedActivityGuard();

    const contentMeta = await loadFeedContentMeta(FEED_CONTENT_META_OPTIONS);
    const projection = await loadFeedProjection({
      supabase,
      contentMeta,
      limit: Infinity,
    });

    const nextItem = (Array.isArray(projection?.items) ? projection.items : []).find((item) => {
      const href = String(item?.href || "").trim();
      if (!href) return false;
      if (resolvedActivityKey && item?.activityKey === resolvedActivityKey) return false;
      return true;
    });

    if (nextItem?.href) {
      window.location.replace(nextItem.href);
      return;
    }
  } catch (error) {
    console.error("Nächste Feed-Aktivität konnte nicht geladen werden:", error);
  }

  goToDashboard();
}

function openFeedDecisionDialog({
  title = "Aktivität abschließen?",
  detail = "",
  completeLabel = "Ja",
  completeDetail = "Nächste Aktivität",
  completeDashboardLabel = "Ja",
  completeDashboardDetail = "Zum Dashboard",
  repeatNowLabel = "Nein",
  repeatNowDetail = "Jetzt wiederholen",
  repeatLaterLabel = "Nein",
  repeatLaterDetail = "Zum Dashboard",
  completeIcon = "✅",
  completeDashboardIcon = "↗",
  repeatNowIcon = "↺",
  repeatLaterIcon = "🕓",
  errorMessage = "Die Entscheidung konnte gerade nicht gespeichert werden.",
  onComplete,
  onRepeat,
  onRepeatLater,
} = {}) {
  closeExistingDecisionDialogs();

  const overlay = document.createElement("div");
  overlay.className = "feed-decision-dialog";
  overlay.setAttribute("role", "presentation");

  const panel = document.createElement("section");
  panel.className = "feed-decision-dialog__panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-modal", "true");
  panel.setAttribute("aria-labelledby", "feed-decision-dialog-title");

  const closeButton = document.createElement("button");
  closeButton.type = "button";
  closeButton.className = "feed-decision-dialog__close";
  closeButton.setAttribute("aria-label", "Dialog schließen");
  closeButton.textContent = "×";

  const eyebrow = document.createElement("p");
  eyebrow.className = "feed-decision-dialog__eyebrow";
  eyebrow.textContent = "Feed";

  const titleNode = document.createElement("h2");
  titleNode.id = "feed-decision-dialog-title";
  titleNode.className = "feed-decision-dialog__title";
  titleNode.textContent = title;

  const detailNode = document.createElement("p");
  detailNode.className = "feed-decision-dialog__detail";
  detailNode.textContent = detail;
  detailNode.hidden = !detail;

  const errorNode = document.createElement("p");
  errorNode.className = "feed-decision-dialog__error";
  errorNode.hidden = true;

  const actions = document.createElement("div");
  actions.className = "feed-decision-dialog__actions";

  const completeButton = createDecisionButton({
    className: "feed-decision-dialog__button feed-decision-dialog__button--primary",
    icon: completeIcon,
    label: completeLabel,
    detail: completeDetail,
  });
  const completeDashboardButton = createDecisionButton({
    className: "feed-decision-dialog__button feed-decision-dialog__button--primary-alt",
    icon: completeDashboardIcon,
    label: completeDashboardLabel,
    detail: completeDashboardDetail,
  });

  const repeatNowButton = createDecisionButton({
    className: "feed-decision-dialog__button feed-decision-dialog__button--repeat-now",
    icon: repeatNowIcon,
    label: repeatNowLabel,
    detail: repeatNowDetail,
  });
  const repeatLaterButton = createDecisionButton({
    className: "feed-decision-dialog__button feed-decision-dialog__button--repeat-later",
    icon: repeatLaterIcon,
    label: repeatLaterLabel,
    detail: repeatLaterDetail,
  });

  let cleanupDialogDrag = () => {};

  const keepDialogInViewport = () => {
    const rect = panel.getBoundingClientRect();
    positionDecisionPanel(panel, rect.left, rect.top);
  };

  const closeDialog = () => {
    document.removeEventListener("keydown", handleKeydown, true);
    window.removeEventListener("resize", keepDialogInViewport);
    overlay.removeEventListener("feed-dialog:request-close", closeDialog);
    cleanupDialogDrag();
    overlay.remove();
  };

  const runDecision = async (action) => {
    if (typeof action !== "function") {
      closeDialog();
      return;
    }

    setDialogBusy(overlay, true);
    errorNode.hidden = true;
    errorNode.textContent = "";

    try {
      await action();
      closeDialog();
    } catch (error) {
      console.error("Feed-Entscheidung konnte nicht ausgeführt werden:", error);
      setDialogBusy(overlay, false);
      errorNode.textContent = errorMessage;
      errorNode.hidden = false;
    }
  };

  const runCompleteDecision = async () => {
    const currentActivityKey = getCurrentFeedActivityKey();
    if (typeof onComplete === "function") {
      await onComplete();
    }

    await goToNextFeedActivity({ currentActivityKey });
  };

  const runCompleteDashboardDecision = async () => {
    if (typeof onComplete === "function") {
      await onComplete();
    }

    goToDashboard();
  };

  const runRepeatNowDecision = async () => {
    await keepCurrentFeedSelection();

    if (typeof onRepeat === "function") {
      await onRepeat();
    }
  };

  const runRepeatLaterDecision = async () => {
    await releaseCurrentFeedSelection();

    if (typeof onRepeatLater === "function") {
      await onRepeatLater();
      return;
    }

    goToDashboard();
  };

  function handleKeydown(event) {
    if (event.key !== "Escape") return;
    event.preventDefault();
    closeDialog();
  }

  closeButton.addEventListener("click", closeDialog);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) closeDialog();
  });
  repeatNowButton.addEventListener("click", () => runDecision(runRepeatNowDecision));
  repeatLaterButton.addEventListener("click", () => runDecision(runRepeatLaterDecision));
  completeButton.addEventListener("click", () => runDecision(runCompleteDecision));
  completeDashboardButton.addEventListener("click", () => runDecision(runCompleteDashboardDecision));

  actions.appendChild(completeButton);
  actions.appendChild(completeDashboardButton);
  actions.appendChild(repeatNowButton);
  actions.appendChild(repeatLaterButton);
  panel.appendChild(closeButton);
  panel.appendChild(eyebrow);
  panel.appendChild(titleNode);
  panel.appendChild(detailNode);
  panel.appendChild(errorNode);
  panel.appendChild(actions);
  overlay.appendChild(panel);
  document.body.appendChild(overlay);
  centerDecisionPanel(panel);
  cleanupDialogDrag = makeDecisionDialogDraggable(panel);
  overlay.addEventListener("feed-dialog:request-close", closeDialog);
  document.addEventListener("keydown", handleKeydown, true);
  window.addEventListener("resize", keepDialogInViewport);
  completeButton.focus({ preventScroll: true });
}

export function leaveFeedContext() {
  if (!confirmFeedActivityAbort()) return;

  try {
    const url = new URL(window.location.href);
    url.searchParams.delete("feed");
    url.searchParams.delete("activity_key");
    url.searchParams.delete("activity_step");
    url.searchParams.delete("activity_run");
    url.searchParams.delete("allow_early_retention_start");
    window.location.assign(`${url.pathname}${url.search}${url.hash}`);
  } catch {
    window.location.assign(window.location.pathname || "/");
  }
}

export function goToDashboard() {
  disableFeedActivityGuard();
  window.location.replace("/dashboard.html");
}

export function navigateFromFeedContext(url) {
  disableFeedActivityGuard();
  window.location.assign(url);
}

export function attachFeedCardControls(section, { cardSelector, stepLabel = "Feed" } = {}) {
  const card = section?.querySelector?.(cardSelector || ".check-card");
  if (!section || !card) return null;

  if (getCurrentFeedActivityKey()) {
    clearManualRetentionPriority();
  }

  section.dataset.feedActive = "true";
  card.classList.add("check-card--feed-active");
  card.dataset.feedStep = stepLabel;

  const headerActions = ensureHeaderActions(card);
  if (!headerActions) return null;

  const existing = headerActions.querySelector(".feed-card-menu");
  if (existing) existing.remove();

  const menu = document.createElement("div");
  menu.className = "check-card__actions-menu feed-card-menu";

  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "check-card__actions-trigger feed-card-menu__trigger";
  trigger.setAttribute("aria-label", `${stepLabel}: noch nicht abschließbar`);
  trigger.title = `${stepLabel}: noch nicht abschließbar`;
  trigger.disabled = true;
  trigger.innerHTML = `<span class="feed-card-menu__icon">${FEED_ICON_SVG}</span><span class="visually-hidden">Feed-Aktivität</span>`;

  menu.appendChild(trigger);
  headerActions.prepend(menu);

  let directTriggerAction = null;

  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    if (trigger.disabled || typeof directTriggerAction !== "function") return;
    directTriggerAction(event);
  });

  function render({ status = "", tone = "neutral", items = [], ready = false } = {}) {
    card.dataset.feedTone = tone;
    menu.dataset.feedReady = ready ? "true" : "false";
    const activeItem = (Array.isArray(items) ? items : []).find((item) => {
      return item?.iconPulse && !item?.disabled && typeof item?.onClick === "function";
    }) || null;

    directTriggerAction = ready ? activeItem?.onClick || null : null;
    trigger.disabled = typeof directTriggerAction !== "function";

    if (typeof directTriggerAction === "function") {
      const actionLabel = String(activeItem?.label || "Abschluss vorbereiten").trim() || "Abschluss vorbereiten";
      trigger.setAttribute("aria-label", `${stepLabel}: ${actionLabel}`);
      trigger.title = `${stepLabel}: ${actionLabel}`;
      return;
    }

    const normalizedStatus = String(status || "").trim();
    const fallbackLabel = normalizedStatus || `${stepLabel}: noch nicht abschließbar`;
    trigger.setAttribute("aria-label", fallbackLabel);
    trigger.title = fallbackLabel;
  }

  return { card, menu, trigger, render, openDecisionDialog: openFeedDecisionDialog };
}