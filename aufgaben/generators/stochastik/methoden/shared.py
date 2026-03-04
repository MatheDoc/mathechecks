import random
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from aufgaben.generators.stochastik.methoden.textbausteine import ABScenarioTemplate


_Q2 = Decimal("0.01")
_Q4 = Decimal("0.0001")


def _round4(value: Decimal) -> Decimal:
    return value.quantize(_Q4, rounding=ROUND_HALF_UP)


def _to_float(value: Decimal) -> float:
    return float(value)


@dataclass(frozen=True)
class ABCase:
    scenario: ABScenarioTemplate
    p_a: float
    p_not_a: float
    p_b_given_a: float
    p_not_b_given_a: float
    p_b_given_not_a: float
    p_not_b_given_not_a: float
    p_a_and_b: float
    p_a_and_not_b: float
    p_not_a_and_b: float
    p_not_a_and_not_b: float


def sample_ab_case(rng: random.Random, scenario: ABScenarioTemplate) -> ABCase:
    p_a = Decimal(rng.randint(20, 80)) * _Q2
    p_b_given_a = Decimal(rng.randint(15, 85)) * _Q2
    p_b_given_not_a = Decimal(rng.randint(15, 85)) * _Q2

    p_not_a = _round4(Decimal("1") - p_a)
    p_not_b_given_a = _round4(Decimal("1") - p_b_given_a)
    p_not_b_given_not_a = _round4(Decimal("1") - p_b_given_not_a)

    p_a_and_b = _round4(p_a * p_b_given_a)
    p_a_and_not_b = _round4(p_a * p_not_b_given_a)
    p_not_a_and_b = _round4(p_not_a * p_b_given_not_a)
    p_not_a_and_not_b = _round4(p_not_a * p_not_b_given_not_a)

    return ABCase(
        scenario=scenario,
        p_a=_to_float(p_a),
        p_not_a=_to_float(p_not_a),
        p_b_given_a=_to_float(p_b_given_a),
        p_not_b_given_a=_to_float(p_not_b_given_a),
        p_b_given_not_a=_to_float(p_b_given_not_a),
        p_not_b_given_not_a=_to_float(p_not_b_given_not_a),
        p_a_and_b=_to_float(p_a_and_b),
        p_a_and_not_b=_to_float(p_a_and_not_b),
        p_not_a_and_b=_to_float(p_not_a_and_b),
        p_not_a_and_not_b=_to_float(p_not_a_and_not_b),
    )
