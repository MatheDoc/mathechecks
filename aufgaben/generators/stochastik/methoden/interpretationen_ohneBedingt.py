"""Wahrscheinlichkeitsausdrücke im Sachzusammenhang interpretieren – ohne bedingte Wkt.

Pro Aufgabe werden genau 4 Teilfragen gestellt (je eine aus):
  1. EINZEL:      P(A), P(¬A), P(B), P(¬B)
  2. SCHNITT:     P(A∩B), P(A∩¬B), P(¬A∩B), P(¬A∩¬B)
  3. VEREINIGUNG: P(A∪B), P(A∪¬B), P(¬A∪B), P(¬A∪¬B)
  4. SPEZIAL:     symdiff, diag_sum, trivial_0, trivial_1

Jede Teilfrage ist eine MC-Frage mit 16 Optionen (Moodle CLOZE-Format).
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import ab_intro
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


# ── Gruppen ────────────────────────────────────────────────────────────────

_GROUP_EINZEL      = ["pa", "pna", "pb", "pnb"]
_GROUP_SCHNITT     = ["pab", "panb", "pnab", "pnanb"]
_GROUP_VEREINIGUNG = ["paub", "paunb", "pnaub", "pnaunb"]
_GROUP_SPEZIAL     = ["symdiff", "diag_sum", "trivial_0", "trivial_1"]

# Feste Reihenfolge des MC-Pools (16 Optionen)
_POOL_KEYS_16 = (
    _GROUP_EINZEL
    + _GROUP_SCHNITT
    + _GROUP_VEREINIGUNG
    + _GROUP_SPEZIAL
)

# ── LaTeX-Notation für Fragetexte ─────────────────────────────────────────

_LATEX: dict[str, str] = {
    "pa":      r"P(A)",
    "pna":     r"P(\overline{A})",
    "pb":      r"P(B)",
    "pnb":     r"P(\overline{B})",
    "pab":     r"P(A \cap B)",
    "panb":    r"P(A \cap \overline{B})",
    "pnab":    r"P(\overline{A} \cap B)",
    "pnanb":   r"P(\overline{A} \cap \overline{B})",
    "paub":    r"P(A \cup B)",
    "paunb":   r"P(A \cup \overline{B})",
    "pnaub":   r"P(\overline{A} \cup B)",
    "pnaunb":  r"P(\overline{A} \cup \overline{B})",
}

_SPEZIAL_LABELS: dict[str, list[str]] = {
    "symdiff":  [
        r"P(A \cup B) - P(A \cap B)",
        r"P(A \cap \overline{B}) + P(\overline{A} \cap B)",
    ],
    "diag_sum": [r"P(A \cap B) + P(\overline{A} \cap \overline{B})"],
    "trivial_0": [r"P(A \cap \overline{A})", r"P(B \cap \overline{B})"],
    "trivial_1": [r"P(A \cup \overline{A})", r"P(B \cup \overline{B})"],
}


# ── Hilfsroutinen ──────────────────────────────────────────────────────────

def _option_text(key: str, scenario) -> str:
    """Optionstext für den MC-Pool (ohne abschließenden Punkt, der wird separat ergänzt)."""
    if key == "symdiff":
        pa = scenario.prob_texts["pa"]
        pb = scenario.prob_texts["pb"]
        return f"entweder {pa} oder {pb}"
    if key == "diag_sum":
        pab   = scenario.prob_texts["pab"]
        pnanb = scenario.prob_texts["pnanb"]
        return f"{pab} oder {pnanb}"
    if key == "trivial_1":
        return scenario.trivial_1_text
    if key == "trivial_0":
        return scenario.trivial_0_text
    return scenario.prob_texts[key]


def _frage(key: str, rng: random.Random) -> str:
    if key in _SPEZIAL_LABELS:
        latex = rng.choice(_SPEZIAL_LABELS[key])
        return f"${latex}$ ist die Wahrscheinlichkeit, dass"
    return f"${_LATEX[key]}$ ist die Wahrscheinlichkeit, dass"


def _build_mc_answer(question_key: str, scenario) -> str:
    """Baut den Moodle-MC-CLOZE-String mit 16 Optionen auf."""
    options = [_option_text(k, scenario) + "." for k in _POOL_KEYS_16]
    correct = _POOL_KEYS_16.index(question_key)
    return mc(options, correct_index=correct)


# ── Generator ─────────────────────────────────────────────────────────────

class MethodenInterpretationenOhneBedingtGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.interpretationen_ohneBedingt"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            chosen_keys: list[str] = [
                rng.choice(_GROUP_EINZEL),
                rng.choice(_GROUP_SCHNITT),
                rng.choice(_GROUP_VEREINIGUNG),
                rng.choice(_GROUP_SPEZIAL),
            ]

            einleitung = (
                ab_intro(scenario)
                + "Interpretieren Sie die folgenden Wahrscheinlichkeiten im Sachzusammenhang."
            )

            fragen   = [_frage(k, rng) for k in chosen_keys]
            antworten = [_build_mc_answer(k, scenario) for k in chosen_keys]

            tasks.append(Task(einleitung=einleitung, fragen=fragen, antworten=antworten))

        return tasks
