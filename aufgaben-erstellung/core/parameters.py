from dataclasses import dataclass
import math


@dataclass(frozen=True)
class BinomialParameter:
    n: int
    p: float
    mu: float
    sigma: float

    @classmethod
    def from_np(cls, n: int, p: float):
        return cls(
            n=n,
            p=p,
            mu=n * p,
            sigma=math.sqrt(n * p * (1 - p))
        )
