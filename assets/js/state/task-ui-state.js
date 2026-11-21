const TAB_SCOPE_SESSION_KEY = "mathechecks.tabScope.v1";
const DASHBOARD_WORKLIST_FILTER_PREFIX = "dashboard-worklist-filter-v1::";
const DASHBOARD_WORKLIST_FILTERS = new Set(["session", "retention", "all"]);

function normalizeSegment(value, fallback = "unknown") {
    const text = String(value ?? "").trim();
    return text || fallback;
}

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

function getDashboardWorklistFilterKey() {
    return `${DASHBOARD_WORKLIST_FILTER_PREFIX}${getTabScopeId()}`;
}

export function loadDashboardWorklistFilter(fallback = "session") {
    const normalizedFallback = DASHBOARD_WORKLIST_FILTERS.has(fallback) ? fallback : "session";

    try {
        const filter = window.localStorage.getItem(getDashboardWorklistFilterKey());
        return DASHBOARD_WORKLIST_FILTERS.has(filter) ? filter : normalizedFallback;
    } catch {
        return normalizedFallback;
    }
}

export function saveDashboardWorklistFilter(filter) {
    if (!DASHBOARD_WORKLIST_FILTERS.has(filter)) return;

    try {
        window.localStorage.setItem(getDashboardWorklistFilterKey(), filter);
    } catch {
        // Ignore quota/storage errors.
    }
}

export function buildTaskUiStateKey({
    lernbereich = "",
    checkId = "",
    taskIndex = 0,
} = {}) {
    const normalizedIndex = Number.isInteger(taskIndex) && taskIndex >= 0 ? taskIndex : 0;
    return [
        "task-ui",
        normalizeSegment(lernbereich),
        normalizeSegment(checkId),
        String(normalizedIndex),
    ].join("::");
}
