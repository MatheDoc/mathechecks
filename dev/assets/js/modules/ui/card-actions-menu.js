/* ------------------------------------------------------------------ */
/*  Three-dot popover menu for dev-check-card headers                  */
/* ------------------------------------------------------------------ */

function escapeAttr(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
}

const DOTS_HTML = `<span class="dev-check-card__actions-dots" aria-hidden="true"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>`;

/* ── Imperative (DOM) API ─────────────────────────────── */

export function createCardActionsMenu() {
    const menu = document.createElement("details");
    menu.className = "dev-check-card__actions-menu";

    const trigger = document.createElement("summary");
    trigger.className = "dev-check-card__actions-trigger";
    trigger.setAttribute("aria-label", "Aktionen");
    trigger.innerHTML = DOTS_HTML;

    const popover = document.createElement("div");
    popover.className = "dev-check-card__actions-popover";
    popover.setAttribute("role", "menu");

    menu.appendChild(trigger);
    menu.appendChild(popover);

    /* close on outside click */
    document.addEventListener("click", (e) => {
        if (!menu.hasAttribute("open")) return;
        if (menu.contains(e.target)) return;
        menu.removeAttribute("open");
    });

    return { menu, popover };
}

export function createCardMenuItem({ emoji, label, onClick }) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "dev-check-card__actions-item";
    btn.setAttribute("role", "menuitem");
    btn.innerHTML = `<span class="dev-check-card__actions-icon" aria-hidden="true">${emoji}</span><span>${escapeAttr(label)}</span>`;
    if (onClick) {
        btn.addEventListener("click", (e) => {
            btn.closest("details")?.removeAttribute("open");
            onClick(e);
        });
    }
    return btn;
}

export function createCardMenuLink({ emoji, label, href }) {
    const a = document.createElement("a");
    a.className = "dev-check-card__actions-item";
    a.setAttribute("role", "menuitem");
    a.href = href;
    a.innerHTML = `<span class="dev-check-card__actions-icon" aria-hidden="true">${emoji}</span><span>${escapeAttr(label)}</span>`;
    return a;
}

/* ── Markup (template-literal) API ────────────────────── */

export function renderCardActionsMenuMarkup(itemsHtml) {
    return `<details class="dev-check-card__actions-menu"><summary class="dev-check-card__actions-trigger" aria-label="Aktionen">${DOTS_HTML}</summary><div class="dev-check-card__actions-popover" role="menu">${itemsHtml}</div></details>`;
}

export function renderCardMenuLinkMarkup({ emoji, label, href, tone = "" }) {
    const cls = tone
        ? `dev-check-card__actions-item dev-check-card__actions-item--${tone}`
        : "dev-check-card__actions-item";
    return `<a class="${cls}" role="menuitem" href="${escapeAttr(href)}"><span class="dev-check-card__actions-icon" aria-hidden="true">${emoji}</span><span>${escapeAttr(label)}</span></a>`;
}

/* ── Light-dismiss for template-rendered menus ────────── */

export function initCardMenuDismiss(root) {
    document.addEventListener("click", (e) => {
        const openMenus = (root || document).querySelectorAll(
            ".dev-check-card__actions-menu[open]"
        );
        for (const menu of openMenus) {
            if (!menu.contains(e.target)) menu.removeAttribute("open");
        }
    });

    (root || document).addEventListener("click", (e) => {
        const item = e.target.closest(".dev-check-card__actions-item");
        if (!item) return;
        const menu = item.closest(".dev-check-card__actions-menu");
        if (menu) menu.removeAttribute("open");
    });
}
