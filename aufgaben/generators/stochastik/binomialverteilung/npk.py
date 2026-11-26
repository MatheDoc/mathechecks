from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.npk_k import BinomialNpkKGenerator
from aufgaben.generators.stochastik.binomialverteilung.npk_n import BinomialNpkNGenerator
from aufgaben.generators.stochastik.binomialverteilung.npk_p import BinomialNpkPGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import mix_generator_tasks


class BinomialNpkGenerator(TaskGenerator):
    """n, p oder k aus einer Bedingung an eine Intervallwahrscheinlichkeit bestimmen (gemischt)."""

    generator_key = "stochastik.binomialverteilung.npk"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        return mix_generator_tasks(
            [BinomialNpkNGenerator, BinomialNpkPGenerator, BinomialNpkKGenerator],
            count=count,
            seed=seed,
        )
