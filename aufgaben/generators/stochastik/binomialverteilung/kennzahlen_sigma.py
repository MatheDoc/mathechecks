from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.kennzahlen_mu_sigma_gegeben import (
    BinomialKennzahlenMuSigmaGegebenGenerator,
)
from aufgaben.generators.stochastik.binomialverteilung.kennzahlen_p_sigma_gegeben import (
    BinomialKennzahlenPSigmaGegebenGenerator,
)
from aufgaben.generators.stochastik.binomialverteilung.shared import mix_generator_tasks


class BinomialKennzahlenSigmaGenerator(TaskGenerator):
    """Kenngrößen über die Formel für sigma bestimmen: (p, sigma) oder (mu, sigma) gegeben (gemischt)."""

    generator_key = "stochastik.binomialverteilung.kennzahlen_sigma"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        return mix_generator_tasks(
            [BinomialKennzahlenPSigmaGegebenGenerator, BinomialKennzahlenMuSigmaGegebenGenerator],
            count=count,
            seed=seed,
        )
