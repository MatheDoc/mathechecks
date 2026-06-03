import {
  completeStartActivity,
  completeCurrentTrainingStep,
  completeKompetenzlisteGate,
  getOrCreateFlashcardRound,
  getOrCreateRetentionFlashcardRound,
  keepCurrentFeedActivity,
  recordCheckModuleAttempt,
  releaseCurrentFeedActivity,
  recordFlashcardReview,
  recordRetentionFlashcardReview,
  resolveFlashcardRound,
  resolveRetentionFlashcardRound,
} from "./progress-client.js?v=20260602-start-complete-fix";

const FEED_BADGE_UPDATE_EVENT = "mathechecks:feed-updated";

function emitFeedUpdated() {
  if (typeof window === "undefined" || typeof CustomEvent !== "function") return;
  window.dispatchEvent(new CustomEvent(FEED_BADGE_UPDATE_EVENT));
}

function ensureFeedActionOk(result, fallbackReason, { emitsFeedUpdate = false } = {}) {
  if (result?.error) {
    throw result.error;
  }

  if (!result?.ok) {
    const reason = String(result?.reason || fallbackReason || "feed-action-failed").trim();
    if (reason === "not-configured") {
      throw new Error("Feed not configured");
    }
    if (reason === "signed-out") {
      throw new Error("Authentication required");
    }
    throw new Error(reason);
  }

  if (emitsFeedUpdate) {
    emitFeedUpdated();
  }

  return result;
}

export async function completeTrainingFeedStep({ checkId, activityKey }) {
  return ensureFeedActionOk(
    await completeCurrentTrainingStep({ checkId, activityKey }),
    "training-not-saved",
    { emitsFeedUpdate: true },
  );
}

export async function completeStartFeedStep({ lernbereichSlug, activityKey }) {
  return ensureFeedActionOk(
    await completeStartActivity({ lernbereichSlug, activityKey }),
    "start-not-saved",
    { emitsFeedUpdate: true },
  );
}

export async function recordCheckFeedDecision({
  lernbereichSlug,
  checkId,
  moduleKey,
  outcomeKey,
  activityKey,
}) {
  return ensureFeedActionOk(
    await recordCheckModuleAttempt({
      lernbereichSlug,
      checkId,
      moduleKey,
      outcomeKey,
      activityKey,
    }),
    "progress-not-saved",
    { emitsFeedUpdate: true },
  );
}

export async function completeKompetenzlisteFeedStep({ checkId, activityKey }) {
  return ensureFeedActionOk(
    await completeKompetenzlisteGate({ checkId, activityKey }),
    "kompetenzliste-gate-not-saved",
    { emitsFeedUpdate: true },
  );
}

export async function keepCurrentFeedCursor({ activityKey }) {
  return ensureFeedActionOk(
    await keepCurrentFeedActivity({ activityKey }),
    "feed-cursor-not-kept",
  );
}

export async function releaseCurrentFeedCursor({ activityKey }) {
  return ensureFeedActionOk(
    await releaseCurrentFeedActivity({ activityKey }),
    "feed-cursor-not-released",
  );
}

export function getFlashcardsFeedApi(trackKind = "session") {
  const usesRetentionTrack = String(trackKind || "").trim().toLowerCase() === "retention";
  const api = usesRetentionTrack
    ? {
      getOrCreateRound: getOrCreateRetentionFlashcardRound,
      recordReview: recordRetentionFlashcardReview,
      resolveRound: resolveRetentionFlashcardRound,
    }
    : {
      getOrCreateRound: getOrCreateFlashcardRound,
      recordReview: recordFlashcardReview,
      resolveRound: resolveFlashcardRound,
    };

  return {
    async getOrCreateRound(params) {
      return ensureFeedActionOk(
        await api.getOrCreateRound(params),
        "flashcards-round-not-loaded",
      );
    },

    async recordReview(params) {
      return ensureFeedActionOk(
        await api.recordReview(params),
        "flashcards-review-not-saved",
      );
    },

    async resolveRound(params) {
      return ensureFeedActionOk(
        await api.resolveRound(params),
        "flashcards-round-not-resolved",
        { emitsFeedUpdate: true },
      );
    },
  };
}