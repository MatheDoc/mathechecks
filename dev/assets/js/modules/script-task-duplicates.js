import { getChecksByLernbereich } from "../data/checks-repo.js";
import { getAufgabenSammlung } from "../data/sammlungen-repo.js";
import {
    loadTrainingState,
    loadTaskIndexForCheck,
    saveTaskIndexForCheck,
} from "../state/check-state-store.js";
import { buildTaskUiStateKey } from "../state/task-ui-state.js";
import { shuffleQuestionsInTask } from "../utils/task-order.js";
import { renderTask as renderRuntimeTask } from "../../../../aufgaben/runtime/task-render.js";
import { createCheckMetaRowNode, formatCheckNumber } from "./ui/check-meta.js";
import { createCardActionsMenu, createCardMenuItem, createCardMenuLink } from "./ui/card-actions-menu.js";
import {
    buildSkriptTippsHref,
    buildTrainingKiAgentPrompt,
    copyTrainingPromptToClipboard,
    fetchTrainingBeispielHtml,
} from "./training.js";

async function renderMath(targetNode, retries = 4) {
    if (!targetNode) return;

    const mathJax = window.MathJax;
    if (mathJax && typeof mathJax.typesetPromise === "function") {
        try {
            await mathJax.typesetPromise([targetNode]);
        } catch {
            // Formula parsing issues should not block task rendering.
        }
        return;
    }

    if (retries <= 0) return;
    await new Promise((resolve) => setTimeout(resolve, 120));
    await renderMath(targetNode, retries - 1);
}

async function resizePlotlyInNode(targetNode, retries = 4) {
    if (!targetNode || !window.Plotly?.Plots?.resize) return;

    const plots = Array.from(targetNode.querySelectorAll(".js-plotly-plot"));
    plots.forEach((plotNode) => {
        try {
            window.Plotly.Plots.resize(plotNode);
        } catch {
            // Try again while the surrounding layout settles.
        }
    });

    if (retries <= 0) return;
    await new Promise((resolve) => setTimeout(resolve, 120));
    await resizePlotlyInNode(targetNode, retries - 1);
}

async function finalizeTaskRender(targetNode) {
    await renderMath(targetNode);
    await new Promise((resolve) => requestAnimationFrame(resolve));
    await resizePlotlyInNode(targetNode);
}

function getCheckId(check) {
    if (typeof check?.check_id === "string" && check.check_id.trim()) {
        return check.check_id;
    }

    const gebiet = check?.Gebiet || "gebiet";
    const lernbereich = check?.Lernbereich || "lernbereich";
    const nummer = String(Number(check?.Nummer) || 0).padStart(2, "0");
    return `${gebiet}__${lernbereich}__${nummer}`;
}

function pickRandomTaskIndex(currentIndex, totalCount) {
    if (!Number.isInteger(totalCount) || totalCount <= 0) {
        return 0;
    }

    if (totalCount === 1) {
        return 0;
    }

    let nextIndex = currentIndex;
    while (nextIndex === currentIndex) {
        nextIndex = Math.floor(Math.random() * totalCount);
    }
    return nextIndex;
}

function normalizeLookupKey(value) {
    return String(value ?? "").trim().toLowerCase();
}

function buildLookupKeys(check) {
    const keys = new Set();
    const checkId = getCheckId(check);
    const skriptAnchor = String(check?.skript_anchor || "");
    const nummer = String(Number(check?.Nummer) || 0).padStart(2, "0");

    keys.add(checkId);
    keys.add(checkId.replace(/__/g, "-"));

    if (skriptAnchor) {
        keys.add(skriptAnchor);
        keys.add(skriptAnchor.replace(/^check-/, ""));
    }

    keys.add(nummer);
    keys.add(String(Number(check?.Nummer) || 0));

    return Array.from(keys)
        .map((key) => normalizeLookupKey(key))
        .filter(Boolean);
}

function findCheckForNote(noteNode, checksByLookupKey) {
    const candidates = [
        noteNode?.dataset?.check || "",
        noteNode?.dataset?.key || "",
        noteNode?.id || "",
        String(noteNode?.id || "").replace(/^check-/, ""),
    ];

    for (const candidate of candidates) {
        const key = normalizeLookupKey(candidate);
        if (!key) continue;
        const matched = checksByLookupKey.get(key);
        if (matched) return matched;
    }

    return null;
}

function createEmptyTaskCard(check) {
    const card = document.createElement("article");
    card.className = "dev-check-card dev-check-card--training";

    const header = document.createElement("div");
    header.className = "dev-check-card__header";

    const headerLeft = createCheckMetaRowNode(
        {
            numberText: formatCheckNumber(check?.Nummer),
            titleText: check.Schlagwort || check["Ich kann"] || `Check ${check.Nummer}`,
            prefix: "Aufgabe",
            tone: "training",
            rowClass: "dev-check-card__header-left",
            titleTag: "span",
        }
    );

    const headerRight = document.createElement("div");
    headerRight.className = "dev-check-card__header-actions";

    const { menu: actionsMenu, popover: actionsPopover } = createCardActionsMenu();
    headerRight.appendChild(actionsMenu);

    const skriptTippsHref = buildSkriptTippsHref(check);
    if (skriptTippsHref) {
        actionsPopover.appendChild(createCardMenuLink({ emoji: "❓", label: "Hilfe", href: skriptTippsHref }));
    }

    header.appendChild(headerLeft);
    header.appendChild(headerRight);
    card.appendChild(header);

    const body = document.createElement("div");
    body.className = "dev-check-card__body";
    body.textContent = "Keine Aufgabe in dieser Sammlung gefunden.";
    card.appendChild(body);

    return card;
}

function createTaskCard(
    check,
    aufgabe,
    taskUiStateKey,
    readPersistedState = true,
    taskIndex = 0,
    totalTasks = 0
) {
    if (!aufgabe) return createEmptyTaskCard(check);

    const titel = check.Schlagwort || check["Ich kann"] || `Check ${check.Nummer}`;
    const card = document.createElement("article");
    card.className = "dev-check-card dev-check-card--training";

    const header = document.createElement("div");
    header.className = "dev-check-card__header";

    const headerLeft = createCheckMetaRowNode(
        {
            numberText: formatCheckNumber(check?.Nummer),
            titleText: titel,
            prefix: "Aufgabe",
            tone: "training",
            rowClass: "dev-check-card__header-left",
            titleTag: "span",
        }
    );

    const headerRight = document.createElement("div");
    headerRight.className = "dev-check-card__header-actions";

    const { menu: actionsMenu, popover: actionsPopover } = createCardActionsMenu();
    headerRight.appendChild(actionsMenu);

    const skriptTippsHref = buildSkriptTippsHref(check);
    if (skriptTippsHref) {
        actionsPopover.appendChild(createCardMenuLink({ emoji: "❓", label: "Hilfe", href: skriptTippsHref }));
    }

    header.appendChild(headerLeft);
    header.appendChild(headerRight);
    card.appendChild(header);

    const body = document.createElement("div");
    body.className = "dev-check-card__body";
    card.appendChild(body);

    const effectiveAufgabe =
        check?.questionOrder === "shuffle" ? shuffleQuestionsInTask(aufgabe, taskUiStateKey) : aufgabe;

    let runtimeTaskNode = null;

    const aiAgentItem = createCardMenuItem({
        emoji: "✨",
        label: "KI-Erkläragent",
        onClick: async () => {
            aiAgentItem.disabled = true;
            try {
                const beispielHtml = await fetchTrainingBeispielHtml(check);
                const prompt = buildTrainingKiAgentPrompt({
                    check,
                    task: effectiveAufgabe,
                    taskIndex,
                    totalTasks,
                    runtimeTaskNode,
                    beispielHtml,
                });
                await copyTrainingPromptToClipboard(prompt);
            } finally {
                aiAgentItem.disabled = false;
            }
        },
    });
    actionsPopover.appendChild(aiAgentItem);

    runtimeTaskNode = renderRuntimeTask(
        effectiveAufgabe,
        {
            index: 0,
            showSolution: false,
            showTaskHeading: false,
            containerClass: "dev-check-card__runtime-task",
            interaction: {
                enablePerQuestionCheck: true,
                enableReload: true,
                enableSolutionToggle: true,
                enableScriptInfoLink: false,
                statePersistenceKey: taskUiStateKey,
                readPersistedState,
            },
        }
    );
    body.appendChild(runtimeTaskNode);

    const runtimeToolbar = runtimeTaskNode.querySelector(".task-toolbar");
    const runtimeActionButtons = runtimeTaskNode.querySelectorAll(".task-toolbar__actions .task-toolbar-btn");
    const runtimeSolutionBtn = Array.from(runtimeActionButtons).find((button) => {
        const label = `${button.getAttribute("aria-label") || ""} ${button.title || ""}`.toLowerCase();
        return label.includes("loesung") || label.includes("lösung");
    });
    const runtimeReloadBtn = Array.from(runtimeActionButtons).find((button) => {
        const label = `${button.getAttribute("aria-label") || ""} ${button.title || ""}`.toLowerCase();
        return label.includes("neue aufgabe");
    });

    if (runtimeSolutionBtn) {
        const isHidden = () => {
            const label = (runtimeSolutionBtn.getAttribute("aria-label") || runtimeSolutionBtn.title || "").toLowerCase();
            return label.includes("ausblenden");
        };

        const solutionItem = createCardMenuItem({
            emoji: "👁️",
            label: isHidden() ? "Lösungen ausblenden" : "Lösungen anzeigen",
            onClick: () => {
                runtimeSolutionBtn.click();
                const labelSpan = solutionItem.querySelector("span:last-child");
                if (labelSpan) labelSpan.textContent = isHidden() ? "Lösungen ausblenden" : "Lösungen anzeigen";
            },
        });
        actionsPopover.appendChild(solutionItem);
    }

    if (runtimeReloadBtn) {
        actionsPopover.appendChild(createCardMenuItem({
            emoji: "🔄",
            label: "Neue Aufgabe",
            onClick: () => runtimeReloadBtn.click(),
        }));
    }

    if (runtimeToolbar) {
        runtimeToolbar.remove();
    }

    return card;
}

function upsertTaskHostAfter(noteNode) {
    const next = noteNode.nextElementSibling;
    if (next?.classList?.contains("mc-note-task")) {
        next.innerHTML = "";
        return next;
    }

    const host = document.createElement("section");
    host.className = "mc-note-task";
    noteNode.insertAdjacentElement("afterend", host);
    return host;
}

async function renderCheckTaskInHost(host, check, { lernbereich, usePersistedState, taskIndexByCheckId }) {
    try {
        const sammlung = await getAufgabenSammlung(check.Sammlung, {
            gebiet: check.Gebiet,
            lernbereich: check.Lernbereich,
        });

        const checkId = getCheckId(check);
        let taskIndex = usePersistedState
            ? loadTaskIndexForCheck(
                lernbereich,
                checkId,
                Number.isInteger(taskIndexByCheckId[checkId]) ? taskIndexByCheckId[checkId] : 0
            )
            : Number.isInteger(taskIndexByCheckId[checkId])
                ? taskIndexByCheckId[checkId]
                : 0;

        if (!Array.isArray(sammlung) || sammlung.length === 0) {
            taskIndex = 0;
        } else if (taskIndex < 0 || taskIndex >= sammlung.length) {
            taskIndex = 0;
        }

        const renderTaskCardForIndex = async (nextTaskIndex) => {
            const normalizedTaskIndex = Number.isInteger(nextTaskIndex) ? nextTaskIndex : 0;
            const aufgabe = Array.isArray(sammlung) ? sammlung[normalizedTaskIndex] || null : null;
            const taskUiStateKey = buildTaskUiStateKey({
                lernbereich,
                checkId,
                taskIndex: normalizedTaskIndex,
            });

            host.innerHTML = "";
            const card = createTaskCard(
                check,
                aufgabe,
                taskUiStateKey,
                usePersistedState,
                normalizedTaskIndex,
                Array.isArray(sammlung) ? sammlung.length : 0
            );
            host.appendChild(card);

            const runtimeRoot = host.querySelector(".dev-check-card__runtime-task");
            if (runtimeRoot) {
                runtimeRoot.addEventListener("task:reload", async () => {
                    const nextRandomIndex = pickRandomTaskIndex(
                        normalizedTaskIndex,
                        Array.isArray(sammlung) ? sammlung.length : 0
                    );
                    saveTaskIndexForCheck(lernbereich, checkId, nextRandomIndex);
                    await renderTaskCardForIndex(nextRandomIndex);
                });
            }

            await finalizeTaskRender(host);
        };

        await renderTaskCardForIndex(taskIndex);
    } catch (error) {
        const message = document.createElement("p");
        message.className = "dev-module__status";
        message.style.color = "var(--rose)";
        message.textContent = error?.message || "Aufgabe konnte nicht geladen werden.";
        host.appendChild(message);
    }
}

export async function initScriptTaskDuplicatesModule({
    root,
    lernbereich,
    usePersistedState = true,
}) {
    if (!root || !lernbereich) return;

    const noteNodes = Array.from(root.querySelectorAll(".mc-note[data-check], .mc-note[data-key]"));
    const ankerNodes = Array.from(root.querySelectorAll(".check-anker[data-nummer]"));
    if (noteNodes.length === 0 && ankerNodes.length === 0) return;

    const checks = await getChecksByLernbereich(lernbereich);
    if (!Array.isArray(checks) || checks.length === 0) return;

    const checksByLookupKey = new Map();
    checks.forEach((check) => {
        buildLookupKeys(check).forEach((lookupKey) => {
            if (!checksByLookupKey.has(lookupKey)) {
                checksByLookupKey.set(lookupKey, check);
            }
        });
    });

    const trainingState = loadTrainingState(lernbereich);
    const taskIndexByCheckId =
        trainingState?.taskIndexByCheckId && typeof trainingState.taskIndexByCheckId === "object"
            ? trainingState.taskIndexByCheckId
            : {};

    const opts = { lernbereich, usePersistedState, taskIndexByCheckId };

    await Promise.all(
        noteNodes.map(async (noteNode) => {
            const check = findCheckForNote(noteNode, checksByLookupKey);
            if (!check) return;

            const host = upsertTaskHostAfter(noteNode);
            await renderCheckTaskInHost(host, check, opts);
        })
    );

    await Promise.all(
        ankerNodes.map(async (ankerNode) => {
            const nummer = normalizeLookupKey(ankerNode.dataset.nummer);
            const check = checksByLookupKey.get(nummer);
            if (!check) return;

            const host = ankerNode.querySelector(".check-anker__aufgabe");
            if (!host) return;

            await renderCheckTaskInHost(host, check, opts);
        })
    );
}
