const LERNBEREICH_ALIASES = {
  "differentialrechnung-ganzrationaler-funktionen": ["differentialrechnung"],
  "zufallsexperimente-und-wahrscheinlichkeiten": ["zufallsexperimente"],
};

const contentMetaPromiseByKey = new Map();

export const FEED_STEP_ORDER = {
  training: 1,
  recall: 2,
  feynman: 3,
  kompetenzliste_gate: 4,
};

export const FEED_STEP_META = {
  training: {
    moduleKey: "training",
    type: "training",
    icon: "🏋️",
    iconStyle: "background:var(--mt-training-soft, var(--accent-soft));color:var(--mt-training, var(--accent));",
    badgeType: "training",
    badgeLabel: "Training",
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
  feynman: {
    moduleKey: "feynman",
    type: "feynman",
    icon: "🎓",
    iconStyle: "background:var(--mt-feynman-soft, var(--teal-soft));color:var(--mt-feynman, var(--teal));",
    badgeType: "feynman",
    badgeLabel: "Feynman",
    description: "Erkläre den Check jetzt in eigenen Worten.",
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
  return Number.isFinite(number) && number > 0 ? `${number}.` : "";
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

  if (entry.allow_early_feed_start) {
    params.set("allow_early_retention_start", "1");
  }

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

async function pickCurrentFeedCursor(supabase, sessionId) {
  if (!supabase || !sessionId) return null;

  const { data, error } = await supabase.rpc("pick_feed_cursor", {
    p_session_id: sessionId,
  });

  if (error) throw error;
  return Array.isArray(data) ? data[0] || null : null;
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

  const [scopeResponse, completedActivityCount, exclusionResponse] = await Promise.all([
    supabase
      .from("user_retention_scopes")
      .select("activity_type, scope_type, lernbereich_slug, status, next_due_after_activity_count, feed_queue_entry_activity_count, activity_due_exponent")
      .eq("activity_type", "flashcards")
      .eq("scope_type", "lernbereich")
      .eq("status", "active"),
    loadCurrentFeedActivityCompletionCount(supabase),
    supabase
      .from("user_retention_check_exclusions")
      .select("lernbereich_slug, check_id"),
  ]);

  const { data: scopeRows, error: scopeError } = scopeResponse;
  const { data: exclusionRows, error: exclusionError } = exclusionResponse;

  if (scopeError) throw scopeError;
  if (exclusionError) throw exclusionError;

  const lernbereichSlugs = [...new Set((Array.isArray(scopeRows) ? scopeRows : [])
    .map((row) => String(row?.lernbereich_slug || "").trim())
    .filter(Boolean))];

  if (!lernbereichSlugs.length) return [];

  // Ausgeschlossene Check-IDs pro Lernbereich
  const excludedChecksBySlug = new Map();
  (Array.isArray(exclusionRows) ? exclusionRows : []).forEach((row) => {
    const slug = String(row?.lernbereich_slug || "").trim();
    const checkId = String(row?.check_id || "").trim();
    if (!slug || !checkId) return;
    if (!excludedChecksBySlug.has(slug)) excludedChecksBySlug.set(slug, new Set());
    excludedChecksBySlug.get(slug).add(checkId);
  });

  const stateBySlug = new Map(lernbereichSlugs.map((slug) => [slug, {
    hasState: false,
    firstDueAt: "",
  }]));

  const nowIso = new Date().toISOString();
  const { data: stateRows, error: stateError } = await supabase
    .from("retention_flashcard_card_state")
    .select("lernbereich_slug, check_id, next_due_at")
    .in("lernbereich_slug", lernbereichSlugs)
    .order("lernbereich_slug", { ascending: true })
    .order("next_due_at", { ascending: true });

  if (stateError) throw stateError;

  (Array.isArray(stateRows) ? stateRows : []).forEach((row) => {
    const lernbereichSlug = String(row?.lernbereich_slug || "").trim();
    const checkId = String(row?.check_id || "").trim();
    // Karten ausgeschlossener Checks nicht in die Due-Prüfung einbeziehen
    if (checkId && excludedChecksBySlug.get(lernbereichSlug)?.has(checkId)) return;
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
        const queueEntryActivityCount = Number(row?.feed_queue_entry_activity_count);
        const dueExponent = Math.max(0, Number(row?.activity_due_exponent) || 0);
        const summary = stateBySlug.get(lernbereichSlug) || { hasState: false, firstDueAt: "" };
        const isDueByActivityCount = Number.isFinite(dueAfterActivityCount) && dueAfterActivityCount <= completedActivityCount;
        const isVisibleByQueue = dueExponent === 0
          && Number.isFinite(queueEntryActivityCount)
          && queueEntryActivityCount <= completedActivityCount;

        if (!lernbereichSlug || (!isDueByActivityCount && !isVisibleByQueue)) {
          return null;
        }

        const queueAnchorActivityCount = Number.isFinite(queueEntryActivityCount)
          ? queueEntryActivityCount
          : (Number.isFinite(dueAfterActivityCount) ? dueAfterActivityCount : completedActivityCount);

        return {
          activity_key: `retention:lernbereich:${lernbereichSlug}:flashcards`,
          activity_type: "flashcards",
          scope_type: "lernbereich",
          lernbereich_slug: lernbereichSlug,
          due_after_activity_count: Number.isFinite(dueAfterActivityCount) ? dueAfterActivityCount : null,
          queue_age: Math.max(0, completedActivityCount - queueAnchorActivityCount),
          due_at: summary.firstDueAt,
          allow_early_feed_start: isVisibleByQueue && !isDueByActivityCount,
        };
      })
      .filter(Boolean)
      .sort((left, right) => {
        const queueAgeDelta = Number(right?.queue_age || 0) - Number(left?.queue_age || 0);
        if (queueAgeDelta !== 0) return queueAgeDelta;

        const activityDelta = Number(left?.due_after_activity_count || Number.MAX_SAFE_INTEGER)
          - Number(right?.due_after_activity_count || Number.MAX_SAFE_INTEGER);
        if (activityDelta !== 0) return activityDelta;

        const dueAtDelta = String(left?.due_at || "").localeCompare(String(right?.due_at || ""));
        if (dueAtDelta !== 0) return dueAtDelta;

        return String(left?.lernbereich_slug || "").localeCompare(String(right?.lernbereich_slug || ""), "de");
      });
  }

  return (Array.isArray(scopeRows) ? scopeRows : [])
    .map((row) => {
      const lernbereichSlug = String(row?.lernbereich_slug || "").trim();
      const dueAfterActivityCount = Number(row?.next_due_after_activity_count);
      const queueEntryActivityCount = Number(row?.feed_queue_entry_activity_count);
      const dueExponent = Math.max(0, Number(row?.activity_due_exponent) || 0);
      const summary = stateBySlug.get(lernbereichSlug) || { hasState: false, firstDueAt: "" };
      const isDueByActivityCount = Number.isFinite(dueAfterActivityCount) && dueAfterActivityCount <= completedActivityCount;
      const isVisibleByQueue = dueExponent === 0
        && Number.isFinite(queueEntryActivityCount)
        && queueEntryActivityCount <= completedActivityCount;

      if (!lernbereichSlug || (!isDueByActivityCount && !isVisibleByQueue)) return null;

      return {
        activity_key: `retention:lernbereich:${lernbereichSlug}:flashcards`,
        activity_type: "flashcards",
        scope_type: "lernbereich",
        lernbereich_slug: lernbereichSlug,
        due_after_activity_count: Number.isFinite(dueAfterActivityCount) ? dueAfterActivityCount : null,
        queue_age: Math.max(0, completedActivityCount - (Number.isFinite(queueEntryActivityCount)
          ? queueEntryActivityCount
          : (Number.isFinite(dueAfterActivityCount) ? dueAfterActivityCount : completedActivityCount))),
        due_at: summary.firstDueAt,
      };
    })
    .filter(Boolean)
    .sort((left, right) => {
      const queueAgeDelta = Number(right?.queue_age || 0) - Number(left?.queue_age || 0);
      if (queueAgeDelta !== 0) return queueAgeDelta;

      const activityDelta = Number(left?.due_after_activity_count || Number.MAX_SAFE_INTEGER)
        - Number(right?.due_after_activity_count || Number.MAX_SAFE_INTEGER);
      if (activityDelta !== 0) return activityDelta;

      const leftDueAt = String(left.due_at || "");
      const rightDueAt = String(right.due_at || "");
      const dueDelta = leftDueAt.localeCompare(rightDueAt);
      if (dueDelta !== 0) return dueDelta;

      return String(left.lernbereich_slug || "").localeCompare(String(right.lernbereich_slug || ""), "de");
    });
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
  queueAge = 0,
  dueAfterActivityCount = null,
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
    queueAge,
    dueAfterActivityCount,
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
    badges: [primaryBadge],
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
      badges: [primaryBadge],
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
    badges: [primaryBadge],
    primaryBadge,
  });
}

function buildCurrentCursorFeedItem(contentMeta, cursorState) {
  const activityKind = String(cursorState?.activity_kind || "").trim();

  if (activityKind === "check") {
    return buildCheckFeedItem(contentMeta, {
      check_id: cursorState?.check_id,
      current_step_key: cursorState?.step_key,
    });
  }

  if (activityKind === "start" || activityKind === "flashcards") {
    return buildSessionActivityFeedItem(contentMeta, {
      activity_key: cursorState?.current_activity_key,
      activity_type: cursorState?.activity_type,
      lernbereich_slug: cursorState?.lernbereich_slug,
      target_module_key: cursorState?.target_module_key,
    });
  }

  return null;
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
    badges: [primaryBadge],
    primaryBadge,
    queueAge: Math.max(0, Number(entry?.queue_age || 0)),
    dueAfterActivityCount: Number.isFinite(Number(entry?.due_after_activity_count))
      ? Number(entry.due_after_activity_count)
      : null,
  });
}

export async function loadFeedProjection({
  supabase,
  contentMeta,
  limit = Infinity,
} = {}) {
  if (!supabase || !contentMeta) {
    return { activeSession: null, items: [], source: "empty", waiting: null };
  }

  const activeSession = await loadActiveSession(supabase);
  let items = [];
  let source = "empty";
  let waiting = null;

  if (activeSession?.id) {
    const cursorState = await pickCurrentFeedCursor(supabase, activeSession.id);
    const currentItem = buildCurrentCursorFeedItem(contentMeta, cursorState);

    if (currentItem) {
      items = [currentItem];
      source = "session";
    } else if (String(cursorState?.activity_kind || "").trim() === "waiting") {
      source = "waiting";
      waiting = {
        nextAvailableFrom: String(cursorState?.next_available_from || "").trim(),
      };
    }
  }

  if (!items.length && !waiting) {
    const retentionEntries = await loadRetentionFeedEntries(supabase);
    items = (Array.isArray(retentionEntries) ? retentionEntries : [])
      .map((entry) => buildRetentionFeedItem(contentMeta, entry))
      .filter(Boolean);

    if (items.length) {
      source = "retention";
    }
  }

  const visibleItems = items.slice(0, limit);

  return {
    activeSession,
    items: visibleItems,
    source,
    waiting,
  };
}