import random

from aufgaben.core.tolerances import graph_read_tolerance_from_span
from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _kennzahlen_items,
)


def _g_value(x: float, k3: float, k2: float, k1: float, k0: float, price: float) -> float:
    return -k3 * (x ** 3) - k2 * (x ** 2) + (price - k1) * x - k0


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
) -> tuple[float, float, float, float, float, float, float, float, int]:
    # Musterfunktionen (vom Nutzer vorgegeben):
    # E(x)=x, K(x)=0.02x^3-0.25x^2+x+2
    base_k3 = 0.02
    base_k2 = -0.25
    base_k1 = 1.0
    base_k0 = 2.0

    for _ in range(9000):
        # VBA-Idee: Koeffizienten mit separatem x/y-Scale und
        # potenzabhaengiger Normierung variieren.
        # coeff_i ~ base_i * wobble_i * y_scale / x_scale^i
        x_scale = rng.uniform(1, 50)
        y_scale = rng.uniform(1, 50)

        wobble_k0 = rng.randint(80, 120) / 100.0
        wobble_k1 = rng.randint(80, 120) / 100.0
        wobble_k2 = rng.randint(80, 120) / 100.0
        wobble_k3 = rng.randint(80, 120) / 100.0
        wobble_e1 = rng.randint(80, 120) / 100.0

        k0 = round(base_k0 * wobble_k0 * y_scale / (x_scale ** 0), 6)
        k1 = round(base_k1 * wobble_k1 * y_scale / (x_scale ** 1), 6)
        k2 = round(base_k2 * wobble_k2 * y_scale / (x_scale ** 2), 6)
        k3 = round(base_k3 * wobble_k3 * y_scale / (x_scale ** 3), 6)
        price = round(1.0 * wobble_e1 * y_scale / (x_scale ** 1), 6)

        if not (k3 > 0.0 and k2 < 0.0 and k1 > 0.0 and k0 > 0.0):
            continue

        # Fuer K(x)=a*x^3+b*x^2+c*x+d: b^2 <= 3ac
        # sichert monotones (nicht fallendes) Verhalten von K auf R.
        if (k2 ** 2) > (3.0 * k3 * k1 + 1e-12):
            continue

        discr = 4.0 * (k2 ** 2) + 12.0 * k3 * (price - k1)
        if discr <= 0.0:
            continue

        sqrt_discr = discr ** 0.5
        x_crit_1 = (-2.0 * k2 - sqrt_discr) / (6.0 * k3)
        x_crit_2 = (-2.0 * k2 + sqrt_discr) / (6.0 * k3)
        if x_crit_2 <= 0.8:
            continue

        g = lambda x: _g_value(x, k3, k2, k1, k0, price)
        g0 = g(0.0)
        g_max = g(x_crit_2)
        if g0 >= 0.0 or g_max <= 0.0:
            continue

        try:
            x_break_even_low = _bisection_root(g, 0.0, x_crit_2)
        except ValueError:
            continue

        right = max(x_crit_2 + 1.0, x_crit_2 * 1.6)
        while g(right) > 0.0 and right < 250.0:
            right *= 1.4
        if g(right) > 0.0:
            continue

        try:
            x_break_even_high = _bisection_root(g, x_crit_2, right)
        except ValueError:
            continue

        if x_break_even_low <= 0.0 or x_break_even_high <= x_break_even_low:
            continue

        # Diagramm-Regel: Kapazitaet klar hinter der Gewinngrenze,
        # idealerweise ca. 20-30% rechts davon.
        capacity = int(round(x_break_even_high * rng.uniform(1.20, 1.30)))
        if capacity < 10:
            capacity = 10
        if capacity <= x_break_even_high:
            capacity = int(x_break_even_high) + 1

        root_to_capacity_ratio = x_break_even_high / float(capacity)
        if not (0.75 <= root_to_capacity_ratio <= 0.90):
            continue

        e_at_capacity = price * float(capacity)

        # Gewinnmaximum soll sichtbar signifikant sein.
        if g_max < 0.10 * e_at_capacity:
            continue

        # Verhindert systematisch zu hohe y-Werte.
        if e_at_capacity > 980.0:
            continue

        return (
            k3,
            k2,
            k1,
            k0,
            price,
            x_break_even_low,
            x_break_even_high,
            x_crit_2,
            capacity,
        )

    raise ValueError("Konnte keine gültigen Parameter aus der Muster-Skalierung erzeugen.")


class EconomicPolynomialKennzahlenGraphischGenerator(TaskGenerator):
    """Erzeugt graphische Kennzahlen-Aufgaben mit visual.spec (ohne Base64 im JSON)."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[float, float, float, float, float, int]] = set()

        for _ in range(count):
            while True:
                (
                    k3,
                    k2,
                    k1,
                    k0,
                    price,
                    x_break_even_low,
                    x_break_even_high,
                    x_gain_max,
                    capacity,
                ) = _sample_template_scaled_parameters(rng)

                key = (k3, k2, k1, k0, price, capacity)
                if key in used_params:
                    continue

                used_params.add(key)
                break

            x_axis_max = max(float(capacity) * rng.uniform(1.02, 1.12), x_break_even_high * 1.08, 10.0)
            # Plotly-ähnliche y_min-Bestimmung, aber ohne den Bereich nach
            # der zweiten Nullstelle der Gewinnfunktion.
            x_min_scan_max = max(0.8, min(x_axis_max, x_break_even_high * 1.02))
            sample_points = 240
            y_scan: list[float] = []
            for index in range(sample_points + 1):
                x_value = (x_min_scan_max * index) / sample_points
                e_value = price * x_value
                k_value = k3 * (x_value ** 3) + k2 * (x_value ** 2) + k1 * x_value + k0
                g_value = e_value - k_value
                y_scan.extend((e_value, k_value, g_value))

            y_min_core = min(y_scan)
            e_at_capacity = price * float(capacity)

            # y_min leicht unterhalb des gescannten Minimums,
            # y_max leicht oberhalb des Erlöswerts an der Kapazitätsgrenze.
            y_min = y_min_core - max(3.0, 0.06 * abs(y_min_core))
            y_max_raw = e_at_capacity + max(4.0, 0.08 * e_at_capacity)

            # Harte Grenzen: y_max <= 1000 und y-Range <= 1000,
            # ohne den negativen Bereich kuenstlich anzuheben.
            y_max = min(y_max_raw, 1000.0, y_min + 1000.0)

            if y_max <= y_min + 1.0:
                y_max = y_min + 8.0

            x_tolerance = graph_read_tolerance_from_span(x_axis_max)
            y_tolerance = graph_read_tolerance_from_span(max(1.0, y_max - y_min))

            items = _kennzahlen_items(
                rng=rng,
                k3=k3,
                k2=k2,
                k1=k1,
                k0=k0,
                price=price,
                x_break_even_low=x_break_even_low,
                x_break_even_high=x_break_even_high,
                x_gain_max=x_gain_max,
                capacity=capacity,
                x_tolerance=x_tolerance,
                y_tolerance=y_tolerance,
            )

            intro = (
                "Das Diagramm zeigt die Erlös-, Kosten- und Gewinnfunktion eines Unternehmens. "
                f"Die Kapazitätsgrenze beträgt {capacity} Mengeneinheiten. "
                "Bestimmen Sie"
            )

            visual = {
                "type": "plot",
                "spec": {
                    "type": "economic-curves",
                    "params": {
                        "k3": k3,
                        "k2": k2,
                        "k1": k1,
                        "k0": k0,
                        "price": price,
                        "capacity": capacity,
                    },
                    "layout": {
                        "title": "Erlös-, Kosten- und Gewinnfunktion",
                        "xaxis": {
                            "title": "Menge x",
                            "range": [0.0, x_axis_max],
                        },
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
