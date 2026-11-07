// Spracheingabe für den Main-Input des Rechners.
// Übersetzt gesprochene Mathematik wörtlich in Rechner-Syntax (keine automatischen Klammern),
// Ausnahme: Funktion + einzelnes Argument ("Sinus von 30" -> sin(30)).
import {
    attachSpeechInput,
    parseGermanCardinalWord,
    parseGermanNumberPhrase,
    stopActiveSpeechInput,
} from "../modules/ui/speech-input.js?v=20261108-speech-preview";

// Abschließendes Signalwort führt die Eingabe aus (wie EXE).
// "exe" wird von der Erkennung uneinheitlich geschrieben; Varianten nach Tests ergänzen.
const EXECUTE_SUFFIX = /(?:^|\s)(?:check|checken|scheck|tscheck|ausrechnen|exe|ixe|xe|e x e|e-x-e)$/;

const STANDALONE_COMMANDS = new Map([
    ["löschen", "clear"],
    ["alles löschen", "clear"],
    ["zurück", "backspace"],
]);

// Mehrwortphrasen zuerst; ersetzt nur ganze Wörter.
const PHRASES = [
    ["klammer auf", "("],
    ["klammer öffnen", "("],
    ["klammer zu", ")"],
    ["klammer schließen", ")"],
    ["logarithmus naturalis", "ln"],
    ["natürlicher logarithmus", "ln"],
    ["geteilt durch", "/"],
    ["dividiert durch", "/"],
    ["multipliziert mit", "*"],
    ["zum quadrat", "^ 2"],
    ["ist gleich", "="],
    ["durch", "/"],
    ["geteilt", "/"],
    ["mal", "*"],
    ["plus", "+"],
    ["minus", "-"],
    ["hoch", "^"],
    ["quadrat", "^ 2"],
    ["gleich", "="],
    ["fakultät", "!"],
    ["pi", "π"],
    ["iks", "x"],
    ["ix", "x"],
];

const FUNCTION_WORDS = new Map([
    ["quadratwurzel", "sqrt"],
    ["wurzel", "sqrt"],
    ["sinus", "sin"],
    ["kosinus", "cos"],
    ["cosinus", "cos"],
    ["tangens", "tan"],
    ["arkussinus", "asin"],
    ["arcussinus", "asin"],
    ["arkuskosinus", "acos"],
    ["arcuscosinus", "acos"],
    ["arkustangens", "atan"],
    ["arcustangens", "atan"],
    ["logarithmus", "log"],
    ["betrag", "abs"],
    ...["sin", "cos", "tan", "asin", "acos", "atan", "ln", "log", "sqrt", "abs"].map((name) => [name, name]),
]);

const FUNCTION_FILLERS = new Set(["von", "vom", "aus"]);
const OPERATORS = new Set(["+", "-", "*", "/", "^", "=", "!"]);

function escapeRegExp(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const PHRASE_PATTERNS = PHRASES.map(([phrase, replacement]) => [
    new RegExp(`(^|\\s)${escapeRegExp(phrase)}(?=\\s|$)`, "g"),
    ` ${replacement} `,
]);

function isNumberToken(token) {
    return /^\d+(?:,\d+)?$/.test(token) || token === "komma" || parseGermanCardinalWord(token) !== null;
}

function numberFromTokens(tokens) {
    const parsed = parseGermanNumberPhrase(tokens.join(" "));
    if (parsed !== null) return parsed;
    return tokens
        .map((token) => {
            if (token === "komma") return ",";
            if (/^\d/.test(token)) return token;
            return String(parseGermanCardinalWord(token));
        })
        .join("");
}

function tokenize(text) {
    let source = String(text || "")
        .trim()
        .replace(/[.!?]+$/, "")
        .replace(/[×·✕]/g, "*")
        .replace(/[÷:]/g, "/")
        .replace(/[−–—]/g, "-")
        .replace(/²/g, "^2")
        .replace(/³/g, "^3")
        // Die Erkennung schreibt "drei mal vier" teils als "3 x 4".
        .replace(/(\d)\s+[xX]\s+(?=\d)/g, "$1 * ")
        .toLowerCase()
        .replace(/([()+\-*/^=!])/g, " $1 ");

    PHRASE_PATTERNS.forEach(([pattern, replacement]) => {
        source = source.replace(pattern, (match, lead) => `${lead}${replacement}`);
    });

    const rawTokens = source.split(/\s+/).filter(Boolean);
    const tokens = [];
    let numberBuffer = [];

    const flushNumber = () => {
        if (!numberBuffer.length) return;
        tokens.push({ type: "num", value: numberFromTokens(numberBuffer) });
        numberBuffer = [];
    };

    rawTokens.forEach((token) => {
        if (isNumberToken(token)) {
            numberBuffer.push(token);
            return;
        }
        flushNumber();
        if (token === "(") tokens.push({ type: "lparen", value: "(" });
        else if (token === ")") tokens.push({ type: "rparen", value: ")" });
        else if (OPERATORS.has(token)) tokens.push({ type: "op", value: token });
        else if (FUNCTION_WORDS.has(token)) tokens.push({ type: "fn", value: FUNCTION_WORDS.get(token) });
        else if (FUNCTION_FILLERS.has(token)) tokens.push({ type: "filler", value: "" });
        else tokens.push({ type: "word", value: token });
    });
    flushNumber();
    return tokens;
}

function isAtom(token) {
    return token?.type === "num" || token?.type === "word";
}

/**
 * Übersetzt einen gesprochenen Term in Rechner-Syntax, z. B.
 * "drei mal x hoch zwei plus Wurzel aus sechzehn" -> "3*x^2+sqrt(16)".
 */
export function speechToExpression(text) {
    const tokens = tokenize(text);
    let output = "";
    let previous = null;

    const append = (token, value) => {
        const needsSpace = isAtom(previous) && isAtom(token) && !(previous.type === "num" && token.type === "word");
        output += (needsSpace ? " " : "") + value;
        previous = token;
    };

    for (let index = 0; index < tokens.length; index++) {
        const token = tokens[index];
        if (token.type === "filler") continue;

        if (token.type !== "fn") {
            append(token, token.value);
            continue;
        }

        let next = index + 1;
        while (tokens[next]?.type === "filler") next++;

        if (tokens[next]?.type === "lparen" || !tokens[next]) {
            append(token, token.value + (tokens[next] ? "" : "("));
            index = next - 1;
            continue;
        }

        const signed = tokens[next].type === "op" && tokens[next].value === "-" && isAtom(tokens[next + 1]);
        const atom = signed ? tokens[next + 1] : tokens[next];
        if (!isAtom(atom)) {
            append(token, `${token.value}(`);
            index = next - 1;
            continue;
        }

        append({ type: "rparen" }, `${token.value}(${signed ? "-" : ""}${atom.value})`);
        index = signed ? next + 1 : next;
    }

    return output;
}

/** Zerlegt eine Äußerung in Term und Kommando (execute, clear, backspace). */
export function parseCalculatorSpeech(transcript) {
    const normalized = String(transcript || "").trim().replace(/[.!?]+$/, "").toLowerCase();
    if (STANDALONE_COMMANDS.has(normalized)) {
        return { text: "", command: STANDALONE_COMMANDS.get(normalized) };
    }

    const match = normalized.match(EXECUTE_SUFFIX);
    if (!match) {
        return { text: transcript, command: null };
    }
    const text = String(transcript || "").trim().replace(/[.!?]+$/, "").slice(0, match.index);
    return { text, command: "execute" };
}

function processCalculatorTranscript(transcript) {
    const api = window.CalculatorApi;
    if (!api) return { inserted: false };

    const { text, command } = parseCalculatorSpeech(transcript);
    if (command === "clear") {
        api.clear();
        return { inserted: true };
    }
    if (command === "backspace") {
        api.backspace();
        return { inserted: true };
    }

    const expression = speechToExpression(text);
    if (expression) api.insert(expression);

    if (command === "execute") {
        return { inserted: Boolean(expression), stop: true, afterStop: () => api.execute() };
    }
    return { inserted: Boolean(expression) };
}

function formatCalculatorPreview(interim) {
    const { text, command } = parseCalculatorSpeech(interim);
    if (command === "clear") return "löschen";
    if (command === "backspace") return "zurück";
    const expression = speechToExpression(text);
    return command === "execute" ? `${expression} ✓`.trim() : expression;
}

const mainInput = document.getElementById("mainInput");
if (mainInput) {
    attachSpeechInput(mainInput, {
        processTranscript: processCalculatorTranscript,
        formatPreview: formatCalculatorPreview,
    });

    window.addEventListener("calculator:visibility", (event) => {
        if (event.detail?.open) return;
        if (mainInput.parentElement?.querySelector(".speech-mic--active")) {
            stopActiveSpeechInput();
        }
    });
}
