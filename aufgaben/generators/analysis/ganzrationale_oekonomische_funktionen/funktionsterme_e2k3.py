import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _answers_for_e_quadratic,
    _answers_for_g,
    _answers_for_k,
    _answers_for_p_linear,
    _build_intro,
    _erlös_quadratic_latex,
    _poly3_latex,
    _preis_linear_latex,
    _sample_e2k3_parameters,
)


class EconomicPolynomialFunctionTermsE2K3Generator(TaskGenerator):
    """Erzeugt Aufgaben zu ökonomischen Funktionen (K, E, G, p) im E2K3-Modell.

    E2K3: quadratischer Erlös E(x)=a2*x²+a1*x, linearer Preis p(x)=a2*x+a1,
    kubische Kosten K(x)=k3*x³+k2*x²+k1*x+k0.
    """

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.funktionsterme_e2k3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[float, float, float, float, float, float, int]] = set()

        variants = [0, 1, 2, 3, 4]

        while len(tasks) < count:
            a2, a1, k3, k2, k1, k0, *_ = _sample_e2k3_parameters(rng, for_graph=False)

            g3 = -k3
            g2 = a2 - k2
            g1 = a1 - k1
            g0 = -k0

            variant = variants[len(tasks) % len(variants)]
            params = (a2, a1, k3, k2, k1, k0, variant)
            if params in used_params:
                continue
            used_params.add(params)

            k_expr = _poly3_latex("K", k3, k2, k1, k0)
            e_expr = _erlös_quadratic_latex(a2, a1)
            g_expr = _poly3_latex("G", g3, g2, g1, g0)
            p_expr = _preis_linear_latex(a2, a1)

            if variant == 0:
                given = [e_expr, g_expr]
                questions = ["Kostenfunktion", "Preisfunktion"]
                answers = [_answers_for_k(k3, k2, k1, k0), _answers_for_p_linear(a2, a1)]
            elif variant == 1:
                given = [k_expr, p_expr]
                questions = ["Erlösfunktion", "Gewinnfunktion"]
                answers = [_answers_for_e_quadratic(a2, a1), _answers_for_g(g3, g2, g1, g0)]
            elif variant == 2:
                given = [p_expr, g_expr]
                questions = ["Erlösfunktion", "Kostenfunktion"]
                answers = [_answers_for_e_quadratic(a2, a1), _answers_for_k(k3, k2, k1, k0)]
            elif variant == 3:
                given = [e_expr, k_expr]
                questions = ["Gewinnfunktion", "Preisfunktion"]
                answers = [_answers_for_g(g3, g2, g1, g0), _answers_for_p_linear(a2, a1)]
            else:
                given = [k_expr, g_expr]
                questions = ["Erlösfunktion", "Preisfunktion"]
                answers = [_answers_for_e_quadratic(a2, a1), _answers_for_p_linear(a2, a1)]

            tasks.append(Task(einleitung=_build_intro(given), fragen=questions, antworten=answers))

        return tasks
