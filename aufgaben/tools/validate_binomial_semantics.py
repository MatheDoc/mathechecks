from aufgaben.generators.stochastik.binomialverteilung.shared import (
    binom_cdf,
    max_successes_for_at_most,
    max_successes_for_less_than,
    max_successes_for_min_failure_percent,
    min_successes_for_at_least,
    min_successes_for_max_failure_percent,
    min_successes_for_more_than,
    prob_at_least,
    prob_less_than,
    violates_probability_rounding_policy,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def _assert_close(actual: float, expected: float, label: str, tol: float = 1e-12) -> None:
    if abs(actual - expected) > tol:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def check_wording_thresholds() -> None:
    _assert_equal(max_successes_for_less_than(3), 2, "weniger als 3 -> höchstens 2")
    _assert_equal(max_successes_for_less_than(3.0), 2, "weniger als 3.0 -> höchstens 2")
    _assert_equal(max_successes_for_less_than(4.9), 4, "weniger als 4.9 -> höchstens 4")

    _assert_equal(max_successes_for_at_most(4.9), 4, "höchstens 4.9 -> höchstens 4")
    _assert_equal(min_successes_for_at_least(4.1), 5, "mindestens 4.1 -> mindestens 5")
    _assert_equal(min_successes_for_more_than(4.0), 5, "mehr als 4 -> mindestens 5")


def check_probability_equivalences() -> None:
    n = 7
    p = 0.3

    left = prob_less_than(n=n, p=p, k=4)
    right = binom_cdf(n=n, p=p, k=3)
    _assert_close(left, right, "P(X < 4) = P(X <= 3)")

    decimal_case = prob_less_than(n=n, p=p, k=max_successes_for_less_than(4.9) + 1)
    expected_decimal = binom_cdf(n=n, p=p, k=4)
    _assert_close(decimal_case, expected_decimal, "P(X < 4.9) = P(X <= 4)")


def check_percent_failure_boundaries() -> None:
    n = 7

    _assert_equal(
        min_successes_for_max_failure_percent(n=n, percent_value=70),
        3,
        "höchstens 70% Misserfolg -> mindestens 3 Erfolge",
    )
    _assert_equal(
        max_successes_for_min_failure_percent(n=n, percent_value=70),
        2,
        "mindestens 70% Misserfolg -> höchstens 2 Erfolge",
    )
    _assert_equal(
        min_successes_for_max_failure_percent(n=n, percent_value=71),
        3,
        "höchstens 71% Misserfolg -> mindestens 3 Erfolge",
    )
    _assert_equal(
        max_successes_for_min_failure_percent(n=n, percent_value=71),
        2,
        "mindestens 71% Misserfolg -> höchstens 2 Erfolge",
    )

    p = 0.3
    prob_max_70_fail = prob_at_least(n=n, p=p, k=min_successes_for_max_failure_percent(n=n, percent_value=70))
    prob_min_70_fail = prob_less_than(
        n=n,
        p=p,
        k=max_successes_for_min_failure_percent(n=n, percent_value=70) + 1,
    )
    _assert_close(
        prob_max_70_fail + prob_min_70_fail,
        1.0,
        "Komplementcheck für 70%-Misserfolgsgrenzen",
        tol=1e-12,
    )


def check_rounding_policy() -> None:
    values_ok = [0.0, 1.0, 0.1234, 0.9998]
    if violates_probability_rounding_policy(values_ok, decimals=4):
        raise AssertionError("Rundungspolicy meldet fälschlich einen Verstoß bei gültigen Werten.")

    tiny_positive = 0.9**100
    almost_one = 1.0 - tiny_positive
    values_bad = [tiny_positive, almost_one]
    if not violates_probability_rounding_policy(values_bad, decimals=4):
        raise AssertionError("Rundungspolicy erkennt erwarteten Verstoß nicht.")


def main() -> None:
    check_wording_thresholds()
    check_probability_equivalences()
    check_percent_failure_boundaries()
    check_rounding_policy()
    print("OK: Binomial-Semantik und Rundungspolicy validiert.")


if __name__ == "__main__":
    main()
