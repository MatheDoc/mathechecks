import { answerToPreview, answerToSolution, evaluateAnswerFields } from "./answers.js";
import { renderVisual } from "./task-visuals.js?v=20260423-market-legends-a";

const TASK_UI_STATE_PREFIX = "dev-task-ui-state-v1::";
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

function getTaskUiStorageKey(stateKey) {
    return `${TASK_UI_STATE_PREFIX}${getTabScopeId()}::${stateKey}`;
}

function loadTaskUiState(stateKey) {
    if (!stateKey || typeof stateKey !== "string") return null;
    try {
        const raw = window.localStorage.getItem(getTaskUiStorageKey(stateKey));
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        if (!parsed || typeof parsed !== "object") return null;
        return parsed;
    } catch {
        return null;
    }
}

function saveTaskUiState(stateKey, state) {
    if (!stateKey || typeof stateKey !== "string") return;
    try {
        window.localStorage.setItem(getTaskUiStorageKey(stateKey), JSON.stringify(state));
    } catch {
        // Ignore quota/storage errors to keep task interaction usable.
    }
}

function readFieldUiState(field) {
    if (!field) return null;

    if (field.classList?.contains("answer-numopt-group")) {
        const input = field.querySelector(".answer-numopt-input");
        const checkbox = field.querySelector(".answer-numopt-none");
        return {
            tag: "numopt",
            value: input?.value ?? "",
            noneChecked: Boolean(checkbox?.checked),
        };
    }

    if (field instanceof HTMLSelectElement) {
        return { tag: "select", value: field.value };
    }

    if (field instanceof HTMLInputElement) {
        if (field.type === "checkbox" || field.type === "radio") {
            return { tag: "input", type: field.type, checked: Boolean(field.checked) };
        }
        return { tag: "input", type: field.type || "text", value: field.value ?? "" };
    }

    return { tag: "other", value: field.value ?? "" };
}

function applyFieldUiState(field, state) {
    if (!field || !state || typeof state !== "object") return;

    if (state.tag === "numopt" && field.classList?.contains("answer-numopt-group")) {
        const input = field.querySelector(".answer-numopt-input");
        const checkbox = field.querySelector(".answer-numopt-none");
        if (input && typeof state.value === "string") input.value = state.value;
        if (checkbox && typeof state.noneChecked === "boolean") {
            checkbox.checked = state.noneChecked;
            if (input) input.disabled = state.noneChecked;
        }
        return;
    }

    if (field instanceof HTMLSelectElement) {
        if (typeof state.value === "string") field.value = state.value;
        return;
    }

    if (field instanceof HTMLInputElement) {
        if (field.type === "checkbox" || field.type === "radio") {
            if (typeof state.checked === "boolean") field.checked = state.checked;
            return;
        }

        if (typeof state.value === "string") field.value = state.value;
        return;
    }

    if (typeof state.value === "string") {
        field.value = state.value;
    }
}

function setFeedback(node, message, variant = "neutral") {
    if (!node) return;
    node.textContent = message;
    node.classList.remove("is-correct", "is-incorrect", "is-neutral");
    if (variant === "correct") node.classList.add("is-correct");
    else if (variant === "incorrect") node.classList.add("is-incorrect");
    else node.classList.add("is-neutral");
}

function markPartStates(parts) {
    parts.forEach((part) => {
        if (!part.control) return;

        const select2Selection = part.control.matches?.("select")
            ? part.control
                .closest(".answer-field-group")
                ?.querySelector(".select2-container .select2-selection")
            : null;

        part.control.classList.remove("is-correct", "is-incorrect");
        select2Selection?.classList.remove("is-correct", "is-incorrect");
        if (!part.isComplete) return;

        const stateClass = part.isCorrect ? "is-correct" : "is-incorrect";
        part.control.classList.add(stateClass);
        select2Selection?.classList.add(stateClass);
    });
}

function renderSelect2OptionWithMath(data) {
    if (!data) return "";

    const encodedLatex = data.element?.getAttribute?.("data-latex") || "";
    const latexSource = encodedLatex ? decodeURIComponent(encodedLatex) : String(data.text || "");

    const span = document.createElement("span");
    span.textContent = latexSource;

    const queueTypeset = (retries = 12) => {
        const mathJax = window.MathJax;
        if (!mathJax || typeof mathJax.typesetPromise !== "function") {
            if (retries <= 0) return;
            setTimeout(() => queueTypeset(retries - 1), 80);
            return;
        }

        if (!span.isConnected) {
            if (retries <= 0) return;
            requestAnimationFrame(() => queueTypeset(retries - 1));
            return;
        }

        mathJax.typesetPromise([span]).catch(() => {
            // Keep dropdown usable if a formula fails to parse.
        });
    };

    requestAnimationFrame(() => queueTypeset());
    return span;
}

function measureTextWidthPx(text, font) {
    const span = document.createElement("span");
    span.textContent = text;
    span.style.position = "absolute";
    span.style.visibility = "hidden";
    span.style.whiteSpace = "nowrap";
    span.style.pointerEvents = "none";
    span.style.font = font || "inherit";
    document.body.appendChild(span);
    const width = span.getBoundingClientRect().width;
    span.remove();
    return width;
}

function getSelect2AvailableWidthPx(selectNode) {
    const fieldGroup = selectNode?.closest?.(".answer-field-group");
    if (!fieldGroup) return 260;

    const answerPreview = fieldGroup.closest(".answer-preview");
    const rowWidth = answerPreview?.clientWidth || 0;
    if (rowWidth <= 0) return 260;

    const groupRect = fieldGroup.getBoundingClientRect();
    const previewRect = answerPreview.getBoundingClientRect();
    const remaining = previewRect.right - groupRect.left - 30;
    return Math.max(100, Math.min(rowWidth, remaining));
}

function computeSelect2DesiredWidthPx(selectNode) {
    if (!selectNode) return 100;

    const selectionRendered = selectNode
        .closest(".answer-field-group")
        ?.querySelector(".select2-selection__rendered");
    const fontSource = selectionRendered || selectNode;
    const font = window.getComputedStyle(fontSource).font;

    let maxOptionWidth = measureTextWidthPx("Antwort", font);
    Array.from(selectNode.options || []).forEach((optionNode) => {
        const text = String(optionNode.textContent || "").trim();
        if (!text) return;
        maxOptionWidth = Math.max(maxOptionWidth, measureTextWidthPx(text, font));
    });

    const contentWidth = maxOptionWidth + 50;
    const availableWidth = getSelect2AvailableWidthPx(selectNode);
    return Math.max(100, Math.min(contentWidth, availableWidth));
}

function measureRenderedDropdownWidthPx() {
    const dropdownNode = document.querySelector(".select2-container--open .select2-dropdown.mc-select2-dropdown");
    if (!dropdownNode) return 0;
    return dropdownNode.scrollWidth || 0;
}

function applySelect2WidthPx(selectNode, widthPx) {
    const fieldGroup = selectNode?.closest?.(".answer-field-group");
    if (!fieldGroup) return;
    fieldGroup.style.setProperty("--mc-select-width", `${Math.round(widthPx)}px`);
}

function initializeSelect2ForDropdowns(rootNode) {
    if (!rootNode) return;

    const $ = window.jQuery || window.$;
    if (!$ || !$.fn || typeof $.fn.select2 !== "function") return;

    const selects = Array.from(rootNode.querySelectorAll("select"));
    selects.forEach((selectNode) => {
        const answerFieldGroup = selectNode.closest(".answer-field-group");
        if (answerFieldGroup) {
            answerFieldGroup.classList.add("answer-field-group--select2");
        }

        // Start compact and grow to the required width after interaction.
        applySelect2WidthPx(selectNode, 100);

        const $select = $(selectNode);
        if ($select.data("select2")) {
            $select.select2("destroy");
        }

        const $dropdownParent = $(document.body);

        $select.select2({
            placeholder: "Antwort",
            minimumResultsForSearch: Infinity,
            width: "100%",
            dropdownAutoWidth: false,
            dropdownCssClass: "mc-select2-dropdown",
            selectionCssClass: "mc-select2-selection",
            dropdownParent: $dropdownParent,
            templateResult: renderSelect2OptionWithMath,
            templateSelection: renderSelect2OptionWithMath,
        });

        if (selectNode.value) {
            applySelect2WidthPx(selectNode, computeSelect2DesiredWidthPx(selectNode));
        }

        $select.off(".adaptiveWidth");
        $select.on("select2:open.adaptiveWidth select2:select.adaptiveWidth", () => {
            applySelect2WidthPx(selectNode, computeSelect2DesiredWidthPx(selectNode));
        });

        $select.off(".mathjax");
        $select.on("select2:open.mathjax select2:select.mathjax select2:close.mathjax", () => {
            const mathJax = window.MathJax;
            if (!mathJax || typeof mathJax.typesetPromise !== "function") return;

            const nodes = [];
            const dropdownNode = document.querySelector(".select2-container--open .select2-results");
            const selectionNode = $select
                .next(".select2-container")
                .find(".select2-selection__rendered")
                .get(0);

            if (dropdownNode) nodes.push(dropdownNode);
            if (selectionNode) nodes.push(selectionNode);
            if (nodes.length === 0) return;

            mathJax.typesetPromise(nodes).then(() => {
                const dropdownWidth = measureRenderedDropdownWidthPx();
                if (dropdownWidth > 0) {
                    const currentWidth = computeSelect2DesiredWidthPx(selectNode);
                    if (dropdownWidth > currentWidth) {
                        applySelect2WidthPx(selectNode, dropdownWidth);
                    }
                }
            }).catch(() => {
                // Ignore rendering errors in single options.
            });
        });
    });
}

export function renderTask(task, options = {}) {
    const {
        index = 0,
        showSolution = false,
        showTaskHeading = true,
        containerClass = "task",
        headingPrefix = "Aufgabe",
        interaction = null,
    } = options;

    const interactionConfig = {
        enablePerQuestionCheck: true,
        enableReload: false,
        enableSolutionToggle: true,
        enableScriptInfoLink: false,
        scriptInfoHref: "",
        scriptInfoLabel: "Zur passenden Skript-Info",
        reloadLabel: "Neue Aufgabe",
        solutionToggleLabelShow: "Loesungen anzeigen",
        solutionToggleLabelHide: "Loesungen ausblenden",
        statePersistenceKey: "",
        readPersistedState: true,
        onReload: null,
        ...(interaction && typeof interaction === "object" ? interaction : {}),
    };

    const interactiveMode = Boolean(interaction);
    const persistenceKey =
        typeof interactionConfig.statePersistenceKey === "string"
            ? interactionConfig.statePersistenceKey.trim()
            : "";
    const shouldReadPersistedState = interactionConfig.readPersistedState !== false;
    const persistedState =
        persistenceKey && shouldReadPersistedState ? loadTaskUiState(persistenceKey) : null;

    const wrapper = document.createElement("article");
    wrapper.className = containerClass;

    const introColumn = document.createElement("div");
    introColumn.className = "task-intro-column";

    if (showTaskHeading) {
        const title = document.createElement("h2");
        title.textContent = `${headingPrefix} ${index + 1}`;
        wrapper.appendChild(title);
    }

    const intro = document.createElement("div");
    intro.className = "intro";
    intro.innerHTML = task?.einleitung ?? "";
    introColumn.appendChild(intro);

    renderVisual(task, introColumn);

    wrapper.appendChild(introColumn);

    const fragen = Array.isArray(task?.fragen) ? task.fragen : [];
    const antworten = Array.isArray(task?.antworten) ? task.antworten : [];
    const itemCount = Math.min(fragen.length, antworten.length);

    const qaList = document.createElement("ol");
    qaList.className = "qa-list";
    qaList.style.margin = "0";
    qaList.style.padding = "0";
    qaList.style.paddingInline = "0";
    qaList.style.paddingBlock = "0";

    const solutionNodes = [];
    const answerFields = [];
    const questionEvaluators = [];
    const checkedQuestionIndexes = new Set(
        Array.isArray(persistedState?.checkedQuestionIndexes)
            ? persistedState.checkedQuestionIndexes.filter((index) => Number.isInteger(index) && index >= 0)
            : []
    );
    let showSolutionsNow =
        typeof persistedState?.showSolutions === "boolean" ? persistedState.showSolutions : showSolution;

    const persistCurrentUiState = () => {
        if (!persistenceKey) return;
        const normalizedChecked = Array.from(checkedQuestionIndexes).sort((a, b) => a - b);
        saveTaskUiState(persistenceKey, {
            showSolutions: showSolutionsNow,
            checkedQuestionIndexes: normalizedChecked,
            inputs: answerFields.map((field) => readFieldUiState(field)),
        });
    };

    for (let i = 0; i < itemCount; i += 1) {
        const item = document.createElement("li");
        item.className = "qa-item";

        const frage = document.createElement("div");
        frage.className = "frage";
        frage.textContent = fragen[i];
        item.appendChild(frage);

        const answerPreview = document.createElement("div");
        answerPreview.className = "answer-preview";
        answerPreview.innerHTML = answerToPreview(antworten[i]);
        item.appendChild(answerPreview);

        const buildQuestionEvaluation = () => {
            const result = evaluateAnswerFields(antworten[i], answerPreview);
            markPartStates(result.parts);
            return result;
        };
        questionEvaluators[i] = buildQuestionEvaluation;

        if (interactiveMode && interactionConfig.enablePerQuestionCheck) {
            const fields = Array.from(answerPreview.querySelectorAll(".answer-input, .answer-select, .answer-numopt-group"));
            fields.forEach((field) => answerFields.push(field));

            fields.forEach((field) => {
                // NUMERICAL_OPT groups are already wrapped; wire up checkbox toggle
                if (field.classList.contains("answer-numopt-group")) {
                    const numoptInput = field.querySelector(".answer-numopt-input");
                    const numoptNone = field.querySelector(".answer-numopt-none");
                    if (numoptNone && numoptInput) {
                        numoptNone.addEventListener("change", () => {
                            numoptInput.disabled = numoptNone.checked;
                            if (numoptNone.checked) numoptInput.value = "";
                        });
                    }

                    const outerGroup = document.createElement("span");
                    outerGroup.className = "answer-field-group answer-field-group--numopt";
                    field.replaceWith(outerGroup);
                    outerGroup.appendChild(field);

                    const checkBtn = document.createElement("button");
                    checkBtn.type = "button";
                    checkBtn.className = "answer-check-btn";
                    checkBtn.setAttribute("aria-label", "Prüfen");
                    checkBtn.innerHTML = '<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><polyline points="1,5.5 4,8.5 10,2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
                    checkBtn.addEventListener("click", () => {
                        buildQuestionEvaluation();
                        if (persistenceKey) {
                            checkedQuestionIndexes.add(i);
                            persistCurrentUiState();
                        }
                    });
                    outerGroup.appendChild(checkBtn);
                    return;
                }

                const group = document.createElement("span");
                group.className = "answer-field-group";
                if (field.classList.contains("answer-input")) {
                    group.classList.add("answer-field-group--input");
                }
                field.replaceWith(group);
                group.appendChild(field);

                const checkBtn = document.createElement("button");
                checkBtn.type = "button";
                checkBtn.className = "answer-check-btn";
                checkBtn.setAttribute("aria-label", "Prüfen");
                checkBtn.innerHTML = '<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><polyline points="1,5.5 4,8.5 10,2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
                checkBtn.addEventListener("click", () => {
                    buildQuestionEvaluation();
                    if (persistenceKey) {
                        checkedQuestionIndexes.add(i);
                        persistCurrentUiState();
                    }
                });
                group.appendChild(checkBtn);
            });
        }

        if (showSolution || (interactiveMode && interactionConfig.enableSolutionToggle)) {
            const solution = document.createElement("div");
            solution.className = "solution";
            solution.innerHTML = answerToSolution(antworten[i]);
            if (!showSolutionsNow) {
                solution.hidden = true;
            }
            solutionNodes.push(solution);
            item.appendChild(solution);
        }

        qaList.appendChild(item);
    }

    wrapper.appendChild(qaList);

    if (interactiveMode) {
        const toolbar = document.createElement("header");
        toolbar.className = "task-toolbar";

        // Left side: stat chips (future use — e.g. attempt count, error rate)
        const statsSlot = document.createElement("div");
        statsSlot.className = "task-toolbar__stats";
        toolbar.appendChild(statsSlot);

        // Right side: action icon buttons
        const actions = document.createElement("div");
        actions.className = "task-toolbar__actions";

        if (interactionConfig.enableSolutionToggle && solutionNodes.length > 0) {
            const solutionBtn = document.createElement("button");
            solutionBtn.type = "button";
            solutionBtn.className = "task-toolbar-btn";

            const updateSolutionBtn = (visible) => {
                solutionBtn.innerHTML = visible
                    ? '<i class="fa-solid fa-eye-slash" aria-hidden="true"></i>'
                    : '<i class="fa-solid fa-eye" aria-hidden="true"></i>';
                solutionBtn.title = visible
                    ? interactionConfig.solutionToggleLabelHide
                    : interactionConfig.solutionToggleLabelShow;
                solutionBtn.setAttribute("aria-label", solutionBtn.title);
            };
            updateSolutionBtn(showSolutionsNow);

            solutionBtn.addEventListener("click", () => {
                showSolutionsNow = !showSolutionsNow;
                solutionNodes.forEach((node) => {
                    node.hidden = !showSolutionsNow;
                });
                updateSolutionBtn(showSolutionsNow);
                persistCurrentUiState();
            });
            actions.appendChild(solutionBtn);
        }

        if (interactionConfig.enableReload) {
            const reloadBtn = document.createElement("button");
            reloadBtn.type = "button";
            reloadBtn.className = "task-toolbar-btn";
            reloadBtn.title = interactionConfig.reloadLabel;
            reloadBtn.setAttribute("aria-label", interactionConfig.reloadLabel);
            reloadBtn.innerHTML = '<i class="fa-solid fa-rotate-right" aria-hidden="true"></i>';
            reloadBtn.addEventListener("click", () => {
                if (typeof interactionConfig.onReload === "function") {
                    interactionConfig.onReload();
                    return;
                }

                wrapper.dispatchEvent(new CustomEvent("task:reload", { bubbles: true }));
            });
            actions.appendChild(reloadBtn);
        }

        if (interactionConfig.enableScriptInfoLink && interactionConfig.scriptInfoHref) {
            const scriptInfoLink = document.createElement("a");
            scriptInfoLink.className = "task-toolbar-btn task-toolbar-link";
            scriptInfoLink.href = interactionConfig.scriptInfoHref;
            scriptInfoLink.title = interactionConfig.scriptInfoLabel;
            scriptInfoLink.setAttribute("aria-label", interactionConfig.scriptInfoLabel);
            scriptInfoLink.innerHTML = '<i class="fa-solid fa-book-open" aria-hidden="true"></i>';
            actions.appendChild(scriptInfoLink);
        }

        toolbar.appendChild(actions);
        wrapper.insertBefore(toolbar, wrapper.firstChild);
    }

    if (persistenceKey) {
        const persistedInputs = Array.isArray(persistedState?.inputs) ? persistedState.inputs : [];
        answerFields.forEach((field, fieldIndex) => {
            applyFieldUiState(field, persistedInputs[fieldIndex]);

            const onFieldChange = () => {
                persistCurrentUiState();
            };

            field.addEventListener("input", onFieldChange);
            field.addEventListener("change", onFieldChange);
        });

        checkedQuestionIndexes.forEach((questionIndex) => {
            const evaluate = questionEvaluators[questionIndex];
            if (typeof evaluate === "function") evaluate();
        });

        persistCurrentUiState();
    }

    initializeSelect2ForDropdowns(wrapper);

    return wrapper;
}
