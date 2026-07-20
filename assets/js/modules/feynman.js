import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";
import { getAufgabenSammlung } from "../data/sammlungen-repo.js?v=20260614-expression-curves-b";
import { recordCheckFeedDecision } from "../platform/feed-actions.js?v=20260603-topbar-feed-badge";
import { recordUserActivity, getUserFeynmanProficiency, extractFeynmanProficiencyRate } from "../platform/progress-client.js?v=20260719-feynman-graph-fix";
import { getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js?v=20260520-feed-loading";
import { answerToSolution, replaceAnswerPlaceholders } from "../../../../aufgaben/runtime/answers.js?v=20260711-speech-textarea-fix";
import { renderVisual } from "../../../../aufgaben/runtime/task-visuals.js?v=20260614-expression-curves-b";
import { fetchBeispielHtml as fetchSharedBeispielHtml } from "./beispiel-loader.js?v=20260514-beispiel-url-d";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { renderCardActionsMenuMarkup, initCardMenuDismiss, runCardMenuItemFeedbackAction } from "./ui/card-actions-menu.js";
import { applyFeedFocusScope, attachFeedCardControls, attachFreeCompletionControl, leaveFeedContext } from "./ui/feed-card-controls.js?v=20260712-feed-focus";
import { enhanceCheckJumpNav } from "./ui/check-jump-nav.js";
import { enhanceSpeechInputs } from "./ui/speech-input.js?v=20260719-speech-cursor-insert";
import { showTaskCompletionPopup } from "./ui/task-completion-popup.js?v=20260719-feynman-quote";

const FY_BEISPIEL_CACHE = new Map();
const FY_STATE_PREFIX = "feynman-state-v1";
const TAB_SCOPE_SESSION_KEY = "mathechecks.tabScope.v1";
const feynmanJumpNavScrollCleanup = new WeakMap();
const FEYNMAN_FEED_STEP_KEY = "feynman";
const FEYNMAN_EVALUATION_TIMEOUT_MS = 75000;
const FEYNMAN_SCORE_THRESHOLDS = { good: 0.8, partial: 0.5 };
const FEYNMAN_RETRY_PENALTY = 0.5;

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

function updateFeynmanRateBadge(badgeEl, rate) {
  if (!badgeEl) return;
  if (rate === null || !Number.isFinite(rate)) {
    badgeEl.textContent = "–";
    badgeEl.removeAttribute("data-has-rate");
    return;
  }
  badgeEl.textContent = `${Math.round(rate)} %`;
  badgeEl.setAttribute("data-has-rate", "true");
}

function pickRandomTaskIndex(totalCount) {
  const count = Math.max(0, Number(totalCount) || 0);
  if (count <= 1) return 0;
  return Math.floor(Math.random() * count);
}

async function buildFeynmanCardEntries(checks) {
  return Promise.all(checks.map(async (check) => {
    try {
      const sammlung = await getAufgabenSammlung(check.Sammlung, {
        gebiet: check.Gebiet,
        lernbereich: check.Lernbereich,
      });
      const totalTasks = Array.isArray(sammlung) ? sammlung.length : 0;
      const scorableTasks = Array.isArray(sammlung)
        ? sammlung
          .map((task, index) => ({ task, index }))
          .filter(({ task }) => getFeynmanScorableItems(task).length > 0)
        : [];
      const selected = scorableTasks.length > 0
        ? scorableTasks[pickRandomTaskIndex(scorableTasks.length)]
        : { task: totalTasks > 0 ? sammlung[pickRandomTaskIndex(totalTasks)] : null, index: 0 };
      return {
        check,
        task: selected.task,
        taskIndex: selected.index,
        totalTasks,
        scorableTasks,
        error: "",
      };
    } catch (error) {
      return {
        check,
        task: null,
        taskIndex: 0,
        totalTasks: 0,
        scorableTasks: [],
        error: error?.message || "Aufgabe konnte nicht geladen werden.",
      };
    }
  }));
}

function applyInitialReveal(root) {
  if (!root) return;
  root.classList.add("module-root--pending");
  // Small intentional delay to avoid a visible top flash during initial hydration.
  window.setTimeout(() => {
    root.classList.add("module-root--ready");
  }, 85);
}

async function fetchBeispielHtml(check) {
  return fetchSharedBeispielHtml(check, FY_BEISPIEL_CACHE);
}

function cleanIchKannStatement(rawText) {
  const text = String(rawText || "").trim();
  if (!text) return "";
  return text
    .replace(/^ich\s+kann\s+/i, "")
    .replace(/[.!?]+\s*$/g, "")
    .trim();
}

function convertJsonLatexToMarkdown(text) {
  return String(text || "")
    .replace(/\\\((.+?)\\\)/g, (_, m) => `$${m}$`)
    .replace(/\\\[(.+?)\\\]/gs, (_, m) => `$$${m}$$`);
}

function normalizeTippForPrompt(raw) {
  if (raw && typeof raw === "object") {
    const cue = typeof raw.cue === "string" ? raw.cue.trim() : "";
    const response = typeof raw.response === "string" ? raw.response.trim() : "";
    return cue ? `${cue}: ${response}` : response;
  }
  return typeof raw === "string" ? raw : "";
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

function truncateText(value, maxLength = 1800) {
  const text = String(value || "").trim();
  return text.length > maxLength ? `${text.slice(0, maxLength)}…` : text;
}

function buildAnswerTargetText(answer) {
  const raw = String(answer || "").trim();
  if (!raw) return "";

  try {
    const solutionText = htmlToPlainText(answerToSolution(raw)).trim();
    if (solutionText) return solutionText;
  } catch {
    // Fall through to the raw answer text.
  }

  return htmlToPlainText(raw).trim();
}

function answerHasFeynmanInput(answer) {
  const raw = String(answer || "").trim();
  if (!raw || raw === "---") return false;

  let hasPlaceholder = false;
  try {
    replaceAnswerPlaceholders(raw, () => {
      hasPlaceholder = true;
      return "";
    });
  } catch {
    return false;
  }

  return hasPlaceholder;
}

function getFeynmanScorableItems(task) {
  const fragen = Array.isArray(task?.fragen) ? task.fragen : [];
  const antworten = Array.isArray(task?.antworten) ? task.antworten : [];
  const itemCount = Math.min(fragen.length, antworten.length);
  const items = [];

  for (let index = 0; index < itemCount; index += 1) {
    if (!answerHasFeynmanInput(antworten[index])) continue;

    const questionHtml = String(fragen[index] || `Teilfrage ${index + 1}`);
    const questionText = htmlToPlainText(questionHtml).trim() || `Teilfrage ${index + 1}`;
    const targetText = buildAnswerTargetText(antworten[index]);
    if (!targetText) continue;

    items.push({
      sourceIndex: index,
      questionHtml,
      questionText,
      targetText,
    });
  }

  return items;
}

function formatPromptProbability(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "";
  return number.toFixed(4);
}

function buildAbTreeVisualContext(spec) {
  const pa = Number(spec?.pa);
  const pba = Number(spec?.pba);
  const pbna = Number(spec?.pbna);
  if (![pa, pba, pbna].every(Number.isFinite)) return "";

  const pNotA = 1 - pa;
  const pNotBA = 1 - pba;
  const pNotBNotA = 1 - pbna;
  const givenSlots = new Set(Array.isArray(spec?.givenSlots) ? spec.givenSlots.map(Number) : []);
  const rows = [
    [1, "P(A)", pa],
    [2, "P(nicht A)", pNotA],
    [3, "P(B | A), oberer B-Ast nach A", pba],
    [4, "P(nicht B | A), Gegenast zu Punkt 3", pNotBA],
    [5, "P(B | nicht A), unterer B-Ast nach nicht A", pbna],
    [6, "P(nicht B | nicht A), Gegenast zu Punkt 5", pNotBNotA],
    [7, "P(A und B) = P(A) * P(B | A)", pa * pba],
    [8, "P(A und nicht B) = P(A) * P(nicht B | A)", pa * pNotBA],
    [9, "P(nicht A und B) = P(nicht A) * P(B | nicht A)", pNotA * pbna],
    [10, "P(nicht A und nicht B) = P(nicht A) * P(nicht B | nicht A)", pNotA * pNotBNotA],
  ];

  return [
    "Baumdiagramm mit nummerierten Punkten/Feldern:",
    ...rows.map(([slot, label, value]) => {
      const visibility = givenSlots.has(slot) ? " sichtbar/vorgegeben" : " zu bestimmen";
      return `- Punkt ${slot}: ${label} = ${formatPromptProbability(value)} (${visibility})`;
    }),
  ].join("\n");
}

function buildTaskVisualContext(task) {
  const spec = task?.visual?.spec;
  if (!spec || typeof spec !== "object") return "";

  try {
    const readableContext = spec.type === "ab-tree" ? buildAbTreeVisualContext(spec) : "";
    const rawContext = truncateText(JSON.stringify(spec), 6000);
    return [readableContext, rawContext ? `Rohdaten: ${rawContext}` : ""].filter(Boolean).join("\n\n");
  } catch {
    return "";
  }
}

function renderFeynmanTaskMarkup(entry, cardAnchorId) {
  const task = entry?.task || null;
  if (entry?.error) {
    return `<p class="module-status" style="color:var(--rose);">${escapeHtml(entry.error)}</p>`;
  }
  if (!task) {
    return `<p class="module-status">Keine Aufgabe in dieser Sammlung gefunden.</p>`;
  }

  const scorableItems = getFeynmanScorableItems(task);
  const questionItems = scorableItems.length > 0
    ? scorableItems.map(({ sourceIndex, questionHtml, questionText, targetText }) => {
      const inputId = `fy-input-${cardAnchorId}-${sourceIndex}`;
      return `
        <li class="qa-item fy-question-item" data-fy-question-item data-fy-question-nr="${sourceIndex + 1}" data-question="${escapeHtml(questionText)}" data-answer="${escapeHtml(targetText)}">
          <div class="frage">${questionHtml}</div>
          <div class="fy-response-cell">
              <textarea class="fy-explain-input answer-input" id="${escapeHtml(inputId)}" rows="1" maxlength="900" data-fy-response-slot="${sourceIndex}" aria-label="Erklärung zu Teilfrage ${sourceIndex + 1}" placeholder="Erkläre deinen Lösungsweg Schritt für Schritt ..."></textarea>
            <div class="task-feedback fy-inline-feedback" data-fy-feedback hidden></div>
          </div>
        </li>
      `;
    }).join("")
    : `<li class="qa-item"><p class="module-status">Keine auswertbaren Teilfragen gefunden.</p></li>`;

  return `
    <div class="fy-task check-card__runtime-task" data-fy-task data-task-index="${Number(entry?.taskIndex) || 0}">
      <div class="task-intro-column" data-fy-task-intro-column>
        <div class="intro">${task?.einleitung || ""}</div>
      </div>
      <ol class="qa-list" data-fy-question-list>
        ${questionItems}
      </ol>
    </div>
  `;
}

function hydrateFeynmanTaskVisuals(root, cardEntries) {
  const sections = Array.from(root.querySelectorAll("[data-fy-check-viewport][data-check-id]"));
  sections.forEach((section, index) => {
    const entry = cardEntries[index];
    const introColumn = section.querySelector("[data-fy-task-intro-column]");
    if (!entry?.task || !introColumn) return;
    renderVisual(entry.task, introColumn);
    requestAnimationFrame(() => resizePlotlyInNode(introColumn));
  });
}

function buildFeynmanEvaluationPayload({ check, task, itemEls, beispielHtml = "" }) {
  const tipps = Array.isArray(check?.Tipps) ? check.Tipps : [];
  const scorableItems = getFeynmanScorableItems(task);

  return {
    check: {
      schlagwort: check?.Schlagwort || `Check ${check?.Nummer ?? ""}`,
      lernbereich: check?.LernbereichAnzeigename || check?.Lernbereich || "",
      kompetenz: convertJsonLatexToMarkdown(check?.["Ich kann"] || ""),
      tipps: tipps.map((tipp) => convertJsonLatexToMarkdown(normalizeTippForPrompt(tipp))).filter(Boolean),
    },
    task: {
      einleitung: convertJsonLatexToMarkdown(truncateText(htmlToPlainText(task?.einleitung || ""), 6000)),
      visualContext: buildTaskVisualContext(task),
      fragen: scorableItems.map((item) => convertJsonLatexToMarkdown(truncateText(item.questionText, 900))),
      zielantworten: scorableItems.map((item) => convertJsonLatexToMarkdown(truncateText(item.targetText, 900))),
      beispiel: beispielHtml ? convertJsonLatexToMarkdown(truncateText(htmlToPlainText(beispielHtml), 6000)) : "",
    },
    items: Array.from(itemEls || []).map((el, index) => ({
      nr: index + 1,
      frage: el.dataset.question || `Teilfrage ${index + 1}`,
      zielantwort: el.dataset.answer || "",
      schueler_antwort: el.querySelector(".fy-explain-input")?.value.trim() || "",
    })),
  };
}

async function evaluateFeynmanItems(payload) {
  let timeoutId = null;
  try {
    const config = getSupabaseRuntimeConfig();
    const baseUrl = String(config.url || "").replace(/\/+$/, "");
    const anonKey = String(config.anonKey || "").trim();
    if (!baseUrl || !anonKey) return { error: "not-configured" };

    const supabase = await getSupabaseClient();
    const sessionResult = supabase ? await supabase.auth.getSession() : null;
    const accessToken = sessionResult?.data?.session?.access_token;
    if (!accessToken) {
      console.warn("MatheChecks: Feynman-Bewertung uebersprungen, kein aktives Login.");
      return { error: "not-authenticated" };
    }

    const controller = typeof AbortController === "function" ? new AbortController() : null;
    timeoutId = controller
      ? window.setTimeout(() => controller.abort(), FEYNMAN_EVALUATION_TIMEOUT_MS)
      : null;

    const response = await fetch(`${baseUrl}/functions/v1/feynman-evaluate`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        apikey: anonKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller?.signal,
    });

    if (!response.ok) {
      let errorBody = null;
      try { errorBody = await response.json(); } catch { /* ignore */ }
      console.warn("MatheChecks: Feynman-Bewertung fehlgeschlagen.", response.status, response.statusText);
      return { error: errorBody?.error || "evaluation-failed", maxItems: errorBody?.maxItems, status: response.status };
    }

    const data = await response.json();
    if (!data || !Array.isArray(data.results)) {
      return { error: "invalid-response" };
    }

    return data;
  } catch (error) {
    console.warn("MatheChecks: Feynman-Bewertung konnte nicht abgerufen werden.", error);
    if (error?.name === "AbortError") return { error: "timeout" };
    return { error: "evaluation-failed" };
  } finally {
    if (timeoutId !== null) window.clearTimeout(timeoutId);
  }
}

function computeFeynmanAttemptScore(rawScore, attempts) {
  const score = Number(rawScore);
  if (!Number.isFinite(score)) return 0;
  const attemptCount = Math.max(1, Number(attempts) || 1);
  const factor = Math.max(0, 1 - (attemptCount - 1) * FEYNMAN_RETRY_PENALTY);
  return Math.max(0, Math.min(1, score)) * factor;
}

function classifyFeynmanScore(score) {
  if (score >= FEYNMAN_SCORE_THRESHOLDS.good) return { label: "gut erklärt", cls: "correct" };
  if (score >= FEYNMAN_SCORE_THRESHOLDS.partial) return { label: "nachbessern", cls: "partial" };
  return { label: "noch unklar", cls: "wrong" };
}

function hasFeynmanEvaluationScore(value) {
  return value !== null && value !== undefined && value !== "" && Number.isFinite(Number(value));
}

const FEYNMAN_INPUT_STATE_CLASSES = [
  "fy-explain-input--partial",
  "fy-explain-input--unchecked",
  "is-correct",
  "is-incorrect",
  "is-partial",
];

function applyFeynmanInputEvaluations(itemEls, finalItems) {
  itemEls.forEach((itemEl, index) => {
    const input = itemEl.querySelector(".fy-explain-input");
    const feedback = itemEl.querySelector("[data-fy-feedback]");
    if (!input) return;

    input.classList.remove(...FEYNMAN_INPUT_STATE_CLASSES);
    input.removeAttribute("data-fy-evaluation");
    if (feedback) {
      feedback.textContent = "";
      feedback.hidden = true;
      feedback.classList.remove("is-correct", "is-incorrect", "is-neutral", "is-partial");
    }

    const item = finalItems[index];
    if (!item || item.unchecked) {
      input.classList.add("fy-explain-input--unchecked");
      input.dataset.fyEvaluation = "unchecked";
      if (feedback) {
        feedback.textContent = "Diese Erklärung konnte nicht automatisch bewertet werden.";
        feedback.classList.add("is-neutral");
        feedback.hidden = false;
      }
      return;
    }

    const verdict = classifyFeynmanScore(item.score);
    if (verdict.cls === "correct") {
      input.classList.add("is-correct");
    } else if (verdict.cls === "partial") {
      input.classList.add("is-partial", "fy-explain-input--partial");
    } else {
      input.classList.add("is-incorrect");
    }
    input.dataset.fyEvaluation = verdict.cls;

    if (feedback) {
      const reason = item.reason || verdict.label;
      feedback.textContent = `${verdict.label}: ${reason}`;
      feedback.classList.add(verdict.cls === "correct" ? "is-correct" : verdict.cls === "partial" ? "is-partial" : "is-incorrect");
      feedback.hidden = false;
    }
  });
}

function buildFeynmanCompletionDetails(evalState, source = "complete") {
  const itemScores = Array.isArray(evalState?.itemScores)
    ? evalState.itemScores.filter((score) => Number.isFinite(Number(score))).map(Number)
    : [];
  return {
    selfOutcome: source,
    ...(Number.isFinite(Number(evalState?.taskIndex)) ? { taskIndex: Number(evalState.taskIndex) } : {}),
    ...(itemScores.length ? { itemScores } : {}),
    ...(Array.isArray(evalState?.rawItemScores) ? { rawItemScores: evalState.rawItemScores } : {}),
    ...(Array.isArray(evalState?.itemAttempts) ? { itemAttempts: evalState.itemAttempts } : {}),
    ...(Array.isArray(evalState?.itemRevealed) ? { itemRevealed: evalState.itemRevealed } : {}),
    ...(Number.isFinite(Number(evalState?.checkableCount)) ? { checkableCount: Number(evalState.checkableCount) } : {}),
    ...(Number.isFinite(Number(evalState?.revealedCount)) ? { revealedCount: Number(evalState.revealedCount) } : {}),
    ...(evalState?.model ? { model: evalState.model } : {}),
  };
}

function normalizeFeynmanFeedContext(activityContext) {
  if (!activityContext || activityContext.mode !== "feed") return null;
  return String(activityContext.activityStep || "").trim() === FEYNMAN_FEED_STEP_KEY
    ? {
      mode: "feed",
      activityKey: String(activityContext.activityKey || "").trim(),
      activityStep: FEYNMAN_FEED_STEP_KEY,
    }
    : null;
}

function attachFeynmanFeedShell(section, activityContext, { lernbereich = "" } = {}) {
  const feedContext = normalizeFeynmanFeedContext(activityContext);
  if (!section || !feedContext) return;

  const controls = attachFeedCardControls(section, {
    cardSelector: "[data-fy-card]",
    stepLabel: "Feynman",
  });
  if (!controls) return;

  let canPrepare = false;
  let completed = false;
  let busy = false;
  let statusMessage = "Erkläre die Aufgabe und lass deine Antworten auswerten. Danach kannst du den Abschluss vorbereiten.";
  let statusTone = "neutral";
  let latestEvalState = null;

  const checkId = section.dataset.checkId || "";

  async function recordFeynmanCompletion() {
    await recordUserActivity({
      activityType: "feynman",
      lernbereichSlug: lernbereich,
      checkId,
      contextKey: "feed",
      details: buildFeynmanCompletionDetails(latestEvalState, "feed_complete"),
    });

    return recordCheckFeedDecision({
      lernbereichSlug: lernbereich,
      checkId,
      moduleKey: "feynman",
      outcomeKey: "can_do",
      activityKey: feedContext.activityKey,
    });
  }

  const enablePrepare = () => {
    if (completed) return;
    canPrepare = true;
    statusMessage = "Die Erklärungen wurden ausgewertet. Du kannst den Feed-Abschluss vorbereiten.";
    statusTone = "neutral";
    renderControls();
  };

  const disablePrepare = () => {
    if (completed) return;
    canPrepare = false;
    statusMessage = "Noch keine vollständige Feynman-Auswertung vorhanden.";
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
    latestEvalState = null;
    statusMessage = "Die Feynman-Aktivität bleibt im Feed offen.";
    statusTone = "neutral";
    section.dispatchEvent(new CustomEvent("feynman:reset-request", { bubbles: true }));
    renderControls();
  };

  const openFeynmanDecision = () => {
    if (!controls?.openDecisionDialog || busy || completed || !canPrepare) return;

    controls.openDecisionDialog({
      title: "Feynman abschließen?",
      detail: "Der bewertete Durchgang wird für deine Feynman-Quote gespeichert.",
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

  section.addEventListener("feynman:evaluation-ready", (event) => {
    latestEvalState = event.detail || null;
    if (latestEvalState?.ready) {
      enablePrepare();
    } else {
      disablePrepare();
    }
  });
  renderControls();
}

function buildKiAgentPrompt(check, beispielHtml) {
  const schlagwort = check.Schlagwort || `Check ${check.Nummer}`;
  const lernbereich = check.LernbereichAnzeigename || check.Lernbereich || "";
  const ichKann = check["Ich kann"] || "";
  const cleaned = cleanIchKannStatement(ichKann);

  const tipps = Array.isArray(check.Tipps) ? check.Tipps : [];

  const tippsBlock = tipps.length > 0
    ? `\nWichtige Aspekte, die in einer guten Erklärung vorkommen könnten:\n${tipps.map(t => `- ${convertJsonLatexToMarkdown(normalizeTippForPrompt(t))}`).join("\n")}`
    : "";

  const beispielText = beispielHtml
    ? htmlToPlainText(beispielHtml).trim()
    : "";
  const beispielBlock = beispielText
    ? `\n# Referenzbeispiel\nOrientiere dich intern an diesem Beispiel, um passende Rückfragen zu stellen und Antworten einzuordnen. Zeige es nicht direkt.\n\n${beispielText}`
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
${cleaned || "diesen Inhalt anwenden"} kann.
Zum Beispiel: „Okay, es geht um ${schlagwort} – wie geht man da vor?"

## Phase 2 – Erklärung begleiten (3–6 Runden)
- Lass den Lernenden erklären und begleite ihn Schritt für Schritt.
- Stelle nach jedem Erklärungsschritt eine gezielte Rückfrage –
  zum Rechenschritt, zur Begründung oder zu einem Begriff.
- Nutze dein Hintergrundwissen: Wenn ein wichtiger Aspekt fehlt,
  lenke mit einer Frage oder einem kleinen Hinweis dorthin.
- Wenn etwas richtig ist, bestätige es und geh zum nächsten Punkt.

## Phase 3 – Zusammenfassung
Wenn die wesentlichen Aspekte abgedeckt sind oder nach 6 Runden:
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

function renderCard(entry) {
  const check = entry?.check || entry;
  const titel = check.Schlagwort || `Check ${check.Nummer}`;
  const checkId = getCheckId(check);
  const cardAnchorId = getCheckCardAnchorId(checkId);
  const checkNummer = formatCheckNumber(check?.Nummer);
  const feynmanTaskMarkup = renderFeynmanTaskMarkup(entry, cardAnchorId);

  const kiMenuItem = `<button type="button" class="check-card__actions-item" role="menuitem" data-fy-ki-menu><span class="check-card__actions-icon" aria-hidden="true">✨</span><span>KI-Lernpartner kopieren</span></button>`;
  const actionsMenu = renderCardActionsMenuMarkup(kiMenuItem);

  return `
    <section id="${escapeHtml(cardAnchorId)}" class="check-viewport-item check-viewport-item--scroll-card" data-fy-check-viewport data-check-id="${escapeHtml(
    checkId
  )}" data-task-index="${Number(entry?.taskIndex) || 0}">
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
            <span class="check-card__rate-badge" aria-label="Feynman-Quote">–</span>
            ${actionsMenu}
          </div>
        </div>
        <div class="check-card__body">
        <div data-fy-stage="evaluate">
          ${feynmanTaskMarkup}
          <div class="module-flow-action-row">
            <button class="module-action-button" type="button" data-fy-run-evaluation>Jetzt auswerten</button>
          </div>
          <div data-fy-eval-status class="recall-eval-status"></div>
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

function initInteractiveFeynmanCards(root, cardEntries, lernbereich, activityContext) {
  const cards = root.querySelectorAll("[data-fy-card]");
  const cardEvalState = new WeakMap();

  cards.forEach((card, index) => {
    const entry = cardEntries[index] || null;
    const check = entry?.check || null;
    let task = entry?.task || null;
    const checkId = check ? getCheckId(check) : "";
    const section = card.closest("[data-fy-check-viewport]");
    const evaluateStage = card.querySelector('[data-fy-stage="evaluate"]');
    const runEvaluationButton = card.querySelector("[data-fy-run-evaluation]");
    const evalStatusEl = card.querySelector("[data-fy-eval-status]");

    const isFreeMode = activityContext?.mode !== "feed";
    let freeCompletionControl = null;
    let completionRecordPromise = null;
    let latestRates = null;
    let itemStates = [];

    function ensureItemStates(itemEls = Array.from(card.querySelectorAll("[data-fy-question-item]"))) {
      if (itemStates.length !== itemEls.length) {
        itemStates = itemEls.map((_, stateIndex) => itemStates[stateIndex] || {
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
      const itemEls = Array.from(card.querySelectorAll("[data-fy-question-item]"));
      const states = ensureItemStates(itemEls);
      const scorable = itemEls
        .map((el, stateIndex) => ({ el, state: states[stateIndex] }))
        .filter(({ el }) => String(el.dataset.answer || "").trim());

      const ready = scorable.length > 0 && scorable.every(({ state }) => hasFeynmanEvaluationScore(state?.rawScore) || state?.revealed);

      return {
        ready,
        taskIndex: Number(section?.dataset?.taskIndex) || Number(entry?.taskIndex) || 0,
        checkableCount: scorable.length,
        revealedCount: scorable.filter(({ state }) => Boolean(state?.revealed)).length,
        rawItemScores: scorable.map(({ state }) => hasFeynmanEvaluationScore(state?.rawScore) ? Number(state.rawScore) : 0),
        itemAttempts: scorable.map(({ state }) => Math.max(0, Number(state?.attempts) || 0)),
        itemRevealed: scorable.map(({ state }) => Boolean(state?.revealed)),
        itemScores: scorable.map(({ state }) => state?.revealed ? 0 : computeFeynmanAttemptScore(state?.rawScore, state?.attempts)),
        model: scorable.find(({ state }) => state?.model)?.state?.model || "",
      };
    }

    function publishCompletionState() {
      const evalState = buildEvalState();
      if (evalState.checkableCount > 0 && evalState.ready) {
        cardEvalState.set(card, evalState);
      } else {
        cardEvalState.delete(card);
      }
      section?.dispatchEvent(new CustomEvent("feynman:evaluation-ready", { detail: evalState, bubbles: true }));
      ensureFreeCompletionControl(evalState.ready);
      return evalState;
    }

    function loadNewRandomTask() {
      const pool = Array.isArray(entry?.scorableTasks) ? entry.scorableTasks : [];
      if (pool.length <= 1) return;

      const currentIndex = Number(entry?.taskIndex);
      const candidates = pool.filter(({ index: poolIndex }) => poolIndex !== currentIndex);
      const next = candidates[Math.floor(Math.random() * candidates.length)];
      if (!next) return;

      entry.task = next.task;
      entry.taskIndex = next.index;
      task = next.task;
      if (section) section.dataset.taskIndex = String(next.index);

      const taskNode = card.querySelector("[data-fy-task]");
      if (!taskNode) return;
      taskNode.outerHTML = renderFeynmanTaskMarkup(entry, section?.id || checkId || "fy-card");

      const introColumn = card.querySelector("[data-fy-task-intro-column]");
      if (introColumn && entry.task) {
        renderVisual(entry.task, introColumn);
        requestAnimationFrame(() => resizePlotlyInNode(introColumn));
      }
      bindQuestionItemListeners();
      enhanceSpeechInputs(card, ".fy-explain-input");
      void renderMath(card);
    }

    function resetFeynmanCard() {
      if (freeCompletionControl) freeCompletionControl.setReady(false);
      completionRecordPromise = null;
      latestRates = null;
      itemStates = [];
      cardEvalState.delete(card);
      loadNewRandomTask();
      card.querySelectorAll(".fy-explain-input").forEach((input) => { input.value = ""; });
      card.querySelectorAll("[data-fy-question-item]").forEach((itemEl) => {
        const input = itemEl.querySelector(".fy-explain-input");
        const feedback = itemEl.querySelector("[data-fy-feedback]");
        input?.classList.remove(...FEYNMAN_INPUT_STATE_CLASSES);
        input?.removeAttribute("data-fy-evaluation");
        if (feedback) {
          feedback.textContent = "";
          feedback.hidden = true;
          feedback.classList.remove("is-correct", "is-incorrect", "is-neutral", "is-partial");
        }
      });
      if (evalStatusEl) evalStatusEl.innerHTML = "";
      section?.dispatchEvent(new CustomEvent("feynman:evaluation-ready", { detail: { ready: false }, bubbles: true }));
      if (evaluateStage) evaluateStage.hidden = false;
    }

    function ensureFreeCompletionControl(ready = true) {
      if (!isFreeMode) return;
      if (!freeCompletionControl) {
        freeCompletionControl = attachFreeCompletionControl(section, {
          cardSelector: "[data-fy-card]",
          stepLabel: "Feynman",
          onComplete: () => {
            void openFreeCompletionPopup();
          },
        });
      }
      if (freeCompletionControl) freeCompletionControl.setReady(Boolean(ready));
    }

    async function recordFeynmanActivityOnce() {
      if (completionRecordPromise) return completionRecordPromise;

      completionRecordPromise = (async () => {
        const evalState = cardEvalState.get(card);
        const details = buildFeynmanCompletionDetails(evalState, "free_complete");
        if (!Array.isArray(details.itemScores) || details.itemScores.length === 0) {
          latestRates = { previousRate: null, newRate: null };
          return latestRates;
        }

        const before = await getUserFeynmanProficiency();
        const previousRate = before.ok ? extractFeynmanProficiencyRate(before.data, checkId) : null;

        await recordUserActivity({
          activityType: "feynman",
          lernbereichSlug: lernbereich,
          checkId,
          contextKey: "free",
          details,
        });

        const after = await getUserFeynmanProficiency();
        const newRate = after.ok ? extractFeynmanProficiencyRate(after.data, checkId) : null;
        updateFeynmanRateBadge(section?.querySelector(".check-card__rate-badge"), newRate);
        latestRates = { previousRate, newRate };
        return latestRates;
      })();

      return completionRecordPromise;
    }

    async function openFreeCompletionPopup() {
      const rates = latestRates || await recordFeynmanActivityOnce();
      showTaskCompletionPopup({
        mode: "feynman",
        showQuote: true,
        previousRate: rates.previousRate,
        newRate: rates.newRate,
        onRepeat: resetFeynmanCard,
        onDashboard: () => window.location.assign("/dashboard.html"),
      });
    }

    ensureFreeCompletionControl(false);

    runEvaluationButton?.addEventListener("click", async () => {
      if (runEvaluationButton.disabled || !task) return;

      const itemEls = Array.from(card.querySelectorAll("[data-fy-question-item]"));
      const states = ensureItemStates(itemEls);
      if (!itemEls.length) {
        if (evalStatusEl) evalStatusEl.innerHTML = `<p class="recall-eval-note">Keine auswertbaren Teilfragen gefunden.</p>`;
        publishCompletionState();
        return;
      }

      runEvaluationButton.disabled = true;
      const originalLabel = runEvaluationButton.textContent;
      runEvaluationButton.textContent = "MatheChecks prüft ...";
      if (evalStatusEl) evalStatusEl.innerHTML = "";

      const beispielHtml = check ? await fetchBeispielHtml(check) : "";
      const payload = buildFeynmanEvaluationPayload({ check, task, itemEls, beispielHtml });
      const evalData = await evaluateFeynmanItems(payload);

      runEvaluationButton.disabled = false;
      runEvaluationButton.textContent = originalLabel;

      if (!evalData?.results) {
        if (evalData?.error === "not-authenticated" || evalData?.error === "invalid-items") {
          const message = evalData?.error === "not-authenticated"
            ? "Melde dich an, um Feynman-Erklärungen automatisch auswerten zu lassen."
            : `Diese Aufgabe hat zu viele Teilfragen für eine automatische Feynman-Auswertung${evalData?.maxItems ? ` (maximal ${evalData.maxItems})` : ""}.`;
          if (evalStatusEl) evalStatusEl.innerHTML = `<p class="recall-eval-note">${escapeHtml(message)}</p>`;
          publishCompletionState();
          return;
        }

        // Fallback wie im Recall: Wenn die KI nicht erreichbar ist (Timeout,
        // Tageslimit, Gemini-Störung), bleibt der Durchgang abschließbar und
        // zählt ohne Bewertung (Itemscore 0). Ein erneuter Versuch bleibt möglich.
        const message = evalData?.error === "rate-limited"
          ? "Das Tageslimit für KI-Auswertungen ist erreicht. Du kannst den Durchgang ohne Bewertung abschließen."
          : evalData?.error === "timeout"
            ? "Die automatische Bewertung hat zu lange gedauert. Versuche es erneut oder schließe den Durchgang ohne Bewertung ab."
            : "Automatische Bewertung war gerade nicht möglich. Versuche es erneut oder schließe den Durchgang ohne Bewertung ab.";
        if (evalStatusEl) evalStatusEl.innerHTML = `<p class="recall-eval-note">${escapeHtml(message)}</p>`;

        const fallbackItems = itemEls.map((itemEl, itemIndex) => {
          const state = states[itemIndex];
          state.revealed = true;
          state.effectiveScore = 0;
          state.reason = "Automatische Bewertung war nicht möglich; der Durchgang zählt ungewertet.";
          return { unchecked: true };
        });
        applyFeynmanInputEvaluations(itemEls, fallbackItems);
        publishCompletionState();
        return;
      }

      const finalItems = itemEls.map((itemEl, itemIndex) => {
        const result = evalData.results[itemIndex] || {};
        const state = states[itemIndex];
        state.attempts += 1;
        state.revealed = false;
        state.rawScore = Number.isFinite(Number(result.score)) ? Math.max(0, Math.min(1, Number(result.score))) : 0;
        state.effectiveScore = computeFeynmanAttemptScore(state.rawScore, state.attempts);
        state.reason = result.reason || "";
        state.model = evalData.model || "";
        return {
          score: state.rawScore,
          reason: state.reason,
          unchecked: Boolean(result.unchecked),
        };
      });

      applyFeynmanInputEvaluations(itemEls, finalItems);
      publishCompletionState();
      void renderMath(evaluateStage);
    });

    function bindQuestionItemListeners() {
      card.querySelectorAll("[data-fy-question-item]").forEach((itemEl, itemIndex) => {
        const input = itemEl.querySelector(".fy-explain-input");
        input?.addEventListener("input", () => {
          const states = ensureItemStates();
          const state = states[itemIndex];
          if (!state) return;
          state.rawScore = null;
          state.effectiveScore = null;
          state.reason = "";
          state.revealed = false;
          completionRecordPromise = null;
          latestRates = null;
          input.classList.remove(...FEYNMAN_INPUT_STATE_CLASSES);
          input.removeAttribute("data-fy-evaluation");
          const feedback = itemEl.querySelector("[data-fy-feedback]");
          if (feedback) {
            feedback.textContent = "";
            feedback.hidden = true;
            feedback.classList.remove("is-correct", "is-incorrect", "is-neutral", "is-partial");
          }
          publishCompletionState();
        });
      });
    }

    bindQuestionItemListeners();

    section?.addEventListener("feynman:reset-request", resetFeynmanCard);

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

  const cardEntries = await buildFeynmanCardEntries(checks);

  renderJumpNav(navNode, checks, selectedCheckId);
  root.innerHTML = cardEntries.map((entry) => renderCard(entry)).join("");
  hydrateFeynmanTaskVisuals(root, cardEntries);
  const selectedSection = Array.from(root.querySelectorAll("[data-fy-check-viewport][data-check-id]"))
    .find((section) => section.dataset.checkId === selectedCheckId) || null;
  if (selectedSection) {
    attachFeynmanFeedShell(selectedSection, activityContext, { lernbereich });
    if (activityContext?.mode === "feed") {
      applyFeedFocusScope(root, selectedSection);
      setJumpNavActive(navNode, selectedCheckId);
      scrollModMainToEl(selectedSection);
    }
  }
  initCardMenuDismiss(root);
  bindJumpNavScrollSync(navNode, root.querySelectorAll("[data-fy-check-viewport][data-check-id]"));
  applyInitialReveal(root);
  initInteractiveFeynmanCards(root, cardEntries, lernbereich, activityContext);
  getUserFeynmanProficiency().then((proficiency) => {
    if (!proficiency.ok) return;
    root.querySelectorAll("[data-fy-check-viewport][data-check-id]").forEach((section) => {
      const rate = extractFeynmanProficiencyRate(proficiency.data, section.dataset.checkId);
      updateFeynmanRateBadge(section.querySelector(".check-card__rate-badge"), rate);
    });
  });
  enhanceSpeechInputs(root, ".fy-explain-input");
  bindCheckPositionPersistence(root, lernbereich, state);
  await renderMath(root);
}
