import { getChecksByLernbereich } from "../data/checks-repo.js";
import { getAufgabenSammlung } from "../data/sammlungen-repo.js";
import {
  loadTrainingState,
  saveTrainingState,
  loadTaskIndexForCheck,
  saveTaskIndexForCheck,
} from "../state/check-state-store.js";
import { buildTaskUiStateKey } from "../state/task-ui-state.js";
import { shuffleQuestionsInTask } from "../utils/task-order.js";
import { renderTask as renderRuntimeTask } from "../../../../aufgaben/runtime/task-render.js";
import { createCheckMetaRowNode, formatCheckNumber } from "./ui/check-meta.js";

async function renderMath(targetNode, retries = 4) {
  if (!targetNode) return;

  const mathJax = window.MathJax;
  if (mathJax && typeof mathJax.typesetPromise === "function") {
    try {
      await mathJax.typesetPromise([targetNode]);
    } catch {
      // Rendering errors should not block the training flow.
    }
    return;
  }

  if (retries <= 0) return;
  await new Promise((resolve) => setTimeout(resolve, 120));
  await renderMath(targetNode, retries - 1);
}

function resizePlotlyInNode(targetNode, retries = 4) {
  if (!targetNode || !window.Plotly?.Plots?.resize) return;

  const plots = Array.from(targetNode.querySelectorAll(".js-plotly-plot"));
  plots.forEach((plotNode) => {
    try {
      window.Plotly.Plots.resize(plotNode);
    } catch {
      // Ignore once and try again while layout settles.
    }
  });

  if (retries <= 0) return;
  setTimeout(() => {
    resizePlotlyInNode(targetNode, retries - 1);
  }, 120);
}

function finalizeTaskRender(targetNode) {
  void renderMath(targetNode);
  requestAnimationFrame(() => resizePlotlyInNode(targetNode));
}

function getCheckId(check) {
  if (typeof check.check_id === "string" && check.check_id.trim()) {
    return check.check_id;
  }

  const gebiet = check.Gebiet || "gebiet";
  const lernbereich = check.Lernbereich || "lernbereich";
  const nummer = String(Number(check.Nummer) || 0).padStart(2, "0");
  return `${gebiet}__${lernbereich}__${nummer}`;
}

function toDomIdFragment(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function getTrainingCheckAnchorId(check) {
  const nummer = Number(check?.Nummer);
  if (Number.isFinite(nummer) && nummer > 0) {
    return `check-${nummer}`;
  }

  const checkId = getCheckId(check);
  return `check-${toDomIdFragment(checkId) || "item"}`;
}

function resolvePreferredCheckIdFromHash(checks) {
  const rawHash = window.location?.hash || "";
  const hash = rawHash.startsWith("#") ? rawHash.slice(1) : rawHash;
  if (!hash) return "";

  const decoded = decodeURIComponent(hash);
  const byAnchor = checks.find((check) => getTrainingCheckAnchorId(check) === decoded);
  if (byAnchor) {
    return getCheckId(byAnchor);
  }

  const nummerMatch = /^check-(\d+)$/.exec(decoded);
  if (!nummerMatch) return "";

  const nummer = Number(nummerMatch[1]);
  if (!Number.isFinite(nummer)) return "";
  const byNummer = checks.find((check) => Number(check?.Nummer) === nummer);
  return byNummer ? getCheckId(byNummer) : "";
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

function toSlug(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function getScriptPageHref() {
  const path = window.location?.pathname || "";
  if (!path.endsWith("training.html")) return "";
  return path.replace(/training\.html$/, "skript.html");
}

function buildScriptInfoHref(check) {
  const scriptPageHref = getScriptPageHref();
  if (!scriptPageHref) return "";

  const explicitAnchor =
    check?.skript_anchor ??
    check?.SkriptAnchor ??
    check?.skriptAnchor ??
    "";
  if (typeof explicitAnchor === "string" && explicitAnchor.trim()) {
    const anchor = explicitAnchor.trim();
    return `${scriptPageHref}#${encodeURIComponent(anchor)}`;
  }

  const infoKeyRaw =
    check?.info_key ??
    check?.InfoKey ??
    check?.infoKey ??
    (Number.isFinite(Number(check?.Nummer)) ? String(Number(check.Nummer)) : "") ??
    getCheckId(check);

  const key = String(infoKeyRaw || "");
  const slug = toSlug(key);
  if (!slug) return "";
  return `${scriptPageHref}#${encodeURIComponent(`check-${slug}`)}`;
}

function createTaskCardNode(
  check,
  aufgabe,
  onReloadTask = null,
  scriptInfoHref = "",
  taskUiStateKey = "",
  readPersistedState = true
) {
  const titel = check.Schlagwort || check["Ich kann"] || `Check ${check.Nummer}`;
  const card = document.createElement("article");
  card.className = "dev-check-card dev-check-card--training";

  // ── Unified card header row ──
  const header = document.createElement("div");
  header.className = "dev-check-card__header";

  const headerLeft = createCheckMetaRowNode(
    {
      numberText: formatCheckNumber(check?.Nummer),
      titleText: titel,
      prefix: "Check",
      tone: "training",
      rowClass: "dev-check-card__header-left",
      titleTag: "h3",
    }
  );

  const headerRight = document.createElement("div");
  headerRight.className = "dev-check-card__header-actions";

  if (scriptInfoHref) {
    const skriptLink = document.createElement("a");
    skriptLink.className = "dev-check-card__action-btn";
    skriptLink.href = scriptInfoHref;
    skriptLink.title = "Im Skript nachschlagen";
    skriptLink.setAttribute("aria-label", "Im Skript nachschlagen");
    skriptLink.innerHTML = '<i class="fa-solid fa-book-open" aria-hidden="true"></i>';
    headerRight.appendChild(skriptLink);
  }

  const createHeaderActionProxyButton = ({ iconClass, title, onClick }) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "dev-check-card__action-btn";
    button.title = title;
    button.setAttribute("aria-label", title);
    button.innerHTML = `<i class="fa-solid ${iconClass}" aria-hidden="true"></i>`;
    button.addEventListener("click", onClick);
    return button;
  };

  const statsBtn = document.createElement("button");
  statsBtn.type = "button";
  statsBtn.className = "dev-check-card__action-btn dev-check-card__stats-btn";
  statsBtn.title = "Noch keine Statistik vorhanden";
  statsBtn.setAttribute("aria-label", "Statistik");
  statsBtn.innerHTML = '<i class="fa-solid fa-chart-simple" aria-hidden="true"></i>';
  headerRight.appendChild(statsBtn);

  header.appendChild(headerLeft);
  header.appendChild(headerRight);
  card.appendChild(header);

  const body = document.createElement("div");
  body.className = "dev-check-card__body";
  card.appendChild(body);

  if (!aufgabe) {
    body.textContent = "Keine Aufgabe in dieser Sammlung gefunden.";
    return card;
  }

  const effectiveAufgabe = check?.questionOrder === "shuffle"
    ? shuffleQuestionsInTask(aufgabe, taskUiStateKey)
    : aufgabe;

  const runtimeTaskNode = renderRuntimeTask(effectiveAufgabe, {
    index: 0,
    showSolution: false,
    showTaskHeading: false,
    containerClass: "dev-check-card__runtime-task",
    interaction: {
      enablePerQuestionCheck: true,
      enableReload: true,
      enableSolutionToggle: true,
      enableScriptInfoLink: false,
      scriptInfoHref,
      statePersistenceKey: taskUiStateKey,
      readPersistedState,
      onReload: onReloadTask,
    },
  });
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
    const syncSolutionButton = (button) => {
      const label = runtimeSolutionBtn.getAttribute("aria-label") || runtimeSolutionBtn.title || "Loesungen anzeigen";
      const showHideState = label.toLowerCase().includes("ausblenden");
      button.title = label;
      button.setAttribute("aria-label", label);
      button.innerHTML = showHideState
        ? '<i class="fa-solid fa-eye-slash" aria-hidden="true"></i>'
        : '<i class="fa-solid fa-eye" aria-hidden="true"></i>';
    };

    const solutionProxy = createHeaderActionProxyButton({
      iconClass: "fa-eye",
      title: "Loesungen anzeigen",
      onClick: () => {
        runtimeSolutionBtn.click();
        syncSolutionButton(solutionProxy);
      },
    });
    syncSolutionButton(solutionProxy);
    headerRight.appendChild(solutionProxy);
  }

  if (runtimeReloadBtn) {
    const reloadProxy = createHeaderActionProxyButton({
      iconClass: "fa-rotate-right",
      title: runtimeReloadBtn.getAttribute("aria-label") || runtimeReloadBtn.title || "Neue Aufgabe",
      onClick: () => runtimeReloadBtn.click(),
    });
    headerRight.appendChild(reloadProxy);
  }

  if (runtimeToolbar) {
    runtimeToolbar.remove();
  }

  return card;
}

function createBrowseTaskCardNode(check, sammlung, options = {}) {
  const {
    initialTaskIndex = 0,
    onTaskIndexChange = null,
    readPersistedState = true,
  } = options;

  const hasTasks = Array.isArray(sammlung) && sammlung.length > 0;
  let taskIndex = Number.isInteger(initialTaskIndex) ? initialTaskIndex : 0;
  if (!hasTasks || taskIndex < 0 || taskIndex >= sammlung.length) {
    taskIndex = 0;
  }

  let cardNode = null;
  const scriptInfoHref = buildScriptInfoHref(check);
  const checkId = getCheckId(check);
  const anchorId = getTrainingCheckAnchorId(check);
  const viewportNode = document.createElement("section");
  viewportNode.className = "check-viewport-item check-viewport-item--scroll-card";
  viewportNode.id = anchorId;
  viewportNode.dataset.checkId = checkId;

  if (hasTasks && typeof onTaskIndexChange === "function") {
    onTaskIndexChange(taskIndex);
  }

  if (!hasTasks) {
    cardNode = createTaskCardNode(check, null, null, scriptInfoHref);
    viewportNode.appendChild(cardNode);
    return viewportNode;
  }

  const renderCurrentCard = () =>
    createTaskCardNode(
      check,
      sammlung[taskIndex] || null,
      () => {
        taskIndex = pickRandomTaskIndex(taskIndex, sammlung.length);
        if (typeof onTaskIndexChange === "function") {
          onTaskIndexChange(taskIndex);
        }
        const nextCard = renderCurrentCard();
        cardNode.replaceWith(nextCard);
        cardNode = nextCard;
        finalizeTaskRender(viewportNode);
      },
      scriptInfoHref,
      buildTaskUiStateKey({ lernbereich: check.Lernbereich, checkId, taskIndex }),
      readPersistedState
    );

  cardNode = renderCurrentCard();
  viewportNode.appendChild(cardNode);
  return viewportNode;
}

function renderInfoFallback(root, text) {
  root.innerHTML = `<p class="dev-module__status">${text}</p>`;
  finalizeTaskRender(root);
}

function bindShell(root) {
  return {
    taskHost: root.querySelector("#dev-training-task"),
    jumpNav: document.getElementById("dev-training-jump-nav"),
  };
}

const trainingJumpNavScrollCleanup = new WeakMap();

function renderTrainingJumpNav(navNode, checks, activeCheckId = "") {
  if (!navNode) return;

  navNode.innerHTML = checks
    .map((check) => {
      const checkId = getCheckId(check);
      const label = `${check.Nummer}. ${check.Schlagwort || "Check"}`;
      const href = `#${getTrainingCheckAnchorId(check)}`;
      const activeClass = checkId === activeCheckId ? " active" : "";
      return `<a class="check-jump-tab${activeClass}" href="${href}" data-check-id="${checkId}">${label}</a>`;
    })
    .join("");

  if (navNode.dataset.activeBinding !== "1") {
    navNode.dataset.activeBinding = "1";
    navNode.addEventListener("click", (event) => {
      const target = event.target.closest(".check-jump-tab");
      if (!target) return;
      navNode.querySelectorAll(".check-jump-tab.active").forEach((el) => el.classList.remove("active"));
      target.classList.add("active");
    });
  }
}

function setTrainingJumpNavActive(navNode, checkId) {
  if (!navNode || !checkId) return;

  const tabs = Array.from(navNode.querySelectorAll(".check-jump-tab"));
  let matched = false;
  tabs.forEach((tab) => {
    const isActive = tab.dataset.checkId === checkId;
    tab.classList.toggle("active", isActive);
    if (isActive) matched = true;
  });

  if (!matched && tabs[0]) {
    tabs[0].classList.add("active");
  }
}

function bindTrainingJumpNavScrollSync(navNode, cardNodes) {
  if (!navNode) return;

  const existingCleanup = trainingJumpNavScrollCleanup.get(navNode);
  if (typeof existingCleanup === "function") {
    existingCleanup();
    trainingJumpNavScrollCleanup.delete(navNode);
  }

  const cards = Array.from(cardNodes || []).filter((card) => card?.dataset?.checkId);
  if (cards.length === 0) return;

  const updateActiveFromScroll = () => {
    const offsetTop = 210;
    let passedCard = null;
    let upcomingCard = null;
    let upcomingDistance = Number.POSITIVE_INFINITY;

    cards.forEach((card) => {
      const top = card.getBoundingClientRect().top;
      const distance = top - offsetTop;
      if (distance <= 0) {
        passedCard = card;
        return;
      }
      if (distance < upcomingDistance) {
        upcomingDistance = distance;
        upcomingCard = card;
      }
    });

    const activeCard = passedCard || upcomingCard || cards[0];
    setTrainingJumpNavActive(navNode, activeCard?.dataset?.checkId || "");
  };

  let ticking = false;
  const scrollContainer = document.querySelector(".mod-main");
  const scrollSource = scrollContainer || window;
  const onViewportChange = () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(() => {
      ticking = false;
      updateActiveFromScroll();
    });
  };

  scrollSource.addEventListener("scroll", onViewportChange, { passive: true });
  window.addEventListener("resize", onViewportChange);
  updateActiveFromScroll();

  trainingJumpNavScrollCleanup.set(navNode, () => {
    scrollSource.removeEventListener("scroll", onViewportChange);
    window.removeEventListener("resize", onViewportChange);
  });
}

function setTaskMessage(taskHost, message, isError = false) {
  if (!taskHost) return;
  const color = isError ? "var(--rose)" : "var(--text-dim)";
  taskHost.innerHTML = `<p class="dev-module__status" style="color:${color};">${message}</p>`;
  finalizeTaskRender(taskHost);
}

export async function initTrainingModule({
  root,
  lernbereich,
  preferredCheckId = "",
  usePersistedState = true,
}) {
  const shell = bindShell(root);
  if (!shell.taskHost) {
    renderInfoFallback(root, "Training-Shell nicht gefunden.");
    return;
  }

  if (!lernbereich) {
    setTaskMessage(shell.taskHost, "Kein Lernbereich gesetzt (data-lernbereich fehlt).", true);
    return;
  }

  const checks = await getChecksByLernbereich(lernbereich);
  if (checks.length === 0) {
    setTaskMessage(shell.taskHost, `Keine Checks fuer Lernbereich "${lernbereich}" gefunden.`, true);
    return;
  }

  const state = usePersistedState
    ? loadTrainingState(lernbereich)
    : { selectedCheckId: null, taskIndexByCheckId: {} };
  const hasPreferredCheckId = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";
  const preferredCheckIdFromHash = resolvePreferredCheckIdFromHash(checks);

  function persist() {
    saveTrainingState(lernbereich, state);
  }

  async function renderBrowseFallback(preferredCheckIdForBrowse = "") {
    shell.taskHost.innerHTML = "";

    const preferredId = typeof preferredCheckIdForBrowse === "string"
      ? preferredCheckIdForBrowse.trim()
      : "";
    const activeCheckId = preferredId || state.selectedCheckId || "";
    if (activeCheckId) {
      state.selectedCheckId = activeCheckId;
      persist();
    }
    renderTrainingJumpNav(shell.jumpNav, checks, activeCheckId);

    const cards = await Promise.all(
      checks.map(async (check) => {
        try {
          const sammlung = await getAufgabenSammlung(check.Sammlung, {
            gebiet: check.Gebiet,
            lernbereich: check.Lernbereich,
          });
          const checkId = getCheckId(check);
          return createBrowseTaskCardNode(check, sammlung, {
            initialTaskIndex: Number.isInteger(state.taskIndexByCheckId[checkId])
              ? usePersistedState
                ? loadTaskIndexForCheck(lernbereich, checkId, state.taskIndexByCheckId[checkId])
                : state.taskIndexByCheckId[checkId]
              : usePersistedState
                ? loadTaskIndexForCheck(lernbereich, checkId, 0)
                : 0,
            readPersistedState: usePersistedState,
            onTaskIndexChange: (taskIndex) => {
              state.taskIndexByCheckId[checkId] = taskIndex;
              saveTaskIndexForCheck(lernbereich, checkId, taskIndex);
              persist();
            },
          });
        } catch (error) {
          const card = document.createElement("article");
          card.className = "dev-check-card";
          const message = document.createElement("p");
          message.className = "dev-module__status";
          message.style.color = "var(--rose)";
          message.textContent = error.message;
          card.appendChild(message);
          return card;
        }
      })
    );

    cards.forEach((card) => shell.taskHost.appendChild(card));

    if (activeCheckId) {
      const cardNodes = Array.from(
        shell.taskHost.querySelectorAll(".check-viewport-item[data-check-id]")
      );
      const targetCard = cardNodes.find((card) => card.dataset.checkId === activeCheckId);
      if (targetCard) {
        setTrainingJumpNavActive(shell.jumpNav, activeCheckId);
        targetCard.scrollIntoView({ behavior: "auto", block: "start" });
      }
    }

    bindTrainingJumpNavScrollSync(
      shell.jumpNav,
      shell.taskHost.querySelectorAll(".check-viewport-item[data-check-id]")
    );
    finalizeTaskRender(shell.taskHost);
  }

  const preferredIdForBrowse =
    (hasPreferredCheckId ? preferredCheckId.trim() : "") || preferredCheckIdFromHash;
  await renderBrowseFallback(preferredIdForBrowse);
}
