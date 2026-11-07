/**
 * Speech-Input – Adds a microphone button to text inputs for voice entry.
 *
 * Usage:
 *   import { enhanceSpeechInputs } from "./ui/speech-input.js";
 *   enhanceSpeechInputs(rootNode);               // all text inputs inside rootNode
 *   enhanceSpeechInputs(rootNode, ".my-input");   // only matching inputs
 *   attachSpeechInput(input, { processTranscript }); // single input, custom handling
 *
 * Only one recognition runs at a time across all inputs. Import this module
 * everywhere with the same URL (incl. ?v=) so that state stays shared.
 *
 * Inputs inside an existing wrapper (.answer-field-group) get the mic button
 * appended to that group. Standalone inputs are wrapped in .speech-input-wrap.
 */

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const SUPPORTED = Boolean(SpeechRecognition);

const ENHANCED_ATTR = "data-speech-enhanced";
const AUTOGROW_ATTR = "data-speech-autogrow";
const AUTO_STOP_DELAY_MS = 60000;
const MOBILE_RESTART_DELAY_MS = 200;
const TASK_CHECK_REQUEST_EVENT = "task:check-request";

let activeRecognition = null;
let activeBtn = null;
let activeRecognitionTimer = null;

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

function normalizeSpeechCommand(text) {
    return String(text || "")
        .trim()
        .replace(/[.!?]+$/g, "")
        .toLowerCase();
}

function splitSpeechCheckCommand(text) {
    const trimmed = String(text || "").trim();
    if (!trimmed) {
        return { spokenText: "", shouldCheck: false };
    }

    const standaloneCommand = normalizeSpeechCommand(trimmed);
    if (standaloneCommand === "check") {
        return { spokenText: "", shouldCheck: true };
    }

    const trailingCommandMatch = trimmed.match(/^(.*\S)\s+check[.!?]*$/i);
    if (!trailingCommandMatch) {
        return { spokenText: trimmed, shouldCheck: false };
    }

    return {
        spokenText: trailingCommandMatch[1].trim(),
        shouldCheck: true,
    };
}

function isCheckCommand(text) {
    return normalizeSpeechCommand(text) === "check";
}

function clearActiveRecognitionTimer() {
    if (activeRecognitionTimer === null) return;
    window.clearTimeout(activeRecognitionTimer);
    activeRecognitionTimer = null;
}

function scheduleActiveRecognitionTimeout(recognition) {
    clearActiveRecognitionTimer();
    activeRecognitionTimer = window.setTimeout(() => {
        if (activeRecognition === recognition) {
            stopActiveRecognition();
        }
    }, AUTO_STOP_DELAY_MS);
}

function requestTaskCheck(input) {
    if (!input) return;
    input.dispatchEvent(new CustomEvent(TASK_CHECK_REQUEST_EVENT, { bubbles: true }));
}

function setListeningState(btn, listening) {
    btn.classList.toggle("speech-mic--active", listening);
    btn.closest(".speech-input-wrap")?.classList.toggle("speech-input-wrap--listening", listening);
}

function stopActiveRecognition() {
    clearActiveRecognitionTimer();

    const recognition = activeRecognition;
    const btn = activeBtn;

    activeRecognition = null;
    activeBtn = null;

    if (btn) {
        setListeningState(btn, false);
        hideSpeechPreview(btn.closest(".speech-input-wrap"));
    }

    if (recognition) {
        try { recognition.stop(); } catch { /* ignore */ }
    }
}

export function stopActiveSpeechInput() {
    stopActiveRecognition();
}

/* ── Live-Vorschau: Zwischenergebnis grau im Feld, Feldinhalt bleibt unverändert ── */
let measureContext = null;

function measureTextWidth(field, text) {
    if (!text) return 0;
    measureContext ||= document.createElement("canvas").getContext("2d");
    const styles = window.getComputedStyle(field);
    measureContext.font = styles.font || `${styles.fontStyle} ${styles.fontWeight} ${styles.fontSize} ${styles.fontFamily}`;
    const spacing = parseFloat(styles.letterSpacing) || 0;
    return measureContext.measureText(text).width + spacing * text.length;
}

function hideSpeechPreview(wrap) {
    const preview = wrap?.querySelector(":scope > .speech-preview");
    if (!preview || preview.hidden) return;
    preview.hidden = true;
    preview.textContent = "";
    setPreviewLineReserved(wrap, false);
}

// Reserviert unten im Textfeld eine Zeile, falls die Vorschau nicht mehr in die letzte Zeile passt.
function setPreviewLineReserved(wrap, reserved) {
    if (wrap.classList.contains("speech-input-wrap--preview-below") === reserved) return;
    wrap.classList.toggle("speech-input-wrap--preview-below", reserved);
    const field = wrap.querySelector(":scope > textarea");
    if (field) resizeSpeechTextarea(field);
}

const MIRROR_STYLE_PROPS = [
    "boxSizing", "width", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
    "borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth", "borderStyle",
    "fontStyle", "fontVariant", "fontWeight", "fontStretch", "fontSize", "lineHeight", "fontFamily",
    "textAlign", "textTransform", "textIndent", "letterSpacing", "wordSpacing", "tabSize",
];

// Cursorposition in einem Textfeld über ein unsichtbares Spiegel-Element mit gleichen Textmaßen.
function getTextareaCaretPoint(field, position) {
    const styles = window.getComputedStyle(field);
    const mirror = document.createElement("div");
    MIRROR_STYLE_PROPS.forEach((prop) => { mirror.style[prop] = styles[prop]; });
    Object.assign(mirror.style, {
        position: "absolute",
        visibility: "hidden",
        top: "0",
        left: "-9999px",
        height: "auto",
        overflow: "hidden",
        whiteSpace: "pre-wrap",
        overflowWrap: "break-word",
    });
    mirror.textContent = field.value.slice(0, position);
    const marker = document.createElement("span");
    marker.textContent = "\u200b";
    mirror.appendChild(marker);
    document.body.appendChild(mirror);
    const point = { left: marker.offsetLeft, top: marker.offsetTop, lineHeight: marker.offsetHeight };
    mirror.remove();
    return point;
}

function showSpeechPreview(input, text) {
    const wrap = input.closest(".speech-input-wrap");
    if (!wrap) return;
    if (!text) {
        hideSpeechPreview(wrap);
        return;
    }

    let preview = wrap.querySelector(":scope > .speech-preview");
    if (!preview) {
        preview = document.createElement("span");
        preview.className = "speech-preview";
        preview.setAttribute("aria-hidden", "true");
        wrap.appendChild(preview);
    }
    preview.hidden = false;
    preview.textContent = text;
    preview.style.font = window.getComputedStyle(input).font;
    preview.style.fontStyle = "italic";

    const styles = window.getComputedStyle(input);
    const caret = Number.isInteger(input.selectionEnd) ? input.selectionEnd : input.value.length;
    const originX = input.offsetLeft + input.clientLeft;
    const textStart = originX + (parseFloat(styles.paddingLeft) || 0);
    const contentRight = wrap.clientWidth - (parseFloat(styles.paddingRight) || 0);
    const gap = caret > 0 ? 4 : 0;

    if (input instanceof HTMLTextAreaElement) {
        // Vorschau direkt hinter dem Text vor dem Cursor, notfalls am Anfang der nächsten Zeile.
        const point = getTextareaCaretPoint(input, caret);
        const originY = input.offsetTop + input.clientTop - input.scrollTop;
        let left = originX + point.left - input.scrollLeft + gap;
        let top = originY + point.top;
        let reserveLine = false;

        if (contentRight - left < 60) {
            left = textStart;
            top += point.lineHeight;
            const contentBottom = input.offsetTop + input.clientTop + input.clientHeight - (parseFloat(styles.paddingBottom) || 0);
            reserveLine = top + point.lineHeight > contentBottom + 1;
        }
        setPreviewLineReserved(wrap, reserveLine);

        preview.classList.remove("speech-preview--overlap");
        Object.assign(preview.style, {
            left: `${left}px`,
            top: `${top}px`,
            bottom: "auto",
            height: `${point.lineHeight}px`,
        });
        return;
    }

    // Einzeiliges Eingabefeld: Textbreite bis zum Cursor messen.
    const textX = textStart + measureTextWidth(input, input.value.slice(0, caret)) - input.scrollLeft;
    const maxLeft = contentRight - 32;
    Object.assign(preview.style, {
        left: `${Math.max(textStart, Math.min(textX + gap, maxLeft))}px`,
        top: "",
        bottom: "",
        height: "",
    });
    preview.classList.toggle("speech-preview--overlap", textX + gap > maxLeft);
    // Bei Überlänge das Ende des Gesprochenen zeigen.
    preview.scrollLeft = preview.scrollWidth;
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

function resizeSpeechTextarea(field) {
    if (!(field instanceof HTMLTextAreaElement)) return;
    const styles = window.getComputedStyle(field);
    const borderHeight = (parseFloat(styles.borderTopWidth) || 0) + (parseFloat(styles.borderBottomWidth) || 0);
    field.style.height = "auto";
    field.style.height = `${field.scrollHeight + borderHeight}px`;
}

function setupSpeechTextarea(field) {
    if (!(field instanceof HTMLTextAreaElement)) return;
    if (field.hasAttribute(AUTOGROW_ATTR)) return;
    field.setAttribute(AUTOGROW_ATTR, "");
    if (!field.hasAttribute("rows")) {
        field.setAttribute("rows", "1");
    }
    field.addEventListener("input", () => resizeSpeechTextarea(field));
    field.addEventListener("change", () => resizeSpeechTextarea(field));
    requestAnimationFrame(() => resizeSpeechTextarea(field));
}

function shouldInsertSpaceBetween(left, right) {
    if (!left || !right) return false;
    if (/\s$/.test(left) || /^\s/.test(right)) return false;
    if (/[([{„"']$/.test(left) || /^[,.;:!?\])}"']/.test(right)) return false;
    if (/[\d,.\-+*/=]$/.test(left) && /^[\d,.\-+*/=]/.test(right)) return false;
    return true;
}

function insertSpeechTextAtCursor(input, text) {
    const cleaned = String(text || "").trim();
    if (!cleaned) return false;

    const current = String(input.value || "");
    const rawStart = Number(input.selectionStart);
    const rawEnd = Number(input.selectionEnd);
    const hasSelectionRange = Number.isFinite(rawStart) && Number.isFinite(rawEnd);
    const start = hasSelectionRange ? Math.max(0, Math.min(current.length, rawStart)) : current.length;
    const end = hasSelectionRange ? Math.max(start, Math.min(current.length, rawEnd)) : current.length;
    const before = current.slice(0, start);
    const after = current.slice(end);

    const prefix = shouldInsertSpaceBetween(before, cleaned) ? " " : "";
    const suffix = shouldInsertSpaceBetween(cleaned, after) ? " " : "";
    const insertion = `${prefix}${cleaned}${suffix}`;

    input.value = `${before}${insertion}${after}`;
    const cursorPosition = before.length + prefix.length + cleaned.length;
    if (typeof input.setSelectionRange === "function") {
        try { input.setSelectionRange(cursorPosition, cursorPosition); } catch { /* ignore unsupported input types */ }
    }
    input.dispatchEvent(new Event("input", { bubbles: true }));
    return true;
}

/**
 * Standardverarbeitung für Antwortfelder: Zahlwörter normalisieren, einfügen,
 * abschließendes "check" löst die Aufgabenprüfung aus.
 */
function processAnswerTranscript(transcript, input) {
    const { spokenText, shouldCheck } = splitSpeechCheckCommand(transcript);
    const cleaned = normalizeSpeechTranscript(spokenText);
    const inserted = cleaned ? insertSpeechTextAtCursor(input, cleaned) : false;
    return {
        inserted,
        stop: shouldCheck,
        afterStop: shouldCheck ? () => requestTaskCheck(input) : undefined,
    };
}

function formatAnswerPreview(interim) {
    const { spokenText, shouldCheck } = splitSpeechCheckCommand(interim);
    const text = normalizeSpeechTranscript(spokenText);
    return shouldCheck ? `${text} ✓`.trim() : text;
}

function bindMic(btn, input, processTranscript = processAnswerTranscript, formatPreview = formatAnswerPreview) {
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
        recognition.interimResults = true;

        recognition.onstart = () => {
            activeRecognition = recognition;
            activeBtn = btn;
            setListeningState(btn, true);
            scheduleActiveRecognitionTimeout(recognition);
        };

        recognition.onspeechstart = () => {
            clearActiveRecognitionTimer();
        };

        recognition.onspeechend = () => {
            scheduleActiveRecognitionTimeout(recognition);
        };

        recognition.onend = () => {
            clearActiveRecognitionTimer();
            if (activeRecognition !== recognition || activeBtn !== btn) return;

            window.setTimeout(() => {
                if (activeRecognition !== recognition || activeBtn !== btn) return;
                try {
                    recognition.start();
                } catch {
                    stopActiveRecognition();
                }
            }, MOBILE_RESTART_DELAY_MS);
        };

        recognition.onerror = () => {
            clearActiveRecognitionTimer();
            setListeningState(btn, false);
            hideSpeechPreview(btn.closest(".speech-input-wrap"));
            if (activeBtn === btn) {
                activeRecognition = null;
                activeBtn = null;
            }
        };

        recognition.onresult = (event) => {
            let transcript = "";
            let interim = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    transcript += event.results[i][0].transcript;
                } else {
                    interim += event.results[i][0].transcript;
                }
            }

            if (interim) {
                clearActiveRecognitionTimer();
            }

            if (!transcript) {
                showSpeechPreview(input, formatPreview(interim));
                return;
            }

            showSpeechPreview(input, "");
            const { inserted, stop, afterStop } = processTranscript(transcript, input) || {};
            if (stop) {
                stopActiveRecognition();
                afterStop?.();
                return;
            }

            showSpeechPreview(input, formatPreview(interim));
            if (!inserted) return;
            scheduleActiveRecognitionTimeout(recognition);
        };

        try {
            recognition.start();
        } catch {
            // Permission denied or no user gesture.
        }
    });
}

/**
 * Adds a speech-input mic button to a single input.
 *
 * @param {HTMLInputElement|HTMLTextAreaElement} input
 * @param {object} [options]
 * @param {(transcript: string, input: HTMLElement) => {inserted?: boolean, stop?: boolean, afterStop?: () => void}} [options.processTranscript]
 *        Custom handling of final transcripts (default: answer-field behaviour).
 * @param {(interimTranscript: string) => string} [options.formatPreview]
 *        Text for the live preview of interim results (default: what would be inserted).
 * @returns {boolean} Whether a mic button was attached.
 */
export function attachSpeechInput(input, { processTranscript, formatPreview } = {}) {
    if (!input) return false;
    if (input instanceof HTMLInputElement && ["checkbox", "radio", "hidden"].includes(input.type)) return false;

    setupSpeechTextarea(input);
    if (!SUPPORTED || input.hasAttribute(ENHANCED_ATTR)) return false;

    input.setAttribute(ENHANCED_ATTR, "");

    const btn = createMicButton();
    bindMic(btn, input, processTranscript, formatPreview);

    // Wrap the input + mic in a relative container so the mic sits inside.
    // Works both standalone and inside .answer-field-group (training tasks),
    // where the check button stays outside as a sibling.
    const wrapper = document.createElement("span");
    wrapper.className = "speech-input-wrap";
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    wrapper.appendChild(btn);
    return true;
}

/**
 * Enhance text inputs inside `root` with a speech-input mic button.
 *
 * @param {HTMLElement} root       Container to scan for inputs.
 * @param {string}      [selector] CSS selector for target inputs.
 */
export function enhanceSpeechInputs(root, selector) {
    if (!root) return;

    const sel = selector || 'input[type="text"], input:not([type]), textarea';
    root.querySelectorAll(sel).forEach((input) => attachSpeechInput(input));
}

export { parseGermanNumberPhrase, parseGermanCardinalWord };

/** Whether the browser supports speech recognition. */
export const speechInputSupported = SUPPORTED;
