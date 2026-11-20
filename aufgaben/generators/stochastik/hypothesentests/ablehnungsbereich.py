import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.hypothesentests.shared import (
    balanced_sides,
    sample_ablehnungsbereich_links,
    sample_ablehnungsbereich_rechts,
)


def _p_fmt(p: float, rng: random.Random) -> str:
    if rng.random() < 0.4:
        return f"{round(p * 100)}\u00a0%"
    return f"{p:.2f}".replace(".", ",")


def _alpha_pct(alpha_req: float) -> str:
    return f"{round(alpha_req * 100)}\u00a0%"


_HISTORISCH = [
    "Bisher nahm man an, dass die Wahrscheinlichkeit, {acc} anzutreffen, {p0} beträgt.",
    "Erfahrungsgemäß liegt die Wahrscheinlichkeit, {acc} zu beobachten, bei {p0}.",
    "Aus früheren Erhebungen ist bekannt, dass mit einer Wahrscheinlichkeit von {p0} {acc} auftritt.",
    "Bisherige Daten belegen eine Wahrscheinlichkeit von {p0} dafür, {acc} zu beobachten.",
    "Der bisherige Erfahrungswert sagt: Mit einer Wahrscheinlichkeit von {p0} tritt {acc} auf.",
]

_VERMUTUNG = {
    "links": [
        "Es besteht nun die Vermutung, dass sich dieser Anteil verringert hat.",
        "Man vermutet, dass die aktuelle Rate darunter liegt.",
        "Neuere Beobachtungen legen nahe, dass der Anteil gesunken sein könnte.",
        "Inzwischen wird vermutet, dass dieser Wert gesunken ist.",
        "Es wird angenommen, dass der wahre Anteil heute kleiner ist.",
    ],
    "rechts": [
        "Es besteht nun die Vermutung, dass sich dieser Anteil erhöht hat.",
        "Man vermutet, dass die aktuelle Rate darüber liegt.",
        "Neuere Beobachtungen legen nahe, dass der Anteil gestiegen sein könnte.",
        "Inzwischen wird vermutet, dass dieser Wert gestiegen ist.",
        "Es wird angenommen, dass der wahre Anteil heute größer ist.",
    ],
}

_STICHPROBE = [
    "Zur Überprüfung werden {n}\u00a0{sample} zufällig ausgewählt.",
    "Daher werden {n}\u00a0{sample} stichprobenartig betrachtet.",
    "{n}\u00a0{sample} werden dafür zufällig untersucht.",
    "Um dies zu überprüfen, betrachtet man {n}\u00a0{sample}.",
]

_ALPHA_SATZ = [
    "Das Signifikanzniveau soll {a} betragen.",
    "Der Test soll ein Signifikanzniveau von {a} einhalten.",
    "Als Signifikanzniveau werden {a} festgelegt.",
]


class AblehnungsbereichGenerator(TaskGenerator):
    generator_key = "stochastik.hypothesentests.ablehnungsbereich"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for side in balanced_sides(rng, count):
            if side == "links":
                case = sample_ablehnungsbereich_links(rng)
            else:
                case = sample_ablehnungsbereich_rechts(rng)
            sc = case.scenario
            k = case.critical_value

            hist = rng.choice(_HISTORISCH).format(acc=sc.success_event_accusative, p0=_p_fmt(case.p0, rng))
            vermutung = rng.choice(_VERMUTUNG[side])
            stichprobe = rng.choice(_STICHPROBE).format(n=case.n, sample=sc.sample_object_plural)
            alpha_satz = rng.choice(_ALPHA_SATZ).format(a=_alpha_pct(case.alpha_requested))

            intro = f"{sc.intro_prefix} {hist} {vermutung} {stichprobe} {alpha_satz}"

            lower, upper = (0, k) if side == "links" else (k, case.n)
            answer = (
                f"Der Ablehnungsbereich lautet: "
                f"[ {numerical(lower, tolerance=0, decimals=0)}, \u2026 , {numerical(upper, tolerance=0, decimals=0)} ]."
            )

            tasks.append(Task(
                einleitung=intro,
                fragen=["Bestimmen Sie den Ablehnungsbereich der Nullhypothese."],
                antworten=[answer],
            ))

        return tasks
