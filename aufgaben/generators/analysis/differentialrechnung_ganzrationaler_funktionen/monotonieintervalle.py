"""Generator fuer Check 07 - Einfache Monotonieintervalle bestimmen."""

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
    SimpleExtremMonotonicityCase,
    build_interval_input_note,
    build_simple_function_intro,
    interval_delimiters,
    sample_simple_extrem_monotonicity_case,
)


class MonotonieintervalleGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.monotonieintervalle"

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
                raise ValueError("Konnte nicht genug einfache Monotonie-Aufgaben erzeugen.")

        return tasks


def _balanced_degrees(count: int) -> list[int]:
    return [2 if index % 2 == 0 else 3 for index in range(count)]


def _build_task(case: SimpleExtremMonotonicityCase) -> Task:
    return Task(
        einleitung=build_simple_function_intro(case) + " " + build_interval_input_note() + " Bestimmen Sie",
        fragen=[
            "die Intervalle, in denen $f$ streng monoton fallend ist.",
            "die Intervalle, in denen $f$ streng monoton wachsend ist.",
        ],
        antworten=[
            _interval_slot_answer(case, case.decreasing_intervals),
            _interval_slot_answer(case, case.increasing_intervals),
        ],
    )


def _interval_slot_answer(
    case: SimpleExtremMonotonicityCase,
    intervals: tuple[tuple[float | None, float | None], ...],
) -> str:
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
    left_bracket, right_bracket = interval_delimiters(left, right)

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
            f"${right_bracket}$"
        )

    if right is None:
        return (
            f"$I_{label}={left_bracket}$"
            f"{interval_bound_analysis(left)}"
            f"$; $"
            f"{interval_bound_pos_inf()}"
            f"$)$"
        )

    return (
        f"$I_{label}={left_bracket}$"
        f"{interval_bound_analysis(left)}"
        f"$; $"
        f"{interval_bound_analysis(right)}"
        f"${right_bracket}$"
    )