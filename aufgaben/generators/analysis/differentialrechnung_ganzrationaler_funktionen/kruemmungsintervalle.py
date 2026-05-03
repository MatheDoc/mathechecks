"""Generator fuer Check 10 - Einfache Kruemmungsintervalle bestimmen."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import (
    interval_bound_analysis,
    interval_bound_neg_inf,
    interval_bound_pos_inf,
    numerical_opt_none,
)
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.extrem_monotonie_shared import (
    SimpleInflectionCurvatureCase,
    build_inflection_function_intro,
    sample_simple_inflection_curvature_case,
)


class KruemmungsintervalleGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.kruemmungsintervalle"

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
                raise ValueError("Konnte nicht genug einfache Kruemmungs-Aufgaben erzeugen.")

        return tasks


def _balanced_degrees(count: int) -> list[int]:
    return [3 if index % 2 == 0 else 4 for index in range(count)]


def _build_task(case: SimpleInflectionCurvatureCase) -> Task:
    return Task(
        einleitung=build_inflection_function_intro(case) + " Bestimmen Sie",
        fragen=[
            "die Intervalle, in denen $f$ linksgekrümmt bzw. konvex ist.",
            "die Intervalle, in denen $f$ rechtsgekrümmt bzw. konkav ist.",
        ],
        antworten=[
            _interval_slot_answer(case.left_curved_intervals),
            _interval_slot_answer(case.right_curved_intervals),
        ],
    )


def _interval_slot_answer(intervals: tuple[tuple[float | None, float | None], ...]) -> str:
    entries: list[str] = []
    sorted_intervals = tuple(intervals)
    for index in range(2):
        label = index + 1
        interval_bounds = sorted_intervals[index] if index < len(sorted_intervals) else None
        entries.append(_single_interval_answer(label, interval_bounds))
    return " $\\quad$ ".join(entries)


def _single_interval_answer(
    label: int,
    interval_bounds: tuple[float | None, float | None] | None,
) -> str:
    if interval_bounds is None:
        return (
            f"$I_{label}=($"
            f"{numerical_opt_none()}"
            f"$; $"
            f"{numerical_opt_none()}"
            f"$)$"
        )

    left, right = interval_bounds

    if left is None and right is None:
        return (
            f"$I_{label}=($"
            f"{interval_bound_neg_inf()}"
            f"$; $"
            f"{interval_bound_pos_inf()}"
            f"$)$"
        )

    if left is None:
        return (
            f"$I_{label}=($"
            f"{interval_bound_neg_inf()}"
            f"$; $"
            f"{interval_bound_analysis(right)}"
            f"$)$"
        )

    if right is None:
        return (
            f"$I_{label}=($"
            f"{interval_bound_analysis(left)}"
            f"$; $"
            f"{interval_bound_pos_inf()}"
            f"$)$"
        )

    return (
        f"$I_{label}=($"
        f"{interval_bound_analysis(left)}"
        f"$; $"
        f"{interval_bound_analysis(right)}"
        f"$)$"
    )