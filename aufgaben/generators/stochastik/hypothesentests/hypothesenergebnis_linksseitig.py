import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.hypothesentests.shared import sample_linksseitig


def _p_fmt(p: float, rng: random.Random) -> str:
    """Zeigt p entweder als Dezimalzahl (0,38) oder als Prozent (38 %)."""
    if rng.random() < 0.4:
        return f"{round(p * 100)} %"
    return f"{p:.2f}".replace(".", ",")


_HISTORISCH = [
    "Bisher nahm man an, dass die Wahrscheinlichkeit, {success_event_acc} anzutreffen, {p0} beträgt.",
    "Erfahrungsgemäß liegt die Wahrscheinlichkeit, {success_event_acc} zu beobachten, bei {p0}.",
    "Aus früheren Erhebungen ist bekannt, dass mit Wahrscheinlichkeit {p0} {success_event_acc} auftritt.",
    "Bisherige Daten belegen eine Wahrscheinlichkeit von {p0} dafür, {success_event_acc} zu beobachten.",
    "Der bisherige Erfahrungswert sagt: Mit Wahrscheinlichkeit {p0} tritt {success_event_acc} auf.",
]

_VERMUTUNG_LINKS = [
    "Es besteht nun die Vermutung, dass sich dieser Anteil verringert hat.",
    "Man vermutet, dass die aktuelle Rate darunter liegt.",
    "Neuere Beobachtungen legen nahe, dass der Anteil gesunken sein könnte.",
    "Inzwischen wird vermutet, dass dieser Wert gesunken ist.",
    "Es wird angenommen, dass der wahre Anteil heute kleiner ist.",
]

_STICHPROBE = [
    "Daher werden {n} {sample_plural} zufällig untersucht.",
    "Um dies zu prüfen, werden {n} {sample_plural} zufällig ausgewählt.",
    "{n} {sample_plural} werden dafür zufällig ausgewählt und überprüft.",
    "Zur Überprüfung werden {n} {sample_plural} stichprobenartig betrachtet.",
]

_ENTSCHEIDUNG_LINKS = [
    "Werden dabei höchstens {k} {success_plural} festgestellt, gilt die Vermutung als bestätigt - andernfalls hält man an der bisherigen Annahme fest.",
    "Falls höchstens {k} {success_plural} auftreten, sieht man die Vermutung als bestätigt an.",
    "Treten höchstens {k} {success_plural} auf, geht man von der neuen Annahme aus - ansonsten bleibt man beim bisherigen Wert.",
    "Treten in der Stichprobe höchstens {k} {success_plural} auf, wird die Vermutung als richtig angesehen.",
]


class HypothesenergebnisLinksseitigGenerator(TaskGenerator):
    generator_key = "stochastik.hypothesentests.hypothesenergebnis_linksseitig"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for _ in range(count):
            case = sample_linksseitig(rng)
            p0_fmt = _p_fmt(case.p0, rng)
            sc = case.scenario

            hist = rng.choice(_HISTORISCH).format(
                success_event_acc=sc.success_event_accusative, p0=p0_fmt
            )
            vermutung = rng.choice(_VERMUTUNG_LINKS)
            stichprobe = rng.choice(_STICHPROBE).format(n=case.n, sample_plural=sc.sample_object_plural)
            entscheidung = rng.choice(_ENTSCHEIDUNG_LINKS).format(
                k=case.critical_value, success_plural=sc.success_plural
            )

            intro = (
                f"{sc.intro_prefix} "
                f"{hist} "
                f"{vermutung} "
                f"{stichprobe} "
                f"{entscheidung}"
            )

            questions = [
                "Berechnen Sie die Wahrscheinlichkeit für den Fehler 1. Art.",
                (
                    f"In der Stichprobe werden ${case.observed_x}$ {sc.success_plural} festgestellt. "
                    "Ist von der Null- oder der Gegenhypothese auszugehen?"
                ),
            ]

            decision_options = [
                "Von der Gegenhypothese $H_1$ ausgehen ($H_0$ verwerfen)",
                "Von der Nullhypothese $H_0$ ausgehen",
            ]
            decision_correct = 0 if case.reject_h0 else 1

            answers = [
                numerical_stochastik_calc(case.alpha),
                mc(decision_options, correct_index=decision_correct),
            ]

            tasks.append(Task(einleitung=intro, fragen=questions, antworten=answers))

        return tasks

