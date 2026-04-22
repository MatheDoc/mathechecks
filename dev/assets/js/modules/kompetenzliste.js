import { getChecksByLernbereich } from "../data/checks-repo.js";
import { renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { renderCardActionsMenuMarkup, renderCardMenuLinkMarkup, initCardMenuDismiss } from "./ui/card-actions-menu.js";

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

function buildSkriptHref(check) {
    const path = window.location?.pathname || "";
    if (!path.endsWith("kompetenzliste.html")) return "";

    const targetPath = path.replace(/kompetenzliste\.html$/, "skript.html");
    const explicitAnchor = check?.skript_anchor ?? check?.SkriptAnchor ?? check?.skriptAnchor ?? "";
    if (typeof explicitAnchor === "string" && explicitAnchor.trim()) {
        return `${targetPath}#${encodeURIComponent(explicitAnchor.trim())}`;
    }

    const nummer = Number(check?.Nummer);
    if (Number.isFinite(nummer) && nummer > 0) {
        return `${targetPath}#${encodeURIComponent(`check-${nummer}`)}`;
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
        <article class="dev-check-card dev-check-card--kompetenzliste kl-row" data-check-id="${escapeHtml(getCheckId(check))}">
            <div class="dev-check-card__header">
                ${renderCheckMetaRowMarkup({
        numberText: nummer,
        titleText: schlagwort,
        prefix: "Kompetenz",
        tone: "kompetenzliste",
        rowClass: "kl-check-meta-row",
        titleClass: "kl-check-name",
        titleTag: "span",
    })}
                <div class="dev-check-card__header-actions kl-actions">
                    ${actionsMenu}
                </div>
            </div>
            <div class="kl-body">
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

export async function initKompetenzlisteModule({ lernbereich } = {}) {
    const root = document.getElementById("dev-kompetenzliste-root");
    if (!root) return;

    if (!lernbereich) {
        root.innerHTML = `<p style="color:var(--text-dim);">Kein Lernbereich angegeben.</p>`;
        return;
    }

    const checks = await getChecksByLernbereich(lernbereich);
    root.innerHTML = renderList(checks);
    initCardMenuDismiss(root);

    // Reveal after rendering.
    root.classList.add("dev-module-root--ready");
}
