"""Generator fuer Check 12 - Globale Extremwerte auf Intervallen."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import random

from aufgaben.core.latex import fmt
from aufgaben.core.models import Task
from aufgaben.core.placeholders import (
    analysis_bound_analysis,
    analysis_bound_neg_inf,
    analysis_bound_pos_inf,
)
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.extrem_monotonie_shared import (
    _fits_bounds,
    _normalize_function_scale,
    _required_decimals,
    _rounded_value,
    interval_delimiters,
    sample_simple_extrem_monotonicity_case,
)
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    PolynomialCase,
    integrate_polynomial,
    multiply_polynomials,
    polynomial_latex,
    scale_polynomial,
)


_DOMAIN_VARIANTS = ("finite", "left_unbounded", "right_unbounded", "all_reals")
_NON_ALL_REAL_DEGREES = (2, 3, 4)
_QUARTIC_ROOT_VALUES = tuple(value / 2.0 for value in range(-10, 11))
_QUARTIC_SCALES = (-1.0, -0.5, 0.5, 1.0)
_Y_SHIFTS = tuple(float(value) for value in range(-6, 7))
_FINITE_ENDPOINT_VALUES = tuple(value / 2.0 for value in range(-14, 15))
_ENDPOINT_OFFSETS = (-3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
_MIN_ROOT_GAP = 1.5
_MIN_DOMAIN_WIDTH = 1.5
_MAX_DOMAIN_WIDTH = 10.0


@dataclass(frozen=True)
class _DomainSpec:
    left: float | None
    right: float | None

    def latex(self) -> str:
        left_text = r"-\infty" if self.left is None else fmt(self.left)
        right_text = r"\infty" if self.right is None else fmt(self.right)
        left_bracket, right_bracket = interval_delimiters(self.left, self.right)
        return f"{left_bracket}{left_text}; {right_text}{right_bracket}"

    def signature(self) -> tuple[float | str, float | str]:
        left = "NEG_INF" if self.left is None else round(float(self.left), 4)
        right = "POS_INF" if self.right is None else round(float(self.right), 4)
        return (left, right)


@dataclass(frozen=True)
class _BasePolynomialCase:
    function_case: PolynomialCase
    critical_points: tuple[float, ...]


@dataclass(frozen=True)
class _ExtremumCandidate:
    location: float | str
    value: float | str
    source: str


@dataclass(frozen=True)
class GlobalExtremaIntervalCase:
    function_case: PolynomialCase
    domain: _DomainSpec
    global_max: _ExtremumCandidate
    global_min: _ExtremumCandidate

    def signature(self) -> tuple[object, ...]:
        return (
            *self.function_case.signature(),
            *self.domain.signature(),
            self.global_max.location,
            self.global_max.value,
            self.global_min.location,
            self.global_min.value,
        )


class GlobaleExtremwerteIntervalleGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.globale_extremwerte_intervalle"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[object, ...]] = set()

        for degree, variant in _balanced_specs(count, rng):
            for _ in range(1200):
                case = sample_global_extrema_interval_case(rng, degree=degree, domain_variant=variant)
                if case.signature() in used:
                    continue
                used.add(case.signature())
                tasks.append(_build_task(case))
                break
            else:
                raise ValueError("Konnte nicht genug Aufgaben zu globalen Extremwerten erzeugen.")

        return tasks


def _balanced_specs(count: int, rng: random.Random) -> list[tuple[int, str]]:
    variants = [_DOMAIN_VARIANTS[index % len(_DOMAIN_VARIANTS)] for index in range(count)]
    rng.shuffle(variants)

    specs: list[tuple[int, str]] = []
    degree_index = 0
    for variant in variants:
        if variant == "all_reals":
            specs.append((3, variant))
            continue
        degree = _NON_ALL_REAL_DEGREES[degree_index % len(_NON_ALL_REAL_DEGREES)]
        degree_index += 1
        specs.append((degree, variant))

    return specs


def sample_global_extrema_interval_case(
    rng: random.Random,
    *,
    degree: int,
    domain_variant: str,
) -> GlobalExtremaIntervalCase:
    for _ in range(600):
        base_case = _sample_base_polynomial_case(rng, degree=degree)
        domains = _candidate_domains(base_case.critical_points, domain_variant=domain_variant)
        if not domains:
            continue
        rng.shuffle(domains)

        for domain in domains:
            max_candidate, min_candidate = _analyze_global_extrema(
                base_case.function_case,
                base_case.critical_points,
                domain,
            )
            if max_candidate is None or min_candidate is None:
                continue
            if not _outputs_are_clean(max_candidate, min_candidate):
                continue
            return GlobalExtremaIntervalCase(
                function_case=base_case.function_case,
                domain=domain,
                global_max=max_candidate,
                global_min=min_candidate,
            )

    raise ValueError("Konnte keinen geeigneten Fall fuer globale Extremwerte erzeugen.")


def _sample_base_polynomial_case(rng: random.Random, *, degree: int) -> _BasePolynomialCase:
    if degree in (2, 3):
        case = sample_simple_extrem_monotonicity_case(rng, degree=degree)
        return _BasePolynomialCase(
            function_case=case.function_case,
            critical_points=tuple(sorted(case.candidate_xs)),
        )
    if degree == 4:
        return _sample_quartic_base_case(rng)
    raise ValueError("Nur Grade 2, 3 und 4 werden fuer globale Extremwerte unterstuetzt.")


def _sample_quartic_base_case(rng: random.Random) -> _BasePolynomialCase:
    for _ in range(900):
        roots = sorted(float(value) for value in rng.sample(_QUARTIC_ROOT_VALUES, 3))
        if roots[1] - roots[0] < _MIN_ROOT_GAP or roots[2] - roots[1] < _MIN_ROOT_GAP:
            continue

        scale = float(rng.choice(_QUARTIC_SCALES))
        y_shift = float(rng.choice(_Y_SHIFTS))
        derivative_case = PolynomialCase(
            scale_polynomial(
                multiply_polynomials((1.0, -roots[0]), (1.0, -roots[1]), (1.0, -roots[2])),
                scale,
            )
        )
        function_case = integrate_polynomial(derivative_case, constant=y_shift)

        try:
            function_case, derivative_case = _normalize_function_scale(
                function_case,
                derivative_case,
                tuple(roots),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, derivative_case, tuple(roots)):
            continue

        second_derivative = function_case.derivative(2)
        if any(abs(second_derivative.evaluate(root)) < 1e-9 for root in roots):
            continue

        return _BasePolynomialCase(
            function_case=function_case,
            critical_points=tuple(_rounded_value(root) for root in roots),
        )

    raise ValueError("Konnte keinen quartischen Grundfall fuer globale Extremwerte erzeugen.")


def _candidate_domains(
    critical_points: tuple[float, ...],
    *,
    domain_variant: str,
) -> list[_DomainSpec]:
    if domain_variant == "all_reals":
        return [_DomainSpec(left=None, right=None)]

    endpoint_pool = _endpoint_pool(critical_points)
    if domain_variant == "finite":
        return [
            _DomainSpec(left=left, right=right)
            for left, right in combinations(endpoint_pool, 2)
            if _MIN_DOMAIN_WIDTH <= right - left <= _MAX_DOMAIN_WIDTH
        ]
    if domain_variant == "left_unbounded":
        return [_DomainSpec(left=None, right=right) for right in endpoint_pool]
    if domain_variant == "right_unbounded":
        return [_DomainSpec(left=left, right=None) for left in endpoint_pool]
    raise ValueError(f"Unbekannte Definitionsbereichsvariante: {domain_variant}")


def _endpoint_pool(critical_points: tuple[float, ...]) -> tuple[float, ...]:
    candidates = set(_FINITE_ENDPOINT_VALUES)
    for point in critical_points:
        for offset in _ENDPOINT_OFFSETS:
            candidates.add(round(point + offset, 4))

    return tuple(
        sorted(
            value
            for value in candidates
            if -7.0 <= value <= 7.0 and all(abs(value - point) >= 0.4 for point in critical_points)
        )
    )


def _analyze_global_extrema(
    function_case: PolynomialCase,
    critical_points: tuple[float, ...],
    domain: _DomainSpec,
) -> tuple[_ExtremumCandidate | None, _ExtremumCandidate | None]:
    candidates: list[_ExtremumCandidate] = []

    for point in critical_points:
        if _point_in_domain(point, domain):
            candidates.append(
                _ExtremumCandidate(
                    location=_rounded_value(point),
                    value=_rounded_value(function_case.evaluate(point)),
                    source="interior",
                )
            )

    if domain.left is None:
        candidates.append(
            _ExtremumCandidate(location="NEG_INF", value=_limit_at_neg_inf(function_case), source="neg_inf")
        )
    else:
        candidates.append(
            _ExtremumCandidate(
                location=_rounded_value(domain.left),
                value=_rounded_value(function_case.evaluate(domain.left)),
                source="left_boundary",
            )
        )

    if domain.right is None:
        candidates.append(
            _ExtremumCandidate(location="POS_INF", value=_limit_at_pos_inf(function_case), source="pos_inf")
        )
    else:
        candidates.append(
            _ExtremumCandidate(
                location=_rounded_value(domain.right),
                value=_rounded_value(function_case.evaluate(domain.right)),
                source="right_boundary",
            )
        )

    max_candidate = _unique_best_candidate(candidates, pick_max=True)
    min_candidate = _unique_best_candidate(candidates, pick_max=False)
    return max_candidate, min_candidate


def _point_in_domain(point: float, domain: _DomainSpec) -> bool:
    if domain.left is not None and point <= domain.left:
        return False
    if domain.right is not None and point >= domain.right:
        return False
    return True


def _limit_at_pos_inf(function_case: PolynomialCase) -> str:
    return "POS_INF" if function_case.coeffs[0] > 0 else "NEG_INF"


def _limit_at_neg_inf(function_case: PolynomialCase) -> str:
    if function_case.degree % 2 == 0:
        return "POS_INF" if function_case.coeffs[0] > 0 else "NEG_INF"
    return "NEG_INF" if function_case.coeffs[0] > 0 else "POS_INF"


def _unique_best_candidate(
    candidates: list[_ExtremumCandidate],
    *,
    pick_max: bool,
) -> _ExtremumCandidate | None:
    ordered = sorted(candidates, key=lambda candidate: _extended_sort_key(candidate.value), reverse=pick_max)
    if not ordered:
        return None
    if len(ordered) > 1 and _same_extended_value(ordered[0].value, ordered[1].value):
        return None
    return ordered[0]


def _extended_sort_key(value: float | str) -> tuple[int, float]:
    if value == "NEG_INF":
        return (-1, 0.0)
    if value == "POS_INF":
        return (1, 0.0)
    return (0, float(value))


def _same_extended_value(left: float | str, right: float | str) -> bool:
    if isinstance(left, str) or isinstance(right, str):
        return left == right
    return abs(float(left) - float(right)) < 1e-9


def _outputs_are_clean(max_candidate: _ExtremumCandidate, min_candidate: _ExtremumCandidate) -> bool:
    return all(
        _is_clean_output_value(value)
        for value in (
            max_candidate.location,
            max_candidate.value,
            min_candidate.location,
            min_candidate.value,
        )
    )


def _is_clean_output_value(value: float | str) -> bool:
    if isinstance(value, str):
        return True
    return _required_decimals(float(value), max_decimals=2) is not None


def _build_task(case: GlobalExtremaIntervalCase) -> Task:
    intro = (
        f"Gegeben ist die Funktion $$ {polynomial_latex(case.function_case, name='f')} $$ "
        f"mit Definitionsbereich $D={case.domain.latex()}$. "
        "Falls der Definitionsbereich endliche Randpunkte hat, sind diese enthalten und werden daher mit eckigen Klammern notiert. "
        "Für unbeschränkte Stellen oder Werte tragen Sie $-\\infty$ bzw. $+\\infty$ ein, "
        "zum Beispiel als '-inf' bzw. '+inf'. "
        "Bestimmen Sie"
    )
    return Task(
        einleitung=intro,
        fragen=[
            "an welcher Stelle das globale Maximum liegt und welchen Wert das globale Maximum hat.",
            "an welcher Stelle das globale Minimum liegt und welchen Wert das globale Minimum hat.",
        ],
        antworten=[
            _extremum_answer(case.global_max, kind="max"),
            _extremum_answer(case.global_min, kind="min"),
        ],
    )


def _extremum_answer(candidate: _ExtremumCandidate, *, kind: str) -> str:
    x_placeholder = _analysis_bound_placeholder(candidate.location)
    y_placeholder = _analysis_bound_placeholder(candidate.value)
    return f"$x_{{\\{kind}}}=${x_placeholder} $\\quad y_{{\\{kind}}}=${y_placeholder}"


def _analysis_bound_placeholder(value: float | str) -> str:
    if value == "NEG_INF":
        return analysis_bound_neg_inf()
    if value == "POS_INF":
        return analysis_bound_pos_inf()
    return analysis_bound_analysis(float(value))