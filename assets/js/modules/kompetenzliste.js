import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";
import { completeKompetenzlisteFeedStep } from "../platform/feed-actions.js?v=20260603-topbar-feed-badge";
import { renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { renderCardActionsMenuMarkup, renderCardMenuLinkMarkup, initCardMenuDismiss } from "./ui/card-actions-menu.js";
import { attachFeedCardControls, leaveFeedContext, navigateFromFeedContext } from "./ui/feed-card-controls.js?v=20260609-complete-icon";

const KOMPETENZLISTE_FEED_STEP_KEY = "kompetenzliste_gate";

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
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

function getTrainingCheckAnchorId(check) {
    const nummer = Number(check?.Nummer);
    if (Number.isFinite(nummer) && nummer > 0) {
        return `check-${nummer}`;
    }
    return `check-${encodeURIComponent(getCheckId(check))}`;
}

function toDomIdFragment(value) {
    return String(value || "")
        .toLowerCase()
        .replaceAll(/[^a-z0-9_-]+/g, "-")
        .replaceAll(/^-+|-+$/g, "");
}

function getRecallCheckAnchorId(check) {
    return `recall-check-${toDomIdFragment(getCheckId(check)) || "item"}`;
}

function getFeynmanCheckAnchorId(check) {
    return `fy-check-${toDomIdFragment(getCheckId(check)) || "item"}`;
}

function buildTrainingHref(check) {
    const path = window.location?.pathname || "";
    if (!path.endsWith("kompetenzliste.html")) return "";

    const targetPath = path.replace(/kompetenzliste\.html$/, "training.html");
    return `${targetPath}#${getTrainingCheckAnchorId(check)}`;
}

function buildRecallHref(check) {
    const path = window.location?.pathname || "";
    if (!path.endsWith("kompetenzliste.html")) return "";

    const targetPath = path.replace(/kompetenzliste\.html$/, "recall.html");
    return `${targetPath}#${getRecallCheckAnchorId(check)}`;
}

function buildFeynmanHref(check) {
    const path = window.location?.pathname || "";
    if (!path.endsWith("kompetenzliste.html")) return "";

    const targetPath = path.replace(/kompetenzliste\.html$/, "feynman.html");
    return `${targetPath}#${getFeynmanCheckAnchorId(check)}`;
}

function buildTrainingHrefFromCheckId(checkId) {
    const path = window.location?.pathname || "";
    if (!path.endsWith("kompetenzliste.html")) return "";
    const targetPath = path.replace(/kompetenzliste\.html$/, "training.html");
    const parts = String(checkId || "").split("__");
    const num = parseInt(parts[parts.length - 1], 10);
    const anchor = Number.isFinite(num) && num > 0
        ? `check-${num}`
        : `check-${encodeURIComponent(checkId)}`;
    return `${targetPath}#${anchor}`;
}

function buildSkriptHref(check) {
    const path = window.location?.pathname || "";
    if (!path.endsWith("kompetenzliste.html")) return "";

    const targetPath = path.replace(/kompetenzliste\.html$/, "skript.html");
    const nummer = Number(check?.Nummer);
    if (Number.isFinite(nummer) && nummer > 0) {
        return `${targetPath}#check-${nummer}`;
    }

    const explicitAnchor = check?.skript_anchor ?? check?.SkriptAnchor ?? check?.skriptAnchor ?? "";
    if (typeof explicitAnchor === "string" && explicitAnchor.trim()) {
        return `${targetPath}#${explicitAnchor.trim()}`;
    }

    return "";
}

function renderRow(check) {
    const nummerRaw = Number(check?.Nummer);
    const nummer = Number.isFinite(nummerRaw) ? String(nummerRaw) : "-";
    const kompetenz = check["Ich kann"] || "";
    const schlagwort = check.Schlagwort || "";
    const trainingHref = buildTrainingHref(check);
    const recallHref = buildRecallHref(check);
    const feynmanHref = buildFeynmanHref(check);
    const skriptHref = buildSkriptHref(check);

    const trainingItem = trainingHref ? renderCardMenuLinkMarkup({ emoji: "🏋️", label: "Training", href: trainingHref, tone: "training" }) : "";
    const recallItem = recallHref ? renderCardMenuLinkMarkup({ emoji: "🧠", label: "Recall", href: recallHref, tone: "recall" }) : "";
    const feynmanItem = feynmanHref ? renderCardMenuLinkMarkup({ emoji: "🎓", label: "Feynman", href: feynmanHref, tone: "feynman" }) : "";
    const skriptItem = skriptHref ? renderCardMenuLinkMarkup({ emoji: "📖", label: "Skript", href: skriptHref, tone: "skript" }) : "";
    const menuItems = trainingItem + recallItem + feynmanItem + skriptItem;
    const actionsMenu = menuItems ? renderCardActionsMenuMarkup(menuItems) : "";

    return `
        <article class="check-card check-card--kompetenzliste" data-check-id="${escapeHtml(getCheckId(check))}">
            <div class="check-card__header">
                ${renderCheckMetaRowMarkup({
        numberText: nummer,
        titleText: schlagwort,
        prefix: "Kompetenz",
        tone: "kompetenzliste",
        titleTag: "span",
    })}
                <div class="check-card__header-actions">
                    ${actionsMenu}
                </div>
            </div>
            <div class="check-card__body">
                <p class="kl-kompetenz">Ich kann ${escapeHtml(kompetenz)}</p>
            </div>
        </article>`;
}

function renderList(checks) {
    if (!checks.length) {
        return `<p style="color:var(--text-dim);line-height:1.6;">Keine Checks für diesen Lernbereich vorhanden.</p>`;
    }

    const rows = checks.map((check) => renderRow(check)).join("");
    return `<div class="kl-list">${rows}</div>`;
}

function normalizeKompetenzlisteFeedContext(activityContext) {
    if (!activityContext || activityContext.mode !== "feed") return null;
    return String(activityContext.activityStep || "").trim() === KOMPETENZLISTE_FEED_STEP_KEY
        ? {
            mode: "feed",
            activityKey: String(activityContext.activityKey || "").trim(),
            activityStep: KOMPETENZLISTE_FEED_STEP_KEY,
        }
        : null;
}

function getTargetCheckCard(root, preferredCheckId) {
    const cards = Array.from(root?.querySelectorAll?.("[data-check-id]") || []);
    cards.forEach((card) => {
        delete card.dataset.feedTarget;
    });

    const normalizedCheckId = String(preferredCheckId || "").trim();
    const targetCard = normalizedCheckId
        ? cards.find((card) => String(card.dataset.checkId || "").trim() === normalizedCheckId)
        : cards[0] || null;

    if (targetCard) {
        targetCard.dataset.feedTarget = "true";
    }

    return targetCard || null;
}

function attachKompetenzlisteFeedShell(root, { preferredCheckId = "", activityContext = null } = {}) {
    const feedContext = normalizeKompetenzlisteFeedContext(activityContext);
    if (!root || !feedContext) return;

    const targetCard = getTargetCheckCard(root, preferredCheckId);
    const resolvedCheckId = String(targetCard?.dataset?.checkId || preferredCheckId || "").trim();
    if (!targetCard || !resolvedCheckId) return;

    const controls = attachFeedCardControls(root, {
        cardSelector: '[data-feed-target="true"]',
        stepLabel: "Kompetenz",
    });
    if (!controls) return;

    let busy = false;
    let completed = false;
    let statusMessage = "Prüfe die markierte Kompetenz. Wenn sie sitzt, kannst du diesen Schritt abschließen.";
    let statusTone = "neutral";

    const completeDecision = async () => {
        if (busy) return;
        busy = true;
        statusMessage = "Der Schritt wird gespeichert.";
        statusTone = "neutral";
        renderControls();

        try {
            await completeKompetenzlisteFeedStep({
                checkId: resolvedCheckId,
                activityKey: feedContext.activityKey,
            });
        } catch (error) {
            console.error("Kompetenzlisten-Schritt konnte nicht abgeschlossen werden:", error);
            busy = false;
            statusMessage = "Der Schritt konnte gerade nicht gespeichert werden.";
            statusTone = "error";
            renderControls();
            throw error;
        }

        completed = true;
        statusMessage = "Der Schritt wurde abgeschlossen. Die nächste Feed-Aktivität wird geöffnet.";
        statusTone = "success";
        renderControls();
    };

    const openDecision = () => {
        if (!controls?.openDecisionDialog || busy || completed) return;

        controls.openDecisionDialog({
            title: "Kompetenz abhaken?",
            detail: "Wenn ja, wird der letzte Planschritt für diesen Check abgeschlossen.",
            repeatNowLabel: "Nein",
            repeatNowDetail: "Training anzeigen",
            repeatNowIcon: "🏋️",
            onComplete: completeDecision,
            onRepeat: () => {
                const trainingHref = buildTrainingHrefFromCheckId(resolvedCheckId);
                if (trainingHref) navigateFromFeedContext(trainingHref);
            },
        });
    };

    function renderControls() {
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
            items,
            ready: !busy && !completed,
        });
    }

    window.requestAnimationFrame(() => {
        targetCard.scrollIntoView({ block: "center", behavior: "auto" });
    });
    renderControls();
}

export async function initKompetenzlisteModule({
    root = document.getElementById("kompetenzliste-root"),
    lernbereich,
    preferredCheckId = "",
    activityContext = null,
} = {}) {
    if (!root) return;

    if (!lernbereich) {
        root.innerHTML = `<p style="color:var(--text-dim);">Kein Lernbereich angegeben.</p>`;
        return;
    }

    const checks = await getChecksByLernbereich(lernbereich);
    root.innerHTML = renderList(checks);
    initCardMenuDismiss(root);
    attachKompetenzlisteFeedShell(root, { preferredCheckId, activityContext });

    // Reveal after rendering.
    root.classList.add("module-root--ready");
}
