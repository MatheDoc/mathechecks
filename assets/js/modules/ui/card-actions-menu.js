/* ------------------------------------------------------------------ */
/*  Three-dot popover menu for check-card headers                  */
/* ------------------------------------------------------------------ */

function escapeAttr(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
}

const DOTS_HTML = `<span class="check-card__actions-dots" aria-hidden="true"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>`;
const ACTION_FEEDBACK_TONE_CLASSES = [
    "check-card__actions-item--pending",
    "check-card__actions-item--success",
    "check-card__actions-item--error",
];
const menuItemFeedbackResetTimers = new WeakMap();

function getCardMenuItemLabelNode(item) {
    return item?.querySelector("span:last-child") || null;
}

function getCardMenuItemIconNode(item) {
    return item?.querySelector(".check-card__actions-icon") || null;
}

function setCardMenuItemTone(item, tone = "") {
    if (!item) return;

    for (const cls of ACTION_FEEDBACK_TONE_CLASSES) {
        item.classList.remove(cls);
    }

    if (tone) {
        item.classList.add(`check-card__actions-item--${tone}`);
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
    menu.className = "check-card__actions-menu";

    const trigger = document.createElement("summary");
    trigger.className = "check-card__actions-trigger";
    trigger.setAttribute("aria-label", "Aktionen");
    trigger.innerHTML = DOTS_HTML;

    const popover = document.createElement("div");
    popover.className = "check-card__actions-popover";
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
    btn.className = "check-card__actions-item";
    btn.setAttribute("role", "menuitem");
    btn.innerHTML = `<span class="check-card__actions-icon" aria-hidden="true">${emoji}</span><span>${escapeAttr(label)}</span>`;
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

/**
 * Menüeintrag "Aufgabe wählen" mit ausklappbarem Nummernraster (Reihenfolge wie in der Sammlung).
 * enabledIndices (optional): nur diese 0-basierten Indizes sind wählbar.
 */
export function createCardTaskPicker({
    total,
    current = -1,
    enabledIndices = null,
    onSelect,
    emoji = "🔢",
    label = "Aufgabe wählen",
    chipAnchor = null,
}) {
    const wrapper = document.createElement("div");
    wrapper.className = "check-card__task-picker";

    const grid = document.createElement("div");
    grid.className = "check-card__task-picker-grid";
    grid.setAttribute("role", "group");
    grid.setAttribute("aria-label", "Aufgabe auswählen");
    grid.hidden = true;

    const toggle = createCardMenuItem({
        emoji,
        label,
        closeOnClick: false,
        onClick: () => {
            grid.hidden = !grid.hidden;
            toggle.setAttribute("aria-expanded", String(!grid.hidden));
        },
    });
    toggle.setAttribute("aria-expanded", "false");

    const collapseGrid = () => {
        grid.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
    };

    const enabledSet = Array.isArray(enabledIndices) ? new Set(enabledIndices) : null;
    const buttons = [];
    for (let index = 0; index < total; index += 1) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "check-card__task-picker-btn";
        btn.textContent = String(index + 1);
        btn.setAttribute("aria-label", `Aufgabe ${index + 1}`);
        if (enabledSet && !enabledSet.has(index)) btn.disabled = true;
        btn.addEventListener("click", () => {
            wrapper.closest("details")?.removeAttribute("open");
            collapseGrid();
            if (btn.getAttribute("aria-pressed") === "true") return;
            onSelect?.(index);
        });
        buttons.push(btn);
        grid.appendChild(btn);
    }

    // Kleines Chip im Header: zeigt die aktuelle Aufgabennummer und öffnet direkt das Raster.
    let chip = null;
    if (chipAnchor) {
        chip = document.createElement("button");
        chip.type = "button";
        chip.className = "check-card__task-chip";
        chip.addEventListener("click", (event) => {
            event.stopPropagation();
            const menu = wrapper.closest("details");
            if (!menu) return;
            if (menu.hasAttribute("open") && !grid.hidden) {
                menu.removeAttribute("open");
                return;
            }
            menu.setAttribute("open", "");
            grid.hidden = false;
            toggle.setAttribute("aria-expanded", "true");
        });
        chipAnchor.before(chip);
    }

    const setCurrent = (currentIndex) => {
        buttons.forEach((btn, index) => {
            btn.setAttribute("aria-pressed", String(index === currentIndex));
        });
        if (chip) {
            const number = currentIndex + 1;
            chip.textContent = `#${number}`;
            chip.setAttribute("aria-label", `Aufgabe ${number} – andere Aufgabe wählen`);
            chip.title = `Aufgabe ${number} – andere Aufgabe wählen`;
        }
    };
    setCurrent(current);

    wrapper.append(toggle, grid);
    return { element: wrapper, setCurrent };
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
    a.className = "check-card__actions-item";
    a.setAttribute("role", "menuitem");
    a.href = href;
    a.innerHTML = `<span class="check-card__actions-icon" aria-hidden="true">${emoji}</span><span>${escapeAttr(label)}</span>`;
    return a;
}

/* ── Markup (template-literal) API ────────────────────── */

export function renderCardActionsMenuMarkup(itemsHtml) {
    return `<details class="check-card__actions-menu"><summary class="check-card__actions-trigger" aria-label="Aktionen">${DOTS_HTML}</summary><div class="check-card__actions-popover" role="menu">${itemsHtml}</div></details>`;
}

export function renderCardMenuLinkMarkup({ emoji, label, href, tone = "" }) {
    const cls = tone
        ? `check-card__actions-item check-card__actions-item--${tone}`
        : "check-card__actions-item";
    return `<a class="${cls}" role="menuitem" href="${escapeAttr(href)}"><span class="check-card__actions-icon" aria-hidden="true">${emoji}</span><span>${escapeAttr(label)}</span></a>`;
}

/* ── Light-dismiss for template-rendered menus ────────── */

export function initCardMenuDismiss(root) {
    document.addEventListener("click", (e) => {
        const openMenus = (root || document).querySelectorAll(
            ".check-card__actions-menu[open]"
        );
        for (const menu of openMenus) {
            if (!menu.contains(e.target)) menu.removeAttribute("open");
        }
    });

    (root || document).addEventListener("click", (e) => {
        const item = e.target.closest(".check-card__actions-item");
        if (!item) return;
        const menu = item.closest(".check-card__actions-menu");
        if (menu) menu.removeAttribute("open");
    });
}
