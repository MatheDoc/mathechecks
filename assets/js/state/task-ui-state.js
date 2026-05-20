const TASK_UI_STORAGE_PREFIX = "task-ui-state-v1::";
const TAB_SCOPE_SESSION_KEY = "mathechecks.tabScope.v1";

function normalizeSegment(value, fallback = "unknown") {
    const text = String(value ?? "").trim();
    return text || fallback;
}

function getTabScopeId() {
    try {
        return window.sessionStorage.getItem(TAB_SCOPE_SESSION_KEY) || "tab-fallback";
    } catch {
        return "tab-fallback";
    }
}

export function buildTaskUiStateKey({
    lernbereich = "",
    checkId = "",
    taskIndex = 0,
    activityKey = "",
    activityStep = "",
    activityRun = "",
} = {}) {
    const normalizedIndex = Number.isInteger(taskIndex) && taskIndex >= 0 ? taskIndex : 0;
    const segments = [
        "task-ui",
        normalizeSegment(lernbereich),
        normalizeSegment(checkId),
        String(normalizedIndex),
    ];

    if (activityKey || activityStep || activityRun) {
        segments.push(
            "feed",
            normalizeSegment(activityStep, "step"),
            normalizeSegment(activityKey, "activity"),
            normalizeSegment(activityRun, "no-run")
        );
    }

    return segments.join("::");
}

export function clearTaskUiStateForCheck({
    lernbereich = "",
    checkId = "",
    activityKey = "",
    activityStep = "",
    activityRun = "",
} = {}) {
    const normalizedLernbereich = normalizeSegment(lernbereich);
    const normalizedCheckId = normalizeSegment(checkId);
    if (!normalizedCheckId || normalizedCheckId === "unknown") return 0;

    const keyPrefix = `${TASK_UI_STORAGE_PREFIX}${getTabScopeId()}::task-ui::${normalizedLernbereich}::${normalizedCheckId}::`;
    const normalizedActivityKey = activityKey ? normalizeSegment(activityKey, "activity") : "";
    const normalizedActivityStep = activityStep ? normalizeSegment(activityStep, "step") : "";
    const normalizedActivityRun = activityRun ? normalizeSegment(activityRun, "no-run") : "";
    let removedCount = 0;

    try {
        for (let index = window.localStorage.length - 1; index >= 0; index -= 1) {
            const key = window.localStorage.key(index);
            if (!key?.startsWith(keyPrefix)) continue;
            if (normalizedActivityStep && !key.includes(`::feed::${normalizedActivityStep}::`)) continue;
            if (normalizedActivityKey && !key.includes(`::${normalizedActivityKey}::`)) continue;
            if (normalizedActivityRun && !key.endsWith(`::${normalizedActivityRun}`)) continue;
            window.localStorage.removeItem(key);
            removedCount += 1;
        }
    } catch {
        return removedCount;
    }

    return removedCount;
}
