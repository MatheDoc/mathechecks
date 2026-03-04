import math


def binom_pmf(n: int, p: float, k: int) -> float:
    if k < 0 or k > n:
        return 0.0
    return math.comb(n, k) * (p**k) * ((1 - p) ** (n - k))


def binom_cdf(n: int, p: float, k: int) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(binom_pmf(n=n, p=p, k=i) for i in range(k + 1))


def prob_exactly(n: int, p: float, k: int) -> float:
    return binom_pmf(n=n, p=p, k=k)


def prob_at_least(n: int, p: float, k: int) -> float:
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return 1.0 - binom_cdf(n=n, p=p, k=k - 1)


def prob_less_than(n: int, p: float, k: int) -> float:
    return binom_cdf(n=n, p=p, k=k - 1)


def prob_between_open_closed(n: int, p: float, lower_open: int, upper_closed: int) -> float:
    if upper_closed <= lower_open:
        return 0.0
    start = lower_open + 1
    end = upper_closed
    start = max(start, 0)
    end = min(end, n)
    if start > end:
        return 0.0
    return sum(binom_pmf(n=n, p=p, k=i) for i in range(start, end + 1))


def prob_at_most_or_at_least(n: int, p: float, at_most: int, at_least: int) -> float:
    left = binom_cdf(n=n, p=p, k=at_most)
    right = 1.0 - binom_cdf(n=n, p=p, k=at_least - 1)
    return left + right


def percent_to_threshold_floor(n: int, percent_value: int) -> int:
    return math.floor(n * percent_value / 100)


def percent_to_threshold_ceil(n: int, percent_value: int) -> int:
    return math.ceil(n * percent_value / 100)


def max_successes_for_less_than(bound: float) -> int:
    return math.ceil(bound) - 1


def max_successes_for_at_most(bound: float) -> int:
    return math.floor(bound)


def min_successes_for_at_least(bound: float) -> int:
    return math.ceil(bound)


def min_successes_for_more_than(bound: float) -> int:
    return math.floor(bound) + 1


def max_successes_for_min_failure_percent(n: int, percent_value: int) -> int:
    min_failures = math.ceil(n * percent_value / 100)
    return n - min_failures


def min_successes_for_max_failure_percent(n: int, percent_value: int) -> int:
    max_failures = math.floor(n * percent_value / 100)
    return n - max_failures


def is_probability_boundary(value: float, epsilon: float = 1e-12) -> bool:
    return value <= epsilon or value >= (1.0 - epsilon)


def rounds_to_extreme_without_boundary(
    value: float,
    decimals: int = 4,
    epsilon: float = 1e-12,
) -> bool:
    if is_probability_boundary(value=value, epsilon=epsilon):
        return False
    rounded = round(value, decimals)
    return rounded <= 0.0 or rounded >= 1.0


def violates_probability_rounding_policy(
    probabilities: list[float],
    decimals: int = 4,
    epsilon: float = 1e-12,
) -> bool:
    return any(
        rounds_to_extreme_without_boundary(
            value=value,
            decimals=decimals,
            epsilon=epsilon,
        )
        for value in probabilities
    )
