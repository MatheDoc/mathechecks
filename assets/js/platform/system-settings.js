const DEFAULT_SYSTEM_SETTINGS = Object.freeze({
  // Bei Änderungen hier immer die passende Supabase-Migration für public.system_settings nachziehen.
  // Maximale Zahl sichtbarer Feed-Einträge im Dashboard.
  feedDashboardItemLimit: 5,
  // Basisabstand N für Retention-Flashcards; weitere Fälligkeiten wachsen als N, 2N, 4N, ...
  feedRetentionActivityBaseGap: 5,
  // Anzahl Session-Aktivitäten, die vor dem ersten Retention-Slot angezeigt werden.
  feedRetentionInterleaveLeadSessionItems: 1,
  // Anzahl weiterer Session-Aktivitäten zwischen zwei Retention-Slots.
  feedRetentionInterleaveStride: 1,
  // Legacy-Name: meint für die Planung offene Aktivitäten pro Tag, nicht Tage pro Aktivität.
  planningDefaultSessionTempoDays: 3,
});

const SETTING_KEY_TO_PROPERTY = Object.freeze({
  "feed.dashboard_item_limit": "feedDashboardItemLimit",
  "feed.retention_activity_base_gap": "feedRetentionActivityBaseGap",
  "feed.retention_interleave_lead_session_items": "feedRetentionInterleaveLeadSessionItems",
  "feed.retention_interleave_stride": "feedRetentionInterleaveStride",
  "planning.default_session_tempo_days": "planningDefaultSessionTempoDays",
});

let systemSettingsPromise = null;

function normalizePositiveInteger(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

export function getDefaultSystemSettings() {
  return { ...DEFAULT_SYSTEM_SETTINGS };
}

export async function loadSystemSettings(supabase) {
  if (!supabase) {
    return getDefaultSystemSettings();
  }

  if (!systemSettingsPromise) {
    systemSettingsPromise = (async () => {
      const settings = getDefaultSystemSettings();
      const { data, error } = await supabase
        .from("system_settings")
        .select("setting_key, value_integer");

      if (error) {
        console.warn("MatheChecks: Systemwerte konnten nicht geladen werden.", error);
        return settings;
      }

      (Array.isArray(data) ? data : []).forEach((row) => {
        const propertyName = SETTING_KEY_TO_PROPERTY[String(row?.setting_key || "").trim()];
        if (!propertyName) return;

        settings[propertyName] = normalizePositiveInteger(row?.value_integer, settings[propertyName]);
      });

      return settings;
    })();
  }

  return systemSettingsPromise;
}

export function resetSystemSettingsCache() {
  systemSettingsPromise = null;
}