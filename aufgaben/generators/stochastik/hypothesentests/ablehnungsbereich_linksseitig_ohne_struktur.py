import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.hypothesentests.shared import (
    AblehnungsbereichCase,
    sample_ablehnungsbereich_links,
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
    "Aus früheren Erhebungen ist bekannt, dass mit Wahrscheinlichkeit {p0} {acc} auftritt.",
    "Bisherige Daten belegen eine Wahrscheinlichkeit von {p0} dafür, {acc} zu beobachten.",
    "Der bisherige Erfahrungswert sagt: Mit Wahrscheinlichkeit {p0} tritt {acc} auf.",
]

_VERMUTUNG = [
    "Es besteht nun die Vermutung, dass sich dieser Anteil verringert hat.",
    "Man vermutet, dass die aktuelle Rate darunter liegt.",
    "Neuere Beobachtungen legen nahe, dass der Anteil gesunken sein könnte.",
    "Inzwischen wird vermutet, dass dieser Wert gesunken ist.",
    "Es wird angenommen, dass der wahre Anteil heute kleiner ist.",
]

_STICHPROBE = [
    "Zur Überprüfung werden {n}\u00a0{sample} zufällig ausgewählt.",
    "Daher werden {n}\u00a0{sample} stichprobenartig betrachtet.",
    "{n}\u00a0{sample} werden dafür zufällig untersucht.",
    "Um dies zu überprüfen, betrachtet man {n}\u00a0{sample}.",
]

_ALPHA_SATZ = [
    "Das Signifikanzniveau soll höchstens {a} betragen.",
    "Der Test soll ein Signifikanzniveau von höchstens {a} einhalten.",
    "Als maximales Signifikanzniveau werden {a} festgelegt.",
]


class AblehnungsbereichLinksseitigOhneStrukturGenerator(TaskGenerator):
    generator_key = "stochastik.hypothesentests.ablehnungsbereich_linksseitig_ohne_struktur"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for _ in range(count):
            case: AblehnungsbereichCase = sample_ablehnungsbereich_links(rng)
            sc = case.scenario
            n = case.n
            k = case.critical_value
            p0 = case.p0
            alpha_req = case.alpha_requested
            alpha = case.alpha  # P(X ≤ k)

            p0_fmt = _p_fmt(p0, rng)
            alpha_pct = _alpha_pct(alpha_req)

            hist = rng.choice(_HISTORISCH).format(acc=sc.success_event_accusative, p0=p0_fmt)
            vermutung = rng.choice(_VERMUTUNG)
            stichprobe = rng.choice(_STICHPROBE).format(n=n, sample=sc.sample_object_plural)
            alpha_satz = rng.choice(_ALPHA_SATZ).format(a=alpha_pct)

            intro = (
                f"<p>{sc.intro_prefix} "
                f"{hist} "
                f"{vermutung} "
                f"{stichprobe} "
                f"{alpha_satz}</p>"
            )

            answer = (
                f"Der Ablehnungsbereich lautet: "
                f"[ {numerical(0, tolerance=0, decimals=0)}, \u2026 , {numerical(k, tolerance=0, decimals=0)} ]."
            )

            tasks.append(Task(
                einleitung=intro,
                fragen=["Bestimmen Sie den Ablehnungsbereich der Nullhypothese."],
                antworten=[answer],
            ))

        return tasks

