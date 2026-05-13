import { getChecksByLernbereich } from "../data/checks-repo.js";
import { fetchBeispielHtml } from "./beispiel-loader.js?v=20260514-beispiel-url-d";
import { initSkriptVisuals, refreshSkriptTables } from "./skript-visuals.js";
import { createCheckMetaRowNode, formatCheckNumber } from "./ui/check-meta.js";

const CHECK_ANKER_BEISPIEL_CACHE = new Map();

/* ------------------------------------------------------------------ */
/*  MathJax helper                                                     */
/* ------------------------------------------------------------------ */

async function typesetNode(node, retries = 4) {
    const mj = window.MathJax;
    if (mj?.typesetPromise) {
        try { await mj.typesetPromise([node]); } catch { /* ignore */ }
        return;
    }
    if (retries > 0) {
        await new Promise((r) => setTimeout(r, 150));
        await typesetNode(node, retries - 1);
    }
}

/* ------------------------------------------------------------------ */
/*  Card-Wrapper (shared by Tipps & Beispiel)                          */
/* ------------------------------------------------------------------ */

function createAnkerCard(check, label, moduleTone) {
    const card = document.createElement("article");
    card.className = `check-card check-card--${moduleTone}`;

    const header = document.createElement("div");
    header.className = "check-card__header";

    const headerLeft = createCheckMetaRowNode({
        numberText: formatCheckNumber(check?.Nummer),
        titleText: check.Schlagwort || check["Ich kann"] || `Check ${check.Nummer}`,
        prefix: label,
        tone: moduleTone,
        rowClass: "check-card__header-left",
        titleTag: "span",
    });

    header.appendChild(headerLeft);
    card.appendChild(header);

    const body = document.createElement("div");
    body.className = "check-card__body";
    card.appendChild(body);

    return { card, body };
}

/* ------------------------------------------------------------------ */
/*  Tipps rendern                                                      */
/* ------------------------------------------------------------------ */

function renderTipps(container, check) {
    const tipps = Array.isArray(check?.Tipps) ? check.Tipps : [];
    if (tipps.length === 0) {
        container.hidden = true;
        return;
    }

    const { card, body } = createAnkerCard(check, "Tipps", "recall");

    const ul = document.createElement("ul");
    ul.className = "check-anker__tipps-list";
    for (const tipp of tipps) {
        const li = document.createElement("li");
        li.textContent = tipp;
        ul.appendChild(li);
    }
    body.appendChild(ul);
    container.appendChild(card);
}

/* ------------------------------------------------------------------ */
/*  Beispiel rendern (fetch Jekyll-processed HTML)                     */
/* ------------------------------------------------------------------ */

async function renderBeispiel(container, check) {
    try {
        const html = await fetchBeispielHtml(check, CHECK_ANKER_BEISPIEL_CACHE);
        if (!html.trim()) { container.hidden = true; return; }

        const { card, body } = createAnkerCard(check, "Beispiel", "feynman");
        body.innerHTML = html;
        container.appendChild(card);

        initSkriptVisuals(body);
        await typesetNode(body);
        refreshSkriptTables(body);
    } catch {
        container.hidden = true;
    }
}

/* ------------------------------------------------------------------ */
/*  Hauptfunktion: alle .check-anker Elemente hydrieren                */
/* ------------------------------------------------------------------ */

export async function initCheckAnker({ root, lernbereich }) {
    if (!root || !lernbereich) return;

    const ankerNodes = Array.from(root.querySelectorAll(".check-anker[data-nummer]"));
    if (ankerNodes.length === 0) return;

    const checks = await getChecksByLernbereich(lernbereich);
    if (!Array.isArray(checks) || checks.length === 0) return;

    const checkByNummer = new Map();
    for (const check of checks) {
        checkByNummer.set(String(Number(check.Nummer)), check);
    }

    const tasks = ankerNodes.map(async (node) => {
        const nummer = node.dataset.nummer;
        const check = checkByNummer.get(nummer);
        if (!check) return;

        const tippsEl = node.querySelector(".check-anker__tipps");
        const beispielEl = node.querySelector(".check-anker__beispiel");

        if (tippsEl) renderTipps(tippsEl, check);
        if (beispielEl) await renderBeispiel(beispielEl, check);
    });

    await Promise.all(tasks);
}
