import math
import random


def round_sig(value: float, digits: int = 2) -> float:
    if value == 0:
        return 0.0
    exponent = math.floor(math.log10(abs(value)))
    factor = 10 ** (digits - 1 - exponent)
    rounded = round(value * factor) / factor
    if abs(rounded) < 1e-12:
        return 0.0
    return rounded


def uniform_sig(rng: random.Random, lower: float, upper: float, digits: int = 2) -> float:
    if lower > upper:
        raise ValueError("lower must be <= upper")
    if digits < 1:
        raise ValueError("digits must be >= 1")

    # Sample directly from a finite grid with at most `digits` significant digits.
    # This avoids post-hoc rounding of continuously sampled values.
    max_mantissa = (10 ** digits) - 1
    candidates: list[float] = []

    if lower <= 0.0 <= upper:
        candidates.append(0.0)

    abs_max = max(abs(lower), abs(upper))
    if abs_max > 0.0:
        exp_max = int(math.floor(math.log10(abs_max)))
    else:
        exp_max = 0
    exp_min = exp_max - 12

    eps = 1e-12 * max(1.0, abs_max)
    for exponent in range(exp_min, exp_max + 1):
        scale = 10.0 ** exponent
        for mantissa in range(1, max_mantissa + 1):
            base = mantissa * scale
            for signed in (base, -base):
                if lower - eps <= signed <= upper + eps:
                    candidates.append(0.0 if abs(signed) < 1e-12 else signed)

    if not candidates:
        raise ValueError("No value with requested significant digits in interval")

    return rng.choice(candidates)


def _sig_digits_int(value: int) -> int:
    if value == 0:
        return 1
    text = str(abs(value)).rstrip("0")
    return len(text)


def randint_sig(rng: random.Random, lower: int, upper: int, digits: int = 2) -> int:
    if lower > upper:
        raise ValueError("lower must be <= upper")

    candidates = [number for number in range(lower, upper + 1) if _sig_digits_int(number) <= digits]
    if candidates:
        return rng.choice(candidates)

    sampled = rng.randint(lower, upper)
    rounded = int(round_sig(float(sampled), digits=digits))
    return min(upper, max(lower, rounded))
