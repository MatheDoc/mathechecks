import { getChecksByLernbereich } from "../data/checks-repo.js";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";

const BL_TOTAL_SECONDS = 300;
const BL_RING_CIRCUMFERENCE = 2 * Math.PI * 20;
const BL_STATE_PREFIX = "dev-blurting-state-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.dev.tabScope.v1";
const blurtingJumpNavScrollCleanup = new WeakMap();

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
  return `${BL_STATE_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}`;
}

function loadBlurtingState(lernbereich) {
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

function saveBlurtingState(lernbereich, state) {
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
  return `bl-check-${toDomIdFragment(checkId) || "item"}`;
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

function formatTimer(secondsLeft) {
  const safe = Math.max(0, Number(secondsLeft) || 0);
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function applyInitialReveal(root) {
  if (!root) return;
  root.classList.add("dev-module-root--pending");
  // Small intentional delay to avoid a visible top flash during initial hydration.
  window.setTimeout(() => {
    root.classList.add("dev-module-root--ready");
  }, 85);
}

function toSlug(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function buildScriptInfoHref(check) {
  const path = window.location?.pathname || "";
  if (!path.endsWith("blurting.html")) return "";
  const scriptPageHref = path.replace(/blurting\.html$/, "skript.html");
  const explicitAnchor = check?.skript_anchor ?? check?.SkriptAnchor ?? check?.skriptAnchor ?? "";
  if (typeof explicitAnchor === "string" && explicitAnchor.trim()) {
    return `${scriptPageHref}#${encodeURIComponent(explicitAnchor.trim())}`;
  }
  const key = String(check?.info_key ?? check?.InfoKey ?? (Number.isFinite(Number(check?.Nummer)) ? String(Number(check.Nummer)) : "") ?? "");
  const slug = toSlug(key);
  if (!slug) return "";
  return `${scriptPageHref}#${encodeURIComponent(`check-${slug}`)}`;
}

function renderCard(check) {
  const begriff = check?.blurting?.begriff || check.Schlagwort || `Check ${check.Nummer}`;
  const checkId = getCheckId(check);
  const cardAnchorId = getCheckCardAnchorId(checkId);
  const checkNummer = formatCheckNumber(check?.Nummer);
  const scriptHref = buildScriptInfoHref(check);
  const refs = Array.isArray(check?.blurting?.referenz_stichwoerter)
    ? check.blurting.referenz_stichwoerter
    : Array.isArray(check?.Stichwoerter)
      ? check.Stichwoerter
      : [];
  const refsMarkup = refs
    .map((ref) => `<span class="bl-kw"><span class="bl-kwdot"></span>${escapeHtml(ref)}</span>`)
    .join("");

  const skriptIcon = scriptHref
    ? `<a class="dev-check-card__action-btn" href="${escapeHtml(scriptHref)}" title="Im Skript nachschlagen" aria-label="Im Skript nachschlagen"><i class="fa-solid fa-book-open" aria-hidden="true"></i></a>`
    : "";

  return `
    <section id="${escapeHtml(cardAnchorId)}" class="check-viewport-item check-viewport-item--blurting" data-bl-check-viewport data-check-id="${escapeHtml(
    checkId
  )}">
      <div class="check-viewport-item__inner">
        <article class="card dev-training__task-card dev-check-card dev-check-card--blurting" data-bl-card>
          <div class="dev-check-card__header">
            ${renderCheckMetaRowMarkup({
    numberText: checkNummer,
    titleText: begriff,
    prefix: "Check",
    rowClass: "dev-check-card__header-left",
    badgeClass: "dev-check-card__badge dev-check-card__badge--blurting",
    titleClass: "dev-training__task-title dev-check-card__title dev-check-card__title--blurting",
    titleTag: "h3",
  })}
            <div class="dev-check-card__header-actions">
              ${skriptIcon}
              <button type="button" class="dev-check-card__action-btn dev-check-card__stats-btn" title="Noch keine Statistik vorhanden" aria-label="Statistik"><i class="fa-solid fa-chart-simple" aria-hidden="true"></i></button>
            </div>
          </div>
          <p class="bl-prompt">Schreib alles auf, was dir zu diesem Begriff einfällt. Nach Ablauf der Zeit folgt der Selbstcheck.</p>

          <div data-bl-stage="write">
            <div class="bl-timer-row">
              <div class="bl-timer-ring">
                <svg width="50" height="50" viewBox="0 0 50 50">
                  <circle class="bl-track" cx="25" cy="25" r="20" />
                  <circle class="bl-arc" data-bl-arc cx="25" cy="25" r="20" stroke-dasharray="${BL_RING_CIRCUMFERENCE.toFixed(
    2
  )}" stroke-dashoffset="0" />
                </svg>
                <span class="bl-timer-num" data-bl-num>${formatTimer(BL_TOTAL_SECONDS)}</span>
              </div>
              <div class="bl-timer-info">
                <div class="bl-ti-t">Brainstorm-Zeit</div>
                <div class="bl-ti-s">Erst schreiben, dann mit Stichwörtern vergleichen.</div>
              </div>
              <button class="bl-reveal-btn" type="button" data-bl-reveal>Jetzt auswerten</button>
            </div>

            <textarea
              class="bl-textarea"
              data-bl-input
              placeholder="Notiere hier Begriffe, Formeln und Lösungswege."></textarea>
          </div>

          <div data-bl-stage="evaluate" hidden>
            <div class="bl-divider">
              <hr><span>Referenz-Stichwörter</span><hr>
            </div>
            ${refs.length ? `<div class="bl-kws" style="margin-bottom:18px;">${refsMarkup}</div>` : "<p style=\"font-size:.82rem;color:var(--text-muted);margin-bottom:18px;\">Keine Referenz-Stichwörter hinterlegt.</p>"}
            <p class="bl-selbst-lbl">Wie sicher bist du bei diesem Begriff?</p>
            <div class="bl-selbst-btns">
              <button class="bl-sb yes" type="button" data-bl-answer="yes">
                <span class="bl-sb-icon">✓</span>
                <span class="bl-sb-title">Kann ich</span>
                <span class="bl-sb-sub">Die wichtigsten Punkte waren da.</span>
              </button>
              <button class="bl-sb no" type="button" data-bl-answer="no">
                <span class="bl-sb-icon">↺</span>
                <span class="bl-sb-title">Noch nicht</span>
                <span class="bl-sb-sub">Ich wiederhole erst im Skript.</span>
              </button>
            </div>
          </div>

          <div data-bl-stage="result-yes" hidden>
            <div class="outcome">
              <div class="oc-icon green">✓</div>
              <h3 class="oc-title green">Sehr gut</h3>
              <p class="oc-sub">Du konntest den Begriff aktiv abrufen.</p>
            </div>
          </div>

          <div data-bl-stage="result-no" hidden>
            <div class="outcome">
              <div class="oc-icon amber">📖</div>
              <h3 class="oc-title amber">Gute Einschätzung</h3>
              <p class="oc-sub">Wiederhole den Abschnitt im Skript und versuche es danach erneut.</p>
            </div>
          </div>
        </article>
      </div>
    </section>
  `;
}

function renderJumpNav(navNode, checks, activeCheckId) {
  if (!navNode) return;

  navNode.innerHTML = checks
    .map((check) => {
      const checkId = getCheckId(check);
      const nummer = Number.isFinite(Number(check?.Nummer)) ? Number(check.Nummer) : "";
      const label = `${nummer}. ${check.Schlagwort || check?.blurting?.begriff || "Check"}`;
      const href = `#${getCheckCardAnchorId(checkId)}`;
      const activeClass = checkId === activeCheckId ? " active" : "";
      return `<a class="check-jump-tab${activeClass}" href="${escapeHtml(href)}" data-check-id="${escapeHtml(checkId)}">${escapeHtml(label)}</a>`;
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

  const existingCleanup = blurtingJumpNavScrollCleanup.get(navNode);
  if (typeof existingCleanup === "function") {
    existingCleanup();
    blurtingJumpNavScrollCleanup.delete(navNode);
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

  blurtingJumpNavScrollCleanup.set(navNode, () => {
    scrollSource.removeEventListener("scroll", onViewportChange);
    window.removeEventListener("resize", onViewportChange);
  });
}

function initInteractiveBlurtingCards(root) {
  const cards = root.querySelectorAll("[data-bl-card]");

  cards.forEach((card) => {
    const stages = {
      write: card.querySelector('[data-bl-stage="write"]'),
      evaluate: card.querySelector('[data-bl-stage="evaluate"]'),
      resultYes: card.querySelector('[data-bl-stage="result-yes"]'),
      resultNo: card.querySelector('[data-bl-stage="result-no"]'),
    };

    const timerLabel = card.querySelector("[data-bl-num]");
    const timerArc = card.querySelector("[data-bl-arc]");
    const revealButton = card.querySelector("[data-bl-reveal]");

    let secondsLeft = BL_TOTAL_SECONDS;
    let timerId = null;

    function setStage(nextStage) {
      stages.write.hidden = nextStage !== "write";
      stages.evaluate.hidden = nextStage !== "evaluate";
      stages.resultYes.hidden = nextStage !== "result-yes";
      stages.resultNo.hidden = nextStage !== "result-no";
    }

    function updateTimerView() {
      if (!timerLabel || !timerArc) return;
      timerLabel.textContent = formatTimer(secondsLeft);
      const fraction = Math.max(0, Math.min(1, secondsLeft / BL_TOTAL_SECONDS));
      timerArc.style.strokeDashoffset = String(BL_RING_CIRCUMFERENCE * (1 - fraction));
    }

    function clearTimer() {
      if (timerId) {
        window.clearInterval(timerId);
        timerId = null;
      }
    }

    function revealEvaluation() {
      clearTimer();
      setStage("evaluate");
    }

    function setResult(canRecall) {
      clearTimer();
      setStage(canRecall ? "result-yes" : "result-no");
    }

    revealButton?.addEventListener("click", revealEvaluation);
    card.querySelector('[data-bl-answer="yes"]')?.addEventListener("click", () => setResult(true));
    card.querySelector('[data-bl-answer="no"]')?.addEventListener("click", () => setResult(false));

    updateTimerView();
    timerId = window.setInterval(() => {
      secondsLeft -= 1;
      if (secondsLeft <= 0) {
        secondsLeft = 0;
        updateTimerView();
        revealEvaluation();
        return;
      }
      updateTimerView();
    }, 1000);
  });
}

function bindCheckPositionPersistence(root, lernbereich, state) {
  const cards = root.querySelectorAll("[data-bl-check-viewport][data-check-id]");
  cards.forEach((card) => {
    const checkId = card.getAttribute("data-check-id") || "";
    if (!checkId) return;

    const remember = () => {
      state.selectedCheckId = checkId;
      saveBlurtingState(lernbereich, state);
    };

    card.addEventListener("pointerdown", remember);
    card.addEventListener("focusin", remember);
    card.addEventListener("click", remember);
  });
}

export async function initBlurtingModule({ root, lernbereich, preferredCheckId = "" }) {
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
  const state = loadBlurtingState(lernbereich);
  const navNode = document.getElementById("dev-blurting-jump-nav");
  const hasPreferred = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";

  const preferredSelected = hasPreferred ? byId.get(preferredCheckId.trim()) : null;
  const selectedCheckId =
    (preferredSelected && getCheckId(preferredSelected)) || state.selectedCheckId || getCheckId(checks[0]);
  state.selectedCheckId = selectedCheckId;
  saveBlurtingState(lernbereich, state);

  renderJumpNav(navNode, checks, selectedCheckId);
  root.innerHTML = checks.map((check) => renderCard(check)).join("");
  bindJumpNavScrollSync(navNode, root.querySelectorAll("[data-bl-check-viewport][data-check-id]"));
  applyInitialReveal(root);
  initInteractiveBlurtingCards(root);
  bindCheckPositionPersistence(root, lernbereich, state);
  await renderMath(root);
}
