// Warm-Up: geführter Einstieg in einen Check mit Fading (nicht verlinkt, kein Fortschritt).
// Daten: <script type="application/json" id="warmup-data"> mit allen Warm-Ups des Lernbereichs
// (aus _data/warmup/<gebiet>/<lernbereich>/*.yml). Titel, Kompetenz, Nummer und Trainingslink
// kommen aus checks.json. Auswahl des Checks über #check-<Nummer> oder ?check_id=.
// Format und Leitlinien: _data/warmup/README.md

import { buildGraphFigure } from "../visuals/graph.js";
import { buildBaumdiagrammFigure } from "../visuals/baumdiagramm.js";
import { buildHistogrammEinzelnFigure } from "../visuals/histogramm.js";
import { plotlyRender, themeTextColor } from "../visuals/plotly-defaults.js?v=20260507-plotly-hover-name-theme";
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { enhanceCheckJumpNav } from "./ui/check-jump-nav.js";
import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";

const DATA_ID = "warmup-data";
const JUMP_NAV_ID = "warmup-jump-nav";

const PHASES = [
  { key: "orientierung", label: "Idee" },
  { key: "vormachen", label: "Zuschauen" },
  { key: "mitmachen", label: "Mitmachen" },
];

/* ───────────────────────── Hilfsfunktionen ───────────────────────── */

function el(tag, className = "", html = null) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (html !== null && html !== undefined) node.innerHTML = html;
  return node;
}

function shuffle(list) {
  const copy = list.slice();
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function parseNumber(raw) {
  const cleaned = String(raw ?? "")
    .trim()
    .replace(/\s+/g, "")
    .replace(/−/g, "-")
    .replace(",", ".");
  if (!cleaned || !/^[-+]?(\d+\.?\d*|\.\d+)$/.test(cleaned)) return null;
  return Number(cleaned);
}

function formatNumber(value) {
  return Number(value).toLocaleString("de-DE", { maximumFractionDigits: 4 });
}

async function typeset(node, retries = 20) {
  if (!node || !node.isConnected) return;
  const mathJax = window.MathJax;
  if (mathJax?.startup?.promise) {
    try { await mathJax.startup.promise; } catch { /* ignore */ }
  }
  if (mathJax && typeof mathJax.typesetPromise === "function") {
    try { await mathJax.typesetPromise([node]); } catch { /* ignore */ }
    return;
  }
  if (retries > 0) {
    await new Promise((resolve) => setTimeout(resolve, 150));
    await typeset(node, retries - 1);
  }
}

function scrollIntoViewSoft(node) {
  if (!node || typeof node.scrollIntoView !== "function") return;
  const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  node.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" });
}

/* ───────────────────────── Visualisierungen ───────────────────────── */

function createGraphVisual(spec) {
  const node = el("div", "cw-plot");
  const shown = new Set((spec.punkte || []).filter((p) => p.sichtbar).map((p) => p.id));
  const textColor = () => themeTextColor();

  function render() {
    if (!node.isConnected || !window.Plotly || !window.math) return;
    const punkte = (spec.punkte || []).filter((p) => shown.has(p.id));
    const figure = buildGraphFigure({
      funktionen: spec.funktionen || [],
      punkte: punkte.map((p) => ({ x: p.x, y: p.y, text: p.label || "" })),
      hilfslinien: punkte.filter((p) => p.hilfslinie).map((p) => ({ x: p.x, y: p.y })),
      xAchse: spec.xAchse || "",
      yAchse: spec.yAchse || "",
      xMin: spec.xMin ?? -1,
      xMax: spec.xMax ?? 10,
      yMin: spec.yMin ?? null,
      yMax: spec.yMax ?? null,
    });
    const labelAnnotations = punkte
      .filter((p) => p.label)
      .map((p) => ({
        x: p.x,
        y: p.y,
        text: p.label,
        showarrow: true,
        arrowhead: 0,
        arrowcolor: textColor(),
        ax: p.ax ?? 34,
        ay: p.ay ?? -28,
        font: { color: textColor(), size: 12 },
      }));
    figure.layout.annotations = [...(figure.layout.annotations || []), ...labelAnnotations];
    figure.layout.margin = { t: 20, r: 20, b: 50, l: 50 };
    figure.layout.legend = { orientation: "h", x: 0.5, xanchor: "center", y: -0.2 };
    plotlyRender(node, figure.data, figure.layout);
  }

  return {
    node,
    render,
    apply(zeige) {
      (zeige?.punkte || []).forEach((id) => shown.add(id));
      render();
    },
  };
}

function createTreeVisual(spec) {
  const node = el("div", "cw-plot cw-plot--tree");
  const given = new Set((spec.gegeben || []).map(Number));

  function render() {
    if (!node.isConnected || !window.Plotly) return;
    const figure = buildBaumdiagrammFigure({
      pa: spec.pa,
      pba: spec.pba,
      pbna: spec.pbna,
      mode: spec.modus || "slots",
      givenSlots: Array.from(given),
      edgeDecimals: spec.dezimal ?? 2,
      leafDecimals: spec.dezimal_blatt ?? spec.dezimal ?? 2,
    });
    plotlyRender(node, figure.data, figure.layout);
  }

  return {
    node,
    render,
    apply(zeige) {
      (zeige?.slots || []).forEach((slot) => given.add(Number(slot)));
      render();
    },
  };
}

const HISTOGRAM_COLORS = {
  neutral: "rgba(54, 162, 235, 0.45)",
  dimmed: "rgba(54, 162, 235, 0.18)",
  marked: "rgba(5, 56, 166, 0.75)",
  gegen: "rgba(226, 112, 58, 0.8)",
};

function normalizeRanges(list) {
  return (list || [])
    .filter((range) => Array.isArray(range) && range.length === 2)
    .map(([a, b]) => [Number(a), Number(b)]);
}

const inRanges = (ranges, k) => ranges.some(([a, b]) => k >= a && k <= b);

function formatDecimalComma(value, digits) {
  return Number(value).toFixed(digits).replace(".", ",");
}

// Binomialverteilung als Histogramm der Einzelwahrscheinlichkeiten.
// zeige.bereiche / zeige.gegen ersetzen die Markierungen, zeige.werte blendet abgelesene Balkenwerte ein.
function createHistogramVisual(spec) {
  const node = el("div", "cw-plot cw-plot--histogramm");
  let ranges = normalizeRanges(spec.bereiche);
  let gegen = normalizeRanges(spec.gegen);
  const werte = new Set((spec.werte || []).map(Number));

  function render() {
    if (!node.isConnected || !window.Plotly) return;
    const n = Number(spec.n);
    const figure = buildHistogrammEinzelnFigure({ n, p: Number(spec.p) });
    const kMin = Math.max(0, Number(spec.kMin ?? 0));
    const kMax = Math.min(n, Number(spec.kMax ?? n));
    const trace = figure.data[0];
    const visible = trace.x.map((k, i) => [k, trace.y[i]]).filter(([k]) => k >= kMin && k <= kMax);
    trace.x = visible.map(([k]) => k);
    trace.y = visible.map(([, y]) => y);
    const anyMark = ranges.length > 0 || gegen.length > 0;
    trace.marker.color = trace.x.map((k) => {
      if (inRanges(gegen, k)) return HISTOGRAM_COLORS.gegen;
      if (inRanges(ranges, k)) return HISTOGRAM_COLORS.marked;
      return anyMark ? HISTOGRAM_COLORS.dimmed : HISTOGRAM_COLORS.neutral;
    });
    // Wie im Training: Antippen zeigt den Wert auf 2 Nachkommastellen.
    trace.hovertemplate = "P(X = %{x}) ≈ %{y:.2f}<extra></extra>";
    const ticks = trace.x;
    const margin = { t: 16, r: 12, b: 48, l: 48 };
    const plotWidth = (node.clientWidth || 600) - margin.l - margin.r;
    const perBarPx = plotWidth / Math.max(ticks.length, 1);
    if (werte.size) {
      trace.text = trace.x.map((k, i) => (werte.has(k) ? formatDecimalComma(trace.y[i], 2) : ""));
      trace.textposition = "outside";
      trace.textangle = perBarPx < 30 ? -90 : 0;
      trace.constraintext = "none";
      trace.cliponaxis = false;
      trace.textfont = { color: themeTextColor(), size: 11 };
    }
    const yMax = Math.max(...trace.y);
    // Bei schmaler Darstellung kleinere Schrift und ggf. nur jede zweite Beschriftung, sonst überlappen zweistellige k.
    const tickStep = perBarPx < 13 ? 2 : 1;
    const labelled = ticks.filter((k) => (k - ticks[0]) % tickStep === 0);
    figure.layout.xaxis = {
      ...figure.layout.xaxis,
      range: [kMin, kMax + 1],
      tickvals: labelled.map((k) => k + 0.5),
      ticktext: labelled.map(String),
      tickangle: 0,
      tickfont: { color: themeTextColor(), size: perBarPx < 18 ? 10 : 12 },
    };
    figure.layout.yaxis = { ...figure.layout.yaxis, range: [0, yMax * (werte.size ? 1.25 : 1.05)] };
    figure.layout.margin = margin;
    figure.layout.separators = ",.";
    plotlyRender(node, figure.data, figure.layout);
  }

  return {
    node,
    render,
    apply(zeige) {
      if (!zeige) return;
      if ("bereiche" in zeige) ranges = normalizeRanges(zeige.bereiche);
      if ("gegen" in zeige) gegen = normalizeRanges(zeige.gegen);
      (zeige.werte || []).forEach((k) => werte.add(Number(k)));
      render();
    },
  };
}

// Zahlenstrahl der Trefferanzahlen 0 … n. zeige.bereiche ersetzt die markierten Bereiche,
// zeige.marke setzt eine nicht ganzzahlige Grenze (null entfernt sie), zeige.p ändert p in der Bcd-Zeile.
function createNumberLineVisual(spec) {
  const node = el("div", "cw-zs");
  const n = Number(spec.n);
  const state = {
    ranges: normalizeRanges(spec.bereiche),
    marke: spec.marke ?? null,
    p: spec.p ?? null,
  };
  const track = el("div", "cw-zs__track");
  const caption = el("div", "cw-zs__caption");
  caption.setAttribute("aria-live", "polite");
  node.append(track, caption);

  const pos = (value) => `${(Number(value) / n) * 100}%`;

  function chooseLabels() {
    const width = track.clientWidth || 300;
    const unitPx = width / n;
    const minGap = 24 / unitPx;
    const ends = new Set();
    state.ranges.forEach(([a, b]) => { ends.add(a); ends.add(b); });
    const chosen = [...ends];
    const candidates = [0, n];
    for (let k = 5; k < n; k += 5) candidates.push(k);
    if (unitPx >= 24) for (let k = 0; k <= n; k += 1) candidates.push(k);
    candidates.forEach((k) => {
      if (!chosen.some((c) => Math.abs(c - k) < minGap)) chosen.push(k);
    });
    return { labels: new Set(chosen), ends };
  }

  function render() {
    if (!node.isConnected) return;
    track.innerHTML = "";
    track.appendChild(el("span", "cw-zs__line"));
    state.ranges.forEach(([a, b]) => {
      const bar = el("span", "cw-zs__range");
      bar.style.left = pos(a);
      bar.style.width = `${((b - a) / n) * 100}%`;
      track.appendChild(bar);
    });
    const { labels, ends } = chooseLabels();
    for (let k = 0; k <= n; k += 1) {
      const isIn = inRanges(state.ranges, k);
      const tick = el("span", `cw-zs__tick${isIn ? " is-in" : ""}`);
      tick.style.left = pos(k);
      track.appendChild(tick);
      if (labels.has(k)) {
        const label = el("span", `cw-zs__label${ends.has(k) ? " is-end" : ""}`, String(k));
        label.style.left = pos(k);
        track.appendChild(label);
      }
    }
    if (state.marke !== null && state.marke !== undefined) {
      const marke = el("span", "cw-zs__marke");
      marke.style.left = pos(state.marke);
      marke.appendChild(el("span", "cw-zs__marke-text", formatNumber(state.marke)));
      track.appendChild(marke);
    }
    const summary = state.ranges.length
      ? state.ranges.map(([a, b]) => `${a} bis ${b}`).join(" und ")
      : "keine";
    node.setAttribute("role", "img");
    node.setAttribute("aria-label", `Zahlenstrahl der Anzahlen 0 bis ${n}, markiert: ${summary}`);

    if (state.p !== null && state.ranges.length) {
      const pTex = String(state.p).replace(".", "{,}");
      const terms = state.ranges.map(([a, b]) => `Bcd(${a};${b};${n};${pTex})`).join("+");
      caption.innerHTML = `<span class="cw-zs__caption-label">Eingabe</span> $${terms}$`;
      typeset(caption);
    } else {
      caption.innerHTML = "";
    }
  }

  return {
    node,
    render,
    apply(zeige) {
      if (!zeige) return;
      if ("bereiche" in zeige) state.ranges = normalizeRanges(zeige.bereiche);
      if ("marke" in zeige) state.marke = zeige.marke;
      if ("p" in zeige) state.p = zeige.p;
      render();
    },
  };
}

function createMatrixVisual(spec) {
  const node = el("div", "cw-matrix");
  const rows = spec.zeilen || [];
  const split = Number(spec.trenn ?? (rows[0]?.length ?? 1) - 1);
  const state = { zeilen: new Set(), spalten: new Set(), bereich: null };
  let selection = null;

  const wrap = el("div", "cw-matrix__wrap");
  if (spec.name) wrap.appendChild(el("span", "cw-matrix__name", spec.name));
  const table = el("table", "cw-matrix__table");
  const tbody = el("tbody");
  const rowNodes = rows.map((row, rowIndex) => {
    const tr = el("tr", "cw-matrix__row");
    tr.dataset.row = String(rowIndex);
    row.forEach((value, colIndex) => {
      const td = el("td", colIndex < split ? "cw-matrix__cell cw-matrix__cell--a" : "cw-matrix__cell cw-matrix__cell--y");
      if (colIndex === split) td.classList.add("cw-matrix__cell--bar");
      td.dataset.col = String(colIndex);
      td.textContent = String(value).replace("-", "−");
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
    return tr;
  });
  table.appendChild(tbody);
  wrap.appendChild(table);
  node.appendChild(wrap);

  function sync() {
    node.dataset.bereich = state.bereich || "";
    node.classList.toggle("is-selectable", Boolean(selection));
    rowNodes.forEach((tr, rowIndex) => {
      tr.classList.toggle("is-marked", state.zeilen.has(rowIndex));
      tr.classList.toggle("is-picked", Boolean(selection?.picked.has(rowIndex)));
      tr.querySelectorAll("td").forEach((td) => {
        td.classList.toggle("is-col-marked", state.spalten.has(Number(td.dataset.col)));
      });
    });
  }

  tbody.addEventListener("click", (event) => {
    if (!selection) return;
    const tr = event.target.closest(".cw-matrix__row");
    if (!tr) return;
    const rowIndex = Number(tr.dataset.row);
    if (selection.picked.has(rowIndex)) selection.picked.delete(rowIndex);
    else selection.picked.add(rowIndex);
    selection.onChange?.(selection.picked);
    sync();
  });

  return {
    node,
    render: sync,
    apply(zeige) {
      if (!zeige) return;
      state.zeilen = new Set(zeige.zeilen || []);
      state.spalten = new Set(zeige.spalten || []);
      state.bereich = zeige.bereich || null;
      sync();
    },
    startSelection({ bereich, onChange }) {
      state.zeilen = new Set();
      state.spalten = new Set();
      state.bereich = bereich || null;
      selection = { picked: new Set(), onChange };
      sync();
      return selection.picked;
    },
    stopSelection() {
      selection = null;
      sync();
    },
  };
}

function createListVisual(spec) {
  const node = el("div", "cw-brief");
  if (spec.titel) node.appendChild(el("div", "cw-brief__title", spec.titel));
  const list = el("ol", "cw-brief__list");
  const items = new Map();
  (spec.eintraege || []).forEach((entry) => {
    const li = el("li", "cw-brief__item");
    li.appendChild(el("span", "cw-brief__check"));
    const content = el("div", "cw-brief__content");
    content.appendChild(el("div", "cw-brief__text", entry.text || ""));
    const equation = el("div", "cw-brief__eq", entry.gleichung || "");
    equation.hidden = true;
    content.appendChild(equation);
    li.appendChild(content);
    list.appendChild(li);
    items.set(entry.id, { li, equation });
  });
  node.appendChild(list);

  function markDone(id, { renderMath = true } = {}) {
    const item = items.get(id);
    if (!item || item.li.classList.contains("is-done")) return;
    item.li.classList.add("is-done");
    if (item.equation.innerHTML) {
      item.equation.hidden = false;
      if (renderMath) typeset(item.equation);
    }
  }

  // Vorab erledigte Einträge setzt MathJax erst mit der angezeigten Seite.
  (spec.eintraege || []).filter((entry) => entry.erledigt).forEach((entry) => markDone(entry.id, { renderMath: false }));

  return {
    node,
    render() {},
    apply(zeige) {
      (zeige?.eintraege || []).forEach(markDone);
    },
  };
}

function createVisual(spec) {
  if (!spec) return null;
  if (spec.typ === "graph") return createGraphVisual(spec);
  if (spec.typ === "baum") return createTreeVisual(spec);
  if (spec.typ === "histogramm") return createHistogramVisual(spec);
  if (spec.typ === "zahlenstrahl") return createNumberLineVisual(spec);
  if (spec.typ === "matrix") return createMatrixVisual(spec);
  if (spec.typ === "liste") return createListVisual(spec);
  return null;
}

/* ───────────────────────── Schritttypen ───────────────────────── */

function stepShell(step) {
  const node = el("li", `cw-step cw-step--${step.typ}`);
  node.appendChild(el("span", "cw-step__marker"));
  const body = el("div", "cw-step__body");
  node.appendChild(body);
  if (step.frage) body.appendChild(el("div", "cw-step__lead", step.frage));
  return { node, body };
}

function feedbackNode() {
  const node = el("div", "cw-feedback");
  node.setAttribute("aria-live", "polite");
  node.hidden = true;
  return node;
}

function showFeedback(node, html, tone = "neutral") {
  node.className = `cw-feedback cw-feedback--${tone}`;
  node.innerHTML = html;
  node.hidden = false;
  typeset(node);
}

function buildTextStep(step, ctx) {
  const { node, body } = stepShell(step);
  body.appendChild(el("div", "cw-step__text", step.text || ""));
  queueMicrotask(() => ctx.complete());
  return node;
}

function buildRevealStep(step, ctx) {
  const { node, body } = stepShell(step);
  const button = el("button", "cw-btn cw-btn--reveal", step.knopf || "Zeig mir den nächsten Schritt");
  button.type = "button";
  const content = el("div", "cw-step__text cw-step__reveal", step.text || "");
  content.hidden = true;
  button.addEventListener("click", async () => {
    button.remove();
    content.hidden = false;
    await typeset(content);
    ctx.complete();
  });
  body.append(button, content);
  return node;
}

function buildChoiceStep(step, ctx) {
  const { node, body } = stepShell(step);
  const list = el("div", "cw-options");
  const feedback = feedbackNode();
  const correctIndex = Number(step.korrekt);
  const buttons = (step.optionen || []).map((option, index) => {
    const button = el("button", "cw-option", option);
    button.type = "button";
    button.addEventListener("click", () => {
      if (index === correctIndex) {
        button.classList.add("is-correct");
        buttons.forEach((b) => { b.disabled = true; });
        feedback.hidden = true;
        ctx.complete();
        return;
      }
      button.classList.add("is-wrong");
      button.disabled = true;
      showFeedback(feedback, step.hinweis || "Noch nicht – probier eine andere Antwort.", "wrong");
    });
    list.appendChild(button);
    return button;
  });
  body.append(list, feedback);
  return node;
}

function buildInputStep(step, ctx) {
  const { node, body } = stepShell(step);
  const fieldsWrap = el("div", step.layout === "zeile" ? "cw-fields cw-fields--zeile" : "cw-fields");
  const feedback = feedbackNode();
  const actions = el("div", "cw-step__actions");
  const checkButton = el("button", "cw-btn cw-btn--check", "Prüfen");
  checkButton.type = "button";
  const revealButton = el("button", "cw-btn cw-btn--ghost", "Lösung zeigen");
  revealButton.type = "button";
  revealButton.hidden = true;
  actions.append(checkButton, revealButton);

  let attempts = 0;
  let finished = false;
  const hasNegative = (step.felder || []).some((field) => Number(field.loesung) < 0);

  const fields = (step.felder || []).map((field) => {
    const label = el("label", "cw-field");
    label.appendChild(el("span", "cw-field__label", field.label || ""));
    const input = el("input", "cw-input");
    input.type = "text";
    // iOS-Ziffernblöcke haben kein Minuszeichen.
    input.inputMode = hasNegative ? "text" : "decimal";
    input.autocomplete = "off";
    input.spellcheck = false;
    input.setAttribute("aria-label", field.aria || "Antwort");
    label.appendChild(input);
    if (field.einheit) label.appendChild(el("span", "cw-field__unit", field.einheit));
    label.appendChild(el("span", "cw-field__mark", ""));
    fieldsWrap.appendChild(label);
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        check();
      }
    });
    input.addEventListener("input", () => label.classList.remove("is-wrong"));
    return { spec: field, label, input, done: false };
  });

  function resolveField(field, mode) {
    field.done = true;
    field.input.readOnly = true;
    field.label.classList.remove("is-wrong");
    field.label.classList.add(mode === "revealed" ? "is-revealed" : "is-correct");
    if (mode === "revealed") field.input.value = formatNumber(field.spec.loesung);
    if (field.spec.zeige) ctx.applyVisual(field.spec.zeige);
  }

  function finish() {
    if (finished) return;
    finished = true;
    actions.remove();
    ctx.complete();
  }

  function check() {
    if (finished) return;
    let allCorrect = true;
    let anyEmpty = false;
    fields.forEach((field) => {
      if (field.done) return;
      const value = parseNumber(field.input.value);
      if (value === null) {
        anyEmpty = true;
        allCorrect = false;
        return;
      }
      const tolerance = Number(field.spec.toleranz ?? 0.0001);
      if (Math.abs(value - Number(field.spec.loesung)) <= tolerance) {
        resolveField(field, "correct");
      } else {
        allCorrect = false;
        field.label.classList.add("is-wrong");
      }
    });

    if (allCorrect) {
      feedback.hidden = true;
      finish();
      return;
    }
    if (anyEmpty && fields.every((f) => f.done || parseNumber(f.input.value) === null)) {
      showFeedback(feedback, "Trag zuerst eine Zahl ein.", "neutral");
      return;
    }
    attempts += 1;
    showFeedback(feedback, step.hinweis || "Noch nicht ganz – schau dir den Ansatz noch einmal an.", "wrong");
    if (attempts >= 2) revealButton.hidden = false;
  }

  checkButton.addEventListener("click", check);
  revealButton.addEventListener("click", () => {
    fields.forEach((field) => { if (!field.done) resolveField(field, "revealed"); });
    feedback.hidden = true;
    finish();
  });

  body.append(fieldsWrap, actions, feedback);
  if (window.matchMedia?.("(pointer: fine)").matches) {
    queueMicrotask(() => fields[0]?.input.focus({ preventScroll: true }));
  }
  return node;
}

function buildMatchStep(step, ctx) {
  const { node, body } = stepShell(step);
  const pairs = step.paare || [];
  const grid = el("div", "cw-match");
  const leftCol = el("div", "cw-match__col");
  const rightCol = el("div", "cw-match__col");
  grid.append(leftCol, rightCol);
  body.appendChild(el("p", "cw-step__help", step.hilfe || "Tippe eine Karte an und dann das passende Gegenstück."));
  body.appendChild(grid);

  let rightOrder = shuffle(pairs.map((_, index) => index));
  if (pairs.length > 1 && rightOrder.every((value, index) => value === index)) {
    rightOrder = rightOrder.slice(1).concat(rightOrder[0]);
  }

  const selected = { left: null, right: null };
  let matchedCount = 0;

  const makeItem = (html, side, pairIndex) => {
    const button = el("button", "cw-match__item", html);
    button.type = "button";
    button.dataset.side = side;
    button.dataset.pair = String(pairIndex);
    button.addEventListener("click", () => pick(button));
    return button;
  };

  const leftItems = pairs.map((pair, index) => makeItem(pair.links, "left", index));
  const rightItems = rightOrder.map((index) => makeItem(pairs[index].rechts, "right", index));
  if (step.titel_links) leftCol.appendChild(el("span", "cw-match__head", step.titel_links));
  if (step.titel_rechts) rightCol.appendChild(el("span", "cw-match__head", step.titel_rechts));
  leftItems.forEach((item) => leftCol.appendChild(item));
  rightItems.forEach((item) => rightCol.appendChild(item));

  function pick(button) {
    if (button.classList.contains("is-matched")) return;
    const side = button.dataset.side;
    if (selected[side] === button) {
      button.classList.remove("is-selected");
      selected[side] = null;
      return;
    }
    selected[side]?.classList.remove("is-selected");
    selected[side] = button;
    button.classList.add("is-selected");
    if (!selected.left || !selected.right) return;

    const left = selected.left;
    const right = selected.right;
    selected.left = null;
    selected.right = null;
    if (left.dataset.pair === right.dataset.pair) {
      matchedCount += 1;
      [left, right].forEach((item) => {
        item.classList.remove("is-selected");
        item.classList.add("is-matched");
        item.disabled = true;
        item.dataset.badge = String(matchedCount);
      });
      if (matchedCount === pairs.length) ctx.complete();
      return;
    }
    [left, right].forEach((item) => item.classList.add("is-wrong"));
    setTimeout(() => {
      [left, right].forEach((item) => item.classList.remove("is-wrong", "is-selected"));
    }, 650);
  }

  return node;
}

function buildMarkStep(step, ctx) {
  const { node, body } = stepShell(step);
  const visual = ctx.visual;
  const feedback = feedbackNode();
  const actions = el("div", "cw-step__actions");
  const checkButton = el("button", "cw-btn cw-btn--check", "Prüfen");
  checkButton.type = "button";
  const counter = el("span", "cw-step__counter", "0 Zeilen markiert");
  actions.append(checkButton, counter);
  body.appendChild(el("p", "cw-step__help", step.hilfe || "Tippe die passenden Zeilen in der Matrix an."));
  body.append(actions, feedback);

  if (!visual || typeof visual.startSelection !== "function") {
    body.appendChild(el("p", "cw-step__help", "Für diesen Schritt fehlt die Matrix."));
    queueMicrotask(() => ctx.complete());
    return node;
  }

  const correct = new Set(step.korrekt || []);
  let attempts = 0;
  const picked = visual.startSelection({
    bereich: step.bereich,
    onChange: (set) => {
      counter.textContent = `${set.size} ${set.size === 1 ? "Zeile" : "Zeilen"} markiert`;
    },
  });

  checkButton.addEventListener("click", () => {
    const isCorrect = picked.size === correct.size && Array.from(picked).every((row) => correct.has(row));
    if (isCorrect) {
      visual.stopSelection();
      visual.apply({ zeilen: Array.from(correct), bereich: step.bereich });
      actions.remove();
      feedback.hidden = true;
      ctx.complete();
      return;
    }
    attempts += 1;
    showFeedback(feedback, step.hinweis || "Noch nicht ganz.", "wrong");
    if (attempts >= 2) {
      visual.stopSelection();
      visual.apply({ zeilen: Array.from(correct), bereich: step.bereich });
      showFeedback(feedback, `${step.hinweis || ""} Die richtigen Zeilen sind jetzt markiert.`, "neutral");
      actions.remove();
      ctx.complete();
    }
  });

  return node;
}

const STEP_BUILDERS = {
  text: buildTextStep,
  aufdecken: buildRevealStep,
  auswahl: buildChoiceStep,
  eingabe: buildInputStep,
  zuordnen: buildMatchStep,
  markieren: buildMarkStep,
};

/* ───────────────────────── Seiten & Ablauf ───────────────────────── */

function buildGoal(kompetenz) {
  const goal = el("p", "cw-goal");
  goal.appendChild(el("span", "cw-goal__label", "Ziel"));
  goal.appendChild(el("span", "cw-goal__text", `Ich kann ${kompetenz}`));
  return goal;
}

function buildPage(card, pageIndex, { goal, onComplete }) {
  const phase = PHASES.find((entry) => entry.key === card.phase) || PHASES[0];
  const page = el("section", `cw-page cw-page--${phase.key}`);
  page.dataset.index = String(pageIndex);

  if (goal) page.appendChild(goal);
  if (card.titel) {
    const head = el("header", "cw-page__head");
    head.appendChild(el("h2", "cw-page__title", card.titel));
    page.appendChild(head);
  }
  if (card.text) page.appendChild(el("div", "cw-page__intro", card.text));

  const visual = createVisual(card.visual);
  const layout = el("div", `cw-page__layout${visual ? " has-visual" : ""}`);
  if (visual) {
    const visualCol = el("div", "cw-page__visual");
    visualCol.appendChild(visual.node);
    layout.appendChild(visualCol);
  }
  const steps = el("ol", "cw-steps");
  layout.appendChild(steps);
  page.appendChild(layout);

  const stepSpecs = card.schritte || [];
  let current = 0;
  let complete = false;

  const applyVisual = (zeige) => visual?.apply(zeige);

  function renderNextStep() {
    if (current >= stepSpecs.length) {
      complete = true;
      onComplete(page);
      return;
    }
    const spec = stepSpecs[current];
    const builder = STEP_BUILDERS[spec.typ] || buildTextStep;
    let done = false;
    const ctx = {
      visual,
      applyVisual,
      complete: () => {
        if (done) return;
        done = true;
        stepNode.classList.add("is-done");
        if (spec.zeige) applyVisual(spec.zeige);
        const finishStep = () => {
          current += 1;
          renderNextStep();
        };
        if (spec.danach) {
          const after = el("div", "cw-after", spec.danach);
          stepNode.querySelector(".cw-step__body").appendChild(after);
          typeset(after).then(() => {
            scrollIntoViewSoft(after);
            finishStep();
          });
          return;
        }
        finishStep();
      },
    };
    const stepNode = builder(spec, ctx);
    steps.querySelectorAll(".cw-step.is-active").forEach((node) => node.classList.remove("is-active"));
    stepNode.classList.add("is-active");
    steps.appendChild(stepNode);
    typeset(stepNode).then(() => {
      if (current > 0) scrollIntoViewSoft(stepNode);
    });
  }

  let started = false;
  return {
    node: page,
    phase: phase.key,
    isComplete: () => complete,
    show() {
      page.hidden = false;
      if (!started) {
        started = true;
        typeset(page).then(() => {
          visual?.render();
          renderNextStep();
        });
      } else {
        visual?.render();
      }
    },
    hide() {
      page.hidden = true;
    },
  };
}

function buildCardHeader(data) {
  const header = el("div", "check-card__header");
  header.innerHTML = renderCheckMetaRowMarkup({
    numberText: formatCheckNumber(data.nummer),
    titleText: data.titel || "Warm-Up",
    prefix: "Warm-Up",
    rowClass: "check-card__header-left",
    titleTag: "span",
  });
  const actions = el("div", "check-card__header-actions");
  actions.appendChild(el("span", "cw-proto", "Prototyp"));
  if (data.training_url) {
    const skip = el("a", "cw-skip", "<span class=\"cw-skip__long\">Zum </span>Training <span aria-hidden=\"true\">→</span>");
    skip.href = data.training_url;
    skip.title = "Warm-Up überspringen und direkt zum Training";
    actions.appendChild(skip);
  }
  header.appendChild(actions);
  return header;
}

function renderPhaseBar(phasesNode, pages, activeIndex) {
  phasesNode.innerHTML = "";
  const activePhase = pages[activeIndex]?.phase;
  const activePhaseIndex = PHASES.findIndex((p) => p.key === activePhase);
  PHASES.forEach((phase, phaseIndex) => {
    const pageIndexes = pages.map((page, index) => (page.phase === phase.key ? index : -1)).filter((i) => i >= 0);
    if (!pageIndexes.length) return;
    const item = el("li", "cw-phase");
    if (phaseIndex < activePhaseIndex) item.classList.add("is-done");
    if (phaseIndex === activePhaseIndex) {
      item.classList.add("is-active");
      item.setAttribute("aria-current", "step");
    }
    item.appendChild(el("span", "cw-phase__label", phase.label));
    const dots = el("span", "cw-phase__dots");
    pageIndexes.forEach((index) => {
      const dot = el("span", "cw-phase__dot");
      if (index < activeIndex) dot.classList.add("is-done");
      if (index === activeIndex) dot.classList.add("is-active");
      dots.appendChild(dot);
    });
    item.appendChild(dots);
    phasesNode.appendChild(item);
  });
}

function buildFinish(data) {
  const finish = el("div", "cw-finish");
  finish.appendChild(el("span", "cw-finish__kicker", "Bereit fürs Training"));
  finish.appendChild(el("div", "cw-finish__text", data.abschluss || "<p>Weiter geht es mit echten Trainingsaufgaben.</p>"));
  return finish;
}

function renderPlayer(root, data) {
  root.innerHTML = "";
  root.classList.add("cw-player");

  const card = el("article", "check-card check-card--warmup cw-card");
  const phases = el("ol", "cw-phases");
  phases.setAttribute("aria-label", "Ablauf");
  const body = el("div", "check-card__body cw-body");
  card.append(buildCardHeader(data), phases, body);

  const stage = el("div", "cw-stage");
  stage.appendChild(card);

  const nav = el("nav", "cw-nav");
  nav.setAttribute("aria-label", "Warm-Up-Navigation");
  const backButton = el("button", "cw-btn cw-btn--ghost", "<span aria-hidden=\"true\">←</span> Zurück");
  backButton.type = "button";
  const nextButton = el("button", "cw-btn cw-btn--primary", "Weiter <span aria-hidden=\"true\">→</span>");
  nextButton.type = "button";
  const trainingButton = el("button", "cw-btn cw-btn--primary", "Weiter zum Training <span aria-hidden=\"true\">→</span>");
  trainingButton.type = "button";
  trainingButton.addEventListener("click", () => {
    if (data.training_url) window.location.href = data.training_url;
  });
  nav.append(backButton, el("span", "cw-nav__spacer"), nextButton, trainingButton);
  root.append(stage, nav);

  let active = 0;
  const cards = data.karten || [];
  const pages = cards.map((entry, index) =>
    buildPage(entry, index, {
      goal: index === 0 && data.kompetenz ? buildGoal(data.kompetenz) : null,
      onComplete: (pageNode) => {
        if (index === cards.length - 1) {
          const finish = buildFinish(data);
          pageNode.appendChild(finish);
          typeset(finish).then(() => scrollIntoViewSoft(finish));
        }
        if (index === active) syncNav();
      },
    })
  );
  pages.forEach((page) => {
    page.hide();
    body.appendChild(page.node);
  });

  function syncNav() {
    const isLast = active === pages.length - 1;
    backButton.disabled = active === 0;
    nextButton.hidden = isLast;
    trainingButton.hidden = !isLast;
    const complete = Boolean(pages[active]?.isComplete());
    nextButton.disabled = !complete;
    trainingButton.disabled = !complete;
    renderPhaseBar(phases, pages, active);
  }

  function goTo(index) {
    if (index < 0 || index >= pages.length) return;
    pages[active]?.hide();
    active = index;
    body.scrollTop = 0;
    pages[active].show();
    syncNav();
  }

  backButton.addEventListener("click", () => goTo(active - 1));
  nextButton.addEventListener("click", () => goTo(active + 1));

  pages[0]?.show();
  syncNav();
}

/* ───────────────────────── Modul: Auswahl pro Lernbereich ───────────────────────── */

function anchorIdFor(entry) {
  return `check-${entry.nummer}`;
}

// Ergänzt die Warm-Up-Daten um die Felder aus checks.json (nicht doppelt gepflegt).
function mergeWithChecks(rawData, checks) {
  const byId = new Map(checks.map((check) => [String(check?.check_id || ""), check]));
  const entries = Object.values(rawData && typeof rawData === "object" ? rawData : {});
  return entries
    .map((entry) => {
      const check = byId.get(String(entry?.check_id || ""));
      if (!check) return null;
      const nummer = Number(check.Nummer);
      return {
        ...entry,
        nummer,
        titel: String(check.Schlagwort || "").trim(),
        kompetenz: String(check["Ich kann"] || "").trim(),
        training_url: `training.html#check-${nummer}`,
      };
    })
    .filter(Boolean)
    .sort((a, b) => a.nummer - b.nummer);
}

function resolveEntryFromLocation(entries, preferredCheckId = "") {
  const preferred = String(preferredCheckId || "").trim();
  if (preferred) {
    const byId = entries.find((entry) => entry.check_id === preferred);
    if (byId) return byId;
  }
  const rawHash = window.location.hash || "";
  const hash = decodeURIComponent(rawHash.startsWith("#") ? rawHash.slice(1) : rawHash);
  const match = /^check-(\d+)$/.exec(hash);
  if (match) {
    const nummer = Number(match[1]);
    const byNummer = entries.find((entry) => entry.nummer === nummer);
    if (byNummer) return byNummer;
  }
  return entries[0] || null;
}

function renderJumpNav(navNode, entries, activeCheckId) {
  if (!navNode) return;
  navNode.innerHTML = "";
  entries.forEach((entry) => {
    const tab = el("a", `check-jump-tab${entry.check_id === activeCheckId ? " active" : ""}`);
    tab.href = `#${anchorIdFor(entry)}`;
    tab.dataset.checkId = entry.check_id;
    tab.textContent = `${entry.nummer}. ${entry.titel || "Check"}`;
    if (entry.check_id === activeCheckId) tab.setAttribute("aria-current", "true");
    navNode.appendChild(tab);
  });
  enhanceCheckJumpNav(navNode);
}

export async function initWarmupModule({ root, lernbereich, preferredCheckId = "" } = {}) {
  if (!root) return;
  const dataNode = document.getElementById(DATA_ID);
  const navNode = document.getElementById(JUMP_NAV_ID);

  let rawData;
  try {
    rawData = JSON.parse(dataNode?.textContent || "null");
  } catch (error) {
    root.innerHTML = `<p class="module-status">Warm-Up-Daten fehlerhaft: ${error.message}</p>`;
    return;
  }

  let checks = [];
  try {
    checks = await getChecksByLernbereich(lernbereich);
  } catch (error) {
    root.innerHTML = `<p class="module-status">${error.message}</p>`;
    return;
  }

  const entries = mergeWithChecks(rawData, checks);
  if (!entries.length) {
    root.innerHTML = "<p class=\"module-status\">Für diesen Lernbereich gibt es noch kein Warm-Up.</p>";
    return;
  }

  let activeCheckId = "";
  const show = (entry) => {
    if (!entry || entry.check_id === activeCheckId) return;
    activeCheckId = entry.check_id;
    renderJumpNav(navNode, entries, activeCheckId);
    renderPlayer(root, entry);
  };

  show(resolveEntryFromLocation(entries, preferredCheckId));

  window.addEventListener("hashchange", () => {
    show(resolveEntryFromLocation(entries));
  });
}
