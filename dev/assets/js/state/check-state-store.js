const STATE_PREFIX = "dev-training-state-v1";
const CHECK_TASK_INDEX_PREFIX = "dev-training-task-index-v1";
const SHUFFLE_NONCE_PREFIX = "dev-training-shuffle-nonce-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.dev.tabScope.v1";

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

function getShuffleNonceKey(lernbereich, checkId) {
  return `${SHUFFLE_NONCE_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}::${checkId || "unknown"}`;
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
