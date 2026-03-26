import { getChecksByLernbereich } from "../data/checks-repo.js";
import { initSkriptVisuals } from "./skript-visuals.js";

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
/*  Tipps rendern                                                      */
/* ------------------------------------------------------------------ */

function renderTipps(container, check) {
    const tipps = Array.isArray(check?.Tipps) ? check.Tipps : [];
    if (tipps.length === 0) {
        container.hidden = true;
        return;
    }
    const ul = document.createElement("ul");
    ul.className = "check-anker__tipps-list";
    for (const tipp of tipps) {
        const li = document.createElement("li");
        li.textContent = tipp;
        ul.appendChild(li);
    }
    container.appendChild(ul);
}

/* ------------------------------------------------------------------ */
/*  Beispiel rendern (fetch Jekyll-processed HTML)                     */
/* ------------------------------------------------------------------ */

async function renderBeispiel(container, check) {
    const nummer = String(Number(check.Nummer) || 0).padStart(2, "0");
    const sammlung = String(check.Sammlung || "").trim();
    const gebiet = String(check.Gebiet || "").trim();
    const lernbereich = String(check.Lernbereich || "").trim();

    if (!sammlung || !gebiet || !lernbereich) {
        container.hidden = true;
        return;
    }

    const url = `/dev/lernbereiche/${gebiet}/${lernbereich}/beispiele/${nummer}-${sammlung}.html`;

    try {
        const resp = await fetch(url);
        if (!resp.ok) { container.hidden = true; return; }
        const html = await resp.text();
        if (!html.trim()) { container.hidden = true; return; }

        container.innerHTML = html;
        initSkriptVisuals(container);
        await typesetNode(container);
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
