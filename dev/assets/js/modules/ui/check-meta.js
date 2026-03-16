function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function sanitizeTagName(tagName) {
  const value = String(tagName || "h3").toLowerCase();
  return /^[a-z][a-z0-9-]*$/.test(value) ? value : "h3";
}

function normalizeClassName(parts) {
  return parts
    .filter((part) => typeof part === "string" && part.trim())
    .join(" ")
    .trim();
}

export function formatCheckNumber(rawNumber, fallback = "-") {
  const numeric = Number(rawNumber);
  if (Number.isFinite(numeric)) {
    return String(numeric).padStart(2, "0");
  }
  const text = String(rawNumber || "").trim();
  return text || fallback;
}

export function buildCheckBadgeText(numberText, prefix = "Check") {
  const nummer = String(numberText || "").trim();
  const pre = String(prefix || "").trim();
  if (!nummer) return pre;
  if (!pre) return nummer;
  return `${pre} ${nummer}`;
}

export function renderCheckMetaRowMarkup({
  numberText,
  titleText,
  prefix = "Check",
  tone = "",
  rowClass = "",
  badgeClass = "",
  titleClass = "",
  titleTag = "h3",
}) {
  const tagName = sanitizeTagName(titleTag);
  const rowClassName = normalizeClassName(["dev-check-card__header-left", rowClass]);
  const toneBadgeClass = tone ? `dev-check-card__badge--${tone}` : "";
  const toneTitleClass = tone ? `dev-check-card__title--${tone}` : "";
  const badgeClassName = normalizeClassName(["dev-check-card__badge", toneBadgeClass, badgeClass]);
  const titleClassName = normalizeClassName(["dev-check-card__title", toneTitleClass, titleClass]);
  const badgeText = buildCheckBadgeText(numberText, prefix);

  return `<div class="${escapeHtml(rowClassName)}"><span class="${escapeHtml(
    badgeClassName
  )}">${escapeHtml(badgeText)}</span><${tagName} class="${escapeHtml(titleClassName)}">${escapeHtml(
    titleText || ""
  )}</${tagName}></div>`;
}

export function createCheckMetaRowNode(options) {
  const wrapper = document.createElement("div");
  wrapper.innerHTML = renderCheckMetaRowMarkup(options);
  return wrapper.firstElementChild;
}