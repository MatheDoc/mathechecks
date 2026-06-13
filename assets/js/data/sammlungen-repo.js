const sammlungCache = new Map();
const EXPORT_BASE_PATH = "/aufgaben/exports/json";
const EXPORT_URL_VERSION = "20260613-axis-grid-b";

function buildExportUrl(gebiet, lernbereich, sammlung) {
  const segments = [gebiet, lernbereich, `${sammlung}.json`]
    .map((seg) => encodeURIComponent(seg.trim().toLowerCase()));
  return `${EXPORT_BASE_PATH}/${segments.join("/")}?v=${EXPORT_URL_VERSION}`;
}

/**
 * Lädt eine Aufgabensammlung anhand von Gebiet, Lernbereich und Sammlungsname.
 * context muss { gebiet, lernbereich } enthalten.
 */
export async function getAufgabenSammlung(sammlungName, context = {}) {
  const gebiet = String(context?.gebiet ?? "").trim().toLowerCase();
  const lernbereich = String(context?.lernbereich ?? "").trim().toLowerCase();
  const sammlung = String(sammlungName ?? "").trim();

  if (!gebiet || !lernbereich || !sammlung) {
    throw new Error(
      `Unvollstaendiger Kontext fuer Sammlung "${sammlungName}" (gebiet="${gebiet}", lernbereich="${lernbereich}").`
    );
  }

  const cacheKey = `${gebiet}/${lernbereich}/${sammlung}?v=${EXPORT_URL_VERSION}`;
  if (sammlungCache.has(cacheKey)) {
    return sammlungCache.get(cacheKey);
  }

  const url = buildExportUrl(gebiet, lernbereich, sammlung);
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(
      `Export konnte nicht geladen werden: ${sammlungName} (${url}, HTTP ${response.status})`
    );
  }

  const data = await response.json();
  const normalized = Array.isArray(data) ? data : [];
  sammlungCache.set(cacheKey, normalized);
  return normalized;
}
