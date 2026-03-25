import { getChecksByLernbereich } from "../data/checks-repo.js";

/* ------------------------------------------------------------------ */
/*  Markdown-light → HTML (für Beispiel-Dateien)                      */
/* ------------------------------------------------------------------ */

function mdToHtml(raw) {
    const lines = raw.split("\n");
    const out = [];
    let inParagraph = false;

    for (const line of lines) {
        const trimmed = line.trimEnd();

        // Headings
        const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
        if (headingMatch) {
            if (inParagraph) { out.push("</p>"); inParagraph = false; }
            const level = headingMatch[1].length;
            out.push(`<h${level}>${headingMatch[2]}</h${level}>`);
            continue;
        }

        // Empty line → close paragraph
        if (!trimmed) {
            if (inParagraph) { out.push("</p>"); inParagraph = false; }
            continue;
        }

        // Display-math block start ($$) or LaTeX environments — pass through
        if (trimmed.startsWith("$$") || trimmed.startsWith("\\begin{")) {
            if (inParagraph) { out.push("</p>"); inParagraph = false; }
            out.push(trimmed);
            continue;
        }

        // Inside display-math or LaTeX — pass through
        if (!inParagraph && (trimmed.startsWith("\\end{") || trimmed === "$$")) {
            out.push(trimmed);
            continue;
        }

        // Regular text
        if (!inParagraph) {
            // Don't wrap lines that are clearly LaTeX continuation
            if (trimmed.startsWith("&") || trimmed.startsWith("\\\\")) {
                out.push(trimmed);
                continue;
            }
            out.push("<p>");
            inParagraph = true;
        }
        out.push(trimmed);
    }

    if (inParagraph) out.push("</p>");
    return out.join("\n");
}

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
/*  Beispiel rendern (fetch + markdown-light)                          */
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

    const url = `/dev/lernbereiche/${gebiet}/${lernbereich}/beispiele/${nummer}-${sammlung}.md`;

    try {
        const resp = await fetch(url);
        if (!resp.ok) { container.hidden = true; return; }
        const md = await resp.text();
        if (!md.trim()) { container.hidden = true; return; }

        container.innerHTML = mdToHtml(md);
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
