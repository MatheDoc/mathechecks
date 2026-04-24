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
const ACTION_FEEDBACK_TONE_CLASSES = [
    "dev-check-card__actions-item--pending",
    "dev-check-card__actions-item--success",
    "dev-check-card__actions-item--error",
];
const menuItemFeedbackResetTimers = new WeakMap();

function getCardMenuItemLabelNode(item) {
    return item?.querySelector("span:last-child") || null;
}

function getCardMenuItemIconNode(item) {
    return item?.querySelector(".dev-check-card__actions-icon") || null;
}

function setCardMenuItemTone(item, tone = "") {
    if (!item) return;

    for (const cls of ACTION_FEEDBACK_TONE_CLASSES) {
        item.classList.remove(cls);
    }

    if (tone) {
        item.classList.add(`dev-check-card__actions-item--${tone}`);
    }
}

function setCardMenuItemContent(item, { label, icon, tone = "" } = {}) {
    if (!item) return;

    const labelNode = getCardMenuItemLabelNode(item);
    const iconNode = getCardMenuItemIconNode(item);

    if (typeof label === "string" && labelNode) {
        labelNode.textContent = label;
    }

    if (typeof icon === "string" && iconNode) {
        iconNode.textContent = icon;
    }

    setCardMenuItemTone(item, tone);
}

function clearCardMenuItemFeedbackReset(item) {
    const resetId = menuItemFeedbackResetTimers.get(item);
    if (!resetId) return;

    window.clearTimeout(resetId);
    menuItemFeedbackResetTimers.delete(item);
}

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

export function createCardMenuItem({ emoji, label, onClick, closeOnClick = true }) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "dev-check-card__actions-item";
    btn.setAttribute("role", "menuitem");
    btn.innerHTML = `<span class="dev-check-card__actions-icon" aria-hidden="true">${emoji}</span><span>${escapeAttr(label)}</span>`;
    if (onClick) {
        btn.addEventListener("click", (e) => {
            if (closeOnClick) {
                btn.closest("details")?.removeAttribute("open");
            } else {
                e.stopPropagation();
            }
            onClick(e);
        });
    }
    return btn;
}

export async function runCardMenuItemFeedbackAction(
    item,
    {
        pendingLabel = "Wird erstellt…",
        successLabel = "Kopiert!",
        errorLabel = "Fehler",
        pendingIcon = "⋯",
        successIcon = "✓",
        errorIcon = "!",
        resetDelayMs = 2000,
        closeMenuOnReset = true,
        action,
    }
) {
    if (!item || typeof action !== "function") return false;

    const labelNode = getCardMenuItemLabelNode(item);
    const iconNode = getCardMenuItemIconNode(item);
    const defaultLabel = labelNode?.textContent || "";
    const defaultIcon = iconNode?.textContent || "";

    clearCardMenuItemFeedbackReset(item);
    item.disabled = true;
    setCardMenuItemContent(item, {
        label: pendingLabel,
        icon: pendingIcon,
        tone: "pending",
    });

    let wasSuccessful = false;
    try {
        wasSuccessful = (await action()) !== false;
    } catch {
        wasSuccessful = false;
    }

    setCardMenuItemContent(item, {
        label: wasSuccessful ? successLabel : errorLabel,
        icon: wasSuccessful ? successIcon : errorIcon,
        tone: wasSuccessful ? "success" : "error",
    });

    const resetId = window.setTimeout(() => {
        clearCardMenuItemFeedbackReset(item);
        setCardMenuItemContent(item, {
            label: defaultLabel,
            icon: defaultIcon,
            tone: "",
        });
        item.disabled = false;
        if (closeMenuOnReset) {
            item.closest("details")?.removeAttribute("open");
        }
    }, resetDelayMs);

    menuItemFeedbackResetTimers.set(item, resetId);
    return wasSuccessful;
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
