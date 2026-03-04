import math
import random
from dataclasses import dataclass

from aufgaben.generators.stochastik.binomialverteilung.shared import (
    binom_cdf,
    rounds_to_extreme_without_boundary,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import ScenarioTemplate, SCENARIOS


@dataclass(frozen=True)
class OneSidedTestCase:
    scenario: ScenarioTemplate
    n: int
    p0: float
    critical_value: int
    alpha: float
    observed_x: int
    reject_h0: bool


def _sample_probability(rng: random.Random) -> float:
    return rng.choice([x / 100 for x in range(12, 69)])


def _sample_n(rng: random.Random) -> int:
    return rng.randint(45, 130)


def _sample_left_case(rng: random.Random) -> tuple[int, float, int, float]:
    for _ in range(300):
        n = _sample_n(rng)
        p0 = _sample_probability(rng)
        mu = n * p0
        sigma = math.sqrt(n * p0 * (1 - p0))
        z = rng.uniform(0.7, 1.9)
        critical = math.floor(mu - z * sigma)
        critical = max(1, min(n - 2, critical))

        alpha = binom_cdf(n=n, p=p0, k=critical)
        if 0.005 <= alpha <= 0.2 and not rounds_to_extreme_without_boundary(alpha, decimals=4):
            return n, p0, critical, alpha

    n = 80
    p0 = 0.35
    critical = 23
    alpha = binom_cdf(n=n, p=p0, k=critical)
    return n, p0, critical, alpha


def _sample_right_case(rng: random.Random) -> tuple[int, float, int, float]:
    for _ in range(300):
        n = _sample_n(rng)
        p0 = _sample_probability(rng)
        mu = n * p0
        sigma = math.sqrt(n * p0 * (1 - p0))
        z = rng.uniform(0.7, 1.9)
        critical = math.ceil(mu + z * sigma)
        critical = max(2, min(n - 1, critical))

        alpha = 1.0 - binom_cdf(n=n, p=p0, k=critical - 1)
        if 0.005 <= alpha <= 0.2 and not rounds_to_extreme_without_boundary(alpha, decimals=4):
            return n, p0, critical, alpha

    n = 80
    p0 = 0.35
    critical = 34
    alpha = 1.0 - binom_cdf(n=n, p=p0, k=critical - 1)
    return n, p0, critical, alpha


def _sample_observed_left(rng: random.Random, n: int, critical: int) -> tuple[int, bool]:
    reject = rng.choice([True, False])
    if reject:
        observed_x = rng.randint(0, critical)
    else:
        observed_x = rng.randint(critical + 1, n)
    return observed_x, reject


def _sample_observed_right(rng: random.Random, n: int, critical: int) -> tuple[int, bool]:
    reject = rng.choice([True, False])
    if reject:
        observed_x = rng.randint(critical, n)
    else:
        observed_x = rng.randint(0, critical - 1)
    return observed_x, reject


def sample_linksseitig(rng: random.Random) -> OneSidedTestCase:
    n, p0, critical, alpha = _sample_left_case(rng)
    observed_x, reject = _sample_observed_left(rng, n=n, critical=critical)
    scenario = rng.choice(SCENARIOS)
    return OneSidedTestCase(
        scenario=scenario,
        n=n,
        p0=p0,
        critical_value=critical,
        alpha=alpha,
        observed_x=observed_x,
        reject_h0=reject,
    )


def sample_rechtsseitig(rng: random.Random) -> OneSidedTestCase:
    n, p0, critical, alpha = _sample_right_case(rng)
    observed_x, reject = _sample_observed_right(rng, n=n, critical=critical)
    scenario = rng.choice(SCENARIOS)
    return OneSidedTestCase(
        scenario=scenario,
        n=n,
        p0=p0,
        critical_value=critical,
        alpha=alpha,
        observed_x=observed_x,
        reject_h0=reject,
    )


# ---------------------------------------------------------------------------
# Ablehnungsbereich – Entscheidungsregel herleiten
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AblehnungsbereichCase:
    scenario: ScenarioTemplate
    n: int
    p0: float
    alpha_requested: float   # vorgegebenes Signifikanzniveau-Limit (z. B. 0.05)
    critical_value: int      # tatsächlicher kritischer Wert k
    alpha: float             # tatsächliches Signifikanzniveau P(X ≤ k) bzw. P(X ≥ k)


_ALPHA_LEVELS = [0.05, 0.10]


def _find_critical_left(n: int, p0: float, alpha_req: float) -> tuple[int, float] | None:
    """Größtes k mit P(X ≤ k; n, p0) ≤ alpha_req."""
    best_k = -1
    for k in range(n + 1):
        if binom_cdf(n=n, p=p0, k=k) <= alpha_req:
            best_k = k
        else:
            break
    if best_k < 1:
        return None
    alpha = binom_cdf(n=n, p=p0, k=best_k)
    if rounds_to_extreme_without_boundary(alpha, decimals=4):
        return None
    return best_k, alpha


def _find_critical_right(n: int, p0: float, alpha_req: float) -> tuple[int, float] | None:
    """Kleinstes k mit P(X ≥ k; n, p0) ≤ alpha_req."""
    for k in range(1, n + 1):
        val = 1.0 - binom_cdf(n=n, p=p0, k=k - 1)
        if val <= alpha_req:
            if rounds_to_extreme_without_boundary(val, decimals=4):
                return None
            return k, val
    return None


def sample_ablehnungsbereich_links(rng: random.Random) -> AblehnungsbereichCase:
    for _ in range(500):
        n = _sample_n(rng)
        p0 = _sample_probability(rng)
        alpha_req = rng.choice(_ALPHA_LEVELS)
        result = _find_critical_left(n, p0, alpha_req)
        if result is None:
            continue
        k, alpha = result
        if alpha < 0.001:
            continue
        scenario = rng.choice(SCENARIOS)
        return AblehnungsbereichCase(
            scenario=scenario, n=n, p0=p0,
            alpha_requested=alpha_req, critical_value=k, alpha=alpha,
        )
    # Fallback
    n, p0, alpha_req = 80, 0.35, 0.05
    k, alpha = _find_critical_left(n, p0, alpha_req)  # type: ignore[misc]
    return AblehnungsbereichCase(
        scenario=SCENARIOS[0], n=n, p0=p0,
        alpha_requested=alpha_req, critical_value=k, alpha=alpha,
    )


def sample_ablehnungsbereich_rechts(rng: random.Random) -> AblehnungsbereichCase:
    for _ in range(500):
        n = _sample_n(rng)
        p0 = _sample_probability(rng)
        alpha_req = rng.choice(_ALPHA_LEVELS)
        result = _find_critical_right(n, p0, alpha_req)
        if result is None:
            continue
        k, alpha = result
        if alpha < 0.001:
            continue
        scenario = rng.choice(SCENARIOS)
        return AblehnungsbereichCase(
            scenario=scenario, n=n, p0=p0,
            alpha_requested=alpha_req, critical_value=k, alpha=alpha,
        )
    # Fallback
    n, p0, alpha_req = 80, 0.65, 0.05
    k, alpha = _find_critical_right(n, p0, alpha_req)  # type: ignore[misc]
    return AblehnungsbereichCase(
        scenario=SCENARIOS[0], n=n, p0=p0,
        alpha_requested=alpha_req, critical_value=k, alpha=alpha,
    )
