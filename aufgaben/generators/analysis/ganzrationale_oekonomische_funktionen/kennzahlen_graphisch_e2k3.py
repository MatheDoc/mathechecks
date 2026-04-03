import random

from aufgaben.core.tolerances import graph_read_tolerance_from_span
from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _e2k3_kennzahlen_items,
)


def _g_value(x: float, a2: float, a1: float, k3: float, k2: float, k1: float, k0: float) -> float:
    return (a2 * (x ** 2) + a1 * x) - (k3 * (x ** 3) + k2 * (x ** 2) + k1 * x + k0)


def _bisection_root(func, left: float, right: float, iterations: int = 80) -> float:
    f_left = func(left)
    f_right = func(right)
    if f_left == 0:
        return left
    if f_right == 0:
        return right
    if f_left * f_right > 0:
        raise ValueError("Intervall enthält keine Nullstelle.")

    a, b = left, right
    for _ in range(iterations):
        middle = (a + b) / 2.0
        f_middle = func(middle)
        if f_middle == 0:
            return middle
        if f_left * f_middle < 0:
            b = middle
            f_right = f_middle
        else:
            a = middle
            f_left = f_middle
    return (a + b) / 2.0


def _sample_template_scaled_parameters(
    rng: random.Random,
) -> tuple[float, float, float, float, float, float, float, float, float]:
    # Musterfunktionen (vom Nutzer vorgegeben):
    # E(x)=-0.15x^2+2x, K(x)=0.02x^3-0.25x^2+x+3
    base_a2 = -0.15
    base_a1 = 2.0
    base_k3 = 0.02
    base_k2 = -0.25
    base_k1 = 1.0
    base_k0 = 3.0

    for _ in range(12000):
        # Potenzbewusste Skalierung analog E1K3.
        x_scale = rng.uniform(1.0, 45.0)
        y_scale = rng.uniform(1.0, 55.0)

        wobble_a2 = rng.randint(80, 120) / 100.0
        wobble_a1 = rng.randint(80, 120) / 100.0
        wobble_k3 = rng.randint(80, 120) / 100.0
        wobble_k2 = rng.randint(80, 120) / 100.0
        wobble_k1 = rng.randint(80, 120) / 100.0
        wobble_k0 = rng.randint(80, 120) / 100.0

        a2 = round(base_a2 * wobble_a2 * y_scale / (x_scale ** 2), 6)
        a1 = round(base_a1 * wobble_a1 * y_scale / (x_scale ** 1), 6)
        k3 = round(base_k3 * wobble_k3 * y_scale / (x_scale ** 3), 6)
        k2 = round(base_k2 * wobble_k2 * y_scale / (x_scale ** 2), 6)
        k1 = round(base_k1 * wobble_k1 * y_scale / (x_scale ** 1), 6)
        k0 = round(base_k0 * wobble_k0 * y_scale / (x_scale ** 0), 6)

        if not (a2 < 0.0 and a1 > 0.0):
            continue
        if not (k3 > 0.0 and k2 < 0.0 and k1 > 0.0 and k0 > 0.0):
            continue

        # Für K(x)=a*x^3+b*x^2+c*x+d: b^2 <= 3ac
        if (k2 ** 2) > (3.0 * k3 * k1 + 1e-12):
            continue

        x_sättigung = -a1 / a2
        if not (8.0 <= x_sättigung <= 140.0):
            continue

        x_erlös_max = -a1 / (2.0 * a2)
        e_max = a2 * (x_erlös_max ** 2) + a1 * x_erlös_max
        if e_max <= 0.0 or e_max > 920.0:
            continue

        g2 = a2 - k2
        g1 = a1 - k1
        discr = 4.0 * (g2 ** 2) + 12.0 * k3 * g1
        if discr <= 0.0:
            continue

        sqrt_discr = discr ** 0.5
        x_crit_1 = (2.0 * g2 - sqrt_discr) / (6.0 * k3)
        x_crit_2 = (2.0 * g2 + sqrt_discr) / (6.0 * k3)

        x_gain_max: float | None = None
        for candidate in (x_crit_1, x_crit_2):
            if candidate <= 0.0:
                continue
            second = -6.0 * k3 * candidate + 2.0 * g2
            if second < 0.0:
                x_gain_max = candidate
                break
        if x_gain_max is None:
            continue

        g = lambda x: _g_value(x, a2, a1, k3, k2, k1, k0)
        g0 = g(0.0)
        g_max = g(x_gain_max)
        if g0 >= 0.0 or g_max <= 0.0:
            continue

        try:
            x_break_even_low = _bisection_root(g, 0.0, x_gain_max)
        except ValueError:
            continue

        right = max(x_gain_max + 1.0, x_sättigung)
        while g(right) > 0.0 and right < 600.0:
            right *= 1.25
        if g(right) > 0.0:
            continue

        try:
            x_break_even_high = _bisection_root(g, x_gain_max, right)
        except ValueError:
            continue

        if x_break_even_low <= 0.0 or x_break_even_high <= x_break_even_low:
            continue

        if x_sättigung <= x_break_even_high * 1.01:
            continue

        # Verhindert visuell sehr schwache Gewinnberge.
        if g_max < max(8.0, 0.10 * e_max):
            continue

        return (
            a2,
            a1,
            k3,
            k2,
            k1,
            k0,
            x_break_even_low,
            x_break_even_high,
            x_gain_max,
        )

    raise ValueError("Konnte keine gültigen E2K3-Parameter aus der Muster-Skalierung erzeugen.")


class EconomicPolynomialKennzahlenGraphischE2K3Generator(TaskGenerator):
    """Erzeugt graphische E2K3-Kennzahlenaufgaben mit kompaktem visual.spec."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch_e2k3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[float, float, float, float, float, float]] = set()

        for _ in range(count):
            attempts = 0
            while True:
                attempts += 1
                (
                    a2,
                    a1,
                    k3,
                    k2,
                    k1,
                    k0,
                    x_break_even_low,
                    x_break_even_high,
                    x_gain_max,
                ) = _sample_template_scaled_parameters(rng)

                key = (a2, a1, k3, k2, k1, k0)
                if key in used_params:
                    continue

                x_sättigung = -a1 / a2
                if x_sättigung <= x_break_even_high * 1.01:
                    continue

                # x-Achse soll bis kurz nach der Sättigungsmenge gehen.
                max_x = x_sättigung * rng.uniform(1.03, 1.08)

                def _k_value(x: float) -> float:
                    return k3 * (x ** 3) + k2 * (x ** 2) + k1 * x + k0

                def _e_value(x: float) -> float:
                    return a2 * (x ** 2) + a1 * x

                def _g_value(x: float) -> float:
                    return _e_value(x) - _k_value(x)

                g0 = _g_value(0.0)
                x_erlös_max = -a1 / (2.0 * a2)
                e_max = _e_value(x_erlös_max)

                # Vorgabe für Check 4:
                # y_max etwas über Erlösmaximum, y_min etwas unterhalb G(0).
                y_span_ref = max(8.0, e_max - g0)
                y_min = g0 - max(2.0, 0.08 * y_span_ref)
                y_max = e_max + max(3.0, 0.08 * e_max)

                if y_min >= g0:
                    y_min = g0 - 2.0
                if y_max <= e_max:
                    y_max = e_max + 3.0
                if y_max <= y_min + 8.0:
                    y_max = y_min + 8.0

                if attempts > 5000:
                    used_params.add(key)
                    break

                used_params.add(key)
                break

            x_tolerance = graph_read_tolerance_from_span(max_x)
            y_tolerance = graph_read_tolerance_from_span(max(1.0, y_max - y_min))

            items = _e2k3_kennzahlen_items(
                rng=rng,
                a2=a2,
                a1=a1,
                k3=k3,
                k2=k2,
                k1=k1,
                k0=k0,
                x_break_even_low=x_break_even_low,
                x_break_even_high=x_break_even_high,
                x_gain_max=x_gain_max,
                x_tolerance=x_tolerance,
                y_tolerance=y_tolerance,
            )

            intro = (
                "Das Diagramm zeigt die Preis-Absatz-, Erlös-, Kosten- und Gewinnfunktion "
                "eines Unternehmens. Bestimmen Sie"
            )

            visual = {
                "type": "plot",
                "spec": {
                    "type": "economic-curves",
                    "params": {
                        "a2": a2,
                        "a1": a1,
                        "k3": k3,
                        "k2": k2,
                        "k1": k1,
                        "k0": k0,
                        "capacity": x_sättigung,
                        "xMax": max_x,
                        "showCapacityLine": False,
                    },
                    "points": 280,
                    "layout": {
                        "title": "Preis-Absatz-, Erlös-, Kosten- und Gewinnfunktion",
                        "xaxis": {"title": "Menge x", "range": [0.0, max_x]},
                        "yaxis": {"title": "Wert", "range": [y_min, y_max]},
                    },
                    "width": 900,
                    "height": 520,
                    "scale": 1,
                },
            }

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                    visual=visual,
                )
            )

        return tasks
