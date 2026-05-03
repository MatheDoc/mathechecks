"""Generator fuer Check 08 - Spezialfaelle bei Extremstellen und Monotonie."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import (
    interval_bound_analysis,
    interval_bound_neg_inf,
    interval_bound_pos_inf,
    numerical_opt_analysis,
    numerical_opt_none,
)
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.extrem_monotonie_shared import (
    SimpleExtremMonotonicityCase,
    build_simple_function_intro,
    sample_special_extrem_monotonicity_case,
)


class ExtremstellenMonotonieSpezialfaelleGenerator(TaskGenerator):
    generator_key = (
        "analysis.differentialrechnung_ganzrationaler_funktionen."
        "extremstellen_monotonie_spezialfaelle"
    )

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, ...]] = set()

        for family in _balanced_families(count):
            for _ in range(900):
                case = sample_special_extrem_monotonicity_case(rng, family=family)
                if case.signature() in used:
                    continue
                used.add(case.signature())
                tasks.append(_build_task(case))
                break
            else:
                raise ValueError("Konnte nicht genug Spezialfall-Aufgaben erzeugen.")

        return tasks


def _balanced_families(count: int) -> list[str]:
    families = ("cubic_saddle", "quartic_triple", "quartic_mixed")
    return [families[index % len(families)] for index in range(count)]


def _build_task(case: SimpleExtremMonotonicityCase) -> Task:
    return Task(
        einleitung=build_simple_function_intro(case) + " Bestimmen Sie",
        fragen=[
            "die x-Werte aller Hochpunkte.",
            "die x-Werte aller Tiefpunkte.",
            "die x-Werte aller Sattelpunkte.",
            "das Intervall, in dem $f$ streng monoton wachsend ist.",
            "das Intervall, in dem $f$ streng monoton fallend ist.",
        ],
        antworten=[
            _x_value_answer(case.high_x, label="H"),
            _x_value_answer(case.low_x, label="T"),
            _x_value_answer(case.saddle_x, label="S"),
            _interval_answer(case.increasing_intervals),
            _interval_answer(case.decreasing_intervals),
        ],
    )


def _x_value_answer(value: float | None, *, label: str) -> str:
    placeholder = numerical_opt_none() if value is None else numerical_opt_analysis(value)
    return f"$x_{label}=${placeholder}"


def _interval_answer(intervals: tuple[tuple[float | None, float | None], ...]) -> str:
    if len(intervals) > 1:
        raise ValueError("Dieser Check erwartet hoechstens ein zusammenhaengendes Monotonieintervall pro Richtung.")
    interval_bounds = intervals[0] if intervals else None
    return _render_interval(interval_bounds)


def _render_interval(interval_bounds: tuple[float | None, float | None] | None) -> str:
    if interval_bounds is None:
        return (
            f"$I=($"
            f"{numerical_opt_none()}"
            f"$; $"
            f"{numerical_opt_none()}"
            f"$)$"
        )

    left, right = interval_bounds

    if left is None and right is None:
        return (
            f"$I=($"
            f"{interval_bound_neg_inf()}"
            f"$; $"
            f"{interval_bound_pos_inf()}"
            f"$)$"
        )

    if left is None:
        return (
            f"$I=($"
            f"{interval_bound_neg_inf()}"
            f"$; $"
            f"{interval_bound_analysis(right)}"
            f"$)$"
        )

    if right is None:
        return (
            f"$I=($"
            f"{interval_bound_analysis(left)}"
            f"$; $"
            f"{interval_bound_pos_inf()}"
            f"$)$"
        )

    return (
        f"$I=($"
        f"{interval_bound_analysis(left)}"
        f"$; $"
        f"{interval_bound_analysis(right)}"
        f"$)$"
    )