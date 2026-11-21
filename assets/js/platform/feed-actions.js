import {
  getOrCreateRetentionFlashcardRound,
  recordRetentionFlashcardReview,
  resolveRetentionFlashcardRound,
} from "./progress-client.js?v=20261121-feed-simple";

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

// Serverrunden gibt es nur noch für Retention-Flashcards; Session-Aktivitäten laufen frei.
export function getRetentionFlashcardsApi() {
  return {
    async getOrCreateRound(params) {
      return ensureFeedActionOk(
        await getOrCreateRetentionFlashcardRound(params),
        "flashcards-round-not-loaded",
      );
    },

    async recordReview(params) {
      return ensureFeedActionOk(
        await recordRetentionFlashcardReview(params),
        "flashcards-review-not-saved",
      );
    },

    async resolveRound(params) {
      return ensureFeedActionOk(
        await resolveRetentionFlashcardRound(params),
        "flashcards-round-not-resolved",
        { emitsFeedUpdate: true },
      );
    },
  };
}
