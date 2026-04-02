import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _format_number,
    _num,
    _poly3_value,
    _sample_points_for_poly,
    _sample_steckbrief_g_coefficients,
    _sample_steckbrief_k_coefficients,
)


class EconomicPolynomialSteckbriefKennzahlenGenerator(TaskGenerator):
    """Erzeugt genau einen Steckbrief-Typ mit fester Mischung für K und G."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.steckbrief_kennzahlen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_keys: set[tuple[float, float, float, float, str, str]] = set()

        k_count = count // 2
        g_count = count - k_count
        g_points_count = g_count // 2
        g_mix_count = g_count - g_points_count

        request_types = (
            ["K_POINTS"] * k_count
            + ["G_POINTS"] * g_points_count
            + ["G_MIX"] * g_mix_count
        )
        rng.shuffle(request_types)

        for request_type in request_types:
            while True:
                if request_type == "K_POINTS":
                    a3, a2, a1, a0 = _sample_steckbrief_k_coefficients(rng)
                    label = "K"
                    question = "Bestimmen Sie die kubische Kostenfunktion."

                    x_values = sorted(rng.sample(range(1, 13), 4))
                    values = [round(_poly3_value(a3, a2, a1, a0, float(x)), 2) for x in x_values]
                    info_parts = [
                        f"Die Kosten für ${x_values[0]}$ ME betragen ${_format_number(values[0])}$ GE.",
                        f"Die Kosten für ${x_values[1]}$ ME betragen ${_format_number(values[1])}$ GE.",
                        f"Die Kosten für ${x_values[2]}$ ME betragen ${_format_number(values[2])}$ GE.",
                        f"Die Kosten für ${x_values[3]}$ ME betragen ${_format_number(values[3])}$ GE.",
                    ]
                else:
                    a3, a2, a1, a0, r1, r2, x_info = _sample_steckbrief_g_coefficients(rng)
                    label = "G"
                    question = "Bestimmen Sie die kubische Gewinnfunktion."

                    if request_type == "G_POINTS":
                        points = _sample_points_for_poly(rng, a3, a2, a1, a0)
                        info_parts = [
                            f"Der Gewinn bei ${int(x)}$ ME beträgt ${_format_number(y)}$ GE."
                            for x, y in points
                        ]
                    else:
                        g0 = round(_poly3_value(a3, a2, a1, a0, 0.0), 2)
                        g_info = round(_poly3_value(a3, a2, a1, a0, x_info), 2)
                        info_parts = [
                            f"Die Gewinnschwelle liegt bei $x={_format_number(r1)}$.",
                            f"Die Gewinngrenze liegt bei $x={_format_number(r2)}$.",
                            f"Bei $x=0$ gilt $G(0)={_format_number(g0)}$.",
                            f"Bei $x={_format_number(x_info)}$ gilt $G(x)={_format_number(g_info)}$.",
                        ]

                key = (a3, a2, a1, a0, label, request_type)
                if key in used_keys:
                    continue
                used_keys.add(key)
                break

            intro = "Es liegen folgende Informationen vor:" + "".join(
                f"</p> <p>{part}" for part in info_parts
            )

            answer = (
                f"$ {label}(x)= $"
                f"{_num(a3)}"
                "$ x^3 $+"
                f"{_num(a2)}"
                "$ x^2 $+"
                f"{_num(a1)}"
                "$ x $+"
                f"{_num(a0)}"
            )

            tasks.append(Task(einleitung=intro, fragen=[question], antworten=[answer]))

        return tasks
