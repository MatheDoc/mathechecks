import { getSupabaseClient, getSupabaseRuntimeConfig } from "./supabase-client.js";

function normalizeText(value) {
  return String(value || "").trim();
}

async function getAuthenticatedSupabaseClient() {
  if (!getSupabaseRuntimeConfig().configured) {
    return { supabase: null, ok: false, skipped: true, reason: "not-configured" };
  }

  const supabase = await getSupabaseClient();
  if (!supabase) {
    return { supabase: null, ok: false, skipped: true, reason: "not-configured" };
  }

  const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
  if (sessionError) {
    console.warn("MatheChecks: Auth-Session konnte fuer Fortschritt nicht geladen werden.", sessionError);
    return { supabase, ok: false, error: sessionError };
  }

  if (!sessionData?.session?.user) {
    return { supabase, ok: false, skipped: true, reason: "signed-out" };
  }

  return { supabase, ok: true };
}

export async function recordCheckModuleAttempt({
  lernbereichSlug,
  checkId,
  moduleKey,
  outcomeKey,
}) {
  const normalizedLernbereichSlug = normalizeText(lernbereichSlug);
  const normalizedCheckId = normalizeText(checkId);
  const normalizedModuleKey = normalizeText(moduleKey).toLowerCase();
  const normalizedOutcomeKey = normalizeText(outcomeKey).toLowerCase();

  if (!normalizedLernbereichSlug || !normalizedCheckId || !normalizedModuleKey || !normalizedOutcomeKey) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("record_check_module_attempt", {
      p_lernbereich_slug: normalizedLernbereichSlug,
      p_check_id: normalizedCheckId,
      p_module_key: normalizedModuleKey,
      p_outcome_key: normalizedOutcomeKey,
    });

    if (error) {
      console.warn("MatheChecks: Fortschritt konnte nicht gespeichert werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Speichern des Fortschritts.", error);
    return { ok: false, error };
  }
}

export async function completeKompetenzlisteGate({ checkId }) {
  const normalizedCheckId = normalizeText(checkId);

  if (!normalizedCheckId) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("complete_kompetenzliste_gate", {
      p_check_id: normalizedCheckId,
    });

    if (error) {
      console.warn("MatheChecks: Kompetenzlisten-Schritt konnte nicht abgeschlossen werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Abschließen des Kompetenzlisten-Schritts.", error);
    return { ok: false, error };
  }
}

export async function completeCurrentTrainingStep({ checkId }) {
  const normalizedCheckId = normalizeText(checkId);

  if (!normalizedCheckId) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("complete_current_training_step", {
      p_check_id: normalizedCheckId,
    });

    if (error) {
      console.warn("MatheChecks: Trainingsschritt konnte nicht abgeschlossen werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Abschließen des Trainingsschritts.", error);
    return { ok: false, error };
  }
}

export async function completeStartActivity({ lernbereichSlug }) {
  const normalizedLernbereichSlug = normalizeText(lernbereichSlug);

  if (!normalizedLernbereichSlug) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("complete_start_activity", {
      p_lernbereich_slug: normalizedLernbereichSlug,
    });

    if (error) {
      console.warn("MatheChecks: Start-Aktivität konnte nicht abgeschlossen werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Abschließen der Start-Aktivität.", error);
    return { ok: false, error };
  }
}

export async function setRetentionScopeStatus({ lernbereichSlug, status }) {
  const normalizedLernbereichSlug = normalizeText(lernbereichSlug);
  const normalizedStatus = normalizeText(status).toLowerCase();

  if (!normalizedLernbereichSlug || !normalizedStatus) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("set_retention_scope_status", {
      p_lernbereich_slug: normalizedLernbereichSlug,
      p_status: normalizedStatus,
    });

    if (error) {
      console.warn("MatheChecks: Wiederholungsstatus konnte nicht aktualisiert werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Aktualisieren des Wiederholungsstatus.", error);
    return { ok: false, error };
  }
}

export async function getOrCreateFlashcardRound({
  lernbereichSlug,
  cardIds,
  checkIds,
  taskIndices,
  cardLimit = 20,
}) {
  const normalizedLernbereichSlug = normalizeText(lernbereichSlug);
  const normalizedCardIds = Array.isArray(cardIds) ? cardIds.map(normalizeText) : [];
  const normalizedCheckIds = Array.isArray(checkIds) ? checkIds.map(normalizeText) : [];
  const normalizedTaskIndices = Array.isArray(taskIndices)
    ? taskIndices.map((value) => Math.max(0, Number(value) || 0))
    : [];
  const normalizedCardLimit = Math.max(1, Math.min(Number(cardLimit) || 20, 50));

  if (!normalizedLernbereichSlug || normalizedCardIds.length === 0 || normalizedCardIds.length !== normalizedCheckIds.length) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("get_or_create_flashcard_round", {
      p_lernbereich_slug: normalizedLernbereichSlug,
      p_card_ids: normalizedCardIds,
      p_check_ids: normalizedCheckIds,
      p_task_indices: normalizedTaskIndices,
      p_card_limit: normalizedCardLimit,
    });

    if (error) {
      console.warn("MatheChecks: Flashcard-Durchgang konnte nicht geladen werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data: Array.isArray(data) ? data : [] };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Laden des Flashcard-Durchgangs.", error);
    return { ok: false, error };
  }
}

export async function getOrCreateRetentionFlashcardRound({
  lernbereichSlug,
  cardIds,
  checkIds,
  taskIndices,
  cardLimit = 20,
}) {
  const normalizedLernbereichSlug = normalizeText(lernbereichSlug);
  const normalizedCardIds = Array.isArray(cardIds) ? cardIds.map(normalizeText) : [];
  const normalizedCheckIds = Array.isArray(checkIds) ? checkIds.map(normalizeText) : [];
  const normalizedTaskIndices = Array.isArray(taskIndices)
    ? taskIndices.map((value) => Math.max(0, Number(value) || 0))
    : [];
  const normalizedCardLimit = Math.max(1, Math.min(Number(cardLimit) || 20, 50));

  if (!normalizedLernbereichSlug || normalizedCardIds.length === 0 || normalizedCardIds.length !== normalizedCheckIds.length) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("get_or_create_retention_flashcard_round", {
      p_lernbereich_slug: normalizedLernbereichSlug,
      p_card_ids: normalizedCardIds,
      p_check_ids: normalizedCheckIds,
      p_task_indices: normalizedTaskIndices,
      p_card_limit: normalizedCardLimit,
    });

    if (error) {
      console.warn("MatheChecks: Retention-Flashcard-Durchgang konnte nicht geladen werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data: Array.isArray(data) ? data : [] };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Laden des Retention-Flashcard-Durchgangs.", error);
    return { ok: false, error };
  }
}

export async function recordFlashcardReview({ roundId, cardId, ratingKey }) {
  const normalizedRoundId = normalizeText(roundId);
  const normalizedCardId = normalizeText(cardId);
  const normalizedRatingKey = normalizeText(ratingKey).toLowerCase();

  if (!normalizedRoundId || !normalizedCardId || !normalizedRatingKey) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("record_flashcard_review", {
      p_round_id: normalizedRoundId,
      p_card_id: normalizedCardId,
      p_rating_key: normalizedRatingKey,
    });

    if (error) {
      console.warn("MatheChecks: Flashcard-Bewertung konnte nicht gespeichert werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Speichern der Flashcard-Bewertung.", error);
    return { ok: false, error };
  }
}

export async function recordRetentionFlashcardReview({ roundId, cardId, ratingKey }) {
  const normalizedRoundId = normalizeText(roundId);
  const normalizedCardId = normalizeText(cardId);
  const normalizedRatingKey = normalizeText(ratingKey).toLowerCase();

  if (!normalizedRoundId || !normalizedCardId || !normalizedRatingKey) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("record_retention_flashcard_review", {
      p_round_id: normalizedRoundId,
      p_card_id: normalizedCardId,
      p_rating_key: normalizedRatingKey,
    });

    if (error) {
      console.warn("MatheChecks: Retention-Flashcard-Bewertung konnte nicht gespeichert werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Speichern der Retention-Flashcard-Bewertung.", error);
    return { ok: false, error };
  }
}

export async function resolveFlashcardRound({ roundId, decisionKey }) {
  const normalizedRoundId = normalizeText(roundId);
  const normalizedDecisionKey = normalizeText(decisionKey).toLowerCase();

  if (!normalizedRoundId || !normalizedDecisionKey) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("resolve_flashcard_round", {
      p_round_id: normalizedRoundId,
      p_decision_key: normalizedDecisionKey,
    });

    if (error) {
      console.warn("MatheChecks: Flashcard-Durchgang konnte nicht abgeschlossen werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Abschließen des Flashcard-Durchgangs.", error);
    return { ok: false, error };
  }
}

export async function resolveRetentionFlashcardRound({ roundId, decisionKey }) {
  const normalizedRoundId = normalizeText(roundId);
  const normalizedDecisionKey = normalizeText(decisionKey).toLowerCase();

  if (!normalizedRoundId || !normalizedDecisionKey) {
    return { ok: false, skipped: true, reason: "missing-input" };
  }

  try {
    const auth = await getAuthenticatedSupabaseClient();
    if (!auth.ok) return auth;

    const { data, error } = await auth.supabase.rpc("resolve_retention_flashcard_round", {
      p_round_id: normalizedRoundId,
      p_decision_key: normalizedDecisionKey,
    });

    if (error) {
      console.warn("MatheChecks: Retention-Flashcard-Durchgang konnte nicht abgeschlossen werden.", error);
      return { ok: false, error };
    }

    return { ok: true, data };
  } catch (error) {
    console.warn("MatheChecks: Unerwarteter Fehler beim Abschließen des Retention-Flashcard-Durchgangs.", error);
    return { ok: false, error };
  }
}