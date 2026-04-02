"""Check 3 (bedingte-wahrscheinlichkeiten) - Wahrscheinlichkeiten aus Baumdiagramm bestimmen.

Das Baumdiagramm ist vollständig ausgefüllt (alle 10 Werte sichtbar).
A und B sind in ca. 50 % der Aufgaben stochastisch unabhängig - ohne Angabe in der Aufgabe.

Es werden genau 7 Teilaufgaben gestellt:
  1. Einzel: P(A), P(¬A), P(B) oder P(¬B)
  2. Schnitt: P(A∩B), P(A∩¬B), P(¬A∩B) oder P(¬A∩¬B)
  3. Vereinigung: P(A∩B), P(A∩¬B), P(¬A∩B) oder P(¬A∩¬B)
  4. Spezial: Symmetrische Differenz, Diagonalsumme oder trivial 0/1
  5. Bedingte Wkt (A/¬A-Bedingung): P(B|A), P(¬B|A), P(B|¬A) oder P(¬B|¬A)
  6. Bedingte Wkt (B/¬B-Bedingung): P(A|B), P(¬A|B), P(A|¬B) oder P(¬A|¬B)
  7. MC-Frage zur stochastischen Unabhängigkeit (Behauptung prüfen)
"""

import random
from decimal import Decimal, ROUND_HALF_UP

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import (
    ABCase,
    sample_ab_case,
    sample_ab_case_independent,
)
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


_Q4 = Decimal("0.0001")


def _r4(v: float) -> float:
    return float(Decimal(str(v)).quantize(_Q4, rounding=ROUND_HALF_UP))


def _extended_probs(c: ABCase) -> dict[str, float]:
    """Alle relevanten Wahrscheinlichkeiten inkl. bedingter Wkt."""
    p_b = _r4(c.p_a_and_b + c.p_not_a_and_b)
    p_nb = _r4(c.p_a_and_not_b + c.p_not_a_and_not_b)

    return {
        # Gruppe 1: Einzel
        "pa": c.p_a,
        "pna": c.p_not_a,
        "pb": p_b,
        "pnb": p_nb,
        # Gruppe 2: Schnitt
        "pab": c.p_a_and_b,
        "panb": c.p_a_and_not_b,
        "pnab": c.p_not_a_and_b,
        "pnanb": c.p_not_a_and_not_b,
        # Gruppe 3: Vereinigung
        "paub": _r4(1 - c.p_not_a_and_not_b),
        "paunb": _r4(1 - c.p_not_a_and_b),
        "pnaub": _r4(1 - c.p_a_and_not_b),
        "pnaunb": _r4(1 - c.p_a_and_b),
        # Gruppe 4: Spezial
        "symdiff": _r4(c.p_a_and_not_b + c.p_not_a_and_b),
        "diag_sum": _r4(c.p_a_and_b + c.p_not_a_and_not_b),
        "trivial_0": 0.0,
        "trivial_1": 1.0,
        # Gruppe 5: Bedingte Wkt (A/¬A-Bedingung)
        "pba": c.p_b_given_a,
        "pnba": c.p_not_b_given_a,
        "pbna": c.p_b_given_not_a,
        "pnbna": c.p_not_b_given_not_a,
        # Gruppe 6: Bedingte Wkt (B/¬B-Bedingung)
        "pab_c": _r4(c.p_a_and_b / p_b) if p_b > 0 else 0.0,
        "pnab_c": _r4(c.p_not_a_and_b / p_b) if p_b > 0 else 0.0,
        "panb_c": _r4(c.p_a_and_not_b / p_nb) if p_nb > 0 else 0.0,
        "pnanb_c": _r4(c.p_not_a_and_not_b / p_nb) if p_nb > 0 else 0.0,
    }


# ---------------------------------------------------------------------------

_GROUP_EINZEL = ["pa", "pna", "pb", "pnb"]
_GROUP_SCHNITT = ["pab", "panb", "pnab", "pnanb"]
_GROUP_VEREINIGUNG = ["paub", "paunb", "pnaub", "pnaunb"]
_GROUP_SPEZIAL = ["symdiff", "diag_sum", "trivial_0", "trivial_1"]
_GROUP_COND_A = ["pba", "pnba", "pbna", "pnbna"]
_GROUP_COND_B = ["pab_c", "pnab_c", "panb_c", "pnanb_c"]


# ---------------------------------------------------------------------------

_LATEX: dict[str, str] = {
    "pa":    r"P(A)",
    "pna":   r"P(\overline{A})",
    "pb":    r"P(B)",
    "pnb":   r"P(\overline{B})",
    "pab":   r"P(A \cap B)",
    "panb":  r"P(A \cap \overline{B})",
    "pnab":  r"P(\overline{A} \cap B)",
    "pnanb": r"P(\overline{A} \cap \overline{B})",
    "paub":  r"P(A \cup B)",
    "paunb": r"P(A \cup \overline{B})",
    "pnaub": r"P(\overline{A} \cup B)",
    "pnaunb": r"P(\overline{A} \cup \overline{B})",
    # Bedingte Wkt (A/¬A-Bedingung)
    "pba":   r"P_A(B)",
    "pnba":  r"P_A(\overline{B})",
    "pbna":  r"P_{\overline{A}}(B)",
    "pnbna": r"P_{\overline{A}}(\overline{B})",
    # Bedingte Wkt (B/¬B-Bedingung)
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


def _build_tree_visual(case: ABCase) -> dict:
    return {
        "type": "plot",
        "spec": {
            "type": "ab-tree",
            "pa": case.p_a,
            "pba": case.p_b_given_a,
            "pbna": case.p_b_given_not_a,
            "givenSlots": list(range(1, 11)),
        },
    }


def _frage_text(key: str, scenario, rng: random.Random) -> str:
    """Fragetext: Spezial-Wkt immer LaTeX; alle anderen 50/50 Text/LaTeX."""
    if key in _SPEZIAL_LABELS:
        return f"${rng.choice(_SPEZIAL_LABELS[key])}$."
    prob_text = scenario.prob_texts.get(key, "")
    if prob_text and rng.random() < 0.5:
        return f"die Wahrscheinlichkeit, dass {prob_text}"
    return f"${_LATEX[key]}$."


class MethodenBaumdiagrammFolgernMitUnabhGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.baumdiagramm_folgern_mitUnabh"

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

            probs = _extended_probs(case)

            # Standard-Gruppen (eine Wkt je Gruppe)
            chosen_keys: list[str] = [
                rng.choice(_GROUP_EINZEL),
                rng.choice(_GROUP_SCHNITT),
                rng.choice(_GROUP_VEREINIGUNG),
                rng.choice(_GROUP_SPEZIAL),
                rng.choice(_GROUP_COND_A),
                rng.choice(_GROUP_COND_B),
            ]

            # MC-Frage zur Unabhängigkeit
            # Behauptung: zufällig Abhängigkeit oder Unabhängigkeit behaupten
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

            intro = (
                f"<p>{scenario.intro}</p>"
                f"<p>$A$: {scenario.event_a}<br>"
                f"$B$: {scenario.event_b}</p>"
                "<p>Bestimmen Sie anhand des Baumdiagramms "
                "auf 4 NKS gerundet</p>"
            )

            fragen: list[str] = [_frage_text(k, scenario, rng) for k in chosen_keys]
            fragen.append(
                f"Überprüfen Sie die folgende Behauptung: {claim_text}"
            )

            antworten: list[str] = [
                numerical_stochastik_calc(probs[k])
                for k in chosen_keys
            ]
            antworten.append(mc_answer)

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=fragen,
                    antworten=antworten,
                    visual=_build_tree_visual(case),
                )
            )

        return tasks

