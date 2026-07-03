// Abschluss-Popup fuer freie Modulaufrufe (Training/Recall/Feynman).
// Bewusst optisch anders als der Feed-Entscheidungsdialog: schlichtes, zentriertes Overlay.
// Spezifikation: .github/quoten.md (Abschluss-Popup, Quotendelta).

const OVERLAY_CLASS = "task-completion-overlay";

function closeExistingPopups() {
  document.querySelectorAll(`.${OVERLAY_CLASS}`).forEach((node) => node.remove());
}

function formatRate(rate) {
  if (rate === null || rate === undefined || !Number.isFinite(Number(rate))) return null;
  const rounded = Math.round(Number(rate));
  return `${rounded}\u202f%`;
}

function buildQuoteDelta(previousRate, newRate, { labelText = "Deine Quote für diesen Check" } = {}) {
  const wrap = document.createElement("div");
  wrap.className = "task-completion-popup__quote";

  const hasNew = Number.isFinite(Number(newRate));
  const hasPrev = Number.isFinite(Number(previousRate));

  if (!hasNew) {
    wrap.classList.add("is-empty");
    const note = document.createElement("p");
    note.className = "task-completion-popup__quote-note";
    note.textContent = "Quote wird nach dem ersten gewerteten Durchgang sichtbar.";
    wrap.appendChild(note);
    return wrap;
  }

  const direction = !hasPrev
    ? "neutral"
    : Number(newRate) > Number(previousRate)
      ? "up"
      : Number(newRate) < Number(previousRate)
        ? "down"
        : "flat";
  wrap.classList.add(`is-${direction}`);

  const label = document.createElement("div");
  label.className = "task-completion-popup__quote-label";
  label.textContent = labelText;
  wrap.appendChild(label);

  const valueRow = document.createElement("div");
  valueRow.className = "task-completion-popup__quote-values";

  if (hasPrev && direction !== "flat") {
    const prev = document.createElement("span");
    prev.className = "task-completion-popup__quote-prev";
    prev.textContent = formatRate(previousRate);
    valueRow.appendChild(prev);

    const arrow = document.createElement("span");
    arrow.className = "task-completion-popup__quote-arrow";
    arrow.textContent = direction === "up" ? "\u2191" : "\u2193";
    valueRow.appendChild(arrow);
  }

  const current = document.createElement("span");
  current.className = "task-completion-popup__quote-current";
  current.textContent = formatRate(newRate);
  valueRow.appendChild(current);

  wrap.appendChild(valueRow);
  return wrap;
}

function buildDialogButton({ variant = "primary", icon = "", label = "", detail = "" } = {}) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `task-completion-popup__button task-completion-popup__button--${variant}`;

  const iconNode = document.createElement("span");
  iconNode.className = "task-completion-popup__button-icon";
  iconNode.setAttribute("aria-hidden", "true");
  iconNode.textContent = icon;
  button.appendChild(iconNode);

  const copy = document.createElement("span");
  copy.className = "task-completion-popup__button-copy";

  const labelNode = document.createElement("span");
  labelNode.className = "task-completion-popup__button-label";
  labelNode.textContent = label;
  copy.appendChild(labelNode);

  if (detail) {
    const detailNode = document.createElement("span");
    detailNode.className = "task-completion-popup__button-detail";
    detailNode.textContent = detail;
    copy.appendChild(detailNode);
  }

  button.appendChild(copy);
  return button;
}

/**
 * Zeigt das Abschluss-Popup.
 * @param {object} options
 * @param {("training"|"recall"|"feynman")} options.mode
 * @param {boolean} options.showQuote   Quotendelta anzeigen (nur Training).
 * @param {number|null} options.previousRate
 * @param {number|null} options.newRate
 * @param {function} options.onRepeat   Callback fuer "Wiederholen".
 * @param {function} options.onDashboard Callback fuer "Zum Dashboard".
 */
export function showTaskCompletionPopup({
  mode = "training",
  showQuote = false,
  quoteUnchanged = false,
  previousRate = null,
  newRate = null,
  onRepeat = null,
  onDashboard = null,
} = {}) {
  closeExistingPopups();

  const overlay = document.createElement("div");
  overlay.className = OVERLAY_CLASS;
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");

  const popup = document.createElement("div");
  popup.className = `task-completion-popup task-completion-popup--${mode}`;

  const eyebrow = document.createElement("p");
  eyebrow.className = "task-completion-popup__eyebrow";
  eyebrow.textContent = "Abschluss";
  popup.appendChild(eyebrow);

  const heading = document.createElement("h2");
  heading.className = "task-completion-popup__title";
  heading.textContent = mode === "training"
    ? "Aufgabe abgeschlossen"
    : mode === "recall"
      ? "Recall abgeschlossen"
      : "Durchgang abgeschlossen";
  popup.appendChild(heading);

  if (showQuote && !quoteUnchanged) {
    popup.appendChild(buildQuoteDelta(previousRate, newRate, {
      labelText: mode === "recall" ? "Deine Recall-Quote für diesen Check" : "Deine Quote für diesen Check",
    }));
  }

  if (quoteUnchanged) {
    const note = document.createElement("p");
    note.className = "task-completion-popup__void-note";
    note.textContent = "Dieser Durchgang wurde nicht gewertet, da alle Lösungen angezeigt wurden. Deine Quote bleibt unverändert.";
    popup.appendChild(note);
  }

  const close = () => overlay.remove();

  const actions = document.createElement("div");
  actions.className = "task-completion-popup__actions";

  const repeatDetail = mode === "training" ? "Neue Variante" : "Neuer Durchgang";
  const repeatBtn = buildDialogButton({
    variant: "primary",
    icon: "\u21ba",
    label: "Wiederholen",
    detail: repeatDetail,
  });
  repeatBtn.addEventListener("click", () => {
    close();
    if (typeof onRepeat === "function") onRepeat();
  });
  actions.appendChild(repeatBtn);

  const dashboardBtn = buildDialogButton({
    variant: "secondary",
    icon: "\u2197",
    label: "Zum Dashboard",
    detail: "\u00dcbersicht",
  });
  dashboardBtn.addEventListener("click", () => {
    close();
    if (typeof onDashboard === "function") {
      onDashboard();
      return;
    }
    window.location.assign("/dashboard.html");
  });
  actions.appendChild(dashboardBtn);

  popup.appendChild(actions);
  overlay.appendChild(popup);

  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) close();
  });
  document.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape") close();
    },
    { once: true }
  );

  document.body.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add("is-visible"));
  return { close };
}
