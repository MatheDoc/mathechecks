import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";
import { getAufgabenSammlung } from "../data/sammlungen-repo.js?v=20260614-expression-curves-b";
import {
    loadTrainingState,
    loadTaskIndexForCheck,
    saveTaskIndexForCheck,
    loadShuffleNonce,
    saveShuffleNonce,
    loadTrainingFeedTaskIndexForCheck,
    saveTrainingFeedTaskIndexForCheck,
    loadTrainingFeedShuffleNonce,
    saveTrainingFeedShuffleNonce,
} from "../state/check-state-store.js?v=20260516-feed-confirm";
import { buildTaskUiStateKey } from "../state/task-ui-state.js?v=20260516-feed-confirm";
import { shuffleQuestionsInTask } from "../utils/task-order.js";
import { renderTask as renderRuntimeTask } from "../../../../aufgaben/runtime/task-render.js?v=20260711-speech-textarea-fix";
import { createCardMenuItem, runCardMenuItemFeedbackAction } from "./ui/card-actions-menu.js";
import { attachFreeCompletionControl } from "./ui/feed-card-controls.js?v=20260701-shared-client";
import { enhanceSpeechInputs } from "./ui/speech-input.js?v=20260711-speech-textarea-fix";
import { recordUserActivity, getUserCheckProficiency, extractCheckProficiencyRate } from "../platform/progress-client.js?v=20260608-quote-perq";
import { showTaskCompletionPopup } from "./ui/task-completion-popup.js?v=20260609-void-revealed";
import {
    attachTrainingFeedShell,
    buildTrainingKiAgentPrompt,
    createTrainingCardHeader,
    updateCheckRateBadge,
    copyTrainingPromptToClipboard,
    fetchTrainingBeispielHtml,
} from "./training.js?v=20260614-expression-curves-b";

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
    enhanceSpeechInputs(targetNode);
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

async function recordTrainingTaskCompletion({
    lernbereich,
    checkId,
    taskIndex,
    checkableCount,
    revealedCount,
    questionAttempts,
    solutionsRevealedGlobally,
    contextKey = "free",
}) {
    const before = await getUserCheckProficiency();
    const previousRate = before.ok ? extractCheckProficiencyRate(before.data, checkId) : null;

    if (solutionsRevealedGlobally) {
        return { previousRate, newRate: previousRate, quoteUnchanged: true };
    }

    await recordUserActivity({
        activityType: "training",
        lernbereichSlug: lernbereich,
        checkId,
        contextKey,
        details: {
            taskIndex,
            checkable_count: checkableCount,
            question_attempts: Array.isArray(questionAttempts) ? questionAttempts : [],
            revealed_count: revealedCount,
        },
    });

    const after = await getUserCheckProficiency();
    const newRate = after.ok ? extractCheckProficiencyRate(after.data, checkId) : null;
    return { previousRate, newRate };
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

function isTrainingFeedStep(activityStep) {
    const normalized = String(activityStep || "").trim();
    return normalized === "training" || /^training_\d+$/.test(normalized);
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
    card.className = "check-card check-card--training";

    const { header } = createTrainingCardHeader(check);
    card.appendChild(header);

    const body = document.createElement("div");
    body.className = "check-card__body";
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
    totalTasks = 0,
    shuffleSeed = ""
) {
    if (!aufgabe) return createEmptyTaskCard(check);

    const titel = check.Schlagwort || check["Ich kann"] || `Check ${check.Nummer}`;
    const card = document.createElement("article");
    card.className = "check-card check-card--training";

    const { header, actionsPopover } = createTrainingCardHeader(check, titel);
    card.appendChild(header);

    const body = document.createElement("div");
    body.className = "check-card__body";
    card.appendChild(body);

    const effectiveAufgabe =
        check?.questionOrder === "shuffle" ? shuffleQuestionsInTask(aufgabe, shuffleSeed || taskUiStateKey) : aufgabe;

    let runtimeTaskNode = null;

    const aiAgentItem = createCardMenuItem({
        emoji: "✨",
        label: "KI-Erkläragent kopieren",
        closeOnClick: false,
        onClick: async () => {
            await runCardMenuItemFeedbackAction(aiAgentItem, {
                pendingLabel: "Wird erstellt…",
                successLabel: "Kopiert!",
                errorLabel: "Fehler",
                pendingIcon: "✨",
                action: async () => {
                    const beispielHtml = await fetchTrainingBeispielHtml(check);
                    const prompt = buildTrainingKiAgentPrompt({
                        check,
                        task: effectiveAufgabe,
                        taskIndex,
                        totalTasks,
                        runtimeTaskNode,
                        beispielHtml,
                    });
                    return copyTrainingPromptToClipboard(prompt);
                },
            });
        },
    });
    actionsPopover.appendChild(aiAgentItem);

    runtimeTaskNode = renderRuntimeTask(
        effectiveAufgabe,
        {
            index: 0,
            showSolution: false,
            showTaskHeading: false,
            containerClass: "check-card__runtime-task",
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
        solutionItem.dataset.trainingFeedControlled = "true";
        actionsPopover.appendChild(solutionItem);
    }

    if (runtimeReloadBtn) {
        const reloadItem = createCardMenuItem({
            emoji: "🔄",
            label: "Neue Aufgabe",
            onClick: () => runtimeReloadBtn.click(),
        });
        reloadItem.dataset.trainingFeedControlled = "true";
        actionsPopover.appendChild(reloadItem);
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

async function renderCheckTaskInHost(host, check, {
    lernbereich,
    usePersistedState,
    taskIndexByCheckId,
    activityContext = null,
    preferredCheckId = "",
}) {
    try {
        const sammlung = await getAufgabenSammlung(check.Sammlung, {
            gebiet: check.Gebiet,
            lernbereich: check.Lernbereich,
        });

        const checkId = getCheckId(check);
        const isActiveFeedTraining =
            activityContext?.mode === "feed" &&
            isTrainingFeedStep(activityContext?.activityStep) &&
            (!preferredCheckId || preferredCheckId === checkId);
        const isFreeMode = !isActiveFeedTraining;
        const totalTaskCount = Array.isArray(sammlung) ? sammlung.length : 0;
        const trackingLernbereich = check.Lernbereich || lernbereich || "";
        const feedActivityKey = isActiveFeedTraining ? String(activityContext?.activityKey || "").trim() : "";
        const sharedTaskIndex = Number.isInteger(taskIndexByCheckId[checkId])
            ? loadTaskIndexForCheck(lernbereich, checkId, taskIndexByCheckId[checkId])
            : loadTaskIndexForCheck(lernbereich, checkId, 0);
        const fallbackTaskIndex = isActiveFeedTraining
            ? pickRandomTaskIndex(sharedTaskIndex, totalTaskCount)
            : sharedTaskIndex;
        let taskIndex = isActiveFeedTraining && feedActivityKey
            ? loadTrainingFeedTaskIndexForCheck(lernbereich, checkId, feedActivityKey, fallbackTaskIndex)
            : usePersistedState
                ? loadTaskIndexForCheck(lernbereich, checkId, fallbackTaskIndex)
                : fallbackTaskIndex;

        if (!Array.isArray(sammlung) || sammlung.length === 0) {
            taskIndex = 0;
        } else if (taskIndex < 0 || taskIndex >= sammlung.length) {
            taskIndex = 0;
        }

        host.dataset.checkId = checkId;
        host.dataset.lernbereich = check.Lernbereich || lernbereich || "";

        let shuffleNonce = isActiveFeedTraining && feedActivityKey
            ? loadTrainingFeedShuffleNonce(lernbereich, checkId, feedActivityKey)
            : loadShuffleNonce(lernbereich, checkId);
        if (!shuffleNonce) {
            shuffleNonce = String(Date.now());
        }

        let taskCompletionTracked = false;
        let initialProgressSeen = false;
        let freeCompleteControl = null;
        let freeCompleteReady = false;
        let latestRates = null;

        const attachFreeCompleteControl = () => {
            if (!isFreeMode || totalTaskCount <= 0) return;
            freeCompleteControl = attachFreeCompletionControl(host, {
                cardSelector: ".check-card--training",
                stepLabel: "Training",
                onComplete: () => {
                    void openFreeCompletionPopup();
                },
            });
            if (freeCompleteControl) freeCompleteControl.setReady(freeCompleteReady);
        };

        const markFreeCompleteReady = () => {
            if (!isFreeMode) return;
            freeCompleteReady = true;
            if (freeCompleteControl) freeCompleteControl.setReady(true);
        };

        const openFreeCompletionPopup = async () => {
            let rates = latestRates;
            if (!rates) {
                const proficiency = await getUserCheckProficiency();
                const newRate = proficiency.ok ? extractCheckProficiencyRate(proficiency.data, checkId) : null;
                rates = { previousRate: null, newRate };
            }

            showTaskCompletionPopup({
                mode: "training",
                showQuote: true,
                quoteUnchanged: Boolean(rates.quoteUnchanged),
                previousRate: rates.previousRate,
                newRate: rates.newRate,
                onRepeat: () => {
                    void reloadTask();
                },
                onDashboard: () => window.location.assign("/dashboard.html"),
            });
        };

        const saveCurrentTaskIndex = (nextTaskIndex) => {
            if (isActiveFeedTraining && feedActivityKey) {
                saveTrainingFeedTaskIndexForCheck(lernbereich, checkId, feedActivityKey, nextTaskIndex);
                return;
            }
            saveTaskIndexForCheck(lernbereich, checkId, nextTaskIndex);
        };

        const saveCurrentShuffleNonce = (nextNonce) => {
            if (isActiveFeedTraining && feedActivityKey) {
                saveTrainingFeedShuffleNonce(lernbereich, checkId, feedActivityKey, nextNonce);
                return;
            }
            saveShuffleNonce(lernbereich, checkId, nextNonce);
        };

        saveCurrentTaskIndex(taskIndex);
        saveCurrentShuffleNonce(shuffleNonce);

        const renderTaskCardForIndex = async (nextTaskIndex) => {
            const normalizedTaskIndex = Number.isInteger(nextTaskIndex) ? nextTaskIndex : 0;
            taskIndex = normalizedTaskIndex;
            const aufgabe = Array.isArray(sammlung) ? sammlung[normalizedTaskIndex] || null : null;
            const taskUiStateKey = buildTaskUiStateKey({
                lernbereich,
                checkId,
                taskIndex: normalizedTaskIndex,
                activityKey: isActiveFeedTraining ? activityContext?.activityKey || "" : "",
                activityStep: isActiveFeedTraining ? activityContext?.activityStep || "" : "",
                activityRun: isActiveFeedTraining ? activityContext?.activityRun || "" : "",
            });

            host.innerHTML = "";
            const card = createTaskCard(
                check,
                aufgabe,
                taskUiStateKey,
                usePersistedState,
                normalizedTaskIndex,
                totalTaskCount,
                `${taskUiStateKey}::${shuffleNonce}`
            );
            host.appendChild(card);

            const runtimeRoot = host.querySelector(".check-card__runtime-task");
            if (runtimeRoot) {
                runtimeRoot.addEventListener("task:reload", () => {
                    void reloadTask();
                });
            }

            await finalizeTaskRender(host);
            attachFreeCompleteControl();
        };

        const reloadTask = async () => {
            const nextRandomIndex = pickRandomTaskIndex(
                taskIndex,
                totalTaskCount
            );
            shuffleNonce = String(Date.now());
            taskCompletionTracked = false;
            initialProgressSeen = false;
            latestRates = null;
            freeCompleteReady = false;
            saveCurrentTaskIndex(nextRandomIndex);
            saveCurrentShuffleNonce(shuffleNonce);
            await renderTaskCardForIndex(nextRandomIndex);
            host.dispatchEvent(new CustomEvent("training:task-reloaded", { bubbles: true }));
        };

        if (isFreeMode) {
            host.addEventListener("task:question-checked", (event) => {
                const isComplete = Boolean(event.detail?.isComplete);

                if (!initialProgressSeen) {
                    initialProgressSeen = true;
                    if (isComplete) {
                        taskCompletionTracked = true;
                        markFreeCompleteReady();
                        return;
                    }
                }

                if (taskCompletionTracked || !isComplete) return;
                taskCompletionTracked = true;

                const detail = event.detail || {};
                Promise.resolve(
                    recordTrainingTaskCompletion({
                        lernbereich: trackingLernbereich,
                        checkId,
                        taskIndex,
                        checkableCount: Number(detail.checkableCount) || (Number(detail.totalCount) || 0),
                        revealedCount: Number(detail.revealedCount) || 0,
                        questionAttempts: Array.isArray(detail.questionAttempts) ? detail.questionAttempts : [],
                        solutionsRevealedGlobally: Boolean(detail.solutionsRevealedGlobally),
                        contextKey: "free",
                    })
                )
                    .then((rates) => {
                        if (rates && typeof rates === "object") {
                            latestRates = {
                                previousRate: rates.previousRate ?? null,
                                newRate: rates.newRate ?? null,
                                quoteUnchanged: Boolean(rates.quoteUnchanged),
                            };
                            // Badge sofort aktualisieren
                            const badge = host.querySelector(".check-card__rate-badge");
                            updateCheckRateBadge(badge, latestRates.newRate);
                        }
                        markFreeCompleteReady();
                    })
                    .catch(() => {
                        markFreeCompleteReady();
                    });
            });
        }

        if (host.dataset.boundTrainingReload !== "true") {
            host.dataset.boundTrainingReload = "true";
            host.addEventListener("training:reload-current-task", () => {
                void reloadTask();
            });
        }

        await renderTaskCardForIndex(taskIndex);

        if (isActiveFeedTraining) {
            attachTrainingFeedShell(host, { activityContext, checkId, lernbereich });
        }

        // Trainingsquote-Badge initial befüllen
        getUserCheckProficiency().then((proficiency) => {
            if (!proficiency.ok) return;
            const rate = extractCheckProficiencyRate(proficiency.data, checkId);
            const badge = host.querySelector(".check-card__rate-badge");
            updateCheckRateBadge(badge, rate);
        });
    } catch (error) {
        const message = document.createElement("p");
        message.className = "module-status";
        message.style.color = "var(--rose)";
        message.textContent = error?.message || "Aufgabe konnte nicht geladen werden.";
        host.appendChild(message);
    }
}

export async function initScriptTaskDuplicatesModule({
    root,
    lernbereich,
    usePersistedState = true,
    activityContext = null,
    preferredCheckId = "",
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

    const opts = { lernbereich, usePersistedState, taskIndexByCheckId, activityContext, preferredCheckId };

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
