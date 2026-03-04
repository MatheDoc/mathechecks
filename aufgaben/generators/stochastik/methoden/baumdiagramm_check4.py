"""Check 4 – Wahrscheinlichkeiten aus vollständigem Baumdiagramm bestimmen.

Das Baumdiagramm ist vollständig ausgefüllt (alle 10 Werte sichtbar).
Es werden 4 Wahrscheinlichkeiten abgefragt, je eine aus den Gruppen:

  1. Einzel: P(A), P(¬A), P(B) oder P(¬B)
  2. Schnitt: P(A∩B), P(A∩¬B), P(¬A∩B) oder P(¬A∩¬B)
  3. Vereinigung: P(A∪B), P(A∪¬B), P(¬A∪B) oder P(¬A∪¬B)
  4. Spezial:
       - P(A∪B) − P(A∩B)  bzw. äquivalent  P(A∩¬B) + P(¬A∩B)
       - P(A∩B) + P(¬A∩¬B)
       - P(A∩¬A) oder P(B∩¬B)   [trivial = 0]
       - P(A∪¬A) oder P(B∪¬B)   [trivial = 1]

Keine bedingten Wahrscheinlichkeiten.
"""

import random
from decimal import Decimal, ROUND_HALF_UP

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import ABCase, sample_ab_case
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


_Q4 = Decimal("0.0001")


def _r4(v: float) -> float:
    return float(Decimal(str(v)).quantize(_Q4, rounding=ROUND_HALF_UP))


def _extended_probs(c: ABCase) -> dict[str, float]:
    """Alle für Check 4 relevanten Wahrscheinlichkeiten."""
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
    }


# ── Gruppen ────────────────────────────────────────────────────────────────

_GROUP_EINZEL = ["pa", "pna", "pb", "pnb"]
_GROUP_SCHNITT = ["pab", "panb", "pnab", "pnanb"]
_GROUP_VEREINIGUNG = ["paub", "paunb", "pnaub", "pnaunb"]
_GROUP_SPEZIAL = ["symdiff", "diag_sum", "trivial_0", "trivial_1"]


# ── LaTeX / Frage-Texte ───────────────────────────────────────────────────

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
}

# Spezial-Fragen: zwei Varianten je Eintrag (zufällig gewählt)
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
    """Vollständig ausgefüllter Baum (alle 10 Slots gegeben)."""
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
    """Baut den Fragetext: mal LaTeX-Notation, mal Textbeschreibung."""
    # Für Spezialgruppe immer LaTeX
    if key in _SPEZIAL_LABELS:
        label = rng.choice(_SPEZIAL_LABELS[key])
        return f"\\({label}\\)."

    # Für Gruppen 1-3: zufällig LaTeX oder prob_text
    prob_text = scenario.prob_texts.get(key, "")
    if prob_text and rng.random() < 0.5:
        return f"die Wahrscheinlichkeit, dass {prob_text}"
    return f"\\({_LATEX[key]}\\)."


class MethodenBaumdiagrammCheck4Generator(TaskGenerator):
    generator_key = "stochastik.methoden.baumdiagramm_check4"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            case = sample_ab_case(rng=rng, scenario=scenario)
            probs = _extended_probs(case)

            # Je eine Wkt pro Gruppe zufällig wählen
            chosen_keys: list[str] = [
                rng.choice(_GROUP_EINZEL),
                rng.choice(_GROUP_SCHNITT),
                rng.choice(_GROUP_VEREINIGUNG),
                rng.choice(_GROUP_SPEZIAL),
            ]

            intro = (
                f"<p>{scenario.intro}</p>"
                f"<p>\\(A\\): {scenario.event_a}<br>"
                f"\\(B\\): {scenario.event_b}</p>"
                "<p>Bestimmen Sie anhand des Baumdiagramms "
                "auf 4 NKS gerundet</p>"
            )

            fragen: list[str] = []
            antworten: list[str] = []

            for key in chosen_keys:
                fragen.append(_frage_text(key, scenario, rng))
                antworten.append(
                    numerical(probs[key], tolerance=0.0001, decimals=4)
                )

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=fragen,
                    antworten=antworten,
                    visual=_build_tree_visual(case),
                )
            )

        return tasks
