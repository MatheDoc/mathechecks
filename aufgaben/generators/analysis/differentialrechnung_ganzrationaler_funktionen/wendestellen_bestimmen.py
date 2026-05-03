"""Generator fuer Check 09 - Einfache Wendestellen bestimmen."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical_opt_analysis, numerical_opt_none
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.extrem_monotonie_shared import (
    SimpleInflectionCurvatureCase,
    build_inflection_function_intro,
    sample_simple_inflection_curvature_case,
)


_INFLECTION_OPTIONS = ["maximale Steigung", "minimale Steigung"]


class WendestellenBestimmenGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.wendestellen_bestimmen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, ...]] = set()

        for degree in _balanced_degrees(count):
            for _ in range(900):
                case = sample_simple_inflection_curvature_case(rng, degree=degree)
                if case.signature() in used:
                    continue
                used.add(case.signature())
                tasks.append(_build_task(case))
                break
            else:
                raise ValueError("Konnte nicht genug einfache Wendestellen-Aufgaben erzeugen.")

        return tasks


def _balanced_degrees(count: int) -> list[int]:
    return [3 if index % 2 == 0 else 4 for index in range(count)]


def _build_task(case: SimpleInflectionCurvatureCase) -> Task:
    return Task(
        einleitung=build_inflection_function_intro(case) + " Bestimmen Sie",
        fragen=[
            "die x-Werte $x_1$ und $x_2$, die die notwendige Bedingung für Wendestellen erfüllen.",
            "die Werte $f'''(x_1)$ und $f'''(x_2)$ für die Prüfung der hinreichenden Bedingung und folgern Sie jeweils, ob dort eine maximale oder minimale Steigung vorliegt.",
            "die x-Werte aller Wendestellen.",
        ],
        antworten=[
            _x_slot_answer(case.candidate_xs, slot_count=2),
            _third_derivative_and_kind_answer(case),
            _inflection_slot_answer(case.inflection_xs, slot_count=2),
        ],
    )


def _x_slot_answer(values: tuple[float, ...], *, slot_count: int) -> str:
    entries: list[str] = []
    sorted_values = tuple(sorted(values))

    for index in range(slot_count):
        label = index + 1
        if index < len(sorted_values):
            placeholder = numerical_opt_analysis(sorted_values[index])
        else:
            placeholder = numerical_opt_none()
        prefix = "$ " if index == 0 else "$\\quad "
        entries.append(f"{prefix}x_{label} = ${placeholder}")

    return " ".join(entries)


def _third_derivative_and_kind_answer(case: SimpleInflectionCurvatureCase) -> str:
    third_derivative = case.function_case.derivative(3)
    entries: list[str] = []

    for index in range(2):
        label = index + 1
        if index < len(case.candidate_xs):
            x_value = case.candidate_xs[index]
            third_value = third_derivative.evaluate(x_value)
            kind = "minimale Steigung" if third_value > 0 else "maximale Steigung"
            third_placeholder = numerical_opt_analysis(third_value)
            kind_placeholder = mc(_INFLECTION_OPTIONS, _INFLECTION_OPTIONS.index(kind))
            entries.append(
                " ".join(
                    [
                        f"$f'''(x_{label})=${third_placeholder}",
                        f"$\\quad$ Art:" + kind_placeholder,
                    ]
                )
            )
        else:
            third_placeholder = numerical_opt_none()
            entries.append(f"$f'''(x_{label})=${third_placeholder}")

    return " $\\qquad$ ".join(entries)


def _inflection_slot_answer(values: tuple[float, ...], *, slot_count: int) -> str:
    entries: list[str] = []
    sorted_values = tuple(sorted(values))

    for index in range(slot_count):
        label = index + 1
        if index < len(sorted_values):
            placeholder = numerical_opt_analysis(sorted_values[index])
        else:
            placeholder = numerical_opt_none()
        prefix = "$ " if index == 0 else "$\\quad "
        entries.append(f"{prefix}x_{{W{label}}} = ${placeholder}")

    return " ".join(entries)