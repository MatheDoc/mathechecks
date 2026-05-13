"""Gemeinsame Falllogik fuer Extrempunkte, Monotonie, Wendestellen und Kruemmung."""

from __future__ import annotations

from dataclasses import dataclass
import random

from aufgaben.core.latex import fmt
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    PolynomialCase,
    integrate_polynomial,
    multiply_polynomials,
    polynomial_latex,
    scale_polynomial,
)


_ROOT_VALUES = tuple(value / 10.0 for value in range(-90, 91))
_QUADRATIC_DERIVATIVE_SLOPES = (-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0)
_CUBIC_DERIVATIVE_SCALES = (-3.0, -1.5, 1.5, 3.0)
_SPECIAL_CUBIC_DOUBLE_ROOT_VALUES = tuple(value / 10.0 for value in range(-45, 46))
_SPECIAL_QUARTIC_TRIPLE_ROOT_VALUES = tuple(value / 2.0 for value in range(-6, 7))
_SPECIAL_QUARTIC_MIXED_DOUBLE_ROOT_VALUES = tuple(value / 10.0 for value in range(-20, 21))
_SPECIAL_QUARTIC_MIXED_SIMPLE_ROOT_VALUES = tuple(float(value) for value in range(-5, 6))
_SPECIAL_CUBIC_DOUBLE_SCALES = (-6.0, -3.0, 3.0, 6.0)
_SPECIAL_QUARTIC_TRIPLE_SCALES = (-4.0, 4.0)
_SPECIAL_QUARTIC_MIXED_SCALES = (-6.0, 6.0)
_INFLECTION_ROOT_VALUES = tuple(value / 10.0 for value in range(-70, 71))
_LINEAR_SECOND_DERIVATIVE_SLOPES = (-6.0, -3.0, -1.5, 1.5, 3.0, 6.0)
_QUADRATIC_SECOND_DERIVATIVE_SCALES = (-6.0, -3.0, 3.0, 6.0)
_SPECIAL_QUARTIC_DOUBLE_ROOT_VALUES = tuple(value / 10.0 for value in range(-40, 41))
_SPECIAL_QUINTIC_TRIPLE_ROOT_VALUES = tuple(value / 2.0 for value in range(-5, 6))
_SPECIAL_QUINTIC_MIXED_DOUBLE_ROOT_VALUES = tuple(value / 10.0 for value in range(-30, 31))
_SPECIAL_QUINTIC_MIXED_SIMPLE_ROOT_VALUES = tuple(float(value) for value in range(-5, 6))
_SPECIAL_QUARTIC_DOUBLE_SCALES = (-12.0, -6.0, 6.0, 12.0)
_SPECIAL_QUINTIC_TRIPLE_SCALES = (-10.0, -5.0, 5.0, 10.0)
_SPECIAL_QUINTIC_MIXED_SCALES = (-10.0, -5.0, 5.0, 10.0)
_FIRST_DERIVATIVE_SHIFTS = tuple(float(value) for value in range(-6, 7))
_Y_SHIFTS = tuple(float(value) for value in range(-6, 7))
_CLEANUP_MULTIPLIERS = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0)
_MIN_ROOT_GAP = 1.5
_MAX_FUNCTION_ABS = 500.0
_MAX_DERIVATIVE_ABS = 300.0
_MAX_FUNCTION_COEFF_ABS = 120.0
_MAX_DERIVATIVE_COEFF_ABS = 120.0


@dataclass(frozen=True)
class SimpleExtremMonotonicityCase:
    function_case: PolynomialCase
    derivative_case: PolynomialCase
    candidate_xs: tuple[float, ...]
    high_x: float | None
    low_x: float | None
    high_point: tuple[float, float] | None
    low_point: tuple[float, float] | None
    increasing_intervals: tuple[tuple[float | None, float | None], ...]
    decreasing_intervals: tuple[tuple[float | None, float | None], ...]
    saddle_x: float | None = None

    def signature(self) -> tuple[float, ...]:
        return self.function_case.signature()

    def polynomial_text(self, *, name: str = "f") -> str:
        return polynomial_latex(self.function_case, name=name)

    def interval_options(self) -> tuple[tuple[float | None, float | None], ...]:
        return _intervals_from_candidates(self.candidate_xs)


@dataclass(frozen=True)
class SimpleInflectionCurvatureCase:
    function_case: PolynomialCase
    second_derivative_case: PolynomialCase
    candidate_xs: tuple[float, ...]
    inflection_xs: tuple[float, ...]
    left_curved_intervals: tuple[tuple[float | None, float | None], ...]
    right_curved_intervals: tuple[tuple[float | None, float | None], ...]

    def signature(self) -> tuple[float, ...]:
        return self.function_case.signature()

    def polynomial_text(self, *, name: str = "f") -> str:
        return polynomial_latex(self.function_case, name=name)

    def interval_options(self) -> tuple[tuple[float | None, float | None], ...]:
        return _intervals_from_candidates(self.candidate_xs)


def sample_simple_extrem_monotonicity_case(
    rng: random.Random,
    *,
    degree: int,
) -> SimpleExtremMonotonicityCase:
    if degree == 2:
        return _sample_quadratic_case(rng)
    if degree == 3:
        return _sample_cubic_case(rng)
    raise ValueError("Nur Grade 2 und 3 werden fuer einfache Extrem- und Monotoniefaelle unterstuetzt.")


def sample_special_extrem_monotonicity_case(
    rng: random.Random,
    *,
    family: str,
) -> SimpleExtremMonotonicityCase:
    if family == "cubic_saddle":
        return _sample_special_cubic_saddle_case(rng)
    if family == "quartic_triple":
        return _sample_special_quartic_triple_case(rng)
    if family == "quartic_mixed":
        return _sample_special_quartic_mixed_case(rng)
    raise ValueError(f"Unbekannte Spezialfall-Familie: {family}")


def sample_simple_inflection_curvature_case(
    rng: random.Random,
    *,
    degree: int,
) -> SimpleInflectionCurvatureCase:
    if degree == 3:
        return _sample_cubic_inflection_case(rng)
    if degree == 4:
        return _sample_quartic_inflection_case(rng)
    raise ValueError("Nur Grade 3 und 4 werden fuer einfache Wende- und Kruemmungsfaelle unterstuetzt.")


def sample_special_inflection_curvature_case(
    rng: random.Random,
    *,
    family: str,
) -> SimpleInflectionCurvatureCase:
    if family == "quartic_flat":
        return _sample_special_quartic_flat_case(rng)
    if family == "quintic_triple":
        return _sample_special_quintic_triple_case(rng)
    if family == "quintic_mixed":
        return _sample_special_quintic_mixed_case(rng)
    raise ValueError(f"Unbekannte Spezialfall-Familie: {family}")


def interval_label(interval_bounds: tuple[float | None, float | None]) -> str:
    left, right = interval_bounds
    left_text = r"-\infty" if left is None else fmt(left)
    right_text = r"\infty" if right is None else fmt(right)
    left_bracket, right_bracket = interval_delimiters(left, right)
    return f"${left_bracket}{left_text}; {right_text}{right_bracket}$"


def interval_delimiters(left: float | None, right: float | None) -> tuple[str, str]:
    return ("(" if left is None else "[", ")" if right is None else "]")


def build_interval_input_note() -> str:
    return (
        "Für unbeschränkte Intervallgrenzen tragen Sie $-\\infty$ bzw. $+\\infty$ ein, zum Beispiel als '-inf' bzw. '+inf'."
    )


def build_simple_function_intro(case: SimpleExtremMonotonicityCase) -> str:
    return (
        f"Gegeben ist die Funktion $$ {case.polynomial_text(name='f')} $$. "
        "Mehrere Antworten geben Sie in aufsteigender bzw. von links nach rechts an. "
        "Nicht benötigte Felder setzen Sie auf 'keine Lösung'."
    )


def build_inflection_function_intro(case: SimpleInflectionCurvatureCase) -> str:
    return (
        f"Gegeben ist die Funktion $$ {case.polynomial_text(name='f')} $$. "
        "Mehrere Antworten geben Sie in aufsteigender bzw. von links nach rechts an. "
        "Nicht benötigte Felder setzen Sie auf 'keine Lösung'."
    )


def _sample_quadratic_case(rng: random.Random) -> SimpleExtremMonotonicityCase:
    for _ in range(500):
        root = float(rng.choice(_ROOT_VALUES))
        slope = float(rng.choice(_QUADRATIC_DERIVATIVE_SLOPES))
        y_shift = float(rng.choice(_Y_SHIFTS))
        derivative_case = PolynomialCase((slope, -slope * root))
        function_case = integrate_polynomial(derivative_case, constant=y_shift)
        try:
            function_case, derivative_case = _normalize_function_scale(
                function_case,
                derivative_case,
                (root,),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, derivative_case, (root,)):
            continue

        second_derivative_value = function_case.derivative(2).evaluate(root)
        high_x = _rounded_value(root) if second_derivative_value < 0 else None
        low_x = _rounded_value(root) if second_derivative_value > 0 else None
        high_point = _point_from_x(function_case, high_x)
        low_point = _point_from_x(function_case, low_x)
        increasing_intervals, decreasing_intervals = _classify_monotonicity(derivative_case, (root,))

        return SimpleExtremMonotonicityCase(
            function_case=function_case,
            derivative_case=derivative_case,
            candidate_xs=(_rounded_value(root),),
            high_x=high_x,
            low_x=low_x,
            high_point=high_point,
            low_point=low_point,
            increasing_intervals=increasing_intervals,
            decreasing_intervals=decreasing_intervals,
        )

    raise ValueError("Konnte keinen einfachen quadratischen Extremfall erzeugen.")


def _sample_cubic_case(rng: random.Random) -> SimpleExtremMonotonicityCase:
    for _ in range(700):
        left_root, right_root = sorted(float(value) for value in rng.sample(_ROOT_VALUES, 2))
        if right_root - left_root < _MIN_ROOT_GAP:
            continue

        scale = float(rng.choice(_CUBIC_DERIVATIVE_SCALES))
        y_shift = float(rng.choice(_Y_SHIFTS))
        derivative_case = PolynomialCase(
            scale_polynomial(
                multiply_polynomials((1.0, -left_root), (1.0, -right_root)),
                scale,
            )
        )
        function_case = integrate_polynomial(derivative_case, constant=y_shift)
        try:
            function_case, derivative_case = _normalize_function_scale(
                function_case,
                derivative_case,
                (left_root, right_root),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, derivative_case, (left_root, right_root)):
            continue

        second_derivative = function_case.derivative(2)
        left_second = second_derivative.evaluate(left_root)
        right_second = second_derivative.evaluate(right_root)
        if abs(left_second) < 1e-9 or abs(right_second) < 1e-9:
            continue

        high_x = _rounded_value(left_root) if left_second < 0 else _rounded_value(right_root)
        low_x = _rounded_value(left_root) if left_second > 0 else _rounded_value(right_root)
        high_point = _point_from_x(function_case, high_x)
        low_point = _point_from_x(function_case, low_x)
        candidates = (_rounded_value(left_root), _rounded_value(right_root))
        increasing_intervals, decreasing_intervals = _classify_monotonicity(derivative_case, candidates)

        return SimpleExtremMonotonicityCase(
            function_case=function_case,
            derivative_case=derivative_case,
            candidate_xs=candidates,
            high_x=high_x,
            low_x=low_x,
            high_point=high_point,
            low_point=low_point,
            increasing_intervals=increasing_intervals,
            decreasing_intervals=decreasing_intervals,
        )

    raise ValueError("Konnte keinen einfachen kubischen Extremfall erzeugen.")


def _sample_special_cubic_saddle_case(rng: random.Random) -> SimpleExtremMonotonicityCase:
    for _ in range(700):
        root = float(rng.choice(_SPECIAL_CUBIC_DOUBLE_ROOT_VALUES))
        scale = float(rng.choice(_SPECIAL_CUBIC_DOUBLE_SCALES))
        y_shift = float(rng.choice(_Y_SHIFTS))

        derivative_case = PolynomialCase(
            scale_polynomial(
                multiply_polynomials((1.0, -root), (1.0, -root)),
                scale,
            )
        )
        function_case = integrate_polynomial(derivative_case, constant=y_shift)

        try:
            function_case, derivative_case = _normalize_function_scale(
                function_case,
                derivative_case,
                (root,),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, derivative_case, (root,)):
            continue

        return _build_special_case(function_case, derivative_case, (root,))

    raise ValueError("Konnte keinen kubischen Spezialfall mit Sattelpunkt erzeugen.")


def _sample_special_quartic_triple_case(rng: random.Random) -> SimpleExtremMonotonicityCase:
    for _ in range(700):
        root = float(rng.choice(_SPECIAL_QUARTIC_TRIPLE_ROOT_VALUES))
        scale = float(rng.choice(_SPECIAL_QUARTIC_TRIPLE_SCALES))
        y_shift = float(rng.choice(_Y_SHIFTS))

        triple_factor = multiply_polynomials(
            multiply_polynomials((1.0, -root), (1.0, -root)),
            (1.0, -root),
        )
        derivative_case = PolynomialCase(scale_polynomial(triple_factor, scale))
        function_case = integrate_polynomial(derivative_case, constant=y_shift)

        try:
            function_case, derivative_case = _normalize_function_scale(
                function_case,
                derivative_case,
                (root,),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, derivative_case, (root,)):
            continue

        return _build_special_case(function_case, derivative_case, (root,))

    raise ValueError("Konnte keinen quartischen Spezialfall mit dreifacher Nullstelle erzeugen.")


def _sample_special_quartic_mixed_case(rng: random.Random) -> SimpleExtremMonotonicityCase:
    for _ in range(900):
        double_root = float(rng.choice(_SPECIAL_QUARTIC_MIXED_DOUBLE_ROOT_VALUES))
        simple_root = float(rng.choice(_SPECIAL_QUARTIC_MIXED_SIMPLE_ROOT_VALUES))
        if abs(simple_root - double_root) < _MIN_ROOT_GAP:
            continue

        scale = float(rng.choice(_SPECIAL_QUARTIC_MIXED_SCALES))
        y_shift = float(rng.choice(_Y_SHIFTS))
        derivative_case = PolynomialCase(
            scale_polynomial(
                multiply_polynomials(
                    multiply_polynomials((1.0, -double_root), (1.0, -double_root)),
                    (1.0, -simple_root),
                ),
                scale,
            )
        )
        function_case = integrate_polynomial(derivative_case, constant=y_shift)

        try:
            function_case, derivative_case = _normalize_function_scale(
                function_case,
                derivative_case,
                tuple(sorted((double_root, simple_root))),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, derivative_case, (double_root, simple_root)):
            continue

        return _build_special_case(function_case, derivative_case, (double_root, simple_root))

    raise ValueError("Konnte keinen quartischen Spezialfall mit Extrem- und Sattelstelle erzeugen.")


def _sample_cubic_inflection_case(rng: random.Random) -> SimpleInflectionCurvatureCase:
    for _ in range(600):
        root = float(rng.choice(_INFLECTION_ROOT_VALUES))
        slope = float(rng.choice(_LINEAR_SECOND_DERIVATIVE_SLOPES))
        first_derivative_shift = float(rng.choice(_FIRST_DERIVATIVE_SHIFTS))
        y_shift = float(rng.choice(_Y_SHIFTS))
        second_derivative_case = PolynomialCase((slope, -slope * root))
        function_case = _integrate_twice(
            second_derivative_case,
            first_constant=first_derivative_shift,
            second_constant=y_shift,
        )

        try:
            function_case, second_derivative_case = _normalize_function_scale(
                function_case,
                second_derivative_case,
                (root,),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, second_derivative_case, (root,)):
            continue

        left_curved_intervals, right_curved_intervals = _classify_curvature(second_derivative_case, (root,))
        rounded_root = _rounded_value(root)

        return SimpleInflectionCurvatureCase(
            function_case=function_case,
            second_derivative_case=second_derivative_case,
            candidate_xs=(rounded_root,),
            inflection_xs=(rounded_root,),
            left_curved_intervals=left_curved_intervals,
            right_curved_intervals=right_curved_intervals,
        )

    raise ValueError("Konnte keinen einfachen kubischen Wendefall erzeugen.")


def _sample_quartic_inflection_case(rng: random.Random) -> SimpleInflectionCurvatureCase:
    for _ in range(800):
        left_root, right_root = sorted(float(value) for value in rng.sample(_INFLECTION_ROOT_VALUES, 2))
        if right_root - left_root < _MIN_ROOT_GAP:
            continue

        scale = float(rng.choice(_QUADRATIC_SECOND_DERIVATIVE_SCALES))
        first_derivative_shift = float(rng.choice(_FIRST_DERIVATIVE_SHIFTS))
        y_shift = float(rng.choice(_Y_SHIFTS))
        second_derivative_case = PolynomialCase(
            scale_polynomial(
                multiply_polynomials((1.0, -left_root), (1.0, -right_root)),
                scale,
            )
        )
        function_case = _integrate_twice(
            second_derivative_case,
            first_constant=first_derivative_shift,
            second_constant=y_shift,
        )

        try:
            function_case, second_derivative_case = _normalize_function_scale(
                function_case,
                second_derivative_case,
                (left_root, right_root),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, second_derivative_case, (left_root, right_root)):
            continue

        third_derivative = function_case.derivative(3)
        if abs(third_derivative.evaluate(left_root)) < 1e-9 or abs(third_derivative.evaluate(right_root)) < 1e-9:
            continue

        candidates = (_rounded_value(left_root), _rounded_value(right_root))
        left_curved_intervals, right_curved_intervals = _classify_curvature(second_derivative_case, candidates)

        return SimpleInflectionCurvatureCase(
            function_case=function_case,
            second_derivative_case=second_derivative_case,
            candidate_xs=candidates,
            inflection_xs=candidates,
            left_curved_intervals=left_curved_intervals,
            right_curved_intervals=right_curved_intervals,
        )

    raise ValueError("Konnte keinen einfachen quartischen Wendefall erzeugen.")


def _sample_special_quartic_flat_case(rng: random.Random) -> SimpleInflectionCurvatureCase:
    for _ in range(700):
        root = float(rng.choice(_SPECIAL_QUARTIC_DOUBLE_ROOT_VALUES))
        scale = float(rng.choice(_SPECIAL_QUARTIC_DOUBLE_SCALES))
        first_derivative_shift = float(rng.choice(_FIRST_DERIVATIVE_SHIFTS))
        y_shift = float(rng.choice(_Y_SHIFTS))

        second_derivative_case = PolynomialCase(
            scale_polynomial(
                multiply_polynomials((1.0, -root), (1.0, -root)),
                scale,
            )
        )
        function_case = _integrate_twice(
            second_derivative_case,
            first_constant=first_derivative_shift,
            second_constant=y_shift,
        )

        try:
            function_case, second_derivative_case = _normalize_function_scale(
                function_case,
                second_derivative_case,
                (root,),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, second_derivative_case, (root,)):
            continue

        return _build_special_inflection_case(function_case, second_derivative_case, (root,))

    raise ValueError("Konnte keinen quartischen Spezialfall ohne Wendestelle erzeugen.")


def _sample_special_quintic_triple_case(rng: random.Random) -> SimpleInflectionCurvatureCase:
    for _ in range(700):
        root = float(rng.choice(_SPECIAL_QUINTIC_TRIPLE_ROOT_VALUES))
        scale = float(rng.choice(_SPECIAL_QUINTIC_TRIPLE_SCALES))
        first_derivative_shift = float(rng.choice(_FIRST_DERIVATIVE_SHIFTS))
        y_shift = float(rng.choice(_Y_SHIFTS))

        triple_factor = multiply_polynomials(
            multiply_polynomials((1.0, -root), (1.0, -root)),
            (1.0, -root),
        )
        second_derivative_case = PolynomialCase(scale_polynomial(triple_factor, scale))
        function_case = _integrate_twice(
            second_derivative_case,
            first_constant=first_derivative_shift,
            second_constant=y_shift,
        )

        try:
            function_case, second_derivative_case = _normalize_function_scale(
                function_case,
                second_derivative_case,
                (root,),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, second_derivative_case, (root,)):
            continue

        return _build_special_inflection_case(function_case, second_derivative_case, (root,))

    raise ValueError("Konnte keinen quintischen Spezialfall mit dreifacher Nullstelle erzeugen.")


def _sample_special_quintic_mixed_case(rng: random.Random) -> SimpleInflectionCurvatureCase:
    for _ in range(900):
        double_root = float(rng.choice(_SPECIAL_QUINTIC_MIXED_DOUBLE_ROOT_VALUES))
        simple_root = float(rng.choice(_SPECIAL_QUINTIC_MIXED_SIMPLE_ROOT_VALUES))
        if abs(simple_root - double_root) < _MIN_ROOT_GAP:
            continue

        scale = float(rng.choice(_SPECIAL_QUINTIC_MIXED_SCALES))
        first_derivative_shift = float(rng.choice(_FIRST_DERIVATIVE_SHIFTS))
        y_shift = float(rng.choice(_Y_SHIFTS))
        second_derivative_case = PolynomialCase(
            scale_polynomial(
                multiply_polynomials(
                    multiply_polynomials((1.0, -double_root), (1.0, -double_root)),
                    (1.0, -simple_root),
                ),
                scale,
            )
        )
        function_case = _integrate_twice(
            second_derivative_case,
            first_constant=first_derivative_shift,
            second_constant=y_shift,
        )

        try:
            function_case, second_derivative_case = _normalize_function_scale(
                function_case,
                second_derivative_case,
                tuple(sorted((double_root, simple_root))),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, second_derivative_case, (double_root, simple_root)):
            continue

        return _build_special_inflection_case(function_case, second_derivative_case, (double_root, simple_root))

    raise ValueError("Konnte keinen quintischen Spezialfall mit Wende- und Nichtwendestelle erzeugen.")


def _integrate_twice(
    case: PolynomialCase,
    *,
    first_constant: float,
    second_constant: float,
) -> PolynomialCase:
    return integrate_polynomial(
        integrate_polynomial(case, constant=first_constant),
        constant=second_constant,
    )


def _apply_function_multiplier(
    function_case: PolynomialCase,
    derivative_case: PolynomialCase,
    multiplier: float,
) -> tuple[PolynomialCase, PolynomialCase]:
    if abs(multiplier - 1.0) < 1e-9:
        return function_case, derivative_case
    return (
        PolynomialCase(scale_polynomial(function_case.coeffs, multiplier)),
        PolynomialCase(scale_polynomial(derivative_case.coeffs, multiplier)),
    )


def _normalize_function_scale(
    function_case: PolynomialCase,
    derivative_case: PolynomialCase,
    candidates: tuple[float, ...],
    *,
    preferred_decimal_targets: tuple[int, ...],
) -> tuple[PolynomialCase, PolynomialCase]:
    for max_decimals in preferred_decimal_targets:
        for multiplier in _CLEANUP_MULTIPLIERS:
            scaled_function, scaled_derivative = _apply_function_multiplier(
                function_case,
                derivative_case,
                multiplier,
            )
            if not _fits_bounds(scaled_function, scaled_derivative, candidates):
                continue
            if _coefficients_fit_decimal_budget(scaled_function, max_decimals=max_decimals):
                return scaled_function, scaled_derivative

    raise ValueError("Konnte keine saubere Skalierung ohne Rundungskoeffizienten finden.")


def _fits_bounds(
    function_case: PolynomialCase,
    derivative_case: PolynomialCase,
    candidates: tuple[float, ...],
) -> bool:
    if max(abs(value) for value in function_case.coeffs) > _MAX_FUNCTION_COEFF_ABS:
        return False
    if max(abs(value) for value in derivative_case.coeffs) > _MAX_DERIVATIVE_COEFF_ABS:
        return False

    sample_x = _local_probe_points(candidates)
    function_abs = max(abs(function_case.evaluate(x_value)) for x_value in sample_x)
    derivative_abs = max(abs(derivative_case.evaluate(x_value)) for x_value in sample_x)
    return function_abs <= _MAX_FUNCTION_ABS and derivative_abs <= _MAX_DERIVATIVE_ABS


def _coefficients_fit_decimal_budget(case: PolynomialCase, *, max_decimals: int) -> bool:
    for coefficient in case.coeffs:
        if abs(coefficient) < 1e-9:
            continue
        if _required_decimals(coefficient, max_decimals=max_decimals) is None:
            return False
    return True


def _required_decimals(value: float, *, max_decimals: int) -> int | None:
    for decimals in range(max_decimals + 1):
        if abs(value - round(value, decimals)) < 1e-9:
            return decimals
    return None


def _local_probe_points(candidates: tuple[float, ...]) -> tuple[float, ...]:
    if not candidates:
        return tuple(float(value) for value in range(-3, 4))

    center = sum(candidates) / len(candidates)
    points = {round(center + offset, 4) for offset in (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)}
    for candidate in candidates:
        points.update(round(candidate + offset, 4) for offset in (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5))
    return tuple(sorted(point for point in points if -10.0 <= point <= 10.0))


def _point_from_x(case: PolynomialCase, x_value: float | None) -> tuple[float, float] | None:
    if x_value is None:
        return None
    return (_rounded_value(x_value), _rounded_value(case.evaluate(x_value)))


def _build_special_case(
    function_case: PolynomialCase,
    derivative_case: PolynomialCase,
    raw_candidates: tuple[float, ...],
) -> SimpleExtremMonotonicityCase:
    sorted_candidates = tuple(sorted(raw_candidates))
    signed_intervals = _signed_intervals(derivative_case, sorted_candidates)

    high_values: list[float] = []
    low_values: list[float] = []
    saddle_values: list[float] = []

    for index, candidate in enumerate(sorted_candidates):
        left_sign = signed_intervals[index][1]
        right_sign = signed_intervals[index + 1][1]
        rounded_candidate = _rounded_value(candidate)

        if left_sign > 0 and right_sign < 0:
            high_values.append(rounded_candidate)
        elif left_sign < 0 and right_sign > 0:
            low_values.append(rounded_candidate)
        else:
            saddle_values.append(rounded_candidate)

    if len(high_values) > 1 or len(low_values) > 1 or len(saddle_values) > 1:
        raise ValueError("Spezialfall erzeugt mehr als einen Punkt pro Kategorie.")

    increasing_intervals, decreasing_intervals = _merged_monotonicity_intervals(signed_intervals)
    high_x = high_values[0] if high_values else None
    low_x = low_values[0] if low_values else None
    saddle_x = saddle_values[0] if saddle_values else None

    return SimpleExtremMonotonicityCase(
        function_case=function_case,
        derivative_case=derivative_case,
        candidate_xs=tuple(_rounded_value(value) for value in sorted_candidates),
        high_x=high_x,
        low_x=low_x,
        high_point=_point_from_x(function_case, high_x),
        low_point=_point_from_x(function_case, low_x),
        increasing_intervals=increasing_intervals,
        decreasing_intervals=decreasing_intervals,
        saddle_x=saddle_x,
    )


def _build_special_inflection_case(
    function_case: PolynomialCase,
    second_derivative_case: PolynomialCase,
    raw_candidates: tuple[float, ...],
) -> SimpleInflectionCurvatureCase:
    sorted_candidates = tuple(sorted(raw_candidates))
    signed_intervals = _signed_intervals(second_derivative_case, sorted_candidates)

    inflection_values: list[float] = []
    for index, candidate in enumerate(sorted_candidates):
        left_sign = signed_intervals[index][1]
        right_sign = signed_intervals[index + 1][1]
        if left_sign != right_sign:
            inflection_values.append(_rounded_value(candidate))

    if len(inflection_values) > 1:
        raise ValueError("Spezialfall erzeugt mehr Wendestellen als der Check beantworten kann.")

    left_curved_intervals, right_curved_intervals = _merged_curvature_intervals(signed_intervals)
    return SimpleInflectionCurvatureCase(
        function_case=function_case,
        second_derivative_case=second_derivative_case,
        candidate_xs=tuple(_rounded_value(value) for value in sorted_candidates),
        inflection_xs=tuple(inflection_values),
        left_curved_intervals=left_curved_intervals,
        right_curved_intervals=right_curved_intervals,
    )


def _classify_monotonicity(
    derivative_case: PolynomialCase,
    candidates: tuple[float, ...],
) -> tuple[tuple[tuple[float | None, float | None], ...], tuple[tuple[float | None, float | None], ...]]:
    increasing: list[tuple[float | None, float | None]] = []
    decreasing: list[tuple[float | None, float | None]] = []

    for interval_bounds in _intervals_from_candidates(candidates):
        sample_x = _sample_point(interval_bounds)
        derivative_value = derivative_case.evaluate(sample_x)
        if derivative_value > 0:
            increasing.append(interval_bounds)
        elif derivative_value < 0:
            decreasing.append(interval_bounds)

    return tuple(increasing), tuple(decreasing)


def _classify_curvature(
    second_derivative_case: PolynomialCase,
    candidates: tuple[float, ...],
) -> tuple[tuple[tuple[float | None, float | None], ...], tuple[tuple[float | None, float | None], ...]]:
    return _classify_monotonicity(second_derivative_case, candidates)


def _signed_intervals(
    derivative_case: PolynomialCase,
    candidates: tuple[float, ...],
) -> tuple[tuple[tuple[float | None, float | None], int], ...]:
    signed: list[tuple[tuple[float | None, float | None], int]] = []

    for interval_bounds in _intervals_from_candidates(candidates):
        sample_x = _sample_point(interval_bounds)
        derivative_value = derivative_case.evaluate(sample_x)
        if derivative_value > 1e-9:
            signed.append((interval_bounds, 1))
            continue
        if derivative_value < -1e-9:
            signed.append((interval_bounds, -1))
            continue
        raise ValueError("Vorzeichen von f' konnte in einem Teilintervall nicht bestimmt werden.")

    return tuple(signed)


def _merged_monotonicity_intervals(
    signed_intervals: tuple[tuple[tuple[float | None, float | None], int], ...],
) -> tuple[tuple[tuple[float | None, float | None], ...], tuple[tuple[float | None, float | None], ...]]:
    merged: list[tuple[float | None, float | None, int]] = []

    for interval_bounds, sign in signed_intervals:
        left, right = interval_bounds
        if merged and merged[-1][2] == sign:
            previous_left, _, previous_sign = merged[-1]
            merged[-1] = (previous_left, right, previous_sign)
        else:
            merged.append((left, right, sign))

    increasing = tuple((left, right) for left, right, sign in merged if sign > 0)
    decreasing = tuple((left, right) for left, right, sign in merged if sign < 0)
    return increasing, decreasing


def _merged_curvature_intervals(
    signed_intervals: tuple[tuple[tuple[float | None, float | None], int], ...],
) -> tuple[tuple[tuple[float | None, float | None], ...], tuple[tuple[float | None, float | None], ...]]:
    return _merged_monotonicity_intervals(signed_intervals)


def _intervals_from_candidates(
    candidates: tuple[float, ...],
) -> tuple[tuple[float | None, float | None], ...]:
    sorted_candidates = tuple(sorted(candidates))
    bounds: list[tuple[float | None, float | None]] = []
    previous: float | None = None
    for candidate in sorted_candidates:
        bounds.append((previous, candidate))
        previous = candidate
    bounds.append((previous, None))
    return tuple(bounds)


def _sample_point(interval_bounds: tuple[float | None, float | None]) -> float:
    left, right = interval_bounds
    if left is None and right is None:
        return 0.0
    if left is None:
        return float(right - 1.0)
    if right is None:
        return float(left + 1.0)
    return 0.5 * (left + right)


def _rounded_value(value: float) -> float:
    if abs(value) < 1e-9:
        return 0.0
    return round(float(value), 4)