"""Check 7: Bestimmung konkreter Produktionsvektoren bei Lagerräumung."""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.shared import (
    ProduktionsSzenario,
    einleitung_text,
    erzeuge_szenario,
    koeff_deckungsbeitrag,
    koeff_erloes,
    koeff_summe,
    koeff_variable_kosten,
    komponente,
    numerical_int,
    t_fuer_zielwert,
)


def _szenario_signatur(sz: ProduktionsSzenario) -> tuple:
    return (tuple(sz.a), tuple(sz.b), sz.t_min, sz.t_max,
            tuple(sz.kv), tuple(sz.p))


class LagerraeumungParameterGenerator(TaskGenerator):
    generator_key = "lineare_algebra.mehrstufige_produktionsprozesse.lagerraeumung_parameter"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                sz = erzeuge_szenario(rng)
                sig = _szenario_signatur(sz)
                if sig in seen:
                    continue

                # --- Frage 1: t so dass E_i genau {wert} ME ---
                # Wähle ein Endprodukt mit b_i != 0
                nonzero = [i for i in range(4) if sz.b[i] != 0]
                idx1 = rng.choice(nonzero)
                # Wähle ein t im zulässigen Bereich (nicht am Rand, wenn möglich)
                inner_min = sz.t_min + 1 if sz.t_max - sz.t_min > 2 else sz.t_min
                inner_max = sz.t_max - 1 if sz.t_max - sz.t_min > 2 else sz.t_max
                t1 = rng.randint(inner_min, inner_max)
                wert1 = komponente(sz, idx1, t1)

                # --- Frage 2: t so dass Gesamtmenge = {wert} ME ---
                c0_s, c1_s = koeff_summe(sz)
                if c1_s == 0:
                    continue
                t2 = rng.randint(inner_min, inner_max)
                wert2 = c0_s + c1_s * t2

                # --- Frage 3: t so dass variable Kosten = {wert} GE ---
                c0_kv, c1_kv = koeff_variable_kosten(sz)
                if c1_kv == 0:
                    continue
                t3 = rng.randint(inner_min, inner_max)
                wert3 = c0_kv + c1_kv * t3

                # --- Frage 4: t so dass Erlös = {wert} GE ---
                c0_e, c1_e = koeff_erloes(sz)
                if c1_e == 0:
                    continue
                t4 = rng.randint(inner_min, inner_max)
                wert4 = c0_e + c1_e * t4

                # --- Frage 5: t so dass Deckungsbeitrag = {wert} GE ---
                c0_db, c1_db = koeff_deckungsbeitrag(sz)
                if c1_db == 0:
                    continue
                t5 = rng.randint(inner_min, inner_max)
                wert5 = c0_db + c1_db * t5

                # Verifikation: alle t-Werte ganzzahlig und im Bereich
                # (ist per Konstruktion erfüllt, aber zur Sicherheit)
                for t_val in (t1, t2, t3, t4, t5):
                    if not (sz.t_min <= t_val <= sz.t_max):
                        break
                else:
                    # Sicherstellen, dass die t-Werte unterschiedlich genug sind
                    # (verschiedene Fragen können gleiche t-Werte haben, das ist ok)
                    seen.add(sig)

                    fragen = [
                        f"Bestimmen Sie \\( t \\) so, dass von E{idx1 + 1} genau {wert1} ME produziert werden.",
                        f"Bestimmen Sie \\( t \\) so, dass insgesamt {wert2} ME der Endprodukte produziert werden.",
                        f"Bestimmen Sie \\( t \\) so, dass die variablen Kosten {wert3} GE betragen.",
                        f"Bestimmen Sie \\( t \\) so, dass der Erlös {wert4} GE beträgt.",
                        f"Bestimmen Sie \\( t \\) so, dass der Deckungsbeitrag {wert5} GE beträgt.",
                    ]

                    antworten = [
                        numerical_int(t1),
                        numerical_int(t2),
                        numerical_int(t3),
                        numerical_int(t4),
                        numerical_int(t5),
                    ]

                    tasks.append(Task(
                        einleitung=einleitung_text(sz),
                        fragen=fragen,
                        antworten=antworten,
                    ))
                    break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für Lagerräumung-Parameter erzeugen."
                )

        return tasks
