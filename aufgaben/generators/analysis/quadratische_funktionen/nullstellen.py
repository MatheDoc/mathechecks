"""Generatoren 04–06 – Nullstellen (pq-Formel, faktorisiert, SPF).

04  NF ax²+bx+c=0 – pq-Formel (a=1 und a≠1; D>0, D=0, D<0)
05  FF f(x)=a(x-x₁)(x-x₂) – NS ablesen
06  SPF f(x)=a(x-d)²+e – NS über Umstellung

Einheitliches Format:
- Aufgabentext: "Bestimmen Sie die Nullstellen der Funktion $ f(x) = ... $"
- Immer 2 Antwortfelder (x₁ und x₂)
- Hinweise je nach Fallanzahl
"""

from __future__ import annotations

import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc, mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    A_VALUES,
    A_VALUES_INT,
    display_eq,
    ff_latex,
    fmt,
    nf_latex,
    spf_latex,
)


# ---------------------------------------------------------------------------
# Gemeinsamer Hinweistext
# ---------------------------------------------------------------------------

_HINT = (
    "Zwei Nullstellen: in aufsteigender Reihenfolge eingeben. "
    "Doppelte Nullstelle: gleichen Wert in beide Felder eintragen. "
    "Keine reelle Nullstelle: jeweils 0 eintragen und als Antwort "
    "keine Nullstelle angeben."
)

_FRAGEN = ["$ x_1 = $", "$ x_2 = $"]


def _build_task(eq_latex: str, case: str,
                x_lo: float | None, x_hi: float | None) -> Task:
    """Erzeugt eine einheitliche Nullstellen-Aufgabe."""
    einleitung = (
        f"Bestimmen Sie die Nullstellen der Funktion"
        f"{display_eq(eq_latex)}"
        f"{_HINT}"
    )

    if case == "neg":
        antworten = ["---", "---"]
    else:
        antworten = [
            numerical_analysis_calc(x_lo),
            numerical_analysis_calc(x_hi),
        ]

    return Task(einleitung=einleitung, fragen=list(_FRAGEN), antworten=antworten)


# ===================================================================
# Check 04 – Nullstellen mit pq-Formel (auch a ≠ 1)
# ===================================================================

_A_PQ = [1, 1, 1, 2, 3, -1, -2]  # Gewichtung: a=1 häufiger


class NullstellenPqFormelGenerator(TaskGenerator):
    """NF ax²+bx+c=0, pq-Formel. Mischung a=1 und a≠1."""

    generator_key = "analysis.quadratische_funktionen.nullstellen_pq_formel"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float, str]] = set()

        case_pool = ["pos"] * 14 + ["zero"] * 3 + ["neg"] * 3

        while len(tasks) < count:
            case = rng.choice(case_pool)
            a = rng.choice(_A_PQ)

            if case == "pos":
                x1 = rng.randint(-8, 8)
                x2 = rng.randint(-8, 8)
                if x1 == x2:
                    continue
                b = -a * (x1 + x2)
                c = a * x1 * x2
            elif case == "zero":
                x0 = rng.randint(-6, 6)
                b = -2 * a * x0
                c = a * x0 * x0
                x1 = x2 = x0
            else:
                # D < 0 – keine reellen NS
                p = rng.randint(-6, 6)
                min_q = int(p**2 / 4) + 1
                q = rng.randint(min_q, min_q + 5)
                b = a * p
                c = a * q
                x1 = x2 = None  # type: ignore[assignment]

            if abs(b) > 20 or abs(c) > 40:
                continue
            key = (float(a), float(b), float(c), case)
            if key in used:
                continue
            used.add(key)

            eq = nf_latex(float(a), float(b), float(c))

            if case == "neg":
                tasks.append(_build_task(eq, case, None, None))
            elif case == "zero":
                tasks.append(_build_task(eq, case, float(x1), float(x2)))
            else:
                x_lo = float(min(x1, x2))
                x_hi = float(max(x1, x2))
                tasks.append(_build_task(eq, case, x_lo, x_hi))

        return tasks


# ===================================================================
# Check 05 – Nullstellen faktorisierte Form
# ===================================================================

class NullstellenFaktorisiertGenerator(TaskGenerator):
    """f(x)=a(x-x₁)(x-x₂) – Nullstellen ablesen."""

    generator_key = "analysis.quadratische_funktionen.nullstellen_faktorisiert"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, int, int]] = set()

        while len(tasks) < count:
            a = rng.choice(A_VALUES_INT)
            x1 = rng.randint(-8, 8)
            x2 = rng.randint(-8, 8)
            if x1 == x2:
                continue
            key = (float(a), x1, x2)
            if key in used:
                continue
            used.add(key)

            x_lo = float(min(x1, x2))
            x_hi = float(max(x1, x2))
            eq = ff_latex(float(a), float(x1), float(x2))

            tasks.append(_build_task(eq, "pos", x_lo, x_hi))

        return tasks


# ===================================================================
# Check 06 – Nullstellen Scheitelpunktform
# ===================================================================

class NullstellenScheitelpunktformGenerator(TaskGenerator):
    """f(x)=a(x-d)²+e → Nullstellen berechnen."""

    generator_key = "analysis.quadratische_funktionen.nullstellen_scheitelpunktform"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float]] = set()

        case_pool = ["two"] * 14 + ["one"] * 3 + ["none"] * 3

        while len(tasks) < count:
            case = rng.choice(case_pool)
            a = rng.choice(A_VALUES)
            d = rng.randint(-4, 4)

            if case == "two":
                k = rng.randint(1, 5)
                e = -a * k**2
            elif case == "one":
                e = 0.0
            else:
                k = rng.randint(1, 5)
                e = a * k**2

            if abs(e) > 30:
                continue
            key = (a, float(d), float(e))
            if key in used:
                continue
            used.add(key)

            eq = spf_latex(a, float(d), float(e))

            if case == "none":
                tasks.append(_build_task(eq, "neg", None, None))
            elif case == "one":
                tasks.append(_build_task(eq, "zero", float(d), float(d)))
            else:
                sq = math.sqrt(abs(e / a))
                ns1 = d - sq
                ns2 = d + sq
                tasks.append(_build_task(eq, "pos", min(ns1, ns2), max(ns1, ns2)))

        return tasks
