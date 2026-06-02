const DEFAULT_SYSTEM_SETTINGS = Object.freeze({
  // Bei Änderungen hier immer die passende Supabase-Migration für public.system_settings nachziehen.
  // Basisabstand in Stunden für didaktische Folgeaktivitäten im Core-Feed.
  feedCoreGapNormalHours: 24,
  // Basisabstand N für Retention-Flashcards; weitere Wiedereinblendungen wachsen als N, 2N, 3N, ...
  feedRetentionActivityBaseGap: 5,
  // Sichtbare Einstiegsposition neuer oder neu sichtbarer Retention-Einträge im Dashboard-Feed.
  feedRetentionNewItemPosition: 5,
  // Legacy-Name: meint für die Planung offene Aktivitäten pro Tag, nicht Tage pro Aktivität.
  planningDefaultSessionTempoDays: 3,
});

const SETTING_KEY_TO_PROPERTY = Object.freeze({
  "feed.core_gap_normal_hours": "feedCoreGapNormalHours",
  "feed.retention_activity_base_gap": "feedRetentionActivityBaseGap",
  "feed.retention_new_item_position": "feedRetentionNewItemPosition",
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