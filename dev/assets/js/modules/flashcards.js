import { getChecksByLernbereich } from "../data/checks-repo.js";

function getCheckId(check) {
    if (typeof check.check_id === "string" && check.check_id.trim()) {
        return check.check_id;
    }

    const gebiet = check.Gebiet || "gebiet";
    const lernbereich = check.Lernbereich || "lernbereich";
    const nummer = String(Number(check.Nummer) || 0).padStart(2, "0");
    return `${gebiet}__${lernbereich}__${nummer}`;
}

async function renderMath(targetNode, retries = 4) {
    if (!targetNode) return;

    const mathJax = window.MathJax;
    if (mathJax && typeof mathJax.typesetPromise === "function") {
        try {
            await mathJax.typesetPromise([targetNode]);
        } catch {
            // Keep UI responsive even if MathJax fails.
        }
        return;
    }

    if (retries <= 0) return;
    await new Promise((resolve) => setTimeout(resolve, 120));
    await renderMath(targetNode, retries - 1);
}

function renderInfo(root, text) {
    root.innerHTML = `<p style="color:var(--text-dim);line-height:1.6;">${text}</p>`;
    void renderMath(root);
}

function makeCardMarkup(check, showBack) {
    const title = check.Schlagwort || `Check ${check.Nummer}`;
    const front = check["Ich kann"] || "Keine Kartenfrage vorhanden.";
    const back = `Bezug: ${title}`;

    return `
    <article class="card" style="max-width:760px; margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px;">
        <div style="font-size:.76rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;">Flashcard</div>
        <div style="font-size:.76rem;color:var(--text-muted);">Check ${check.Nummer}</div>
      </div>
      <h3 style="margin:0 0 10px 0;">${title}</h3>
      <div style="line-height:1.6;">${showBack ? back : front}</div>
    </article>
  `;
}

export async function initFlashcardsModule({ root, lernbereich, preferredCheckId = "" }) {
    if (!lernbereich) {
        renderInfo(root, "Kein Lernbereich gesetzt (data-lernbereich fehlt).");
        return;
    }

    const checks = await getChecksByLernbereich(lernbereich);
    if (checks.length === 0) {
        renderInfo(root, `Keine Checks fuer Lernbereich "${lernbereich}" gefunden.`);
        return;
    }

    const byId = new Map(checks.map((check) => [getCheckId(check), check]));
    const hasPreferred = typeof preferredCheckId === "string" && preferredCheckId.trim() !== "";

    let index = 0;
    if (hasPreferred) {
        const selected = byId.get(preferredCheckId.trim());
        if (selected) {
            const selectedIndex = checks.findIndex((check) => getCheckId(check) === getCheckId(selected));
            index = selectedIndex >= 0 ? selectedIndex : 0;
        }
    }

    let showBack = false;

    function rerender() {
        const check = checks[index] || checks[0];
        root.innerHTML = `
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:12px;flex-wrap:wrap;">
        <button id="dev-fc-flip" type="button" class="btn-ghost">${showBack ? "Vorderseite" : "Rückseite"}</button>
        <button id="dev-fc-next" type="button" class="btn-ghost">Nächste Karte</button>
        <span style="font-size:.78rem;color:var(--text-muted);">${index + 1} / ${checks.length}</span>
      </div>
      ${makeCardMarkup(check, showBack)}
    `;

        const flipBtn = root.querySelector("#dev-fc-flip");
        const nextBtn = root.querySelector("#dev-fc-next");
        if (flipBtn) {
            flipBtn.addEventListener("click", () => {
                showBack = !showBack;
                rerender();
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                index = (index + 1) % checks.length;
                showBack = false;
                rerender();
            });
        }

        void renderMath(root);
    }

    rerender();
}
