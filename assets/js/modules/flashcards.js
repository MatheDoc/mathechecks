import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";
import { getAufgabenSammlung } from "../data/sammlungen-repo.js";
import { getFlashcardsFeedApi } from "../platform/feed-actions.js?v=20260603-topbar-feed-badge";
import { recordUserActivity } from "../platform/progress-client.js?v=20260604-activity-stats";
import { renderVisual } from "../../../../aufgaben/runtime/task-visuals.js";
import { attachFeedCardControls, leaveFeedContext } from "./ui/feed-card-controls.js?v=20260604-manual-retention-head";

const FLASHCARDS_FEED_STEP_KEY = "flashcards";
const FLASHCARDS_ROUND_LIMIT = 20;

const RATING_KEYS_BY_GRADE = {
    2: "hard",
    3: "medium",
    5: "easy",
};

const RATING_LABELS = {
    hard: "Rot",
    medium: "Orange",
    easy: "Grün",
};

const state = {
    cards: [],
    currentCard: null,
    currentTaskIndex: 0,
    root: null,
    lernbereich: "",
    activityContext: null,
    free: {
        preferredCheckId: "",
        roundCards: [],
        currentIndex: 0,
        statusMessage: "",
        statusTone: "neutral",
    },
    feed: {
        active: false,
        trackKind: "session",
        allowEarlyRetentionStart: false,
        controls: null,
        roundId: "",
        roundCards: [],
        currentIndex: 0,
        canPrepare: false,
        busy: false,
        completed: false,
        statusMessage: "",
        statusTone: "neutral",
    },
    hasResizeBinding: false,
};

function getCheckId(check) {
    if (typeof check.check_id === "string" && check.check_id.trim()) {
        return check.check_id;
    }

    const gebiet = check.Gebiet || "gebiet";
    const lernbereich = check.Lernbereich || "lernbereich";
    const nummer = String(Number(check.Nummer) || 0).padStart(2, "0");
    return `${gebiet}__${lernbereich}__${nummer}`;
}

function normalizeFlashcardsFeedContext(activityContext) {
    if (!activityContext || activityContext.mode !== "feed") return null;
    const activityKey = String(activityContext.activityKey || "").trim();
    const params = new URLSearchParams(window.location.search);
    return String(activityContext.activityStep || "").trim() === FLASHCARDS_FEED_STEP_KEY
        ? {
            mode: "feed",
            activityKey,
            activityStep: FLASHCARDS_FEED_STEP_KEY,
            activityRun: String(activityContext.activityRun || "").trim(),
            trackKind: activityKey.startsWith("retention:") ? "retention" : "session",
            allowEarlyRetentionStart: activityKey.startsWith("retention:")
                && params.get("allow_early_retention_start") === "1",
        }
        : null;
}

function getFeedRoundApi() {
    return getFlashcardsFeedApi(state.feed.trackKind);
}

function extractMultipleChoice(text) {
    const result = [];
    let index = 0;

    while (index < text.length) {
        const start = text.indexOf("{", index);
        if (start === -1) {
            result.push(text.slice(index));
            break;
        }

        result.push(text.slice(index, start));
        const rest = text.slice(start);
        const mcMatch = rest.match(/^\{(\d+):(MC|MCV|MULTICHOICE):/);
        if (!mcMatch) {
            result.push("{");
            index = start + 1;
            continue;
        }

        let braceLevel = 0;
        let end = start;
        while (end < text.length) {
            if (text[end] === "{") braceLevel += 1;
            if (text[end] === "}") braceLevel -= 1;
            if (braceLevel === 0 && end > start) break;
            end += 1;
        }

        const fullMatch = text.slice(start, end + 1);
        const inner = fullMatch.replace(/^\{\d+:(MC|MCV|MULTICHOICE):/, "").slice(0, -1);
        const options = inner.split(/(?<!\\)~/);
        const correct = options.find((option) => option.trim().startsWith("=")) || options[0] || "";
        const clean = correct.replace(/^=/, "").trim().replace(/\\~/g, "~");

        result.push(clean);
        index = end + 1;
    }

    return result.join("");
}

function cleanupAnswer(text) {
    if (!text) return "";
    let cleaned = String(text);
    cleaned = cleaned.replace(/\{TIKTOK:id=[A-Za-z0-9_-]+}/g, "");
    cleaned = cleaned.replace(/\{YOUTUBE:id=[A-Za-z0-9_-]+}/g, "");
    cleaned = cleaned.replace(/\{\d+:ANALYSIS_BOUND:=NEG_INF}/g, "-∞");
    cleaned = cleaned.replace(/\{\d+:ANALYSIS_BOUND:=POS_INF}/g, "∞");
    cleaned = cleaned.replace(/\{\d+:ANALYSIS_BOUND:=(-?[0-9.,]+):[0-9.,]+}/g, "$1");
    cleaned = cleaned.replace(/\{\d+:INTERVAL_BOUND:=NEG_INF}/g, "-∞");
    cleaned = cleaned.replace(/\{\d+:INTERVAL_BOUND:=POS_INF}/g, "∞");
    cleaned = cleaned.replace(/\{\d+:INTERVAL_BOUND:=(-?[0-9.,]+):[0-9.,]+}/g, "$1");
    cleaned = cleaned.replace(/\{\d+:NUMERICAL_OPT:=NONE}/g, "existiert nicht");
    cleaned = cleaned.replace(/\{\d+:NUMERICAL_OPT:=(-?[0-9.,]+):[0-9.,]+}/g, "$1");
    cleaned = cleaned.replace(/\{\d+:NUMERICAL:=(-?[0-9.,]+):[0-9.,]+}/g, "$1");
    cleaned = extractMultipleChoice(cleaned);
    return cleaned;
}

function clampTaskIndex(card, taskIndex) {
    const tasks = Array.isArray(card?.tasks) ? card.tasks : [];
    if (!tasks.length) return -1;
    const normalized = Number(taskIndex);
    if (!Number.isInteger(normalized) || normalized < 0 || normalized >= tasks.length) return 0;
    return normalized;
}

function chooseTaskIndex(card) {
    const tasks = Array.isArray(card?.tasks) ? card.tasks : [];
    if (!tasks.length) return -1;
    if (card.questionOrder === "fixed") return 0;
    return Math.floor(Math.random() * tasks.length);
}

function getTaskForCard(card, taskIndex = null) {
    const tasks = Array.isArray(card?.tasks) ? card.tasks : [];
    if (!tasks.length) {
        return { task: null, taskIndex: -1 };
    }

    const resolvedIndex = taskIndex == null
        ? chooseTaskIndex(card)
        : clampTaskIndex(card, taskIndex);

    return { task: tasks[resolvedIndex] || tasks[0] || null, taskIndex: resolvedIndex };
}

function buildDisplayCard(card, task) {
    const fragen = Array.isArray(task?.fragen) ? task.fragen : [];
    const antworten = Array.isArray(task?.antworten) ? task.antworten : [];
    const einleitung = task?.einleitung || "";

    if (card.mode === "single-index") {
        const cardIndex = card.index;
        return {
            einleitung,
            fragen: [fragen[cardIndex] || ""],
            antworten: [antworten[cardIndex] || ""],
            task,
        };
    }

    return {
        einleitung,
        fragen,
        antworten,
        task,
    };
}

function buildFrontHtml(displayCard) {
    const hasMultiple = displayCard.fragen.length > 1;
    const intro = displayCard.einleitung
        ? `<div class="flashcards-intro">${displayCard.einleitung}</div>`
        : "";
    const fragen = hasMultiple
        ? `<ol class="flashcards-list">${displayCard.fragen.map((question) => `<li>${question}</li>`).join("")}</ol>`
        : `<div class="flashcards-text">${displayCard.fragen[0] || ""}</div>`;

    return `
        <div class="flashcards-scroll">
            ${intro}
            ${fragen}
        </div>
    `;
}

function buildBackHtml(displayCard) {
    const hasQuestions = displayCard.fragen.length > 1;
    const intro = displayCard.einleitung
        ? `<div class="flashcards-intro">${displayCard.einleitung}</div>`
        : "";
    const fragen = hasQuestions
        ? `<ol class="flashcards-list">${displayCard.fragen.map((question) => `<li>${question}</li>`).join("")}</ol>`
        : `<div class="flashcards-text">${displayCard.fragen[0] || ""}</div>`;

    const cleaned = displayCard.antworten.map((answer) => cleanupAnswer(answer));
    const hasMultiple = cleaned.length > 1;
    const antworten = hasMultiple
        ? `<ol class="flashcards-list flashcards-answer-tone">${cleaned.map((answer) => `<li>${answer}</li>`).join("")}</ol>`
        : `<div class="flashcards-text flashcards-answer-tone">${cleaned[0] || ""}</div>`;

    return `
        <div class="flashcards-scroll">
            ${intro}
            ${fragen}
            ${antworten}
        </div>
    `;
}

function resizePlotlyInNode(targetNode, retries = 4) {
    if (!targetNode || !window.Plotly?.Plots?.resize) return;

    const plots = Array.from(targetNode.querySelectorAll(".js-plotly-plot"));
    plots.forEach((plotNode) => {
        try {
            window.Plotly.Plots.resize(plotNode);
        } catch {
            // Ignore transient resize errors while layout settles.
        }
    });

    if (retries <= 0) return;
    setTimeout(() => resizePlotlyInNode(targetNode, retries - 1), 120);
}

function shouldIgnoreFlipTarget(target) {
    if (!(target instanceof Element)) return false;
    return Boolean(target.closest("button, a, input, select, textarea, [data-grade]"));
}

async function renderMath(targetNode, retries = 4) {
    if (!targetNode) return;

    const mathJax = window.MathJax;
    if (mathJax && typeof mathJax.typesetPromise === "function") {
        try {
            await mathJax.typesetPromise([targetNode]);
        } catch {
            // Keep UI responsive even if MathJax fails.
        }
        return;
    }

    if (retries <= 0) return;
    await new Promise((resolve) => setTimeout(resolve, 120));
    await renderMath(targetNode, retries - 1);
}

function wrapTablesForHorizontalScroll(root) {
    if (!root) return;

    root.querySelectorAll("table").forEach((table) => {
        const parent = table.parentElement;
        if (!parent || parent.classList.contains("table-scroll")) return;

        const wrapper = document.createElement("div");
        wrapper.classList.add("table-scroll");
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

function syncCardViewportHeight() {
    const bodyNode = state.root?.querySelector(".flashcards-body");
    const cardNode = state.root?.querySelector("#flashcards-card");
    const innerNode = state.root?.querySelector("#flashcards-inner");
    const ratingNode = state.root?.querySelector("#flashcards-rating");
    const frontNode = state.root?.querySelector("#flashcards-front");
    const backNode = state.root?.querySelector("#flashcards-back");
    if (!bodyNode || !cardNode || !innerNode || !ratingNode) return;

    const bodyRect = bodyNode.getBoundingClientRect();
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
    const viewportNode = state.root?.closest(".check-viewport-item");
    const viewportRect = viewportNode?.getBoundingClientRect();
    const viewportBottom = viewportRect
        ? Math.min(viewportRect.bottom, viewportHeight)
        : viewportHeight;
    const bottomSafeSpace = 26;
    const available = Math.max(220, viewportBottom - bodyRect.top - bottomSafeSpace);
    const ratingHeight = ratingNode.offsetHeight || 0;
    const verticalGap = 50;
    const maxCardHeight = Math.max(220, available - ratingHeight - verticalGap);

    cardNode.style.height = `${maxCardHeight}px`;
    cardNode.style.maxHeight = `${maxCardHeight}px`;
    innerNode.style.height = `${maxCardHeight}px`;
    innerNode.style.maxHeight = `${maxCardHeight}px`;

    const setScrollState = (faceNode) => {
        const scrollNode = faceNode?.querySelector(".flashcards-scroll");
        if (!scrollNode) return;
        const overflowDelta = scrollNode.scrollHeight - scrollNode.clientHeight;
        scrollNode.classList.toggle("is-no-scroll", overflowDelta <= 6);
    };

    setScrollState(frontNode);
    setScrollState(backNode);
}

function syncCardViewportHeightWithRetry(targetNode, retries = 4) {
    resizePlotlyInNode(targetNode, 0);
    syncCardViewportHeight();
    if (retries <= 0) return;
    setTimeout(() => syncCardViewportHeightWithRetry(targetNode, retries - 1), 140);
}

function insertVisualIntoFace(faceNode, task) {
    if (!faceNode || !task?.visual) return;

    const visualWrap = document.createElement("div");
    visualWrap.className = "flashcards-visual";

    const scrollNode = faceNode.querySelector(".flashcards-scroll");
    const introNode = scrollNode?.querySelector(".flashcards-intro") || null;

    if (scrollNode) {
        if (introNode && introNode.parentElement === scrollNode) {
            introNode.insertAdjacentElement("afterend", visualWrap);
        } else {
            scrollNode.appendChild(visualWrap);
        }
    } else {
        faceNode.appendChild(visualWrap);
    }

    renderVisual(task, visualWrap);
}

function updateCounterAndMessage() {
    const counterEl = state.root?.querySelector("#flashcards-counter");
    const messageEl = state.root?.querySelector("#flashcards-message");
    if (!counterEl || !messageEl) return;

    if (state.feed.active) {
        const total = state.feed.roundCards.length;
        const current = total > 0 ? Math.min(state.feed.currentIndex + 1, total) : 0;
        const inlineMessage = state.feed.statusTone === "error" ? state.feed.statusMessage : "";
        counterEl.textContent = `Karte ${current} von ${total}`;
        messageEl.hidden = !inlineMessage;
        messageEl.textContent = inlineMessage;
        messageEl.classList.toggle("is-error", state.feed.statusTone === "error");
        messageEl.classList.remove("is-success");
        return;
    }

    if (state.free.roundCards.length) {
        const total = state.free.roundCards.length;
        const current = Math.min(state.free.currentIndex + 1, total);
        counterEl.textContent = `Karte ${current} von ${total}`;
        messageEl.hidden = !state.free.statusMessage;
        messageEl.textContent = state.free.statusMessage;
        messageEl.classList.toggle("is-error", state.free.statusTone === "error");
        messageEl.classList.toggle("is-success", state.free.statusTone === "success");
        return;
    }

    counterEl.textContent = `Karten ${state.cards.length}`;
    messageEl.hidden = true;
    messageEl.textContent = "";
    messageEl.classList.remove("is-error", "is-success");
}

async function renderCurrentCard(card, options = {}) {
    const { taskIndex = null } = options;

    const cardNode = state.root.querySelector("#flashcards-card");
    const innerNode = state.root.querySelector("#flashcards-inner");
    const frontNode = state.root.querySelector("#flashcards-front");
    const backNode = state.root.querySelector("#flashcards-back");
    const ratingNode = state.root.querySelector("#flashcards-rating");
    if (!cardNode || !innerNode || !frontNode || !backNode) return;

    const resolved = getTaskForCard(card, taskIndex);
    const displayCard = buildDisplayCard(card, resolved.task);

    state.currentCard = card;
    state.currentTaskIndex = resolved.taskIndex;

    cardNode.classList.remove("is-flipped");
    cardNode.setAttribute("aria-pressed", "false");
    ratingNode?.classList.remove("is-active");

    frontNode.innerHTML = buildFrontHtml(displayCard);
    backNode.innerHTML = buildBackHtml(displayCard);

    insertVisualIntoFace(frontNode, resolved.task);
    insertVisualIntoFace(backNode, resolved.task);
    wrapTablesForHorizontalScroll(frontNode);
    wrapTablesForHorizontalScroll(backNode);

    await renderMath(innerNode);
    requestAnimationFrame(() => {
        syncCardViewportHeightWithRetry(innerNode, 5);
    });
    updateCounterAndMessage();
}

function flipCurrentCard() {
    const cardNode = state.root.querySelector("#flashcards-card");
    const ratingNode = state.root.querySelector("#flashcards-rating");
    if (!cardNode) return;

    cardNode.classList.toggle("is-flipped");
    const isFlipped = cardNode.classList.contains("is-flipped");
    cardNode.setAttribute("aria-pressed", isFlipped ? "true" : "false");
    ratingNode?.classList.toggle("is-active", isFlipped);

    requestAnimationFrame(() => {
        syncCardViewportHeightWithRetry(cardNode, 2);
    });
}

function findCardById(cardId) {
    return state.cards.find((card) => card.id === cardId) || null;
}

function chooseFreeCard(preferredCheckId = "") {
    const preferredCards = preferredCheckId
        ? state.cards.filter((card) => card.checkId === preferredCheckId)
        : [];
    const pool = preferredCards.length ? preferredCards : state.cards;
    if (!pool.length) return null;
    return pool[Math.floor(Math.random() * pool.length)] || null;
}

function shuffleCards(cards) {
    const shuffled = [...cards];
    for (let index = shuffled.length - 1; index > 0; index -= 1) {
        const randomIndex = Math.floor(Math.random() * (index + 1));
        [shuffled[index], shuffled[randomIndex]] = [shuffled[randomIndex], shuffled[index]];
    }
    return shuffled;
}

function buildFreeRoundCards(preferredCheckId = "") {
    const preferredCards = preferredCheckId
        ? state.cards.filter((card) => card.checkId === preferredCheckId)
        : [];
    const pool = preferredCards.length ? preferredCards : state.cards;
    const limitedCards = shuffleCards(pool).slice(0, Math.min(FLASHCARDS_ROUND_LIMIT, pool.length));
    return limitedCards.map((card) => ({
        card,
        taskIndex: chooseTaskIndex(card),
    }));
}

async function startFreeRound({ preferredCheckId = state.free.preferredCheckId, statusMessage = "", statusTone = "neutral" } = {}) {
    state.free.preferredCheckId = String(preferredCheckId || "").trim();
    state.free.roundCards = buildFreeRoundCards(state.free.preferredCheckId);
    state.free.currentIndex = 0;
    state.free.statusMessage = statusMessage;
    state.free.statusTone = statusTone;

    const firstRoundCard = state.free.roundCards[0] || null;
    if (!firstRoundCard) {
        updateCounterAndMessage();
        return;
    }

    await renderCurrentCard(firstRoundCard.card, { taskIndex: firstRoundCard.taskIndex });
}

function buildRoundRequestPayload(cards) {
    return {
        cardIds: cards.map((card) => card.id),
        checkIds: cards.map((card) => card.checkId),
        taskIndices: cards.map((card) => chooseTaskIndex(card)),
    };
}

function normalizeRoundRows(rows) {
    return (Array.isArray(rows) ? rows : [])
        .map((row) => {
            const card = findCardById(row?.card_id);
            if (!card) return null;
            return {
                card,
                cardId: row.card_id,
                checkId: row.check_id,
                position: Number(row.card_position ?? row.position) || 0,
                taskIndex: Number(row.task_index) || 0,
                ratingKey: row.rating_key || "",
                reviewedAt: row.reviewed_at || null,
            };
        })
        .filter(Boolean)
        .sort((left, right) => left.position - right.position);
}

function getRatingCounts() {
    return state.feed.roundCards.reduce((counts, roundCard) => {
        if (roundCard.ratingKey && counts[roundCard.ratingKey] != null) {
            counts[roundCard.ratingKey] += 1;
        }
        return counts;
    }, { hard: 0, medium: 0, easy: 0 });
}

function getReviewedCount() {
    return state.feed.roundCards.filter((roundCard) => Boolean(roundCard.ratingKey || roundCard.reviewedAt)).length;
}

function getNextUnreviewedIndex(startIndex = 0) {
    const total = state.feed.roundCards.length;
    for (let offset = 0; offset < total; offset += 1) {
        const index = (startIndex + offset) % total;
        const roundCard = state.feed.roundCards[index];
        if (!roundCard?.ratingKey && !roundCard?.reviewedAt) return index;
    }
    return -1;
}

function buildDecisionDetail() {
    const counts = getRatingCounts();
    const total = state.feed.roundCards.length;
    const reviewed = getReviewedCount();
    return `${reviewed} von ${total} Karten bewertet · ${RATING_LABELS.hard}: ${counts.hard}, ${RATING_LABELS.medium}: ${counts.medium}, ${RATING_LABELS.easy}: ${counts.easy}`;
}

function mapFlashcardsFeedLoadError(error, trackKind = "session") {
    const message = String(error?.message || error || "").trim();

    if (message.includes("Authentication required")) {
        return "Bitte melde dich zuerst an, um diesen Flashcard-Durchgang zu laden.";
    }
    if (message.includes("lernbereich_slug is required") || message.includes("card_ids and check_ids must have the same non-empty length")) {
        return "Der Feed-Kontext für diesen Flashcard-Durchgang ist unvollständig.";
    }

    if (trackKind === "retention") {
        if (message.includes("Active flashcard retention scope not found")) {
            return "Für diesen Lernbereich ist noch keine Wiederholung aktiv.";
        }
        if (message.includes("Flashcard retention is not due") || message.includes("No due retention flashcards available")) {
            return "Dieser Wiederholungsdurchgang ist serverseitig noch nicht bereit.";
        }
    }

    return "Der Flashcard-Durchgang konnte gerade nicht geladen werden.";
}

function setFeedStatus(message, tone = "neutral") {
    state.feed.statusMessage = message;
    state.feed.statusTone = tone;
    updateCounterAndMessage();
    renderFeedControls();
}

function renderFeedControls() {
    const controls = state.feed.controls;
    if (!controls) return;

    const ready = state.feed.canPrepare && !state.feed.busy && !state.feed.completed;
    const items = [
        {
            icon: "❌",
            label: "Aktivität abbrechen",
            onClick: leaveFeedContext,
        },
        {
            icon: "✅",
            label: state.feed.busy ? "Wird gespeichert ..." : "Abschluss vorbereiten",
            disabled: !ready,
            iconPulse: ready,
            onClick: openFlashcardsDecision,
        },
    ];

    controls.render({
        status: state.feed.statusMessage,
        tone: state.feed.statusTone,
        items,
        ready,
    });
}

async function completeFlashcardsDecision() {
    if (state.feed.busy || !state.feed.roundId) return;

    state.feed.busy = true;
    setFeedStatus("Der Flashcard-Durchgang wird gespeichert.");

    try {
        await getFeedRoundApi().resolveRound({
            roundId: state.feed.roundId,
            decisionKey: "complete",
        });
        await recordUserActivity({
            activityType: "flashcards",
            lernbereichSlug: state.lernbereich,
            contextKey: state.feed.trackKind === "retention" ? "retention_feed" : "feed",
            details: {
                roundSize: state.feed.roundCards.length,
            },
        });
    } catch (error) {
        state.feed.busy = false;
        setFeedStatus("Der Flashcard-Durchgang konnte gerade nicht gespeichert werden.", "error");
        throw error;
    }

    state.feed.completed = true;
    setFeedStatus("Flashcard-Durchgang abgeschlossen. Die nächste Feed-Aktivität wird geöffnet.", "success");
}

async function repeatFlashcardsDecision() {
    if (state.feed.busy || !state.feed.roundId) return;

    state.feed.busy = true;
    setFeedStatus("Ein neuer Flashcard-Durchgang wird vorbereitet.");

    try {
        await getFeedRoundApi().resolveRound({
            roundId: state.feed.roundId,
            decisionKey: "keep_open",
        });
    } catch (error) {
        state.feed.busy = false;
        setFeedStatus("Der neue Flashcard-Durchgang konnte gerade nicht vorbereitet werden.", "error");
        throw error;
    }

    await loadFeedRound();
}

function openFlashcardsDecision() {
    if (!state.feed.controls?.openDecisionDialog || !state.feed.canPrepare || state.feed.busy) return;

    state.feed.controls.openDecisionDialog({
        title: "Flashcards abschließen?",
        detail: buildDecisionDetail(),
        onComplete: completeFlashcardsDecision,
        onRepeat: repeatFlashcardsDecision,
    });
}

async function loadFeedRound() {
    const payload = buildRoundRequestPayload(state.cards);
    state.feed.busy = true;
    state.feed.canPrepare = false;
    state.feed.completed = false;
    setFeedStatus("Flashcard-Durchgang wird geladen.");

    state.feed.busy = false;

    let rows = [];
    try {
        const result = await getFeedRoundApi().getOrCreateRound({
            lernbereichSlug: state.lernbereich,
            cardIds: payload.cardIds,
            checkIds: payload.checkIds,
            taskIndices: payload.taskIndices,
            cardLimit: FLASHCARDS_ROUND_LIMIT,
            allowEarlyStart: state.feed.trackKind === "retention" && state.feed.allowEarlyRetentionStart,
        });
        rows = Array.isArray(result?.data) ? result.data : [];
    } catch (error) {
        console.error("Flashcard-Durchgang konnte im Feed nicht geladen werden:", error);
        setFeedStatus(mapFlashcardsFeedLoadError(error, state.feed.trackKind), "error");
        return;
    }

    const firstRow = rows[0] || null;
    state.feed.roundId = firstRow?.round_id || "";
    state.feed.roundCards = normalizeRoundRows(rows);
    const nextUnreviewedIndex = getNextUnreviewedIndex(0);
    state.feed.currentIndex = nextUnreviewedIndex >= 0 ? nextUnreviewedIndex : 0;
    state.feed.canPrepare = state.feed.roundCards.length > 0 && getReviewedCount() >= state.feed.roundCards.length;

    if (!state.feed.roundCards.length) {
        setFeedStatus("Für diesen Durchgang wurden keine Karten gefunden.", "error");
        return;
    }

    setFeedStatus(
        state.feed.canPrepare
            ? "Alle Karten wurden bewertet. Du kannst den Abschluss vorbereiten."
            : "Bewerte alle Karten dieses Durchgangs. Danach kannst du den Abschluss vorbereiten.",
    );

    const currentRoundCard = state.feed.roundCards[state.feed.currentIndex] || state.feed.roundCards[0];
    await renderCurrentCard(currentRoundCard.card, { taskIndex: currentRoundCard.taskIndex });
    renderFeedControls();
}

function attachFlashcardsFeedShell(activityContext) {
    const feedContext = normalizeFlashcardsFeedContext(activityContext);
    state.feed.active = Boolean(feedContext);
    state.feed.trackKind = feedContext?.trackKind || "session";
    state.feed.allowEarlyRetentionStart = Boolean(feedContext?.allowEarlyRetentionStart);
    if (!state.feed.active) return;

    state.feed.controls = attachFeedCardControls(state.root, {
        cardSelector: "[data-flashcards-app]",
        stepLabel: "Flashcards",
    });
    state.feed.statusMessage = "Bewerte alle Karten dieses Durchgangs. Danach kannst du den Abschluss vorbereiten.";
    state.feed.statusTone = "neutral";
    renderFeedControls();
}

async function rateCurrentFeedCard(ratingKey) {
    if (state.feed.busy || !state.feed.roundId) return;
    const roundCard = state.feed.roundCards[state.feed.currentIndex];
    if (!roundCard) return;

    state.feed.busy = true;
    renderFeedControls();

    state.feed.busy = false;

    try {
        await getFeedRoundApi().recordReview({
            roundId: state.feed.roundId,
            cardId: roundCard.cardId,
            ratingKey,
        });
    } catch (error) {
        const detail = String(error?.message || "").trim();
        setFeedStatus(
            detail
                ? `Die Kartenbewertung konnte gerade nicht gespeichert werden. Detail: ${detail}`
                : "Die Kartenbewertung konnte gerade nicht gespeichert werden.",
            "error",
        );
        return;
    }

    roundCard.ratingKey = ratingKey;
    roundCard.reviewedAt = new Date().toISOString();

    const nextIndex = getNextUnreviewedIndex(state.feed.currentIndex + 1);
    if (nextIndex >= 0) {
        state.feed.currentIndex = nextIndex;
        const nextRoundCard = state.feed.roundCards[nextIndex];
        setFeedStatus("Bewerte alle Karten dieses Durchgangs. Danach kannst du den Abschluss vorbereiten.");
        await renderCurrentCard(nextRoundCard.card, { taskIndex: nextRoundCard.taskIndex });
        renderFeedControls();
        return;
    }

    state.feed.canPrepare = true;
    setFeedStatus("Alle Karten wurden bewertet. Du kannst den Abschluss vorbereiten.");
    renderFeedControls();
}

async function rateCurrentCard(grade) {
    const ratingKey = RATING_KEYS_BY_GRADE[grade];
    if (!ratingKey) return;

    if (state.feed.active) {
        await rateCurrentFeedCard(ratingKey);
        return;
    }

    const currentRoundSize = state.free.roundCards.length;
    if (!currentRoundSize) return;

    const nextIndex = state.free.currentIndex + 1;
    if (nextIndex < currentRoundSize) {
        state.free.currentIndex = nextIndex;
        state.free.statusMessage = "";
        state.free.statusTone = "neutral";
        const nextRoundCard = state.free.roundCards[nextIndex];
        await renderCurrentCard(nextRoundCard.card, { taskIndex: nextRoundCard.taskIndex });
        return;
    }

    await recordUserActivity({
        activityType: "flashcards",
        lernbereichSlug: state.lernbereich,
        contextKey: "free",
        details: {
            roundSize: currentRoundSize,
        },
    });

    await startFreeRound({
        preferredCheckId: state.free.preferredCheckId,
        statusMessage: `Stapel mit ${currentRoundSize} Karten abgeschlossen. Neuer Durchgang gestartet.`,
        statusTone: "success",
    });
}

function buildCards(checks) {
    const cards = [];

    checks.forEach((check) => {
        const tasks = Array.isArray(check._sammlung) ? check._sammlung : [];
        if (!tasks.length) return;

        const questionOrder = check.questionOrder === "fixed" ? "fixed" : "shuffle";
        const flashtyp = check.Flashtyp === "gruppiert" ? "gruppiert" : "einzeln";
        const checkId = getCheckId(check);

        if (flashtyp === "einzeln") {
            const maxQuestions = tasks.reduce((max, task) => {
                const questionCount = Array.isArray(task?.fragen) ? task.fragen.length : 0;
                return Math.max(max, questionCount);
            }, 0);

            for (let questionIndex = 0; questionIndex < maxQuestions; questionIndex += 1) {
                cards.push({
                    id: `${checkId}::single::${questionIndex}`,
                    checkId,
                    check,
                    mode: "single-index",
                    index: questionIndex,
                    questionOrder,
                    tasks,
                });
            }
            return;
        }

        cards.push({
            id: `${checkId}::grouped`,
            checkId,
            check,
            mode: "grouped",
            questionOrder,
            tasks,
        });
    });

    return cards;
}

function bindEvents() {
    const cardNode = state.root.querySelector("#flashcards-card");

    cardNode?.addEventListener("click", (event) => {
        if (shouldIgnoreFlipTarget(event.target)) return;
        flipCurrentCard();
    }, { capture: true });

    cardNode?.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        flipCurrentCard();
    });

    const ratingButtons = Array.from(state.root.querySelectorAll(".flashcards-rate"));
    ratingButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const grade = Number(button.getAttribute("data-grade") || 0);
            if (!grade) return;
            void rateCurrentCard(grade);
        });
    });
}

function renderInfo(text) {
    if (!state.root) return;
    const body = state.root.querySelector(".check-card__body");
    if (!body) return;
    body.innerHTML = `<p class="flashcards-message-static">${text}</p>`;
}

export async function initFlashcardsModule({ root, lernbereich, preferredCheckId = "", activityContext = null }) {
    state.root = root;
    state.lernbereich = lernbereich || "";
    state.activityContext = activityContext;
    state.cards = [];
    state.currentCard = null;
    state.currentTaskIndex = 0;
    state.free = {
        preferredCheckId: String(preferredCheckId || "").trim(),
        roundCards: [],
        currentIndex: 0,
        statusMessage: "",
        statusTone: "neutral",
    };
    state.feed = {
        active: false,
        trackKind: "session",
        allowEarlyRetentionStart: false,
        controls: null,
        roundId: "",
        roundCards: [],
        currentIndex: 0,
        canPrepare: false,
        busy: false,
        completed: false,
        statusMessage: "",
        statusTone: "neutral",
    };

    if (!state.lernbereich) {
        renderInfo("Kein Lernbereich gesetzt.");
        return;
    }

    const checks = await getChecksByLernbereich(state.lernbereich);
    if (!checks.length) {
        renderInfo(`Keine Checks für Lernbereich "${state.lernbereich}" gefunden.`);
        return;
    }

    const checksWithTasks = await Promise.all(
        checks.map(async (check) => {
            const sammlungName = String(check?.Sammlung || "").trim();
            if (!sammlungName) return { ...check, _sammlung: [] };
            try {
                const sammlung = await getAufgabenSammlung(sammlungName, {
                    gebiet: check.Gebiet,
                    lernbereich: check.Lernbereich,
                });
                return { ...check, _sammlung: sammlung };
            } catch {
                return { ...check, _sammlung: [] };
            }
        }),
    );

    state.cards = buildCards(checksWithTasks);
    if (!state.cards.length) {
        renderInfo("Keine Flashcards gefunden.");
        return;
    }

    bindEvents();
    attachFlashcardsFeedShell(activityContext);

    if (!state.hasResizeBinding) {
        const onResize = () => syncCardViewportHeight();
        window.addEventListener("resize", onResize);
        state.hasResizeBinding = true;
    }

    if (state.feed.active) {
        await loadFeedRound();
        return;
    }

    await startFreeRound({ preferredCheckId });
}
