import { getChecksByLernbereich } from "../data/checks-repo.js";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { renderCardActionsMenuMarkup, renderCardMenuLinkMarkup, initCardMenuDismiss } from "./ui/card-actions-menu.js";
import { enhanceSpeechInputs } from "./ui/speech-input.js";

const RECALL_STATE_PREFIX = "dev-recall-state-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.dev.tabScope.v1";
const recallJumpNavScrollCleanup = new WeakMap();

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
  if (!/recall\.html$/.test(path)) return "";
  const scriptPageHref = path.replace(/recall\.html$/, "skript.html");
  const explicitAnchor = check?.skript_anchor ?? check?.SkriptAnchor ?? check?.skriptAnchor ?? "";
  if (typeof explicitAnchor === "string" && explicitAnchor.trim()) {
    return `${scriptPageHref}#${encodeURIComponent(explicitAnchor.trim())}`;
  }
  const key = String(check?.info_key ?? check?.InfoKey ?? (Number.isFinite(Number(check?.Nummer)) ? String(Number(check.Nummer)) : "") ?? "");
  const slug = toSlug(key);
  if (!slug) return "";
  return `${scriptPageHref}#${encodeURIComponent(`check-${slug}`)}`;
}

const RECALL_DELAY_MS = 30000;

function renderCard(check) {
  const begriff = check?.recall?.begriff || check.Schlagwort || `Check ${check.Nummer}`;
  const ichKann = check?.["Ich kann"] || "";
  const checkId = getCheckId(check);
  const cardAnchorId = getCheckCardAnchorId(checkId);
  const checkNummer = formatCheckNumber(check?.Nummer);
  const scriptHref = buildScriptInfoHref(check);
  const refs = Array.isArray(check?.Tipps) ? check.Tipps : [];
  const refsListMarkup = refs
    .map((ref) => `<div class="recall-list-item"><span class="recall-list-dot"></span><span class="recall-list-text">${escapeHtml(ref)}</span></div>`)
    .join("");
  const refsKwMarkup = refs
    .map((ref) => `<span class="recall-keyword"><span class="recall-keyword-dot"></span>${escapeHtml(ref)}</span>`)
    .join("");
  const noRefsNote = `<p class="recall-no-refs">Keine Kernpunkte hinterlegt.</p>`;

  const skriptMenuItem = scriptHref
    ? renderCardMenuLinkMarkup({ emoji: "📖", label: "Im Skript nachschlagen", href: scriptHref })
    : "";
  const actionsMenu = skriptMenuItem ? renderCardActionsMenuMarkup(skriptMenuItem) : "";

  return `
    <section id="${escapeHtml(cardAnchorId)}" class="check-viewport-item check-viewport-item--scroll-card check-viewport-item--narrow" data-recall-check-viewport data-check-id="${escapeHtml(
    checkId
  )}" data-recall-ref-count="${refs.length}">
      <article class="dev-check-card dev-check-card--recall" data-recall-card>
        <div class="dev-check-card__header">
          ${renderCheckMetaRowMarkup({
    numberText: checkNummer,
    titleText: begriff,
    prefix: "Recall",
    tone: "recall",
    rowClass: "dev-check-card__header-left",
    titleTag: "span",
  })}
          <div class="dev-check-card__header-actions">
            ${actionsMenu}
          </div>
        </div>
        <div class="dev-check-card__body">
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
            <p class="recall-prompt">Überlege jetzt, was dir alles zu dieser Kompetenz einfällt.</p>
            <p class="recall-stage-note">Denke erst selbst nach, bevor du zu den Kernpunkten gehst.</p>
            <div class="recall-timer-bar" data-recall-timer-bar="recall">
              <div class="recall-timer-bar__fill" data-recall-timer-fill="recall"></div>
            </div>
            <div class="recall-action-row">
              <button class="module-action-button module-action-button--locked" type="button" data-recall-to-memorize disabled>Zu den Kernpunkten</button>
            </div>
          </div>
        </div>

        <div data-recall-stage="memorize" hidden>
          <p class="recall-prompt">Merke dir jetzt die wichtigsten Kernpunkte.</p>
          <p class="recall-stage-note">Präge dir die Liste ein, bevor du in die Abfrage gehst.</p>
          <div class="recall-timer-bar" data-recall-timer-bar="memorize">
            <div class="recall-timer-bar__fill" data-recall-timer-fill="memorize"></div>
          </div>
          ${refs.length ? `<div class="recall-list-items">${refsListMarkup}</div>` : noRefsNote}
          <div class="recall-action-row">
            <button class="module-action-button module-action-button--locked" type="button" data-recall-to-retrieve disabled>Jetzt abfragen</button>
          </div>
        </div>

        <div data-recall-stage="retrieve" hidden>
          <p class="recall-prompt">Welche Kernpunkte kannst du jetzt abrufen?</p>
          <p class="recall-stage-note">Schreibe nur das auf, was dir jetzt ohne Hilfe einfällt.</p>
          <div class="recall-input-slots" data-recall-input-slots>
            ${(refs.length ? refs : [""]).map((_, i) => `<input class="recall-input-slot" type="text" data-recall-slot="${i}" placeholder="Punkt ${i + 1}">`).join("")}
          </div>
          <div class="recall-action-row">
            <button class="module-action-button" type="button" data-recall-to-compare>Kernpunkte vergleichen</button>
          </div>
          <div class="recall-compare-panel" data-recall-compare-panel hidden>
          <div class="recall-divider">
            <hr><span>Dein Abruf</span><hr>
          </div>
          <div class="recall-user-notes" data-recall-user-notes></div>
          <div class="recall-divider">
            <hr><span>Kernpunkte</span><hr>
          </div>
          ${refs.length ? `<div class="recall-keywords">${refsKwMarkup}</div>` : noRefsNote}
          <p class="self-check-label">Wie sicher fühlst du dich bei dieser Kompetenz?</p>
          <div class="self-check-actions">
            <button class="self-check-button yes" type="button" data-recall-answer="yes">
              <span class="self-check-button__icon">✓</span>
              <span class="self-check-button__title">Kann ich</span>
              <span class="self-check-button__sub">Die wichtigsten Kernpunkte waren da.</span>
            </button>
            <button class="self-check-button no" type="button" data-recall-answer="no">
              <span class="self-check-button__icon">↺</span>
              <span class="self-check-button__title">Noch nicht</span>
              <span class="self-check-button__sub">Ich gehe die Kernpunkte noch einmal durch.</span>
            </button>
          </div>
          </div>
        </div>

        <div data-recall-stage="result-yes" hidden>
          <div class="outcome">
            <div class="oc-icon green">✓</div>
            <h3 class="oc-title green">Sehr gut</h3>
            <p class="oc-sub">Du konntest die Kernpunkte aktiv abrufen.</p>
          </div>
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

function initInteractiveRecallCards(root) {
  const cards = root.querySelectorAll("[data-recall-card]");

  cards.forEach((card) => {
    const section = card.closest("[data-recall-check-viewport]");
    const refCount = Number(section?.dataset?.recallRefCount) || 3;

    const stageEls = {
      recall: card.querySelector('[data-recall-stage="recall"]'),
      memorize: card.querySelector('[data-recall-stage="memorize"]'),
      retrieve: card.querySelector('[data-recall-stage="retrieve"]'),
      resultYes: card.querySelector('[data-recall-stage="result-yes"]'),
    };

    const recallIdle = card.querySelector("[data-recall-idle]");
    const recallActive = card.querySelector("[data-recall-active]");
    const startBtn = card.querySelector("[data-recall-start]");
    const toMemorizeBtn = card.querySelector("[data-recall-to-memorize]");
    const toRetrieveBtn = card.querySelector("[data-recall-to-retrieve]");
    const toCompareBtn = card.querySelector("[data-recall-to-compare]");
    const comparePanel = card.querySelector("[data-recall-compare-panel]");
    const inputSlots = card.querySelector("[data-recall-input-slots]");
    const userNotesEl = card.querySelector("[data-recall-user-notes]");

    function setStage(name) {
      for (const [key, el] of Object.entries(stageEls)) {
        if (el) el.hidden = key !== name;
      }
    }

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
      setStage("memorize");
      const memDuration = Math.min(Math.max(refCount * 5000, 10000), 45000);
      startTimerBar("memorize", memDuration, toRetrieveBtn);
      void renderMath(stageEls.memorize);
    });

    // Phase 2 → 3
    toRetrieveBtn?.addEventListener("click", () => {
      if (inputSlots) {
        inputSlots.querySelectorAll(".recall-input-slot").forEach((el) => { el.value = ""; });
      }
      if (comparePanel) comparePanel.hidden = true;
      setStage("retrieve");
      const first = inputSlots?.querySelector(".recall-input-slot");
      first?.focus();
    });

    // Phase 3: compare + self-assess inside the same stage
    toCompareBtn?.addEventListener("click", () => {
      if (userNotesEl && inputSlots) {
        const entries = Array.from(inputSlots.querySelectorAll(".recall-input-slot"))
          .map((el) => el.value.trim())
          .filter(Boolean);
        userNotesEl.innerHTML = entries.length
          ? `<div class="recall-user-entries">${entries.map((e) => `<span class="recall-keyword recall-keyword--user"><span class="recall-keyword-dot"></span>${escapeHtml(e)}</span>`).join("")}</div>`
          : `<p class="recall-no-refs">Keine Notizen eingegeben.</p>`;
      }
      if (comparePanel) comparePanel.hidden = false;
      void renderMath(stageEls.retrieve);
    });

    // "Kann ich" → result
    card.querySelector('[data-recall-answer="yes"]')?.addEventListener("click", () => {
      setStage("resultYes");
    });

    // "Noch nicht" → back to memorize
    card.querySelector('[data-recall-answer="no"]')?.addEventListener("click", () => {
      setStage("memorize");
      if (comparePanel) comparePanel.hidden = true;
      const memDuration = Math.min(Math.max(refCount * 5000, 10000), 45000);
      startTimerBar("memorize", memDuration, toRetrieveBtn);
      void renderMath(stageEls.memorize);
    });
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

export async function initRecallModule({ root, lernbereich, preferredCheckId = "" }) {
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
  const navNode = document.getElementById("dev-recall-jump-nav");
  const hasPreferred = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";

  const preferredSelected = hasPreferred ? byId.get(preferredCheckId.trim()) : null;
  const selectedCheckId =
    (preferredSelected && getCheckId(preferredSelected)) || state.selectedCheckId || getCheckId(checks[0]);
  state.selectedCheckId = selectedCheckId;
  saveRecallState(lernbereich, state);

  renderJumpNav(navNode, checks, selectedCheckId);
  root.innerHTML = checks.map((check) => renderCard(check)).join("");
  initCardMenuDismiss(root);
  bindJumpNavScrollSync(navNode, root.querySelectorAll("[data-recall-check-viewport][data-check-id]"));
  applyInitialReveal(root);
  initInteractiveRecallCards(root);
  enhanceSpeechInputs(root, ".recall-input-slot");
  bindCheckPositionPersistence(root, lernbereich, state);
  await renderMath(root);
}
