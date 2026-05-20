const STATE_PREFIX = "training-state-v1";
const CHECK_TASK_INDEX_PREFIX = "training-task-index-v1";
const FEED_TASK_INDEX_PREFIX = "training-feed-task-index-v1";
const SHUFFLE_NONCE_PREFIX = "training-shuffle-nonce-v1";
const FEED_SHUFFLE_NONCE_PREFIX = "training-feed-shuffle-nonce-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.tabScope.v1";

function getTabScopeId() {
  try {
    let scope = window.sessionStorage.getItem(TAB_SCOPE_SESSION_KEY);
    if (!scope) {
      const randomPart = Math.random().toString(36).slice(2, 10);
      scope = `tab-${Date.now().toString(36)}-${randomPart}`;
      window.sessionStorage.setItem(TAB_SCOPE_SESSION_KEY, scope);
    }
    return scope;
  } catch {
    return "tab-fallback";
  }
}

function getStorageKey(lernbereich) {
  return `${STATE_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}`;
}

function getCheckTaskIndexKey(lernbereich, checkId) {
  return `${CHECK_TASK_INDEX_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}::${checkId || "unknown"}`;
}

function getFeedTaskIndexKey(lernbereich, checkId, activityKey) {
  return `${FEED_TASK_INDEX_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}::${checkId || "unknown"}::${activityKey || "unknown"}`;
}

function getShuffleNonceKey(lernbereich, checkId) {
  return `${SHUFFLE_NONCE_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}::${checkId || "unknown"}`;
}

function getFeedShuffleNonceKey(lernbereich, checkId, activityKey) {
  return `${FEED_SHUFFLE_NONCE_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}::${checkId || "unknown"}::${activityKey || "unknown"}`;
}

function getEmptyState() {
  return {
    selectedCheckId: null,
    taskIndexByCheckId: {},
  };
}

export function loadTrainingState(lernbereich) {
  try {
    const raw = localStorage.getItem(getStorageKey(lernbereich));
    if (!raw) return getEmptyState();
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return getEmptyState();

    return {
      selectedCheckId:
        typeof parsed.selectedCheckId === "string" ? parsed.selectedCheckId : null,
      taskIndexByCheckId:
        parsed.taskIndexByCheckId && typeof parsed.taskIndexByCheckId === "object"
          ? parsed.taskIndexByCheckId
          : {},
    };
  } catch {
    return getEmptyState();
  }
}

export function saveTrainingState(lernbereich, state) {
  localStorage.setItem(getStorageKey(lernbereich), JSON.stringify(state));
}

export function loadTaskIndexForCheck(lernbereich, checkId, fallback = 0) {
  if (!checkId || typeof checkId !== "string") {
    return Number.isInteger(fallback) && fallback >= 0 ? fallback : 0;
  }

  try {
    const raw = localStorage.getItem(getCheckTaskIndexKey(lernbereich, checkId));
    if (raw == null) {
      return Number.isInteger(fallback) && fallback >= 0 ? fallback : 0;
    }
    const parsed = Number(raw);
    if (Number.isInteger(parsed) && parsed >= 0) {
      return parsed;
    }
  } catch {
    // Fall through to fallback.
  }

  return Number.isInteger(fallback) && fallback >= 0 ? fallback : 0;
}

export function saveTaskIndexForCheck(lernbereich, checkId, taskIndex) {
  if (!checkId || typeof checkId !== "string") return;

  const normalized = Number.isInteger(taskIndex) && taskIndex >= 0 ? taskIndex : 0;
  try {
    localStorage.setItem(getCheckTaskIndexKey(lernbereich, checkId), String(normalized));
  } catch {
    // Ignore quota/storage errors.
  }
}

export function loadTrainingFeedTaskIndexForCheck(lernbereich, checkId, activityKey, fallback = 0) {
  if (!checkId || typeof checkId !== "string" || !activityKey || typeof activityKey !== "string") {
    return Number.isInteger(fallback) && fallback >= 0 ? fallback : 0;
  }

  try {
    const raw = localStorage.getItem(getFeedTaskIndexKey(lernbereich, checkId, activityKey));
    if (raw == null) {
      return Number.isInteger(fallback) && fallback >= 0 ? fallback : 0;
    }
    const parsed = Number(raw);
    if (Number.isInteger(parsed) && parsed >= 0) {
      return parsed;
    }
  } catch {
    // Fall through to fallback.
  }

  return Number.isInteger(fallback) && fallback >= 0 ? fallback : 0;
}

export function saveTrainingFeedTaskIndexForCheck(lernbereich, checkId, activityKey, taskIndex) {
  if (!checkId || typeof checkId !== "string" || !activityKey || typeof activityKey !== "string") return;

  const normalized = Number.isInteger(taskIndex) && taskIndex >= 0 ? taskIndex : 0;
  try {
    localStorage.setItem(getFeedTaskIndexKey(lernbereich, checkId, activityKey), String(normalized));
  } catch {
    // Ignore quota/storage errors.
  }
}

export function clearTrainingTaskStateForCheck(lernbereich, checkId) {
  if (!checkId || typeof checkId !== "string") return;

  try {
    localStorage.removeItem(getCheckTaskIndexKey(lernbereich, checkId));
    localStorage.removeItem(getShuffleNonceKey(lernbereich, checkId));

    const state = loadTrainingState(lernbereich);
    if (state.taskIndexByCheckId && Object.prototype.hasOwnProperty.call(state.taskIndexByCheckId, checkId)) {
      delete state.taskIndexByCheckId[checkId];
      saveTrainingState(lernbereich, state);
    }
  } catch {
    // Ignore storage errors.
  }
}

export function loadShuffleNonce(lernbereich, checkId) {
  if (!checkId || typeof checkId !== "string") return null;

  try {
    const raw = localStorage.getItem(getShuffleNonceKey(lernbereich, checkId));
    if (raw != null && raw !== "") return raw;
  } catch {
    // Fall through.
  }
  return null;
}

export function saveShuffleNonce(lernbereich, checkId, nonce) {
  if (!checkId || typeof checkId !== "string") return;

  try {
    localStorage.setItem(getShuffleNonceKey(lernbereich, checkId), String(nonce));
  } catch {
    // Ignore quota/storage errors.
  }
}

export function loadTrainingFeedShuffleNonce(lernbereich, checkId, activityKey) {
  if (!checkId || typeof checkId !== "string" || !activityKey || typeof activityKey !== "string") return null;

  try {
    const raw = localStorage.getItem(getFeedShuffleNonceKey(lernbereich, checkId, activityKey));
    if (raw != null && raw !== "") return raw;
  } catch {
    // Fall through.
  }
  return null;
}

export function saveTrainingFeedShuffleNonce(lernbereich, checkId, activityKey, nonce) {
  if (!checkId || typeof checkId !== "string" || !activityKey || typeof activityKey !== "string") return;

  try {
    localStorage.setItem(getFeedShuffleNonceKey(lernbereich, checkId, activityKey), String(nonce));
  } catch {
    // Ignore quota/storage errors.
  }
}
