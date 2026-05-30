import { buildBaumdiagrammFigure } from "../visuals/baumdiagramm.js";
import { buildBaumdiagrammBinomialFigure } from "../visuals/baumdiagramm-binomial.js";
import { buildHistogrammEinzelnFigure, buildHistogrammKumuliertFigure, binomialIntervalProbability } from "../visuals/histogramm.js";
import { buildHistogrammAllgemeinFigure } from "../visuals/histogramm-allgemein.js";
import { buildGraphFigure } from "../visuals/graph.js";
import { buildHMethodeAbleitungFigure } from "../visuals/h-methode-ableitung.js";
import { buildPunktwolkeRegressionFigure, createPunktwolkeRegressionScenario } from "../visuals/punktwolke-regression.js";
import { buildVerflechtungsdiagrammFigure } from "../visuals/verflechtungsdiagramm.js";
import { buildQuadratischeFunktionenFigure } from "../visuals/quadratische-funktionen.js";
import { buildQuadratischeParameterFigure } from "../visuals/quadratische-funktionen-parameter.js";
import { plotlyRender, themeTextColor } from "../visuals/plotly-defaults.js?v=20260507-plotly-hover-name-theme";

function parseNum(raw) {
    if (raw == null || raw === "") return null;
    return parseFloat(String(raw).replace(",", "."));
}

function parseSlots(raw) {
    if (raw == null || String(raw).trim() === "") return [];

    const text = String(raw).trim();

    if (text.startsWith("[") && text.endsWith("]")) {
        try {
            const parsed = JSON.parse(text);
            if (Array.isArray(parsed)) {
                return parsed
                    .map(Number)
                    .filter((n) => Number.isInteger(n) && n >= 1 && n <= 10);
            }
        } catch {
            // Fall back to separator-based parsing below.
        }
    }

    return text
        .replace(/[{}\[\]]/g, "")
        .split(/[\s,;]+/)
        .map(Number)
        .filter((n) => Number.isInteger(n) && n >= 1 && n <= 10);
}

function ensureEqualColumns(table) {
    if (!table) return;

    const hasManualColgroup = Array.from(table.children).some(
        (c) => c.tagName === "COLGROUP"
    );
    if (hasManualColgroup) return;

    const firstRow = table.querySelector("tr");
    if (!firstRow) return;

    const cols = [...firstRow.children].reduce((sum, cell) => {
        const colspan = parseInt(cell.getAttribute("colspan") || "1", 10);
        return sum + (Number.isFinite(colspan) && colspan > 0 ? colspan : 1);
    }, 0);

    if (cols < 1) return;

    const cg = document.createElement("colgroup");
    for (let i = 0; i < cols; i++) {
        cg.appendChild(document.createElement("col"));
    }
    table.insertBefore(cg, table.firstChild);
}

function normalizeTableCellText(value) {
    return String(value ?? "")
        .replace(/\s+/g, "")
        .replaceAll("$", "")
        .replaceAll("&nbsp;", "")
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .toUpperCase();
}

function isVierfeldertafel(table) {
    if (!table || table.classList.contains("vft-table")) return false;

    const rows = Array.from(table.rows);
    if (rows.length !== 4) return false;

    const grid = rows.map((row) => Array.from(row.cells));
    if (grid.some((row) => row.length !== 4)) return false;

    const values = grid.map((row) => row.map((cell) => normalizeTableCellText(cell.textContent)));
    const header = values[0];
    const firstCol = values.slice(1).map((row) => row[0] ?? "");
    const flatText = values.flat().join("|");
    const hasSigma = (text) => text.includes("Σ") || text.includes("SIGMA");

    return Boolean(
        header[1]?.includes("B")
        && header[2]?.includes("B")
        && hasSigma(header[3] ?? "")
        && firstCol[0]?.includes("A")
        && firstCol[1]?.includes("A")
        && hasSigma(firstCol[2] ?? "")
        && (flatText.includes("P(") || flatText.includes("0,") || flatText.includes("0.") || flatText.includes("|1|"))
    );
}

function wrapTablesForHorizontalScroll(root) {
    if (!root) return;

    root.querySelectorAll("table").forEach((table) => {
        if (isVierfeldertafel(table)) {
            table.classList.add("vft-table");
        }

        ensureEqualColumns(table);

        if (table.parentElement.classList.contains("table-scroll")) return;
        if (table.closest(".skript-widget")) return;  // widget tables have own layout

        const wrapper = document.createElement("div");
        wrapper.classList.add("table-scroll");
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

export function refreshSkriptTables(root) {
    wrapTablesForHorizontalScroll(root);
}

const MONO_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const MONO_TEXTS = [
    "Der zerstreute Detektiv verschlüsselte seine Einkaufsliste und wunderte sich dann sehr, warum er statt Zitronen, Zahnpasta und Zimtschnecken plötzlich zehn Zahnräder, zwei Zirkuszelte und eine Ziehharmonika bestellte.",
    "Im Geheimclub der gelangweilten Pinguine schrieb der Vorsitzende jede Einladung in einer monoalphabetischen Substitution, damit nicht schon wieder ein neugieriger Eisbär früher auftauchte und den gesamten Vanillepudding wegfutterte.",
    "Eine kluge Schülerin merkte beim Entschlüsseln sofort, dass ein langer deutscher Text viele verräterische Muster enthält, denn häufige Buchstaben tauchen erstaunlich oft auf, selbst wenn ein übermotivierter Caesar sie geschniegelt und geschniegelt verschoben hat.",
    "Der Hofzauberer verkündete feierlich, seine neue Geheimschrift sei absolut unknackbar, doch nach fünf Minuten Häufigkeitsanalyse las die halbe Schlossküche bereits mit, dass er heimlich jeden Mittwoch extra Erdbeereis mit Sahne und Streuseln bestellt.",
];
const MONO_GERMAN_FREQUENCIES = {
    E: 17.4, N: 9.8, I: 7.6, S: 7.3, R: 7.0, A: 6.5, T: 6.2, D: 5.1,
    H: 4.8, U: 4.4, L: 3.4, C: 3.1, G: 3.0, M: 2.5, O: 2.5, B: 1.9,
    W: 1.9, F: 1.7, K: 1.2, Z: 1.1, P: 0.8, V: 0.7, J: 0.3, Y: 0.04,
    X: 0.03, Q: 0.02,
};

const ROULETTE_RED_NUMBERS = new Set([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]);
const ROULETTE_WHEEL_ORDER = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26];
const ROULETTE_EVENTS = {
    red: { label: "rot", favorable: 18, matches: (number) => ROULETTE_RED_NUMBERS.has(number) },
    black: { label: "schwarz", favorable: 18, matches: (number) => number !== 0 && !ROULETTE_RED_NUMBERS.has(number) },
    even: { label: "gerade Zahl", favorable: 18, matches: (number) => number !== 0 && number % 2 === 0 },
    odd: { label: "ungerade Zahl", favorable: 18, matches: (number) => number % 2 === 1 },
    "first-dozen": { label: "1 bis 12", favorable: 12, matches: (number) => number >= 1 && number <= 12 },
    zero: { label: "0", favorable: 1, matches: (number) => number === 0 },
};

function formatDecimalDe(value, digits = 1) {
    return value.toFixed(digits).replace(".", ",");
}

function formatPercentDe(value, digits = 1) {
    return `${formatDecimalDe(value, digits)} %`;
}

function normalizeGermanAlphabetText(text) {
    return String(text)
        .replaceAll("Ä", "AE")
        .replaceAll("Ö", "OE")
        .replaceAll("Ü", "UE")
        .replaceAll("ä", "AE")
        .replaceAll("ö", "OE")
        .replaceAll("ü", "UE")
        .replaceAll("ß", "SS")
        .toUpperCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^A-Z ]+/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function shuffleItems(items) {
    const shuffled = [...items];
    for (let index = shuffled.length - 1; index > 0; index -= 1) {
        const swapIndex = Math.floor(Math.random() * (index + 1));
        [shuffled[index], shuffled[swapIndex]] = [shuffled[swapIndex], shuffled[index]];
    }
    return shuffled;
}

function createSubstitutionMap() {
    const shuffledLetters = shuffleItems(MONO_ALPHABET.split(""));
    const substitution = new Map();
    MONO_ALPHABET.split("").forEach((letter, index) => {
        substitution.set(letter, shuffledLetters[index]);
    });
    return substitution;
}

function encryptMonoalphabetic(text, substitution) {
    return text
        .split("")
        .map((character) => substitution.get(character) || character)
        .join("");
}

function buildLetterFrequencyList(text) {
    const letters = text.replace(/[^A-Z]/g, "").split("");
    const total = letters.length || 1;
    const counts = new Map();
    letters.forEach((letter) => counts.set(letter, (counts.get(letter) || 0) + 1));
    return Array.from(counts.entries())
        .map(([letter, count]) => ({ letter, percent: (count / total) * 100 }))
        .sort((first, second) => second.percent - first.percent || first.letter.localeCompare(second.letter));
}

function renderFrequencyList(container, frequencies) {
    if (!container) return;
    container.innerHTML = "";
    frequencies.forEach(({ letter, percent }) => {
        const row = document.createElement("div");
        row.className = "ms-widget__freq-row";
        const letterNode = document.createElement("span");
        letterNode.textContent = letter;
        const percentNode = document.createElement("span");
        percentNode.textContent = formatPercentDe(percent, percent < 0.1 ? 2 : 1);
        row.append(letterNode, percentNode);
        container.appendChild(row);
    });
}

function initMonoalphabetischeSubstitutionWidgets(root) {
    root.querySelectorAll(".ms-widget").forEach((widget) => {
        if (widget.dataset.bound === "true") return;
        widget.dataset.bound = "true";

        const cipherTextNode = widget.querySelector(".ms-widget__ciphertext");
        const decodedTextNode = widget.querySelector(".ms-widget__decoded");
        const mappingNode = widget.querySelector(".ms-widget__mapping");
        const statusNode = widget.querySelector(".ms-widget__status");
        const cipherFrequencyNode = widget.querySelector(".ms-widget__cipher-frequencies");
        const germanFrequencyNode = widget.querySelector(".ms-widget__german-frequencies");
        const newButton = widget.querySelector(".ms-widget__new");
        const resetButton = widget.querySelector(".ms-widget__reset");
        const germanFrequencies = Object.entries(MONO_GERMAN_FREQUENCIES)
            .map(([letter, percent]) => ({ letter, percent }))
            .sort((first, second) => second.percent - first.percent);

        let plainText = "";
        let cipherText = "";
        let guesses = new Map();
        let substitution = createSubstitutionMap();

        function decodedText() {
            return cipherText
                .split("")
                .map((character) => MONO_ALPHABET.includes(character) ? (guesses.get(character) || "_") : character)
                .join("");
        }

        function updateDecodedText() {
            const decoded = decodedText();
            decodedTextNode.textContent = decoded;
            const filledCount = Array.from(guesses.values()).filter(Boolean).length;
            const solved = decoded === plainText;
            statusNode.textContent = solved
                ? "Erfolgreich entschlüsselt"
                : `${filledCount} Buchstaben gesetzt`;
            statusNode.dataset.solved = solved ? "true" : "false";
        }

        function renderMappingInputs() {
            mappingNode.innerHTML = "";
            const uniqueCipherLetters = Array.from(new Set(cipherText.replace(/[^A-Z]/g, "").split(""))).sort();
            uniqueCipherLetters.forEach((cipherLetter) => {
                const field = document.createElement("label");
                field.className = "ms-widget__mapping-field";

                const cipherNode = document.createElement("span");
                cipherNode.className = "ms-widget__cipher-letter";
                cipherNode.textContent = cipherLetter;

                const input = document.createElement("input");
                input.type = "text";
                input.inputMode = "latin";
                input.maxLength = 1;
                input.autocomplete = "off";
                input.spellcheck = false;
                input.setAttribute("aria-label", `Klartextbuchstabe für ${cipherLetter}`);
                input.addEventListener("input", () => {
                    const normalized = input.value.toUpperCase().replace(/[^A-Z]/g, "").slice(0, 1);
                    input.value = normalized;
                    if (normalized) guesses.set(cipherLetter, normalized);
                    else guesses.delete(cipherLetter);
                    updateDecodedText();
                });

                field.append(cipherNode, input);
                mappingNode.appendChild(field);
            });
        }

        function startNewChallenge() {
            const rawText = MONO_TEXTS[Math.floor(Math.random() * MONO_TEXTS.length)];
            plainText = normalizeGermanAlphabetText(rawText);
            substitution = createSubstitutionMap();
            cipherText = encryptMonoalphabetic(plainText, substitution);
            guesses = new Map();
            cipherTextNode.textContent = cipherText;
            renderFrequencyList(cipherFrequencyNode, buildLetterFrequencyList(cipherText));
            renderFrequencyList(germanFrequencyNode, germanFrequencies);
            renderMappingInputs();
            updateDecodedText();
        }

        newButton?.addEventListener("click", startNewChallenge);
        resetButton?.addEventListener("click", () => {
            guesses = new Map();
            widget.querySelectorAll(".ms-widget__mapping input").forEach((input) => { input.value = ""; });
            updateDecodedText();
        });

        startNewChallenge();
    });
}

function rouletteColor(number) {
    if (number === 0) return "green";
    return ROULETTE_RED_NUMBERS.has(number) ? "red" : "black";
}

function rouletteEventDefinition(selectNode) {
    return ROULETTE_EVENTS[selectNode?.value] || ROULETTE_EVENTS.red;
}

function initRouletteWidgets(root) {
    root.querySelectorAll(".roulette-widget").forEach((widget) => {
        if (widget.dataset.bound === "true") return;
        widget.dataset.bound = "true";

        const eventSelect = widget.querySelector(".roulette-widget__event");
        const probabilityNode = widget.querySelector(".roulette-widget__probability");
        const spinOneButton = widget.querySelector(".roulette-widget__spin-one");
        const spinManyButton = widget.querySelector(".roulette-widget__spin-many");
        const resetButton = widget.querySelector(".roulette-widget__reset");
        const wheelNode = widget.querySelector(".roulette-widget__wheel");
        const resultNode = widget.querySelector(".roulette-widget__result");
        const spinsNode = widget.querySelector(".roulette-widget__spins");
        const hitsNode = widget.querySelector(".roulette-widget__hits");
        const relativeNode = widget.querySelector(".roulette-widget__relative");
        let spinCount = 0;
        let hitCount = 0;
        let rotation = 0;

        function updateProbability() {
            const eventDefinition = rouletteEventDefinition(eventSelect);
            probabilityNode.textContent = `$P(${eventDefinition.label}) = ${eventDefinition.favorable}/37 \\approx ${formatDecimalDe(eventDefinition.favorable / 37, 4)}$`;
            if (window.MathJax?.typesetPromise) {
                window.MathJax.typesetPromise([probabilityNode]);
            }
        }

        function updateStats() {
            spinsNode.textContent = String(spinCount);
            hitsNode.textContent = String(hitCount);
            relativeNode.textContent = spinCount > 0 ? formatDecimalDe(hitCount / spinCount, 4) : "-";
        }

        function showResult(number) {
            const color = rouletteColor(number);
            resultNode.textContent = String(number);
            resultNode.dataset.color = color;
            const pocketIndex = ROULETTE_WHEEL_ORDER.indexOf(number);
            const pocketAngle = (360 / ROULETTE_WHEEL_ORDER.length) * Math.max(pocketIndex, 0);
            rotation += 720 + (360 - pocketAngle);
            wheelNode.style.transform = `rotate(${rotation}deg)`;
        }

        function spin(times) {
            const eventDefinition = rouletteEventDefinition(eventSelect);
            let lastNumber = 0;
            for (let index = 0; index < times; index += 1) {
                const result = Math.floor(Math.random() * 37);
                spinCount += 1;
                if (eventDefinition.matches(result)) hitCount += 1;
                lastNumber = result;
            }
            showResult(lastNumber);
            updateStats();
        }

        function reset() {
            spinCount = 0;
            hitCount = 0;
            resultNode.textContent = "-";
            resultNode.dataset.color = "neutral";
            updateStats();
        }

        eventSelect?.addEventListener("change", () => {
            updateProbability();
            reset();
        });
        spinOneButton?.addEventListener("click", () => spin(1));
        spinManyButton?.addEventListener("click", () => spin(100));
        resetButton?.addEventListener("click", reset);

        updateProbability();
        reset();
    });
}

function initPunktwolkeRegressionWidgets(root) {
    root.querySelectorAll(".pr-widget").forEach((widget) => {
        if (widget.dataset.bound === "true") return;
        widget.dataset.bound = "true";

        const plotDiv = widget.querySelector(".pr-widget__plot");
        const typeNode = widget.querySelector(".pr-widget__type");
        const formulaNode = widget.querySelector(".pr-widget__formula");
        const refreshButton = widget.querySelector(".pr-widget__button");
        let revealTimer = null;

        if (!plotDiv || !typeNode || !formulaNode) return;

        function updateFormula(latex = "") {
            formulaNode.innerHTML = latex;
            if (latex && window.MathJax?.typesetPromise) {
                window.MathJax.typesetPromise([formulaNode]);
            }
        }

        function renderScenario() {
            if (revealTimer) {
                window.clearTimeout(revealTimer);
                revealTimer = null;
            }

            const scenario = createPunktwolkeRegressionScenario();
            typeNode.textContent = "Punktewolke wird analysiert ...";
            updateFormula("");

            const initialFigure = buildPunktwolkeRegressionFigure({ scenario, showCurve: false });
            plotlyRender(plotDiv, initialFigure.data, initialFigure.layout);

            revealTimer = window.setTimeout(() => {
                if (!widget.isConnected) return;
                typeNode.textContent = `Passende Regression: ${scenario.typeLabel}`;
                updateFormula(scenario.formulaLatex);
                const revealedFigure = buildPunktwolkeRegressionFigure({ scenario, showCurve: true });
                plotlyRender(plotDiv, revealedFigure.data, revealedFigure.layout);
            }, 1000);
        }

        refreshButton?.addEventListener("click", renderScenario);
        renderScenario();
    });
}

/* ---- Gauß-Schritte-Widget ---- */

const GAUSS_ROW_NAMES = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"];

function gaussRowName(index) {
    return GAUSS_ROW_NAMES[index] ?? `R_{${index + 1}}`;
}

function gaussFormatCell(value) {
    if (Object.is(value, -0)) value = 0;
    if (Number.isInteger(value)) return String(value);
    const rounded = Math.round(value * 1e9) / 1e9;
    if (Number.isInteger(rounded)) return String(rounded);
    for (let denom = 2; denom <= 16; denom += 1) {
        const numerator = rounded * denom;
        if (Math.abs(numerator - Math.round(numerator)) < 1e-9) {
            const num = Math.round(numerator);
            const sign = num < 0 ? "-" : "";
            return `${sign}\\tfrac{${Math.abs(num)}}{${denom}}`;
        }
    }
    return rounded.toString().replace(".", ",");
}

function gaussApplyOp(matrix, op) {
    const [type] = op;
    if (type === "addMul") {
        const [, target, source, factor] = op;
        for (let j = 0; j < matrix[target].length; j += 1) {
            matrix[target][j] = matrix[target][j] + factor * matrix[source][j];
        }
    } else if (type === "swap") {
        const [, a, b] = op;
        const tmp = matrix[a];
        matrix[a] = matrix[b];
        matrix[b] = tmp;
    } else if (type === "scale") {
        const [, row, factor] = op;
        for (let j = 0; j < matrix[row].length; j += 1) {
            matrix[row][j] = matrix[row][j] * factor;
        }
    }
}

function gaussOpRows(op) {
    const [type] = op;
    if (type === "addMul") return [op[1]];
    if (type === "swap") return [op[1], op[2]];
    if (type === "scale") return [op[1]];
    return [];
}

function gaussOpLabel(op) {
    return op[op.length - 1];
}

function gaussFormatSignedCell(value) {
    const formatted = gaussFormatCell(value);
    return value < 0 ? `(${formatted})` : formatted;
}

function gaussRenderMatrixLatex(matrix, highlightSet) {
    const nCols = matrix[0].length;
    const valueCols = nCols - 1;
    const colSpec = "r".repeat(valueCols) + "|r";
    const body = matrix
        .map((row, i) => row.map((value, j) => {
            const text = gaussFormatCell(value);
            if (highlightSet && highlightSet.has(`${i}:${j}`)) {
                return `{\\color{#d97706} ${text}}`;
            }
            return text;
        }).join(" & "))
        .join(" \\\\ ");
    return `\\left( \\begin{array}{${colSpec}} ${body} \\end{array} \\right)`;
}

function gaussComputeChangeMask(prev, next) {
    const mask = new Set();
    for (let i = 0; i < next.length; i += 1) {
        for (let j = 0; j < next[i].length; j += 1) {
            const a = prev?.[i]?.[j];
            if (a === undefined || Math.abs(a - next[i][j]) > 1e-9) {
                mask.add(`${i}:${j}`);
            }
        }
    }
    return mask;
}

function gaussRenderStepCalcLatex(prevMatrix, nextMatrix, step) {
    const lines = [];
    (step?.ops || []).forEach((op) => {
        const [type] = op;
        if (type === "addMul") {
            const [, target, source, factor] = op;
            const sign = factor >= 0 ? "+" : "-";
            const absF = Math.abs(factor);
            const factorPart = absF === 1 ? "" : `${gaussFormatCell(absF)} \\cdot `;
            const terms = [];
            for (let j = 0; j < prevMatrix[target].length; j += 1) {
                const a = prevMatrix[target][j];
                const b = prevMatrix[source][j];
                const r = nextMatrix[target][j];
                terms.push(
                    `${gaussFormatCell(a)} ${sign} ${factorPart}${gaussFormatSignedCell(b)} = {\\color{#d97706} ${gaussFormatCell(r)}}`,
                );
            }
            lines.push(`\\text{${gaussRowName(target)}:}\\;${terms.join(",\\;\\;")}`);
        } else if (type === "scale") {
            const [, row, factor] = op;
            const terms = [];
            for (let j = 0; j < prevMatrix[row].length; j += 1) {
                const a = prevMatrix[row][j];
                const r = nextMatrix[row][j];
                terms.push(
                    `${gaussFormatCell(factor)} \\cdot ${gaussFormatSignedCell(a)} = {\\color{#d97706} ${gaussFormatCell(r)}}`,
                );
            }
            lines.push(`\\text{${gaussRowName(row)}:}\\;${terms.join(",\\;\\;")}`);
        } else if (type === "swap") {
            const [, a, b] = op;
            lines.push(`\\text{Zeilen ${gaussRowName(a)} und ${gaussRowName(b)} getauscht.}`);
        }
    });
    if (!lines.length) return "";
    return `\\begin{aligned} ${lines.join(" \\\\ ")} \\end{aligned}`;
}

function gaussRenderOpsLatex(opsByRow, nRows) {
    const lines = [];
    for (let i = 0; i < nRows; i += 1) {
        const ops = opsByRow.get(i);
        lines.push(ops && ops.length ? ops.join(",\\;") : "\\phantom{X}");
    }
    return `\\begin{matrix} ${lines.join(" \\\\ ")} \\end{matrix}`;
}

function initGaussSchritteWidgets(root) {
    root.querySelectorAll(".gauss-widget").forEach((widget) => {
        if (widget.dataset.bound === "true") return;
        widget.dataset.bound = "true";

        let initialMatrix;
        let steps;
        try {
            initialMatrix = JSON.parse(widget.dataset.matrix);
            steps = JSON.parse(widget.dataset.steps);
        } catch (error) {
            console.warn("[gauss-widget] ungültige Konfiguration", error);
            return;
        }

        if (!Array.isArray(initialMatrix) || !Array.isArray(steps)) return;

        const matrices = [initialMatrix.map((row) => row.slice())];
        steps.forEach((step) => {
            const previous = matrices[matrices.length - 1];
            const next = previous.map((row) => row.slice());
            (step.ops || []).forEach((op) => gaussApplyOp(next, op));
            matrices.push(next);
        });

        const totalSteps = steps.length;
        let stepIndex = 0;

        const historyHost = widget.querySelector(".gauss-history");
        const labelNode = widget.querySelector(".gauss-step-label");
        const prevButton = widget.querySelector(".gauss-prev");
        const nextButton = widget.querySelector(".gauss-next");
        const resetButton = widget.querySelector(".gauss-reset");

        function opsByRowFor(step) {
            const opsByRow = new Map();
            (step?.ops || []).forEach((op) => {
                gaussOpRows(op).forEach((row) => {
                    const existing = opsByRow.get(row) ?? [];
                    existing.push(gaussOpLabel(op));
                    opsByRow.set(row, existing);
                });
            });
            return opsByRow;
        }

        function render() {
            const visibleCount = stepIndex + 1; // initial matrix + applied steps
            const parts = [];
            for (let i = 0; i < visibleCount; i += 1) {
                const matrix = matrices[i];
                const appliedStep = i < stepIndex ? steps[i] : null;
                const highlight = i > 0 ? gaussComputeChangeMask(matrices[i - 1], matrix) : null;

                if (i > 0) {
                    const calcLatex = gaussRenderStepCalcLatex(matrices[i - 1], matrix, steps[i - 1]);
                    if (calcLatex) {
                        parts.push(`<div class="gauss-calc">\\[ ${calcLatex} \\]</div>`);
                    }
                }

                parts.push('<div class="gauss-row">');
                parts.push(`<div class="gauss-matrix">\\[ ${gaussRenderMatrixLatex(matrix, highlight)} \\]</div>`);
                if (appliedStep) {
                    parts.push(
                        `<div class="gauss-ops">\\[ ${gaussRenderOpsLatex(opsByRowFor(appliedStep), matrix.length)} \\]</div>`,
                    );
                }
                parts.push("</div>");
            }
            historyHost.innerHTML = parts.join("");

            if (stepIndex < totalSteps) {
                const planned = steps[stepIndex];
                const title = planned.title ? `: ${planned.title}` : "";
                labelNode.textContent = `Nächste Umformung (${stepIndex + 1} von ${totalSteps})${title}`;
                labelNode.dataset.state = "active";
            } else {
                labelNode.textContent = `Zeilenstufenform nach ${totalSteps} Umformung${totalSteps === 1 ? "" : "en"} erreicht.`;
                labelNode.dataset.state = "done";
            }

            prevButton.disabled = stepIndex === 0;
            nextButton.disabled = stepIndex >= totalSteps;

            if (window.MathJax?.typesetPromise) {
                window.MathJax.typesetPromise([widget]).catch(() => { });
            }
        }

        prevButton?.addEventListener("click", () => {
            if (stepIndex > 0) {
                stepIndex -= 1;
                render();
            }
        });
        nextButton?.addEventListener("click", () => {
            if (stepIndex < totalSteps) {
                stepIndex += 1;
                render();
            }
        });
        resetButton?.addEventListener("click", () => {
            stepIndex = 0;
            render();
        });

        render();
    });
}

export function initSkriptVisuals(root) {
    if (!root) return;

    // Keep table semantics intact and move horizontal scrolling to the wrapper.
    refreshSkriptTables(root);
    initMonoalphabetischeSubstitutionWidgets(root);
    initRouletteWidgets(root);
    initGaussSchritteWidgets(root);

    if (!window.Plotly) return;

    initPunktwolkeRegressionWidgets(root);

    /* ---- Baumdiagramme ---- */
    const divs = root.querySelectorAll(".baumdiagramm-auto");
    divs.forEach((div) => {
        const opts = {
            pa: parseFloat(div.dataset.pa),
            pba: parseFloat(div.dataset.pba),
            pbna: parseFloat(div.dataset.pbna),
            titel: div.dataset.titel || "",
            labelA: div.dataset.labelA || "A",
            labelAbar: div.dataset.labelAbar || "A\u0305",
            labelB: div.dataset.labelB || "B",
            labelBbar: div.dataset.labelBbar || "B\u0305",
            mode: div.dataset.mode || "numeric",
            givenSlots: parseSlots(div.dataset.givenSlots),
        };

        const figure = buildBaumdiagrammFigure(opts);
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Graphen (symbolische Funktionen) ---- */
    root.querySelectorAll(".graph-auto").forEach((div) => {
        if (!window.math) return;
        let funktionen;
        try { funktionen = JSON.parse(div.dataset.funktionen); } catch { return; }
        const punkte = div.dataset.punkte ? JSON.parse(div.dataset.punkte) : null;
        const flaechen = div.dataset.flaechen ? JSON.parse(div.dataset.flaechen) : null;

        const figure = buildGraphFigure({
            funktionen,
            punkte,
            flaechen,
            titel: div.dataset.titel || "",
            xAchse: div.dataset.xachse || "",
            yAchse: div.dataset.yachse || "",
            xMin: div.dataset.xmin !== "" ? Number(div.dataset.xmin) : -5,
            xMax: div.dataset.xmax !== "" ? Number(div.dataset.xmax) : 20,
            yMin: div.dataset.ymin !== "" ? Number(div.dataset.ymin) : null,
            yMax: div.dataset.ymax !== "" ? Number(div.dataset.ymax) : null,
        });

        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Histogramme (allgemein, frei definierte x/y) ---- */
    root.querySelectorAll(".histogramm-allgemein-auto").forEach((div) => {
        let x, y;
        try { x = JSON.parse(div.dataset.x); y = JSON.parse(div.dataset.y); } catch { return; }
        const titel = div.dataset.titel || "";
        const balkenbreite = div.dataset.balkenbreite !== "" ? Number(div.dataset.balkenbreite) : null;

        const figure = buildHistogrammAllgemeinFigure({ x, y, titel, balkenbreite });
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Histogramme (Einzelwahrscheinlichkeiten) ---- */
    root.querySelectorAll(".histogramm-einzel-auto").forEach((div) => {
        const n = parseNum(div.dataset.n);
        const p = parseNum(div.dataset.p);
        if (n == null || p == null) return;
        const a = parseNum(div.dataset.a);
        const b = parseNum(div.dataset.b);
        const titel = div.dataset.titel || "";

        const figure = buildHistogrammEinzelnFigure({ n, p, a, b, titel });
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Histogramme (Kumuliert) ---- */
    root.querySelectorAll(".histogramm-kumuliert-auto").forEach((div) => {
        const n = parseNum(div.dataset.n);
        const p = parseNum(div.dataset.p);
        if (n == null || p == null) return;
        const a = parseNum(div.dataset.a);
        const b = parseNum(div.dataset.b);
        const titel = div.dataset.titel || "";

        const figure = buildHistogrammKumuliertFigure({ n, p, a, b, titel });
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Verflechtungsdiagramme ---- */
    root.querySelectorAll(".verflechtungsdiagramm-auto").forEach((div) => {
        let rohstoffe, zwischenprodukte, endprodukte, stufe1, stufe2;
        try {
            rohstoffe = JSON.parse(div.dataset.rohstoffe);
            zwischenprodukte = JSON.parse(div.dataset.zwischenprodukte);
            endprodukte = JSON.parse(div.dataset.endprodukte);
            stufe1 = JSON.parse(div.dataset.stufe1);
            stufe2 = JSON.parse(div.dataset.stufe2);
        } catch { return; }

        const figure = buildVerflechtungsdiagrammFigure({
            rohstoffe, zwischenprodukte, endprodukte, stufe1, stufe2,
        });
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Interaktive Histogramm-Widgets ---- */
    root.querySelectorAll(".hb-widget").forEach((row) => {
        const nSlider = row.querySelector(".hb-nSlider");
        if (!nSlider) return;
        const pSlider = row.querySelector(".hb-pSlider");
        const aSlider = row.querySelector(".hb-aSlider");
        const bSlider = row.querySelector(".hb-bSlider");
        const nWert = row.querySelector(".hb-nWert");
        const pWert = row.querySelector(".hb-pWert");
        const aWert = row.querySelector(".hb-aWert");
        const bWert = row.querySelector(".hb-bWert");
        const autoYBox = row.querySelector(".hb-autoY");
        const intervallEl = row.querySelector(".hb-intervallWert");
        const plotEinzeln = row.querySelector(".hb-plotEinzeln");
        const plotKumuliert = row.querySelector(".hb-plotKumuliert");

        function updateSliderRanges() {
            const n = parseInt(nSlider.value);
            aSlider.max = n;
            bSlider.max = n;
            if (parseInt(aSlider.value) > n) aSlider.value = n;
            if (parseInt(bSlider.value) > n) bSlider.value = n;
        }

        function update() {
            const n = parseInt(nSlider.value);
            const p = parseFloat(pSlider.value);
            const a = parseInt(aSlider.value);
            const b = parseInt(bSlider.value);
            const autoY = autoYBox.checked;

            nWert.textContent = n;
            pWert.textContent = p.toFixed(2).replace(".", ",");
            aWert.textContent = a;
            bWert.textContent = b;

            const figE = buildHistogrammEinzelnFigure({
                n, p, a, b, titel: "Einzelwahrscheinlichkeiten", autoY,
            });

            if (intervallEl) {
                const pIntervall = binomialIntervalProbability(n, p, a, b);
                intervallEl.innerHTML = `$ P(${a} ≤ X ≤ ${b}) = ${pIntervall.toFixed(4)} $`;
                if (window.MathJax?.typesetPromise) MathJax.typesetPromise([intervallEl]);
            }

            plotlyRender(plotEinzeln, figE.data, figE.layout);

            const figK = buildHistogrammKumuliertFigure({
                n, p, a, b, titel: "Kumulierte Wahrscheinlichkeiten",
            });
            plotlyRender(plotKumuliert, figK.data, figK.layout);
        }

        nSlider.addEventListener("input", () => { updateSliderRanges(); update(); });
        pSlider.addEventListener("input", update);
        aSlider.addEventListener("input", update);
        bSlider.addEventListener("input", update);
        autoYBox.addEventListener("change", update);

        updateSliderRanges();
        update();
    });

    /* ---- Lineare Funktionen Explorer ---- */
    root.querySelectorAll(".lf-widget").forEach((row) => {
        const mSlider = row.querySelector(".lf-mSlider");
        if (!mSlider) return;
        if (!window.math) return;
        const bSlider = row.querySelector(".lf-bSlider");
        const mWert = row.querySelector(".lf-mWert");
        const bWert = row.querySelector(".lf-bWert");
        const eqDisplay = row.querySelector(".lf-eqDisplay");
        const plotDiv = row.querySelector(".lf-plotGraph");
        const tableBody = row.querySelector(".lf-tableBody");

        function fmt(n) {
            const r = Math.round(n * 10) / 10;
            return r % 1 === 0 ? String(r) : r.toFixed(1);
        }

        function fmtDe(n) {
            return fmt(n).replace(".", ",");
        }

        function update() {
            const m = parseFloat(mSlider.value);
            const b = parseFloat(bSlider.value);

            mWert.textContent = fmtDe(m);
            bWert.textContent = fmtDe(b);

            // Equation (LaTeX)
            const bAbs = Math.abs(b);
            const sign = b >= 0 ? "+" : "-";
            eqDisplay.innerHTML = "$ f(x) = " + fmtDe(m) + " \\cdot x " + sign + " " + fmtDe(bAbs) + " $";
            if (window.MathJax?.typesetPromise) MathJax.typesetPromise([eqDisplay]);

            // Graph via buildGraphFigure (matches the legacy graph preview rendering)
            const xMin = -6, xMax = 6, yMin = -8, yMax = 8;
            const term = "(" + m + ")*x+(" + b + ")";
            const figure = buildGraphFigure({
                funktionen: [{ name: "f", term: term }],
                punkte: [{ x: 0, y: b, text: "y-Achsenabschnitt (0 | " + fmtDe(b) + ")" }],
                xMin, xMax, yMin, yMax,
            });

            // Fixed axis scaling with integer ticks
            figure.layout.xaxis.dtick = 1;
            figure.layout.yaxis.dtick = 1;

            // Steigungsdreieck (slope triangle) at x = 1
            const x0 = 1, y0 = m * x0 + b, y1 = m * (x0 + 1) + b;
            const dimColor = themeTextColor() + "80";   // 50 % opacity
            figure.layout.shapes = [];
            if (m !== 0 && y0 >= yMin && y0 <= yMax && y1 >= yMin && y1 <= yMax) {
                // horizontal leg: (x0, y0) → (x0+1, y0)
                figure.layout.shapes.push({
                    type: "line", x0: x0, y0: y0, x1: x0 + 1, y1: y0,
                    line: { color: dimColor, width: 1.5, dash: "dot" },
                });
                // vertical leg: (x0+1, y0) → (x0+1, y1)
                figure.layout.shapes.push({
                    type: "line", x0: x0 + 1, y0: y0, x1: x0 + 1, y1: y1,
                    line: { color: dimColor, width: 1.5, dash: "dot" },
                });
                // annotations: "1" on horizontal, "m" on vertical
                figure.layout.annotations = [
                    {
                        x: x0 + 0.5, y: y0, yshift: m > 0 ? -14 : 14,
                        text: "1", showarrow: false,
                        font: { size: 12, color: dimColor },
                    },
                    {
                        x: x0 + 1, xshift: 14, y: (y0 + y1) / 2,
                        text: fmtDe(m), showarrow: false,
                        font: { size: 12, color: dimColor },
                    },
                ];
            } else {
                figure.layout.annotations = [];
            }

            plotlyRender(plotDiv, figure.data, figure.layout);

            // Value table
            const xs = [-3, -2, -1, 0, 1, 2, 3];
            let html = "";
            for (const x of xs) {
                const y = m * x + b;
                if (x === 0) {
                    html += "<tr><td><strong>" + fmtDe(x) + "</strong></td><td><strong>" + fmtDe(y) + "</strong></td></tr>";
                } else {
                    html += "<tr><td>" + fmtDe(x) + "</td><td>" + fmtDe(y) + "</td></tr>";
                }
            }
            tableBody.innerHTML = html;
        }

        mSlider.addEventListener("input", update);
        bSlider.addEventListener("input", update);
        update();
    });

    /* ---- Baumdiagramme und Vierfeldertafeln (interaktiv) ---- */
    root.querySelectorAll(".bvt-widget").forEach((row) => {
        const paSlider = row.querySelector(".bvt-paSlider");
        if (!paSlider) return;
        const pbaSlider = row.querySelector(".bvt-pbaSlider");
        const pbnaSlider = row.querySelector(".bvt-pbnaSlider");
        const paWert = row.querySelector(".bvt-paWert");
        const pbaWert = row.querySelector(".bvt-pbaWert");
        const pbnaWert = row.querySelector(".bvt-pbnaWert");
        const unabh = row.querySelector(".bvt-unabhaengigkeit");
        const plotBaum = row.querySelector(".bvt-plotBaum");
        const plotInvers = row.querySelector(".bvt-plotInvers");

        // Vierfeldertafel cells
        const c = (cls) => row.querySelector(`.bvt-${cls}`);

        function fmtDe(v, d) { return v.toFixed(d).replace(".", ","); }

        function update() {
            const pa = parseFloat(paSlider.value);
            const pba = parseFloat(pbaSlider.value);
            const pbna = parseFloat(pbnaSlider.value);

            paWert.textContent = fmtDe(pa, 2);
            pbaWert.textContent = fmtDe(pba, 2);
            pbnaWert.textContent = fmtDe(pbna, 2);

            // Baumdiagramm
            const figBaum = buildBaumdiagrammFigure({
                pa, pba, pbna,
                titel: "Baumdiagramm",
                labelA: "A", labelAbar: "A\u0305",
                labelB: "B", labelBbar: "B\u0305",
            });
            plotlyRender(plotBaum, figBaum.data, figBaum.layout);

            // Inverses Baumdiagramm
            const pb = pa * pba + (1 - pa) * pbna;
            const pab = pb > 0 ? (pa * pba) / pb : 0;
            const panb = (1 - pb) > 0 ? (pa * (1 - pba)) / (1 - pb) : 0;
            const figInvers = buildBaumdiagrammFigure({
                pa: pb, pba: pab, pbna: panb,
                titel: "Inverses Baumdiagramm",
                labelA: "B", labelAbar: "B\u0305",
                labelB: "A", labelBbar: "A\u0305",
            });
            plotlyRender(plotInvers, figInvers.data, figInvers.layout);

            // Vierfeldertafel
            const a_b = pa * pba;
            const a_nb = pa * (1 - pba);
            const na_b = (1 - pa) * pbna;
            const na_nb = (1 - pa) * (1 - pbna);

            c("ab").textContent = fmtDe(a_b, 4);
            c("anb").textContent = fmtDe(a_nb, 4);
            c("nab").textContent = fmtDe(na_b, 4);
            c("nanb").textContent = fmtDe(na_nb, 4);
            c("asum").textContent = fmtDe(a_b + a_nb, 2);
            c("nasum").textContent = fmtDe(na_b + na_nb, 2);
            c("sumb").textContent = fmtDe(a_b + na_b, 2);
            c("sumnb").textContent = fmtDe(a_nb + na_nb, 2);
            c("sumsum").textContent = "1";

            // Unabhängigkeit
            unabh.textContent = Math.abs(pba - pbna) < 1e-6 ? "unabhängig." : "abhängig.";
        }

        paSlider.addEventListener("input", update);
        pbaSlider.addEventListener("input", update);
        pbnaSlider.addEventListener("input", update);
        update();
    });

    /* ---- h-Methode der Ableitung ---- */
    root.querySelectorAll(".qhm-widget").forEach((row) => {
        const x0Slider = row.querySelector(".qhm-x0Slider");
        if (!x0Slider) return;
        const hSlider = row.querySelector(".qhm-hSlider");
        const x0Wert = row.querySelector(".qhm-x0Wert");
        const hWert = row.querySelector(".qhm-hWert");
        const punktDisplay = row.querySelector(".qhm-punktDisplay");
        const formulaDisplay = row.querySelector(".qhm-formulaDisplay");
        const info = row.querySelector(".qhm-info");
        const plotDiv = row.querySelector(".qhm-plotGraph");
        const controls = row.querySelector(".widget-controls");
        const eps = 1e-9;

        function fmt(n) {
            const r = Math.round(n * 100) / 100;
            return r % 1 === 0 ? String(r) : r.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
        }

        function fmtDe(n) {
            return fmt(n).replace(".", ",");
        }

        function fmtTex(n) {
            return fmtDe(n).replaceAll("-", "-");
        }

        function update() {
            const x0 = parseFloat(x0Slider.value);
            const h = parseFloat(hSlider.value);
            const y0 = x0 * x0;
            const x1 = x0 + h;
            const y1 = x1 * x1;
            const tangentSteigung = 2 * x0;

            x0Wert.textContent = fmtDe(x0);
            hWert.textContent = fmtDe(h);

            punktDisplay.innerHTML = Math.abs(h) > eps
                ? `$P(${fmtTex(x0)}\\mid ${fmtTex(y0)}), \\quad Q(${fmtTex(x1)}\\mid ${fmtTex(y1)})$`
                : `$P(${fmtTex(x0)}\\mid ${fmtTex(y0)})$`;

            if (Math.abs(h) > eps) {
                const sekantenSteigung = 2 * x0 + h;
                const sign = h >= 0 ? "+" : "-";
                formulaDisplay.innerHTML = `$$\\begin{aligned}
m_h & = \\frac{f(x_0+h)-f(x_0)}{h} = \\frac{(x_0+h)^2-x_0^2}{h} = 2x_0+h \\\\
m_h & = 2\\cdot ${fmtTex(x0)} ${sign} ${fmtTex(Math.abs(h))} = ${fmtTex(sekantenSteigung)} \\\\
f'(x_0) & = \\lim_{h \\to 0} m_h = 2x_0 = ${fmtTex(tangentSteigung)}
\\end{aligned}$$`;
                info.innerHTML = "Je näher $h$ an $0$ liegt, desto näher rückt die Sekante an die Tangente.";
            } else {
                formulaDisplay.innerHTML = `$$\\begin{aligned}
m_h & = \\frac{f(x_0+h)-f(x_0)}{h} = \\frac{(x_0+h)^2-x_0^2}{h} = 2x_0+h \\\\
m_h & \\text{ ist für } h=0 \\text{ nicht definiert} \\\\
f'(x_0) & = \\lim_{h \\to 0} m_h = 2x_0 = ${fmtTex(tangentSteigung)}
\\end{aligned}$$`;
                info.innerHTML = "Für die Ableitung braucht man nicht $h=0$, sondern den Grenzwert für $h \\to 0$.";
            }

            if (window.MathJax?.typesetPromise) {
                window.MathJax.typesetPromise([controls]);
            }

            const figure = buildHMethodeAbleitungFigure({ x0, h });
            plotlyRender(plotDiv, figure.data, figure.layout);
        }

        x0Slider.addEventListener("input", update);
        hSlider.addEventListener("input", update);
        update();
    });

    /* ---- Baumdiagramm Binomial / Bernoulli-Formel (interaktiv) ---- */
    root.querySelectorAll(".bb-widget").forEach((row) => {
        const nSlider = row.querySelector(".bb-nSlider");
        if (!nSlider) return;
        const pSlider = row.querySelector(".bb-pSlider");
        const kSlider = row.querySelector(".bb-kSlider");
        const nWert = row.querySelector(".bb-nWert");
        const pWert = row.querySelector(".bb-pWert");
        const kWert = row.querySelector(".bb-kWert");
        const anzahlPfade = row.querySelector(".bb-anzahlPfade");
        const pfadwkeit = row.querySelector(".bb-pfadwkeit");
        const bernoulli = row.querySelector(".bb-bernoulli");
        const plotBaum = row.querySelector(".bb-plotBaum");

        function binom(n, k) {
            if (k < 0 || k > n) return 0;
            let res = 1;
            for (let i = 1; i <= k; i++) res = (res * (n - i + 1)) / i;
            return res;
        }

        function update() {
            const n = parseInt(nSlider.value, 10);
            const p = parseFloat(pSlider.value);
            kSlider.max = n;
            let k = parseInt(kSlider.value, 10);
            if (k > n) { k = n; kSlider.value = n; }

            nWert.textContent = n;
            pWert.textContent = p;
            kWert.textContent = k;

            const anz = binom(n, k);
            const pw = Math.pow(p, k) * Math.pow(1 - p, n - k);
            const bern = anz * pw;

            anzahlPfade.textContent = `$ \\binom{n}{k}=  ${anz} $`;
            pfadwkeit.textContent = `$ p^${k} \\cdot (1-p)^${n - k} =  ${pw.toLocaleString(undefined, { maximumFractionDigits: 4 })}$`;
            bernoulli.textContent = `\\begin{align*} P(X=k) &= \\binom{n}{k} \\cdot p^k \\cdot (1-p)^{n-k} \\\\ &=${anz}\\cdot ${pw.toLocaleString(undefined, { maximumFractionDigits: 4 })} \\\\ &=  ${bern.toLocaleString(undefined, { maximumFractionDigits: 4 })}\\end{align*}`;

            if (window.MathJax?.typesetPromise) {
                MathJax.typesetPromise([anzahlPfade, pfadwkeit, bernoulli]);
            }

            const figure = buildBaumdiagrammBinomialFigure({ n, p, k });
            plotlyRender(plotBaum, figure.data, figure.layout);
        }

        nSlider.addEventListener("input", update);
        pSlider.addEventListener("input", update);
        kSlider.addEventListener("input", update);
        update();
    });

    /* ---- Quadratische Funktionen (Normalform) ---- */
    root.querySelectorAll(".qf-widget").forEach((row) => {
        const aSlider = row.querySelector(".qf-aSlider");
        if (!aSlider) return;
        const bSlider = row.querySelector(".qf-bSlider");
        const cSlider = row.querySelector(".qf-cSlider");
        const aWert = row.querySelector(".qf-aWert");
        const bWert = row.querySelector(".qf-bWert");
        const cWert = row.querySelector(".qf-cWert");
        const eqDisplay = row.querySelector(".qf-eqDisplay");
        const plotDiv = row.querySelector(".qf-plotGraph");
        const tableBody = row.querySelector(".qf-tableBody");

        function fmt(n) {
            const r = Math.round(n * 100) / 100;
            return r % 1 === 0 ? String(r) : r.toFixed(2).replace(/0+$/, "");
        }
        function fmtDe(n) { return fmt(n).replace(".", ","); }

        function buildEquation(a, b, c) {
            let parts = [];
            // a·x²
            if (a === 1) parts.push("x^2");
            else if (a === -1) parts.push("-x^2");
            else parts.push(fmtDe(a) + "x^2");
            // b·x
            if (b !== 0) {
                const sign = b > 0 ? "+" : "-";
                const bAbs = Math.abs(b);
                parts.push(sign + " " + (bAbs === 1 ? "x" : fmtDe(bAbs) + "x"));
            }
            // c
            if (c !== 0) {
                const sign = c > 0 ? "+" : "-";
                parts.push(sign + " " + fmtDe(Math.abs(c)));
            }
            return "$ f(x) = " + parts.join(" ") + " $";
        }

        function update() {
            const a = parseFloat(aSlider.value);
            const b = parseFloat(bSlider.value);
            const c = parseFloat(cSlider.value);

            aWert.textContent = fmtDe(a);
            bWert.textContent = fmtDe(b);
            cWert.textContent = fmtDe(c);

            eqDisplay.innerHTML = buildEquation(a, b, c);
            if (window.MathJax?.typesetPromise) MathJax.typesetPromise([eqDisplay]);

            // Graph
            const figure = buildQuadratischeFunktionenFigure({ a, b, c });
            plotlyRender(plotDiv, figure.data, figure.layout);

            // Wertetabelle
            const xs = [-3, -2, -1, 0, 1, 2, 3];
            let html = "";
            for (const x of xs) {
                const y = a * x * x + b * x + c;
                html += "<tr><td>" + fmtDe(x) + "</td><td>" + fmtDe(y) + "</td></tr>";
            }
            tableBody.innerHTML = html;
        }

        aSlider.addEventListener("input", update);
        bSlider.addEventListener("input", update);
        cSlider.addEventListener("input", update);
        update();
    });

    /* ---- Quadratische Funktionen Parameter (Scheitelpunktform) ---- */
    root.querySelectorAll(".qfp-widget").forEach((row) => {
        const aSlider = row.querySelector(".qfp-aSlider");
        if (!aSlider) return;
        const dSlider = row.querySelector(".qfp-dSlider");
        const eSlider = row.querySelector(".qfp-eSlider");
        const aWert = row.querySelector(".qfp-aWert");
        const dWert = row.querySelector(".qfp-dWert");
        const eWert = row.querySelector(".qfp-eWert");
        const eqDisplay = row.querySelector(".qfp-eqDisplay");
        const scheitelX = row.querySelector(".qfp-scheitelX");
        const scheitelY = row.querySelector(".qfp-scheitelY");
        const plotDiv = row.querySelector(".qfp-plotGraph");

        function fmt(n) {
            const r = Math.round(n * 100) / 100;
            return r % 1 === 0 ? String(r) : r.toFixed(2).replace(/0+$/, "");
        }
        function fmtDe(n) { return fmt(n).replace(".", ","); }

        function buildEquation(a, d, e) {
            let term = "";
            // a-Faktor
            if (a === 1) term = "";
            else if (a === -1) term = "-";
            else term = fmtDe(a);
            // (x - d)²
            if (d === 0) term += "(x)^2";
            else if (d > 0) term += "(x - " + fmtDe(d) + ")^2";
            else term += "(x + " + fmtDe(Math.abs(d)) + ")^2";
            // + e
            if (e !== 0) {
                const sign = e > 0 ? "+" : "-";
                term += " " + sign + " " + fmtDe(Math.abs(e));
            }
            return "$ f(x) = " + term + " $";
        }

        function update() {
            const a = parseFloat(aSlider.value);
            const d = parseFloat(dSlider.value);
            const e = parseFloat(eSlider.value);

            aWert.textContent = fmtDe(a);
            dWert.textContent = fmtDe(d);
            eWert.textContent = fmtDe(e);

            eqDisplay.innerHTML = buildEquation(a, d, e);
            scheitelX.textContent = fmtDe(d);
            scheitelY.textContent = fmtDe(e);
            if (window.MathJax?.typesetPromise) MathJax.typesetPromise([eqDisplay, eqDisplay.closest(".widget-controls")]);

            // Graph
            const figure = buildQuadratischeParameterFigure({ a, d, e });
            plotlyRender(plotDiv, figure.data, figure.layout);
        }

        aSlider.addEventListener("input", update);
        dSlider.addEventListener("input", update);
        eSlider.addEventListener("input", update);
        update();
    });
}
