import { getChecksByLernbereich } from "../data/checks-repo.js";
import { recordCheckFeedDecision } from "../platform/feed-actions.js?v=20260521-flashcards-review-save";
import { fetchBeispielHtml as fetchSharedBeispielHtml } from "./beispiel-loader.js?v=20260514-beispiel-url-d";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { renderCardActionsMenuMarkup, initCardMenuDismiss, runCardMenuItemFeedbackAction } from "./ui/card-actions-menu.js";
import { attachFeedCardControls, leaveFeedContext } from "./ui/feed-card-controls.js?v=20260521-feed-deterministic-tabs";
import { enhanceCheckJumpNav } from "./ui/check-jump-nav.js";
import { initSkriptVisuals } from "./skript-visuals.js";

const FY_BEISPIEL_CACHE = new Map();
const FY_STATE_PREFIX = "feynman-state-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.tabScope.v1";
const feynmanJumpNavScrollCleanup = new WeakMap();
const FEYNMAN_FEED_STEP_KEY = "feynman";

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

function resizePlotlyInNode(targetNode, retries = 4) {
  if (!targetNode || !window.Plotly?.Plots?.resize) return;

  const plots = Array.from(targetNode.querySelectorAll(".js-plotly-plot"));
  plots.forEach((plotNode) => {
    try {
      window.Plotly.Plots.resize(plotNode);
    } catch {
      // Retry while layout settles after stage visibility changes.
    }
  });

  if (retries <= 0) return;
  window.setTimeout(() => {
    resizePlotlyInNode(targetNode, retries - 1);
  }, 120);
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

function applyInitialReveal(root) {
  if (!root) return;
  root.classList.add("module-root--pending");
  // Small intentional delay to avoid a visible top flash during initial hydration.
  window.setTimeout(() => {
    root.classList.add("module-root--ready");
  }, 85);
}

const FEYNMAN_DELAY_MS = 1000;

async function fetchBeispielHtml(check) {
  return fetchSharedBeispielHtml(check, FY_BEISPIEL_CACHE);
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
      initSkriptVisuals(slot);
      await renderMath(slot);
    } else {
      slot.innerHTML = `<p style="margin:0;color:var(--text-dim);line-height:1.55;">Kein Auswertungsbeispiel fuer diesen Check hinterlegt.</p>`;
      slot.classList.remove("fy-beispiel-loading");
    }
  });
  await Promise.all(tasks);
}

function cleanIchKannStatement(rawText) {
  const text = String(rawText || "").trim();
  if (!text) return "";
  return text
    .replace(/^ich\s+kann\s+/i, "")
    .replace(/[.!?]+\s*$/g, "")
    .trim();
}

const FEYNMAN_PROMPT_STEPS = [
  "in einfachen Worten",
  "Schritt für Schritt",
  "anhand eines Beispiels.",
];
const FEYNMAN_EXPLAIN_PROMPT = "Erkläre jemandem diese Kompetenz";

function buildFeynmanPromptListMarkup() {
  const stepsMarkup = FEYNMAN_PROMPT_STEPS
    .map((step) => `<li class="fy-prompt-list-item"><span class="fy-prompt-list-icon" aria-hidden="true">•</span><span>${escapeHtml(step)}</span></li>`)
    .join("");
  return `
    <ul class="fy-prompt-list">
      ${stepsMarkup}
    </ul>
  `;
}

function buildFeynmanActionFromIchKann(check) {
  const ichKannRaw = check?.["Ich kann"];
  const cleaned = cleanIchKannStatement(ichKannRaw);
  if (!cleaned) {
    return "diesen Inhalt erklären kann";
  }
  return `${cleaned} kann`;
}

function convertJsonLatexToMarkdown(text) {
  return String(text || "")
    .replace(/\\\((.+?)\\\)/g, (_, m) => `$${m}$`)
    .replace(/\\\[(.+?)\\\]/gs, (_, m) => `$$${m}$$`);
}

function extractGraphDescriptions(container) {
  const parts = [];

  // ── .graph-auto (Analysis function graphs) ──
  container.querySelectorAll(".graph-auto").forEach((g) => {
    const lines = [];
    const titel = g.dataset.titel;
    if (titel) lines.push(`Diagramm: ${titel}`);

    const xachse = g.dataset.xachse;
    const yachse = g.dataset.yachse;
    if (xachse) lines.push(`x-Achse: ${xachse}`);
    if (yachse) lines.push(`y-Achse: ${yachse}`);

    try {
      const fns = JSON.parse(g.dataset.funktionen || "[]");
      if (fns.length > 0) {
        lines.push("Funktionen:");
        for (const f of fns) {
          const name = f.name || "";
          const term = f.term || "";
          const desc = f.beschreibung || "";
          lines.push(`  ${name ? name + ": " : ""}${term}${desc ? " (" + desc + ")" : ""}`);
        }
      }
    } catch { /* ignore */ }

    try {
      const pts = JSON.parse(g.dataset.punkte || "[]");
      if (pts.length > 0) {
        lines.push("Markierte Punkte:");
        for (const p of pts) {
          lines.push(`  (${p.x}, ${p.y})${p.text ? " – " + p.text : ""}`);
        }
      }
    } catch { /* ignore */ }

    try {
      const fl = JSON.parse(g.dataset.flaechen || "[]");
      if (fl.length > 0) {
        lines.push("Flächen:");
        for (const f of fl) {
          const desc = f.beschreibung || f.name || "";
          lines.push(`  ${desc}${f.von != null ? " von x=" + f.von : ""}${f.bis != null ? " bis x=" + f.bis : ""}`);
        }
      }
    } catch { /* ignore */ }

    if (lines.length > 0) parts.push(lines.join("\n"));
  });

  // ── .baumdiagramm-auto (Baumdiagramme) ──
  container.querySelectorAll(".baumdiagramm-auto").forEach((node) => {
    const lines = [];
    const titel = node.dataset.titel;
    if (titel) lines.push(`Baumdiagramm: ${titel}`);
    else lines.push("Baumdiagramm");
    const pa = node.dataset.pa;
    const pba = node.dataset.pba;
    const pbna = node.dataset.pbna;
    if (pa) lines.push(`  P(A) = ${pa}`);
    if (pba) lines.push(`  P_A(B) = ${pba}`);
    if (pbna) lines.push(`  P_A̅(B) = ${pbna}`);
    parts.push(lines.join("\n"));
  });

  // ── .verflechtungsdiagramm-auto ──
  container.querySelectorAll(".verflechtungsdiagramm-auto").forEach((node) => {
    const lines = ["Verflechtungsdiagramm"];
    try {
      const r = JSON.parse(node.dataset.rohstoffe || "[]");
      const z = JSON.parse(node.dataset.zwischenprodukte || "[]");
      const e = JSON.parse(node.dataset.endprodukte || "[]");
      if (r.length > 0) lines.push(`  Rohstoffe: ${r.join(", ")}`);
      if (z.length > 0) lines.push(`  Zwischenprodukte: ${z.join(", ")}`);
      if (e.length > 0) lines.push(`  Endprodukte: ${e.join(", ")}`);
    } catch { /* ignore */ }
    parts.push(lines.join("\n"));
  });

  // ── .histogramm-einzel-auto / .histogramm-kumuliert-auto ──
  container.querySelectorAll(".histogramm-einzel-auto, .histogramm-kumuliert-auto").forEach((node) => {
    const lines = [];
    const isKumuliert = node.classList.contains("histogramm-kumuliert-auto");
    const titel = node.dataset.titel;
    if (titel) lines.push(`Histogramm: ${titel}`);
    else lines.push(isKumuliert ? "Kumuliertes Histogramm" : "Histogramm (Einzelwahrscheinlichkeiten)");
    const n = node.dataset.n;
    const p = node.dataset.p;
    if (n) lines.push(`  n = ${n}`);
    if (p) lines.push(`  p = ${p}`);
    parts.push(lines.join("\n"));
  });

  return parts.join("\n\n");
}

function htmlToPlainText(html) {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  const graphText = extractGraphDescriptions(tmp);
  const plainText = tmp.textContent || "";
  return [plainText.trim(), graphText].filter(Boolean).join("\n\n");
}

function normalizeFeynmanFeedContext(activityContext) {
  if (!activityContext || activityContext.mode !== "feed") return null;
  return String(activityContext.activityStep || "").trim() === FEYNMAN_FEED_STEP_KEY
    ? { mode: "feed", activityStep: FEYNMAN_FEED_STEP_KEY }
    : null;
}

function attachFeynmanFeedShell(section, activityContext, { lernbereich = "" } = {}) {
  const feedContext = normalizeFeynmanFeedContext(activityContext);
  if (!section || !feedContext) return;

  const activityCard = section.querySelector("[data-fy-card]");
  const toEvaluateButton = activityCard?.querySelector("[data-fy-to-evaluate]") || null;
  const answerNoButton = activityCard?.querySelector('[data-fy-answer="no"]') || null;
  const controls = attachFeedCardControls(section, {
    cardSelector: "[data-fy-card]",
    stepLabel: "Feynman",
  });
  if (!controls) return;

  let canPrepare = false;
  let completed = false;
  let busy = false;
  let statusMessage = "Erkläre den Inhalt und öffne danach die Auswertung. Dann kannst du den Abschluss vorbereiten.";
  let statusTone = "neutral";

  const checkId = section.dataset.checkId || "";

  async function recordFeynmanCompletion() {
    return recordCheckFeedDecision({
      lernbereichSlug: lernbereich,
      checkId,
      moduleKey: "feynman",
      outcomeKey: "can_do",
    });
  }

  const enablePrepare = () => {
    if (completed) return;
    canPrepare = true;
    statusMessage = "Die Auswertung ist sichtbar. Du kannst den Feed-Abschluss vorbereiten.";
    statusTone = "neutral";
    renderControls();
  };

  const completeFeynmanDecision = async () => {
    if (busy) return;
    busy = true;
    statusMessage = "Der Feed-Schritt wird gespeichert.";
    statusTone = "neutral";
    renderControls();

    try {
      await recordFeynmanCompletion();
    } catch (error) {
      console.error("Feynman-Aktivität konnte nicht abgeschlossen werden:", error);
      busy = false;
      statusMessage = "Die Feynman-Aktivität konnte gerade nicht gespeichert werden.";
      statusTone = "error";
      renderControls();
      throw error;
    }

    completed = true;
    statusMessage = "Die Feynman-Aktivität wurde abgeschlossen. Die nächste Feed-Aktivität wird geöffnet.";
    statusTone = "success";
    renderControls();
  };

  const repeatFeynmanDecision = () => {
    canPrepare = false;
    statusMessage = "Die Feynman-Aktivität bleibt im Feed offen.";
    statusTone = "neutral";
    answerNoButton?.click();
    renderControls();
  };

  const openFeynmanDecision = () => {
    if (!controls?.openDecisionDialog || busy || completed || !canPrepare) return;

    controls.openDecisionDialog({
      title: "Feynman abschließen?",
      detail: "Nutze deine Auswertung als Maßstab für die Entscheidung.",
      onComplete: completeFeynmanDecision,
      onRepeat: repeatFeynmanDecision,
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
        onClick: openFeynmanDecision,
      },
    ];

    controls.render({
      status: statusMessage,
      tone: statusTone,
      items,
      ready: canPrepare && !busy && !completed,
    });
  }

  toEvaluateButton?.addEventListener("click", enablePrepare);
  renderControls();
}

function buildKiAgentPrompt(check, beispielHtml) {
  const schlagwort = check.Schlagwort || `Check ${check.Nummer}`;
  const lernbereich = check.LernbereichAnzeigename || check.Lernbereich || "";
  const ichKann = check["Ich kann"] || "";
  const cleaned = cleanIchKannStatement(ichKann);

  const tipps = Array.isArray(check.Tipps) ? check.Tipps : [];

  const tippsBlock = tipps.length > 0
    ? `\nWichtige Aspekte, die in einer guten Erklärung vorkommen könnten:\n${tipps.map(t => `- ${convertJsonLatexToMarkdown(t)}`).join("\n")}`
    : "";

  const beispielText = beispielHtml
    ? htmlToPlainText(beispielHtml).trim()
    : "";
  const beispielBlock = beispielText
    ? `\n# Referenzbeispiel\nOrientiere dich intern an diesem Beispiel, um passende Rückfragen zu stellen und Antworten einzuordnen. Zeige es NICHT direkt.\n\n${beispielText}`
    : "";

  return `# Rolle
Du bist ein KI-Lernpartner für die Feynman-Methode. Der Lernende soll dir ein Mathe-Thema erklären, und du hilfst ihm dabei, seine eigene Erklärung zu schärfen. Du sprichst Deutsch und duzt dein Gegenüber.

# Thema
Check: ${schlagwort}
Lernbereich: ${lernbereich}
Kompetenz: Ich kann ${convertJsonLatexToMarkdown(ichKann)}

# Dein Hintergrundwissen (nicht wörtlich wiedergeben)
${tippsBlock}${beispielBlock}

# Stil
- Reagiere natürlich und abwechslungsreich – mal kurz bestätigend,
  mal interessiert nachfragend, mal zusammenfassend.
- Lobe ruhig, wenn etwas gut erklärt ist – kurz und ehrlich.
- Du darfst leichte Denkanstöße geben, die in die richtige Richtung weisen, ohne die Antwort komplett zu verraten.
- Wenn der Lernende einen Fehler macht, korrigiere nicht sofort,
  sondern hake gezielt nach, damit er den Fehler selbst findet.
- Halte dich kurz. Keine langen Monologe.

# Ablauf
## Phase 1 – Einstieg
Begrüße den Lernenden kurz und steig direkt ins Thema ein.
Nimm Bezug auf die Kompetenz und frage konkret, wie man
${cleaned || "diesen Inhalt anwendet"}.
Zum Beispiel: „Okay, es geht um ${schlagwort} – wie geht man da vor?"

## Phase 2 – Erklärung begleiten (3–6 Runden)
- Lass den Lernenden erklären und begleite ihn Schritt für Schritt.
- Stelle nach jedem Erklärungsschritt eine gezielte Rückfrage –
  zum Rechenschritt, zur Begründung oder zu einem Begriff.
- Nutze dein Hintergrundwissen: Wenn ein wichtiger Aspekt fehlt,
  lenke mit einer Frage oder einem kleinen Hinweis dorthin.
- Wenn etwas richtig ist, bestätige es und geh zum nächsten Punkt.

## Phase 3 – Zusammenfassung
Wenn die wesentlichen Aspekte abgedeckt sind ODER nach 6 Runden:
1. Fasse zusammen, was gut erklärt wurde.
2. Benenne, was noch fehlt oder unklar war.
3. Gib eine kurze, ehrliche Einschätzung:
   ✅ Gut erklärt: [Punkte]
   ❓ Noch offen: [Punkte]
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

function renderCard(check, { includeSelfCheck = false } = {}) {
  const titel = check.Schlagwort || `Check ${check.Nummer}`;
  const ichKann = check?.["Ich kann"] || "";
  const competenceText = String(ichKann || titel).replace(/\.$/, "");
  const promptListMarkup = buildFeynmanPromptListMarkup();
  const checkId = getCheckId(check);
  const cardAnchorId = getCheckCardAnchorId(checkId);
  const checkNummer = formatCheckNumber(check?.Nummer);
  const evaluationExampleMarkup = getEvaluationExamplePlaceholder();
  const selfCheckMarkup = includeSelfCheck
    ? `
          <p class="module-flow-prompt module-flow-prompt--self-check">Konntest du es schlüssig erklären?</p>
          <div class="self-check-actions">
            <button class="self-check-button yes" type="button" data-fy-answer="yes">
              <span class="self-check-button__icon">✅</span>
              <span class="self-check-button__title">Kann ich</span>
              <span class="self-check-button__sub">Ich habe die Kerngedanken getroffen.</span>
            </button>
            <button class="self-check-button no" type="button" data-fy-answer="no">
              <span class="self-check-button__icon">🔄</span>
              <span class="self-check-button__title">Noch nicht</span>
              <span class="self-check-button__sub">Ich brauche noch Wiederholung.</span>
            </button>
          </div>`
    : "";

  const kiMenuItem = `<button type="button" class="check-card__actions-item" role="menuitem" data-fy-ki-menu><span class="check-card__actions-icon" aria-hidden="true">✨</span><span>KI-Lernpartner kopieren</span></button>`;
  const actionsMenu = renderCardActionsMenuMarkup(kiMenuItem);

  return `
    <section id="${escapeHtml(cardAnchorId)}" class="check-viewport-item check-viewport-item--scroll-card check-viewport-item--narrow" data-fy-check-viewport data-check-id="${escapeHtml(
    checkId
  )}">
      <article class="check-card check-card--feynman" data-fy-card>
        <div class="check-card__header">
          ${renderCheckMetaRowMarkup({
    numberText: checkNummer,
    titleText: titel,
    prefix: "Feynman",
    tone: "feynman",
    rowClass: "check-card__header-left",
    titleTag: "span",
  })}
          <div class="check-card__header-actions">
            ${actionsMenu}
          </div>
        </div>
        <div class="check-card__body">
        <div class="module-flow-focus">
          <p class="module-flow-competence">${escapeHtml(competenceText)}</p>
        </div>

        <div data-fy-stage="explain">
          <div data-fy-idle>
            <div class="module-flow-action-row">
              <button class="module-action-button" type="button" data-fy-start>Start</button>
            </div>
          </div>
          <div data-fy-active hidden>
            <p class="module-flow-prompt">${escapeHtml(FEYNMAN_EXPLAIN_PROMPT)}</p>
            ${promptListMarkup}
            <div class="module-flow-timer-bar" data-fy-timer-bar="explain">
              <div class="module-flow-timer-bar__fill" data-fy-timer-fill="explain"></div>
            </div>
            <div class="module-flow-action-row">
              <button class="module-action-button module-action-button--locked" type="button" data-fy-to-evaluate disabled>Selbstcheck starten</button>
            </div>
          </div>
        </div>

        <div data-fy-stage="evaluate" hidden>
          <p class="module-flow-prompt">Vergleiche deine Erklärung mit dem Auswertungsbeispiel.</p>
          <div style="margin-bottom:20px;">${evaluationExampleMarkup}</div>
          ${selfCheckMarkup}
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

  enhanceCheckJumpNav(navNode);

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

function revealEvaluationStage(stageEl) {
  if (!stageEl) return;

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const cardBody = stageEl.closest(".check-card")?.querySelector(".check-card__body");

  stageEl.classList.remove("is-revealed");
  void stageEl.offsetWidth;
  stageEl.classList.add("is-revealed");

  if (cardBody) {
    const bodyRect = cardBody.getBoundingClientRect();
    const stageRect = stageEl.getBoundingClientRect();
    const top = cardBody.scrollTop + (stageRect.top - bodyRect.top) - 10;

    cardBody.scrollTo({
      top: Math.max(0, top),
      behavior: prefersReducedMotion ? "auto" : "smooth",
    });
  }

  window.setTimeout(() => {
    stageEl.classList.remove("is-revealed");
  }, 900);
}

function initInteractiveFeynmanCards(root, checks, lernbereich, activityContext) {
  const cards = root.querySelectorAll("[data-fy-card]");

  cards.forEach((card, index) => {
    const check = checks[index];
    const checkId = check ? getCheckId(check) : "";
    const stages = {
      explain: card.querySelector('[data-fy-stage="explain"]'),
      evaluate: card.querySelector('[data-fy-stage="evaluate"]'),
      resultYes: card.querySelector('[data-fy-stage="result-yes"]'),
      resultNo: card.querySelector('[data-fy-stage="result-no"]'),
    };

    const explainIdle = card.querySelector("[data-fy-idle]");
    const explainActive = card.querySelector("[data-fy-active]");
    const startButton = card.querySelector("[data-fy-start]");
    const toEvaluateButton = card.querySelector("[data-fy-to-evaluate]");

    function setStage(nextStage) {
      stages.explain.hidden = nextStage !== "explain";
      stages.evaluate.hidden = nextStage !== "evaluate";
      stages.resultYes.hidden = nextStage !== "result-yes";
      stages.resultNo.hidden = nextStage !== "result-no";
    }

    function startTimerBar(scope, durationMs, btn) {
      const fill = card.querySelector(`[data-fy-timer-fill="${scope}"]`);
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

    function revealEvaluation() {
      setStage("evaluate");
      void renderMath(stages.evaluate);
      revealEvaluationStage(stages.evaluate);
      window.requestAnimationFrame(() => {
        resizePlotlyInNode(stages.evaluate);
      });
    }

    function setResult(canExplain) {
      setStage(canExplain ? "result-yes" : "result-no");
      if (activityContext?.mode === "feed") {
        void recordCheckFeedDecision({
          lernbereichSlug: lernbereich,
          checkId,
          moduleKey: "feynman",
          outcomeKey: canExplain ? "can_do" : "repeat",
        }).catch(() => {});
      }
    }

    startButton?.addEventListener("click", () => {
      if (explainIdle) explainIdle.hidden = true;
      if (explainActive) explainActive.hidden = false;
      void renderMath(explainActive);
      startTimerBar("explain", FEYNMAN_DELAY_MS, toEvaluateButton);
    });

    toEvaluateButton?.addEventListener("click", revealEvaluation);
    card.querySelector('[data-fy-answer="yes"]')?.addEventListener("click", () => setResult(true));
    card.querySelector('[data-fy-answer="no"]')?.addEventListener("click", () => setResult(false));

    const kiButton = card.querySelector("[data-fy-ki-menu]");
    if (kiButton && check) {
      kiButton.addEventListener("click", async (event) => {
        event.stopPropagation();
        await runCardMenuItemFeedbackAction(kiButton, {
          pendingLabel: "Wird erstellt…",
          successLabel: "Kopiert!",
          errorLabel: "Fehler",
          pendingIcon: "✨",
          action: async () => {
            const beispielHtml = await fetchBeispielHtml(check);
            const agentPrompt = buildKiAgentPrompt(check, beispielHtml);
            return copyToClipboard(agentPrompt);
          },
        });
      });
    }
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

export async function initFeynmanModule({ root, lernbereich, preferredCheckId = "", activityContext = null }) {
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
  const navNode = document.getElementById("feynman-jump-nav");
  const hasPreferred = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";

  const preferredSelected = hasPreferred ? byId.get(preferredCheckId.trim()) : null;
  const selectedCheckId =
    (preferredSelected && getCheckId(preferredSelected)) || state.selectedCheckId || getCheckId(checks[0]);
  state.selectedCheckId = selectedCheckId;
  saveFeynmanState(lernbereich, state);

  renderJumpNav(navNode, checks, selectedCheckId);
  root.innerHTML = checks
    .map((check) => renderCard(check, {
      includeSelfCheck: activityContext?.mode === "feed" && getCheckId(check) === selectedCheckId,
    }))
    .join("");
  const selectedSection = Array.from(root.querySelectorAll("[data-fy-check-viewport][data-check-id]"))
    .find((section) => section.dataset.checkId === selectedCheckId) || null;
  if (selectedSection) {
    attachFeynmanFeedShell(selectedSection, activityContext, { lernbereich });
    if (activityContext?.mode === "feed") {
      setJumpNavActive(navNode, selectedCheckId);
      selectedSection.scrollIntoView({ behavior: "auto", block: "start" });
    }
  }
  initCardMenuDismiss(root);
  bindJumpNavScrollSync(navNode, root.querySelectorAll("[data-fy-check-viewport][data-check-id]"));
  applyInitialReveal(root);
  initInteractiveFeynmanCards(root, checks, lernbereich, activityContext);
  bindCheckPositionPersistence(root, lernbereich, state);
  await renderMath(root);
  await hydrateBeispielSlots(root, checks);
}
