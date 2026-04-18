"""Generator 08 – Darstellungsformen umwandeln.

NF→SPF, NF→FF, SPF→NF, FF→NF zufällig.
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    A_VALUES_INT,
    display_eq,
    ff_latex,
    ff_to_nf,
    fmt,
    nf_latex,
    nf_to_ff,
    nf_to_spf,
    sample_nf_nice,
    spf_latex,
    spf_to_nf,
)


class DarstellungsformenUmwandelnGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.darstellungsformen_umwandeln"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        variants = ["nf_to_spf", "nf_to_ff", "spf_to_nf", "ff_to_nf"]

        while len(tasks) < count:
            variant = rng.choice(variants)

            if variant == "nf_to_spf":
                task = self._nf_to_spf(rng)
            elif variant == "nf_to_ff":
                task = self._nf_to_ff(rng)
            elif variant == "spf_to_nf":
                task = self._spf_to_nf(rng)
            else:
                task = self._ff_to_nf(rng)

            if task is not None:
                tasks.append(task)

        return tasks

    def _nf_to_spf(self, rng: random.Random) -> Task:
        a, b, c, _, _ = sample_nf_nice(rng)
        eq = nf_latex(a, b, c)
        a2, d, e = nf_to_spf(a, b, c)
        return Task(
            einleitung=(
                f"Wandeln Sie in die Scheitelpunktform um:"
                f"{display_eq(eq)}"
                f"$ f(x) = a(x-d)^2+e $"
            ),
            fragen=["$ a = $", "$ d = $", "$ e = $"],
            antworten=[
                numerical_analysis_calc(a2),
                numerical_analysis_calc(d),
                numerical_analysis_calc(e),
            ],
        )

    def _nf_to_ff(self, rng: random.Random) -> Task:
        a, b, c, x1, x2 = sample_nf_nice(rng)
        eq = nf_latex(a, b, c)
        return Task(
            einleitung=(
                f"Wandeln Sie in die faktorisierte Form um:"
                f"{display_eq(eq)}"
                f"$ f(x) = a(x-x_1)(x-x_2) $ mit $ x_1 \\leq x_2 $"
            ),
            fragen=["$ a = $", "$ x_1 = $", "$ x_2 = $"],
            antworten=[
                numerical_analysis_calc(a),
                numerical_analysis_calc(x1),
                numerical_analysis_calc(x2),
            ],
        )

    def _spf_to_nf(self, rng: random.Random) -> Task:
        a = rng.choice(A_VALUES_INT)
        d = rng.randint(-4, 4)
        e = rng.randint(-6, 6)
        eq = spf_latex(float(a), float(d), float(e))
        a2, b, c = spf_to_nf(float(a), float(d), float(e))
        return Task(
            einleitung=(
                f"Wandeln Sie in die Normalform um:"
                f"{display_eq(eq)}"
                f"$ f(x) = ax^2+bx+c $"
            ),
            fragen=["$ a = $", "$ b = $", "$ c = $"],
            antworten=[
                numerical_analysis_calc(a2),
                numerical_analysis_calc(b),
                numerical_analysis_calc(c),
            ],
        )

    def _ff_to_nf(self, rng: random.Random) -> Task:
        a = rng.choice(A_VALUES_INT)
        x1 = rng.randint(-5, 5)
        x2 = rng.randint(-5, 5)
        while x1 == x2:
            x2 = rng.randint(-5, 5)
        eq = ff_latex(float(a), float(x1), float(x2))
        a2, b, c = ff_to_nf(float(a), float(x1), float(x2))
        return Task(
            einleitung=(
                f"Wandeln Sie in die Normalform um:"
                f"{display_eq(eq)}"
                f"$ f(x) = ax^2+bx+c $"
            ),
            fragen=["$ a = $", "$ b = $", "$ c = $"],
            antworten=[
                numerical_analysis_calc(a2),
                numerical_analysis_calc(b),
                numerical_analysis_calc(c),
            ],
        )
