import { getChecksByLernbereich } from "../data/checks-repo.js";
import { getAufgabenSammlung } from "../data/sammlungen-repo.js";
import {
  loadTrainingState,
  saveTrainingState,
  loadTaskIndexForCheck,
  saveTaskIndexForCheck,
  loadShuffleNonce,
  saveShuffleNonce,
} from "../state/check-state-store.js";
import { buildTaskUiStateKey } from "../state/task-ui-state.js";
import { shuffleQuestionsInTask } from "../utils/task-order.js";
import { renderTask as renderRuntimeTask } from "../../../../aufgaben/runtime/task-render.js?v=20260423-market-legends-a";
import { createCheckMetaRowNode, formatCheckNumber } from "./ui/check-meta.js";
import { createCardActionsMenu, createCardMenuItem, createCardMenuLink, runCardMenuItemFeedbackAction } from "./ui/card-actions-menu.js";
import { enhanceSpeechInputs } from "./ui/speech-input.js";

const TR_BEISPIEL_CACHE = new Map();

async function renderMath(targetNode, retries = 4) {
  if (!targetNode) return;

  const mathJax = window.MathJax;
  if (mathJax && typeof mathJax.typesetPromise === "function") {
    try {
      await mathJax.typesetPromise([targetNode]);
    } catch {
      // Rendering errors should not block the training flow.
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
      // Ignore once and try again while layout settles.
    }
  });

  if (retries <= 0) return;
  setTimeout(() => {
    resizePlotlyInNode(targetNode, retries - 1);
  }, 120);
}

function finalizeTaskRender(targetNode) {
  void renderMath(targetNode);
  requestAnimationFrame(() => resizePlotlyInNode(targetNode));
  enhanceSpeechInputs(targetNode);
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
    .replace(/[^a-z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function getTrainingCheckAnchorId(check) {
  const nummer = Number(check?.Nummer);
  if (Number.isFinite(nummer) && nummer > 0) {
    return `check-${nummer}`;
  }

  const checkId = getCheckId(check);
  return `check-${toDomIdFragment(checkId) || "item"}`;
}

function resolvePreferredCheckIdFromHash(checks) {
  const rawHash = window.location?.hash || "";
  const hash = rawHash.startsWith("#") ? rawHash.slice(1) : rawHash;
  if (!hash) return "";

  const decoded = decodeURIComponent(hash);
  const byAnchor = checks.find((check) => getTrainingCheckAnchorId(check) === decoded);
  if (byAnchor) {
    return getCheckId(byAnchor);
  }

  const nummerMatch = /^check-(\d+)$/.exec(decoded);
  if (!nummerMatch) return "";

  const nummer = Number(nummerMatch[1]);
  if (!Number.isFinite(nummer)) return "";
  const byNummer = checks.find((check) => Number(check?.Nummer) === nummer);
  return byNummer ? getCheckId(byNummer) : "";
}

function pickRandomTaskIndex(currentIndex, totalCount) {
  if (!Number.isInteger(totalCount) || totalCount <= 0) {
    return 0;
  }

  if (totalCount === 1) {
    return 0;
  }

  let nextIndex = currentIndex;
  while (nextIndex === currentIndex) {
    nextIndex = Math.floor(Math.random() * totalCount);
  }
  return nextIndex;
}

function getScriptPageHref() {
  const path = window.location?.pathname || "";
  if (!path.endsWith("training.html")) return "";
  return path.replace(/training\.html$/, "skript.html");
}

function getTrainingBaseOrigin() {
  const origin = String(window.location?.origin || "").trim();
  if (/^https?:\/\//i.test(origin) && !/localhost|127\.0\.0\.1/i.test(origin)) {
    return origin;
  }
  return "https://www.mathechecks.de";
}

function buildTrainingCheckUrl(check) {
  const gebiet = String(check?.Gebiet || "").trim();
  const lernbereich = String(check?.Lernbereich || "").trim();
  const anchor = getTrainingCheckAnchorId(check);

  if (!gebiet || !lernbereich || !anchor) return "";

  const origin = getTrainingBaseOrigin();
  return `${origin}/dev/lernbereiche/${encodeURIComponent(gebiet)}/${encodeURIComponent(lernbereich)}/training.html#${encodeURIComponent(anchor)}`;
}

function getSkriptCheckAnchorId(check) {
  const nummer = Number(check?.Nummer);
  if (!Number.isFinite(nummer) || nummer <= 0) return "";
  return `check-${nummer}`;
}

function buildSkriptTippsHref(check) {
  const anchorId = getSkriptCheckAnchorId(check);
  if (!anchorId) return "";

  const path = window.location?.pathname || "";
  if (path.endsWith("skript.html")) {
    return `#${encodeURIComponent(anchorId)}`;
  }

  const scriptPageHref = getScriptPageHref();
  if (scriptPageHref) {
    return `${scriptPageHref}#${encodeURIComponent(anchorId)}`;
  }

  const gebiet = String(check?.Gebiet || "").trim();
  const lernbereich = String(check?.Lernbereich || "").trim();
  if (!gebiet || !lernbereich) return "";
  return `/dev/lernbereiche/${gebiet}/${lernbereich}/skript.html#${encodeURIComponent(anchorId)}`;
}

function buildBeispielUrl(check) {
  const nummer = String(Number(check?.Nummer) || 0).padStart(2, "0");
  const sammlung = String(check?.Sammlung || "").trim();
  const gebiet = String(check?.Gebiet || "").trim();
  const lernbereich = String(check?.Lernbereich || "").trim();
  if (!sammlung || !gebiet || !lernbereich) return "";
  return `/dev/lernbereiche/${gebiet}/${lernbereich}/beispiele/${nummer}-${sammlung}.html`;
}

async function fetchBeispielHtml(check) {
  const url = buildBeispielUrl(check);
  if (!url) return "";
  if (TR_BEISPIEL_CACHE.has(url)) return TR_BEISPIEL_CACHE.get(url);

  try {
    const response = await fetch(url);
    if (!response.ok) {
      TR_BEISPIEL_CACHE.set(url, "");
      return "";
    }
    const html = (await response.text()).trim();
    TR_BEISPIEL_CACHE.set(url, html);
    return html;
  } catch {
    TR_BEISPIEL_CACHE.set(url, "");
    return "";
  }
}

function convertJsonLatexToMarkdown(text) {
  return String(text || "")
    .replace(/\\\((.+?)\\\)/g, (_, m) => `$${m}$`)
    .replace(/\\\[(.+?)\\\]/gs, (_, m) => `$$${m}$$`);
}

function extractGraphDescriptions(container) {
  if (!container) return "";
  const parts = [];

  // ── .graph-auto (Analysis function graphs) ──
  container.querySelectorAll(".graph-auto").forEach((graphNode) => {
    const lines = [];
    const titel = graphNode.dataset.titel;
    if (titel) lines.push(`Diagramm: ${titel}`);

    const xachse = graphNode.dataset.xachse;
    const yachse = graphNode.dataset.yachse;
    if (xachse) lines.push(`x-Achse: ${xachse}`);
    if (yachse) lines.push(`y-Achse: ${yachse}`);

    try {
      const funktionen = JSON.parse(graphNode.dataset.funktionen || "[]");
      if (funktionen.length > 0) {
        lines.push("Funktionen:");
        funktionen.forEach((funktion) => {
          const name = funktion.name || "";
          const term = funktion.term || "";
          const beschreibung = funktion.beschreibung || "";
          lines.push(`  ${name ? `${name}: ` : ""}${term}${beschreibung ? ` (${beschreibung})` : ""}`);
        });
      }
    } catch {
      // Ignore malformed graph metadata.
    }

    try {
      const punkte = JSON.parse(graphNode.dataset.punkte || "[]");
      if (punkte.length > 0) {
        lines.push("Markierte Punkte:");
        punkte.forEach((punkt) => {
          lines.push(`  (${punkt.x}, ${punkt.y})${punkt.text ? ` \u2013 ${punkt.text}` : ""}`);
        });
      }
    } catch {
      // Ignore malformed graph metadata.
    }

    try {
      const flaechen = JSON.parse(graphNode.dataset.flaechen || "[]");
      if (flaechen.length > 0) {
        lines.push("Flächen:");
        flaechen.forEach((flaeche) => {
          const beschreibung = flaeche.beschreibung || flaeche.name || "";
          lines.push(
            `  ${beschreibung}${flaeche.von != null ? ` von x=${flaeche.von}` : ""}${flaeche.bis != null ? ` bis x=${flaeche.bis}` : ""
            }`
          );
        });
      }
    } catch {
      // Ignore malformed graph metadata.
    }

    if (lines.length > 0) {
      parts.push(lines.join("\n"));
    }
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
    } catch {
      // Ignore malformed metadata.
    }
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
  tmp.innerHTML = String(html || "");
  const graphText = extractGraphDescriptions(tmp);
  const plainText = (tmp.textContent || "").trim();
  return [plainText, graphText].filter(Boolean).join("\n\n");
}

function unescapeMoodleText(value) {
  return String(value)
    .replaceAll("\\~", "~")
    .replaceAll("\\=", "=")
    .replaceAll("\\#", "#")
    .replaceAll("\\:", ":")
    .trim();
}

function parseAnswerTargets(answerRaw) {
  const source = String(answerRaw || "");
  const regex = /\{\d+:(NUMERICAL_OPT|NUMERICAL|MC):([\s\S]*?)\}/g;
  const targets = [];
  let match = null;

  while ((match = regex.exec(source)) !== null) {
    const kind = match[1];
    const payload = match[2];

    if (kind === "NUMERICAL_OPT") {
      if (String(payload).trim().toUpperCase() === "NONE") {
        targets.push({ kind, expectedNone: true });
      } else {
        const numericalMatch = String(payload).match(/=([^:}#]+):([^:}#]+)/);
        if (numericalMatch) {
          targets.push({ kind, value: numericalMatch[1].trim(), tolerance: numericalMatch[2].trim(), expectedNone: false });
        } else {
          targets.push({ kind, raw: payload.trim() });
        }
      }
      continue;
    }

    if (kind === "NUMERICAL") {
      const numericalMatch = String(payload).match(/=([^:}#]+):([^:}#]+)/);
      if (numericalMatch) {
        targets.push({ kind, value: numericalMatch[1].trim(), tolerance: numericalMatch[2].trim() });
      } else {
        targets.push({ kind, raw: payload.trim() });
      }
      continue;
    }

    const options = String(payload)
      .split(/(?<!\\)~/)
      .map((part) => part.trim())
      .filter(Boolean);
    const correct = options.find((option) => option.startsWith("="));
    if (correct) {
      targets.push({ kind, correct: unescapeMoodleText(correct.slice(1).trim()) });
    } else {
      targets.push({ kind, raw: payload.trim() });
    }
  }

  return targets;
}

function buildAnswerTargetText(answerRaw) {
  const targets = parseAnswerTargets(answerRaw);
  if (targets.length === 0) {
    return String(answerRaw || "").trim() || "(kein Antwortschluessel gefunden)";
  }

  return targets
    .map((target, index) => {
      const part = `Teil ${index + 1}`;
      if (target.kind === "NUMERICAL_OPT") {
        if (target.expectedNone) {
          return `${part}: existiert nicht`;
        }
        if (target.value != null && target.tolerance != null) {
          return `${part}: Zielwert ${target.value} (Toleranz \u00b1${target.tolerance}), oder "existiert nicht"`;
        }
        return `${part}: Numerische Antwort oder "existiert nicht" (${target.raw || "unbekannt"})`;
      }
      if (target.kind === "NUMERICAL") {
        if (target.value != null && target.tolerance != null) {
          return `${part}: Zielwert ${target.value} (Toleranz ±${target.tolerance})`;
        }
        return `${part}: Numerische Antwort (${target.raw || "unbekannt"})`;
      }

      if (target.correct != null) {
        return `${part}: Richtige Option "${convertJsonLatexToMarkdown(target.correct)}"`;
      }
      return `${part}: MC-Antwort (${target.raw || "unbekannt"})`;
    })
    .join("\n");
}

function toFiniteNumber(value, fallback = 0) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
}

function formatFormulaNumber(value, digits = 6) {
  const safe = Math.abs(toFiniteNumber(value, 0)) < 1e-12 ? 0 : toFiniteNumber(value, 0);
  const text = safe.toFixed(digits).replace(/\.0+$/, "").replace(/(\.\d*?)0+$/, "$1");
  return text === "-0" ? "0" : text;
}

function formatPolynomialExpression(coefficients) {
  const coeffs = Array.isArray(coefficients) ? coefficients : [];
  const terms = [];

  for (let power = coeffs.length - 1; power >= 0; power -= 1) {
    const coefficient = toFiniteNumber(coeffs[power], 0);
    if (Math.abs(coefficient) < 1e-10) continue;

    const absCoeff = Math.abs(coefficient);
    let termCore = "";

    if (power === 0) {
      termCore = formatFormulaNumber(absCoeff);
    } else {
      const coeffText = Math.abs(absCoeff - 1) < 1e-10 ? "" : `${formatFormulaNumber(absCoeff)}*`;
      termCore = power === 1 ? `${coeffText}x` : `${coeffText}x^${power}`;
    }

    terms.push({ sign: coefficient < 0 ? "-" : "+", termCore });
  }

  if (terms.length === 0) return "0";

  return terms
    .map((term, index) => {
      if (index === 0) {
        return term.sign === "-" ? `-${term.termCore}` : term.termCore;
      }
      return `${term.sign}${term.termCore}`;
    })
    .join("");
}

function appendSignedConstant(baseExpression, constantValue) {
  const c = toFiniteNumber(constantValue, 0);
  if (Math.abs(c) < 1e-10) return baseExpression;
  return `${baseExpression}${c >= 0 ? "+" : ""}${formatFormulaNumber(c)}`;
}

function describeFunctionName(nameRaw) {
  const key = String(nameRaw || "").trim();
  const map = {
    "p(x)": "Preisfunktion",
    "E(x)": "Erlösfunktion",
    "K(x)": "Kostenfunktion",
    "G(x)": "Gewinnfunktion",
    "K'(x)": "Grenzkostenfunktion",
    "k(x)": "Stückkostenfunktion",
    "kv(x)": "Variable Stückkostenfunktion",
    "p_A(x)": "Angebotsfunktion",
    "p_N(x)": "Nachfragefunktion",
  };
  return map[key] || "";
}

function formatFunctionLine(name, expression, description = "") {
  const suffix = description ? ` (${description})` : "";
  return `  ${name}: ${expression}${suffix}`;
}

function solveLinearSystem(matrix, vector) {
  const size = Array.isArray(matrix) ? matrix.length : 0;
  if (size === 0 || !Array.isArray(vector) || vector.length !== size) return null;

  const augmented = matrix.map((row, rowIndex) => {
    const safeRow = Array.isArray(row) ? row.slice(0, size) : [];
    while (safeRow.length < size) safeRow.push(0);
    safeRow.push(vector[rowIndex]);
    return safeRow;
  });

  for (let pivot = 0; pivot < size; pivot += 1) {
    let maxRow = pivot;
    let maxAbs = Math.abs(augmented[pivot][pivot]);

    for (let row = pivot + 1; row < size; row += 1) {
      const absVal = Math.abs(augmented[row][pivot]);
      if (absVal > maxAbs) {
        maxAbs = absVal;
        maxRow = row;
      }
    }

    if (maxAbs < 1e-14) return null;
    if (maxRow !== pivot) {
      const temp = augmented[pivot];
      augmented[pivot] = augmented[maxRow];
      augmented[maxRow] = temp;
    }

    const pivotValue = augmented[pivot][pivot];
    for (let col = pivot; col <= size; col += 1) {
      augmented[pivot][col] /= pivotValue;
    }

    for (let row = 0; row < size; row += 1) {
      if (row === pivot) continue;
      const factor = augmented[row][pivot];
      if (Math.abs(factor) < 1e-14) continue;
      for (let col = pivot; col <= size; col += 1) {
        augmented[row][col] -= factor * augmented[pivot][col];
      }
    }
  }

  return augmented.map((row) => row[size]);
}

function evaluatePolynomial(coefficients, x) {
  let result = 0;
  for (let power = coefficients.length - 1; power >= 0; power -= 1) {
    result = result * x + toFiniteNumber(coefficients[power], 0);
  }
  return result;
}

function fitPolynomialCoefficients(xValues, yValues, degree) {
  const n = Math.min(xValues.length, yValues.length);
  const d = Math.max(0, Math.min(3, Math.floor(degree)));
  if (n < d + 1) return null;

  const maxAbsX = xValues.reduce((maxVal, x) => Math.max(maxVal, Math.abs(toFiniteNumber(x, 0))), 0);
  const scale = Math.max(1, maxAbsX);
  const scaledX = xValues.map((x) => toFiniteNumber(x, 0) / scale);
  const y = yValues.map((val) => toFiniteNumber(val, 0));

  const size = d + 1;
  const normalMatrix = Array.from({ length: size }, () => Array.from({ length: size }, () => 0));
  const rhs = Array.from({ length: size }, () => 0);

  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      let sum = 0;
      for (let i = 0; i < n; i += 1) {
        sum += scaledX[i] ** (row + col);
      }
      normalMatrix[row][col] = sum;
    }

    let rhsSum = 0;
    for (let i = 0; i < n; i += 1) {
      rhsSum += y[i] * scaledX[i] ** row;
    }
    rhs[row] = rhsSum;
  }

  const coeffScaled = solveLinearSystem(normalMatrix, rhs);
  if (!coeffScaled) return null;

  return coeffScaled.map((value, power) => value / scale ** power);
}

function computeNormalizedRmse(coefficients, xValues, yValues) {
  const n = Math.min(xValues.length, yValues.length);
  if (n === 0) return Number.POSITIVE_INFINITY;

  let sumSquared = 0;
  let yMin = Number.POSITIVE_INFINITY;
  let yMax = Number.NEGATIVE_INFINITY;

  for (let i = 0; i < n; i += 1) {
    const x = toFiniteNumber(xValues[i], 0);
    const y = toFiniteNumber(yValues[i], 0);
    const estimated = evaluatePolynomial(coefficients, x);
    const error = estimated - y;
    sumSquared += error * error;
    yMin = Math.min(yMin, y);
    yMax = Math.max(yMax, y);
  }

  const rmse = Math.sqrt(sumSquared / n);
  const range = yMax - yMin;
  const normalizer = range > 1e-9 ? range : Math.max(1, Math.abs(yMax), Math.abs(yMin));
  return rmse / normalizer;
}

function inferTracePolynomialExpression(trace) {
  const xRaw = Array.isArray(trace?.x) ? trace.x : [];
  const yRaw = Array.isArray(trace?.y) ? trace.y : [];
  const n = Math.min(xRaw.length, yRaw.length);
  if (n < 2) return "";

  const xValues = [];
  const yValues = [];
  for (let i = 0; i < n; i += 1) {
    const x = Number(xRaw[i]);
    const y = Number(yRaw[i]);
    if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
    xValues.push(x);
    yValues.push(y);
  }

  if (xValues.length < 2) return "";

  let best = null;
  for (let degree = 0; degree <= 3; degree += 1) {
    const coefficients = fitPolynomialCoefficients(xValues, yValues, degree);
    if (!coefficients) continue;
    const nrmse = computeNormalizedRmse(coefficients, xValues, yValues);
    if (!best || nrmse < best.nrmse) {
      best = { coefficients, nrmse };
    }
  }

  if (!best) return "";
  const expression = formatPolynomialExpression(best.coefficients);
  if (best.nrmse <= 5e-5) return expression;
  if (best.nrmse <= 0.015) return `~${expression}`;
  return "";
}

function functionExpressionFromCurveParams(curveDef) {
  if (!curveDef || typeof curveDef !== "object") return "";
  const type = String(curveDef.type || "").toLowerCase();

  if (type === "linear") {
    return formatPolynomialExpression([toFiniteNumber(curveDef.b, 0), toFiniteNumber(curveDef.a, 0)]);
  }
  if (type === "quadratic") {
    return formatPolynomialExpression([
      toFiniteNumber(curveDef.c, 0),
      toFiniteNumber(curveDef.b, 0),
      toFiniteNumber(curveDef.a, 0),
    ]);
  }
  if (type === "exp") {
    const amplitude = formatFormulaNumber(toFiniteNumber(curveDef.A, 1));
    const rate = formatFormulaNumber(toFiniteNumber(curveDef.rate, 0.1));
    return appendSignedConstant(`${amplitude}*exp(-${rate}*x)`, toFiniteNumber(curveDef.c, 0));
  }

  return "";
}

function buildFunctionLinesFromSpec(spec) {
  if (!spec || typeof spec !== "object") return [];

  const specType = String(spec.type || "").toLowerCase();
  const params = spec.params && typeof spec.params === "object" ? spec.params : null;
  const lines = [];

  if (specType === "economic-curves" && params) {
    const hasMonopolyRevenue = Number.isFinite(Number(params.a2)) && Number.isFinite(Number(params.a1));
    const k3 = toFiniteNumber(params.k3, 0);
    const k2 = toFiniteNumber(params.k2, 0);
    const k1 = toFiniteNumber(params.k1, 0);
    const k0 = toFiniteNumber(params.k0, 0);
    const price = toFiniteNumber(params.price, 0);

    let eExpr = formatPolynomialExpression([0, price]);
    let gExpr = formatPolynomialExpression([-k0, price - k1, -k2, -k3]);
    let pExpr = formatPolynomialExpression([price]);

    if (hasMonopolyRevenue) {
      const a2 = toFiniteNumber(params.a2, 0);
      const a1 = toFiniteNumber(params.a1, 0);
      eExpr = formatPolynomialExpression([0, a1, a2]);
      gExpr = formatPolynomialExpression([-k0, a1 - k1, a2 - k2, -k3]);
      pExpr = formatPolynomialExpression([a1, a2]);
    }

    const kExpr = formatPolynomialExpression([k0, k1, k2, k3]);

    lines.push(formatFunctionLine("E(x)", eExpr, "Erloesfunktion"));
    lines.push(formatFunctionLine("K(x)", kExpr, "Kostenfunktion"));
    lines.push(formatFunctionLine("G(x)", gExpr, "Gewinnfunktion"));
    lines.push(formatFunctionLine("p(x)", pExpr, "Preisfunktion"));
    return lines;
  }

  if (specType === "cost-curves" && params) {
    const k3 = toFiniteNumber(params.k3, 0);
    const k2 = toFiniteNumber(params.k2, 0);
    const k1 = toFiniteNumber(params.k1, 0);
    const k0 = toFiniteNumber(params.k0, 0);

    const gkExpr = formatPolynomialExpression([k1, 2 * k2, 3 * k3]);
    const kvExpr = formatPolynomialExpression([k1, k2, k3]);
    const kExpr = `${formatPolynomialExpression([k1, k2, k3])}${k0 >= 0 ? "+" : ""}${formatFormulaNumber(k0)}*x^-1`;

    lines.push(formatFunctionLine("K'(x)", gkExpr, "Grenzkostenfunktion"));
    lines.push(formatFunctionLine("k(x)", kExpr, "Stueckkostenfunktion"));
    lines.push(formatFunctionLine("kv(x)", kvExpr, "Variable Stueckkostenfunktion"));
    return lines;
  }

  if (specType === "market-curves" && params) {
    const supplyExpr = formatPolynomialExpression([
      toFiniteNumber(params.minPrice, 0),
      toFiniteNumber(params.supplySlope, 1),
    ]);
    const demandExpr = formatPolynomialExpression([
      toFiniteNumber(params.maxPrice, 0),
      -toFiniteNumber(params.demandSlope, 1),
    ]);

    lines.push(formatFunctionLine("p_A(x)", supplyExpr, "Angebotsfunktion"));
    lines.push(formatFunctionLine("p_N(x)", demandExpr, "Nachfragefunktion"));
    return lines;
  }

  if ((specType === "market-equilibrium" || specType === "market-abschoepfung") && params) {
    const supplyExpr = functionExpressionFromCurveParams(params.supply);
    const demandExpr = functionExpressionFromCurveParams(params.demand);

    if (supplyExpr) lines.push(formatFunctionLine("p_A(x)", supplyExpr, "Angebotsfunktion"));
    if (demandExpr) lines.push(formatFunctionLine("p_N(x)", demandExpr, "Nachfragefunktion"));
    if (lines.length > 0) return lines;
  }

  const traces = Array.isArray(spec.traces) ? spec.traces : [];
  traces.forEach((trace, index) => {
    const name = String(trace?.name || "").trim() || `f_${index + 1}(x)`;
    const expression = inferTracePolynomialExpression(trace);
    if (!expression) return;
    const description = describeFunctionName(name);
    lines.push(formatFunctionLine(name, expression, description));
  });

  return lines;
}

function buildVisualContext(task, runtimeTaskNode = null) {
  const visual = task?.visual;
  const spec = visual?.spec;
  const lines = [];
  const graphFromDom = extractGraphDescriptions(runtimeTaskNode);
  if (graphFromDom) {
    lines.push(graphFromDom);
  }

  if (!visual || !spec) {
    return lines.join("\n");
  }

  const specType = String(spec.type || "").toLowerCase();

  // Layout-based title/axes (for Plotly-rendered charts)
  const layout = spec.layout || {};
  const diagrammTitel = layout?.title || "";
  if (diagrammTitel) {
    lines.push(`Diagramm: ${diagrammTitel}`);
  } else if (specType && !["vft", "wkt-tabelle"].includes(specType)) {
    lines.push(`Diagrammtyp: ${specType}`);
  }

  const xTitle = layout?.xaxis?.title;
  const yTitle = layout?.yaxis?.title;
  if (xTitle) lines.push(`x-Achse: ${xTitle}`);
  if (yTitle) lines.push(`y-Achse: ${yTitle}`);

  // Function lines from parametric spec types
  const functionLines = buildFunctionLinesFromSpec(spec);
  if (functionLines.length > 0) {
    lines.push("Funktionen:");
    lines.push(...functionLines);
  }

  // Explicit funktionen array from generator (e.g. Produktlebenszyklus)
  const explicitFns = Array.isArray(spec.funktionen) ? spec.funktionen : [];
  if (explicitFns.length > 0 && functionLines.length === 0) {
    lines.push("Funktionen:");
    explicitFns.forEach((fn) => {
      const name = fn.name || "";
      const term = fn.term || "";
      const desc = fn.beschreibung || "";
      lines.push(`  ${name ? `${name}: ` : ""}${term}${desc ? ` (${desc})` : ""}`);
    });
  }

  // ── ab-tree (Baumdiagramm) ──
  if (specType === "ab-tree") {
    const pa = spec.pa;
    const pba = spec.pba;
    const pbna = spec.pbna;
    if (pa != null) lines.push(`  P(A) = ${pa}`);
    if (pba != null) lines.push(`  P_A(B) = ${pba}`);
    if (pbna != null) lines.push(`  P_A̅(B) = ${pbna}`);
    const given = Array.isArray(spec.givenSlots) ? spec.givenSlots : [];
    if (given.length > 0) lines.push(`  Gegebene Felder: ${given.join(", ")}`);
  }

  // ── vft (Vierfeldertafel) ──
  if (specType === "vft") {
    if (!diagrammTitel) lines.push("Vierfeldertafel");
    const slots = typeof spec.slots === "object" && spec.slots ? spec.slots : {};
    const givenSlots = new Set(Array.isArray(spec.givenSlots) ? spec.givenSlots : []);
    const slotLabels = {
      1: "P(A∩B)", 2: "P(A∩B̅)", 3: "P(A̅∩B)", 4: "P(A̅∩B̅)",
      5: "P(A)", 6: "P(A̅)", 7: "P(B)", 8: "P(B̅)",
    };
    const givenParts = [];
    for (const idx of givenSlots) {
      const label = slotLabels[idx] || `Feld ${idx}`;
      const val = slots[String(idx)];
      if (val != null) givenParts.push(`${label} = ${val}`);
    }
    if (givenParts.length > 0) lines.push(`Gegeben: ${givenParts.join(", ")}`);
  }

  // ── wkt-tabelle (Wahrscheinlichkeitstabelle) ──
  if (specType === "wkt-tabelle") {
    if (!diagrammTitel) lines.push("Wahrscheinlichkeitstabelle");
    const xVals = Array.isArray(spec.x) ? spec.x : [];
    const pVals = Array.isArray(spec.p) ? spec.p : [];
    if (xVals.length > 0) lines.push(`x-Werte: ${xVals.join(", ")}`);
    if (pVals.length > 0) lines.push(`P(X=x_i): ${pVals.join(", ")}`);
  }

  // ── verflechtungsdiagramm ──
  if (specType === "verflechtungsdiagramm") {
    if (!diagrammTitel) lines.push("Verflechtungsdiagramm");
    const r = Array.isArray(spec.rohstoffe) ? spec.rohstoffe : [];
    const z = Array.isArray(spec.zwischenprodukte) ? spec.zwischenprodukte : [];
    const e = Array.isArray(spec.endprodukte) ? spec.endprodukte : [];
    if (r.length > 0) lines.push(`  Rohstoffe: ${r.join(", ")}`);
    if (z.length > 0) lines.push(`  Zwischenprodukte: ${z.join(", ")}`);
    if (e.length > 0) lines.push(`  Endprodukte: ${e.join(", ")}`);
  }

  // ── binomial-histogramm ──
  if (specType === "binomial-histogramm-einzeln" || specType === "binomial-histogramm-kumuliert") {
    const n = spec.n;
    const p = spec.p;
    if (n != null) lines.push(`  n = ${n}`);
    if (p != null) lines.push(`  p = ${p}`);
  }

  // Fallback: raw params if no function lines and no specific handler matched
  const params = spec.params && typeof spec.params === "object" ? spec.params : null;
  if (params && functionLines.length === 0 && !["ab-tree", "vft", "wkt-tabelle", "verflechtungsdiagramm", "binomial-histogramm-einzeln", "binomial-histogramm-kumuliert"].includes(specType)) {
    lines.push("Parameter:");
    Object.entries(params).forEach(([key, value]) => {
      lines.push(`- ${key}: ${value}`);
    });
  }

  return lines.join("\n");
}

function buildTrainingKiAgentPrompt({ check, task, taskIndex, totalTasks, runtimeTaskNode = null, beispielHtml = "" }) {
  const schlagwort = check?.Schlagwort || check?.["Ich kann"] || `Check ${check?.Nummer ?? ""}`;
  const lernbereich = check?.LernbereichAnzeigename || check?.Lernbereich || "";
  const kompetenz = check?.["Ich kann"] || "";
  const einleitung = convertJsonLatexToMarkdown(htmlToPlainText(task?.einleitung || ""));
  const fragen = Array.isArray(task?.fragen) ? task.fragen : [];
  const antworten = Array.isArray(task?.antworten) ? task.antworten : [];
  const visualContext = buildVisualContext(task, runtimeTaskNode);

  const fragenBlock = fragen
    .map((frage, index) => `- Teilfrage ${index + 1}: ${convertJsonLatexToMarkdown(String(frage || "").trim())}`)
    .join("\n");

  const loesungsBlock = antworten
    .map((antwort, index) => `- Teilfrage ${index + 1}:\n${buildAnswerTargetText(antwort || "")}`)
    .join("\n\n");

  const tips = Array.isArray(check?.Tipps) ? check.Tipps : [];
  const tippsBlock = tips.length > 0
    ? `Hinweise:\n${tips.map((t) => `- ${convertJsonLatexToMarkdown(t)}`).join("\n")}`
    : "";

  const beispielText = beispielHtml ? htmlToPlainText(beispielHtml).trim() : "";
  const beispielBlock = beispielText
    ? `## Musterbeispiel mit anderen Zufallszahlen\nOrientiere dich intern an diesem Beispiel, um passende Erklärungen zu geben. Zeige es nicht direkt.\n\n${beispielText}`
    : "";

  const hintergrundBlock = [tippsBlock, beispielBlock].filter(Boolean).join("\n\n");

  const nextTaskUrl = buildTrainingCheckUrl(check) || "https://www.mathechecks.de/dev/lernbereiche/.../training.html";

  const einleitungParts = [einleitung || "(keine Einleitung vorhanden)"];
  if (visualContext) {
    einleitungParts.push(visualContext);
  }
  const aufgabenstellungBlock = einleitungParts.join("\n\n");

  return `# Rolle
Du bist ein KI-Lernpartner für das Trainingsmodul. Der Lernende arbeitet an einer konkreten Mathe-Aufgabe, und du bist der Erklärer: Du hilfst, Verständnislücken zu schließen und Lösungswege nachvollziehbar zu machen. Du sprichst Deutsch und duzt den Lernenden.

# Thema
Check: ${schlagwort}
Lernbereich: ${lernbereich}
Kompetenz: Ich kann ${convertJsonLatexToMarkdown(kompetenz)}

# Konkrete Mathe-Aufgabe
## Aufgabenstellung
${aufgabenstellungBlock}

## Fragen
${fragenBlock || "(keine Teilfragen vorhanden)"}

## Hinterlegte Zielantworten (intern)
${loesungsBlock || "(keine Zielantworten vorhanden)"}

# Weiteres Hintergrundwissen
${hintergrundBlock || "(keine weiteren Hintergrundhinweise hinterlegt)"}

# Stil
- Reagiere natürlich und abwechslungsreich.
- Lobe kurz und ehrlich, wenn ein Teilschritt gut ist.
- Erkläre mit kurzen, klaren Schritten und aufgabennaher Sprache.
- Wenn der Lernende einen Fehler macht, korrigiere freundlich und begründe kurz warum.
- Halte dich kurz. Keine langen Monologe.
- Antworte immer auf Deutsch.

# Ablauf
## Phase 1 - Einstieg
Begrüße den Lernenden kurz und starte direkt mit einer Frage zur Aufgabe:
Zum Beispiel: "Okay, was hast du bei dieser Aufgabe nicht verstanden?"
Wenn die Frage zu allgemein ist, bitte um eine konkrete Teilfrage.

## Phase 2 - Erklären und begleiten (3-6 Runden)
- Wenn der Lernende eine konkrete Teilfrage nennt, erkläre diese zuerst, falls es didaktisch sinnvoll ist. Wenn man zunächst eine andere Teilfrage behandeln sollte, arbeite damit weiter.
- Wenn der Lernende "alles" sagt, gehe Teilfrage für Teilfrage in der Reihenfolge durch.
- Nutze dein Hintergrundwissen, um Erklärungen fachlich korrekt zu halten.
- Nutze die Diagramminformationen aus der Aufgabenstellung, wenn sie fuer den Schritt relevant sind.
- Frage nach jeder abgeschlossenen Erklärung, ob es noch weitere Unklarheiten gibt.

## Phase 3 – Zusammenfassung
Wenn keine Fragen mehr gestellt werden oder du denkst, dass der Lernende dazu bereit ist:
1. Fasse die Lösung noch einmal zusammen.
2. Motiviere, eine weitere Trainingsaufgabe dieser Art zu bearbeiten, gib dabei den Link zur Aufgabe: ${nextTaskUrl}
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

function createTrainingCardHeader(check, titleText = check.Schlagwort || check["Ich kann"] || `Check ${check.Nummer}`) {
  const header = document.createElement("div");
  header.className = "dev-check-card__header";

  const headerLeft = createCheckMetaRowNode(
    {
      numberText: formatCheckNumber(check?.Nummer),
      titleText,
      prefix: "Aufgabe",
      tone: "training",
      rowClass: "dev-check-card__header-left",
      titleTag: "span",
    }
  );

  const headerRight = document.createElement("div");
  headerRight.className = "dev-check-card__header-actions";

  const { menu: actionsMenu, popover: actionsPopover } = createCardActionsMenu();
  headerRight.appendChild(actionsMenu);

  const skriptTippsHref = buildSkriptTippsHref(check);
  if (skriptTippsHref) {
    actionsPopover.appendChild(createCardMenuLink({ emoji: "💡", label: "Tipps", href: skriptTippsHref }));
  }

  header.appendChild(headerLeft);
  header.appendChild(headerRight);
  return { header, actionsPopover };
}

export {
  buildTrainingKiAgentPrompt,
  buildSkriptTippsHref,
  createTrainingCardHeader,
  copyToClipboard as copyTrainingPromptToClipboard,
  fetchBeispielHtml as fetchTrainingBeispielHtml,
};

function createTaskCardNode(
  check,
  aufgabe,
  onReloadTask = null,
  taskUiStateKey = "",
  readPersistedState = true,
  shuffleSeed = "",
  taskIndex = 0,
  totalTasks = 0
) {
  const titel = check.Schlagwort || check["Ich kann"] || `Check ${check.Nummer}`;
  const card = document.createElement("article");
  card.className = "dev-check-card dev-check-card--training";

  const { header, actionsPopover } = createTrainingCardHeader(check, titel);
  card.appendChild(header);

  const body = document.createElement("div");
  body.className = "dev-check-card__body";
  card.appendChild(body);

  if (!aufgabe) {
    body.textContent = "Keine Aufgabe in dieser Sammlung gefunden.";
    return card;
  }

  const effectiveAufgabe = check?.questionOrder === "shuffle"
    ? shuffleQuestionsInTask(aufgabe, shuffleSeed || taskUiStateKey)
    : aufgabe;

  let runtimeTaskNode = null;

  const aiAgentItem = createCardMenuItem({
    emoji: "✨",
    label: "KI-Erkläragent kopieren",
    closeOnClick: false,
    onClick: async () => {
      await runCardMenuItemFeedbackAction(aiAgentItem, {
        pendingLabel: "Wird erstellt…",
        successLabel: "Kopiert!",
        errorLabel: "Fehler",
        pendingIcon: "✨",
        action: async () => {
          const beispielHtml = await fetchBeispielHtml(check);
          const prompt = buildTrainingKiAgentPrompt({
            check,
            task: effectiveAufgabe,
            taskIndex,
            totalTasks,
            runtimeTaskNode,
            beispielHtml,
          });
          return copyToClipboard(prompt);
        },
      });
    },
  });
  actionsPopover.appendChild(aiAgentItem);

  runtimeTaskNode = renderRuntimeTask(effectiveAufgabe, {
    index: 0,
    showSolution: false,
    showTaskHeading: false,
    containerClass: "dev-check-card__runtime-task",
    interaction: {
      enablePerQuestionCheck: true,
      enableReload: true,
      enableSolutionToggle: true,
      enableScriptInfoLink: false,
      statePersistenceKey: taskUiStateKey,
      readPersistedState,
      onReload: onReloadTask,
    },
  });
  body.appendChild(runtimeTaskNode);

  const runtimeToolbar = runtimeTaskNode.querySelector(".task-toolbar");
  const runtimeActionButtons = runtimeTaskNode.querySelectorAll(".task-toolbar__actions .task-toolbar-btn");
  const runtimeSolutionBtn = Array.from(runtimeActionButtons).find((button) => {
    const label = `${button.getAttribute("aria-label") || ""} ${button.title || ""}`.toLowerCase();
    return label.includes("loesung") || label.includes("lösung");
  });
  const runtimeReloadBtn = Array.from(runtimeActionButtons).find((button) => {
    const label = `${button.getAttribute("aria-label") || ""} ${button.title || ""}`.toLowerCase();
    return label.includes("neue aufgabe");
  });

  if (runtimeSolutionBtn) {
    const isHidden = () => {
      const label = (runtimeSolutionBtn.getAttribute("aria-label") || runtimeSolutionBtn.title || "").toLowerCase();
      return label.includes("ausblenden");
    };

    const solutionItem = createCardMenuItem({
      emoji: "👁️",
      label: isHidden() ? "Lösungen ausblenden" : "Lösungen anzeigen",
      onClick: () => {
        runtimeSolutionBtn.click();
        const labelSpan = solutionItem.querySelector("span:last-child");
        if (labelSpan) labelSpan.textContent = isHidden() ? "Lösungen ausblenden" : "Lösungen anzeigen";
      },
    });
    actionsPopover.appendChild(solutionItem);
  }

  if (runtimeReloadBtn) {
    actionsPopover.appendChild(createCardMenuItem({
      emoji: "🔄",
      label: "Neue Aufgabe",
      onClick: () => runtimeReloadBtn.click(),
    }));
  }

  if (runtimeToolbar) {
    runtimeToolbar.remove();
  }

  return card;
}

function createBrowseTaskCardNode(check, sammlung, options = {}) {
  const {
    initialTaskIndex = 0,
    onTaskIndexChange = null,
    readPersistedState = true,
  } = options;

  const hasTasks = Array.isArray(sammlung) && sammlung.length > 0;
  let taskIndex = Number.isInteger(initialTaskIndex) ? initialTaskIndex : 0;
  if (!hasTasks || taskIndex < 0 || taskIndex >= sammlung.length) {
    taskIndex = 0;
  }

  let cardNode = null;
  const checkId = getCheckId(check);
  const anchorId = getTrainingCheckAnchorId(check);
  const viewportNode = document.createElement("section");
  viewportNode.className = "check-viewport-item check-viewport-item--scroll-card";
  viewportNode.id = anchorId;
  viewportNode.dataset.checkId = checkId;

  if (hasTasks && typeof onTaskIndexChange === "function") {
    onTaskIndexChange(taskIndex);
  }

  if (!hasTasks) {
    cardNode = createTaskCardNode(check, null, null);
    viewportNode.appendChild(cardNode);
    return viewportNode;
  }

  let shuffleNonce = loadShuffleNonce(check.Lernbereich, checkId) || String(Date.now());
  saveShuffleNonce(check.Lernbereich, checkId, shuffleNonce);

  const renderCurrentCard = (shouldReadPersistedState = readPersistedState) => {
    const stateKey = buildTaskUiStateKey({ lernbereich: check.Lernbereich, checkId, taskIndex });
    return createTaskCardNode(
      check,
      sammlung[taskIndex] || null,
      () => {
        taskIndex = pickRandomTaskIndex(taskIndex, sammlung.length);
        shuffleNonce = String(Date.now());
        saveShuffleNonce(check.Lernbereich, checkId, shuffleNonce);
        if (typeof onTaskIndexChange === "function") {
          onTaskIndexChange(taskIndex);
        }
        const nextCard = renderCurrentCard(false);
        cardNode.replaceWith(nextCard);
        cardNode = nextCard;
        finalizeTaskRender(viewportNode);
      },
      stateKey,
      shouldReadPersistedState,
      `${stateKey}::${shuffleNonce}`,
      taskIndex,
      sammlung.length
    );
  };

  cardNode = renderCurrentCard();
  viewportNode.appendChild(cardNode);
  return viewportNode;
}

function renderInfoFallback(root, text) {
  root.innerHTML = `<p class="dev-module__status">${text}</p>`;
  finalizeTaskRender(root);
}

function bindShell(root) {
  return {
    taskHost: root.querySelector("#dev-training-task"),
    jumpNav: document.getElementById("dev-training-jump-nav"),
  };
}

const trainingJumpNavScrollCleanup = new WeakMap();

function renderTrainingJumpNav(navNode, checks, activeCheckId = "") {
  if (!navNode) return;

  navNode.innerHTML = checks
    .map((check) => {
      const checkId = getCheckId(check);
      const label = `${check.Nummer}. ${check.Schlagwort || "Check"}`;
      const href = `#${getTrainingCheckAnchorId(check)}`;
      const activeClass = checkId === activeCheckId ? " active" : "";
      return `<a class="check-jump-tab${activeClass}" href="${href}" data-check-id="${checkId}">${label}</a>`;
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

function setTrainingJumpNavActive(navNode, checkId) {
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

function bindTrainingJumpNavScrollSync(navNode, cardNodes) {
  if (!navNode) return;

  const existingCleanup = trainingJumpNavScrollCleanup.get(navNode);
  if (typeof existingCleanup === "function") {
    existingCleanup();
    trainingJumpNavScrollCleanup.delete(navNode);
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
    setTrainingJumpNavActive(navNode, activeCard?.dataset?.checkId || "");
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

  trainingJumpNavScrollCleanup.set(navNode, () => {
    scrollSource.removeEventListener("scroll", onViewportChange);
    window.removeEventListener("resize", onViewportChange);
  });
}

function setTaskMessage(taskHost, message, isError = false) {
  if (!taskHost) return;
  const color = isError ? "var(--rose)" : "var(--text-dim)";
  taskHost.innerHTML = `<p class="dev-module__status" style="color:${color};">${message}</p>`;
  finalizeTaskRender(taskHost);
}

export async function initTrainingModule({
  root,
  lernbereich,
  preferredCheckId = "",
  usePersistedState = true,
}) {
  const shell = bindShell(root);
  if (!shell.taskHost) {
    renderInfoFallback(root, "Training-Shell nicht gefunden.");
    return;
  }

  if (!lernbereich) {
    setTaskMessage(shell.taskHost, "Kein Lernbereich gesetzt (data-lernbereich fehlt).", true);
    return;
  }

  const checks = await getChecksByLernbereich(lernbereich);
  if (checks.length === 0) {
    setTaskMessage(shell.taskHost, `Keine Checks fuer Lernbereich "${lernbereich}" gefunden.`, true);
    return;
  }

  const state = usePersistedState
    ? loadTrainingState(lernbereich)
    : { selectedCheckId: null, taskIndexByCheckId: {} };
  const hasPreferredCheckId = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";
  const preferredCheckIdFromHash = resolvePreferredCheckIdFromHash(checks);

  function persist() {
    saveTrainingState(lernbereich, state);
  }

  async function renderBrowseFallback(preferredCheckIdForBrowse = "") {
    shell.taskHost.innerHTML = "";

    const preferredId = typeof preferredCheckIdForBrowse === "string"
      ? preferredCheckIdForBrowse.trim()
      : "";
    const activeCheckId = preferredId || state.selectedCheckId || "";
    if (activeCheckId) {
      state.selectedCheckId = activeCheckId;
      persist();
    }
    renderTrainingJumpNav(shell.jumpNav, checks, activeCheckId);

    const cards = await Promise.all(
      checks.map(async (check) => {
        try {
          const sammlung = await getAufgabenSammlung(check.Sammlung, {
            gebiet: check.Gebiet,
            lernbereich: check.Lernbereich,
          });
          const checkId = getCheckId(check);
          return createBrowseTaskCardNode(check, sammlung, {
            initialTaskIndex: Number.isInteger(state.taskIndexByCheckId[checkId])
              ? usePersistedState
                ? loadTaskIndexForCheck(lernbereich, checkId, state.taskIndexByCheckId[checkId])
                : state.taskIndexByCheckId[checkId]
              : usePersistedState
                ? loadTaskIndexForCheck(
                  lernbereich,
                  checkId,
                  pickRandomTaskIndex(-1, Array.isArray(sammlung) ? sammlung.length : 0)
                )
                : pickRandomTaskIndex(-1, Array.isArray(sammlung) ? sammlung.length : 0),
            readPersistedState: usePersistedState,
            onTaskIndexChange: (taskIndex) => {
              state.taskIndexByCheckId[checkId] = taskIndex;
              saveTaskIndexForCheck(lernbereich, checkId, taskIndex);
              persist();
            },
          });
        } catch (error) {
          const card = document.createElement("article");
          card.className = "dev-check-card";
          const message = document.createElement("p");
          message.className = "dev-module__status";
          message.style.color = "var(--rose)";
          message.textContent = error.message;
          card.appendChild(message);
          return card;
        }
      })
    );

    cards.forEach((card) => shell.taskHost.appendChild(card));

    if (activeCheckId) {
      const cardNodes = Array.from(
        shell.taskHost.querySelectorAll(".check-viewport-item[data-check-id]")
      );
      const targetCard = cardNodes.find((card) => card.dataset.checkId === activeCheckId);
      if (targetCard) {
        setTrainingJumpNavActive(shell.jumpNav, activeCheckId);
        targetCard.scrollIntoView({ behavior: "auto", block: "start" });
      }
    }

    bindTrainingJumpNavScrollSync(
      shell.jumpNav,
      shell.taskHost.querySelectorAll(".check-viewport-item[data-check-id]")
    );
    finalizeTaskRender(shell.taskHost);
  }

  const preferredIdForBrowse =
    (hasPreferredCheckId ? preferredCheckId.trim() : "") || preferredCheckIdFromHash;
  await renderBrowseFallback(preferredIdForBrowse);
}
