function normalizeSegment(value, fallback = "unknown") {
    const text = String(value ?? "").trim();
    return text || fallback;
}

export function buildTaskUiStateKey({ lernbereich = "", checkId = "", taskIndex = 0 } = {}) {
    const normalizedIndex = Number.isInteger(taskIndex) && taskIndex >= 0 ? taskIndex : 0;
    return [
        "task-ui",
        normalizeSegment(lernbereich),
        normalizeSegment(checkId),
        String(normalizedIndex),
    ].join("::");
}
