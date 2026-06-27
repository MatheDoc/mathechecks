import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import (
    binom_cdf,
    rounds_to_extreme_without_boundary,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _alpha_left(n: int, p0: float, k: int) -> float:
    return binom_cdf(n=n, p=p0, k=k)


def _alpha_right(n: int, p0: float, k: int) -> float:
    return 1.0 - binom_cdf(n=n, p=p0, k=k - 1)


def _beta_left(n: int, p1: float, k: int) -> float:
    """P(X > k | p1) = 1 - P(X <= k | p1)"""
    return 1.0 - binom_cdf(n=n, p=p1, k=k)


def _beta_right(n: int, p1: float, k: int) -> float:
    """P(X < k | p1) = P(X <= k-1 | p1)"""
    return binom_cdf(n=n, p=p1, k=k - 1)


def _sample_k(rng: random.Random, side: str, n: int, p0: float) -> int:
    mu = n * p0
    sigma = math.sqrt(n * p0 * (1 - p0))
    z = rng.uniform(0.7, 1.9)
    if side == "links":
        return max(1, min(n - 2, math.floor(mu - z * sigma)))
    else:
        return max(2, min(n - 1, math.ceil(mu + z * sigma)))


def _p_fmt(p: float, rng: random.Random) -> str:
    if rng.random() < 0.4:
        return f"{round(p * 100)} %"
    return f"{p:.2f}".replace(".", ",")


def _ep_fmt(ep: float) -> str:
    return f"{ep:.4f}".replace(".", ",")


def _entsch(rng: random.Random, side: str, k: int, success_plural: str) -> str:
    if side == "links":
        return rng.choice([
            f"Werden dabei höchstens ${k}$ {success_plural} festgestellt, wird $H_0$ abgelehnt.",
            f"Die Entscheidungsregel lautet $\\overline{{A}}=\\{{0, 1, \\ldots, {k}\\}}$.",
            f"Treten höchstens ${k}$ {success_plural} auf, wird $H_0$ verworfen.",
        ])
    else:
        return rng.choice([
            f"Werden dabei mindestens ${k}$ {success_plural} festgestellt, wird $H_0$ abgelehnt.",
            f"Treten mindestens ${k}$ {success_plural} auf, wird $H_0$ verworfen.",
        ])


_HISTORISCH = [
    "Bisher nahm man an, dass die Wahrscheinlichkeit, {event_acc} anzutreffen, {p0} beträgt.",
    "Erfahrungsgemäß liegt die Wahrscheinlichkeit, {event_acc} zu beobachten, bei {p0}.",
    "Aus früheren Erhebungen ist bekannt, dass man mit einer Wahrscheinlichkeit von {p0} {event_acc} antrifft.",
    "Der bisherige Erfahrungswert für {event_acc} liegt bei {p0}.",
]

_VERMUTUNG_LINKS = [
    "Es besteht nun die Vermutung, dass sich dieser Anteil verringert hat.",
    "Man vermutet, dass die aktuelle Rate darunter liegt.",
    "Neuere Beobachtungen legen nahe, dass der Anteil gesunken sein könnte.",
]

_VERMUTUNG_RECHTS = [
    "Es besteht nun die Vermutung, dass sich dieser Anteil erhöht hat.",
    "Man vermutet, dass die aktuelle Rate darüber liegt.",
    "Neuere Beobachtungen legen nahe, dass der Anteil gestiegen sein könnte.",
]

_STICHPROBE_N = [
    "Dazu werden {n} {sample_plural} untersucht.",
    "{n} {sample_plural} werden zufällig ausgewählt und untersucht.",
    "Es werden {n} {sample_plural} betrachtet.",
]

_P1_BEKANNT = [
    "Es ist nun bekannt, dass die Wahrscheinlichkeit, {event_acc} anzutreffen, tatsächlich {p1} beträgt.",
    "Es stellt sich heraus, dass der wahre Anteil bei {p1} liegt.",
    "Inzwischen ist bekannt, dass die tatsächliche Wahrscheinlichkeit für {event_acc} gleich {p1} ist.",
]

_FEHLER1_GEGEBEN = [
    "Die Wahrscheinlichkeit für den Fehler 1. Art beträgt ${ep}$.",
]

_FEHLER2_GEGEBEN = [
    "Die Wahrscheinlichkeit für den Fehler 2. Art beträgt ${ep}$.",
    "Es gilt $\\beta = {ep}$.",
]

_FRAGE_P0 = [
    "Bestimmen Sie $p_0$ (auf 2 Nachkommastellen).",
    "Welchen Wert hat die Wahrscheinlichkeit $p_0$ der Nullhypothese (auf 2 NKS)?",
]

_FRAGE_P1 = [
    "Bestimmen Sie $p_1$ (die Wahrscheinlichkeit der Gegenhypothese, auf 2 NKS).",
    "Welchen Wert hat $p_1$, also die tatsächliche Wahrscheinlichkeit (auf 2 NKS)?",
]

_FRAGE_N = [
    "Bestimmen Sie den Stichprobenumfang $n$.",
    "Wie groß ist der Stichprobenumfang $n$?",
]


class ParameterAusFehlerwahrscheinlichkeitGenerator(TaskGenerator):
    generator_key = "stochastik.hypothesentests.parameter_aus_fehlerwahrscheinlichkeit"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        for _ in range(count):
            for _ in range(500):
                task = self._try_one(rng)
                if task is not None:
                    tasks.append(task)
                    break
            else:
                raise ValueError("Konnte keine gültige Aufgabe erzeugen.")
        return tasks

    def _try_one(self, rng: random.Random) -> Task | None:
        side = rng.choice(["links", "rechts"])
        error_type = rng.choice([1, 2])
        unknown = rng.choice(["n", "p"])
        sc = rng.choice(SCENARIOS)

        n = rng.randint(50, 200)
        p0 = rng.choice([x / 100 for x in range(12, 69)])

        if error_type == 2:
            if side == "links":
                p1_pool = [x / 100 for x in range(5, int(p0 * 100) - 4)]
            else:
                p1_pool = [x / 100 for x in range(int(p0 * 100) + 5, 91)]
            if not p1_pool:
                return None
            p1 = rng.choice(p1_pool)
        else:
            p1 = None

        k = _sample_k(rng, side=side, n=n, p0=p0)

        # Fehlerwahrscheinlichkeit berechnen
        if error_type == 1:
            ep = _alpha_left(n, p0, k) if side == "links" else _alpha_right(n, p0, k)
        else:
            ep = _beta_left(n, p1, k) if side == "links" else _beta_right(n, p1, k)

        # Bereich prüfen
        if error_type == 1 and not (0.005 <= ep <= 0.20):
            return None
        if error_type == 2 and not (0.05 <= ep <= 0.95):
            return None
        if rounds_to_extreme_without_boundary(ep, decimals=4):
            return None

        ep_fmt = _ep_fmt(ep)
        p0_fmt = _p_fmt(p0, rng)

        # Intro und Frage je nach Fall
        parts = [sc.intro_prefix]

        if error_type == 1 and unknown == "p":
            # n, k, alpha gegeben → p0 gesucht
            side_phrase = (
                "Es wird ein linksseitiger Hypothesentest durchgeführt."
                if side == "links"
                else "Es wird ein rechtsseitiger Hypothesentest durchgeführt."
            )
            parts.append(side_phrase)
            parts.append(rng.choice(_STICHPROBE_N).format(n=n, sample_plural=sc.sample_object_plural))
            parts.append(_entsch(rng, side, k, sc.success_plural))
            parts.append(rng.choice(_FEHLER1_GEGEBEN).format(ep=ep_fmt))
            question = rng.choice(_FRAGE_P0)
            answer = numerical(p0, tolerance=0, decimals=2)

        elif error_type == 1 and unknown == "n":
            # p0, k, alpha gegeben → n gesucht
            hist = rng.choice(_HISTORISCH).format(event_acc=sc.success_event_accusative, p0=p0_fmt)
            vermutung = rng.choice(_VERMUTUNG_LINKS if side == "links" else _VERMUTUNG_RECHTS)
            parts.extend([hist, vermutung])
            parts.append(_entsch(rng, side, k, sc.success_plural))
            parts.append(rng.choice(_FEHLER1_GEGEBEN).format(ep=ep_fmt))
            question = rng.choice(_FRAGE_N)
            answer = numerical(n, tolerance=0, decimals=0)

        elif error_type == 2 and unknown == "p":
            # n, p0, k, beta gegeben → p1 gesucht
            hist = rng.choice(_HISTORISCH).format(event_acc=sc.success_event_accusative, p0=p0_fmt)
            vermutung = rng.choice(_VERMUTUNG_LINKS if side == "links" else _VERMUTUNG_RECHTS)
            parts.extend([hist, vermutung])
            parts.append(rng.choice(_STICHPROBE_N).format(n=n, sample_plural=sc.sample_object_plural))
            parts.append(_entsch(rng, side, k, sc.success_plural))
            parts.append(rng.choice(_FEHLER2_GEGEBEN).format(ep=ep_fmt))
            question = rng.choice(_FRAGE_P1)
            answer = numerical(p1, tolerance=0, decimals=2)

        else:
            # error_type == 2 and unknown == "n"
            # p0, p1, k, beta gegeben → n gesucht
            p1_fmt = _p_fmt(p1, rng)
            hist = rng.choice(_HISTORISCH).format(event_acc=sc.success_event_accusative, p0=p0_fmt)
            vermutung = rng.choice(_VERMUTUNG_LINKS if side == "links" else _VERMUTUNG_RECHTS)
            p1_info = rng.choice(_P1_BEKANNT).format(event_acc=sc.success_event_accusative, p1=p1_fmt)
            parts.extend([hist, vermutung, p1_info])
            parts.append(_entsch(rng, side, k, sc.success_plural))
            parts.append(rng.choice(_FEHLER2_GEGEBEN).format(ep=ep_fmt))
            question = rng.choice(_FRAGE_N)
            answer = numerical(n, tolerance=0, decimals=0)

        return Task(
            einleitung=" ".join(parts),
            fragen=[question],
            antworten=[answer],
        )
