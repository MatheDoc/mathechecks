"""Generator für Check 02 – Ableitungen ganzrationaler Funktionen bestimmen."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    align_equations,
    polynomial_latex,
    polynomial_input_answer,
    sample_constant_case,
    sample_expansion_product_case,
    sample_normal_polynomial,
    sample_simple_product_case,
)


class AbleitungenBestimmenGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.ableitungen_bestimmen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[tuple[float, ...], ...]] = set()

        while len(tasks) < count:
            const_case = sample_constant_case(rng)
            linear_case = sample_normal_polynomial(rng, degree=1, value_bound=18.0)
            quadratic_case = sample_normal_polynomial(rng, degree=2, value_bound=24.0)
            cubic_case = sample_normal_polynomial(rng, degree=3, value_bound=32.0)
            simple_expression, simple_product_case = sample_simple_product_case(rng, name="p")
            higher_expression, higher_product_case = sample_expansion_product_case(rng, name="q")

            key = (
                const_case.signature(),
                linear_case.signature(),
                quadratic_case.signature(),
                cubic_case.signature(),
                simple_product_case.signature(),
                higher_product_case.signature(),
            )
            if key in used:
                continue
            used.add(key)

            expressions = [
                polynomial_latex(const_case, name="f"),
                polynomial_latex(linear_case, name="g"),
                polynomial_latex(quadratic_case, name="h"),
                polynomial_latex(cubic_case, name="k"),
                simple_expression,
                higher_expression,
            ]

            tasks.append(
                Task(
                    einleitung=(
                        "Gegeben:\n\n"
                        f"{align_equations(expressions)}\n\n"
                        "Bestimmen Sie die gefragten Ableitungen jeweils in Normalform."
                    ),
                    fragen=[
                        "die erste Ableitung $ f'(x) $.",
                        "die erste Ableitung $ g'(x) $.",
                        "die erste Ableitung $ h'(x) $.",
                        "die erste Ableitung $ k'(x) $.",
                        "die erste Ableitung $ p'(x) $.",
                        "die erste Ableitung $ q'(x) $.",
                    ],
                    antworten=[
                        polynomial_input_answer(const_case.derivative(1), name="f'"),
                        polynomial_input_answer(linear_case.derivative(1), name="g'"),
                        polynomial_input_answer(quadratic_case.derivative(1), name="h'"),
                        polynomial_input_answer(cubic_case.derivative(1), name="k'"),
                        polynomial_input_answer(simple_product_case.derivative(1), name="p'"),
                        polynomial_input_answer(higher_product_case.derivative(1), name="q'"),
                    ],
                )
            )

        return tasks