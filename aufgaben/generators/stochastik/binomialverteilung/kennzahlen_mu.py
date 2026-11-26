from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.kennzahlen_n_mu_gegeben import (
    BinomialKennzahlenNMuGegebenGenerator,
)
from aufgaben.generators.stochastik.binomialverteilung.kennzahlen_n_p_gegeben import (
    BinomialKennzahlenNPGegebenGenerator,
)
from aufgaben.generators.stochastik.binomialverteilung.kennzahlen_p_mu_gegeben import (
    BinomialKennzahlenPMuGegebenGenerator,
)
from aufgaben.generators.stochastik.binomialverteilung.shared import mix_generator_tasks


class BinomialKennzahlenMuGenerator(TaskGenerator):
    """Kenngrößen über mu = n*p bestimmen: (n, p), (n, mu) oder (p, mu) gegeben (gemischt)."""

    generator_key = "stochastik.binomialverteilung.kennzahlen_mu"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        return mix_generator_tasks(
            [
                BinomialKennzahlenNPGegebenGenerator,
                BinomialKennzahlenNMuGegebenGenerator,
                BinomialKennzahlenPMuGegebenGenerator,
            ],
            count=count,
            seed=seed,
        )
