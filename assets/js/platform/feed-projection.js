import { loadSystemSettings } from "./system-settings.js?v=20260521-feed-deferred-db";

const LERNBEREICH_ALIASES = {
  "differentialrechnung-ganzrationaler-funktionen": ["differentialrechnung"],
  "zufallsexperimente-und-wahrscheinlichkeiten": ["zufallsexperimente"],
};

const contentMetaPromiseByKey = new Map();

export const FEED_STEP_ORDER = {
  training_1: 1,
  recall: 2,
  training_2: 3,
  feynman: 4,
  training_3: 5,
  kompetenzliste_gate: 6,
};

export const FEED_STEP_META = {
  training_1: {
    moduleKey: "training",
    type: "training",
    icon: "🏋️",
    iconStyle: "background:var(--mt-training-soft, var(--accent-soft));color:var(--mt-training, var(--accent));",
    badgeType: "training",
    badgeLabel: "Training 1",
    description: "Starte mit der nächsten Trainingsaufgabe für diesen Check.",
  },
  recall: {
    moduleKey: "recall",
    type: "recall",
    icon: "🧠",
    iconStyle: "background:var(--mt-recall-soft, var(--amber-soft));color:var(--mt-recall, var(--amber));",
    badgeType: "recall",
    badgeLabel: "Recall",
    description: "Prüfe jetzt, ob du die Kernideen aus dem Check abrufen kannst.",
  },
  training_2: {
    moduleKey: "training",
    type: "training",
    icon: "🏋️",
    iconStyle: "background:var(--mt-training-soft, var(--accent-soft));color:var(--mt-training, var(--accent));",
    badgeType: "training",
    badgeLabel: "Training 2",
    description: "Der zweite Trainingsschritt ist jetzt fällig.",
  },
  feynman: {
    moduleKey: "feynman",
    type: "feynman",
    icon: "🎓",
    iconStyle: "background:var(--mt-feynman-soft, var(--teal-soft));color:var(--mt-feynman, var(--teal));",
    badgeType: "feynman",
    badgeLabel: "Feynman",
    description: "Erkläre den Check jetzt in eigenen Worten.",
  },
  training_3: {
    moduleKey: "training",
    type: "training",
    icon: "🏋️",
    iconStyle: "background:var(--mt-training-soft, var(--accent-soft));color:var(--mt-training, var(--accent));",
    badgeType: "training",
    badgeLabel: "Training 3",
    description: "Der letzte Trainingsschritt für diesen Check wartet noch.",
  },
  kompetenzliste_gate: {
    moduleKey: "kompetenzliste",
    type: "kompetenzliste",
    icon: "☑️",
    iconStyle: "background:var(--mt-kompetenzliste-soft, var(--lavender-soft));color:var(--mt-kompetenzliste, var(--lavender));",
    badgeType: "kompetenzliste",
    badgeLabel: "Kompetenz",
    description: "Öffne die Kompetenzliste, prüfe die markierte Kompetenz und bestätige sie erst dann als sicher.",
  },
};

const START_FEED_META = {
  moduleKey: "start",
  type: "start",
  icon: "🏠",
  iconStyle: "background:var(--mt-start-soft, var(--accent-soft));color:var(--mt-start, var(--accent));",
  badgeType: "start",
  badgeLabel: "Start",
  description: "",
};

function parseJsonScript(id, fallback) {
  try {
    return JSON.parse(document.getElementById(id)?.textContent || JSON.stringify(fallback));
  } catch {
    return fallback;
  }
}

function normalizeKey(value) {
  return String(value || "")
    .toLowerCase()
    .trim()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

export async function deferFeedActivity(supabase, activityKey) {
  const normalizedKey = String(activityKey || "").trim();
  if (!supabase || !normalizedKey) return;

  const { error } = await supabase.rpc("defer_feed_activity", {
    p_activity_key: normalizedKey,
  });

  if (error) throw error;
}

export async function clearDeferredFeedActivity(supabase, activityKey) {
  const normalizedKey = String(activityKey || "").trim();
  if (!supabase || !normalizedKey) return;

  const { error } = await supabase.rpc("clear_feed_activity_deferral", {
    p_activity_key: normalizedKey,
  });

  if (error) throw error;
}

async function loadActiveDeferredFeedActivityKeys(supabase) {
  if (!supabase) return new Set();

  const currentCompletedActivityCount = await loadCurrentFeedActivityCompletionCount(supabase);
  const { data, error } = await supabase
    .from("user_feed_activity_deferrals")
    .select("activity_key")
    .gt("defer_until_activity_count", currentCompletedActivityCount);

  if (error) throw error;

  return new Set((Array.isArray(data) ? data : [])
    .map((row) => String(row?.activity_key || "").trim())
    .filter(Boolean));
}

function filterDeferredFeedItems(items, deferredActivityKeys) {
  if (!deferredActivityKeys || !deferredActivityKeys.size) {
    return Array.isArray(items) ? items : [];
  }

  return (Array.isArray(items) ? items : []).filter((item) => {
    const activityKey = String(item?.activityKey || "").trim();
    return !activityKey || !deferredActivityKeys.has(activityKey);
  });
}

function normalizePositiveInteger(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

export function stripTrailingPeriod(text) {
  return String(text || "").trim().replace(/[.。]\s*$/, "");
}

function buildGebietMeta(gebiete) {
  return Object.fromEntries(
    (Array.isArray(gebiete) ? gebiete : []).map((gebiet) => [gebiet.key, {
      group: gebiet.name,
      icon: gebiet.icon,
      iconBg: gebiet.icon_bg,
      iconColor: gebiet.icon_color,
      color: gebiet.chip_color,
    }]),
  );
}

function buildCheckIndex(checks) {
  const index = new Map();

  const add = (rawKey, check) => {
    const key = normalizeKey(rawKey);
    if (!key || !check?.id) return;

    if (!index.has(key)) {
      index.set(key, []);
    }

    const list = index.get(key);
    if (!list.some((entry) => entry.id === check.id)) {
      list.push(check);
    }
  };

  (Array.isArray(checks) ? checks : []).forEach((entry) => {
    const checkId = String(entry?.check_id || "").trim();
    const label = String(entry?.["Ich kann"] || "").trim();
    const shortTitle = String(entry?.Schlagwort || "").trim();
    const numberValue = Number(entry?.Nummer);
    if (!checkId || !label) return;

    const check = {
      id: checkId,
      label,
      shortTitle,
      number: Number.isFinite(numberValue) ? numberValue : null,
    };

    add(entry?.Lernbereich, check);
    add(entry?.LernbereichAnzeigename, check);
  });

  return index;
}

function buildLernbereicheFromData(checks, gebiete, lernbereicheSource) {
  const gebietMeta = buildGebietMeta(gebiete);
  const checkIndex = buildCheckIndex(checks);
  const grouped = new Map();

  (Array.isArray(lernbereicheSource) ? lernbereicheSource : []).forEach((lernbereich) => {
    const meta = gebietMeta[lernbereich.gebiet];
    if (!meta) return;

    if (!grouped.has(lernbereich.gebiet)) {
      grouped.set(lernbereich.gebiet, {
        group: meta.group,
        icon: meta.icon,
        iconBg: meta.iconBg,
        iconColor: meta.iconColor,
        items: [],
      });
    }

    const candidates = [
      lernbereich.slug,
      lernbereich.name,
      ...(LERNBEREICH_ALIASES[lernbereich.slug] || []),
    ]
      .map(normalizeKey)
      .filter(Boolean);

    const checksById = new Map();
    candidates.forEach((candidate) => {
      (checkIndex.get(candidate) || []).forEach((check) => {
        if (!checksById.has(check.id)) {
          checksById.set(check.id, check);
        }
      });
    });

    grouped.get(lernbereich.gebiet).items.push({
      id: lernbereich.slug,
      name: lernbereich.name,
      gebietKey: lernbereich.gebiet,
      color: meta.color,
      checks: Array.from(checksById.values()),
    });
  });

  return Array.from(grouped.values());
}

function buildCheckMetaById(lernbereiche) {
  const map = new Map();

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      lb.checks.forEach((check) => {
        if (map.has(check.id)) return;
        map.set(check.id, {
          checkId: check.id,
          label: check.label,
          shortTitle: check.shortTitle,
          number: check.number,
          lernbereichId: lb.id,
          lernbereichName: lb.name,
          gebietKey: lb.gebietKey,
          groupName: group.group,
        });
      });
    });
  });

  return map;
}

function buildLernbereichMetaById(lernbereiche) {
  const map = new Map();

  lernbereiche.forEach((group) => {
    group.items.forEach((lb) => {
      if (map.has(lb.id)) return;
      map.set(lb.id, {
        lernbereichId: lb.id,
        lernbereichName: lb.name,
        gebietKey: lb.gebietKey,
        groupName: group.group,
      });
    });
  });

  return map;
}

export function buildFeedContentMetaFromLernbereiche(lernbereiche) {
  return {
    checkMetaById: buildCheckMetaById(lernbereiche),
    lernbereichMetaById: buildLernbereichMetaById(lernbereiche),
  };
}

export async function loadFeedContentMeta({
  checksUrl = "/checks.json",
  gebieteScriptId,
  lernbereicheScriptId,
} = {}) {
  const cacheKey = `${checksUrl}|${gebieteScriptId || ""}|${lernbereicheScriptId || ""}`;
  if (!contentMetaPromiseByKey.has(cacheKey)) {
    contentMetaPromiseByKey.set(cacheKey, (async () => {
      const gebiete = parseJsonScript(gebieteScriptId, []);
      const lernbereicheSource = parseJsonScript(lernbereicheScriptId, []);

      let checks = [];
      const response = await fetch(checksUrl, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`checks.json konnte nicht geladen werden (${response.status})`);
      }
      checks = await response.json();

      const lernbereiche = buildLernbereicheFromData(checks, gebiete, lernbereicheSource);
      return buildFeedContentMetaFromLernbereiche(lernbereiche);
    })());
  }

  return contentMetaPromiseByKey.get(cacheKey);
}

export function formatCheckIndexLabel(checkMeta) {
  const number = Number(checkMeta?.number);
  return Number.isFinite(number) && number > 0 ? `${number}. Check` : "Check";
}

export function formatCheckShortTitle(checkMeta) {
  const shortTitle = String(checkMeta?.shortTitle || "").trim();
  return shortTitle || stripTrailingPeriod(checkMeta?.label || "");
}

function formatCompactCheckTitle(checkMeta) {
  const shortTitle = formatCheckShortTitle(checkMeta);
  const number = Number(checkMeta?.number);
  return Number.isFinite(number) && number > 0 ? `${number} ${shortTitle}` : shortTitle;
}

function buildFeedActionHref(checkMeta, stepKey) {
  const stepMeta = FEED_STEP_META[stepKey];
  if (!checkMeta || !stepMeta?.moduleKey) return "";

  const params = new URLSearchParams({
    check_id: checkMeta.checkId,
    feed: "1",
    activity_key: `check:${checkMeta.checkId}:${stepKey}`,
    activity_step: stepKey,
    activity_run: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
  });

  return `/lernbereiche/${encodeURIComponent(checkMeta.gebietKey)}/${encodeURIComponent(checkMeta.lernbereichId)}/${stepMeta.moduleKey}.html?${params.toString()}`;
}

function buildFlashcardsFeedActionHref(lernbereichMeta, entry) {
  if (!lernbereichMeta || !entry?.activity_key) return "";

  const params = new URLSearchParams({
    feed: "1",
    activity_key: entry.activity_key,
    activity_step: "flashcards",
    activity_run: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
  });

  return `/lernbereiche/${encodeURIComponent(lernbereichMeta.gebietKey)}/${encodeURIComponent(lernbereichMeta.lernbereichId)}/flashcards.html?${params.toString()}`;
}

function buildStartFeedActionHref(lernbereichMeta, entry) {
  if (!lernbereichMeta || !entry?.activity_key) return "";

  const params = new URLSearchParams({
    feed: "1",
    activity_key: entry.activity_key,
    activity_step: "start",
    activity_run: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
  });

  return `/lernbereiche/${encodeURIComponent(lernbereichMeta.gebietKey)}/${encodeURIComponent(lernbereichMeta.lernbereichId)}/start.html?${params.toString()}`;
}

async function loadActiveSession(supabase) {
  if (!supabase) return null;

  const { data, error } = await supabase
    .from("learning_sessions")
    .select("id, started_at")
    .eq("status", "active")
    .order("started_at", { ascending: false })
    .limit(1);

  if (error) throw error;
  return Array.isArray(data) ? data[0] || null : null;
}

async function loadCheckFeedEntries(supabase, sessionId) {
  if (!supabase || !sessionId) return [];

  const stepKeys = Object.keys(FEED_STEP_ORDER);
  const { data, error } = await supabase
    .from("session_check_state")
    .select("check_id, current_step_key, current_step_status")
    .eq("session_id", sessionId)
    .eq("current_step_status", "due")
    .in("current_step_key", stepKeys);

  if (error) throw error;
  return Array.isArray(data) ? data : [];
}

function compareCheckEntries(left, right, contentMeta) {
  const leftStep = FEED_STEP_ORDER[String(left?.current_step_key || "").trim()] || 99;
  const rightStep = FEED_STEP_ORDER[String(right?.current_step_key || "").trim()] || 99;
  if (leftStep !== rightStep) return leftStep - rightStep;

  const leftMeta = contentMeta?.checkMetaById?.get(String(left?.check_id || "").trim());
  const rightMeta = contentMeta?.checkMetaById?.get(String(right?.check_id || "").trim());
  const leftNumber = Number(leftMeta?.number);
  const rightNumber = Number(rightMeta?.number);
  const leftOrder = Number.isFinite(leftNumber) && leftNumber > 0 ? leftNumber : Number.MAX_SAFE_INTEGER;
  const rightOrder = Number.isFinite(rightNumber) && rightNumber > 0 ? rightNumber : Number.MAX_SAFE_INTEGER;
  if (leftOrder !== rightOrder) return leftOrder - rightOrder;

  const lernbereichDelta = String(leftMeta?.lernbereichName || "").localeCompare(String(rightMeta?.lernbereichName || ""), "de");
  if (lernbereichDelta !== 0) return lernbereichDelta;

  const titleDelta = formatCheckShortTitle(leftMeta).localeCompare(formatCheckShortTitle(rightMeta), "de");
  if (titleDelta !== 0) return titleDelta;

  return String(left?.check_id || "").localeCompare(String(right?.check_id || ""), "de");
}

function orderSessionCheckEntries(checkEntries, contentMeta, systemSettings) {
  const entries = Array.isArray(checkEntries) ? checkEntries : [];
  if (!entries.length) return [];

  const followUpGap = normalizePositiveInteger(systemSettings?.feedSessionFollowUpMaxGap, 3);
  const freshStartEntries = entries
    .filter((entry) => String(entry?.current_step_key || "").trim() === "training_1")
    .sort((left, right) => compareCheckEntries(left, right, contentMeta));
  const followUpEntries = entries
    .filter((entry) => String(entry?.current_step_key || "").trim() !== "training_1")
    .sort((left, right) => compareCheckEntries(left, right, contentMeta));

  if (!freshStartEntries.length) return followUpEntries;
  if (!followUpEntries.length) return freshStartEntries;

  // Didaktische Regel fuer Session-Checks:
  // Eine begonnene Check-Kette soll sichtbar weitergehen, aber nicht sofort komplett durchlaufen.
  // feedSessionFollowUpMaxGap ist deshalb nur eine Obergrenze fuer frische training_1-Eintraege
  // zwischen zwei Folgeaktivitaeten. Der tatsaechliche Abstand schrumpft dynamisch, wenn vorne
  // training_1-Eintraege wegfallen, damit wartende Follow-ups wie Recall nach vorne ruecken koennen.
  const ordered = [];
  let freshIndex = 0;
  let followUpIndex = 0;

  while (freshIndex < freshStartEntries.length || followUpIndex < followUpEntries.length) {
    const remainingFreshStarts = freshStartEntries.length - freshIndex;
    const remainingFollowUps = followUpEntries.length - followUpIndex;
    const dynamicGap = remainingFollowUps > 0
      ? Math.min(followUpGap, Math.ceil(remainingFreshStarts / (remainingFollowUps + 1)))
      : remainingFreshStarts;

    for (let gapCount = 0; gapCount < dynamicGap && freshIndex < freshStartEntries.length; gapCount += 1) {
      ordered.push(freshStartEntries[freshIndex]);
      freshIndex += 1;
    }

    if (followUpIndex < followUpEntries.length) {
      ordered.push(followUpEntries[followUpIndex]);
      followUpIndex += 1;
    }

    if (freshIndex >= freshStartEntries.length && followUpIndex < followUpEntries.length) {
      ordered.push(...followUpEntries.slice(followUpIndex));
      break;
    }

    if (followUpIndex >= followUpEntries.length && freshIndex < freshStartEntries.length) {
      ordered.push(...freshStartEntries.slice(freshIndex));
      break;
    }
  }

  return ordered;
}

async function loadActivityFeedEntries(supabase, sessionId) {
  if (!supabase || !sessionId) return [];

  const { data, error } = await supabase
    .from("session_activity_state")
    .select("activity_key, activity_type, scope_type, lernbereich_slug, target_module_key, status, due_at, sort_bucket, sort_index")
    .eq("session_id", sessionId)
    .eq("status", "due")
    .order("sort_bucket", { ascending: true })
    .order("sort_index", { ascending: true })
    .order("due_at", { ascending: true })
    .order("activity_key", { ascending: true });

  if (error) throw error;
  return Array.isArray(data) ? data : [];
}

async function loadCurrentFeedActivityCompletionCount(supabase) {
  if (!supabase) return 0;

  const { data, error } = await supabase.rpc("get_current_feed_activity_completion_count");
  if (error) throw error;

  const count = Number(data);
  return Number.isFinite(count) && count >= 0 ? count : 0;
}

async function loadRetentionFeedEntries(supabase, { activeSession = null } = {}) {
  if (!supabase) return [];

  const hasActiveSession = Boolean(activeSession?.id);

  const [scopeResponse, completedActivityCount] = await Promise.all([
    supabase
      .from("user_retention_scopes")
      .select("activity_type, scope_type, lernbereich_slug, status, next_due_after_activity_count")
      .eq("activity_type", "flashcards")
      .eq("scope_type", "lernbereich")
      .eq("status", "active"),
    hasActiveSession ? loadCurrentFeedActivityCompletionCount(supabase) : Promise.resolve(0),
  ]);

  const { data: scopeRows, error: scopeError } = scopeResponse;

  if (scopeError) throw scopeError;

  const lernbereichSlugs = [...new Set((Array.isArray(scopeRows) ? scopeRows : [])
    .map((row) => String(row?.lernbereich_slug || "").trim())
    .filter(Boolean))];

  if (!lernbereichSlugs.length) return [];

  const stateBySlug = new Map(lernbereichSlugs.map((slug) => [slug, {
    hasState: false,
    firstDueAt: "",
  }]));

  const nowIso = new Date().toISOString();
  const { data: stateRows, error: stateError } = await supabase
    .from("retention_flashcard_card_state")
    .select("lernbereich_slug, next_due_at")
    .in("lernbereich_slug", lernbereichSlugs)
    .order("lernbereich_slug", { ascending: true })
    .order("next_due_at", { ascending: true });

  if (stateError) throw stateError;

  (Array.isArray(stateRows) ? stateRows : []).forEach((row) => {
    const lernbereichSlug = String(row?.lernbereich_slug || "").trim();
    const summary = stateBySlug.get(lernbereichSlug);
    if (!summary) return;
    summary.hasState = true;

    const nextDueAt = String(row?.next_due_at || "").trim();
    if (!summary.firstDueAt && nextDueAt && nextDueAt <= nowIso) {
      summary.firstDueAt = nextDueAt;
    }
  });

  if (hasActiveSession) {
    return (Array.isArray(scopeRows) ? scopeRows : [])
      .map((row) => {
        const lernbereichSlug = String(row?.lernbereich_slug || "").trim();
        const dueAfterActivityCount = Number(row?.next_due_after_activity_count);
        const summary = stateBySlug.get(lernbereichSlug) || { hasState: false, firstDueAt: "" };
        const isDueByActivityCount = Number.isFinite(dueAfterActivityCount) && dueAfterActivityCount <= completedActivityCount;
        const isDueByCardState = Boolean(summary.hasState && summary.firstDueAt);

        if (!lernbereichSlug || (!isDueByActivityCount && !isDueByCardState)) {
          return null;
        }

        return {
          activity_key: `retention:lernbereich:${lernbereichSlug}:flashcards`,
          activity_type: "flashcards",
          scope_type: "lernbereich",
          lernbereich_slug: lernbereichSlug,
          due_after_activity_count: isDueByActivityCount ? dueAfterActivityCount : null,
          due_at: summary.firstDueAt,
        };
      })
      .filter(Boolean)
      .sort((left, right) => {
        const leftDueByActivityCount = Number.isFinite(Number(left?.due_after_activity_count));
        const rightDueByActivityCount = Number.isFinite(Number(right?.due_after_activity_count));
        const dueTypeDelta = Number(rightDueByActivityCount) - Number(leftDueByActivityCount);
        if (dueTypeDelta !== 0) return dueTypeDelta;

        const activityDelta = Number(left?.due_after_activity_count || Number.MAX_SAFE_INTEGER)
          - Number(right?.due_after_activity_count || Number.MAX_SAFE_INTEGER);
        if (activityDelta !== 0) return activityDelta;

        const dueAtDelta = String(left?.due_at || "").localeCompare(String(right?.due_at || ""));
        if (dueAtDelta !== 0) return dueAtDelta;

        return String(left?.lernbereich_slug || "").localeCompare(String(right?.lernbereich_slug || ""), "de");
      });
  }

  return lernbereichSlugs
    .map((lernbereichSlug) => {
      const summary = stateBySlug.get(lernbereichSlug) || { hasState: false, firstDueAt: "" };
      if (summary.hasState && !summary.firstDueAt) return null;

      return {
        activity_key: `retention:lernbereich:${lernbereichSlug}:flashcards`,
        activity_type: "flashcards",
        scope_type: "lernbereich",
        lernbereich_slug: lernbereichSlug,
        due_at: summary.firstDueAt,
        is_initial_scope: !summary.hasState,
      };
    })
    .filter(Boolean)
    .sort((left, right) => {
      const initialDelta = Number(Boolean(right.is_initial_scope)) - Number(Boolean(left.is_initial_scope));
      if (initialDelta !== 0) return initialDelta;

      const leftDueAt = String(left.due_at || "");
      const rightDueAt = String(right.due_at || "");
      const dueDelta = leftDueAt.localeCompare(rightDueAt);
      if (dueDelta !== 0) return dueDelta;

      return String(left.lernbereich_slug || "").localeCompare(String(right.lernbereich_slug || ""), "de");
    });
}

function mergeHybridFeedItems(sessionItems, retentionItems, systemSettings) {
  if (!Array.isArray(sessionItems) || sessionItems.length === 0) {
    return Array.isArray(retentionItems) ? [...retentionItems] : [];
  }

  if (!Array.isArray(retentionItems) || retentionItems.length === 0) {
    return [...sessionItems];
  }

  const leadSessionItems = normalizePositiveInteger(systemSettings?.feedRetentionInterleaveLeadSessionItems, 1) - 1;
  const stride = normalizePositiveInteger(systemSettings?.feedRetentionInterleaveStride, 1);
  const merged = [];
  let sessionIndex = 0;
  let retentionIndex = 0;

  for (let leadCount = 0; leadCount <= leadSessionItems && sessionIndex < sessionItems.length; leadCount += 1) {
    merged.push(sessionItems[sessionIndex]);
    sessionIndex += 1;
  }

  while (sessionIndex < sessionItems.length || retentionIndex < retentionItems.length) {
    if (retentionIndex < retentionItems.length) {
      merged.push(retentionItems[retentionIndex]);
      retentionIndex += 1;
    }

    for (let strideCount = 0; strideCount < stride && sessionIndex < sessionItems.length; strideCount += 1) {
      merged.push(sessionItems[sessionIndex]);
      sessionIndex += 1;
    }

    if (sessionIndex >= sessionItems.length && retentionIndex < retentionItems.length) {
      merged.push(...retentionItems.slice(retentionIndex));
      break;
    }
  }

  return merged;
}

function buildSessionFeedItems(contentMeta, checkEntries, activityEntries, systemSettings) {
  const orderedCheckEntries = orderSessionCheckEntries(checkEntries, contentMeta, systemSettings);
  const checkItems = orderedCheckEntries
    .map((entry) => buildCheckFeedItem(contentMeta, entry))
    .filter(Boolean);

  const sessionActivityItems = (Array.isArray(activityEntries) ? activityEntries : [])
    .map((entry) => ({
      rawType: String(entry?.activity_type || "").trim(),
      item: buildSessionActivityFeedItem(contentMeta, entry),
    }))
    .filter((entry) => entry.item);

  const leadingStartItems = sessionActivityItems
    .filter((entry) => entry.rawType === "start")
    .map((entry) => entry.item);
  const trailingActivityItems = sessionActivityItems
    .filter((entry) => entry.rawType !== "start")
    .map((entry) => entry.item);

  return [...leadingStartItems, ...checkItems, ...trailingActivityItems];
}

function createFeedItem({
  kind,
  type,
  href,
  activityKey,
  icon,
  iconStyle,
  titleText,
  checkIndexLabel = "",
  checkKeyword = "",
  descText,
  badges,
  primaryBadge,
}) {
  return {
    kind,
    type,
    href,
    activityKey,
    icon,
    iconStyle,
    titleText,
    checkIndexLabel,
    checkKeyword,
    descText,
    badges,
    primaryBadge,
  };
}

function buildCheckFeedItem(contentMeta, entry) {
  const stepMeta = FEED_STEP_META[entry?.current_step_key];
  const checkMeta = contentMeta?.checkMetaById?.get(entry?.check_id);
  if (!stepMeta || !checkMeta) return null;

  const href = buildFeedActionHref(checkMeta, entry.current_step_key);
  if (!href) return null;

  const primaryBadge = { label: stepMeta.badgeLabel, type: stepMeta.badgeType };
  return createFeedItem({
    kind: "check",
    type: stepMeta.type,
    href,
    activityKey: `check:${checkMeta.checkId}:${entry.current_step_key}`,
    icon: stepMeta.icon,
    iconStyle: stepMeta.iconStyle,
    titleText: formatCompactCheckTitle(checkMeta),
    checkIndexLabel: formatCheckIndexLabel(checkMeta),
    checkKeyword: formatCheckShortTitle(checkMeta),
    descText: "",
    badges: [
      { label: "Session", type: "" },
      { label: checkMeta.lernbereichName, type: "" },
      primaryBadge,
    ],
    primaryBadge,
  });
}

function buildSessionActivityFeedItem(contentMeta, entry) {
  const lernbereichMeta = contentMeta?.lernbereichMetaById?.get(entry?.lernbereich_slug);
  if (!lernbereichMeta) return null;

  if (entry?.activity_type === "start") {
    const href = buildStartFeedActionHref(lernbereichMeta, entry);
    if (!href) return null;

    const primaryBadge = { label: START_FEED_META.badgeLabel, type: START_FEED_META.badgeType };
    return createFeedItem({
      kind: "session-activity",
      type: START_FEED_META.type,
      href,
      activityKey: entry.activity_key,
      icon: START_FEED_META.icon,
      iconStyle: START_FEED_META.iconStyle,
      titleText: lernbereichMeta.lernbereichName,
      descText: "",
      badges: [
        { label: "Session", type: "" },
        { label: lernbereichMeta.lernbereichName, type: "" },
        primaryBadge,
      ],
      primaryBadge,
    });
  }

  if (entry?.activity_type !== "flashcards") return null;

  const href = buildFlashcardsFeedActionHref(lernbereichMeta, entry);
  if (!href) return null;

  const primaryBadge = { label: "Flashcards", type: "flashcards" };
  return createFeedItem({
    kind: "session-activity",
    type: "flashcards",
    href,
    activityKey: entry.activity_key,
    icon: "📚",
    iconStyle: "background:var(--mt-flashcards-soft, var(--amber-soft));color:var(--mt-flashcards, var(--amber));",
    titleText: lernbereichMeta.lernbereichName,
    descText: "",
    badges: [
      { label: "Session", type: "" },
      { label: lernbereichMeta.lernbereichName, type: "" },
      primaryBadge,
    ],
    primaryBadge,
  });
}

function buildRetentionFeedItem(contentMeta, entry) {
  const lernbereichMeta = contentMeta?.lernbereichMetaById?.get(entry?.lernbereich_slug);
  if (entry?.activity_type !== "flashcards" || !lernbereichMeta) return null;

  const href = buildFlashcardsFeedActionHref(lernbereichMeta, entry);
  if (!href) return null;

  const primaryBadge = { label: "Flashcards", type: "flashcards" };
  return createFeedItem({
    kind: "retention",
    type: "flashcards",
    href,
    activityKey: entry.activity_key,
    icon: "📚",
    iconStyle: "background:var(--mt-flashcards-soft, var(--amber-soft));color:var(--mt-flashcards, var(--amber));",
    titleText: lernbereichMeta.lernbereichName,
    descText: "",
    badges: [
      { label: "Wiederholung", type: "" },
      { label: lernbereichMeta.lernbereichName, type: "" },
      primaryBadge,
    ],
    primaryBadge,
  });
}

export async function loadFeedProjection({
  supabase,
  contentMeta,
  limit = Infinity,
} = {}) {
  if (!supabase || !contentMeta) {
    return { activeSession: null, items: [], source: "empty" };
  }

  const activeSession = await loadActiveSession(supabase);
  const systemSettings = await loadSystemSettings(supabase);
  let items = [];
  let source = "empty";

  if (activeSession?.id) {
    const [checkEntries, activityEntries, retentionEntries] = await Promise.all([
      loadCheckFeedEntries(supabase, activeSession.id),
      loadActivityFeedEntries(supabase, activeSession.id),
      loadRetentionFeedEntries(supabase, { activeSession }),
    ]);

    const sessionItems = buildSessionFeedItems(contentMeta, checkEntries, activityEntries, systemSettings);
    const retentionItems = (Array.isArray(retentionEntries) ? retentionEntries : [])
      .map((entry) => buildRetentionFeedItem(contentMeta, entry))
      .filter(Boolean);

    items = mergeHybridFeedItems(sessionItems, retentionItems, systemSettings);

    if (items.length) {
      source = sessionItems.length ? "session" : "retention";
    }
  }

  if (!items.length) {
    const retentionEntries = await loadRetentionFeedEntries(supabase);
    items = (Array.isArray(retentionEntries) ? retentionEntries : [])
      .map((entry) => buildRetentionFeedItem(contentMeta, entry))
      .filter(Boolean);

    if (items.length) {
      source = "retention";
    }
  }

  if (items.length) {
    const deferredActivityKeys = await loadActiveDeferredFeedActivityKeys(supabase);
    items = filterDeferredFeedItems(items, deferredActivityKeys);
  }

  const visibleItems = items.slice(0, limit);

  return {
    activeSession,
    items: visibleItems,
    source,
  };
}