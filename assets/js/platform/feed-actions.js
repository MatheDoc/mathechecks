import {
  completeStartActivity,
  completeCurrentTrainingStep,
  completeKompetenzlisteGate,
  getOrCreateFlashcardRound,
  getOrCreateRetentionFlashcardRound,
  recordCheckModuleAttempt,
  recordFlashcardReview,
  recordRetentionFlashcardReview,
  resolveFlashcardRound,
  resolveRetentionFlashcardRound,
} from "./progress-client.js?v=20260521-flashcards-review-save";

function ensureFeedActionOk(result, fallbackReason) {
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

  return result;
}

export async function completeTrainingFeedStep({ checkId }) {
  return ensureFeedActionOk(
    await completeCurrentTrainingStep({ checkId }),
    "training-not-saved",
  );
}

export async function completeStartFeedStep({ lernbereichSlug }) {
  return ensureFeedActionOk(
    await completeStartActivity({ lernbereichSlug }),
    "start-not-saved",
  );
}

export async function recordCheckFeedDecision({
  lernbereichSlug,
  checkId,
  moduleKey,
  outcomeKey,
}) {
  return ensureFeedActionOk(
    await recordCheckModuleAttempt({
      lernbereichSlug,
      checkId,
      moduleKey,
      outcomeKey,
    }),
    "progress-not-saved",
  );
}

export async function completeKompetenzlisteFeedStep({ checkId }) {
  return ensureFeedActionOk(
    await completeKompetenzlisteGate({ checkId }),
    "kompetenzliste-gate-not-saved",
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
      );
    },
  };
}