let checksPromise = null;

async function loadChecks() {
  if (!checksPromise) {
    checksPromise = fetch("/checks.json").then((response) => {
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
