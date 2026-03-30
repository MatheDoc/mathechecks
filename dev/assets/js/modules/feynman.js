import { getChecksByLernbereich } from "../data/checks-repo.js";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";

const FY_TOTAL_SECONDS = 300;
const FY_BEISPIEL_CACHE = new Map();
const FY_RING_CIRCUMFERENCE = 2 * Math.PI * 20;
const FY_STATE_PREFIX = "dev-feynman-state-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.dev.tabScope.v1";
const feynmanJumpNavScrollCleanup = new WeakMap();

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
  return `${FY_STATE_PREFIX}::${getTabScopeId()}::${lernbereich || "unknown"}`;
}

function loadFeynmanState(lernbereich) {
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

function saveFeynmanState(lernbereich, state) {
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
  return `fy-check-${toDomIdFragment(checkId) || "item"}`;
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

function buildBeispielUrl(check) {
  const nummer = String(Number(check.Nummer) || 0).padStart(2, "0");
  const sammlung = String(check.Sammlung || "").trim();
  const gebiet = String(check.Gebiet || "").trim();
  const lernbereich = String(check.Lernbereich || "").trim();
  if (!sammlung || !gebiet || !lernbereich) return "";
  return `/dev/lernbereiche/${gebiet}/${lernbereich}/beispiele/${nummer}-${sammlung}.html`;
}

async function fetchBeispielHtml(check) {
  const url = buildBeispielUrl(check);
  if (!url) return "";
  if (FY_BEISPIEL_CACHE.has(url)) return FY_BEISPIEL_CACHE.get(url);
  try {
    const resp = await fetch(url);
    if (!resp.ok) { FY_BEISPIEL_CACHE.set(url, ""); return ""; }
    const html = (await resp.text()).trim();
    FY_BEISPIEL_CACHE.set(url, html);
    return html;
  } catch {
    FY_BEISPIEL_CACHE.set(url, "");
    return "";
  }
}

function getEvaluationExamplePlaceholder() {
  return `<div data-fy-beispiel-slot class="fy-beispiel-loading"><p style="margin:0;color:var(--text-muted);font-size:.82rem;">Beispiel wird geladen…</p></div>`;
}

async function hydrateBeispielSlots(root, checks) {
  const slots = root.querySelectorAll("[data-fy-beispiel-slot]");
  const tasks = Array.from(slots).map(async (slot, i) => {
    const check = checks[i];
    if (!check) return;
    const html = await fetchBeispielHtml(check);
    if (html) {
      slot.innerHTML = html;
      slot.classList.remove("fy-beispiel-loading");
      await renderMath(slot);
    } else {
      slot.innerHTML = `<p style="margin:0;color:var(--text-dim);line-height:1.55;">Kein Auswertungsbeispiel fuer diesen Check hinterlegt.</p>`;
      slot.classList.remove("fy-beispiel-loading");
    }
  });
  await Promise.all(tasks);
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
  if (!path.endsWith("feynman.html")) return "";
  const scriptPageHref = path.replace(/feynman\.html$/, "skript.html");
  const explicitAnchor = check?.skript_anchor ?? check?.SkriptAnchor ?? check?.skriptAnchor ?? "";
  if (typeof explicitAnchor === "string" && explicitAnchor.trim()) {
    return `${scriptPageHref}#${encodeURIComponent(explicitAnchor.trim())}`;
  }
  const key = String(check?.info_key ?? check?.InfoKey ?? (Number.isFinite(Number(check?.Nummer)) ? String(Number(check.Nummer)) : "") ?? "");
  const slug = toSlug(key);
  if (!slug) return "";
  return `${scriptPageHref}#${encodeURIComponent(`check-${slug}`)}`;
}

function cleanIchKannStatement(rawText) {
  const text = String(rawText || "").trim();
  if (!text) return "";
  return text
    .replace(/^ich\s+kann\s+/i, "")
    .replace(/[.!?]+\s*$/g, "")
    .trim();
}

function splitTrailingParenthesis(text) {
  const trimmed = String(text || "").trim();
  if (!trimmed) return { core: "", trailing: "" };

  const match = trimmed.match(/\s*(\([^()]*\))\s*$/);
  if (!match) {
    return { core: trimmed, trailing: "" };
  }

  const trailing = match[1].trim();
  const core = trimmed.slice(0, match.index).trim();
  return { core, trailing };
}

function buildFeynmanPromptFromIchKann(check) {
  const ichKannRaw = check?.["Ich kann"];
  const cleaned = cleanIchKannStatement(ichKannRaw);
  if (!cleaned) {
    const legacyPrompt = String(check?.feynman?.prompt || "").trim();
    return legacyPrompt || `Erkläre in einfachen Worten, Schritt für Schritt und anhand eines Beispiels wie man diesen Inhalt erklären kann.`;
  }

  const { core, trailing } = splitTrailingParenthesis(cleaned);
  let action = core;

  if (!/\bkann\b/i.test(core)) {
    action = `${core} kann`;
  }

  if (trailing) {
    return `Erkläre in einfachen Worten, Schritt für Schritt und anhand eines Beispiels wie man ${action} ${trailing}.`;
  }

  return `Erkläre in einfachen Worten, Schritt für Schritt und anhand eines Beispiels wie man ${action}.`;
}

function convertJsonLatexToMarkdown(text) {
  return String(text || "")
    .replace(/\\\((.+?)\\\)/g, (_, m) => `$${m}$`)
    .replace(/\\\[(.+?)\\\]/gs, (_, m) => `$$${m}$$`);
}

function htmlToPlainText(html) {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  return tmp.textContent || "";
}

function buildKiAgentPrompt(check, beispielHtml) {
  const schlagwort = check.Schlagwort || `Check ${check.Nummer}`;
  const lernbereich = check.LernbereichAnzeigename || check.Lernbereich || "";
  const ichKann = check["Ich kann"] || "";
  const cleaned = cleanIchKannStatement(ichKann);

  const tipps = Array.isArray(check.Tipps) ? check.Tipps : [];
  const blurting = Array.isArray(check.Blurting) ? check.Blurting : [];

  const tippsBlock = tipps.length > 0
    ? `Folgende Stichpunkte sollte eine vollständige Erklärung abdecken:\n${tipps.map(t => `- ${convertJsonLatexToMarkdown(t)}`).join("\n")}`
    : "";

  const blurtingBlock = blurting.length > 0
    ? `\nWichtige Fachbegriffe, die vorkommen sollten:\n${blurting.map(b => `- ${convertJsonLatexToMarkdown(b)}`).join("\n")}`
    : "";

  const beispielText = beispielHtml
    ? htmlToPlainText(beispielHtml).trim()
    : "";
  const beispielBlock = beispielText
    ? `\n# Referenzbeispiel (nur intern – NICHT dem Lernenden zeigen)\n${beispielText}`
    : "";

  return `# Rolle
Du bist ein freundlicher, neugieriger Mitschüler. Du verstehst das Thema
noch NICHT und möchtest es anhand eines konkreten Beispiels erklärt
bekommen. Du sprichst Deutsch und duzt dein Gegenüber.

# Thema
Check: ${schlagwort}
Lernbereich: ${lernbereich}
Lernziel: Ich kann ${convertJsonLatexToMarkdown(ichKann)}

# Dein Wissen (nur intern – NICHT dem Lernenden zeigen)
${tippsBlock}${blurtingBlock}${beispielBlock}

# Regeln
1. Erkläre NICHTS selbst. Du bist der Zuhörer, nicht der Lehrer.
2. Bitte den Lernenden, sich ein eigenes Beispiel auszudenken oder eines
   aus dem Unterricht zu nehmen und dir Schritt für Schritt zu erklären.
3. Stelle nach jedem Erklärungsschritt genau EINE Rückfrage – z. B. zu
   einem Rechenschritt, einer Begriffsverwendung oder einer Begründung.
4. Variiere deine Reaktionen: kurze Bestätigungen, Nachfassen,
   Verständnisfragen. Wiederhole dich nicht.
5. Gib KEINE Hinweise, die die Antwort verraten.
6. Bleib natürlich und neugierig, aber nicht übertrieben lobend.
7. Antworte immer auf Deutsch.

# Ablauf
## Phase 1 – Start
Begrüße den Lernenden und bitte ihn, dir anhand eines selbst gewählten
Beispiels zu erklären, wie man ${cleaned || "diesen Inhalt anwendet"}.

## Phase 2 – Gemeinsam durch das Beispiel (3–5 Runden)
- Lass den Lernenden das Beispiel Schritt für Schritt durchgehen.
- Frage bei jedem Schritt nach dem Warum oder bitte um eine
  Veranschaulichung, wenn etwas unklar ist.
- Orientiere dich an den internen Stichpunkten. Wenn ein Aspekt im
  Beispiel noch nicht aufgetaucht ist, lenke mit einer natürlichen
  Frage dorthin, OHNE die Antwort zu verraten.

## Phase 3 – Zusammenfassung
Wenn das Beispiel durchgearbeitet ist ODER nach 5 Runden:
1. Fasse in 2–3 Sätzen zusammen, was du jetzt verstanden hast.
2. Benenne offen, welche Punkte noch unklar geblieben sind.
3. Gib eine ehrliche Einschätzung:
   ✅ Gut erklärt: [Punkte]
   ❓ Noch unklar / fehlend: [Punkte]
`;
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

function renderCard(check) {
  const prompt = buildFeynmanPromptFromIchKann(check);
  const titel = check.Schlagwort || `Check ${check.Nummer}`;
  const checkId = getCheckId(check);
  const cardAnchorId = getCheckCardAnchorId(checkId);
  const checkNummer = formatCheckNumber(check?.Nummer);
  const scriptHref = buildScriptInfoHref(check);
  const evaluationExampleMarkup = getEvaluationExamplePlaceholder();

  const skriptIcon = scriptHref
    ? `<a class="dev-check-card__action-btn" href="${escapeHtml(scriptHref)}" title="Im Skript nachschlagen" aria-label="Im Skript nachschlagen"><i class="fa-solid fa-book-open" aria-hidden="true"></i></a>`
    : "";

  return `
    <section id="${escapeHtml(cardAnchorId)}" class="check-viewport-item check-viewport-item--scroll-card check-viewport-item--narrow" data-fy-check-viewport data-check-id="${escapeHtml(
    checkId
  )}">
      <article class="dev-check-card dev-check-card--feynman" data-fy-card>
        <div class="dev-check-card__header">
          ${renderCheckMetaRowMarkup({
    numberText: checkNummer,
    titleText: titel,
    prefix: "Check",
    tone: "feynman",
    rowClass: "dev-check-card__header-left",
    titleTag: "span",
  })}
          <div class="dev-check-card__header-actions">
            ${skriptIcon}
            <button type="button" class="dev-check-card__action-btn dev-check-card__stats-btn" title="Noch keine Statistik vorhanden" aria-label="Statistik"><i class="fa-solid fa-chart-simple" aria-hidden="true"></i></button>
          </div>
        </div>
        <div class="dev-check-card__body">
        <p class="fy-prompt-text" style="margin-bottom:6px;">${escapeHtml(prompt)}</p>
        <p class="fy-prompt-hint">Schreib zuerst deine Erklärung. Nach Ablauf der Zeit bekommst du ein Auswertungsbeispiel.</p>

        <div data-fy-stage="write">
          <div class="fy-timer-row">
            <div class="fy-ring">
              <svg width="50" height="50" viewBox="0 0 50 50">
                <circle class="fy-track" cx="25" cy="25" r="20" />
                <circle class="fy-arc" data-fy-arc cx="25" cy="25" r="20" stroke-dasharray="${FY_RING_CIRCUMFERENCE.toFixed(
    2
  )}" stroke-dashoffset="0" />
              </svg>
              <span class="fy-ring-num" data-fy-num>${formatTimer(FY_TOTAL_SECONDS)}</span>
            </div>
            <div>
              <div style="font-size:.82rem;font-weight:600;color:var(--text);margin-bottom:2px;">Erklärungszeit</div>
              <div style="font-size:.72rem;color:var(--text-muted);">Schreib in eigenen Worten, danach folgt der Abgleich.</div>
            </div>
            <button class="bl-reveal-btn fy-reveal-btn" type="button" data-fy-reveal>Jetzt auswerten</button>
            <button class="bl-reveal-btn fy-ki-btn" type="button" data-fy-ki-copy title="KI-Lernpartner in die Zwischenablage kopieren – füge den Text in eine KI deiner Wahl ein">✨ KI-Lernpartner</button>
          </div>

          <textarea
            class="fy-write"
            data-fy-input
            placeholder="Erkläre den Lösungsweg so, dass ein Mitschüler ihn versteht."></textarea>
        </div>

        <div data-fy-stage="evaluate" hidden>
          <p style="font-size:.88rem;color:var(--text-dim);line-height:1.6;margin-bottom:14px;">Vergleiche deine Erklärung mit dem Auswertungsbeispiel.</p>
          <div style="margin-bottom:20px;">${evaluationExampleMarkup}</div>
          <p class="bl-selbst-lbl">Konntest du es schlüssig erklären?</p>
          <div class="bl-selbst-btns">
            <button class="bl-sb yes" type="button" data-fy-answer="yes">
              <span class="bl-sb-icon">✓</span>
              <span class="bl-sb-title">Kann ich</span>
              <span class="bl-sb-sub">Ich habe die Kerngedanken getroffen.</span>
            </button>
            <button class="bl-sb no" type="button" data-fy-answer="no">
              <span class="bl-sb-icon">↺</span>
              <span class="bl-sb-title">Noch nicht</span>
              <span class="bl-sb-sub">Ich brauche noch Wiederholung.</span>
            </button>
          </div>
        </div>

        <div data-fy-stage="result-yes" hidden>
          <div class="outcome">
            <div class="oc-icon violet">🎓</div>
            <h3 class="oc-title violet">Stark erklärt</h3>
            <p class="oc-sub">Du kannst den Inhalt bereits verständlich erklären.</p>
          </div>
        </div>

        <div data-fy-stage="result-no" hidden>
          <div class="outcome">
            <div class="oc-icon amber">📖</div>
            <h3 class="oc-title amber">Guter Zwischenstand</h3>
            <p class="oc-sub">Nutze das Skript zur Wiederholung und versuche es danach erneut.</p>
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
      const label = `${nummer}. ${check.Schlagwort || "Check"}`;
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

  const existingCleanup = feynmanJumpNavScrollCleanup.get(navNode);
  if (typeof existingCleanup === "function") {
    existingCleanup();
    feynmanJumpNavScrollCleanup.delete(navNode);
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

  feynmanJumpNavScrollCleanup.set(navNode, () => {
    scrollSource.removeEventListener("scroll", onViewportChange);
    window.removeEventListener("resize", onViewportChange);
  });
}

function initInteractiveFeynmanCards(root, checks) {
  const cards = root.querySelectorAll("[data-fy-card]");

  cards.forEach((card, index) => {
    const check = checks[index];
    const stages = {
      write: card.querySelector('[data-fy-stage="write"]'),
      evaluate: card.querySelector('[data-fy-stage="evaluate"]'),
      resultYes: card.querySelector('[data-fy-stage="result-yes"]'),
      resultNo: card.querySelector('[data-fy-stage="result-no"]'),
    };

    const timerLabel = card.querySelector("[data-fy-num]");
    const timerArc = card.querySelector("[data-fy-arc]");
    const revealButton = card.querySelector("[data-fy-reveal]");

    let secondsLeft = FY_TOTAL_SECONDS;
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
      const fraction = Math.max(0, Math.min(1, secondsLeft / FY_TOTAL_SECONDS));
      timerArc.style.strokeDashoffset = String(FY_RING_CIRCUMFERENCE * (1 - fraction));
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

    function setResult(canExplain) {
      clearTimer();
      setStage(canExplain ? "result-yes" : "result-no");
    }

    revealButton?.addEventListener("click", revealEvaluation);
    card.querySelector('[data-fy-answer="yes"]')?.addEventListener("click", () => setResult(true));
    card.querySelector('[data-fy-answer="no"]')?.addEventListener("click", () => setResult(false));

    const kiButton = card.querySelector("[data-fy-ki-copy]");
    if (kiButton && check) {
      kiButton.addEventListener("click", async () => {
        kiButton.disabled = true;
        kiButton.textContent = "⏳ Wird erstellt…";
        try {
          const beispielHtml = await fetchBeispielHtml(check);
          const agentPrompt = buildKiAgentPrompt(check, beispielHtml);
          const ok = await copyToClipboard(agentPrompt);
          kiButton.textContent = ok ? "✅ Kopiert!" : "❌ Fehler";
          setTimeout(() => { kiButton.textContent = "✨ KI-Lernpartner"; }, 2000);
        } finally {
          kiButton.disabled = false;
        }
      });
    }

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
  const cards = root.querySelectorAll("[data-fy-check-viewport][data-check-id]");
  cards.forEach((card) => {
    const checkId = card.getAttribute("data-check-id") || "";
    if (!checkId) return;

    const remember = () => {
      state.selectedCheckId = checkId;
      saveFeynmanState(lernbereich, state);
    };

    card.addEventListener("pointerdown", remember);
    card.addEventListener("focusin", remember);
    card.addEventListener("click", remember);
  });
}

export async function initFeynmanModule({ root, lernbereich, preferredCheckId = "" }) {
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
  const state = loadFeynmanState(lernbereich);
  const navNode = document.getElementById("dev-feynman-jump-nav");
  const hasPreferred = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";

  const preferredSelected = hasPreferred ? byId.get(preferredCheckId.trim()) : null;
  const selectedCheckId =
    (preferredSelected && getCheckId(preferredSelected)) || state.selectedCheckId || getCheckId(checks[0]);
  state.selectedCheckId = selectedCheckId;
  saveFeynmanState(lernbereich, state);

  renderJumpNav(navNode, checks, selectedCheckId);
  root.innerHTML = checks.map((check) => renderCard(check)).join("");
  bindJumpNavScrollSync(navNode, root.querySelectorAll("[data-fy-check-viewport][data-check-id]"));
  applyInitialReveal(root);
  initInteractiveFeynmanCards(root, checks);
  bindCheckPositionPersistence(root, lernbereich, state);
  await renderMath(root);
  await hydrateBeispielSlots(root, checks);
}
