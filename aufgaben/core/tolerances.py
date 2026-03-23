import math


# Zentrale Rundungspolicies fuer berechnete Werte.
ANALYSIS_CALC_DECIMALS = 2
ANALYSIS_CALC_TOLERANCE = 0.01

STOCHASTIK_CALC_DECIMALS = 4
STOCHASTIK_CALC_TOLERANCE = 0.0001

# Standardregel fuer graphisches Ablesen: ein Viertel der Achsen-Schrittweite.
GRAPH_READ_FRACTION = 0.25


def axis_tick_step(span: float) -> float:
    if span <= 0:
        return 1.0
    target = span / 7.0
    power = 10 ** math.floor(math.log10(target))
    mantissa = target / power
    if mantissa <= 1.0:
        base = 1.0
    elif mantissa <= 2.0:
        base = 2.0
    elif mantissa <= 2.5:
        base = 2.5
    elif mantissa <= 5.0:
        base = 5.0
    else:
        base = 10.0
    return base * power


def graph_read_tolerance_from_step(step: float, fraction: float = GRAPH_READ_FRACTION) -> float:
    return max(0.0, step) * fraction


def graph_read_tolerance_from_span(span: float, fraction: float = GRAPH_READ_FRACTION) -> float:
    return graph_read_tolerance_from_step(axis_tick_step(span), fraction=fraction)
