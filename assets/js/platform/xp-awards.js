// Erkennt im Training neu richtig beantwortete Antwortfelder (aus "task:question-checked")
// und vergibt dafür sofort XP. Der erste Fortschritt nach dem Rendern ist der wiederhergestellte
// Zustand und wird nur gemerkt, nicht vergeben.
import { awardXp } from "./progress-client.js?v=20261103-xp-runs";

export function createTrainingXpTracker(getContext) {
  let awarded = new Set();

  return {
    reset() {
      awarded = new Set();
    },
    handle(detail, { initial = false } = {}) {
      const questions = Array.isArray(detail?.questionFields) ? detail.questionFields : [];
      const fresh = [];
      questions.forEach((fields, questionPosition) => {
        (Array.isArray(fields) ? fields : []).forEach((field, fieldIndex) => {
          const key = `q${questionPosition}:f${fieldIndex}`;
          if (!field?.correct || field.revealed || awarded.has(key)) return;
          awarded.add(key);
          if (!initial && !detail?.solutionsRevealedGlobally) {
            fresh.push({ key, attempts: Math.max(1, Number(field.attempts) || 1) });
          }
        });
      });
      if (!fresh.length) return;

      const { lernbereich = "", checkId = "", taskIndex = 0 } = getContext() || {};
      if (!checkId) return;
      void awardXp({
        activityType: "training",
        lernbereichSlug: lernbereich,
        checkId,
        units: fresh.map((unit) => ({ ...unit, key: `t${taskIndex}:${unit.key}` })),
      });
    },
  };
}

// Recall/Feynman: nach jeder KI-Auswertung den Zuwachs je Item vergeben. Beitrag eines Items
// = Erstscore + Anteil der Verbesserung (wie in der Quote); vergeben wird nur, was neu dazukommt.
// Alle Items eines Durchgangs teilen sich den Schlüssel-Präfix "r<Durchgang>", der Server
// bestimmt daraus einen gemeinsamen Wiederholungsfaktor.
export function createRunXpTracker(activityType, getContext) {
  let runId = "";
  let awarded = new Map();

  const newRun = () => {
    runId = Math.random().toString(36).slice(2, 10);
    awarded = new Map();
  };
  newRun();

  return {
    reset: newRun,
    // contributions: Beitrag (0..1) je Item-Index, null für nicht bewertete oder aufgedeckte Items.
    sync(contributions) {
      const list = Array.isArray(contributions) ? contributions : [];
      const units = [];
      list.forEach((value, index) => {
        const score = Number(value);
        if (!Number.isFinite(score) || score <= 0) return;
        const bounded = Math.min(1, score);
        if (bounded <= (awarded.get(index) || 0) + 1e-6) return;
        awarded.set(index, bounded);
        units.push({ key: `r${runId}:i${index}`, score: bounded, itemCount: list.length });
      });
      if (!units.length) return;

      const { lernbereich = "", checkId = "" } = getContext() || {};
      if (!checkId) return;
      void awardXp({ activityType, lernbereichSlug: lernbereich, checkId, units });
    },
  };
}
