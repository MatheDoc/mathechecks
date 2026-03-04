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


def sample_ab_case_independent(rng: random.Random, scenario: ABScenarioTemplate) -> ABCase:
    """Wie sample_ab_case, aber mit P(B|A) = P(B|¬A) (stochastische Unabhängigkeit)."""
    p_a = Decimal(rng.randint(20, 80)) * _Q2
    p_b = Decimal(rng.randint(15, 85)) * _Q2

    # Unabhängigkeit: bedingte Wahrscheinlichkeiten gleich der Randwahrscheinlichkeit
    p_b_given_a = p_b
    p_b_given_not_a = p_b

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


def vft_slots(case: ABCase) -> dict[int, float]:
    """Liefert alle 8 Felder der Vier-Felder-Tafel als {Slot-Nr: Wert}.

    Nummerierung (Projektstandard):
      1 = P(A∩B)    2 = P(A∩B̄)
      3 = P(Ā∩B)   4 = P(Ā∩B̄)
      5 = P(A)      6 = P(Ā)
      7 = P(B)      8 = P(B̄)
    """
    p_b = _to_float(_round4(Decimal(str(case.p_a_and_b)) + Decimal(str(case.p_not_a_and_b))))
    p_nb = _to_float(_round4(Decimal(str(case.p_a_and_not_b)) + Decimal(str(case.p_not_a_and_not_b))))
    return {
        1: case.p_a_and_b,
        2: case.p_a_and_not_b,
        3: case.p_not_a_and_b,
        4: case.p_not_a_and_not_b,
        5: case.p_a,
        6: case.p_not_a,
        7: p_b,
        8: p_nb,
    }


def extended_probs(case: ABCase) -> dict[str, float]:
    """Alle Wahrscheinlichkeiten für folgern-Generatoren (Einzel, Schnitt, Vereinigung, Spezial, Bedingt A/B)."""
    def _r(v: float) -> float:
        return _to_float(_round4(Decimal(str(v))))

    p_b = _r(case.p_a_and_b + case.p_not_a_and_b)
    p_nb = _r(case.p_a_and_not_b + case.p_not_a_and_not_b)
    return {
        "pa": case.p_a,
        "pna": case.p_not_a,
        "pb": p_b,
        "pnb": p_nb,
        "pab": case.p_a_and_b,
        "panb": case.p_a_and_not_b,
        "pnab": case.p_not_a_and_b,
        "pnanb": case.p_not_a_and_not_b,
        "paub": _r(1 - case.p_not_a_and_not_b),
        "paunb": _r(1 - case.p_not_a_and_b),
        "pnaub": _r(1 - case.p_a_and_not_b),
        "pnaunb": _r(1 - case.p_a_and_b),
        "symdiff": _r(case.p_a_and_not_b + case.p_not_a_and_b),
        "diag_sum": _r(case.p_a_and_b + case.p_not_a_and_not_b),
        "trivial_0": 0.0,
        "trivial_1": 1.0,
        "pba": case.p_b_given_a,
        "pnba": case.p_not_b_given_a,
        "pbna": case.p_b_given_not_a,
        "pnbna": case.p_not_b_given_not_a,
        "pab_c": _r(case.p_a_and_b / p_b) if p_b > 0 else 0.0,
        "pnab_c": _r(case.p_not_a_and_b / p_b) if p_b > 0 else 0.0,
        "panb_c": _r(case.p_a_and_not_b / p_nb) if p_nb > 0 else 0.0,
        "pnanb_c": _r(case.p_not_a_and_not_b / p_nb) if p_nb > 0 else 0.0,
    }
