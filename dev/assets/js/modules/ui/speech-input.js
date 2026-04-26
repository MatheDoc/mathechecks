/**
 * Speech-Input – Adds a microphone button to text inputs for voice entry.
 *
 * Usage:
 *   import { enhanceSpeechInputs } from "./ui/speech-input.js";
 *   enhanceSpeechInputs(rootNode);               // all text inputs inside rootNode
 *   enhanceSpeechInputs(rootNode, ".my-input");   // only matching inputs
 *
 * Inputs inside an existing wrapper (.answer-field-group) get the mic button
 * appended to that group. Standalone inputs are wrapped in .speech-input-wrap.
 */

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const SUPPORTED = Boolean(SpeechRecognition);

const ENHANCED_ATTR = "data-speech-enhanced";

let activeRecognition = null;
let activeBtn = null;

/* ── German speech → numeric string normalization (Chrome workaround) ── */
const DIRECT_NUMBER_WORDS = new Map([
    ["null", "0"], ["eins", "1"], ["zwei", "2"], ["drei", "3"],
    ["vier", "4"], ["fünf", "5"], ["sechs", "6"], ["sieben", "7"],
    ["acht", "8"], ["neun", "9"], ["zehn", "10"], ["elf", "11"],
    ["zwölf", "12"], ["dreizehn", "13"], ["vierzehn", "14"],
    ["fünfzehn", "15"], ["sechzehn", "16"], ["siebzehn", "17"],
    ["achtzehn", "18"], ["neunzehn", "19"], ["zwanzig", "20"],
    ["dreißig", "30"], ["vierzig", "40"], ["fünfzig", "50"],
    ["sechzig", "60"], ["siebzig", "70"], ["achtzig", "80"],
    ["neunzig", "90"], ["hundert", "100"], ["tausend", "1000"],
    ["million", "1000000"], ["millionen", "1000000"],
    ["minus", "-"], ["komma", ","],
]);

const DIGIT_WORDS = new Map([
    ["null", "0"], ["eins", "1"], ["ein", "1"], ["zwei", "2"], ["drei", "3"],
    ["vier", "4"], ["fünf", "5"], ["sechs", "6"], ["sieben", "7"],
    ["acht", "8"], ["neun", "9"],
]);

const CARDINAL_WORDS = new Map([
    ["null", 0], ["eins", 1], ["ein", 1], ["zwei", 2], ["drei", 3],
    ["vier", 4], ["fünf", 5], ["sechs", 6], ["sieben", 7], ["acht", 8],
    ["neun", 9], ["zehn", 10], ["elf", 11], ["zwölf", 12], ["dreizehn", 13],
    ["vierzehn", 14], ["fünfzehn", 15], ["sechzehn", 16], ["siebzehn", 17],
    ["achtzehn", 18], ["neunzehn", 19], ["zwanzig", 20], ["dreißig", 30],
    ["vierzig", 40], ["fünfzig", 50], ["sechzig", 60], ["siebzig", 70],
    ["achtzig", 80], ["neunzig", 90],
]);

const TENS_PATTERN = /^(.*)und(zwanzig|dreißig|vierzig|fünfzig|sechzig|siebzig|achtzig|neunzig)$/;

function normalizeNumberToken(word) {
    return String(word || "")
        .toLowerCase()
        .replace(/dreissig/g, "dreißig")
        .replace(/fuenf/g, "fünf")
        .replace(/funf/g, "fünf")
        .replace(/zwo/g, "zwei")
        .replace(/^eine[rmns]?$/, "ein")
        .replace(/^eins$/, "eins")
        .replace(/sechszehn/g, "sechzehn")
        .replace(/siebenzehn/g, "siebzehn");
}

function parseGermanCardinalWord(word) {
    const normalized = normalizeNumberToken(word);
    if (!normalized) return null;

    if (/^\d+$/.test(normalized)) {
        return Number(normalized);
    }

    if (CARDINAL_WORDS.has(normalized)) {
        return CARDINAL_WORDS.get(normalized);
    }

    const millionMatch = normalized.match(/^(.*?)(million(?:en)?)(.*)$/);
    if (millionMatch) {
        const left = millionMatch[1] || "ein";
        const right = millionMatch[3];
        const leftValue = parseGermanCardinalWord(left);
        const rightValue = right ? parseGermanCardinalWord(right) : 0;
        if (leftValue !== null && rightValue !== null) {
            return leftValue * 1000000 + rightValue;
        }
    }

    const thousandIndex = normalized.indexOf("tausend");
    if (thousandIndex !== -1) {
        const left = normalized.slice(0, thousandIndex) || "ein";
        const right = normalized.slice(thousandIndex + "tausend".length);
        const leftValue = parseGermanCardinalWord(left);
        const rightValue = right ? parseGermanCardinalWord(right) : 0;
        if (leftValue !== null && rightValue !== null) {
            return leftValue * 1000 + rightValue;
        }
    }

    const hundredIndex = normalized.indexOf("hundert");
    if (hundredIndex !== -1) {
        const left = normalized.slice(0, hundredIndex) || "ein";
        const right = normalized.slice(hundredIndex + "hundert".length);
        const leftValue = parseGermanCardinalWord(left);
        const rightValue = right ? parseGermanCardinalWord(right) : 0;
        if (leftValue !== null && rightValue !== null) {
            return leftValue * 100 + rightValue;
        }
    }

    const tensMatch = normalized.match(TENS_PATTERN);
    if (tensMatch) {
        const onesValue = parseGermanCardinalWord(tensMatch[1]);
        const tensValue = CARDINAL_WORDS.get(tensMatch[2]);
        if (onesValue !== null && onesValue < 10 && tensValue !== undefined) {
            return tensValue + onesValue;
        }
    }

    return null;
}

function parseDigitSequence(words) {
    if (!words.length) return null;

    let digits = "";
    for (const rawWord of words) {
        const word = normalizeNumberToken(rawWord);
        if (!word) return null;

        if (/^\d+$/.test(word)) {
            digits += word;
            continue;
        }

        const digit = DIGIT_WORDS.get(word);
        if (digit === undefined) {
            return null;
        }
        digits += digit;
    }

    return digits || null;
}

function parseGermanIntegerWords(words) {
    if (!words.length) return null;

    const digitSequence = parseDigitSequence(words);
    if (digitSequence !== null) {
        return digitSequence;
    }

    const joined = words.map(normalizeNumberToken).join("");
    const parsed = parseGermanCardinalWord(joined);
    return parsed !== null ? String(parsed) : null;
}

function parseGermanFractionWords(words) {
    if (!words.length) return null;

    const digitSequence = parseDigitSequence(words);
    if (digitSequence !== null) {
        return digitSequence;
    }

    const joined = words.map(normalizeNumberToken).join("");
    const parsed = parseGermanCardinalWord(joined);
    return parsed !== null ? String(parsed) : null;
}

function parseGermanNumberPhrase(text) {
    const cleaned = String(text || "")
        .trim()
        .replace(/\.+$/, "")
        .replace(/[–—−]/g, "-")
        .replace(/\s+/g, " ");

    if (!cleaned) return null;

    const compactNumeric = cleaned.replace(/\s*,\s*/g, ",").replace(/\s+/g, "");
    if (/^-?\d+(?:,\d+)?$/.test(compactNumeric)) {
        return compactNumeric;
    }

    let sign = "";
    let rest = cleaned;
    if (rest.startsWith("-")) {
        sign = "-";
        rest = rest.slice(1).trim();
    }

    const tokens = rest
        .replace(/,/g, " komma ")
        .split(/\s+/)
        .map(normalizeNumberToken)
        .filter(Boolean);

    if (!tokens.length) return null;

    if (tokens[0] === "minus") {
        sign = "-";
        tokens.shift();
    }

    if (!tokens.length) return null;

    const commaIndex = tokens.indexOf("komma");
    if (commaIndex === -1) {
        const integerPart = parseGermanIntegerWords(tokens);
        return integerPart !== null ? `${sign}${integerPart}` : null;
    }

    const integerTokens = tokens.slice(0, commaIndex);
    const fractionTokens = tokens.slice(commaIndex + 1);
    const integerPart = integerTokens.length ? parseGermanIntegerWords(integerTokens) : "0";
    const fractionPart = parseGermanFractionWords(fractionTokens);

    if (integerPart === null || fractionPart === null) {
        return null;
    }

    return `${sign}${integerPart},${fractionPart}`;
}

function replaceNumberWords(text) {
    return text.replace(/\b[a-zäöüß]+\b/gi, (word) => {
        const digit = DIRECT_NUMBER_WORDS.get(normalizeNumberToken(word));
        return digit !== undefined ? digit : word;
    });
}

function normalizeSpeechTranscript(text) {
    const cleaned = String(text || "").trim().replace(/\.+$/, "");
    if (!cleaned) return "";

    const numericText = parseGermanNumberPhrase(cleaned);
    if (numericText !== null) {
        return numericText;
    }

    const replaced = replaceNumberWords(cleaned);
    const compact = replaced.trim();
    if (/^[\d\s,-]+$/.test(compact)) {
        return compact.replace(/\s*,\s*/g, ",").replace(/\s+/g, "");
    }
    return compact.replace(/\s*,\s*/g, ",");
}

function stopActiveRecognition() {
    if (activeRecognition) {
        try { activeRecognition.stop(); } catch { /* ignore */ }
        activeRecognition = null;
    }
    if (activeBtn) {
        activeBtn.classList.remove("speech-mic--active");
        activeBtn = null;
    }
}

function createMicButton() {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "speech-mic";
    btn.title = "Spracheingabe";
    btn.setAttribute("aria-label", "Spracheingabe starten");
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2" width="6" height="11" rx="3"/><path d="M5 10a7 7 0 0 0 14 0"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="8" y1="22" x2="16" y2="22"/></svg>`;
    return btn;
}

function bindMic(btn, input) {
    btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();

        if (activeBtn === btn) {
            stopActiveRecognition();
            return;
        }

        stopActiveRecognition();

        const recognition = new SpeechRecognition();
        recognition.lang = "de-DE";
        recognition.continuous = true;
        recognition.interimResults = false;

        recognition.onstart = () => {
            activeRecognition = recognition;
            activeBtn = btn;
            btn.classList.add("speech-mic--active");
        };

        recognition.onend = () => {
            btn.classList.remove("speech-mic--active");
            if (activeBtn === btn) {
                activeRecognition = null;
                activeBtn = null;
            }
        };

        recognition.onerror = () => {
            btn.classList.remove("speech-mic--active");
            if (activeBtn === btn) {
                activeRecognition = null;
                activeBtn = null;
            }
        };

        recognition.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    transcript += event.results[i][0].transcript;
                }
            }
            if (!transcript) return;

            const cleaned = normalizeSpeechTranscript(transcript);

            const current = input.value;
            if (current && !current.endsWith(" ")) {
                input.value = current + " " + cleaned;
            } else {
                input.value = current + cleaned;
            }

            input.dispatchEvent(new Event("input", { bubbles: true }));
        };

        try {
            recognition.start();
        } catch {
            // Permission denied or no user gesture.
        }
    });
}

/**
 * Enhance text inputs inside `root` with a speech-input mic button.
 *
 * @param {HTMLElement} root       Container to scan for inputs.
 * @param {string}      [selector] CSS selector for target inputs.
 */
export function enhanceSpeechInputs(root, selector) {
    if (!SUPPORTED || !root) return;

    const sel = selector || 'input[type="text"], input:not([type])';
    const inputs = Array.from(root.querySelectorAll(sel));

    inputs.forEach((input) => {
        if (input.hasAttribute(ENHANCED_ATTR)) return;
        if (input.type === "checkbox" || input.type === "radio" || input.type === "hidden") return;

        input.setAttribute(ENHANCED_ATTR, "");

        const btn = createMicButton();
        bindMic(btn, input);

        // Wrap the input + mic in a relative container so the mic sits inside.
        // Works both standalone and inside .answer-field-group (training tasks),
        // where the check button stays outside as a sibling.
        const wrapper = document.createElement("span");
        wrapper.className = "speech-input-wrap";
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        wrapper.appendChild(btn);
    });
}

/** Whether the browser supports speech recognition. */
export const speechInputSupported = SUPPORTED;
