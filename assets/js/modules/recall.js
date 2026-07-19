import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";
import { recordCheckFeedDecision } from "../platform/feed-actions.js?v=20260603-topbar-feed-badge";
import { recordUserActivity, getUserRecallProficiency, extractRecallProficiencyRate } from "../platform/progress-client.js?v=20260701-recall-quote-ui";
import { getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js?v=20260520-feed-loading";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { applyFeedFocusScope, attachFeedCardControls, attachFreeCompletionControl, leaveFeedContext } from "./ui/feed-card-controls.js?v=20260712-feed-focus";
import { enhanceCheckJumpNav } from "./ui/check-jump-nav.js";
import { enhanceSpeechInputs } from "./ui/speech-input.js?v=20260719-speech-cursor-insert";
import { showTaskCompletionPopup } from "./ui/task-completion-popup.js?v=20260701-recall-quote-popup";

const RECALL_STATE_PREFIX = "recall-state-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.tabScope.v1";
const recallJumpNavScrollCleanup = new WeakMap();
const RECALL_FEED_STEP_KEY = "recall";
const RECALL_EVALUATION_TIMEOUT_MS = 30000;

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
  return `${RECALL_STATE_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}`;
}

function loadRecallState(lernbereich) {
  try {
    const raw = window.localStorage.getItem(getStateKey(lernbereich));
    if (!raw) {
      return { selectedCheckId: null };
    }
    const parsed = JSON.parse(raw);
    return {
      selectedCheckId:
        parsed && typeof parsed.selectedCheckId === "string" ? parsed.selectedCheckId : null,
    };
  } catch {
    return { selectedCheckId: null };
  }
}

function saveRecallState(lernbereich, state) {
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
  return `recall-check-${toDomIdFragment(checkId) || "item"}`;
}

function renderInfo(root, text) {
  root.innerHTML = `<p style="color:var(--text-dim);line-height:1.6;">${text}</p>`;
  void renderMath(root);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function updateRecallRateBadge(badgeEl, rate) {
  if (!badgeEl) return;
  if (rate === null || !Number.isFinite(rate)) {
    badgeEl.textContent = "–";
    badgeEl.removeAttribute("data-has-rate");
    return;
  }
  badgeEl.textContent = `${Math.round(rate)} %`;
  badgeEl.setAttribute("data-has-rate", "true");
}

function renderRecallListMarkup(items, { user = false } = {}) {
  const listClassName = user ? "recall-list recall-list--user" : "recall-list";
  return `
    <ul class="${listClassName}">
      ${items.map((item) => `<li class="recall-list__item">${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;
}

const RECALL_SCORE_THRESHOLDS = { correct: 0.82, partial: 0.65 };
const RECALL_RETRY_PENALTY = 0.5;

function shuffleArray(items) {
  const arr = items.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function normalizeTipp(raw) {
  if (raw && typeof raw === "object") {
    return {
      cue: typeof raw.cue === "string" ? raw.cue.trim() : "",
      response: typeof raw.response === "string" ? raw.response.trim() : "",
    };
  }
  return { cue: "", response: typeof raw === "string" ? raw.trim() : "" };
}

function getFixedTipps(check) {
  return Array.isArray(check?.Tipps) ? check.Tipps.map(normalizeTipp).filter((tipp) => tipp.response) : [];
}

function getQueryTipps(check) {
  const tipps = getFixedTipps(check);
  const order = String(check?.tippOrder || "shuffle").trim().toLowerCase();
  return order === "fixed" ? tipps : shuffleArray(tipps);
}

function renderTippLine(item) {
  const responseHtml = escapeHtml(item.response);
  return item.cue ? `<strong>${escapeHtml(item.cue)}:</strong> ${responseHtml}` : responseHtml;
}

function renderTippListMarkup(items) {
  return `
    <ul class="recall-list recall-list--tips">
      ${items.map((item) => `<li class="recall-list__item">${renderTippLine(item)}</li>`).join("")}
    </ul>
  `;
}

function renderCueItemsMarkup(items, cardAnchorId) {
  return items
    .map((item, index) => {
      const inputId = `recall-input-${cardAnchorId}-${index}`;
      const label = item.cue ? escapeHtml(item.cue) : `Punkt ${index + 1}`;
      const solutionText = escapeHtml(item.response);
      return `
        <div class="recall-cue-item" data-recall-cue-item data-cue="${escapeHtml(item.cue)}" data-response="${escapeHtml(item.response)}">
          <label class="recall-cue-item__label" for="${inputId}">${label}</label>
          <div class="recall-response-cell">
            <textarea class="recall-input-slot answer-input" id="${inputId}" rows="1" maxlength="240" data-recall-slot="${index}" placeholder="Deine Antwort ..."></textarea>
            <div class="task-feedback recall-inline-feedback" data-recall-feedback hidden></div>
            <div class="solution recall-inline-solution" data-recall-solution hidden><span class="solution-badge">${solutionText}</span></div>
            <button class="answer-reveal-request" type="button" data-recall-show-solution hidden>Lösung anzeigen</button>
          </div>
        </div>
      `;
    })
    .join("");
}

function classifyRecallScore(score) {
  if (score >= RECALL_SCORE_THRESHOLDS.correct) return { label: "korrekt", cls: "correct" };
  if (score >= RECALL_SCORE_THRESHOLDS.partial) return { label: "teilweise", cls: "partial" };
  return { label: "nicht erkannt", cls: "wrong" };
}

async function evaluateRecallItems(items) {
  let timeoutId = null;
  try {
    const config = getSupabaseRuntimeConfig();
    const baseUrl = String(config.url || "").replace(/\/+$/, "");
    const anonKey = String(config.anonKey || "").trim();
    if (!baseUrl || !anonKey) return null;

    const supabase = await getSupabaseClient();
    const sessionResult = supabase ? await supabase.auth.getSession() : null;
    const accessToken = sessionResult?.data?.session?.access_token;
    if (!accessToken) {
      // Ohne echtes Login keine KI-Bewertung anfragen; Aufrufer behandelt das
      // wie einen KI-Ausfall (Loesungen werden eingeblendet).
      console.warn("MatheChecks: Recall-Bewertung uebersprungen, kein aktives Login.");
      return null;
    }

    const controller = typeof AbortController === "function" ? new AbortController() : null;
    timeoutId = controller
      ? window.setTimeout(() => controller.abort(), RECALL_EVALUATION_TIMEOUT_MS)
      : null;

    const response = await fetch(`${baseUrl}/functions/v1/recall-evaluate`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        apikey: anonKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        items: items.map((item) => ({ cue: item.cue, response: item.response, student: item.student })),
      }),
      signal: controller?.signal,
    });

    if (!response.ok) {
      console.warn("MatheChecks: Recall-Bewertung fehlgeschlagen.", response.status, response.statusText);
      return null;
    }

    const data = await response.json();
    if (!data || !Array.isArray(data.results)) {
      return null;
    }

    return data;
  } catch (error) {
    console.warn("MatheChecks: Recall-Bewertung konnte nicht abgerufen werden.", error);
    return null;
  } finally {
    if (timeoutId !== null) window.clearTimeout(timeoutId);
  }
}

function applyInitialReveal(root) {
  if (!root) return;
  root.classList.add("module-root--pending");
  // Small intentional delay to avoid a visible top flash during initial hydration.
  window.setTimeout(() => {
    root.classList.add("module-root--ready");
  }, 85);
}

const RECALL_DELAY_MS = 1000;
const RECALL_MEMORIZE_DELAY_MS = 1000;

function renderCard(check) {
  const begriff = check?.recall?.begriff || check.Schlagwort || `Check ${check.Nummer}`;
  const ichKann = check?.["Ich kann"] || "";
  const checkId = getCheckId(check);
  const cardAnchorId = getCheckCardAnchorId(checkId);
  const checkNummer = formatCheckNumber(check?.Nummer);
  const fixedTipps = getFixedTipps(check);
  const queryTipps = getQueryTipps(check);
  const kernpunkteMarkup = fixedTipps.length ? renderTippListMarkup(fixedTipps) : "";
  const noRefsNote = `<p class="recall-no-refs">Keine Kernpunkte hinterlegt.</p>`;
  const cueItemsMarkup = queryTipps.length
    ? renderCueItemsMarkup(queryTipps, cardAnchorId)
    : `
        <div class="recall-cue-item" data-recall-cue-item data-cue="" data-response="">
          <span class="recall-cue-item__label">Punkt 1</span>
          <div class="recall-response-cell">
            <textarea class="recall-input-slot answer-input" rows="1" maxlength="240" data-recall-slot="0" placeholder="Was fällt dir ein?"></textarea>
          </div>
        </div>
      `;

  return `
    <section id="${escapeHtml(cardAnchorId)}" class="check-viewport-item check-viewport-item--scroll-card check-viewport-item--narrow" data-recall-check-viewport data-check-id="${escapeHtml(
    checkId
  )}" data-recall-ref-count="${fixedTipps.length}">
      <article class="check-card check-card--recall" data-recall-card>
        <div class="check-card__header">
          ${renderCheckMetaRowMarkup({
    numberText: checkNummer,
    titleText: begriff,
    prefix: "Recall",
    tone: "recall",
    rowClass: "check-card__header-left",
    titleTag: "span",
  })}
          <div class="check-card__header-actions">
            <span class="check-card__rate-badge" aria-label="Recall-Quote">–</span>
          </div>
        </div>
        <div class="check-card__body">
        <div class="recall-focus">
          <p class="recall-competence">${escapeHtml(ichKann.replace(/\.$/, ""))}</p>
        </div>
        <div data-recall-stage="recall">
          <div data-recall-idle>
            <div class="recall-action-row">
              <button class="module-action-button" type="button" data-recall-start>Start</button>
            </div>
          </div>
          <div data-recall-active hidden>
            <p class="recall-prompt">Welche Tipps fallen dir dazu ein?</p>
            <div class="recall-timer-bar" data-recall-timer-bar="recall">
              <div class="recall-timer-bar__fill" data-recall-timer-fill="recall"></div>
            </div>
            <div class="recall-action-row">
              <button class="module-action-button module-action-button--locked" type="button" data-recall-to-memorize disabled>Zu den Tipps</button>
            </div>
          </div>
        </div>

        <div data-recall-stage="memorize" hidden>
          <p class="recall-prompt">Merke dir jetzt die wichtigsten Tipps.</p>
          <div class="recall-timer-bar" data-recall-timer-bar="memorize">
            <div class="recall-timer-bar__fill" data-recall-timer-fill="memorize"></div>
          </div>
          ${fixedTipps.length ? kernpunkteMarkup : noRefsNote}
          <div class="recall-action-row">
            <button class="module-action-button module-action-button--locked" type="button" data-recall-to-retrieve disabled>Jetzt abfragen</button>
          </div>
        </div>

        <div data-recall-stage="retrieve" hidden>
          <p class="recall-prompt">Welche Tipps kannst du abrufen?</p>
          <div class="recall-cue-list check-card__runtime-task" data-recall-cue-list>
            ${cueItemsMarkup}
          </div>
          <div class="recall-action-row">
            <button class="module-action-button" type="button" data-recall-to-compare>Antworten prüfen</button>
          </div>
          <div data-recall-eval-status class="recall-eval-status"></div>
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
      const label = `${nummer}. ${check.Schlagwort || check?.recall?.begriff || "Check"}`;
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

  const existingCleanup = recallJumpNavScrollCleanup.get(navNode);
  if (typeof existingCleanup === "function") {
    existingCleanup();
    recallJumpNavScrollCleanup.delete(navNode);
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

  recallJumpNavScrollCleanup.set(navNode, () => {
    scrollSource.removeEventListener("scroll", onViewportChange);
    window.removeEventListener("resize", onViewportChange);
  });
}

function revealComparePanel(comparePanel) {
  if (!comparePanel) return;
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  comparePanel.hidden = false;

  const cardBody = comparePanel.closest(".check-card")?.querySelector(".check-card__body");
  const scrollTarget = comparePanel.querySelector(".recall-divider") || comparePanel;
  if (cardBody) {
    const bodyRect = cardBody.getBoundingClientRect();
    const targetRect = scrollTarget.getBoundingClientRect();
    const top = cardBody.scrollTop + (targetRect.top - bodyRect.top) - 10;

    cardBody.scrollTo({
      top: Math.max(0, top),
      behavior: prefersReducedMotion ? "auto" : "smooth",
    });
  }
}

function computeRecallAttemptScore(rawScore, attempts) {
  const score = Number(rawScore);
  if (!Number.isFinite(score)) return 0;
  const attemptCount = Math.max(1, Number(attempts) || 1);
  const factor = Math.max(0, 1 - (attemptCount - 1) * RECALL_RETRY_PENALTY);
  return Math.max(0, Math.min(1, score)) * factor;
}

const RECALL_INPUT_STATE_CLASSES = [
  "recall-input-slot--partial",
  "recall-input-slot--unchecked",
  "is-correct",
  "is-incorrect",
  "is-partial",
];

function resetRecallInputEvaluation(root) {
  root?.querySelectorAll?.("[data-recall-cue-item]").forEach((itemEl) => {
    const input = itemEl.querySelector(".recall-input-slot");
    const feedback = itemEl.querySelector("[data-recall-feedback]");
    const solution = itemEl.querySelector("[data-recall-solution]");
    const revealButton = itemEl.querySelector("[data-recall-show-solution]");

    input?.classList.remove(...RECALL_INPUT_STATE_CLASSES);
    input?.removeAttribute("data-recall-evaluation");
    if (feedback) {
      feedback.textContent = "";
      feedback.hidden = true;
      feedback.classList.remove("is-correct", "is-incorrect", "is-neutral", "is-partial");
    }
    if (solution) solution.hidden = true;
    if (revealButton) {
      revealButton.hidden = true;
      revealButton.onclick = null;
    }
  });
}

function applyRecallInputEvaluations(cueItemEls, finalItems, itemStates, onStateChange = null) {
  cueItemEls.forEach((itemEl, index) => {
    const input = itemEl.querySelector(".recall-input-slot");
    const feedback = itemEl.querySelector("[data-recall-feedback]");
    const solution = itemEl.querySelector("[data-recall-solution]");
    const revealButton = itemEl.querySelector("[data-recall-show-solution]");
    if (!input) return;
    input.classList.remove(...RECALL_INPUT_STATE_CLASSES);
    if (feedback) {
      feedback.textContent = "";
      feedback.hidden = true;
      feedback.classList.remove("is-correct", "is-incorrect", "is-neutral", "is-partial");
    }
    if (solution) solution.hidden = true;
    if (revealButton) {
      revealButton.hidden = true;
      revealButton.onclick = null;
    }

    const item = finalItems[index];
    const state = itemStates[index];
    if (!item || item.unchecked) {
      input.classList.add("recall-input-slot--unchecked");
      input.dataset.recallEvaluation = "unchecked";
      if (feedback) {
        feedback.textContent = "Dieser Punkt konnte nicht automatisch bewertet werden.";
        feedback.classList.add("is-neutral");
        feedback.hidden = false;
      }
      return;
    }

    const verdict = classifyRecallScore(item.score);
    if (verdict.cls === "correct") {
      input.classList.add("is-correct");
    } else if (verdict.cls === "partial") {
      input.classList.add("is-partial", "recall-input-slot--partial");
    } else {
      input.classList.add("is-incorrect");
    }
    input.dataset.recallEvaluation = verdict.cls;

    if (feedback && item.reason) {
      feedback.textContent = item.reason;
      feedback.classList.add(verdict.cls === "correct" ? "is-correct" : verdict.cls === "partial" ? "is-partial" : "is-incorrect");
      feedback.hidden = false;
    }

    if (solution) {
      solution.hidden = verdict.cls !== "correct" && !state?.revealed;
      void renderMath(solution);
    }

    if (revealButton && solution && verdict.cls !== "correct" && !state?.revealed) {
      revealButton.hidden = false;
      revealButton.onclick = () => {
        if (state) state.revealed = true;
        solution.hidden = false;
        revealButton.hidden = true;
        void renderMath(solution);
        if (typeof onStateChange === "function") onStateChange();
      };
    }
  });
}

function buildRecallCompletionDetails(evalState, source = "complete") {
  const itemScores = Array.isArray(evalState?.itemScores)
    ? evalState.itemScores.filter((score) => Number.isFinite(Number(score))).map(Number)
    : [];
  return {
    selfOutcome: source,
    ...(itemScores.length ? { itemScores } : {}),
    ...(Array.isArray(evalState?.rawItemScores) ? { rawItemScores: evalState.rawItemScores } : {}),
    ...(Array.isArray(evalState?.itemAttempts) ? { itemAttempts: evalState.itemAttempts } : {}),
    ...(Array.isArray(evalState?.itemRevealed) ? { itemRevealed: evalState.itemRevealed } : {}),
    ...(Number.isFinite(Number(evalState?.checkableCount)) ? { checkableCount: Number(evalState.checkableCount) } : {}),
    ...(Number.isFinite(Number(evalState?.revealedCount)) ? { revealedCount: Number(evalState.revealedCount) } : {}),
    ...(evalState?.model ? { model: evalState.model } : {}),
  };
}

function normalizeRecallFeedContext(activityContext) {
  if (!activityContext || activityContext.mode !== "feed") return null;
  return String(activityContext.activityStep || "").trim() === RECALL_FEED_STEP_KEY
    ? {
      mode: "feed",
      activityKey: String(activityContext.activityKey || "").trim(),
      activityStep: RECALL_FEED_STEP_KEY,
    }
    : null;
}

function attachRecallFeedShell(section, activityContext, { lernbereich = "" } = {}) {
  const feedContext = normalizeRecallFeedContext(activityContext);
  if (!section || !feedContext) return;

  const activityCard = section.querySelector("[data-recall-card]");
  const controls = attachFeedCardControls(section, {
    cardSelector: "[data-recall-card]",
    stepLabel: "Recall",
  });
  if (!controls) return;

  let canPrepare = false;
  let completed = false;
  let busy = false;
  let statusMessage = "Prüfe die Antworten. Abschluss ist möglich, sobald alles richtig ist oder die Lösungen angezeigt wurden.";
  let statusTone = "neutral";
  let latestEvalState = null;

  const checkId = section.dataset.checkId || "";

  async function recordRecallCompletion() {
    await recordUserActivity({
      activityType: "recall",
      lernbereichSlug: lernbereich,
      checkId,
      contextKey: "feed",
      details: buildRecallCompletionDetails(latestEvalState, "feed_complete"),
    });

    return recordCheckFeedDecision({
      lernbereichSlug: lernbereich,
      checkId,
      moduleKey: "recall",
      outcomeKey: "can_do",
      activityKey: feedContext.activityKey,
    });
  }

  const enablePrepare = () => {
    if (completed) return;
    canPrepare = true;
    statusMessage = "Alle Punkte sind abgeschlossen. Du kannst den Feed-Abschluss vorbereiten.";
    statusTone = "neutral";
    renderControls();
  };

  const disablePrepare = () => {
    if (completed) return;
    canPrepare = false;
    statusMessage = "Noch nicht alle Punkte sind richtig oder aufgelöst.";
    statusTone = "neutral";
    renderControls();
  };

  const completeRecallDecision = async () => {
    if (busy) return;
    busy = true;
    statusMessage = "Der Feed-Schritt wird gespeichert.";
    statusTone = "neutral";
    renderControls();

    try {
      await recordRecallCompletion();
    } catch (error) {
      console.error("Recall-Aktivität konnte nicht abgeschlossen werden:", error);
      busy = false;
      statusMessage = "Die Recall-Aktivität konnte gerade nicht gespeichert werden.";
      statusTone = "error";
      renderControls();
      throw error;
    }

    completed = true;
    statusMessage = "Die Recall-Aktivität wurde abgeschlossen. Die nächste Feed-Aktivität wird geöffnet.";
    statusTone = "success";
    renderControls();
  };

  const repeatRecallDecision = () => {
    canPrepare = false;
    latestEvalState = null;
    statusMessage = "Die Recall-Aktivität bleibt im Feed offen.";
    statusTone = "neutral";
    section.dispatchEvent(new CustomEvent("recall:reset-request", { bubbles: true }));
    renderControls();
  };

  const openRecallDecision = () => {
    if (!controls?.openDecisionDialog || busy || completed || !canPrepare) return;

    controls.openDecisionDialog({
      title: "Recall abschließen?",
      detail: "Der bewertete Durchgang wird für deine Recall-Quote gespeichert.",
      onComplete: completeRecallDecision,
      onRepeat: repeatRecallDecision,
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
        onClick: openRecallDecision,
      },
    ];

    controls.render({
      status: statusMessage,
      tone: statusTone,
      items,
      ready: canPrepare && !busy && !completed,
    });
  }

  section.addEventListener("recall:evaluation-ready", (event) => {
    latestEvalState = event.detail || null;
    if (latestEvalState?.ready) {
      enablePrepare();
    } else {
      disablePrepare();
    }
  });
  renderControls();
}

function initInteractiveRecallCards(root, lernbereich, activityContext) {
  const cards = root.querySelectorAll("[data-recall-card]");
  const cardEvalState = new WeakMap();

  cards.forEach((card) => {
    const section = card.closest("[data-recall-check-viewport]");
    const checkId = section?.getAttribute("data-check-id") || "";

    const stageEls = {
      recall: card.querySelector('[data-recall-stage="recall"]'),
      memorize: card.querySelector('[data-recall-stage="memorize"]'),
      retrieve: card.querySelector('[data-recall-stage="retrieve"]'),
    };

    const recallIdle = card.querySelector("[data-recall-idle]");
    const recallActive = card.querySelector("[data-recall-active]");
    const startBtn = card.querySelector("[data-recall-start]");
    const toMemorizeBtn = card.querySelector("[data-recall-to-memorize]");
    const toRetrieveBtn = card.querySelector("[data-recall-to-retrieve]");
    const toCompareBtn = card.querySelector("[data-recall-to-compare]");
    const comparePanel = card.querySelector("[data-recall-compare-panel]");
    const cueList = card.querySelector("[data-recall-cue-list]");
    const evalStatusEl = card.querySelector("[data-recall-eval-status]");
    const userNotesEl = card.querySelector("[data-recall-user-notes]");

    function setStage(name) {
      for (const [key, el] of Object.entries(stageEls)) {
        if (el) el.hidden = key !== name;
      }
    }

    const isFreeMode = activityContext?.mode !== "feed";
    let freeCompletionControl = null;
    let completionRecordPromise = null;
    let latestRates = null;
    let itemStates = [];

    function ensureItemStates(cueItemEls = Array.from(card.querySelectorAll("[data-recall-cue-item]"))) {
      if (itemStates.length !== cueItemEls.length) {
        itemStates = cueItemEls.map((_, index) => itemStates[index] || {
          attempts: 0,
          rawScore: null,
          effectiveScore: null,
          reason: "",
          model: "",
          revealed: false,
        });
      }
      return itemStates;
    }

    function buildEvalState() {
      const cueItemEls = Array.from(card.querySelectorAll("[data-recall-cue-item]"));
      const states = ensureItemStates(cueItemEls);
      const scorable = cueItemEls
        .map((el, index) => ({ el, state: states[index] }))
        .filter(({ el }) => String(el.dataset.response || "").trim());

      const ready = scorable.length > 0 && scorable.every(({ state }) => {
        return Boolean(state?.revealed) || Number(state?.rawScore) >= RECALL_SCORE_THRESHOLDS.correct;
      });

      return {
        ready,
        checkableCount: scorable.length,
        revealedCount: scorable.filter(({ state }) => Boolean(state?.revealed)).length,
        rawItemScores: scorable.map(({ state }) => Number.isFinite(Number(state?.rawScore)) ? Number(state.rawScore) : 0),
        itemAttempts: scorable.map(({ state }) => Math.max(0, Number(state?.attempts) || 0)),
        itemRevealed: scorable.map(({ state }) => Boolean(state?.revealed)),
        itemScores: scorable.map(({ state }) => {
          if (state?.revealed) return 0;
          return computeRecallAttemptScore(state?.rawScore, state?.attempts);
        }),
        model: scorable.find(({ state }) => state?.model)?.state?.model || "",
      };
    }

    function publishCompletionState() {
      const evalState = buildEvalState();
      if (evalState.checkableCount > 0) {
        cardEvalState.set(card, evalState);
      } else {
        cardEvalState.delete(card);
      }
      section?.dispatchEvent(new CustomEvent("recall:evaluation-ready", { detail: evalState, bubbles: true }));
      ensureFreeCompletionControl(evalState.ready);
      return evalState;
    }

    async function recordRecallActivityOnce() {
      if (completionRecordPromise) return completionRecordPromise;

      completionRecordPromise = (async () => {
        const evalState = cardEvalState.get(card);
        const details = buildRecallCompletionDetails(evalState, "free_complete");
        if (!Array.isArray(details.itemScores) || details.itemScores.length === 0) {
          latestRates = { previousRate: null, newRate: null };
          return latestRates;
        }

        const before = await getUserRecallProficiency();
        const previousRate = before.ok ? extractRecallProficiencyRate(before.data, checkId) : null;

        await recordUserActivity({
          activityType: "recall",
          lernbereichSlug: lernbereich,
          checkId,
          contextKey: "free",
          details,
        });

        const after = await getUserRecallProficiency();
        const newRate = after.ok ? extractRecallProficiencyRate(after.data, checkId) : null;
        updateRecallRateBadge(section?.querySelector(".check-card__rate-badge"), newRate);
        latestRates = { previousRate, newRate };
        return latestRates;
      })();

      return completionRecordPromise;
    }

    async function openFreeCompletionPopup() {
      const rates = latestRates || await recordRecallActivityOnce();
      showTaskCompletionPopup({
        mode: "recall",
        showQuote: true,
        previousRate: rates.previousRate,
        newRate: rates.newRate,
        onRepeat: resetRecallCard,
        onDashboard: () => window.location.assign("/dashboard.html"),
      });
    }

    function goToMemorizeStage() {
      setStage("memorize");
      const memDuration = RECALL_MEMORIZE_DELAY_MS;
      startTimerBar("memorize", memDuration, toRetrieveBtn);
      void renderMath(stageEls.memorize);
    }

    function resetRecallCard() {
      if (comparePanel) comparePanel.hidden = true;
      if (freeCompletionControl) freeCompletionControl.setReady(false);
      completionRecordPromise = null;
      latestRates = null;
      itemStates = [];
      if (cueList) {
        cueList.querySelectorAll(".recall-input-slot").forEach((el) => { el.value = ""; });
        resetRecallInputEvaluation(cueList);
      }
      if (evalStatusEl) evalStatusEl.innerHTML = "";
      if (userNotesEl) { userNotesEl.hidden = true; userNotesEl.innerHTML = ""; }
      cardEvalState.delete(card);
      section?.dispatchEvent(new CustomEvent("recall:evaluation-ready", { detail: { ready: false }, bubbles: true }));
      if (recallActive) recallActive.hidden = true;
      if (recallIdle) recallIdle.hidden = false;
      goToMemorizeStage();
    }

    function ensureFreeCompletionControl(ready = false) {
      if (!isFreeMode) return;
      if (!freeCompletionControl) {
        freeCompletionControl = attachFreeCompletionControl(section, {
          cardSelector: "[data-recall-card]",
          stepLabel: "Recall",
          onComplete: () => {
            void openFreeCompletionPopup();
          },
        });
      }
      if (freeCompletionControl) freeCompletionControl.setReady(Boolean(ready));
    }

    ensureFreeCompletionControl(false);

    function startTimerBar(scope, durationMs, btn) {
      const fill = card.querySelector(`[data-recall-timer-fill="${scope}"]`);
      if (fill) {
        fill.style.transition = "none";
        fill.style.width = "100%";
        void fill.offsetWidth;
        fill.style.transition = `width ${durationMs}ms linear`;
        fill.style.width = "0%";
      }
      if (btn) {
        btn.disabled = true;
        btn.classList.add("module-action-button--locked");
        setTimeout(() => {
          btn.disabled = false;
          btn.classList.remove("module-action-button--locked");
        }, durationMs);
      }
    }

    // Start button → reveal Kompetenz + timer
    startBtn?.addEventListener("click", () => {
      if (recallIdle) recallIdle.hidden = true;
      if (recallActive) recallActive.hidden = false;
      void renderMath(recallActive);
      startTimerBar("recall", RECALL_DELAY_MS, toMemorizeBtn);
    });

    // Phase 1 → 2
    toMemorizeBtn?.addEventListener("click", () => {
      goToMemorizeStage();
    });

    // Phase 2 → 3
    toRetrieveBtn?.addEventListener("click", () => {
      if (cueList) {
        cueList.querySelectorAll(".recall-input-slot").forEach((el) => { el.value = ""; });
        resetRecallInputEvaluation(cueList);
      }
      if (comparePanel) comparePanel.hidden = true;
      if (evalStatusEl) evalStatusEl.innerHTML = "";
      if (userNotesEl) { userNotesEl.hidden = true; userNotesEl.innerHTML = ""; }
      cardEvalState.delete(card);
      completionRecordPromise = null;
      latestRates = null;
      itemStates = [];
      section?.dispatchEvent(new CustomEvent("recall:evaluation-ready", { detail: { ready: false }, bubbles: true }));
      setStage("retrieve");
      ensureItemStates();
      const first = cueList?.querySelector(".recall-input-slot");
      first?.focus();
    });

    // Phase 3: KI-Bewertung + Vergleich + Selbstcheck innerhalb derselben Stage
    toCompareBtn?.addEventListener("click", async () => {
      if (toCompareBtn.disabled) return;

      const cueItemEls = Array.from(card.querySelectorAll("[data-recall-cue-item]"));
      const states = ensureItemStates(cueItemEls);
      const allItems = cueItemEls.map((el) => ({
        cue: el.dataset.cue || "",
        response: el.dataset.response || "",
        student: el.querySelector(".recall-input-slot")?.value.trim() || "",
      }));
      const evaluationTargets = allItems
        .map((item, index) => ({ item, index }))
        .filter(({ item, index }) => {
          const state = states[index];
          if (!item.response || state?.revealed) return false;
          return Number(state?.rawScore) < RECALL_SCORE_THRESHOLDS.correct;
        });
      const hasScorableItems = allItems.some((item) => item.response);

      toCompareBtn.disabled = true;
      const originalLabel = toCompareBtn.textContent;
      toCompareBtn.textContent = "MatheChecks prüft ...";
    
      let finalItems = allItems.map((item, index) => ({
        ...item,
        score: Number.isFinite(Number(states[index]?.rawScore)) ? Number(states[index].rawScore) : 0,
        reason: states[index]?.reason || "",
        unchecked: !Number.isFinite(Number(states[index]?.rawScore)) && !states[index]?.revealed,
      }));
      let evaluationOk = false;

      if (evaluationTargets.length) {
        const evalData = await evaluateRecallItems(evaluationTargets.map(({ item }) => item));
        if (evalData?.results) {
          evaluationTargets.forEach(({ item, index }, targetPos) => {
            const result = evalData.results[targetPos] || {};
            const state = states[index];
            state.attempts += 1;
            state.rawScore = typeof result.score === "number" ? result.score : 0;
            state.effectiveScore = computeRecallAttemptScore(state.rawScore, state.attempts);
            state.reason = result.reason || "";
            state.model = evalData.model || "";
            finalItems[index] = {
              ...item,
              score: typeof result.score === "number" ? result.score : 0,
              reason: result.reason || "",
              unchecked: Boolean(result.unchecked),
            };
          });
          evaluationOk = true;
        }
      } else if (hasScorableItems) {
        evaluationOk = true;
      }

      if (evalStatusEl) evalStatusEl.innerHTML = "";
      toCompareBtn.disabled = false;
      toCompareBtn.textContent = originalLabel;

      if (evaluationOk) {
        if (userNotesEl) { userNotesEl.hidden = true; userNotesEl.innerHTML = ""; }

        applyRecallInputEvaluations(cueItemEls, finalItems, states, publishCompletionState);
        publishCompletionState();
      } else {
        if (userNotesEl) { userNotesEl.hidden = true; userNotesEl.innerHTML = ""; }
        if (evalStatusEl && hasScorableItems) {
          evalStatusEl.innerHTML = `<p class="recall-eval-note">Automatische Bewertung war gerade nicht möglich. Die Lösungen werden angezeigt.</p>`;
        }
        if (hasScorableItems) {
          evaluationTargets.forEach(({ item, index }) => {
            const state = states[index];
            if (!state) return;
            state.revealed = true;
            state.rawScore = Number.isFinite(Number(state.rawScore)) ? Number(state.rawScore) : 0;
            state.effectiveScore = 0;
            state.reason = "Automatische Bewertung war nicht möglich; die Lösung ist eingeblendet.";
            finalItems[index] = {
              ...item,
              score: state.rawScore,
              reason: state.reason,
              unchecked: false,
            };
          });
          applyRecallInputEvaluations(cueItemEls, finalItems, states, publishCompletionState);
          publishCompletionState();
        } else {
          resetRecallInputEvaluation(cueList);
          cardEvalState.delete(card);
          section?.dispatchEvent(new CustomEvent("recall:evaluation-ready", { detail: null, bubbles: true }));
        }
      }

      revealComparePanel(comparePanel);
      void renderMath(stageEls.retrieve);
    });

    card.querySelectorAll("[data-recall-cue-item]").forEach((itemEl, index) => {
      const input = itemEl.querySelector(".recall-input-slot");
      input?.addEventListener("input", () => {
        const states = ensureItemStates();
        const state = states[index];
        if (!state || state.revealed) return;
        state.rawScore = null;
        state.effectiveScore = null;
        state.reason = "";
        const feedback = itemEl.querySelector("[data-recall-feedback]");
        const solution = itemEl.querySelector("[data-recall-solution]");
        const revealButton = itemEl.querySelector("[data-recall-show-solution]");
        input.classList.remove(...RECALL_INPUT_STATE_CLASSES);
        input.removeAttribute("data-recall-evaluation");
        if (feedback) {
          feedback.textContent = "";
          feedback.hidden = true;
          feedback.classList.remove("is-correct", "is-incorrect", "is-neutral", "is-partial");
        }
        if (solution) solution.hidden = true;
        if (revealButton) revealButton.hidden = true;
        publishCompletionState();
      });
    });

    section?.addEventListener("recall:reset-request", resetRecallCard);
  });
}

function bindCheckPositionPersistence(root, lernbereich, state) {
  const cards = root.querySelectorAll("[data-recall-check-viewport][data-check-id]");
  cards.forEach((card) => {
    const checkId = card.getAttribute("data-check-id") || "";
    if (!checkId) return;

    const remember = () => {
      state.selectedCheckId = checkId;
      saveRecallState(lernbereich, state);
    };

    card.addEventListener("pointerdown", remember);
    card.addEventListener("focusin", remember);
    card.addEventListener("click", remember);
  });
}

export async function initRecallModule({ root, lernbereich, preferredCheckId = "", activityContext = null }) {
  if (!lernbereich) {
    renderInfo(root, "Kein Lernbereich gesetzt (data-lernbereich fehlt).");
    return;
  }

  const checks = await getChecksByLernbereich(lernbereich);
  if (checks.length === 0) {
    renderInfo(root, `Keine Checks fuer Lernbereich \"${lernbereich}\" gefunden.`);
    return;
  }

  const byId = new Map(checks.map((check) => [getCheckId(check), check]));
  const state = loadRecallState(lernbereich);
  const navNode = document.getElementById("recall-jump-nav");
  const hasPreferred = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";

  const preferredSelected = hasPreferred ? byId.get(preferredCheckId.trim()) : null;
  const selectedCheckId =
    (preferredSelected && getCheckId(preferredSelected)) || state.selectedCheckId || getCheckId(checks[0]);
  state.selectedCheckId = selectedCheckId;
  saveRecallState(lernbereich, state);

  renderJumpNav(navNode, checks, selectedCheckId);
  root.innerHTML = checks.map((check) => renderCard(check)).join("");
  const selectedSection = Array.from(root.querySelectorAll("[data-recall-check-viewport][data-check-id]"))
    .find((section) => section.dataset.checkId === selectedCheckId) || null;
  if (selectedSection) {
    attachRecallFeedShell(selectedSection, activityContext, { lernbereich });
    if (activityContext?.mode === "feed") {
      setJumpNavActive(navNode, selectedCheckId);
      scrollModMainToEl(selectedSection);
    }
  }
  bindJumpNavScrollSync(navNode, root.querySelectorAll("[data-recall-check-viewport][data-check-id]"));
  applyInitialReveal(root);
  initInteractiveRecallCards(root, lernbereich, activityContext);
  getUserRecallProficiency().then((proficiency) => {
    if (!proficiency.ok) return;
    root.querySelectorAll("[data-recall-check-viewport][data-check-id]").forEach((section) => {
      const rate = extractRecallProficiencyRate(proficiency.data, section.dataset.checkId);
      updateRecallRateBadge(section.querySelector(".check-card__rate-badge"), rate);
    });
  });
  enhanceSpeechInputs(root, ".recall-input-slot");
  if (activityContext?.mode === "feed" && selectedSection) {
    applyFeedFocusScope(root, selectedSection);
  }
  bindCheckPositionPersistence(root, lernbereich, state);
  await renderMath(root);
}
