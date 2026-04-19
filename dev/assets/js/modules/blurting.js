import { getChecksByLernbereich } from "../data/checks-repo.js";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { renderCardActionsMenuMarkup, renderCardMenuLinkMarkup, initCardMenuDismiss } from "./ui/card-actions-menu.js";

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

const BL_RECALL_DELAY_MS = 30000;

function renderCard(check) {
  const begriff = check?.blurting?.begriff || check.Schlagwort || `Check ${check.Nummer}`;
  const ichKann = check?.["Ich kann"] || "";
  const checkId = getCheckId(check);
  const cardAnchorId = getCheckCardAnchorId(checkId);
  const checkNummer = formatCheckNumber(check?.Nummer);
  const scriptHref = buildScriptInfoHref(check);
  const refs = Array.isArray(check?.Tipps) ? check.Tipps : [];
  const refsListMarkup = refs
    .map((ref) => `<div class="bl-list-item"><span class="bl-list-dot"></span><span class="bl-list-text">${escapeHtml(ref)}</span></div>`)
    .join("");
  const refsKwMarkup = refs
    .map((ref) => `<span class="bl-kw"><span class="bl-kwdot"></span>${escapeHtml(ref)}</span>`)
    .join("");
  const noRefsNote = `<p class="bl-no-refs">Keine Kernpunkte hinterlegt.</p>`;

  const skriptMenuItem = scriptHref
    ? renderCardMenuLinkMarkup({ emoji: "📖", label: "Im Skript nachschlagen", href: scriptHref })
    : "";
  const actionsMenu = skriptMenuItem ? renderCardActionsMenuMarkup(skriptMenuItem) : "";

  return `
    <section id="${escapeHtml(cardAnchorId)}" class="check-viewport-item check-viewport-item--scroll-card check-viewport-item--narrow" data-bl-check-viewport data-check-id="${escapeHtml(
    checkId
  )}" data-bl-ref-count="${refs.length}">
      <article class="dev-check-card dev-check-card--blurting" data-bl-card>
        <div class="dev-check-card__header">
          ${renderCheckMetaRowMarkup({
    numberText: checkNummer,
    titleText: begriff,
    prefix: "Blurting",
    tone: "blurting",
    rowClass: "dev-check-card__header-left",
    titleTag: "span",
  })}
          <div class="dev-check-card__header-actions">
            ${actionsMenu}
          </div>
        </div>
        <div class="dev-check-card__body">
<div style="font-size: 72px; text-align: center;">💭</div>
        <div data-bl-stage="recall">
          <div data-bl-recall-idle>
            <p class="bl-prompt">Was fällt dir zu folgender Kompetenz ein?</p>
            <div class="bl-action-row">
              <button class="bl-reveal-btn" type="button" data-bl-start>Start</button>
            </div>
          </div>
          <div data-bl-recall-active hidden>
            <p class="bl-kompetenz">${escapeHtml(ichKann.replace(/\.$/, ''))}</p>
            <div class="bl-timer-bar" data-bl-timer-bar="recall">
              <div class="bl-timer-bar__fill" data-bl-timer-fill="recall"></div>
            </div>
            <div class="bl-action-row">
              <button class="bl-reveal-btn bl-reveal-btn--locked" type="button" data-bl-to-memorize disabled>Weiter</button>
            </div>
          </div>
        </div>

        <div data-bl-stage="memorize" hidden>
          <p class="bl-prompt">Präge dir die folgenden Kernpunkte ein.</p>
          <div class="bl-timer-bar" data-bl-timer-bar="memorize">
            <div class="bl-timer-bar__fill" data-bl-timer-fill="memorize"></div>
          </div>
          ${refs.length ? `<div class="bl-list-items">${refsListMarkup}</div>` : noRefsNote}
          <div class="bl-action-row">
            <button class="bl-reveal-btn bl-reveal-btn--locked" type="button" data-bl-to-retrieve disabled>Weiter</button>
          </div>
        </div>

        <div data-bl-stage="retrieve" hidden>
          <p class="bl-prompt">Schreibe die wichtigsten Punkte aus dem Gedächtnis auf.</p>
          <div class="bl-input-slots" data-bl-input-slots>
            ${(refs.length ? refs : [""]).map((_, i) => `<input class="bl-input-slot" type="text" data-bl-slot="${i}" placeholder="Punkt ${i + 1}">`).join("")}
          </div>
          <div class="bl-action-row">
            <button class="bl-reveal-btn" type="button" data-bl-to-compare>Jetzt vergleichen</button>
          </div>
        </div>

        <div data-bl-stage="compare" hidden>
          <div class="bl-divider">
            <hr><span>Deine Notizen</span><hr>
          </div>
          <div class="bl-user-notes" data-bl-user-notes></div>
          <div class="bl-divider">
            <hr><span>Kernpunkte</span><hr>
          </div>
          ${refs.length ? `<div class="bl-kws">${refsKwMarkup}</div>` : noRefsNote}
          <p class="bl-selbst-lbl">Wie vollständig war dein Abruf?</p>
          <div class="bl-selbst-btns">
            <button class="bl-sb yes" type="button" data-bl-answer="yes">
              <span class="bl-sb-icon">✓</span>
              <span class="bl-sb-title">Kann ich</span>
              <span class="bl-sb-sub">Die wichtigsten Punkte waren da.</span>
            </button>
            <button class="bl-sb no" type="button" data-bl-answer="no">
              <span class="bl-sb-icon">↺</span>
              <span class="bl-sb-title">Noch nicht</span>
              <span class="bl-sb-sub">Ich präge mir die Kernpunkte nochmal ein.</span>
            </button>
          </div>
        </div>

        <div data-bl-stage="result-yes" hidden>
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
    const section = card.closest("[data-bl-check-viewport]");
    const refCount = Number(section?.dataset?.blRefCount) || 3;

    const stageEls = {
      recall: card.querySelector('[data-bl-stage="recall"]'),
      memorize: card.querySelector('[data-bl-stage="memorize"]'),
      retrieve: card.querySelector('[data-bl-stage="retrieve"]'),
      compare: card.querySelector('[data-bl-stage="compare"]'),
      resultYes: card.querySelector('[data-bl-stage="result-yes"]'),
    };

    const recallIdle = card.querySelector("[data-bl-recall-idle]");
    const recallActive = card.querySelector("[data-bl-recall-active]");
    const startBtn = card.querySelector("[data-bl-start]");
    const toMemorizeBtn = card.querySelector("[data-bl-to-memorize]");
    const toRetrieveBtn = card.querySelector("[data-bl-to-retrieve]");
    const toCompareBtn = card.querySelector("[data-bl-to-compare]");
    const inputSlots = card.querySelector("[data-bl-input-slots]");
    const userNotesEl = card.querySelector("[data-bl-user-notes]");

    function setStage(name) {
      for (const [key, el] of Object.entries(stageEls)) {
        if (el) el.hidden = key !== name;
      }
    }

    function startTimerBar(scope, durationMs, btn) {
      const fill = card.querySelector(`[data-bl-timer-fill="${scope}"]`);
      if (fill) {
        fill.style.transition = "none";
        fill.style.width = "100%";
        void fill.offsetWidth;
        fill.style.transition = `width ${durationMs}ms linear`;
        fill.style.width = "0%";
      }
      if (btn) {
        btn.disabled = true;
        btn.classList.add("bl-reveal-btn--locked");
        setTimeout(() => {
          btn.disabled = false;
          btn.classList.remove("bl-reveal-btn--locked");
        }, durationMs);
      }
    }

    // Start button → reveal Kompetenz + timer
    startBtn?.addEventListener("click", () => {
      if (recallIdle) recallIdle.hidden = true;
      if (recallActive) recallActive.hidden = false;
      void renderMath(recallActive);
      startTimerBar("recall", BL_RECALL_DELAY_MS, toMemorizeBtn);
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
        inputSlots.querySelectorAll(".bl-input-slot").forEach((el) => { el.value = ""; });
      }
      setStage("retrieve");
      const first = inputSlots?.querySelector(".bl-input-slot");
      first?.focus();
    });

    // Phase 3 → 4 (compare + self-assess)
    toCompareBtn?.addEventListener("click", () => {
      if (userNotesEl && inputSlots) {
        const entries = Array.from(inputSlots.querySelectorAll(".bl-input-slot"))
          .map((el) => el.value.trim())
          .filter(Boolean);
        userNotesEl.innerHTML = entries.length
          ? `<div class="bl-user-entries">${entries.map((e) => `<span class="bl-kw bl-kw--user"><span class="bl-kwdot"></span>${escapeHtml(e)}</span>`).join("")}</div>`
          : `<p class="bl-no-refs">Keine Notizen eingegeben.</p>`;
      }
      setStage("compare");
      void renderMath(stageEls.compare);
    });

    // "Kann ich" → result
    card.querySelector('[data-bl-answer="yes"]')?.addEventListener("click", () => {
      setStage("resultYes");
    });

    // "Noch nicht" → back to memorize
    card.querySelector('[data-bl-answer="no"]')?.addEventListener("click", () => {
      setStage("memorize");
      const memDuration = Math.min(Math.max(refCount * 5000, 10000), 45000);
      startTimerBar("memorize", memDuration, toRetrieveBtn);
      void renderMath(stageEls.memorize);
    });
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
  initCardMenuDismiss(root);
  bindJumpNavScrollSync(navNode, root.querySelectorAll("[data-bl-check-viewport][data-check-id]"));
  applyInitialReveal(root);
  initInteractiveBlurtingCards(root);
  bindCheckPositionPersistence(root, lernbereich, state);
  await renderMath(root);
}
