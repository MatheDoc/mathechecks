import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.hypothesentests.shared import sample_rechtsseitig


def _p_fmt(p: float, rng: random.Random) -> str:
    """Zeigt p entweder als Dezimalzahl (0,38) oder als Prozent (38 %)."""
    if rng.random() < 0.4:
        return f"{round(p * 100)} %"
    return f"{p:.2f}".replace(".", ",")


_HISTORISCH = [
    "Bisher nahm man an, dass die Wahrscheinlichkeit, {success_event_acc} anzutreffen, {p0} beträgt.",
    "Erfahrungsgemäß liegt die Wahrscheinlichkeit, {success_event_acc} zu beobachten, bei {p0}.",
    "Aus früheren Erhebungen ist bekannt, dass mit einer Wahrscheinlichkeit von {p0} {success_event_acc} auftritt.",
    "Bisherige Daten belegen eine Wahrscheinlichkeit von {p0} dafür, {success_event_acc} zu beobachten.",
    "Der bisherige Erfahrungswert sagt: Mit einer Wahrscheinlichkeit von {p0} tritt {success_event_acc} auf.",
]

_VERMUTUNG_RECHTS = [
    "Es besteht nun die Vermutung, dass sich dieser Anteil erhöht hat.",
    "Man vermutet, dass die aktuelle Rate darüber liegt.",
    "Neuere Beobachtungen legen nahe, dass der Anteil gestiegen sein könnte.",
    "Inzwischen wird vermutet, dass dieser Wert gestiegen ist.",
    "Es wird angenommen, dass der wahre Anteil heute größer ist.",
]

_STICHPROBE = [
    "Daher werden {n} {sample_plural} zufällig untersucht.",
    "Um dies zu prüfen, werden {n} {sample_plural} zufällig ausgewählt.",
    "{n} {sample_plural} werden dafür zufällig ausgewählt und überprüft.",
    "Zur Überprüfung werden {n} {sample_plural} stichprobenartig betrachtet.",
]

_ENTSCHEIDUNG_RECHTS = [
    "Werden dabei mindestens {k} {success_plural} festgestellt, gilt die Vermutung als bestätigt - andernfalls hält man an der bisherigen Annahme fest.",
    "Falls mindestens {k} {success_plural} auftreten, sieht man die Vermutung als bestätigt an.",
    "Treten mindestens {k} {success_plural} auf, geht man von der neuen Annahme aus - ansonsten bleibt man beim bisherigen Wert.",
    "Treten in der Stichprobe mindestens {k} {success_plural} auf, wird die Vermutung als richtig angesehen.",
]


class HypothesenergebnisRechtsseitigGenerator(TaskGenerator):
    generator_key = "stochastik.hypothesentests.hypothesenergebnis_rechtsseitig"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for _ in range(count):
            case = sample_rechtsseitig(rng)
            p0_fmt = _p_fmt(case.p0, rng)
            sc = case.scenario

            hist = rng.choice(_HISTORISCH).format(
                success_event_acc=sc.success_event_accusative, p0=p0_fmt
            )
            vermutung = rng.choice(_VERMUTUNG_RECHTS)
            stichprobe = rng.choice(_STICHPROBE).format(n=case.n, sample_plural=sc.sample_object_plural)
            entscheidung = rng.choice(_ENTSCHEIDUNG_RECHTS).format(
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
                "Berechnen Sie die Wahrscheinlichkeit für den Fehler 1. Art",
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

