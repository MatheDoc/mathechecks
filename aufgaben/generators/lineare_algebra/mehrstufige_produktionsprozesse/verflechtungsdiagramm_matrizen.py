"""Check 1: Verflechtungsdiagramm ↔ Produktionsmatrizen.

Ein Verflechtungsdiagramm (mit Lücken) und die beiden Produktionsmatrizen
RZ und ZE (ebenfalls mit Lücken) sind gegeben.  Jeder Wert ist in genau
einer Darstellung sichtbar und in der anderen als eingekreiste Nummer
markiert.  Die Schüler bestimmen die fehlenden Werte.
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator

CIRCLED = {
    1: "\u2460", 2: "\u2461", 3: "\u2462", 4: "\u2463",
    5: "\u2464", 6: "\u2465", 7: "\u2466", 8: "\u2467",
}

NUM_SLOTS = 5


# ---------------------------------------------------------------------------
#  Szenario-Erzeugung
# ---------------------------------------------------------------------------

def _generate_scenario(rng: random.Random):
    """Erzeuge Rohstoff/Zwischen/Endprodukt-Matrizen mit genug Nicht-Null-Einträgen."""
    nR = rng.choice([2, 3])
    nZ = rng.choice([2, 3])
    nE = rng.choice([2, 3])

    # --- RZ (nR × nZ) ---
    rz = [[0] * nZ for _ in range(nR)]
    for i in range(nR):
        for j in range(nZ):
            rz[i][j] = 0 if rng.random() < 0.25 else rng.randint(1, 8)

    # Jede Spalte (Zwischenprodukt) braucht mindestens einen Rohstoff
    for j in range(nZ):
        if all(rz[i][j] == 0 for i in range(nR)):
            rz[rng.randint(0, nR - 1)][j] = rng.randint(1, 8)
    # Jede Zeile (Rohstoff) muss irgendwo eingehen
    for i in range(nR):
        if all(rz[i][j] == 0 for j in range(nZ)):
            rz[i][rng.randint(0, nZ - 1)] = rng.randint(1, 8)

    # --- ZE (nZ × nE) ---
    ze = [[0] * nE for _ in range(nZ)]
    for i in range(nZ):
        for j in range(nE):
            ze[i][j] = 0 if rng.random() < 0.15 else rng.randint(1, 6)
    for j in range(nE):
        if all(ze[i][j] == 0 for i in range(nZ)):
            ze[rng.randint(0, nZ - 1)][j] = rng.randint(1, 6)
    for i in range(nZ):
        if all(ze[i][j] == 0 for j in range(nE)):
            ze[i][rng.randint(0, nE - 1)] = rng.randint(1, 6)

    # Nicht-Null-Einträge sammeln
    nz_rz = [("rz", i, j, rz[i][j]) for i in range(nR) for j in range(nZ) if rz[i][j] > 0]
    nz_ze = [("ze", i, j, ze[i][j]) for i in range(nZ) for j in range(nE) if ze[i][j] > 0]

    if len(nz_rz) + len(nz_ze) < NUM_SLOTS:
        return None

    return nR, nZ, nE, rz, ze, nz_rz, nz_ze


# ---------------------------------------------------------------------------
#  Aufgabe zusammenbauen
# ---------------------------------------------------------------------------

def _latex_matrix(mat, matrix_name, slot_lookup):
    """Erzeuge den LaTeX-Inhalt einer pmatrix mit Slot-Markierungen."""
    rows_tex = []
    for i, row in enumerate(mat):
        cells = []
        for j, v in enumerate(row):
            key = (matrix_name, i, j)
            if key in slot_lookup:
                idx, _val, location = slot_lookup[key]
                if location == "matrix":
                    cells.append(f"\\text{{{CIRCLED[idx]}}}")
                else:
                    cells.append(str(v))
            else:
                cells.append(str(v))
        rows_tex.append(" & ".join(cells))
    return " \\\\ ".join(rows_tex)


def _build_edges(mat, matrix_name, n_rows, n_cols, slot_lookup):
    """Erzeuge die Kantenliste [fromIdx, toIdx, label] für das Diagramm."""
    edges = []
    for i in range(n_rows):
        for j in range(n_cols):
            if mat[i][j] == 0:
                continue
            key = (matrix_name, i, j)
            if key in slot_lookup:
                idx, val, location = slot_lookup[key]
                label = CIRCLED[idx] if location == "diagram" else str(val)
            else:
                label = str(mat[i][j])
            edges.append([i, j, label])
    return edges


def _join_labels(labels):
    """'R1, R2 und R3' – deutsche Aufzählung."""
    if len(labels) <= 1:
        return labels[0] if labels else ""
    return ", ".join(labels[:-1]) + " und " + labels[-1]


def _create_task(rng, nR, nZ, nE, rz, ze, nz_rz, nz_ze):
    all_nz = nz_rz + nz_ze
    slot_entries = rng.sample(all_nz, NUM_SLOTS)

    # Zuweisung: Slot in Diagramm oder in Matrix?
    slots = []
    for idx_1, (matrix, i, j, v) in enumerate(slot_entries, 1):
        location = rng.choice(["diagram", "matrix"])
        slots.append((idx_1, matrix, i, j, v, location))

    # Sicherstellen, dass mindestens ein Slot in jeder Darstellung liegt
    locs = {s[5] for s in slots}
    if "diagram" not in locs:
        s = slots[0]
        slots[0] = (s[0], s[1], s[2], s[3], s[4], "diagram")
    if "matrix" not in locs:
        s = slots[-1]
        slots[-1] = (s[0], s[1], s[2], s[3], s[4], "matrix")

    slot_lookup = {}
    for idx_1, matrix, i, j, v, location in slots:
        slot_lookup[(matrix, i, j)] = (idx_1, v, location)

    # --- Visual-Spec ---
    stufe1 = _build_edges(rz, "rz", nR, nZ, slot_lookup)
    stufe2 = _build_edges(ze, "ze", nZ, nE, slot_lookup)

    r_labels = [f"R{k + 1}" for k in range(nR)]
    z_labels = [f"Z{k + 1}" for k in range(nZ)]
    e_labels = [f"E{k + 1}" for k in range(nE)]

    visual = {
        "type": "plot",
        "spec": {
            "type": "verflechtungsdiagramm",
            "rohstoffe": r_labels,
            "zwischenprodukte": z_labels,
            "endprodukte": e_labels,
            "stufe1": stufe1,
            "stufe2": stufe2,
        },
    }

    # --- Einleitung ---
    rz_tex = _latex_matrix(rz, "rz", slot_lookup)
    ze_tex = _latex_matrix(ze, "ze", slot_lookup)

    einleitung = (
        f"In einem zweistufigen Produktionsprozess werden "
        f"die Rohstoffe {_join_labels(r_labels)} "
        f"zu den Zwischenprodukten {_join_labels(z_labels)} verarbeitet, "
        f"aus denen die Endprodukte {_join_labels(e_labels)} hergestellt werden.\n\n"
        f"Das Verflechtungsdiagramm und die Produktionsmatrizen "
        f"enthalten Lücken. Bestimmen Sie die fehlenden Werte.\n\n"
        f"$$\n"
        f"RZ = \\begin{{pmatrix}} {rz_tex} \\end{{pmatrix}}, \\quad "
        f"ZE = \\begin{{pmatrix}} {ze_tex} \\end{{pmatrix}}\n"
        f"$$"
    )

    # --- Fragen / Antworten ---
    fragen = [CIRCLED[idx] for idx, *_ in slots]
    antworten = [f"{{1:NUMERICAL:={v}:0}}" for _, _, _, _, v, _ in slots]

    return Task(
        einleitung=einleitung,
        fragen=fragen,
        antworten=antworten,
        visual=visual,
    )


# ---------------------------------------------------------------------------
#  Generator
# ---------------------------------------------------------------------------

class VerflechtungsdiagrammMatrizenGenerator(TaskGenerator):
    generator_key = (
        "lineare_algebra.mehrstufige_produktionsprozesse"
        ".verflechtungsdiagramm_matrizen"
    )

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(500):
                result = _generate_scenario(rng)
                if result is None:
                    continue
                nR, nZ, nE, rz, ze, nz_rz, nz_ze = result

                sig = (
                    tuple(tuple(r) for r in rz),
                    tuple(tuple(r) for r in ze),
                )
                if sig in seen:
                    continue
                seen.add(sig)

                tasks.append(
                    _create_task(rng, nR, nZ, nE, rz, ze, nz_rz, nz_ze)
                )
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für "
                    "Verflechtungsdiagramm-Matrizen erzeugen."
                )

        return tasks
