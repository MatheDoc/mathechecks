import { getChecksByLernbereich } from "../data/checks-repo.js";
import { getAufgabenSammlung } from "../data/sammlungen-repo.js";
import { renderVisual } from "../../../../aufgaben/runtime/task-visuals.js";

const msPerDay = 24 * 60 * 60 * 1000;
const PROGRESS_PREFIX = "dev-flashcards-progress-v1";
const VIEW_PREFIX = "dev-flashcards-view-v1";

const state = {
    cards: [],
    progress: {},
    currentCard: null,
    root: null,
    lernbereich: "",
    view: {
        currentCardId: null,
        taskIndexByCard: {},
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

function getProgressStorageKey() {
    return `${PROGRESS_PREFIX}:${state.lernbereich || "default"}`;
}

function getViewStorageKey() {
    return `${VIEW_PREFIX}:${state.lernbereich || "default"}`;
}

function createDefaultViewState() {
    return {
        currentCardId: null,
        taskIndexByCard: {},
    };
}

function normalizeViewState(raw) {
    const fallback = createDefaultViewState();
    if (!raw || typeof raw !== "object") return fallback;
    return {
        currentCardId: typeof raw.currentCardId === "string" ? raw.currentCardId : null,
        taskIndexByCard:
            raw.taskIndexByCard && typeof raw.taskIndexByCard === "object"
                ? raw.taskIndexByCard
                : {},
    };
}

function loadProgress() {
    try {
        const raw = localStorage.getItem(getProgressStorageKey());
        const parsed = raw ? JSON.parse(raw) : {};
        state.progress = parsed && typeof parsed === "object" ? parsed : {};
    } catch {
        state.progress = {};
    }
}

function saveProgress() {
    try {
        localStorage.setItem(getProgressStorageKey(), JSON.stringify(state.progress));
    } catch {
        // Ignore storage write failures in private browsing.
    }
}

function loadViewState() {
    try {
        const raw = localStorage.getItem(getViewStorageKey());
        state.view = normalizeViewState(raw ? JSON.parse(raw) : null);
    } catch {
        state.view = createDefaultViewState();
    }
}

function saveViewState() {
    try {
        state.view = normalizeViewState(state.view);
        localStorage.setItem(getViewStorageKey(), JSON.stringify(state.view));
    } catch {
        // Ignore storage write failures in private browsing.
    }
}

function getCardState(cardId) {
    const entry = state.progress[cardId];
    if (!entry) {
        return { reps: 0, interval: 0, ease: 2.5, due: 0 };
    }
    return entry;
}

function setCardState(cardId, data) {
    state.progress[cardId] = data;
    saveProgress();
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
        const correct = options.find((opt) => opt.trim().startsWith("=")) || options[0] || "";
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
    cleaned = cleaned.replace(/\{\d+:NUMERICAL:=(-?[0-9.,]+):[0-9.,]+}/g, "$1");
    cleaned = extractMultipleChoice(cleaned);
    return cleaned;
}

function formatDueMessage(nextDue) {
    if (!nextDue) return "";
    const now = Date.now();
    const diff = Math.max(nextDue - now, 0);
    const minutes = Math.ceil(diff / 60000);
    if (minutes < 60) return `Nächste Karte in ca. ${minutes} Min.`;
    const hours = Math.round(minutes / 60);
    return `Nächste Karte in ca. ${hours} Std.`;
}

function getDueSnapshot(cards) {
    const now = Date.now();
    const dueCards = [];
    let nextUpcoming = null;

    cards.forEach((card) => {
        const cardState = getCardState(card.id);
        const due = cardState.due || 0;
        if (due <= now) {
            dueCards.push(card);
            return;
        }
        if (!nextUpcoming || due < nextUpcoming.due) {
            nextUpcoming = { card, due };
        }
    });

    return { dueCards, nextUpcoming };
}

function updateCounterAndMessage() {
    const counterEl = state.root?.querySelector("#dev-fc-counter");
    const messageEl = state.root?.querySelector("#dev-fc-message");
    if (!counterEl || !messageEl) return;

    const { dueCards, nextUpcoming } = getDueSnapshot(state.cards);
    counterEl.textContent = `Karten ${dueCards.length} von ${state.cards.length}`;
    messageEl.textContent = dueCards.length > 0 ? "" : formatDueMessage(nextUpcoming?.due);
}

function chooseNextCard() {
    const { dueCards, nextUpcoming } = getDueSnapshot(state.cards);
    if (dueCards.length > 0) {
        return dueCards[Math.floor(Math.random() * dueCards.length)] || null;
    }
    return nextUpcoming?.card || null;
}

function findStoredCard(cards) {
    const storedId = state.view?.currentCardId;
    if (!storedId) return null;
    return cards.find((card) => card.id === storedId) || null;
}

function chooseInitialCard(cards, preferredCheckId = "") {
    const preferred = preferredCheckId
        ? cards.find((card) => card.checkId === preferredCheckId) || null
        : null;
    if (preferred) return preferred;
    const stored = findStoredCard(cards);
    if (stored) return stored;
    return chooseNextCard();
}

function getTaskForCard(card, refreshVariant = false) {
    const tasks = Array.isArray(card.tasks) ? card.tasks : [];
    if (!tasks.length) {
        return { task: null, taskIndex: -1 };
    }

    const stored = Number(state.view.taskIndexByCard?.[card.id]);
    const hasStored = Number.isInteger(stored) && stored >= 0 && stored < tasks.length;

    let taskIndex = 0;
    if (card.questionOrder === "fixed") {
        taskIndex = hasStored ? stored : 0;
    } else {
        taskIndex = hasStored && !refreshVariant
            ? stored
            : Math.floor(Math.random() * tasks.length);
    }

    state.view.taskIndexByCard[card.id] = taskIndex;
    saveViewState();
    return { task: tasks[taskIndex], taskIndex };
}

function buildDisplayCard(card, task) {
    const fragen = Array.isArray(task?.fragen) ? task.fragen : [];
    const antworten = Array.isArray(task?.antworten) ? task.antworten : [];
    const einleitung = task?.einleitung || "";

    if (card.mode === "single-index") {
        const idx = card.index;
        return {
            einleitung,
            fragen: [fragen[idx] || ""],
            antworten: [antworten[idx] || ""],
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
        ? `<div class="dev-fc-intro">${displayCard.einleitung}</div>`
        : "";
    const fragen = hasMultiple
        ? `<ol class="dev-fc-list">${displayCard.fragen.map((f) => `<li>${f}</li>`).join("")}</ol>`
        : `<div class="dev-fc-text">${displayCard.fragen[0] || ""}</div>`;

    return `
        <div class="dev-fc-scroll">
            ${intro}
            ${fragen}
        </div>
    `;
}

function buildBackHtml(displayCard) {
    const hasQuestions = displayCard.fragen.length > 1;
    const intro = displayCard.einleitung
        ? `<div class="dev-fc-intro">${displayCard.einleitung}</div>`
        : "";
    const fragen = hasQuestions
        ? `<ol class="dev-fc-list">${displayCard.fragen.map((f) => `<li>${f}</li>`).join("")}</ol>`
        : `<div class="dev-fc-text">${displayCard.fragen[0] || ""}</div>`;

    const cleaned = displayCard.antworten.map((a) => cleanupAnswer(a));
    const hasMultiple = cleaned.length > 1;
    const antworten = hasMultiple
        ? `<ol class="dev-fc-list dev-fc-answer-tone">${cleaned.map((a) => `<li>${a}</li>`).join("")}</ol>`
        : `<div class="dev-fc-text dev-fc-answer-tone">${cleaned[0] || ""}</div>`;

    return `
        <div class="dev-fc-scroll">
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
    return Boolean(target.closest("button, a, input, select, textarea, [data-grade], #dev-fc-reset"));
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

function syncCardViewportHeight() {
    const bodyNode = state.root?.querySelector(".dev-fc-body");
    const cardNode = state.root?.querySelector("#dev-fc-card");
    const innerNode = state.root?.querySelector("#dev-fc-inner");
    const ratingNode = state.root?.querySelector("#dev-fc-rating");
    const frontNode = state.root?.querySelector("#dev-fc-front");
    const backNode = state.root?.querySelector("#dev-fc-back");
    if (!bodyNode || !cardNode || !innerNode || !ratingNode) return;

    const measureFaceHeight = (faceNode) => {
        if (!faceNode) return 0;
        const style = window.getComputedStyle(faceNode);
        const paddingTop = Number.parseFloat(style.paddingTop || "0") || 0;
        const paddingBottom = Number.parseFloat(style.paddingBottom || "0") || 0;
        const scrollNode = faceNode.querySelector(".dev-fc-scroll");
        const contentHeight = scrollNode ? scrollNode.scrollHeight : faceNode.scrollHeight;
        return Math.ceil(contentHeight + paddingTop + paddingBottom);
    };

    const bodyRect = bodyNode.getBoundingClientRect();
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
    const bottomSafeSpace = 26;
    const available = Math.max(220, viewportHeight - bodyRect.top - bottomSafeSpace);
    const ratingHeight = ratingNode.offsetHeight || 0;
    const verticalGap = 30;
    const maxCardHeight = Math.max(220, available - ratingHeight - verticalGap);

    const isFlipped = cardNode.classList.contains("is-flipped");
    const frontSafetyBuffer = 8;
    const backSafetyBuffer = 4;

    const contentNeeded = Math.max(
        measureFaceHeight(frontNode) + frontSafetyBuffer,
        measureFaceHeight(backNode) + backSafetyBuffer,
        260
    );

    // On the front side we keep a tiny extra buffer to prevent 1-2px phantom scrollbars.
    const activeFaceBuffer = isFlipped ? backSafetyBuffer : frontSafetyBuffer;
    const cardHeight = Math.min(contentNeeded + activeFaceBuffer, maxCardHeight);

    cardNode.style.height = `${cardHeight}px`;
    cardNode.style.maxHeight = `${maxCardHeight}px`;
    innerNode.style.height = `${cardHeight}px`;
    innerNode.style.maxHeight = `${maxCardHeight}px`;

    const setScrollState = (faceNode) => {
        const scrollNode = faceNode?.querySelector(".dev-fc-scroll");
        if (!scrollNode) return;
        const overflowDelta = scrollNode.scrollHeight - scrollNode.clientHeight;
        const hasRealOverflow = overflowDelta > 3;
        scrollNode.classList.toggle("is-no-scroll", !hasRealOverflow);
    };

    setScrollState(frontNode);
    setScrollState(backNode);
}

function insertVisualIntoFace(faceNode, task) {
    if (!faceNode || !task?.visual) return;

    const visualWrap = document.createElement("div");
    visualWrap.className = "dev-fc-visual";

    const scrollNode = faceNode.querySelector(".dev-fc-scroll");
    const introNode = scrollNode?.querySelector(".dev-fc-intro") || null;

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

async function renderCurrentCard(card, options = {}) {
    const { refreshVariant = false } = options;

    const cardNode = state.root.querySelector("#dev-fc-card");
    const innerNode = state.root.querySelector("#dev-fc-inner");
    const frontNode = state.root.querySelector("#dev-fc-front");
    const backNode = state.root.querySelector("#dev-fc-back");
    const ratingNode = state.root.querySelector("#dev-fc-rating");
    if (!cardNode || !innerNode || !frontNode || !backNode) return;

    const { task } = getTaskForCard(card, refreshVariant);
    const displayCard = buildDisplayCard(card, task);

    state.currentCard = card;
    state.view.currentCardId = card.id;
    saveViewState();

    cardNode.classList.remove("is-flipped");
    cardNode.setAttribute("aria-pressed", "false");
    ratingNode?.classList.remove("is-active");

    frontNode.innerHTML = buildFrontHtml(displayCard);
    backNode.innerHTML = buildBackHtml(displayCard);

    insertVisualIntoFace(frontNode, task);
    insertVisualIntoFace(backNode, task);

    await renderMath(innerNode);
    requestAnimationFrame(() => {
        resizePlotlyInNode(innerNode);
        syncCardViewportHeight();
    });
    updateCounterAndMessage();
}

function flipCurrentCard() {
    const cardNode = state.root.querySelector("#dev-fc-card");
    const ratingNode = state.root.querySelector("#dev-fc-rating");
    if (!cardNode) return;

    cardNode.classList.toggle("is-flipped");
    const isFlipped = cardNode.classList.contains("is-flipped");
    cardNode.setAttribute("aria-pressed", isFlipped ? "true" : "false");
    ratingNode?.classList.toggle("is-active", isFlipped);

    // Re-sync after flip animation/layout changes to avoid transient phantom scrollbars.
    requestAnimationFrame(() => {
        resizePlotlyInNode(cardNode, 2);
        syncCardViewportHeight();
    });
}

async function rateCurrentCard(grade) {
    if (!state.currentCard) return;
    const cardId = state.currentCard.id;
    const now = Date.now();
    const current = getCardState(cardId);

    let reps = current.reps || 0;
    let interval = current.interval || 0;
    let ease = current.ease || 2.5;

    if (grade < 3) {
        reps = 0;
        interval = 1;
    } else {
        reps += 1;
        if (reps === 1) {
            interval = 1;
        } else if (reps === 2) {
            interval = 6;
        } else {
            interval = Math.max(1, Math.round(interval * ease));
        }
    }

    const delta = 0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02);
    ease = Math.max(1.3, ease + delta);
    const due = now + interval * msPerDay;

    setCardState(cardId, { reps, interval, ease, due });

    const next = chooseNextCard();
    if (next) {
        await renderCurrentCard(next, { refreshVariant: true });
    }
}

async function resetProgress() {
    const confirmed = window.confirm("Fortschritt wirklich loeschen?");
    if (!confirmed) return;

    state.progress = {};
    saveProgress();

    const next = chooseInitialCard(state.cards);
    if (next) {
        await renderCurrentCard(next, { refreshVariant: true });
    }
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
                const count = Array.isArray(task?.fragen) ? task.fragen.length : 0;
                return Math.max(max, count);
            }, 0);

            for (let index = 0; index < maxQuestions; index += 1) {
                cards.push({
                    id: `${checkId}::single::${index}`,
                    checkId,
                    check,
                    mode: "single-index",
                    index,
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
    const cardNode = state.root.querySelector("#dev-fc-card");
    const resetBtn = state.root.querySelector("#dev-fc-reset");

    cardNode?.addEventListener("click", (event) => {
        if (shouldIgnoreFlipTarget(event.target)) return;
        flipCurrentCard();
    }, { capture: true });

    cardNode?.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        flipCurrentCard();
    });

    resetBtn?.addEventListener("click", () => {
        void resetProgress();
    });

    const ratingButtons = Array.from(state.root.querySelectorAll(".dev-fc-rate"));
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
    const body = state.root.querySelector(".dev-check-card__body");
    if (!body) return;
    body.innerHTML = `<p class="dev-fc-message-static">${text}</p>`;
}

export async function initFlashcardsModule({ root, lernbereich, preferredCheckId = "" }) {
    state.root = root;
    state.lernbereich = lernbereich || "";

    if (!state.lernbereich) {
        renderInfo("Kein Lernbereich gesetzt.");
        return;
    }

    const checks = await getChecksByLernbereich(state.lernbereich);
    if (!checks.length) {
        renderInfo(`Keine Checks fuer Lernbereich \"${state.lernbereich}\" gefunden.`);
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
        })
    );

    state.cards = buildCards(checksWithTasks);
    if (!state.cards.length) {
        renderInfo("Keine Flashcards gefunden.");
        return;
    }

    loadProgress();
    loadViewState();
    bindEvents();

    if (!state.hasResizeBinding) {
        const onResize = () => syncCardViewportHeight();
        window.addEventListener("resize", onResize);
        state.hasResizeBinding = true;
    }

    const next = chooseInitialCard(state.cards, preferredCheckId);
    if (next) {
        await renderCurrentCard(next, { refreshVariant: true });
    }
}
