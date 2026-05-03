"""Generator fuer Check 06 - Einfache Extrempunkte bestimmen."""

from __future__ import annotations

import random

from aufgaben.core.placeholders import mc, numerical_opt_analysis, numerical_opt_none
from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.extrem_monotonie_shared import (
    SimpleExtremMonotonicityCase,
    build_simple_function_intro,
    sample_simple_extrem_monotonicity_case,
)


_POINT_KIND_OPTIONS = ["Hochpunkt", "Tiefpunkt"]


class ExtremstellenBestimmenGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.extremstellen_bestimmen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, ...]] = set()

        for degree in _balanced_degrees(count):
            for _ in range(900):
                case = sample_simple_extrem_monotonicity_case(rng, degree=degree)
                if case.signature() in used:
                    continue
                used.add(case.signature())
                tasks.append(_build_task(case))
                break
            else:
                raise ValueError("Konnte nicht genug einfache Extrempunkt-Aufgaben erzeugen.")

        return tasks


def _balanced_degrees(count: int) -> list[int]:
    degrees = [2 if index % 2 == 0 else 3 for index in range(count)]
    return degrees


def _build_task(case: SimpleExtremMonotonicityCase) -> Task:
    return Task(
        einleitung=build_simple_function_intro(case) + " Bestimmen Sie",
        fragen=[
            "die x-Werte $x_1$ und $x_2$, die die notwendige Bedingung für Extremstellen erfüllen.",
            "die Werte $f''(x_1)$ und $f''(x_2)$ für die Prüfung der hinreichenden Bedingung und folgern Sie jeweils, ob dort ein Hochpunkt oder Tiefpunkt vorliegt.",
            "den Hochpunkt von $f$.",
            "den Tiefpunkt von $f$.",
        ],
        antworten=[
            _x_slot_answer(case.candidate_xs, slot_count=2),
            _second_derivative_and_kind_answer(case),
            _point_slot_answer(case.high_point, prefix="H"),
            _point_slot_answer(case.low_point, prefix="T"),
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


def _second_derivative_and_kind_answer(case: SimpleExtremMonotonicityCase) -> str:
    second_derivative = case.function_case.derivative(2)
    entries: list[str] = []

    for index in range(2):
        label = index + 1
        if index < len(case.candidate_xs):
            x_value = case.candidate_xs[index]
            second_value = second_derivative.evaluate(x_value)
            kind = "Hochpunkt" if second_value < 0 else "Tiefpunkt"
            second_placeholder = numerical_opt_analysis(second_value)
            kind_placeholder = mc(_POINT_KIND_OPTIONS, _POINT_KIND_OPTIONS.index(kind))
            entries.append(
                " ".join(
                    [
                        f"$f''(x_{label})=${second_placeholder}",
                        f"$\\quad$ Art:" + kind_placeholder,
                    ]
                )
            )
        else:
            second_placeholder = numerical_opt_none()
            entries.append(f"$f''(x_{label})=${second_placeholder}")

    return " $\\qquad$ ".join(entries)


def _point_slot_answer(point: tuple[float, float] | None, *, prefix: str) -> str:
    if point is None:
        x_placeholder = numerical_opt_none()
        y_placeholder = numerical_opt_none()
    else:
        x_placeholder = numerical_opt_analysis(point[0])
        y_placeholder = numerical_opt_analysis(point[1])

    return " ".join(
        [
            f"$x_{prefix}=${x_placeholder}",
            f"$\\quad y_{prefix}=${y_placeholder}",
        ]
    )