import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _answers_for_e,
    _answers_for_g,
    _answers_for_k,
    _answers_for_p,
    _build_intro,
    _erlös_latex,
    _poly3_latex,
    _preis_latex,
    _has_max_sig_digits,
    _sample_cost_coefficients,
)
from aufgaben.generators.analysis.shared_numbers import uniform_sig


class EconomicPolynomialFunctionTermsGenerator(TaskGenerator):
    """Erzeugt Aufgaben zu ganzrationalen ökonomischen Funktionen (K, E, G, p)."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.funktionsterme"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[float, float, float, float, float, int]] = set()

        variants = [
            0,
            1,
            2,
            3,
            4,
        ]

        while len(tasks) < count:
            k3, k2, k1, k0 = _sample_cost_coefficients(rng)
            price = uniform_sig(rng, 3.0, 60.0)

            g3 = -k3
            g2 = -k2
            g1 = round(price - k1, 10)
            g0 = -k0
            if abs(g1) < 1e-9:
                continue
            if not _has_max_sig_digits(g1, max_digits=2):
                continue

            variant = variants[len(tasks) % len(variants)]
            params = (k3, k2, k1, k0, price, variant)
            if params in used_params:
                continue
            used_params.add(params)

            k_expr = _poly3_latex("K", k3, k2, k1, k0)
            e_expr = _erlös_latex(price)
            g_expr = _poly3_latex("G", g3, g2, g1, g0)
            p_expr = _preis_latex(price)

            if variant == 0:
                given = [e_expr, g_expr]
                questions = ["Kostenfunktion", "Preisfunktion"]
                answers = [_answers_for_k(k3, k2, k1, k0), _answers_for_p(price)]
            elif variant == 1:
                given = [k_expr, p_expr]
                questions = ["Erlösfunktion", "Gewinnfunktion"]
                answers = [_answers_for_e(price), _answers_for_g(g3, g2, g1, g0)]
            elif variant == 2:
                given = [p_expr, g_expr]
                questions = ["Erlösfunktion", "Kostenfunktion"]
                answers = [_answers_for_e(price), _answers_for_k(k3, k2, k1, k0)]
            elif variant == 3:
                given = [e_expr, k_expr]
                questions = ["Gewinnfunktion", "Preisfunktion"]
                answers = [_answers_for_g(g3, g2, g1, g0), _answers_for_p(price)]
            else:
                given = [k_expr, g_expr]
                questions = ["Erlösfunktion", "Preisfunktion"]
                answers = [_answers_for_e(price), _answers_for_p(price)]

            tasks.append(Task(einleitung=_build_intro(given), fragen=questions, antworten=answers))

        return tasks
