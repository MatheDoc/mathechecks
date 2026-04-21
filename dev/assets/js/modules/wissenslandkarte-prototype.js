import { getChecksByLernbereich } from "../data/checks-repo.js";

const ROOT_ID = "dev-wissenslandkarte-root";
const STAGES = ["intro", "dump", "review", "assign", "compare", "summary"];
let thoughtCounter = 0;

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function createThought(text = "", checkId = "") {
  thoughtCounter += 1;
  return {
    id: `wl-thought-${thoughtCounter}`,
    text,
    checkId,
  };
}

function splitRawThoughts(rawText) {
  return String(rawText || "")
    .split(/\r?\n/)
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function normalizeThoughts(thoughts) {
  return thoughts
    .map((thought) => ({
      ...thought,
      text: String(thought?.text || "").trim(),
      checkId: String(thought?.checkId || "").trim(),
    }))
    .filter((thought) => thought.text);
}

function stageIndex(stage) {
  return Math.max(STAGES.indexOf(stage), 0);
}

async function renderMath(targetNode, retries = 6) {
  if (!targetNode) return;

  const mathJax = window.MathJax;
  if (mathJax && typeof mathJax.typesetPromise === "function") {
    try {
      await mathJax.typesetPromise([targetNode]);
    } catch {
      // Keep the prototype usable if one formula fails.
    }
    return;
  }

  if (retries <= 0) return;
  await new Promise((resolve) => setTimeout(resolve, 120));
  await renderMath(targetNode, retries - 1);
}

function getThoughtById(state, thoughtId) {
  return state.thoughts.find((thought) => thought.id === thoughtId) || null;
}

function duplicateThought(state, thoughtId) {
  const index = state.thoughts.findIndex((thought) => thought.id === thoughtId);
  if (index < 0) return;

  const source = state.thoughts[index];
  const duplicate = createThought(source.text, source.checkId);
  state.thoughts.splice(index + 1, 0, duplicate);
}

function deleteThought(state, thoughtId) {
  state.thoughts = state.thoughts.filter((thought) => thought.id !== thoughtId);
}

function ensureThoughtsForNextStage(state) {
  state.thoughts = normalizeThoughts(state.thoughts);
  return state.thoughts.length > 0;
}

function getAssignedThoughts(state, checkId) {
  return state.thoughts.filter((thought) => thought.checkId === checkId);
}

function getUnassignedThoughts(state) {
  return state.thoughts.filter((thought) => !thought.checkId);
}

function getCheckStatus(state, checkId) {
  const assignedCount = getAssignedThoughts(state, checkId).length;
  if (assignedCount >= 2) {
    return { key: "covered", label: "abgedeckt" };
  }
  if (assignedCount === 1) {
    return { key: "partial", label: "angerissen" };
  }
  return { key: "open", label: "offen" };
}

function buildSummary(state, checks) {
  const covered = [];
  const partial = [];
  const open = [];

  checks.forEach((check) => {
    const status = getCheckStatus(state, check.check_id);
    if (status.key === "covered") covered.push(check);
    if (status.key === "partial") partial.push(check);
    if (status.key === "open") open.push(check);
  });

  return {
    covered,
    partial,
    open,
    unassigned: getUnassignedThoughts(state),
  };
}

function renderProgress(state) {
  const activeIndex = stageIndex(state.stage);
  const labels = [
    "Einstieg",
    "Brain Dump",
    "Karten",
    "Zuordnung",
    "Abgleich",
    "Übersicht",
  ];

  return `
    <ol class="wl-progress" aria-label="Ablauf der Wissenslandkarte">
      ${labels
        .map((label, index) => {
          const classes = ["wl-progress__step"];
          if (index < activeIndex) classes.push("is-complete");
          if (index === activeIndex) classes.push("is-active");
          return `<li class="${classes.join(" ")}"><span>${escapeHtml(label)}</span></li>`;
        })
        .join("")}
    </ol>
  `;
}

function renderNotice(state) {
  if (!state.notice) return "";
  return `<p class="wl-inline-note">${escapeHtml(state.notice)}</p>`;
}

function renderThoughtEditor(thought, checks, options = {}) {
  const { withSelect = false } = options;
  const selectMarkup = withSelect
    ? `
      <label class="wl-field-label" for="assign-${escapeHtml(thought.id)}">Check-Zuordnung</label>
      <select class="wl-select" id="assign-${escapeHtml(thought.id)}" data-thought-check="${escapeHtml(thought.id)}">
        <option value="">Noch nicht zugeordnet</option>
        ${checks
          .map(
            (check) => `<option value="${escapeHtml(check.check_id)}"${
              thought.checkId === check.check_id ? " selected" : ""
            }>${escapeHtml(String(check.Nummer))}. ${escapeHtml(check.Schlagwort || "Check")}</option>`
          )
          .join("")}
      </select>
    `
    : "";

  return `
    <article class="wl-thought-card">
      <div class="wl-thought-card__row">
        <p class="wl-thought-card__label">Gedankenkarte</p>
        <div class="wl-thought-actions">
          <button class="wl-ghost-button" type="button" data-action="duplicate-thought" data-thought-id="${escapeHtml(thought.id)}">Duplizieren</button>
          <button class="wl-ghost-button wl-ghost-button--danger" type="button" data-action="delete-thought" data-thought-id="${escapeHtml(thought.id)}">Löschen</button>
        </div>
      </div>
      <textarea class="wl-thought-input" rows="3" data-thought-text="${escapeHtml(thought.id)}" placeholder="Ein Gedanke, eine Beobachtung, eine Formel, ein Zusammenhang...">${escapeHtml(
        thought.text
      )}</textarea>
      ${selectMarkup}
    </article>
  `;
}

function renderThoughtPills(thoughts) {
  if (!thoughts.length) {
    return `<p class="wl-empty-copy">Noch keine Gedanken zugeordnet.</p>`;
  }

  return `
    <div class="wl-pill-list">
      ${thoughts
        .map((thought) => `<span class="wl-pill wl-pill--thought">${escapeHtml(thought.text)}</span>`)
        .join("")}
    </div>
  `;
}

function renderTips(check) {
  const tipps = Array.isArray(check?.Tipps) ? check.Tipps : [];
  if (!tipps.length) {
    return `<p class="wl-empty-copy">Für diesen Check sind noch keine Kernpunkte hinterlegt.</p>`;
  }

  return `
    <ul class="wl-tips-list">
      ${tipps.map((tipp) => `<li>${escapeHtml(tipp)}</li>`).join("")}
    </ul>
  `;
}

function renderCheckOverview(state, checks) {
  return `
    <div class="wl-check-grid">
      ${checks
        .map((check) => {
          const status = getCheckStatus(state, check.check_id);
          const assignedThoughts = getAssignedThoughts(state, check.check_id);
          return `
            <article class="wl-check-card wl-check-card--${status.key}">
              <div class="wl-check-card__header">
                <div>
                  <p class="wl-check-card__eyebrow">Check ${escapeHtml(String(check.Nummer))}</p>
                  <h3 class="wl-check-card__title">${escapeHtml(check.Schlagwort || "Check")}</h3>
                </div>
                <span class="wl-status wl-status--${status.key}">${escapeHtml(status.label)}</span>
              </div>
              <p class="wl-check-card__competence">Ich kann ${escapeHtml(check["Ich kann"] || "")}</p>
              <div class="wl-check-card__columns">
                <section>
                  <p class="wl-section-label">Deine Gedanken</p>
                  ${renderThoughtPills(assignedThoughts)}
                </section>
                <section>
                  <p class="wl-section-label">Kernpunkte</p>
                  ${renderTips(check)}
                </section>
              </div>
            </article>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderCheckBadges(checks) {
  if (!checks.length) {
    return `<p class="wl-empty-copy">Keine Checks in dieser Kategorie.</p>`;
  }

  return `
    <div class="wl-badge-list">
      ${checks
        .map((check) => `<span class="wl-badge">${escapeHtml(String(check.Nummer))}. ${escapeHtml(check.Schlagwort || "Check")}</span>`)
        .join("")}
    </div>
  `;
}

function renderStageActions(backAction, nextAction, nextLabel, options = {}) {
  const { nextDisabled = false, secondaryAction = "", secondaryLabel = "" } = options;
  return `
    <div class="wl-stage-actions">
      <div class="wl-stage-actions__group">
        ${backAction ? `<button class="wl-ghost-button" type="button" data-action="${escapeHtml(backAction)}">Zurück</button>` : ""}
      </div>
      <div class="wl-stage-actions__group">
        ${secondaryAction ? `<button class="wl-ghost-button" type="button" data-action="${escapeHtml(secondaryAction)}">${escapeHtml(secondaryLabel)}</button>` : ""}
        ${nextAction ? `<button class="module-action-button${nextDisabled ? " module-action-button--locked" : ""}" type="button" data-action="${escapeHtml(nextAction)}"${nextDisabled ? " disabled" : ""}>${escapeHtml(nextLabel)}</button>` : ""}
      </div>
    </div>
  `;
}

function renderIntro(state, checks) {
  return `
    <section class="wl-hero">
      <p class="wl-eyebrow">Pilotmodul B</p>
      <h2 class="wl-title">Wissenslandkarte zu ${escapeHtml(state.lernbereichName)}</h2>
      <p class="wl-subtitle">Freies Blurting für den ganzen Lernbereich</p>
      <p class="wl-lead">Dieses Prototypmodul sammelt zunächst alles, was dir schon einfällt, und ordnet deine Gedanken erst danach an die Check-Struktur des Lernbereichs an. V1 liefert bewusst eine Strukturdiagnose statt einer automatischen fachlichen Bewertung.</p>
      <div class="wl-hero-meta">
        <span class="wl-badge">Pilot-Lernbereich</span>
        <span class="wl-badge">${escapeHtml(String(checks.length))} Checks</span>
      </div>
      <div class="wl-stage-actions wl-stage-actions--hero">
        <div class="wl-stage-actions__group"></div>
        <div class="wl-stage-actions__group">
          <button class="module-action-button" type="button" data-action="start">Wissenslandkarte starten</button>
        </div>
      </div>
    </section>
  `;
}

function renderDumpStage(state) {
  return `
    <article class="dev-check-card wl-stage-card">
      <div class="dev-check-card__body">
        <p class="wl-stage-kicker">Phase 1 – Großer Brain Dump</p>
        <h3 class="wl-stage-title">Schreibe alles auf, was dir zu ${escapeHtml(state.lernbereichName)} einfällt.</h3>
        <p class="wl-stage-copy">Nutze einzelne Zeilen für einzelne Gedanken. Es dürfen Begriffe, Formeln, kurze Beobachtungen, Fehlvorstellungen oder halbfertige Ideen sein.</p>
        ${renderNotice(state)}
        <label class="wl-field-label" for="wl-raw-input">Deine Rohnotizen</label>
        <textarea id="wl-raw-input" class="wl-textarea" rows="12" data-raw-input placeholder="Zum Beispiel:\n- Was zeigt der Graph?\n- Welche Kennzahlen spielen eine Rolle?\n- Wo liegen Maximum, Wendepunkt oder Fläche?">${escapeHtml(
          state.rawText
        )}</textarea>
        ${renderStageActions("to-intro", "to-review", "In Gedankenkarten aufteilen")}
      </div>
    </article>
  `;
}

function renderReviewStage(state) {
  return `
    <article class="dev-check-card wl-stage-card">
      <div class="dev-check-card__body">
        <p class="wl-stage-kicker">Phase 2 – Gedankenkarten prüfen</p>
        <h3 class="wl-stage-title">Mache aus deinen Rohnotizen einzelne, klare Gedankenkarten.</h3>
        <p class="wl-stage-copy">Eine Gedankenkarte sollte genau einen Gedanken tragen. Wenn etwas zu breit ist, trenne es auf. Wenn etwas doppelt auftaucht, lösche oder bündele es.</p>
        ${renderNotice(state)}
        <div class="wl-thought-list">
          ${state.thoughts.map((thought) => renderThoughtEditor(thought, [], { withSelect: false })).join("")}
        </div>
        <div class="wl-stage-actions wl-stage-actions--stacked">
          <div class="wl-stage-actions__group">
            <button class="wl-ghost-button" type="button" data-action="add-thought">Gedankenkarte hinzufügen</button>
          </div>
        </div>
        ${renderStageActions("to-dump", "to-assign", "Zu den Checks zuordnen", {
          nextDisabled: state.thoughts.length === 0,
        })}
      </div>
    </article>
  `;
}

function renderAssignStage(state, checks) {
  const assignedCount = state.thoughts.filter((thought) => thought.checkId).length;
  return `
    <article class="dev-check-card wl-stage-card">
      <div class="dev-check-card__body">
        <p class="wl-stage-kicker">Phase 3 – Strukturieren und zuordnen</p>
        <h3 class="wl-stage-title">Ordne jede Gedankenkarte dem passendsten Check zu.</h3>
        <p class="wl-stage-copy">Wenn ein Gedanke wirklich zu mehreren Checks gehört, dupliziere ihn und gib jeder Kopie eine eindeutige Rolle.</p>
        <div class="wl-metrics-row">
          <span class="wl-badge">${escapeHtml(String(assignedCount))} zugeordnet</span>
          <span class="wl-badge">${escapeHtml(String(state.thoughts.length - assignedCount))} noch offen</span>
        </div>
        ${renderNotice(state)}
        <div class="wl-thought-list">
          ${state.thoughts.map((thought) => renderThoughtEditor(thought, checks, { withSelect: true })).join("")}
        </div>
        <div class="wl-stage-actions wl-stage-actions--stacked">
          <div class="wl-stage-actions__group">
            <button class="wl-ghost-button" type="button" data-action="add-thought">Gedankenkarte hinzufügen</button>
          </div>
        </div>
        ${renderStageActions("to-review", "to-compare", "Zum Abgleich", {
          nextDisabled: state.thoughts.length === 0,
        })}
      </div>
    </article>
  `;
}

function renderCompareStage(state, checks) {
  const unassignedThoughts = getUnassignedThoughts(state);
  return `
    <article class="dev-check-card wl-stage-card">
      <div class="dev-check-card__body">
        <p class="wl-stage-kicker">Phase 4 – Abgleich mit Kernpunkten</p>
        <h3 class="wl-stage-title">Vergleiche deine Zuordnungen mit der Check-Struktur des Lernbereichs.</h3>
        <p class="wl-stage-copy">Die Farben zeigen nur eine Mengenregel: mindestens zwei Karten = abgedeckt, eine Karte = angerissen, keine Karte = offen.</p>
        ${renderCheckOverview(state, checks)}
        <section class="wl-unassigned-block">
          <p class="wl-section-label">Noch nicht zugeordnet</p>
          ${renderThoughtPills(unassignedThoughts)}
        </section>
        ${renderStageActions("to-assign", "to-summary", "Strukturübersicht anzeigen")}
      </div>
    </article>
  `;
}

function renderSummaryStage(state, checks) {
  const summary = buildSummary(state, checks);
  return `
    <article class="dev-check-card wl-stage-card">
      <div class="dev-check-card__body">
        <p class="wl-stage-kicker">Phase 5 – Strukturübersicht</p>
        <h3 class="wl-stage-title">So weit ist deine Wissenslandkarte strukturell gefüllt.</h3>
        <p class="wl-stage-copy">Diese Übersicht bewertet nicht die fachliche Qualität deiner Gedanken. Sie zeigt nur, welche Teile des Lernbereichs in deinem Abruf schon sichtbar geworden sind.</p>
        <div class="wl-summary-grid">
          <article class="wl-summary-card wl-summary-card--covered">
            <p class="wl-summary-card__count">${escapeHtml(String(summary.covered.length))}</p>
            <p class="wl-summary-card__label">abgedeckt</p>
          </article>
          <article class="wl-summary-card wl-summary-card--partial">
            <p class="wl-summary-card__count">${escapeHtml(String(summary.partial.length))}</p>
            <p class="wl-summary-card__label">angerissen</p>
          </article>
          <article class="wl-summary-card wl-summary-card--open">
            <p class="wl-summary-card__count">${escapeHtml(String(summary.open.length))}</p>
            <p class="wl-summary-card__label">offen</p>
          </article>
          <article class="wl-summary-card wl-summary-card--neutral">
            <p class="wl-summary-card__count">${escapeHtml(String(summary.unassigned.length))}</p>
            <p class="wl-summary-card__label">unzugeordnet</p>
          </article>
        </div>
        <div class="wl-summary-sections">
          <section>
            <p class="wl-section-label">Abgedeckte Checks</p>
            ${renderCheckBadges(summary.covered)}
          </section>
          <section>
            <p class="wl-section-label">Angerissene Checks</p>
            ${renderCheckBadges(summary.partial)}
          </section>
          <section>
            <p class="wl-section-label">Offene Checks</p>
            ${renderCheckBadges(summary.open)}
          </section>
        </div>
        ${renderStageActions("to-compare", "restart", "Neu beginnen", {
          secondaryAction: "to-assign",
          secondaryLabel: "Zuordnungen überarbeiten",
        })}
      </div>
    </article>
  `;
}

function renderStage(state, checks) {
  if (state.stage === "intro") return renderIntro(state, checks);
  if (state.stage === "dump") return renderDumpStage(state);
  if (state.stage === "review") return renderReviewStage(state);
  if (state.stage === "assign") return renderAssignStage(state, checks);
  if (state.stage === "compare") return renderCompareStage(state, checks);
  return renderSummaryStage(state, checks);
}

function render(root, state, checks) {
  root.innerHTML = `
    ${renderProgress(state)}
    ${renderStage(state, checks)}
  `;
  void renderMath(root);
}

function clearNotice(state) {
  state.notice = "";
}

function bindPrototypeEvents(root, state, checks) {
  if (root.dataset.wlBound === "1") return;
  root.dataset.wlBound = "1";

  root.addEventListener("input", (event) => {
    const rawInput = event.target.closest("[data-raw-input]");
    if (rawInput) {
      state.rawText = rawInput.value;
      clearNotice(state);
      return;
    }

    const thoughtField = event.target.closest("[data-thought-text]");
    if (!thoughtField) return;
    const thought = getThoughtById(state, thoughtField.dataset.thoughtText || "");
    if (!thought) return;
    thought.text = thoughtField.value;
    clearNotice(state);
  });

  root.addEventListener("change", (event) => {
    const select = event.target.closest("[data-thought-check]");
    if (!select) return;
    const thought = getThoughtById(state, select.dataset.thoughtCheck || "");
    if (!thought) return;
    thought.checkId = select.value;
    clearNotice(state);
  });

  root.addEventListener("click", (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;

    const action = button.dataset.action || "";
    const thoughtId = button.dataset.thoughtId || "";

    switch (action) {
      case "start":
        clearNotice(state);
        state.stage = "dump";
        break;
      case "to-intro":
        clearNotice(state);
        state.stage = "intro";
        break;
      case "to-dump":
        clearNotice(state);
        state.stage = "dump";
        break;
      case "to-review": {
        const parsed = splitRawThoughts(state.rawText);
        if (!parsed.length) {
          state.notice = "Bitte schreibe zuerst mindestens einen Gedanken auf.";
          render(root, state, checks);
          return;
        }
        state.thoughts = parsed.map((entry) => createThought(entry));
        clearNotice(state);
        state.stage = "review";
        break;
      }
      case "to-assign":
        if (!ensureThoughtsForNextStage(state)) {
          state.notice = "Bitte lasse mindestens eine nichtleere Gedankenkarte stehen.";
          render(root, state, checks);
          return;
        }
        clearNotice(state);
        state.stage = "assign";
        break;
      case "to-compare":
        if (!ensureThoughtsForNextStage(state)) {
          state.notice = "Bitte ordne zuerst mindestens eine nichtleere Gedankenkarte weiter.";
          render(root, state, checks);
          return;
        }
        clearNotice(state);
        state.stage = "compare";
        break;
      case "to-summary":
        clearNotice(state);
        state.stage = "summary";
        break;
      case "duplicate-thought":
        duplicateThought(state, thoughtId);
        clearNotice(state);
        break;
      case "delete-thought":
        deleteThought(state, thoughtId);
        clearNotice(state);
        break;
      case "add-thought":
        state.thoughts.push(createThought(""));
        clearNotice(state);
        break;
      case "restart":
        state.rawText = "";
        state.thoughts = [];
        clearNotice(state);
        state.stage = "intro";
        break;
      default:
        return;
    }

    render(root, state, checks);
  });
}

export async function initWissenslandkartePrototype({ root, lernbereich = "" } = {}) {
  if (!root) return;
  if (!lernbereich) {
    root.innerHTML = `<p class="dev-module__status">Kein Lernbereich gesetzt.</p>`;
    return;
  }

  root.innerHTML = `<p class="dev-module__status">Die Wissenslandkarte wird geladen...</p>`;

  try {
    const checks = await getChecksByLernbereich(lernbereich);
    if (!checks.length) {
      root.innerHTML = `<p class="dev-module__status">Keine Checks für diesen Lernbereich gefunden.</p>`;
      return;
    }

    const lernbereichName =
      root.dataset.lernbereichName ||
      checks[0]?.LernbereichAnzeigename ||
      checks[0]?.Lernbereich ||
      lernbereich;

    const state = {
      stage: "intro",
      lernbereich,
      lernbereichName,
      rawText: "",
      thoughts: [],
      notice: "",
    };

    bindPrototypeEvents(root, state, checks);
    render(root, state, checks);
  } catch (error) {
    root.innerHTML = `<p class="dev-module__status">Die Wissenslandkarte konnte nicht geladen werden.</p>`;
    console.error(error);
  }
}

const root = document.getElementById(ROOT_ID);
if (root) {
  void initWissenslandkartePrototype({
    root,
    lernbereich: root.dataset.lernbereich || document.body?.dataset?.lernbereich || "",
  });
}