import math
import random
from dataclasses import dataclass

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator


@dataclass(frozen=True)
class InterpretationContext:
    intro: str
    item_plural: str
    item_singular_with_article: str
    success_plural: str
    failure_plural: str
    success_predicate: str
    failure_predicate: str
    p_min: float
    p_max: float


CONTEXTS: list[InterpretationContext] = [
    InterpretationContext(
        intro=(
            "Eine Porzellanmanufaktur stellt Vasen her. Der Großteil der produzierten Vasen ist "
            "verkaufsfähig, ein kleiner Teil ist jedoch defekt und muss entsorgt werden."
        ),
        item_plural="Vasen",
        item_singular_with_article="eine Vase",
        success_plural="defekte Vasen",
        failure_plural="verkaufsfähige Vasen",
        success_predicate="defekt ist",
        failure_predicate="verkaufsfähig ist",
        p_min=0.03,
        p_max=0.10,
    ),
    InterpretationContext(
        intro=(
            "Ein Fahrradhersteller prüft Bremshebel aus einer Tagesproduktion. Nur ein kleiner Teil der "
            "Hebel fällt in der Qualitätskontrolle durch."
        ),
        item_plural="Bremshebel",
        item_singular_with_article="ein Bremshebel",
        success_plural="fehlerhafte Bremshebel",
        failure_plural="einwandfreie Bremshebel",
        success_predicate="fehlerhaft ist",
        failure_predicate="einwandfrei ist",
        p_min=0.03,
        p_max=0.10,
    ),
    InterpretationContext(
        intro=(
            "Ein Labor untersucht Blutproben auf einen bestimmten Marker. Nur ein kleiner Teil der "
            "Proben zeigt einen positiven Befund."
        ),
        item_plural="Blutproben",
        item_singular_with_article="eine Blutprobe",
        success_plural="positive Blutproben",
        failure_plural="negative Blutproben",
        success_predicate="positiv ist",
        failure_predicate="negativ ist",
        p_min=0.03,
        p_max=0.10,
    ),
    InterpretationContext(
        intro=(
            "Ein Versandzentrum kontrolliert Pakete auf beschädigte Verpackungen. Die meisten Pakete "
            "sind unbeschädigt, einige weisen Schäden auf."
        ),
        item_plural="Pakete",
        item_singular_with_article="ein Paket",
        success_plural="beschädigte Pakete",
        failure_plural="unbeschädigte Pakete",
        success_predicate="beschädigt ist",
        failure_predicate="unbeschädigt ist",
        p_min=0.03,
        p_max=0.10,
    ),
    InterpretationContext(
        intro=(
            "Eine Schule wertet Mathetests aus. Deutlich weniger als die Hälfte der Tests erreicht "
            "die Bestehensgrenze nicht."
        ),
        item_plural="Tests",
        item_singular_with_article="ein Test",
        success_plural="nicht bestandene Tests",
        failure_plural="bestandene Tests",
        success_predicate="nicht bestanden ist",
        failure_predicate="bestanden ist",
        p_min=0.18,
        p_max=0.40,
    ),
    InterpretationContext(
        intro=(
            "Ein Obstbetrieb sortiert Äpfel nach Qualitätsklassen. Nur wenige Äpfel werden wegen Druckstellen "
            "aussortiert."
        ),
        item_plural="Äpfel",
        item_singular_with_article="ein Apfel",
        success_plural="aussortierte Äpfel",
        failure_plural="verkaufsfähige Äpfel",
        success_predicate="aussortiert wird",
        failure_predicate="verkaufsfähig ist",
        p_min=0.03,
        p_max=0.12,
    ),
]


def _latex_decimal(value: float, decimals: int) -> str:
    return f"{value:.{decimals}f}".replace(".", "{,}")


def _predicate_plural(predicate_singular: str) -> str:
    if predicate_singular.endswith(" ist"):
        return predicate_singular[:-4] + " sind"
    if predicate_singular.endswith(" wird"):
        return predicate_singular[:-5] + " werden"
    return predicate_singular


def _sample_parameters(rng: random.Random, p_min: float, p_max: float) -> tuple[int, int, float, float, int]:
    p_min_pct = max(1, int(round(p_min * 100)))
    p_max_pct = min(99, int(round(p_max * 100)))
    if p_min_pct > p_max_pct:
        raise ValueError("Ungültiger p-Bereich im InterpretationContext.")

    for _ in range(400):
        n = rng.randint(35, 85)
        p = rng.choice([x / 100 for x in range(p_min_pct, p_max_pct + 1)])
        mu = n * p
        sigma = math.sqrt(n * p * (1 - p))

        low = max(1, int(round(mu - 1.0 * sigma)))
        high = min(n - 1, int(round(mu + 1.0 * sigma)))
        if low > high:
            continue
        k = rng.randint(low, high)

        result = math.comb(n, k) * (p**k) * ((1 - p) ** (n - k))
        if 0.02 <= result <= 0.35:
            return n, k, p, result, n - k

    raise ValueError("Konnte keine plausiblen Parameter für Interpretation-Aufgabe erzeugen.")


class BinomialInterpretationParameterGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.interpretation_parameter"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            context = CONTEXTS[index % len(CONTEXTS)]
            n, k, p, result, n_minus_k = _sample_parameters(rng, p_min=context.p_min, p_max=context.p_max)
            q = 1 - p

            use_complement_as_success = rng.choice([False, True])
            if use_complement_as_success:
                event_plural = context.failure_plural
                anti_event_plural = context.success_plural
                event_predicate = context.failure_predicate
                anti_event_predicate = context.success_predicate
                event_probability = q
                anti_event_probability = p
                event_count = n_minus_k
                anti_event_count = k
            else:
                event_plural = context.success_plural
                anti_event_plural = context.failure_plural
                event_predicate = context.success_predicate
                anti_event_predicate = context.failure_predicate
                event_probability = p
                anti_event_probability = q
                event_count = k
                anti_event_count = n_minus_k

            formula_result = (
                math.comb(n, event_count)
                * (event_probability**event_count)
                * (anti_event_probability ** (anti_event_count))
            )

            formula = (
                "\\[ "
                f"\\binom{{{n}}}{{{event_count}}}\\cdot {_latex_decimal(event_probability, 2)}^{{{event_count}}}"
                f"\\cdot {_latex_decimal(anti_event_probability, 2)}^{{{anti_event_count}}}"
                f"={_latex_decimal(formula_result, 4)} "
                "\\]"
            )

            intro = (
                f"{context.intro} In einer Stichprobe werden {event_plural} und "
                f"{anti_event_plural} festgestellt. Danach wird die folgende Rechnung aufgestellt: "
                f"{formula}"
            )

            optionen = [
                f"Die Anzahl der untersuchten {context.item_plural}.",
                (
                    f"Die Anzahl der {context.item_plural}, die "
                    f"{_predicate_plural(event_predicate)}."
                ),
                f"Die Wahrscheinlichkeit, dass {context.item_singular_with_article} {event_predicate}.",
                f"Die Wahrscheinlichkeit, dass {context.item_singular_with_article} {anti_event_predicate}.",
                (
                    f"Die Anzahl der {context.item_plural}, die "
                    f"{_predicate_plural(anti_event_predicate)}."
                ),
                (
                    f"Die Wahrscheinlichkeit, dass unter {n} {context.item_plural} genau {event_count} "
                    f"{_predicate_plural(event_predicate)}."
                ),
            ]

            fragen = [
                f"Was bedeutet die Zahl \\({n}\\) im Sachzusammenhang?",
                f"Was bedeutet die Zahl \\({event_count}\\) im Sachzusammenhang?",
                f"Was bedeutet die Zahl \\({_latex_decimal(event_probability, 2)}\\) im Sachzusammenhang?",
                f"Was bedeutet die Zahl \\({_latex_decimal(anti_event_probability, 2)}\\) im Sachzusammenhang?",
                f"Was bedeutet die Zahl \\({anti_event_count}\\) im Sachzusammenhang?",
                f"Was bedeutet die Zahl \\({_latex_decimal(formula_result, 4)}\\) im Sachzusammenhang?",
            ]

            antworten = [
                mc(optionen, correct_index=0),
                mc(optionen, correct_index=1),
                mc(optionen, correct_index=2),
                mc(optionen, correct_index=3),
                mc(optionen, correct_index=4),
                mc(optionen, correct_index=5),
            ]

            tasks.append(Task(einleitung=intro, fragen=fragen, antworten=antworten))

        return tasks
