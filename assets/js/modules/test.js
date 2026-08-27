import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";
import { completeTestFeedStep } from "../platform/feed-actions.js?v=20260826-test-module";
import { recordUserActivity, getUserTestProficiency, extractTestProficiencyRate } from "../platform/progress-client.js?v=20260826-test-module";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { applyFeedFocusScope, attachFeedCardControls, attachFreeCompletionControl, leaveFeedContext } from "./ui/feed-card-controls.js?v=20260826-test-module";
import { enhanceCheckJumpNav } from "./ui/check-jump-nav.js";
import { showTaskCompletionPopup } from "./ui/task-completion-popup.js?v=20260826-test-module";

const TEST_STATE_PREFIX = "test-state-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.tabScope.v1";
const TEST_FEED_STEP_KEY = "test";
const TEST_QUESTION_SECONDS = 20;
const testJumpNavScrollCleanup = new WeakMap();

function scrollModMainToEl(el) {
  const container = document.querySelector(".mod-main");
  if (!container) { el.scrollIntoView({ behavior: "auto", block: "start" }); return; }
  const tabNav = container.querySelector(".mod-tab-nav");
  const jumpNavWrap = container.querySelector(".check-jump-nav-wrap");
  const offset = (tabNav ? tabNav.offsetHeight : 0) + (jumpNavWrap ? jumpNavWrap.offsetHeight : 0);
  const y = container.scrollTop + el.getBoundingClientRect().top - container.getBoundingClientRect().top - offset;
  container.scrollTo({ top: Math.max(0, y), behavior: "auto" });
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

function getStateKey(lernbereich) {
  return `${TEST_STATE_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}`;
}

function loadTestState(lernbereich) {
  try {
    const raw = window.localStorage.getItem(getStateKey(lernbereich));
    if (!raw) return { selectedCheckId: null };
    const parsed = JSON.parse(raw);
    return {
      selectedCheckId:
        parsed && typeof parsed.selectedCheckId === "string" ? parsed.selectedCheckId : null,
    };
  } catch {
    return { selectedCheckId: null };
  }
}

function saveTestState(lernbereich, state) {
  try {
    window.localStorage.setItem(getStateKey(lernbereich), JSON.stringify(state));
  } catch {
    // Ignore storage errors.
  }
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
    .replaceAll(/[^a-z0-9_-]+/g, "-")
    .replaceAll(/^-+|-+$/g, "");
}

function getCheckCardAnchorId(checkId) {
  return `test-check-${toDomIdFragment(checkId) || "item"}`;
}

function renderInfo(root, text) {
  root.innerHTML = `<p style="color:var(--text-dim);line-height:1.6;">${text}</p>`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function updateTestRateBadge(badgeEl, rate) {
  if (!badgeEl) return;
  if (rate === null || !Number.isFinite(rate)) {
    badgeEl.textContent = "–";
    badgeEl.removeAttribute("data-has-rate");
    return;
  }
  badgeEl.textContent = `${Math.round(rate)} %`;
  badgeEl.setAttribute("data-has-rate", "true");
}

function shuffleArray(items) {
  const arr = items.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function buildTestSourceUrl(check) {
  const gebiet = encodeURIComponent(String(check?.Gebiet || "").trim());
  const lernbereich = encodeURIComponent(String(check?.Lernbereich || "").trim());
  const checkId = encodeURIComponent(getCheckId(check));
  return `/aufgaben/test/${gebiet}/${lernbereich}/${checkId}.json`;
}

function normalizeQuestion(raw, sourceIndex) {
  const frage = typeof raw?.frage === "string" ? raw.frage.trim() : "";
  const antworten = Array.isArray(raw?.antworten)
    ? raw.antworten.map((item) => (typeof item === "string" ? item.trim() : "")).filter(Boolean)
    : [];
  const fehler = Array.isArray(raw?.fehler)
    ? raw.fehler.map((item) => (typeof item === "string" ? item.trim() : ""))
    : [];
  if (!frage || antworten.length !== 4) return null;
  return { frage, antworten, fehler, sourceIndex };
}

async function loadTestQuestions(check) {
  const response = await fetch(buildTestSourceUrl(check), { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`Test-Quelle nicht erreichbar (${response.status})`);
  }
  const data = await response.json();
  const fragen = Array.isArray(data?.fragen) ? data.fragen : [];
  const normalized = fragen
    .map((raw, index) => normalizeQuestion(raw, index))
    .filter(Boolean);
  if (!normalized.length) {
    throw new Error("Test-Quelle enthält keine gültigen Fragen.");
  }
  return normalized;
}

function buildRun(questions) {
  return shuffleArray(questions).map((question) => {
    // answerOrder[i] = Original-Index der Antwort an Anzeigeposition i (0 = richtig).
    const answerOrder = shuffleArray([0, 1, 2, 3]);
    return { question, answerOrder };
  });
}

function applyInitialReveal(root) {
  if (!root) return;
  root.classList.add("module-root--pending");
  window.setTimeout(() => {
    root.classList.add("module-root--ready");
  }, 85);
}

const ANSWER_LONG_TEXT_THRESHOLD = 55;

// Sichtbare Textlaenge ohne LaTeX-Markup (Befehle/Klammern zaehlen nicht als Anzeigebreite).
function estimateVisibleLength(text) {
  return String(text || "")
    .replaceAll(/\\[()\[\]]/g, "")
    .replaceAll(/\\[a-zA-Z]+/g, "")
    .replaceAll(/[{}_^]/g, "")
    .trim()
    .length;
}

function renderCard(check) {
  const begriff = check.Schlagwort || `Check ${check.Nummer}`;
  const ichKann = check?.["Ich kann"] || "";
  const checkId = getCheckId(check);
  const cardAnchorId = getCheckCardAnchorId(checkId);
  const checkNummer = formatCheckNumber(check?.Nummer);

  return `
    <section id="${escapeHtml(cardAnchorId)}" class="check-viewport-item check-viewport-item--scroll-card check-viewport-item--narrow" data-test-check-viewport data-check-id="${escapeHtml(checkId)}">
      <article class="check-card check-card--test" data-test-card>
        <div class="check-card__header">
          ${renderCheckMetaRowMarkup({
    numberText: checkNummer,
    titleText: begriff,
    prefix: "Test",
    tone: "test",
    rowClass: "check-card__header-left",
    titleTag: "span",
  })}
          <div class="check-card__header-actions">
            <span class="check-card__rate-badge" aria-label="Test-Quote">–</span>
          </div>
        </div>
        <div class="check-card__body">
          <div class="module-flow-focus">
            <p class="module-flow-competence">${escapeHtml(ichKann.replace(/\.$/, ""))}</p>
          </div>
          <div data-test-stage="idle">
            <p class="test-intro">10 Fragen · eine richtige Antwort je Frage</p>
            <div class="module-flow-action-row">
              <button class="module-action-button" type="button" data-test-start>Start</button>
            </div>
            <div class="test-load-error" data-test-load-error hidden></div>
          </div>
          <div data-test-stage="run" hidden>
            <p class="test-progress" data-test-progress></p>
            <div class="module-flow-timer-bar" data-test-timer-bar>
              <div class="module-flow-timer-bar__fill" data-test-timer-fill></div>
            </div>
            <p class="test-question" data-test-question></p>
            <div class="test-answer-grid" data-test-answers></div>
            <div class="test-feedback" data-test-feedback hidden></div>
            <div class="module-flow-action-row">
              <button class="module-action-button" type="button" data-test-next hidden>Weiter</button>
            </div>
          </div>
          <div data-test-stage="summary" hidden>
            <p class="test-summary-headline" data-test-summary-headline></p>
            <div class="test-summary-chips" data-test-summary-chips></div>
            <div class="test-summary-list" data-test-summary-list></div>
          </div>
        </div>
      </article>
    </section>
  `;
}

function renderJumpNav(navNode, checks, activeCheckId) {
  if (!navNode) return;

  navNode.innerHTML = checks
    .map((check) => {
      const checkId = getCheckId(check);
      const nummer = Number.isFinite(Number(check?.Nummer)) ? Number(check.Nummer) : "";
      const label = `${nummer}. ${check.Schlagwort || "Check"}`;
      const href = `#${getCheckCardAnchorId(checkId)}`;
      const activeClass = checkId === activeCheckId ? " active" : "";
      return `<a class="check-jump-tab${activeClass}" href="${escapeHtml(href)}" data-check-id="${escapeHtml(checkId)}">${escapeHtml(label)}</a>`;
    })
    .join("");

  enhanceCheckJumpNav(navNode);

  if (navNode.dataset.activeBinding !== "1") {
    navNode.dataset.activeBinding = "1";
    navNode.addEventListener("click", (event) => {
      const target = event.target.closest(".check-jump-tab");
      if (!target) return;
      event.preventDefault();
      navNode.querySelectorAll(".check-jump-tab.active").forEach((el) => el.classList.remove("active"));
      target.classList.add("active");
      const href = target.getAttribute("href");
      const targetId = href?.startsWith("#") ? href.slice(1) : null;
      if (targetId) {
        const targetEl = document.getElementById(targetId);
        if (targetEl) scrollModMainToEl(targetEl);
      }
    });
  }
}

function setJumpNavActive(navNode, checkId) {
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

function bindJumpNavScrollSync(navNode, cardNodes) {
  if (!navNode) return;

  const existingCleanup = testJumpNavScrollCleanup.get(navNode);
  if (typeof existingCleanup === "function") {
    existingCleanup();
    testJumpNavScrollCleanup.delete(navNode);
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
    setJumpNavActive(navNode, activeCard?.dataset?.checkId || "");
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

  testJumpNavScrollCleanup.set(navNode, () => {
    scrollSource.removeEventListener("scroll", onViewportChange);
    window.removeEventListener("resize", onViewportChange);
  });
}

function buildTestCompletionDetails(results, source = "complete") {
  const questionResults = results.map((result) => ({
    sourceIndex: result.sourceIndex,
    correct: Boolean(result.correct),
    answerIndex: result.answerIndex,
    timeMs: result.timeMs,
  }));
  const correctCount = questionResults.filter((entry) => entry.correct).length;
  return {
    selfOutcome: source,
    questionResults,
    correctCount,
    totalCount: questionResults.length,
  };
}

function normalizeTestFeedContext(activityContext) {
  if (!activityContext || activityContext.mode !== "feed") return null;
  return String(activityContext.activityStep || "").trim() === TEST_FEED_STEP_KEY
    ? {
      mode: "feed",
      activityKey: String(activityContext.activityKey || "").trim(),
      activityStep: TEST_FEED_STEP_KEY,
    }
    : null;
}

function attachTestFeedShell(section, activityContext, { lernbereich = "" } = {}) {
  const feedContext = normalizeTestFeedContext(activityContext);
  if (!section || !feedContext) return;

  const controls = attachFeedCardControls(section, {
    cardSelector: "[data-test-card]",
    stepLabel: "Test",
  });
  if (!controls) return;

  let canPrepare = false;
  let completed = false;
  let busy = false;
  let statusMessage = "Beantworte die 10 Testfragen. Danach kannst du den Check abschließen.";
  let statusTone = "neutral";
  let latestResults = null;

  const checkId = section.dataset.checkId || "";

  async function recordTestCompletion() {
    await recordUserActivity({
      activityType: "test",
      lernbereichSlug: lernbereich,
      checkId,
      contextKey: "feed",
      details: buildTestCompletionDetails(latestResults || [], "feed_complete"),
    });

    return completeTestFeedStep({
      checkId,
      activityKey: feedContext.activityKey,
    });
  }

  const completeTestDecision = async () => {
    if (busy) return;
    busy = true;
    statusMessage = "Der Feed-Schritt wird gespeichert.";
    statusTone = "neutral";
    renderControls();

    try {
      await recordTestCompletion();
    } catch (error) {
      console.error("Test-Aktivität konnte nicht abgeschlossen werden:", error);
      busy = false;
      statusMessage = "Die Test-Aktivität konnte gerade nicht gespeichert werden.";
      statusTone = "error";
      renderControls();
      throw error;
    }

    completed = true;
    statusMessage = "Der Check ist abgeschlossen. Die nächste Feed-Aktivität wird geöffnet.";
    statusTone = "success";
    renderControls();
  };

  const repeatTestDecision = () => {
    canPrepare = false;
    latestResults = null;
    statusMessage = "Die Test-Aktivität bleibt im Feed offen.";
    statusTone = "neutral";
    section.dispatchEvent(new CustomEvent("test:reset-request", { bubbles: true }));
    renderControls();
  };

  const openTestDecision = () => {
    if (!controls?.openDecisionDialog || busy || completed || !canPrepare) return;

    controls.openDecisionDialog({
      title: "Test abschließen?",
      detail: "Der Durchgang wird für deine Test-Quote gespeichert und der Check abgeschlossen.",
      onComplete: completeTestDecision,
      onRepeat: repeatTestDecision,
    });
  };

  function renderControls() {
    const items = [
      {
        icon: "❌",
        label: "Aktivität abbrechen",
        onClick: leaveFeedContext,
      },
      {
        icon: "✅",
        label: busy ? "Wird gespeichert ..." : "Abschluss vorbereiten",
        disabled: busy || completed || !canPrepare,
        iconPulse: canPrepare && !busy && !completed,
        onClick: openTestDecision,
      },
    ];

    controls.render({
      status: statusMessage,
      tone: statusTone,
      items,
      ready: canPrepare && !busy && !completed,
    });
  }

  section.addEventListener("test:run-finished", (event) => {
    latestResults = Array.isArray(event.detail?.results) ? event.detail.results : null;
    canPrepare = Boolean(latestResults?.length);
    if (canPrepare) {
      statusMessage = "Alle Fragen sind beantwortet. Du kannst den Feed-Abschluss vorbereiten.";
    }
    renderControls();
  });
  renderControls();
}

function initInteractiveTestCards(root, lernbereich, activityContext) {
  const cards = root.querySelectorAll("[data-test-card]");

  cards.forEach((card) => {
    const section = card.closest("[data-test-check-viewport]");
    const checkId = section?.getAttribute("data-check-id") || "";
    const check = section?.__testCheck || null;

    const stageEls = {
      idle: card.querySelector('[data-test-stage="idle"]'),
      run: card.querySelector('[data-test-stage="run"]'),
      summary: card.querySelector('[data-test-stage="summary"]'),
    };
    const startBtn = card.querySelector("[data-test-start]");
    const loadErrorEl = card.querySelector("[data-test-load-error]");
    const progressEl = card.querySelector("[data-test-progress]");
    const timerBar = card.querySelector("[data-test-timer-bar]");
    const timerFill = card.querySelector("[data-test-timer-fill]");
    const questionEl = card.querySelector("[data-test-question]");
    const answersEl = card.querySelector("[data-test-answers]");
    const feedbackEl = card.querySelector("[data-test-feedback]");
    const nextBtn = card.querySelector("[data-test-next]");
    const summaryHeadlineEl = card.querySelector("[data-test-summary-headline]");
    const summaryChipsEl = card.querySelector("[data-test-summary-chips]");
    const summaryListEl = card.querySelector("[data-test-summary-list]");

    const isFreeMode = activityContext?.mode !== "feed";
    let freeCompletionControl = null;
    let completionRecordPromise = null;
    let latestRates = null;

    let questionsPromise = null;
    let run = [];
    let runIndex = 0;
    let results = [];
    let questionShownAt = 0;

    function setStage(name) {
      for (const [key, el] of Object.entries(stageEls)) {
        if (el) el.hidden = key !== name;
      }
      if (name === "run") {
        card.setAttribute("data-test-run-active", "");
      } else {
        card.removeAttribute("data-test-run-active");
      }
    }

    function ensureQuestions() {
      if (!questionsPromise && check) {
        questionsPromise = loadTestQuestions(check);
      }
      return questionsPromise;
    }

    function startQuestionTimer() {
      if (!timerFill) return;
      timerFill.style.transition = "none";
      timerFill.style.width = "100%";
      void timerFill.offsetWidth;
      timerFill.style.transition = `width ${TEST_QUESTION_SECONDS * 1000}ms linear`;
      timerFill.style.width = "0%";
    }

    function renderQuestion() {
      const entry = run[runIndex];
      if (!entry) return;

      if (progressEl) progressEl.textContent = `Frage ${runIndex + 1} von ${run.length}`;
      if (feedbackEl) {
        feedbackEl.hidden = true;
        feedbackEl.innerHTML = "";
        feedbackEl.classList.remove("is-correct", "is-incorrect");
      }
      if (nextBtn) nextBtn.hidden = true;
      if (questionEl) questionEl.innerHTML = escapeHtml(entry.question.frage);

      if (answersEl) {
        answersEl.innerHTML = entry.answerOrder
          .map((originalIndex) => {
            const answerText = entry.question.antworten[originalIndex];
            const longClass = estimateVisibleLength(answerText) > ANSWER_LONG_TEXT_THRESHOLD ? " test-answer--long" : "";
            return `
            <button class="test-answer${longClass}" type="button" data-test-answer data-original-index="${originalIndex}">
              <span class="test-answer__scroll"><span class="test-answer__text">${escapeHtml(answerText)}</span></span>
            </button>
          `;
          })
          .join("");
      }

      questionShownAt = performance.now();
      startQuestionTimer();
      void renderMath(stageEls.run);
    }

    function handleAnswerClick(button) {
      const entry = run[runIndex];
      if (!entry || !answersEl) return;
      if (answersEl.dataset.locked === "1") return;
      answersEl.dataset.locked = "1";

      const chosenOriginalIndex = Number(button.dataset.originalIndex);
      const correct = chosenOriginalIndex === 0;
      const timeMs = Math.round(performance.now() - questionShownAt);

      results.push({
        sourceIndex: entry.question.sourceIndex,
        correct,
        answerIndex: chosenOriginalIndex,
        timeMs,
      });

      if (timerFill) {
        const width = window.getComputedStyle(timerFill).width;
        timerFill.style.transition = "none";
        timerFill.style.width = width;
      }

      answersEl.querySelectorAll("[data-test-answer]").forEach((answerBtn) => {
        answerBtn.disabled = true;
        const originalIndex = Number(answerBtn.dataset.originalIndex);
        if (originalIndex === 0) {
          answerBtn.classList.add("test-answer--correct");
        } else if (answerBtn === button) {
          answerBtn.classList.add("test-answer--wrong");
        } else {
          answerBtn.classList.add("test-answer--muted");
        }
      });

      if (feedbackEl) {
        if (correct) {
          feedbackEl.innerHTML = `<strong>Richtig!</strong>`;
          feedbackEl.classList.add("is-correct");
        } else {
          const fehlerText = entry.question.fehler?.[chosenOriginalIndex - 1] || "";
          feedbackEl.innerHTML = fehlerText
            ? `<strong>Leider falsch.</strong> ${escapeHtml(fehlerText)}`
            : `<strong>Leider falsch.</strong>`;
          feedbackEl.classList.add("is-incorrect");
        }
        feedbackEl.hidden = false;
        void renderMath(feedbackEl);
      }

      if (nextBtn) {
        nextBtn.textContent = runIndex + 1 >= run.length ? "Zur Auswertung" : "Weiter";
        nextBtn.hidden = false;
        nextBtn.focus({ preventScroll: true });
      }
    }

    function renderSummary() {
      const correctCount = results.filter((result) => result.correct).length;
      if (summaryHeadlineEl) {
        summaryHeadlineEl.textContent = `${correctCount} von ${results.length} Fragen richtig`;
      }
      if (summaryChipsEl) {
        summaryChipsEl.innerHTML = results
          .map((result, index) => `<span class="test-summary-chip ${result.correct ? "test-summary-chip--correct" : "test-summary-chip--wrong"}" aria-label="Frage ${index + 1} ${result.correct ? "richtig" : "falsch"}">${result.correct ? "✓" : "✗"}</span>`)
          .join("");
      }
      if (summaryListEl) {
        summaryListEl.innerHTML = run
          .map((entry, index) => {
            const result = results[index];
            const correctAnswer = entry.question.antworten[0];
            const chosenAnswer = Number.isFinite(result?.answerIndex)
              ? entry.question.antworten[result.answerIndex]
              : "";
            const detail = result?.correct
              ? ""
              : `<p class="test-summary-item__detail"><span class="test-summary-item__label">Deine Antwort:</span> ${escapeHtml(chosenAnswer)}<br><span class="test-summary-item__label">Richtig:</span> ${escapeHtml(correctAnswer)}</p>`;
            return `
              <div class="test-summary-item ${result?.correct ? "test-summary-item--correct" : "test-summary-item--wrong"}">
                <span class="test-summary-item__icon">${result?.correct ? "✓" : "✗"}</span>
                <div class="test-summary-item__content">
                  <p class="test-summary-item__question">${escapeHtml(entry.question.frage)}</p>
                  ${detail}
                </div>
              </div>
            `;
          })
          .join("");
      }
      setStage("summary");
      void renderMath(stageEls.summary);
    }

    async function recordTestActivityOnce() {
      if (completionRecordPromise) return completionRecordPromise;

      completionRecordPromise = (async () => {
        const before = await getUserTestProficiency();
        const previousRate = before.ok ? extractTestProficiencyRate(before.data, checkId) : null;

        await recordUserActivity({
          activityType: "test",
          lernbereichSlug: lernbereich,
          checkId,
          contextKey: "free",
          details: buildTestCompletionDetails(results, "free_complete"),
        });

        const after = await getUserTestProficiency();
        const newRate = after.ok ? extractTestProficiencyRate(after.data, checkId) : null;
        updateTestRateBadge(section?.querySelector(".check-card__rate-badge"), newRate);
        latestRates = { previousRate, newRate };
        return latestRates;
      })();

      return completionRecordPromise;
    }

    async function openFreeCompletionPopup() {
      const rates = latestRates || await recordTestActivityOnce();
      showTaskCompletionPopup({
        mode: "test",
        showQuote: true,
        previousRate: rates.previousRate,
        newRate: rates.newRate,
        onRepeat: resetTestCard,
        onDashboard: () => window.location.assign("/dashboard.html"),
        onStay: () => {
          if (freeCompletionControl) freeCompletionControl.setReady(false);
        },
      });
    }

    function ensureFreeCompletionControl(ready = false) {
      if (!isFreeMode) return;
      if (!freeCompletionControl) {
        freeCompletionControl = attachFreeCompletionControl(section, {
          cardSelector: "[data-test-card]",
          stepLabel: "Test",
          onComplete: () => {
            void openFreeCompletionPopup();
          },
        });
      }
      if (freeCompletionControl) freeCompletionControl.setReady(Boolean(ready));
    }

    function finishRun() {
      renderSummary();
      section?.dispatchEvent(new CustomEvent("test:run-finished", {
        detail: { results: results.slice() },
        bubbles: true,
      }));
      if (isFreeMode) {
        void recordTestActivityOnce();
        ensureFreeCompletionControl(true);
      }
    }

    function resetTestCard() {
      results = [];
      runIndex = 0;
      run = [];
      completionRecordPromise = null;
      latestRates = null;
      if (freeCompletionControl) freeCompletionControl.setReady(false);
      if (answersEl) delete answersEl.dataset.locked;
      setStage("idle");
    }

    async function startRun() {
      if (startBtn) startBtn.disabled = true;
      if (loadErrorEl) loadErrorEl.hidden = true;

      let questions;
      try {
        questions = await ensureQuestions();
      } catch (error) {
        console.error("Test-Fragen konnten nicht geladen werden:", error);
        questionsPromise = null;
        if (startBtn) startBtn.disabled = false;
        if (loadErrorEl) {
          loadErrorEl.textContent = "Die Testfragen konnten gerade nicht geladen werden. Bitte versuche es erneut.";
          loadErrorEl.hidden = false;
        }
        return;
      }

      if (startBtn) startBtn.disabled = false;
      run = buildRun(questions);
      runIndex = 0;
      results = [];
      if (answersEl) delete answersEl.dataset.locked;
      setStage("run");
      renderQuestion();
    }

    ensureFreeCompletionControl(false);

    startBtn?.addEventListener("click", () => {
      void startRun();
    });

    answersEl?.addEventListener("click", (event) => {
      const button = event.target.closest("[data-test-answer]");
      if (!button || button.disabled) return;
      handleAnswerClick(button);
    });

    nextBtn?.addEventListener("click", () => {
      if (answersEl) delete answersEl.dataset.locked;
      runIndex += 1;
      if (runIndex >= run.length) {
        finishRun();
        return;
      }
      renderQuestion();
    });

    section?.addEventListener("test:reset-request", resetTestCard);
  });
}

function bindCheckPositionPersistence(root, lernbereich, state) {
  const cards = root.querySelectorAll("[data-test-check-viewport][data-check-id]");
  cards.forEach((card) => {
    const checkId = card.getAttribute("data-check-id") || "";
    if (!checkId) return;

    const remember = () => {
      state.selectedCheckId = checkId;
      saveTestState(lernbereich, state);
    };

    card.addEventListener("pointerdown", remember);
    card.addEventListener("focusin", remember);
    card.addEventListener("click", remember);
  });
}

export async function initTestModule({ root, lernbereich, preferredCheckId = "", activityContext = null }) {
  if (!lernbereich) {
    renderInfo(root, "Kein Lernbereich gesetzt (data-lernbereich fehlt).");
    return;
  }

  const checks = await getChecksByLernbereich(lernbereich);
  if (checks.length === 0) {
    renderInfo(root, `Keine Checks fuer Lernbereich "${lernbereich}" gefunden.`);
    return;
  }

  const byId = new Map(checks.map((check) => [getCheckId(check), check]));
  const state = loadTestState(lernbereich);
  const navNode = document.getElementById("test-jump-nav");
  const hasPreferred = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";

  const preferredSelected = hasPreferred ? byId.get(preferredCheckId.trim()) : null;
  const selectedCheckId =
    (preferredSelected && getCheckId(preferredSelected)) || state.selectedCheckId || getCheckId(checks[0]);
  state.selectedCheckId = selectedCheckId;
  saveTestState(lernbereich, state);

  renderJumpNav(navNode, checks, selectedCheckId);
  root.innerHTML = checks.map((check) => renderCard(check)).join("");
  root.querySelectorAll("[data-test-check-viewport][data-check-id]").forEach((section) => {
    section.__testCheck = byId.get(section.dataset.checkId) || null;
  });

  const selectedSection = Array.from(root.querySelectorAll("[data-test-check-viewport][data-check-id]"))
    .find((section) => section.dataset.checkId === selectedCheckId) || null;
  if (selectedSection) {
    attachTestFeedShell(selectedSection, activityContext, { lernbereich });
    if (activityContext?.mode === "feed") {
      setJumpNavActive(navNode, selectedCheckId);
      scrollModMainToEl(selectedSection);
    }
  }
  bindJumpNavScrollSync(navNode, root.querySelectorAll("[data-test-check-viewport][data-check-id]"));
  applyInitialReveal(root);
  initInteractiveTestCards(root, lernbereich, activityContext);
  getUserTestProficiency().then((proficiency) => {
    if (!proficiency.ok) return;
    root.querySelectorAll("[data-test-check-viewport][data-check-id]").forEach((section) => {
      const rate = extractTestProficiencyRate(proficiency.data, section.dataset.checkId);
      updateTestRateBadge(section.querySelector(".check-card__rate-badge"), rate);
    });
  });
  if (activityContext?.mode === "feed" && selectedSection) {
    applyFeedFocusScope(root, selectedSection);
  }
  bindCheckPositionPersistence(root, lernbereich, state);
  await renderMath(root);
}
