"""Wahrscheinlichkeiten ohne Struktur berechnen - 3 gegebene Wkt, ohne Info zur stoch. Unabhängigkeit.

Szenario: Drei von {P(A), P(B), P(A∩B), P(A∩B)} sind bekannt.
A und B können unabhängig oder abhängig sein (kein Hinweis in der Aufgabe).
Keine VFT, kein Baumdiagramm.

Es werden genau 7 Teilaufgaben gestellt:
  1-6: Je eine Wahrscheinlichkeit aus den Gruppen
       EINZEL, SCHNITT, VEREINIGUNG, COND_A, COND_B, SPEZIAL
  7:   MC-Frage zur stochastischen Unabhängigkeit
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import (
    extended_probs,
    sample_ab_case,
    sample_ab_case_independent,
)
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


# ---------------------------------------------------------------------------

_GROUP_EINZEL      = ["pa", "pna", "pb", "pnb"]
_GROUP_SCHNITT     = ["pab", "panb", "pnab", "pnanb"]
_GROUP_VEREINIGUNG = ["paub", "paunb", "pnaub", "pnaunb"]
_GROUP_SPEZIAL     = ["symdiff", "diag_sum", "trivial_0", "trivial_1"]
_GROUP_COND_A      = ["pba", "pnba", "pbna", "pnbna"]
_GROUP_COND_B      = ["pab_c", "pnab_c", "panb_c", "pnanb_c"]

# Mögliche 3-Anker aus {pa, pb, pab, paub}.
# Da paub = pa + pb - pab, bestimmt jede Kombination von 3 die vierte eindeutig.
_ANCHOR3_OPTS = [
    ("pa", "pb", "pab"),
    ("pa", "pb", "paub"),
    ("pa", "pab", "paub"),
    ("pb", "pab", "paub"),
]


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


# ---------------------------------------------------------------------------

def _pct_str(value: float) -> str:
    """Wert als Prozentzahl mit deutschem Komma, z. B. 0.69 -> '69%', 0.084 -> '8,4%'."""
    pct = value * 100
    s = f"{pct:.4f}".rstrip("0").rstrip(".")
    return s.replace(".", ",") + "%"


def _dec_str(value: float) -> str:
    """Wert als Dezimalzahl mit deutschem Komma, z. B. 0.6348 -> '0,6348'."""
    s = f"{value:.4f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def _format_given(key: str, value: float, scenario, rng: random.Random) -> str:
    """Gibt die Formulierung für einen bekannten Wert zurück: textlich oder symbolisch."""
    prob_text = scenario.prob_texts.get(key, "")
    if prob_text and rng.random() < 0.5:
        return f"die Wahrscheinlichkeit, dass {prob_text}, {_pct_str(value)} beträgt"
    return f"$ {_LATEX[key]} $$ = $$ {_dec_str(value)} $"


def _frage_text(key: str, scenario, rng: random.Random) -> str:
    """Fragetext: Spezial-Wkt immer LaTeX; alle anderen 50/50 Text/LaTeX."""
    if key in _SPEZIAL_LABELS:
        return f"${rng.choice(_SPEZIAL_LABELS[key])}$."
    prob_text = scenario.prob_texts.get(key, "")
    if prob_text and rng.random() < 0.5:
        return f"die Wahrscheinlichkeit, dass {prob_text}"
    return f"${_LATEX[key]}$."


# ---------------------------------------------------------------------------

class OhneStrukturOhneInfoUnabhGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.ohneStruktur_ohneInfoUnabh"

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

            # 3 gegebene Wahrscheinlichkeiten aus {pa, pb, pab, paub}
            anchor_keys = rng.choice(_ANCHOR3_OPTS)
            g0 = _format_given(anchor_keys[0], probs[anchor_keys[0]], scenario, rng)
            g1 = _format_given(anchor_keys[1], probs[anchor_keys[1]], scenario, rng)
            g2 = _format_given(anchor_keys[2], probs[anchor_keys[2]], scenario, rng)
            given_text = f"{g0}, dass {g1} und dass {g2}"

            # 6 Wahrscheinlichkeitsfragen
            chosen_keys: list[str] = [
                rng.choice(_GROUP_EINZEL),
                rng.choice(_GROUP_SCHNITT),
                rng.choice(_GROUP_VEREINIGUNG),
                rng.choice(_GROUP_COND_A),
                rng.choice(_GROUP_COND_B),
                rng.choice(_GROUP_SPEZIAL),
            ]

            # MC-Frage zur stochastischen Unabhängigkeit
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

            einleitung = (
                f"<p>{scenario.intro}</p>"
                f"<p>$A$: {scenario.event_a}<br>"
                f"$B$: {scenario.event_b}</p>"
                f"<p>Es ist bekannt, dass {given_text}.</p>"
                "<p>Berechnen Sie (auf 4 NKS gerundet)</p>"
            )

            fragen = [_frage_text(k, scenario, rng) for k in chosen_keys]
            fragen.append(f"Überprüfen Sie die folgende Behauptung: {claim_text}")

            antworten = [
                numerical_stochastik_calc(probs[k])
                for k in chosen_keys
            ]
            antworten.append(mc_answer)

            tasks.append(Task(einleitung=einleitung, fragen=fragen, antworten=antworten))

        return tasks

