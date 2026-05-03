"""Generator fuer Check 11 - Spezialfaelle bei Wendestellen und Kruemmung."""

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
    SimpleInflectionCurvatureCase,
    build_inflection_function_intro,
    sample_special_inflection_curvature_case,
)


class WendestellenKruemmungSpezialfaelleGenerator(TaskGenerator):
    generator_key = (
        "analysis.differentialrechnung_ganzrationaler_funktionen."
        "wendestellen_kruemmung_spezialfaelle"
    )

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, ...]] = set()

        for family in _balanced_families(count):
            for _ in range(900):
                case = sample_special_inflection_curvature_case(rng, family=family)
                if case.signature() in used:
                    continue
                used.add(case.signature())
                tasks.append(_build_task(case))
                break
            else:
                raise ValueError("Konnte nicht genug Spezialfall-Aufgaben fuer Wendestellen erzeugen.")

        return tasks


def _balanced_families(count: int) -> list[str]:
    families = ("quartic_flat", "quintic_triple", "quintic_mixed")
    return [families[index % len(families)] for index in range(count)]


def _build_task(case: SimpleInflectionCurvatureCase) -> Task:
    return Task(
        einleitung=build_inflection_function_intro(case) + " Bestimmen Sie",
        fragen=[
            "die x-Werte aller Wendestellen.",
            "das Intervall, in dem $f$ linksgekrümmt bzw. konvex ist.",
            "das Intervall, in dem $f$ rechtsgekrümmt bzw. konkav ist.",
        ],
        antworten=[
            _inflection_answer(case.inflection_xs),
            _interval_answer(case.left_curved_intervals),
            _interval_answer(case.right_curved_intervals),
        ],
    )


def _inflection_answer(values: tuple[float, ...]) -> str:
    if len(values) > 1:
        raise ValueError("Dieser Check erwartet hoechstens eine echte Wendestelle.")
    placeholder = numerical_opt_none() if not values else numerical_opt_analysis(values[0])
    return f"$x_W=${placeholder}"


def _interval_answer(intervals: tuple[tuple[float | None, float | None], ...]) -> str:
    if len(intervals) > 1:
        raise ValueError("Dieser Check erwartet hoechstens ein zusammenhaengendes Kruemmungsintervall pro Richtung.")
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