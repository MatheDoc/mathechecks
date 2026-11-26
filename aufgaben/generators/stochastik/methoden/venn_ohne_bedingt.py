"""Venn-Diagramme interpretieren (ohne bedingte Wahrscheinlichkeiten).

Die Ergebnismenge X zerfällt in vier Teilflächen:
  "a"  = A ∩ B̅,  "ab" = A ∩ B,  "b" = A̅ ∩ B,  "n" = A̅ ∩ B̅.

Pro Aufgabe ist eine Kombination von Teilflächen markiert (Plotly-Spec ``venn``,
Renderer ``assets/js/visuals/venn.js`` mit denselben Schlüsseln). Gefragt ist die
dargestellte Wahrscheinlichkeit als MC-Frage mit 4 Optionen. Die Distraktoren
unterscheiden sich bevorzugt um genau eine Teilfläche von der richtigen Lösung
(typische Verwechslungen wie P(A) ↔ P(A ∩ B̅) oder P(A ∪ B) ↔ P(A ∪ B̅)).
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator


REGIONEN = ("a", "ab", "b", "n")

# Symbolische Darstellungen je Flächenkombination (Schlüssel: sortiertes Tupel).
# Erste Form = Standardform. Formen mit „1 - …“ stehen nicht im Pool, damit die
# Optionen reine Ereignis-Schreibweisen bleiben (wie im Skript).
_FORMEN: dict[tuple[str, ...], list[str]] = {
    (): [r"P(A\cap\overline{A})", r"P(B\cap\overline{B})"],
    ("a",): [r"P(A\cap\overline{B})"],
    ("ab",): [r"P(A\cap B)"],
    ("b",): [r"P(\overline{A}\cap B)"],
    ("n",): [r"P(\overline{A}\cap\overline{B})"],
    ("a", "ab"): [r"P(A)"],
    ("ab", "b"): [r"P(B)"],
    ("a", "b"): [
        r"P(A\cup B)-P(A\cap B)",
        r"P(A\cap\overline{B})+P(\overline{A}\cap B)",
    ],
    ("a", "n"): [r"P(\overline{B})"],
    ("b", "n"): [r"P(\overline{A})"],
    ("ab", "n"): [r"P(A\cap B)+P(\overline{A}\cap\overline{B})"],
    ("a", "ab", "b"): [r"P(A\cup B)"],
    ("a", "ab", "n"): [r"P(A\cup\overline{B})"],
    ("ab", "b", "n"): [r"P(\overline{A}\cup B)"],
    ("a", "b", "n"): [r"P(\overline{A}\cup\overline{B})"],
    ("a", "ab", "b", "n"): [r"P(A\cup\overline{A})", r"P(B\cup\overline{B})"],
}

# Gesuchte Flächen: alle Kombinationen außer „nichts markiert“
_ZIELE = [key for key in _FORMEN if key]

_EINLEITUNG = (
    "Gegeben ist das folgende Venn-Diagramm mit den Ereignissen $A$ und $B$ "
    "in der Ergebnismenge $X$."
)
_FRAGE = (
    "Geben Sie an, welche Wahrscheinlichkeit durch den Inhalt "
    "der markierten Fläche dargestellt wird."
)


def _abstand(k1: tuple[str, ...], k2: tuple[str, ...]) -> int:
    return len(set(k1) ^ set(k2))


def _distraktoren(ziel: tuple[str, ...], rng: random.Random) -> list[tuple[str, ...]]:
    """Zwei „Nachbarn“ (eine Teilfläche mehr/weniger) und eine weitere Kombination."""
    nachbarn = [k for k in _FORMEN if _abstand(k, ziel) == 1]
    rng.shuffle(nachbarn)
    gewaehlt = nachbarn[:2]
    rest = [k for k in _FORMEN if k != ziel and k not in gewaehlt]
    # bevorzugt nicht-triviale Kombinationen als dritten Distraktor
    nicht_trivial = [k for k in rest if 0 < len(k) < 4]
    gewaehlt.append(rng.choice(nicht_trivial or rest))
    return gewaehlt


def _option(key: tuple[str, ...], rng: random.Random) -> str:
    return rf"\( {rng.choice(_FORMEN[key])} \)"


def _visual(key: tuple[str, ...]) -> dict:
    return {
        "type": "plot",
        "spec": {
            "type": "venn",
            "markiert": list(key),
        },
    }


class MethodenVennOhneBedingtGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.venn_ohne_bedingt"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)

        # Jede Kombination mindestens einmal, danach zufällige nicht-triviale
        reihenfolge: list[tuple[str, ...]] = []
        while len(reihenfolge) < count:
            runde = list(_ZIELE) if not reihenfolge else [k for k in _ZIELE if len(k) < 4]
            rng.shuffle(runde)
            reihenfolge.extend(runde)
        reihenfolge = reihenfolge[:count]

        tasks: list[Task] = []
        for ziel in reihenfolge:
            keys = [ziel] + _distraktoren(ziel, rng)
            rng.shuffle(keys)
            optionen = [_option(k, rng) for k in keys]
            antwort = mc(optionen, correct_index=keys.index(ziel))
            tasks.append(
                Task(
                    einleitung=_EINLEITUNG,
                    fragen=[_FRAGE],
                    antworten=[antwort],
                    visual=_visual(ziel),
                )
            )
        return tasks
