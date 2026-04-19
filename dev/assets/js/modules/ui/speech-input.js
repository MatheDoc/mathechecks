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

            const cleaned = transcript.trim().replace(/\.+$/, "");

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
