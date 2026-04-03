import random

from aufgaben.core.tolerances import graph_read_tolerance_from_span
from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _num_tol,
    _sample_k3_cost_coefficients_from_exact_kennzahlen,
)


class ErtragsgesetzlicheKostenKennzahlenGraphischK3Generator(TaskGenerator):
    """Erzeugt graphische K3-Kennzahlenaufgaben für ertragsgesetzliche Kostenfunktionen."""

    generator_key = "analysis.ertragsgesetzliche_kostenfunktionen.kennzahlen_graphisch_k3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float, float]] = set()

        for _ in range(count):
            while True:
                (
                    k3,
                    k2,
                    k1,
                    k0,
                    x_wende,
                    x_betriebsminimum,
                    x_betriebsoptimum,
                    kurzfristige_preisuntergrenze,
                    langfristige_preisuntergrenze,
                ) = _sample_k3_cost_coefficients_from_exact_kennzahlen(rng)

                key = (k3, k2, k1, k0)
                if key in used:
                    continue
                used.add(key)
                break

            # Fokus auf lesbare Wendestelle und die relevanten Kennzahlenbereiche.
            max_x = round(max(12.0, x_betriebsoptimum * 1.18, x_wende * 1.9), 1)

            def _k_value(x: float) -> float:
                return k3 * x ** 2 + k2 * x + k1 + (k0 / x)

            delta = min(max(0.8, 0.08 * max_x), x_wende * 0.35, (max_x - x_wende) * 0.35)
            if delta > 0.35:
                m_tan = 3.0 * k3 * x_wende ** 2 + 2.0 * k2 * x_wende + k1
                m_sec = (_k_value(x_wende + delta) - _k_value(x_wende - delta)) / (2.0 * delta)
                slope_gap = abs(m_tan - m_sec)
                slope_target = max(0.02, 0.025 * abs(m_tan))
                if slope_gap < slope_target:
                    max_x = round(max(10.0, x_wende * 1.55, x_betriebsoptimum * 1.10), 1)

            x_focus_min = max(1.0, x_wende * 0.45)

            points = 280
            y_values: list[float] = []
            for index in range(points):
                x_value = x_focus_min + ((max_x - x_focus_min) * index) / (points - 1)
                gk_value = 3.0 * k3 * x_value ** 2 + 2.0 * k2 * x_value + k1
                k_value = _k_value(x_value)
                kv_value = k3 * x_value ** 2 + k2 * x_value + k1
                y_values.extend((gk_value, k_value, kv_value))

            y_low_raw = min(y_values)
            y_high_raw = max(y_values)
            span = max(5.0, y_high_raw - y_low_raw)
            y_min = round(max(0.0, y_low_raw - 0.12 * span), 1)
            y_max = round(y_high_raw + 0.15 * span, 1)
            x_tolerance = graph_read_tolerance_from_span(max_x)
            y_tolerance = graph_read_tolerance_from_span(max(1.0, y_max - y_min))

            items = [
                ("die kurzfristige Preisuntergrenze.", _num_tol(kurzfristige_preisuntergrenze, y_tolerance)),
                ("das Betriebsminimum.", _num_tol(x_betriebsminimum, x_tolerance)),
                ("die langfristige Preisuntergrenze.", _num_tol(langfristige_preisuntergrenze, y_tolerance)),
                ("das Betriebsoptimum.", _num_tol(x_betriebsoptimum, x_tolerance)),
                (
                    "die Menge beim Übergang vom degressiven zum progressiven Kostenwachstum.",
                    _num_tol(x_wende, x_tolerance),
                ),
            ]

            intro = (
                "Das Diagramm zeigt die Grenzkosten-, Stückkosten- und variable "
                "Stückkostenfunktion eines Unternehmens. Bestimmen Sie"
            )

            visual = {
                "type": "plot",
                "spec": {
                    "type": "cost-curves",
                    "params": {
                        "k3": k3,
                        "k2": k2,
                        "k1": k1,
                        "k0": k0,
                        "maxX": max_x,
                        "yMax": y_max,
                    },
                    "layout": {
                        "title": "Grenzkosten-, Stückkosten- und variable Stückkostenfunktion",
                        "xaxis": {"title": "Menge x", "range": [0, max_x]},
                        "yaxis": {"title": "Kosten", "range": [y_min, y_max]},
                        "shapes": [
                            {
                                "type": "line",
                                "x0": x_wende,
                                "x1": x_wende,
                                "y0": y_min,
                                "y1": y_max,
                                "line": {"color": "#374151", "dash": "dot", "width": 1},
                            }
                        ],
                        "annotations": [
                            {
                                "x": x_wende,
                                "y": y_min,
                                "yref": "y",
                                "text": "x_W",
                                "showarrow": False,
                                "yshift": -14,
                            }
                        ],
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
