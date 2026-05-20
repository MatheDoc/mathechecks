const FEED_ABORT_MESSAGE = "Diese Feed-Aktivität ist noch offen. Wenn du die Seite verlässt, wird sie abgebrochen. Wirklich abbrechen?";

let activeFeedContext = null;
let isBound = false;
let bypassUnloadUntil = 0;

function normalizeFeedContext(activityContext) {
  if (!activityContext || activityContext.mode !== "feed") return null;

  return {
    mode: "feed",
    activityKey: String(activityContext.activityKey || "").trim(),
    activityStep: String(activityContext.activityStep || "").trim(),
  };
}

function allowNextUnload(ms = 1500) {
  bypassUnloadUntil = Date.now() + Math.max(0, Number(ms) || 0);
}

function isUnloadBypassed() {
  return Date.now() < bypassUnloadUntil;
}

function isHashOnlyNavigation(targetUrl) {
  try {
    const currentUrl = new URL(window.location.href);
    return targetUrl.origin === currentUrl.origin
      && targetUrl.pathname === currentUrl.pathname
      && targetUrl.search === currentUrl.search;
  } catch {
    return false;
  }
}

function keepsSameFeedActivity(targetUrl) {
  if (!activeFeedContext) return false;

  const params = targetUrl.searchParams;
  if (params.get("feed") !== "1") return false;
  if (activeFeedContext.activityKey && params.get("activity_key") !== activeFeedContext.activityKey) return false;
  if (activeFeedContext.activityStep && params.get("activity_step") !== activeFeedContext.activityStep) return false;
  return true;
}

function parseAnchorUrl(anchor) {
  try {
    return new URL(anchor.href, window.location.href);
  } catch {
    return null;
  }
}

function isPlainSameTabClick(event, anchor) {
  if (event.defaultPrevented) return false;
  if (event.button && event.button !== 0) return false;
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return false;
  if (anchor.hasAttribute("download")) return false;

  const target = String(anchor.getAttribute("target") || "").trim().toLowerCase();
  return !target || target === "_self";
}

function handleDocumentClick(event) {
  if (!activeFeedContext) return;

  const anchor = event.target?.closest?.("a[href]");
  if (!anchor || !isPlainSameTabClick(event, anchor)) return;

  const targetUrl = parseAnchorUrl(anchor);
  if (!targetUrl) return;
  if (isHashOnlyNavigation(targetUrl)) return;

  if (keepsSameFeedActivity(targetUrl)) {
    allowNextUnload();
    return;
  }

  if (window.confirm(FEED_ABORT_MESSAGE)) {
    disableFeedActivityGuard();
    return;
  }

  event.preventDefault();
  event.stopPropagation();
}

function handleBeforeUnload(event) {
  if (!activeFeedContext || isUnloadBypassed()) return;

  event.preventDefault();
  event.returnValue = FEED_ABORT_MESSAGE;
  return FEED_ABORT_MESSAGE;
}

function bindFeedActivityGuard() {
  if (isBound) return;
  isBound = true;

  document.addEventListener("click", handleDocumentClick, true);
  window.addEventListener("beforeunload", handleBeforeUnload);
}

export function initFeedActivityGuard(activityContext) {
  activeFeedContext = normalizeFeedContext(activityContext);
  if (activeFeedContext) bindFeedActivityGuard();
}

export function disableFeedActivityGuard() {
  activeFeedContext = null;
  allowNextUnload();
}

export function confirmFeedActivityAbort() {
  if (!activeFeedContext) return true;
  if (!window.confirm(FEED_ABORT_MESSAGE)) return false;
  disableFeedActivityGuard();
  return true;
}