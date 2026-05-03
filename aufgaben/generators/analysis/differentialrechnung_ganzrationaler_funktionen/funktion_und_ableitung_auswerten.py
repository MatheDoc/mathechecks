"""Generator für Check 03 – Funktion und Ableitung auswerten."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    align_equations,
    fmt,
    point_answer,
    polynomial_latex,
    sample_controlled_cubic,
    sample_centered_quadratic,
)


CUBIC_LEADING_SEQUENCE = (0.5, -0.5, 1.0, -1.0)


class FunktionUndAbleitungAuswertenGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.funktion_und_ableitung_auswerten"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[str, tuple[float, ...], tuple[int, ...]]] = set()

        while len(tasks) < count:
            try:
                if len(tasks) % 2 == 0:
                    task, key = _build_quadratic_task(rng)
                else:
                    cubic_index = len(tasks) // 2
                    preferred_a3 = CUBIC_LEADING_SEQUENCE[cubic_index % len(CUBIC_LEADING_SEQUENCE)]
                    task, key = _build_cubic_task(rng, preferred_a3=preferred_a3)
            except ValueError:
                continue

            if key in used:
                continue
            used.add(key)
            tasks.append(task)

        return tasks


def _build_quadratic_task(rng: random.Random) -> tuple[Task, tuple[str, tuple[float, ...], tuple[int, ...]]]:
    case, center, distance = sample_centered_quadratic(rng)
    derivative = case.derivative(1)
    question_data = _sample_quadratic_question_data(rng, center, int(distance))
    if question_data is None:
        raise ValueError("Konnte keine quadratische Aufgabenvariante erzeugen.")

    x_fun, x_tangent, x_slope, x_eval, x_point, pair_offset = question_data
    x_left = center - pair_offset
    x_right = center + pair_offset
    if max(
        abs(case.evaluate(x_value))
        for x_value in [x_fun, x_tangent, x_eval, x_point, x_left, x_right]
    ) > 24.0:
        raise ValueError("Quadratische Aufgabe außerhalb des Wertebereichs.")

    y_pair = case.evaluate(x_left)
    point_y = case.evaluate(x_point)
    derivative_latex = polynomial_latex(derivative, name="f'")
    task = Task(
        einleitung=(
            "Gegeben ist die Funktion $ f $ mit\n\n"
            f"{align_equations([polynomial_latex(case), derivative_latex])}\n\n"
            "Berechnen Sie."
        ),
        fragen=[
            f"den Funktionswert von $ f $ an der Stelle $ x={fmt(x_fun)} $.",
            f"alle Stellen $ x $, an denen $ f $ den Wert $ y={fmt(y_pair)} $ hat. Geben Sie die Lösungen in aufsteigender Reihenfolge an.",
            f"die Steigung der Tangente an den Graphen von $ f $ an der Stelle $ x={fmt(x_tangent)} $.",
            f"die Stelle $ x $, an der $ f'(x)={fmt(derivative.evaluate(x_slope))} $ gilt.",
            f"den Wert der Ableitung an der Stelle $ x={fmt(x_eval)} $.",
            f"den Punkt des Graphen von $ f $, in dem die Tangente die Steigung $ m={fmt(derivative.evaluate(x_point))} $ hat.",
        ],
        antworten=[
            f"$ f({fmt(x_fun)}) = ${numerical_analysis_calc(case.evaluate(x_fun))}",
            (
                f"$ x_1 = ${numerical_analysis_calc(x_left)}"
                f"\n$ x_2 = ${numerical_analysis_calc(x_right)}"
            ),
            f"$ m = ${numerical_analysis_calc(derivative.evaluate(x_tangent))}",
            f"$ x = ${numerical_analysis_calc(x_slope)}",
            f"$ f'({fmt(x_eval)}) = ${numerical_analysis_calc(derivative.evaluate(x_eval))}",
            point_answer(x_point, point_y),
        ],
    )
    key = ("quadratic", case.signature(), (x_fun, x_tangent, x_slope, x_eval, x_point, pair_offset))
    return task, key


def _build_cubic_task(
    rng: random.Random,
    *,
    preferred_a3: float,
) -> tuple[Task, tuple[str, tuple[float, ...], tuple[int, ...]]]:
    case, center, _root_distance, _slope_shift = sample_controlled_cubic(rng, preferred_a3=preferred_a3)
    derivative = case.derivative(1)
    question_data = _sample_cubic_question_data(rng, case, derivative, center)
    if question_data is None:
        raise ValueError("Konnte keine kubische Aufgabenvariante erzeugen.")

    x_fun, y_target, y_solution_xs, x_tangent, q4_xs, x_eval, q6_xs = question_data
    relevant_xs = [x_fun, x_tangent, x_eval, *y_solution_xs, *q4_xs, *q6_xs]
    if max(abs(case.evaluate(x_value)) for x_value in relevant_xs) > 30.0:
        raise ValueError("Kubische Aufgabe außerhalb des Wertebereichs.")

    q4_target = derivative.evaluate(q4_xs[0])
    q6_target = derivative.evaluate(q6_xs[0])
    point_answers = [(x_value, case.evaluate(x_value)) for x_value in q6_xs]
    derivative_latex = polynomial_latex(derivative, name="f'")
    y_question = (
        f"alle Stellen $ x $, an denen $ f $ den Wert $ y={fmt(y_target)} $ hat."
        if len(y_solution_xs) == 1
        else f"alle Stellen $ x $, an denen $ f $ den Wert $ y={fmt(y_target)} $ hat. Geben Sie die Lösungen in aufsteigender Reihenfolge an."
    )
    task = Task(
        einleitung=(
            "Gegeben ist die Funktion $ f $ mit\n\n"
            f"{align_equations([polynomial_latex(case), derivative_latex])}\n\n"
            "Berechnen Sie."
        ),
        fragen=[
            f"den Funktionswert von $ f $ an der Stelle $ x={fmt(x_fun)} $.",
            y_question,
            f"die Steigung der Tangente an den Graphen von $ f $ an der Stelle $ x={fmt(x_tangent)} $.",
            f"alle Stellen $ x $, an denen $ f'(x)={fmt(q4_target)} $ gilt. Geben Sie die Lösungen in aufsteigender Reihenfolge an.",
            f"den Wert der Ableitung an der Stelle $ x={fmt(x_eval)} $.",
            f"die Punkte des Graphen von $ f $, in denen die Tangente die Steigung $ m={fmt(q6_target)} $ hat. Geben Sie die Punkte in aufsteigender Reihenfolge der $x$-Werte an.",
        ],
        antworten=[
            f"$ f({fmt(x_fun)}) = ${numerical_analysis_calc(case.evaluate(x_fun))}",
            _x_solution_answer(y_solution_xs),
            f"$ m = ${numerical_analysis_calc(derivative.evaluate(x_tangent))}",
            _x_solution_answer(q4_xs),
            f"$ f'({fmt(x_eval)}) = ${numerical_analysis_calc(derivative.evaluate(x_eval))}",
            _point_solution_answer(point_answers),
        ],
    )
    key = (
        "cubic",
        case.signature(),
        (x_fun, *y_solution_xs, x_tangent, *q4_xs, x_eval, *q6_xs),
    )
    return task, key


def _sample_quadratic_question_data(
    rng: random.Random,
    center: float,
    root_distance: int,
) -> tuple[int, int, int, int, int, int] | None:
    candidate_offsets = [-3, -2, -1, 1, 2, 3]
    pair_offsets = [offset for offset in (1, 2, 3) if offset != root_distance]
    if len(pair_offsets) < 1:
        return None
    sampled_offsets = rng.sample(candidate_offsets, 5)
    pair_offset = rng.choice(pair_offsets)
    return (
        int(center + sampled_offsets[0]),
        int(center + sampled_offsets[1]),
        int(center + sampled_offsets[2]),
        int(center + sampled_offsets[3]),
        int(center + sampled_offsets[4]),
        pair_offset,
    )


def _sample_cubic_question_data(
    rng: random.Random,
    case,
    derivative,
    center: int,
) -> tuple[int, float, tuple[int, ...], int, tuple[int, int], int, tuple[int, int]] | None:
    domain = tuple(range(-3, 4))
    available_offsets = [offset for offset in (1, 2, 3) if -3 <= center - offset and center + offset <= 3]
    if len(available_offsets) < 2:
        return None

    grouped_values: dict[float, list[int]] = {}
    for x_value in domain:
        y_value = case.evaluate(x_value)
        grouped_values.setdefault(y_value, []).append(x_value)

    multi_candidates = [
        (y_value, tuple(sorted(xs)))
        for y_value, xs in grouped_values.items()
        if 2 <= len(xs) <= 3
    ]
    single_candidates = [
        (y_value, (xs[0],))
        for y_value, xs in grouped_values.items()
        if len(xs) == 1
    ]
    if multi_candidates:
        y_target, y_solution_xs = rng.choice(multi_candidates)
    elif single_candidates:
        y_target, y_solution_xs = rng.choice(single_candidates)
    else:
        return None

    q4_offset, q6_offset = rng.sample(available_offsets, 2)
    q4_xs = (center - q4_offset, center + q4_offset)
    q6_xs = (center - q6_offset, center + q6_offset)

    free_xs = [x_value for x_value in domain if x_value not in set(q4_xs) | set(q6_xs)]
    if len(free_xs) < 3:
        return None

    x_fun, x_tangent, x_eval = rng.sample(free_xs, 3)
    if len({derivative.evaluate(q4_xs[0]), derivative.evaluate(q6_xs[0])}) < 2:
        return None

    return (
        x_fun,
        y_target,
        y_solution_xs,
        x_tangent,
        q4_xs,
        x_eval,
        q6_xs,
    )


def _x_solution_answer(x_values: tuple[int, ...]) -> str:
    if len(x_values) == 1:
        return f"$ x = ${numerical_analysis_calc(x_values[0])}"
    return "\n".join(
        f"$ x_{index} = ${numerical_analysis_calc(x_value)}"
        for index, x_value in enumerate(x_values, start=1)
    )


def _point_solution_answer(points: list[tuple[int, float]]) -> str:
    if len(points) == 1:
        x_value, y_value = points[0]
        return point_answer(x_value, y_value)
    return "\n".join(
        f"$ x_{index} = ${numerical_analysis_calc(x_value)}, $ y_{index} = ${numerical_analysis_calc(y_value)}"
        for index, (x_value, y_value) in enumerate(points, start=1)
    )