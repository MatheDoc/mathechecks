"""Generator für Check 04 - Graphische Deutung erster Ableitungen."""

from __future__ import annotations

import math
import random

from aufgaben.core.tolerances import axis_tick_step
from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    PolynomialCase,
    build_plotly_visual_from_cases,
    integrate_polynomial,
    multiply_polynomials,
    scale_polynomial,
)


_ROOT_VALUES = (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5)
_FUNCTION_DEGREES = (1, 2, 3)
_CONSTANT_LEVELS = (1.0, 1.5, 2.0, 2.5)
_LINEAR_LEADING_MAGNITUDES = (0.7, 0.9, 1.1)
_QUADRATIC_LEADING_MAGNITUDES = (0.45, 0.6, 0.75)
_UPPER_SHIFTS = (1.0, 2.0, 3.0)
_LOWER_SHIFTS = (-3.0, -2.0, -1.0)
_ANCHOR_X_VALUES = (-2.0, -1.0, 0.0, 1.0, 2.0)
_Y_FOCUS_X_VALUES = (-3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
_X_RANGE = (-3.5, 3.5)
_MAX_GRAPH_ABS = 24.0
_MIN_FUNCTION_SPAN = 2.6
_MIN_DERIVATIVE_SPAN = 1.5
_MIN_CONSTANT_LEVEL = 0.9
_MIN_ANCHOR_GAP = 0.8
_MAX_TOTAL_SPAN = 18.0
_MIN_PAIRWISE_AVG_DISTANCE = 1.7
_MIN_FUNCTION_MEAN_GAP = 2.4
_MIN_DERIVATIVE_MEAN_GAP = 0.8
_MIN_RELATIVE_TRACE_SPAN = 0.14
_MIN_DECOY_AVG_DISTANCE = 2.0
_MIN_DECOY_CLEAR_POINT_GAP = 0.8
_MIN_DECOY_CLEAR_POINT_COUNT = 11
_PLOT_LABELS = ("a", "b", "c", "d", "e")


class GraphischeDeutungAbleitungenGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.graphische_deutung_ableitungen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...], str, float, float]] = set()
        failed_samples = 0

        while len(tasks) < count:
            try:
                f_case, f_prime, g_case, g_prime, decoy_case, anchor = _sample_function_pair_task(rng)
            except ValueError:
                failed_samples += 1
                if failed_samples >= 40:
                    raise ValueError("Konnte nach mehreren Anläufen keine geeigneten Graphen für Check 04 erzeugen.")
                continue
            task, key = _build_task(rng, f_case, f_prime, g_case, g_prime, decoy_case, anchor)
            if key in used:
                continue
            failed_samples = 0
            used.add(key)
            tasks.append(task)

        return tasks


def _sample_function_pair_task(
    rng: random.Random,
) -> tuple[PolynomialCase, PolynomialCase, PolynomialCase, PolynomialCase, PolynomialCase, tuple[str, float, float]]:
    for _ in range(900):
        shared_root = rng.choice(_ROOT_VALUES)
        sign = rng.choice((-1.0, 1.0))
        degree_f = rng.choice(_FUNCTION_DEGREES)
        degree_g = rng.choice(_FUNCTION_DEGREES)

        if rng.choice((True, False)):
            y_shift_f = rng.choice(_UPPER_SHIFTS)
            y_shift_g = rng.choice(_LOWER_SHIFTS)
        else:
            y_shift_f = rng.choice(_LOWER_SHIFTS)
            y_shift_g = rng.choice(_UPPER_SHIFTS)

        f_prime = _sample_derivative_case(rng, degree_f, shared_root, sign)
        g_prime = _sample_derivative_case(rng, degree_g, shared_root, -sign)

        f_case = integrate_polynomial(f_prime, constant=y_shift_f)
        g_case = integrate_polynomial(g_prime, constant=y_shift_g)

        decoy_case = _sample_decoy_case(rng, shared_root, f_prime, g_prime)
        if decoy_case is None:
            continue

        if not _pair_is_usable(f_case, f_prime, g_case, g_prime, decoy_case):
            continue

        anchor = _choose_anchor(rng, f_case, f_prime, g_case, g_prime, decoy_case)
        if anchor is None:
            continue

        return f_case, f_prime, g_case, g_prime, decoy_case, anchor

    raise ValueError("Konnte keine geeigneten Graphen für Check 04 erzeugen.")


def _quadratic_from_roots(leading: float, root_a: float, root_b: float) -> PolynomialCase:
    return PolynomialCase(
        scale_polynomial(
            multiply_polynomials((1.0, -root_a), (1.0, -root_b)),
            leading,
        )
    )


def _linear_from_root(leading: float, root: float) -> PolynomialCase:
    return PolynomialCase((leading, -leading * root))


def _sample_derivative_case(
    rng: random.Random,
    function_degree: int,
    shared_root: float,
    preferred_sign: float,
) -> PolynomialCase:
    return _sample_polynomial_case(rng, function_degree - 1, shared_root, preferred_sign)


def _sample_polynomial_case(
    rng: random.Random,
    degree: int,
    shared_root: float,
    preferred_sign: float,
) -> PolynomialCase:
    sign = -1.0 if preferred_sign < 0 else 1.0

    if degree == 0:
        return PolynomialCase((sign * rng.choice(_CONSTANT_LEVELS),))

    if degree == 1:
        root = shared_root if rng.choice((True, False)) else rng.choice(_ROOT_VALUES)
        leading = sign * rng.choice(_LINEAR_LEADING_MAGNITUDES)
        return _linear_from_root(leading, root)

    if degree == 2:
        other_candidates = [value for value in _ROOT_VALUES if value != shared_root and abs(value - shared_root) >= 1.0]
        if not other_candidates:
            raise ValueError("Konnte keine Nullstellen für quadratische Ableitung wählen.")
        leading = sign * rng.choice(_QUADRATIC_LEADING_MAGNITUDES)
        if rng.choice((True, False)):
            return _quadratic_from_roots(leading, shared_root, shared_root)
        return _quadratic_from_roots(leading, shared_root, rng.choice(other_candidates))

    raise ValueError(f"Nicht unterstützter Grad: {degree}")


def _sample_decoy_case(
    rng: random.Random,
    shared_root: float,
    f_prime: PolynomialCase,
    g_prime: PolynomialCase,
) -> PolynomialCase | None:
    for _ in range(180):
        degree = rng.choice((0, 1, 2))
        preferred_sign = rng.choice((-1.0, 1.0))
        decoy_case = _sample_polynomial_case(rng, degree, shared_root, preferred_sign)

        if decoy_case.signature() in {f_prime.signature(), g_prime.signature()}:
            continue
        if not _derivative_case_is_clear(decoy_case):
            continue
        return decoy_case

    return None


def _pair_is_usable(
    f_case: PolynomialCase,
    f_prime: PolynomialCase,
    g_case: PolynomialCase,
    g_prime: PolynomialCase,
    decoy_case: PolynomialCase,
) -> bool:
    sample_x = _Y_FOCUS_X_VALUES
    all_cases = (f_case, f_prime, g_case, g_prime, decoy_case)

    max_abs = max(abs(case.evaluate(x_value)) for case in all_cases for x_value in sample_x)
    if max_abs > _MAX_GRAPH_ABS:
        return False

    if _case_span(f_case, _Y_FOCUS_X_VALUES) < _MIN_FUNCTION_SPAN or _case_span(g_case, _Y_FOCUS_X_VALUES) < _MIN_FUNCTION_SPAN:
        return False
    if not _derivative_case_is_clear(f_prime) or not _derivative_case_is_clear(g_prime):
        return False
    if not _derivative_case_is_clear(decoy_case):
        return False

    if f_case.signature() == g_case.signature() or f_prime.signature() == g_prime.signature():
        return False
    if decoy_case.signature() in {f_prime.signature(), g_prime.signature()}:
        return False

    if not _distribution_is_clear(f_case, f_prime, g_case, g_prime, decoy_case):
        return False

    return True


def _case_span(case: PolynomialCase, x_values: tuple[float, ...] = _ANCHOR_X_VALUES) -> float:
    y_values = [case.evaluate(x_value) for x_value in x_values]
    return max(y_values) - min(y_values)


def _derivative_case_is_clear(case: PolynomialCase) -> bool:
    y_values = [case.evaluate(x_value) for x_value in _Y_FOCUS_X_VALUES]
    span = max(y_values) - min(y_values)
    if span >= _MIN_DERIVATIVE_SPAN:
        return True
    return abs(_mean_level(y_values)) >= _MIN_CONSTANT_LEVEL


def _distribution_is_clear(
    f_case: PolynomialCase,
    f_prime: PolynomialCase,
    g_case: PolynomialCase,
    g_prime: PolynomialCase,
    decoy_case: PolynomialCase,
) -> bool:
    sample_x = list(_Y_FOCUS_X_VALUES)
    curves = {
        "f": [f_case.evaluate(x_value) for x_value in sample_x],
        "f'": [f_prime.evaluate(x_value) for x_value in sample_x],
        "g": [g_case.evaluate(x_value) for x_value in sample_x],
        "g'": [g_prime.evaluate(x_value) for x_value in sample_x],
        "stör": [decoy_case.evaluate(x_value) for x_value in sample_x],
    }

    all_values = [value for values in curves.values() for value in values]
    y_low, y_high = _display_y_range_from_values(all_values)
    rendered_axis_span = y_high - y_low
    if rendered_axis_span > _MAX_TOTAL_SPAN:
        return False

    if any(not _curve_is_visually_clear(values, rendered_axis_span) for values in curves.values()):
        return False

    if abs(_mean_level(curves["f"]) - _mean_level(curves["g"])) < _MIN_FUNCTION_MEAN_GAP:
        return False
    if abs(_mean_level(curves["f'"]) - _mean_level(curves["g'"])) < _MIN_DERIVATIVE_MEAN_GAP:
        return False

    pair_names = (("f", "f'"), ("f", "g"), ("f", "g'"), ("f'", "g"), ("f'", "g'"), ("g", "g'"))
    min_pairwise_distance = min(
        sum(abs(left - right) for left, right in zip(curves[name_a], curves[name_b])) / len(sample_x)
        for name_a, name_b in pair_names
    )
    if min_pairwise_distance < _MIN_PAIRWISE_AVG_DISTANCE:
        return False

    decoy_gaps = {
        name: [abs(left - right) for left, right in zip(curves["stör"], curves[name])]
        for name in ("f", "f'", "g", "g'")
    }
    closest_real_curve = min(
        decoy_gaps,
        key=lambda name: sum(decoy_gaps[name]) / len(sample_x),
    )
    decoy_distance = sum(decoy_gaps[closest_real_curve]) / len(sample_x)
    if decoy_distance < _MIN_DECOY_AVG_DISTANCE:
        return False

    clear_decoy_points = sum(
        gap >= _MIN_DECOY_CLEAR_POINT_GAP
        for gap in decoy_gaps[closest_real_curve]
    )
    if clear_decoy_points < _MIN_DECOY_CLEAR_POINT_COUNT:
        return False

    return True


def _mean_level(values: list[float]) -> float:
    return sum(values) / len(values)


def _curve_is_visually_clear(values: list[float], rendered_axis_span: float) -> bool:
    span = max(values) - min(values)
    if span >= 1e-9:
        return span / rendered_axis_span >= _MIN_RELATIVE_TRACE_SPAN
    return abs(_mean_level(values)) >= _MIN_CONSTANT_LEVEL


def _display_y_range_from_values(values: list[float]) -> tuple[float, float]:
    y_min = min(values)
    y_max = max(values)
    span = max(1.0, y_max - y_min)
    y_pad = max(0.75, 0.12 * span)
    y_step = axis_tick_step(span + 2.0 * y_pad)
    y_low = y_step * math.floor((y_min - y_pad) / y_step)
    y_high = y_step * math.ceil((y_max + y_pad) / y_step)
    return y_low, y_high


def _rendered_axis_span(values: list[float]) -> float:
    y_low, y_high = _display_y_range_from_values(values)
    return y_high - y_low


def _display_y_range_for_cases(cases: list[PolynomialCase]) -> tuple[float, float]:
    focus_values = [case.evaluate(x_value) for case in cases for x_value in _Y_FOCUS_X_VALUES]
    return _display_y_range_from_values(focus_values)


def _choose_anchor(
    rng: random.Random,
    f_case: PolynomialCase,
    f_prime: PolynomialCase,
    g_case: PolynomialCase,
    g_prime: PolynomialCase,
    decoy_case: PolynomialCase,
) -> tuple[str, float, float] | None:
    cases = {
        "f": f_case,
        "f'": f_prime,
        "g": g_case,
        "g'": g_prime,
        "stör": decoy_case,
    }
    options: list[tuple[str, float, float]] = []

    for x_value in _ANCHOR_X_VALUES:
        values = {name: case.evaluate(x_value) for name, case in cases.items()}
        for name in ("f", "f'", "g", "g'"):
            value = values[name]
            if abs(value) < 0.35:
                continue
            gap = min(abs(value - other) for other_name, other in values.items() if other_name != name)
            if gap < _MIN_ANCHOR_GAP:
                continue
            options.append((name, x_value, round(value, 2)))

    if not options:
        return None

    return rng.choice(options)


def _build_task(
    rng: random.Random,
    f_case: PolynomialCase,
    f_prime: PolynomialCase,
    g_case: PolynomialCase,
    g_prime: PolynomialCase,
    decoy_case: PolynomialCase,
    anchor: tuple[str, float, float],
) -> tuple[Task, tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...], str, float, float]]:
    cases = [f_case, f_prime, g_case, g_prime, decoy_case]
    permutation = list(range(5))
    rng.shuffle(permutation)

    ordered_cases = [cases[index] for index in permutation]
    y_range = _display_y_range_for_cases(cases)
    label_for_index = {original_index: _PLOT_LABELS[position] for position, original_index in enumerate(permutation)}
    visual = build_plotly_visual_from_cases(
        ordered_cases,
        names=list(_PLOT_LABELS),
        x_range=_X_RANGE,
        y_range=y_range,
        title="",
        x_axis="",
        y_axis="",
        showlegend=True,
    )

    anchor_name, anchor_x, anchor_value = anchor
    questions = [
        "welcher Graph zu $f$ gehört.",
        "welcher Graph zu $f'$ gehört.",
        "welcher Graph zu $g$ gehört.",
        "welcher Graph zu $g'$ gehört.",
    ]
    answers = [
        mc(list(_PLOT_LABELS), list(_PLOT_LABELS).index(label_for_index[0])),
        mc(list(_PLOT_LABELS), list(_PLOT_LABELS).index(label_for_index[1])),
        mc(list(_PLOT_LABELS), list(_PLOT_LABELS).index(label_for_index[2])),
        mc(list(_PLOT_LABELS), list(_PLOT_LABELS).index(label_for_index[3])),
    ]

    task = Task(
        einleitung=(
            "Die fünf Graphen $a$, $b$, $c$, $d$ und $e$ zeigen die Funktionen $f$, $f'$, $g$, $g'$ "
            "sowie einen weiteren Graphen "
            "in unbekannter Reihenfolge. "
            f"Zusätzlich gilt ${anchor_name}({_latex_number(anchor_x)})={_latex_number(anchor_value)}$. "
            "Bestimmen Sie"
        ),
        fragen=questions,
        antworten=answers,
        visual=visual,
    )
    key = (
        f_case.signature(),
        g_case.signature(),
        decoy_case.signature(),
        tuple(permutation),
        anchor_name,
        anchor_x,
        anchor_value,
    )
    return task, key


def _latex_number(value: float) -> str:
    rounded = round(float(value), 2)
    if abs(rounded) < 1e-9:
        return "0"
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))
    text = f"{rounded:.2f}".rstrip("0").rstrip(".")
    return text.replace(".", "{,}")