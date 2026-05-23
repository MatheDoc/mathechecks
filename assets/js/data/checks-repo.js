let checksPromise = null;

function resolveChecksUrl() {
  const bodyUrl = String(document.body?.dataset?.checksUrl || "").trim();
  if (bodyUrl) return bodyUrl;

  const dashboardUrl = String(document.querySelector("[data-dashboard-root]")?.dataset?.dashboardChecksUrl || "").trim();
  if (dashboardUrl) return dashboardUrl;

  return "/checks.json";
}

async function loadChecks() {
  if (!checksPromise) {
    checksPromise = fetch(resolveChecksUrl(), { cache: "no-store" }).then((response) => {
      if (!response.ok) {
        throw new Error("checks.json konnte nicht geladen werden");
      }
      return response.json();
    });
  }

  return checksPromise;
}

export async function getChecksByLernbereich(lernbereich) {
  const checks = await loadChecks();
  return checks
    .filter((entry) => entry && entry.Lernbereich === lernbereich)
    .sort((a, b) => (Number(a.Nummer) || 0) - (Number(b.Nummer) || 0));
}
