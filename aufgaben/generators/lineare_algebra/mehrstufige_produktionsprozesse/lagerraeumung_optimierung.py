"""Check 6: Minimierung/Maximierung bei Lagerräumung."""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.shared import (
    ProduktionsSzenario,
    deckungsbeitrag,
    einleitung_text,
    erloes,
    erzeuge_szenario,
    koeff_deckungsbeitrag,
    koeff_erloes,
    koeff_variable_kosten,
    komponente,
    numerical_int,
    optimum_linear,
    optimum_t,
    variable_kosten,
)


def _szenario_signatur(sz: ProduktionsSzenario) -> tuple:
    return (tuple(sz.a), tuple(sz.b), sz.t_min, sz.t_max,
            tuple(sz.kv), tuple(sz.p))


class LagerraeumungOptimierungGenerator(TaskGenerator):
    generator_key = "lineare_algebra.mehrstufige_produktionsprozesse.lagerraeumung_optimierung"

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
                seen.add(sig)

                # --- Frage 1: maximale Menge eines Endprodukts mit b_i > 0 ---
                pos_indices = [i for i in range(4) if sz.b[i] > 0]
                idx_max = rng.choice(pos_indices)
                # Maximum bei t_max (da b_i > 0)
                max_menge = komponente(sz, idx_max, sz.t_max)

                # --- Frage 2: minimale Menge eines Endprodukts mit b_j < 0 ---
                neg_indices = [i for i in range(4) if sz.b[i] < 0]
                idx_min = rng.choice(neg_indices)
                # Minimum bei t_max (da b_j < 0)
                min_menge = komponente(sz, idx_min, sz.t_max)

                # --- Frage 3: minimale variable Kosten ---
                c0_kv, c1_kv = koeff_variable_kosten(sz)
                min_kv = optimum_linear(c0_kv, c1_kv, sz.t_min, sz.t_max, maximize=False)

                # --- Frage 4: maximaler Erlös ---
                c0_e, c1_e = koeff_erloes(sz)
                max_e = optimum_linear(c0_e, c1_e, sz.t_min, sz.t_max, maximize=True)

                # --- Frage 5: maximaler Deckungsbeitrag ---
                c0_db, c1_db = koeff_deckungsbeitrag(sz)
                max_db = optimum_linear(c0_db, c1_db, sz.t_min, sz.t_max, maximize=True)

                fragen = [
                    f"Bestimmen Sie die maximale Menge, die von E{idx_max + 1} produziert werden könnte.",
                    f"Bestimmen Sie die minimale Menge, die von E{idx_min + 1} produziert werden müsste.",
                    "Bestimmen Sie die minimalen variablen Kosten.",
                    "Bestimmen Sie den maximalen Erlös.",
                    "Bestimmen Sie den maximalen Deckungsbeitrag.",
                ]

                antworten = [
                    numerical_int(max_menge),
                    numerical_int(min_menge),
                    numerical_int(min_kv),
                    numerical_int(max_e),
                    numerical_int(max_db),
                ]

                tasks.append(Task(
                    einleitung=einleitung_text(sz),
                    fragen=fragen,
                    antworten=antworten,
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für Lagerräumung-Optimierung erzeugen."
                )

        return tasks
