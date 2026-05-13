const LEGACY_BEISPIEL_SAMMLUNGEN = new Map([
  ["baumdiagramm-erstellen-ohne-unabh-var1", "baumdiagramm-erstellen-ohneUnabh-var1"],
  ["baumdiagramm-erstellen-ohne-unabh-var2", "baumdiagramm-erstellen-ohneUnabh-var2"],
  ["baumdiagramm-erstellen-ohne-unabh-var3", "baumdiagramm-erstellen-ohneUnabh-var3"],
  ["baumdiagramm-folgern-ohne-unabh", "baumdiagramm-folgern-ohneUnabh"],
  ["interpretationen-mit-bedingt", "interpretationen-mitBedingt"],
  ["baumdiagramm-erstellen-mit-unabh", "baumdiagramm-erstellen-mitUnabh"],
  ["baumdiagramm-folgern-mit-unabh", "baumdiagramm-folgern-mitUnabh"],
  ["vierfelder-erstellen-ohne-unabh", "vierfelder-erstellen-ohneUnabh"],
  ["vierfelder-folgern-ohne-unabh", "vierfelder-folgern-ohneUnabh"],
  ["vierfelder-erstellen-mit-unabh", "vierfelder-erstellen-mitUnabh"],
  ["vierfelder-folgern-mit-unabh", "vierfelder-folgern-mitUnabh"],
  ["ohne-struktur-ohne-info-unabh", "ohne-struktur-ohneInfoUnabh"],
  ["ohne-struktur-mit-info-unabh", "ohne-struktur-mitInfoUnabh"],
  ["venn-mit-bedingt", "venn-mitBedingt"],
  ["venn-ohne-bedingt", "venn-ohneBedingt"],
]);

function getBeispielContext(check) {
  const nummer = String(Number(check?.Nummer) || 0).padStart(2, "0");
  const sammlung = String(check?.Sammlung || "").trim();
  const gebiet = String(check?.Gebiet || "").trim();
  const lernbereich = String(check?.Lernbereich || "").trim();

  if (!sammlung || !gebiet || !lernbereich) return null;
  return { nummer, sammlung, gebiet, lernbereich };
}

function buildBeispielUrl(context, sammlung) {
  return `/lernbereiche/${context.gebiet}/${context.lernbereich}/beispiele/${context.nummer}-${sammlung}.html`;
}

function toLegacyBeispielSammlung(sammlung) {
  return LEGACY_BEISPIEL_SAMMLUNGEN.get(sammlung) || sammlung;
}

export function buildBeispielUrlCandidates(check) {
  const context = getBeispielContext(check);
  if (!context) return [];

  const legacySammlung = toLegacyBeispielSammlung(context.sammlung);
  if (legacySammlung !== context.sammlung) {
    return [
      buildBeispielUrl(context, legacySammlung),
      buildBeispielUrl(context, context.sammlung),
    ];
  }

  return [buildBeispielUrl(context, context.sammlung)];
}

export async function fetchBeispielHtml(check, cache = null) {
  const context = getBeispielContext(check);
  if (!context) return "";

  const cacheKey = `${context.gebiet}/${context.lernbereich}/${context.nummer}-${context.sammlung}`;
  if (cache?.has(cacheKey)) return cache.get(cacheKey);

  for (const url of buildBeispielUrlCandidates(check)) {
    try {
      const response = await fetch(url);
      if (!response.ok) continue;

      const html = (await response.text()).trim();
      if (!html) continue;

      if (cache) cache.set(cacheKey, html);
      return html;
    } catch {
      // Try the next known URL variant.
    }
  }

  if (cache) cache.set(cacheKey, "");
  return "";
}