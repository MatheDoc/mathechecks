"""Generator fuer Check 05 - Aus dem Ableitungsgraphen folgern."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_opt, numerical_opt_none
from aufgaben.core.tolerances import graph_read_tolerance_from_span
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    PolynomialCase,
    build_plotly_visual_from_cases,
    multiply_polynomials,
    scale_polynomial,
)


_ROOT_VALUES = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)
_CENTER_VALUES = (-2.0, -1.0, 0.0, 1.0, 2.0)
_OFFSET_VALUES = (1.0, 2.0)
_SCALE_MAGNITUDES = (0.1, 0.12, 0.15, 0.18, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.75, 1.0)
_SINGLE_EVENT_MARGIN = 0.7
_DOUBLE_EVENT_MARGIN = 0.85
_TRIPLE_EVENT_MARGIN = 0.75
_MULTI_EVENT_MARGIN = 1.0
_NO_ROOT_SINGLE_MARGIN = 1.2
_NO_ROOT_MULTI_MARGIN = 1.4
_SINGLE_EVENT_MIN_X_WIDTH = 4.25
_DOUBLE_EVENT_MIN_X_WIDTH = 4.75
_TRIPLE_EVENT_MIN_X_WIDTH = 4.75
_MULTI_EVENT_MIN_X_WIDTH = 5.25
_SEARCH_MARGIN = 3.5
_MIN_Y_SPAN = 3.5
_MAX_Y_ABS = 14.0
_MIN_INFLECTION_PROMINENCE_ABS = 0.2
_MIN_INFLECTION_PROMINENCE_REL = 0.02

_FAMILY_ORDER = (
    "linear",
    "quadratic_two_roots",
    "quadratic_double_root",
    "quadratic_no_root",
    "cubic_triple_root",
    "cubic_simple_double",
    "cubic_three_roots",
    "cubic_irreducible_mix",
    "quartic_four_roots",
    "quartic_two_double_roots",
    "quartic_double_two_simple",
    "quartic_triple_simple",
    "quartic_irreducible_mix",
)


@dataclass(frozen=True)
class _DerivativeGraphCase:
    family: str
    derivative_case: PolynomialCase
    x_range: tuple[float, float]
    highs: tuple[float, ...]
    lows: tuple[float, ...]
    inflections: tuple[float, ...]
    inflections_left_right: tuple[float, ...]
    inflections_right_left: tuple[float, ...]


class AbleitungsgraphFolgernGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.ableitungsgraph_folgern"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        buckets = {family: list(cases) for family, cases in _candidate_pool_by_family().items()}
        families = [family for family in _FAMILY_ORDER if buckets.get(family)]
        rng.shuffle(families)

        for family in families:
            rng.shuffle(buckets[family])

        selected: list[_DerivativeGraphCase] = []
        while len(selected) < count:
            progress = False
            for family in families:
                bucket = buckets[family]
                if not bucket:
                    continue
                selected.append(bucket.pop())
                progress = True
                if len(selected) >= count:
                    break
            if not progress:
                break

        if len(selected) < count:
            raise ValueError("Zu wenige geeignete Kandidaten fuer ableitungsgraph-folgern.")

        return [_build_task(case) for case in selected]


@lru_cache(maxsize=1)
def _candidate_pool_by_family() -> dict[str, tuple[_DerivativeGraphCase, ...]]:
    candidates: dict[str, list[_DerivativeGraphCase]] = {family: [] for family in _FAMILY_ORDER}
    seen_signatures: set[tuple[float, ...]] = set()

    for family, base_case, real_roots, support_points in _iter_base_cases():
        search_range = _range_from_points(
            real_roots if real_roots else support_points,
            margin=_SEARCH_MARGIN,
            min_width=8.0,
        )
        inflections = _roots_with_sign_change(base_case.derivative(1), search_range)
        x_range = _final_x_range(real_roots, support_points, inflections)
        scales = _preferred_scales(base_case, x_range)
        if not scales:
            continue

        for scale in scales:
            derivative_case = PolynomialCase(scale_polynomial(base_case.coeffs, scale))
            signature = derivative_case.signature()
            if signature in seen_signatures:
                continue

            highs, lows = _classify_extrema(derivative_case, real_roots, x_range)
            inflections_rounded = tuple(_rounded_x(value) for value in inflections)
            inflections_left_right, inflections_right_left = _classify_inflection_directions(
                derivative_case,
                inflections,
                x_range,
            )

            if len(highs) > 2 or len(lows) > 2 or len(inflections_rounded) > 3:
                continue
            if not _is_graphically_clear(derivative_case, highs, lows, inflections_rounded, x_range):
                continue

            seen_signatures.add(signature)
            candidates[family].append(
                _DerivativeGraphCase(
                    family=family,
                    derivative_case=derivative_case,
                    x_range=x_range,
                    highs=highs,
                    lows=lows,
                    inflections=inflections_rounded,
                    inflections_left_right=inflections_left_right,
                    inflections_right_left=inflections_right_left,
                )
            )

    return {family: tuple(cases) for family, cases in candidates.items() if cases}


def _iter_base_cases() -> list[tuple[str, PolynomialCase, tuple[float, ...], tuple[float, ...]]]:
    cases: list[tuple[str, PolynomialCase, tuple[float, ...], tuple[float, ...]]] = []

    for root in _ROOT_VALUES:
        cases.append(("linear", PolynomialCase((1.0, -root)), (root,), (root,)))

    for left, right in combinations(_ROOT_VALUES, 2):
        cases.append(
            (
                "quadratic_two_roots",
                PolynomialCase(multiply_polynomials((1.0, -left), (1.0, -right))),
                (left, right),
                (left, right),
            )
        )

    for root in _ROOT_VALUES:
        factor = (1.0, -root)
        cases.append(
            (
                "quadratic_double_root",
                PolynomialCase(multiply_polynomials(factor, factor)),
                (root,),
                (root,),
            )
        )

    for center in _CENTER_VALUES:
        for offset in _OFFSET_VALUES:
            cases.append(
                (
                    "quadratic_no_root",
                    PolynomialCase(_irreducible_quadratic(center, offset)),
                    (),
                    (center,),
                )
            )

    for root in _CENTER_VALUES:
        factor = (1.0, -root)
        cases.append(
            (
                "cubic_triple_root",
                PolynomialCase(multiply_polynomials(factor, factor, factor)),
                (root,),
                (root,),
            )
        )

    for simple_root in _ROOT_VALUES:
        for double_root in _ROOT_VALUES:
            if abs(simple_root - double_root) < 1.0:
                continue
            double_factor = (1.0, -double_root)
            cases.append(
                (
                    "cubic_simple_double",
                    PolynomialCase(multiply_polynomials((1.0, -simple_root), double_factor, double_factor)),
                    tuple(sorted((simple_root, double_root))),
                    tuple(sorted((simple_root, double_root))),
                )
            )

    for root_a, root_b, root_c in combinations(_ROOT_VALUES, 3):
        cases.append(
            (
                "cubic_three_roots",
                PolynomialCase(multiply_polynomials((1.0, -root_a), (1.0, -root_b), (1.0, -root_c))),
                (root_a, root_b, root_c),
                (root_a, root_b, root_c),
            )
        )

    for linear_root in _ROOT_VALUES:
        for center in _CENTER_VALUES:
            for offset in _OFFSET_VALUES:
                cases.append(
                    (
                        "cubic_irreducible_mix",
                        PolynomialCase(
                            multiply_polynomials((1.0, -linear_root), _irreducible_quadratic(center, offset))
                        ),
                        (linear_root,),
                        tuple(sorted((linear_root, center))),
                    )
                )

    for roots in combinations(_ROOT_VALUES, 4):
        cases.append(
            (
                "quartic_four_roots",
                PolynomialCase(multiply_polynomials(*tuple((1.0, -root) for root in roots))),
                roots,
                roots,
            )
        )

    for root_a, root_b in combinations(_ROOT_VALUES, 2):
        factor_a = (1.0, -root_a)
        factor_b = (1.0, -root_b)
        cases.append(
            (
                "quartic_two_double_roots",
                PolynomialCase(multiply_polynomials(factor_a, factor_a, factor_b, factor_b)),
                (root_a, root_b),
                (root_a, root_b),
            )
        )

    for double_root in _ROOT_VALUES:
        remaining = [root for root in _ROOT_VALUES if root != double_root]
        for root_b, root_c in combinations(remaining, 2):
            factor = (1.0, -double_root)
            cases.append(
                (
                    "quartic_double_two_simple",
                    PolynomialCase(multiply_polynomials(factor, factor, (1.0, -root_b), (1.0, -root_c))),
                    tuple(sorted((double_root, root_b, root_c))),
                    tuple(sorted((double_root, root_b, root_c))),
                )
            )

    for triple_root in _ROOT_VALUES:
        factor = (1.0, -triple_root)
        for simple_root in _ROOT_VALUES:
            if simple_root == triple_root:
                continue
            cases.append(
                (
                    "quartic_triple_simple",
                    PolynomialCase(multiply_polynomials(factor, factor, factor, (1.0, -simple_root))),
                    tuple(sorted((triple_root, simple_root))),
                    tuple(sorted((triple_root, simple_root))),
                )
            )

    for root_a, root_b in combinations(_ROOT_VALUES, 2):
        for center in _CENTER_VALUES:
            for offset in _OFFSET_VALUES:
                cases.append(
                    (
                        "quartic_irreducible_mix",
                        PolynomialCase(
                            multiply_polynomials(
                                (1.0, -root_a),
                                (1.0, -root_b),
                                _irreducible_quadratic(center, offset),
                            )
                        ),
                        tuple(sorted((root_a, root_b))),
                        tuple(sorted((root_a, root_b, center))),
                    )
                )

    return cases


def _build_task(case: _DerivativeGraphCase) -> Task:
    x_tolerance = graph_read_tolerance_from_span(case.x_range[1] - case.x_range[0])
    visual = build_plotly_visual_from_cases(
        [case.derivative_case],
        names=["f'"],
        x_range=case.x_range,
        title="",
        x_axis="",
        y_axis="",
        showlegend=False,
    )

    return Task(
        einleitung=(
            "Das Diagramm zeigt den Graphen der ersten Ableitungsfunktion $f'$ einer ganzrationalen "
            "Funktion $f$. Geben Sie die x-Werte jeweils in aufsteigender Reihenfolge an. "
            "Nicht benötigte Felder setzen Sie auf 'keine Lösung'. Bestimmen Sie"
        ),
        fragen=[
            "die x-Werte aller Hochpunkte von $f$.",
            "die x-Werte aller Tiefpunkte von $f$.",
            "die x-Werte aller Wendestellen von $f$ mit Krümmungswechsel von linksgekrümmt nach rechtsgekrümmt.",
            "die x-Werte aller Wendestellen von $f$ mit Krümmungswechsel von rechtsgekrümmt nach linksgekrümmt.",
        ],
        antworten=[
            _x_slot_answer(case.highs, slot_count=2, tolerance=x_tolerance),
            _x_slot_answer(case.lows, slot_count=2, tolerance=x_tolerance),
            _x_slot_answer(case.inflections_left_right, slot_count=2, tolerance=x_tolerance),
            _x_slot_answer(case.inflections_right_left, slot_count=2, tolerance=x_tolerance),
        ],
        visual=visual,
    )


def _x_slot_answer(values: tuple[float, ...], *, slot_count: int, tolerance: float) -> str:
    entries: list[str] = []
    sorted_values = tuple(sorted(values))

    for index in range(slot_count):
        label = index + 1
        if index < len(sorted_values):
            placeholder = numerical_opt(sorted_values[index], tolerance=tolerance)
        else:
            placeholder = numerical_opt_none()
        prefix = "$ " if index == 0 else "$\\quad "
        entries.append(f"{prefix}x_{label} = ${placeholder}")

    return " ".join(entries)


def _classify_extrema(
    derivative_case: PolynomialCase,
    real_roots: tuple[float, ...],
    x_range: tuple[float, float],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    highs: list[float] = []
    lows: list[float] = []

    for root in real_roots:
        delta = _classification_delta(root, real_roots, x_range)
        left = derivative_case.evaluate(root - delta)
        right = derivative_case.evaluate(root + delta)

        if left > 1e-6 and right < -1e-6:
            highs.append(_rounded_x(root))
        elif left < -1e-6 and right > 1e-6:
            lows.append(_rounded_x(root))

    return tuple(sorted(highs)), tuple(sorted(lows))


def _classify_inflection_directions(
    derivative_case: PolynomialCase,
    inflections: tuple[float, ...],
    x_range: tuple[float, float],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    left_right: list[float] = []
    right_left: list[float] = []

    for inflection in inflections:
        delta = _classification_delta(inflection, inflections, x_range)
        left = derivative_case.evaluate(inflection - delta)
        middle = derivative_case.evaluate(inflection)
        right = derivative_case.evaluate(inflection + delta)

        if middle > max(left, right) + 1e-6:
            left_right.append(_rounded_x(inflection))
        elif middle < min(left, right) - 1e-6:
            right_left.append(_rounded_x(inflection))

    return tuple(sorted(left_right)), tuple(sorted(right_left))


def _classification_delta(
    root: float,
    real_roots: tuple[float, ...],
    x_range: tuple[float, float],
) -> float:
    distances = [abs(root - other) for other in real_roots if abs(root - other) > 1e-9]
    max_delta = 0.5 if not distances else 0.35 * min(distances)
    span_delta = 0.08 * (x_range[1] - x_range[0])
    return max(0.12, min(0.45, max_delta, span_delta))


def _preferred_scales(base_case: PolynomialCase, x_range: tuple[float, float]) -> tuple[float, ...]:
    x_values = _sample_x_values(x_range, steps=240)
    y_values = [base_case.evaluate(x_value) for x_value in x_values]
    y_span = max(y_values) - min(y_values)
    y_abs = max(abs(value) for value in y_values)

    if y_span < 1e-9 or y_abs < 1e-9:
        return ()

    magnitudes = [
        value
        for value in _SCALE_MAGNITUDES
        if y_span * value >= _MIN_Y_SPAN and y_abs * value <= _MAX_Y_ABS
    ]
    if not magnitudes:
        return ()

    best_magnitudes = sorted(magnitudes, key=lambda value: abs(y_span * value - 9.0))[:2]
    scales: list[float] = []
    for magnitude in best_magnitudes:
        scales.extend((-magnitude, magnitude))
    return tuple(scales)


def _roots_with_sign_change(
    case: PolynomialCase,
    x_range: tuple[float, float],
    *,
    steps: int = 2200,
) -> tuple[float, ...]:
    x_min, x_max = x_range
    prev_x = x_min
    prev_y = case.evaluate(prev_x)
    candidates: list[float] = []

    for index in range(1, steps + 1):
        x_value = x_min + (x_max - x_min) * index / steps
        y_value = case.evaluate(x_value)

        if prev_y * y_value < 0:
            candidates.append(_bisect_root(case, prev_x, x_value))
        elif abs(y_value) < 1e-5:
            candidates.append(x_value)

        prev_x = x_value
        prev_y = y_value

    unique_candidates = _unique_sorted(candidates)
    check_delta = max(0.08, 0.015 * (x_max - x_min))
    roots: list[float] = []

    for candidate in unique_candidates:
        left = case.evaluate(candidate - check_delta)
        right = case.evaluate(candidate + check_delta)
        if left * right < 0:
            roots.append(_rounded_x(candidate))

    return tuple(_unique_sorted(roots))


def _bisect_root(case: PolynomialCase, left: float, right: float, iterations: int = 60) -> float:
    left_y = case.evaluate(left)

    for _ in range(iterations):
        mid = 0.5 * (left + right)
        mid_y = case.evaluate(mid)
        if abs(mid_y) < 1e-12:
            return mid
        if left_y * mid_y <= 0:
            right = mid
        else:
            left = mid
            left_y = mid_y

    return 0.5 * (left + right)


def _final_x_range(
    real_roots: tuple[float, ...],
    support_points: tuple[float, ...],
    inflections: tuple[float, ...],
) -> tuple[float, float]:
    if real_roots:
        points = tuple(sorted(real_roots + inflections)) if inflections else real_roots
        margin, min_width = _display_window_parameters(points, has_real_roots=True)
        return _range_from_points(points, margin=margin, min_width=min_width)

    points = inflections if inflections else support_points
    margin, min_width = _display_window_parameters(points, has_real_roots=False)
    return _range_from_points(points, margin=margin, min_width=min_width)


def _display_window_parameters(
    points: tuple[float, ...],
    *,
    has_real_roots: bool,
) -> tuple[float, float]:
    point_count = len(points)
    point_span = 0.0 if point_count < 2 else max(points) - min(points)

    if has_real_roots:
        if point_count <= 1:
            margin = _SINGLE_EVENT_MARGIN
            min_width = _SINGLE_EVENT_MIN_X_WIDTH
        elif point_count == 2:
            margin = _DOUBLE_EVENT_MARGIN
            min_width = _DOUBLE_EVENT_MIN_X_WIDTH
        elif point_count == 3:
            margin = _TRIPLE_EVENT_MARGIN
            min_width = _TRIPLE_EVENT_MIN_X_WIDTH
        else:
            margin = _MULTI_EVENT_MARGIN
            min_width = _MULTI_EVENT_MIN_X_WIDTH
    else:
        if point_count <= 1:
            margin = _NO_ROOT_SINGLE_MARGIN
            min_width = _DOUBLE_EVENT_MIN_X_WIDTH
        else:
            margin = _NO_ROOT_MULTI_MARGIN
            min_width = _MULTI_EVENT_MIN_X_WIDTH

    margin += min(0.15, 0.08 * point_span)
    return margin, min_width


def _range_from_points(
    points: tuple[float, ...],
    *,
    margin: float,
    min_width: float,
) -> tuple[float, float]:
    anchors = points if points else (0.0,)
    x_min = min(anchors) - margin
    x_max = max(anchors) + margin

    if x_max - x_min < min_width:
        midpoint = 0.5 * (x_min + x_max)
        half_width = 0.5 * min_width
        x_min = midpoint - half_width
        x_max = midpoint + half_width

    return (_rounded_x(x_min), _rounded_x(x_max))


def _sample_x_values(x_range: tuple[float, float], *, steps: int) -> list[float]:
    x_min, x_max = x_range
    return [x_min + (x_max - x_min) * index / steps for index in range(steps + 1)]


def _is_graphically_clear(
    derivative_case: PolynomialCase,
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    inflections: tuple[float, ...],
    x_range: tuple[float, float],
) -> bool:
    x_min, x_max = x_range
    for points in (highs, lows, inflections):
        if not all(x_min + 0.15 < value < x_max - 0.15 for value in points):
            return False
        if _min_distance(points) < 0.55:
            return False
    if not _inflections_are_visible(derivative_case, inflections, x_range):
        return False
    return True


def _inflections_are_visible(
    derivative_case: PolynomialCase,
    inflections: tuple[float, ...],
    x_range: tuple[float, float],
) -> bool:
    if not inflections:
        return True

    x_values = _sample_x_values(x_range, steps=240)
    y_values = [derivative_case.evaluate(x_value) for x_value in x_values]
    y_span = max(y_values) - min(y_values)
    min_prominence = max(_MIN_INFLECTION_PROMINENCE_ABS, _MIN_INFLECTION_PROMINENCE_REL * y_span)

    for inflection in inflections:
        delta = _classification_delta(inflection, inflections, x_range)
        left = derivative_case.evaluate(inflection - delta)
        middle = derivative_case.evaluate(inflection)
        right = derivative_case.evaluate(inflection + delta)
        local_prominence = max(abs(left - middle), abs(right - middle))
        if local_prominence < min_prominence:
            return False

    return True


def _min_distance(values: tuple[float, ...]) -> float:
    if len(values) < 2:
        return 999.0
    return min(abs(values[index + 1] - values[index]) for index in range(len(values) - 1))


def _irreducible_quadratic(center: float, offset: float) -> tuple[float, float, float]:
    return (1.0, -2.0 * center, center * center + offset)


def _unique_sorted(values: list[float] | tuple[float, ...]) -> list[float]:
    unique: list[float] = []
    for value in sorted(values):
        rounded = _rounded_x(value)
        if not unique or abs(rounded - unique[-1]) > 1e-3:
            unique.append(rounded)
    return unique


def _rounded_x(value: float) -> float:
    if abs(value) < 1e-9:
        return 0.0
    return round(float(value), 4)