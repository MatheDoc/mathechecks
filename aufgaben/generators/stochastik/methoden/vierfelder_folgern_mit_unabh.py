"""Wahrscheinlichkeiten aus vollständiger Vier-Felder-Tafel bestimmen - mit bedingten Wkt.

Die Vier-Felder-Tafel ist vollständig ausgefüllt (alle 8 Felder sichtbar).
A und B sind in ca. 50 % der Aufgaben stochastisch unabhängig (ohne Hinweis in der Aufgabe).

Es werden genau 7 Teilaufgaben gestellt:
  1. Einzel:      P(A), P(¬A), P(B), P(¬B)
  2. Schnitt:     P(A∩B), P(A∩¬B), P(¬A∩B), P(¬A∩¬B)
  3. Vereinigung: P(A∩B), P(A∩¬B), P(¬A∩B), P(¬A∩¬B)
  4. Spezial:     symmetrische Differenz, Diagonalsumme, trivial 0/1
  5. Bedingte Wkt (A/¬A-Bedingung): P(B|A), P(¬B|A), P(B|¬A), P(¬B|¬A)
  6. Bedingte Wkt (B/¬B-Bedingung): P(A|B), P(¬A|B), P(A|¬B), P(¬A|¬B)
  7. MC-Frage zur stochastischen Unabhängigkeit
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import (
    ab_intro,
    extended_probs,
    sample_ab_case,
    sample_ab_case_independent,
    vft_slots,
)
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


# ---------------------------------------------------------------------------

_GROUP_EINZEL = ["pa", "pna", "pb", "pnb"]
_GROUP_SCHNITT = ["pab", "panb", "pnab", "pnanb"]
_GROUP_VEREINIGUNG = ["paub", "paunb", "pnaub", "pnaunb"]
_GROUP_SPEZIAL = ["symdiff", "diag_sum", "trivial_0", "trivial_1"]
_GROUP_COND_A = ["pba", "pnba", "pbna", "pnbna"]
_GROUP_COND_B = ["pab_c", "pnab_c", "panb_c", "pnanb_c"]


# ---------------------------------------------------------------------------

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
    "pba":     r"P_A(B)",
    "pnba":    r"P_A(\overline{B})",
    "pbna":    r"P_{\overline{A}}(B)",
    "pnbna":   r"P_{\overline{A}}(\overline{B})",
    "pab_c":   r"P_B(A)",
    "pnab_c":  r"P_B(\overline{A})",
    "panb_c":  r"P_{\overline{B}}(A)",
    "pnanb_c": r"P_{\overline{B}}(\overline{A})",
}

_SPEZIAL_LABELS: dict[str, list[str]] = {
    "symdiff": [
        r"P(A \cup B) - P(A \cap B)",
        r"P(A \cap \overline{B}) + P(\overline{A} \cap B)",
    ],
    "diag_sum": [
        r"P(A \cap B) + P(\overline{A} \cap \overline{B})",
    ],
    "trivial_0": [
        r"P(A \cap \overline{A})",
        r"P(B \cap \overline{B})",
    ],
    "trivial_1": [
        r"P(A \cup \overline{A})",
        r"P(B \cup \overline{B})",
    ],
}


def _frage_text(key: str, scenario, rng: random.Random) -> str:
    """Fragetext: Spezial-Wkt immer LaTeX; alle anderen 50/50 Text/LaTeX."""
    if key in _SPEZIAL_LABELS:
        return f"${rng.choice(_SPEZIAL_LABELS[key])}$."
    prob_text = scenario.prob_texts.get(key, "")
    if prob_text and rng.random() < 0.5:
        return f"die Wahrscheinlichkeit, dass {prob_text}"
    return f"${_LATEX[key]}$."


class MethodenVierfelderFolgernMitBedingtGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.vierfelder_folgern_mit_unabh"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            # 50 % unabhängig, 50 % abhängig - ohne Hinweis in der Aufgabe
            is_independent = rng.choice([True, False])
            if is_independent:
                case = sample_ab_case_independent(rng=rng, scenario=scenario)
            else:
                case = sample_ab_case(rng=rng, scenario=scenario)

            probs = extended_probs(case)

            chosen_keys: list[str] = [
                rng.choice(_GROUP_EINZEL),
                rng.choice(_GROUP_SCHNITT),
                rng.choice(_GROUP_VEREINIGUNG),
                rng.choice(_GROUP_SPEZIAL),
                rng.choice(_GROUP_COND_A),
                rng.choice(_GROUP_COND_B),
            ]

            # MC-Frage zur Unabhängigkeit
            claim_is_independence = rng.choice([True, False])
            if claim_is_independence:
                claim_text = (
                    scenario.independence_claim
                    or "$A$ und $B$ sind stochastisch unabhängig."
                )
                mc_correct_is_richtig = is_independent
            else:
                claim_text = (
                    scenario.dependence_claim
                    or "$A$ und $B$ sind stochastisch abhängig."
                )
                mc_correct_is_richtig = not is_independent

            mc_correct_index = 0 if mc_correct_is_richtig else 1
            mc_answer = mc(["Richtig", "Falsch"], correct_index=mc_correct_index)

            slots = vft_slots(case)
            intro = (
                ab_intro(scenario)
                + "Bestimmen Sie anhand der Vier-Felder-Tafel auf 4 NKS gerundet"
            )

            fragen = [_frage_text(k, scenario, rng) for k in chosen_keys]
            fragen.append(f"Überprüfen Sie die folgende Behauptung: {claim_text}")

            antworten = [
                numerical_stochastik_calc(probs[k])
                for k in chosen_keys
            ]
            antworten.append(mc_answer)

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=fragen,
                    antworten=antworten,
                    visual={
                        "type": "plot",
                        "spec": {
                            "type": "vft",
                            "slots": {str(k): v for k, v in slots.items()},
                            "givenSlots": list(range(1, 9)),
                        },
                    },
                )
            )

        return tasks

