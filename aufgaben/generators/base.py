from abc import ABC, abstractmethod

from aufgaben.core.models import Task


class TaskGenerator(ABC):
    generator_key: str | None = None

    @abstractmethod
    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        raise NotImplementedError
