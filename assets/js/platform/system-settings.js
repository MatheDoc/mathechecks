const DEFAULT_SYSTEM_SETTINGS = Object.freeze({
  // Source of truth liegt in public.system_settings.
  // Das Frontend haelt hier nur noch den aktuell verwendeten Read-Only-Teilausschnitt vor.
  // Kein lokaler Zahlen-Fallback: fehlende Werte bleiben null und werden im UI explizit nicht ersetzt.
  feedCoreGapNormalHours: null,
  planningDefaultSessionTempoDays: null,
});

const SETTING_KEY_TO_PROPERTY = Object.freeze({
  "feed.core_gap_normal_hours": "feedCoreGapNormalHours",
  "planning.default_session_tempo_days": "planningDefaultSessionTempoDays",
});

const ACTIVE_FRONTEND_SETTING_KEYS = Object.freeze(Object.keys(SETTING_KEY_TO_PROPERTY));

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
        .select("setting_key, value_integer")
        .in("setting_key", ACTIVE_FRONTEND_SETTING_KEYS);

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