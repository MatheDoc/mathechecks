"""Generator fuer Check 13 - Globale Extremwerte der Steigung auf Intervallen."""

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
    sample_simple_inflection_curvature_case,
)
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    PolynomialCase,
    integrate_polynomial,
    multiply_polynomials,
    polynomial_latex,
    scale_polynomial,
)


_DOMAIN_VARIANTS = ("finite", "left_unbounded", "right_unbounded", "all_reals")
_NON_ALL_REAL_DEGREES = (3, 4, 5)
_QUINTIC_ROOT_VALUES = tuple(value / 2.0 for value in range(-10, 11))
_QUINTIC_SCALES = (-1.0, -0.5, 0.5, 1.0)
_FIRST_DERIVATIVE_SHIFTS = tuple(float(value) for value in range(-6, 7))
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
class _BaseSlopeCase:
    function_case: PolynomialCase
    slope_case: PolynomialCase
    inflection_points: tuple[float, ...]


@dataclass(frozen=True)
class _SlopeCandidate:
    location: float | str
    value: float | str
    source: str


@dataclass(frozen=True)
class GlobalSlopeExtremaIntervalCase:
    function_case: PolynomialCase
    domain: _DomainSpec
    global_max: _SlopeCandidate
    global_min: _SlopeCandidate

    def signature(self) -> tuple[object, ...]:
        return (
            *self.function_case.signature(),
            *self.domain.signature(),
            self.global_max.location,
            self.global_max.value,
            self.global_min.location,
            self.global_min.value,
        )


class GlobaleSteigungsextremaIntervalleGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.globale_steigungsextrema_intervalle"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[object, ...]] = set()

        for degree, variant in _balanced_specs(count, rng):
            for _ in range(1200):
                case = sample_global_slope_extrema_interval_case(rng, degree=degree, domain_variant=variant)
                if case.signature() in used:
                    continue
                used.add(case.signature())
                tasks.append(_build_task(case))
                break
            else:
                raise ValueError("Konnte nicht genug Aufgaben zu globalen Steigungsextrema erzeugen.")

        return tasks


def _balanced_specs(count: int, rng: random.Random) -> list[tuple[int, str]]:
    variants = [_DOMAIN_VARIANTS[index % len(_DOMAIN_VARIANTS)] for index in range(count)]
    rng.shuffle(variants)

    specs: list[tuple[int, str]] = []
    degree_index = 0
    for variant in variants:
        if variant == "all_reals":
            specs.append((4, variant))
            continue
        degree = _NON_ALL_REAL_DEGREES[degree_index % len(_NON_ALL_REAL_DEGREES)]
        degree_index += 1
        specs.append((degree, variant))

    return specs


def sample_global_slope_extrema_interval_case(
    rng: random.Random,
    *,
    degree: int,
    domain_variant: str,
) -> GlobalSlopeExtremaIntervalCase:
    for _ in range(600):
        base_case = _sample_base_slope_case(rng, degree=degree)
        domains = _candidate_domains(base_case.inflection_points, domain_variant=domain_variant)
        if not domains:
            continue
        rng.shuffle(domains)

        for domain in domains:
            max_candidate, min_candidate = _analyze_global_slope_extrema(base_case, domain)
            if max_candidate is None or min_candidate is None:
                continue
            if not _outputs_are_clean(max_candidate, min_candidate):
                continue
            return GlobalSlopeExtremaIntervalCase(
                function_case=base_case.function_case,
                domain=domain,
                global_max=max_candidate,
                global_min=min_candidate,
            )

    raise ValueError("Konnte keinen geeigneten Fall fuer globale Steigungsextrema erzeugen.")


def _sample_base_slope_case(rng: random.Random, *, degree: int) -> _BaseSlopeCase:
    if degree in (3, 4):
        case = sample_simple_inflection_curvature_case(rng, degree=degree)
        return _BaseSlopeCase(
            function_case=case.function_case,
            slope_case=case.function_case.derivative(),
            inflection_points=tuple(sorted(case.inflection_xs)),
        )
    if degree == 5:
        return _sample_quintic_base_case(rng)
    raise ValueError("Nur Grade 3, 4 und 5 werden fuer globale Steigungsextrema unterstuetzt.")


def _sample_quintic_base_case(rng: random.Random) -> _BaseSlopeCase:
    for _ in range(900):
        roots = sorted(float(value) for value in rng.sample(_QUINTIC_ROOT_VALUES, 3))
        if roots[1] - roots[0] < _MIN_ROOT_GAP or roots[2] - roots[1] < _MIN_ROOT_GAP:
            continue

        scale = float(rng.choice(_QUINTIC_SCALES))
        first_derivative_shift = float(rng.choice(_FIRST_DERIVATIVE_SHIFTS))
        y_shift = float(rng.choice(_Y_SHIFTS))
        second_derivative_case = PolynomialCase(
            scale_polynomial(
                multiply_polynomials((1.0, -roots[0]), (1.0, -roots[1]), (1.0, -roots[2])),
                scale,
            )
        )
        slope_case = integrate_polynomial(second_derivative_case, constant=first_derivative_shift)
        function_case = integrate_polynomial(slope_case, constant=y_shift)

        try:
            function_case, second_derivative_case = _normalize_function_scale(
                function_case,
                second_derivative_case,
                tuple(roots),
                preferred_decimal_targets=(1, 2),
            )
        except ValueError:
            continue

        if not _fits_bounds(function_case, second_derivative_case, tuple(roots)):
            continue

        third_derivative = function_case.derivative(3)
        if any(abs(third_derivative.evaluate(root)) < 1e-9 for root in roots):
            continue

        return _BaseSlopeCase(
            function_case=function_case,
            slope_case=function_case.derivative(),
            inflection_points=tuple(_rounded_value(root) for root in roots),
        )

    raise ValueError("Konnte keinen quintischen Grundfall fuer globale Steigungsextrema erzeugen.")


def _candidate_domains(
    inflection_points: tuple[float, ...],
    *,
    domain_variant: str,
) -> list[_DomainSpec]:
    if domain_variant == "all_reals":
        return [_DomainSpec(left=None, right=None)]

    endpoint_pool = _endpoint_pool(inflection_points)
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


def _endpoint_pool(inflection_points: tuple[float, ...]) -> tuple[float, ...]:
    candidates = set(_FINITE_ENDPOINT_VALUES)
    for point in inflection_points:
        for offset in _ENDPOINT_OFFSETS:
            candidates.add(round(point + offset, 4))

    return tuple(
        sorted(
            value
            for value in candidates
            if -7.0 <= value <= 7.0 and all(abs(value - point) >= 0.4 for point in inflection_points)
        )
    )


def _analyze_global_slope_extrema(
    base_case: _BaseSlopeCase,
    domain: _DomainSpec,
) -> tuple[_SlopeCandidate | None, _SlopeCandidate | None]:
    candidates: list[_SlopeCandidate] = []

    for point in base_case.inflection_points:
        if _point_in_domain(point, domain):
            candidates.append(
                _SlopeCandidate(
                    location=_rounded_value(point),
                    value=_rounded_value(base_case.slope_case.evaluate(point)),
                    source="interior",
                )
            )

    if domain.left is None:
        candidates.append(
            _SlopeCandidate(
                location="NEG_INF",
                value=_limit_at_neg_inf(base_case.slope_case),
                source="neg_inf",
            )
        )
    else:
        candidates.append(
            _SlopeCandidate(
                location=_rounded_value(domain.left),
                value=_rounded_value(base_case.slope_case.evaluate(domain.left)),
                source="left_boundary",
            )
        )

    if domain.right is None:
        candidates.append(
            _SlopeCandidate(
                location="POS_INF",
                value=_limit_at_pos_inf(base_case.slope_case),
                source="pos_inf",
            )
        )
    else:
        candidates.append(
            _SlopeCandidate(
                location=_rounded_value(domain.right),
                value=_rounded_value(base_case.slope_case.evaluate(domain.right)),
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


def _limit_at_pos_inf(case: PolynomialCase) -> str:
    return "POS_INF" if case.coeffs[0] > 0 else "NEG_INF"


def _limit_at_neg_inf(case: PolynomialCase) -> str:
    if case.degree % 2 == 0:
        return "POS_INF" if case.coeffs[0] > 0 else "NEG_INF"
    return "NEG_INF" if case.coeffs[0] > 0 else "POS_INF"


def _unique_best_candidate(
    candidates: list[_SlopeCandidate],
    *,
    pick_max: bool,
) -> _SlopeCandidate | None:
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


def _outputs_are_clean(max_candidate: _SlopeCandidate, min_candidate: _SlopeCandidate) -> bool:
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


def _build_task(case: GlobalSlopeExtremaIntervalCase) -> Task:
    intro = (
        f"Gegeben ist die Funktion $$ {polynomial_latex(case.function_case, name='f')} $$ "
        f"mit Definitionsbereich $D={case.domain.latex()}$. "
        "Falls der Definitionsbereich endliche Randpunkte hat, sind diese enthalten und werden daher mit eckigen Klammern notiert. "
        "Für unbeschränkte Stellen oder Steigungswerte tragen Sie $-\\infty$ bzw. $+\\infty$ ein, "
        "zum Beispiel als '-inf' bzw. '+inf'. "
        "Bestimmen Sie"
    )
    return Task(
        einleitung=intro,
        fragen=[
            "an welcher Stelle die Steigung global maximal ist und welchen Wert diese maximale Steigung hat.",
            "an welcher Stelle die Steigung global minimal ist und welchen Wert diese minimale Steigung hat.",
        ],
        antworten=[
            _slope_extremum_answer(case.global_max, kind="max"),
            _slope_extremum_answer(case.global_min, kind="min"),
        ],
    )


def _slope_extremum_answer(candidate: _SlopeCandidate, *, kind: str) -> str:
    kind_tex = r"\max" if kind == "max" else r"\min"
    x_placeholder = _analysis_bound_placeholder(candidate.location)
    m_placeholder = _analysis_bound_placeholder(candidate.value)
    return f"$x_{{{kind_tex}}}=${x_placeholder} $\\quad m_{{{kind_tex}}}=${m_placeholder}"


def _analysis_bound_placeholder(value: float | str) -> str:
    if value == "NEG_INF":
        return analysis_bound_neg_inf()
    if value == "POS_INF":
        return analysis_bound_pos_inf()
    return analysis_bound_analysis(float(value))