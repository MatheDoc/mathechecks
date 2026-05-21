import { completeStartFeedStep } from "../platform/feed-actions.js?v=20260520-start-feed";
import { attachFeedCardControls, leaveFeedContext } from "./ui/feed-card-controls.js?v=20260521-feed-session-gap";

const START_FEED_STEP_KEY = "start";

function normalizeStartFeedContext(activityContext) {
    if (!activityContext || activityContext.mode !== "feed") return null;
    return String(activityContext.activityStep || "").trim() === START_FEED_STEP_KEY
        ? { mode: "feed", activityStep: START_FEED_STEP_KEY }
        : null;
}

function attachStartFeedShell(root, { lernbereich = "", activityContext = null } = {}) {
    const feedContext = normalizeStartFeedContext(activityContext);
    const card = root?.querySelector?.("[data-start-feed-card]");
    if (!root || !feedContext || !card || !lernbereich) return;

    const controls = attachFeedCardControls(root, {
        cardSelector: "[data-start-feed-card]",
        stepLabel: "Start",
    });
    if (!controls) return;

    let busy = false;
    let completed = false;
    let statusMessage = "Lies die kurze Orientierung zum Lernbereich. Danach kannst du diese Start-Aktivität direkt abschließen.";
    let statusTone = "neutral";

    const completeDecision = async () => {
        if (busy) return;
        busy = true;
        statusMessage = "Die Start-Aktivität wird gespeichert.";
        statusTone = "neutral";
        renderControls();

        try {
            await completeStartFeedStep({ lernbereichSlug: lernbereich });
        } catch (error) {
            console.error("Start-Aktivität konnte nicht abgeschlossen werden:", error);
            busy = false;
            statusMessage = "Die Start-Aktivität konnte gerade nicht gespeichert werden.";
            statusTone = "error";
            renderControls();
            throw error;
        }

        completed = true;
        statusMessage = "Die Start-Aktivität wurde abgeschlossen. Die nächste Feed-Aktivität wird geöffnet.";
        statusTone = "success";
        renderControls();
    };

    const keepOpenDecision = () => {
        statusMessage = "Die Start-Aktivität bleibt im Feed offen.";
        statusTone = "neutral";
        renderControls();
    };

    const openDecision = () => {
        if (!controls?.openDecisionDialog || busy || completed) return;

        controls.openDecisionDialog({
            title: "Start-Aktivität abschließen?",
            detail: "Wenn du den Überblick gelesen hast, wird diese Einstiegsaktivität abgeschlossen und die nächste Feed-Aktivität geöffnet.",
            completeLabel: "Ja",
            completeDetail: "Nächste Aktivität",
            completeDashboardLabel: "Ja",
            completeDashboardDetail: "Zum Dashboard",
            repeatNowLabel: "Nein",
            repeatNowDetail: "Offen lassen",
            repeatLaterLabel: "Nein",
            repeatLaterDetail: "Später wiederholen",
            onComplete: completeDecision,
            onRepeat: keepOpenDecision,
        });
    };

    function renderControls() {
        const statusNode = card.querySelector("[data-start-feed-status]");
        if (statusNode) {
            statusNode.hidden = false;
            statusNode.textContent = statusMessage;
        }

        const items = [
            {
                icon: "❌",
                label: "Aktivität abbrechen",
                onClick: leaveFeedContext,
            },
            {
                icon: "✅",
                label: busy ? "Wird gespeichert ..." : "Abschluss vorbereiten",
                disabled: busy || completed,
                iconPulse: !busy && !completed,
                onClick: openDecision,
            },
        ];

        controls.render({
            status: statusMessage,
            tone: statusTone,
            ready: !busy && !completed,
            items,
        });
    }

    renderControls();
}

export async function initStartModule({ lernbereich = "", activityContext = null } = {}) {
    const root = document.querySelector(".mod-start-content");
    if (!root) return;

    attachStartFeedShell(root, {
        lernbereich,
        activityContext,
    });
}
