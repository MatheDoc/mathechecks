import { completeSessionStart } from "../platform/progress-client.js?v=20261121-feed-simple";
import { attachFreeCompletionControl } from "./ui/feed-card-controls.js?v=20261121-feed-simple";
import { showTaskCompletionPopup } from "./ui/task-completion-popup.js?v=20261121-feed-simple";

// Start ist sofort abschließbar: Wer die Orientierung geöffnet hat, kann sie abhaken.
function attachStartCompletion(root, { lernbereich = "" } = {}) {
    const card = root?.querySelector?.("[data-start-feed-card]");
    if (!card || !lernbereich) return;

    let completionPromise = null;

    const control = attachFreeCompletionControl(root, {
        cardSelector: "[data-start-feed-card]",
        stepLabel: "Start",
        onComplete: () => {
            if (!completionPromise) {
                completionPromise = completeSessionStart({ lernbereichSlug: lernbereich });
            }
            void completionPromise.finally(() => {
                showTaskCompletionPopup({
                    mode: "start",
                    onStay: () => control?.setReady(true),
                });
            });
        },
    });
    control?.setReady(true);
}

export async function initStartModule({ lernbereich = "" } = {}) {
    const root = document.querySelector(".mod-start-content");
    if (!root) return;

    attachStartCompletion(root, { lernbereich });
}
