"""Check 6: Erlöse, Kosten, Gewinn – Kennzahlen.

Alle drei Produktionsmatrizen, ein Mengenvektor m, Kostenvektoren
k_R, k_Z, k_E, Fixkosten K_fix und der Preisvektor p sind gegeben.

9 Fragen:
  1. Vektor der variablen Stückkosten k_v
  2. Vektor der Stückdeckungsbeiträge db
  3. Rohstoffkosten
  4. Fertigungskosten der ersten Produktionsstufe
  5. Fertigungskosten der zweiten Produktionsstufe
  6. Gesamte Kosten
  7. Erlös
  8. Deckungsbeitrag
  9. Gewinn
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.mpp_shared import (
    antwort_zeilenvektor,
    dot,
    einleitung_matrizen,
    erzeuge_mpp_triple,
    mat_vec,
    numerical_int,
    spaltenvektor_latex,
    var_zeilenvektor_latex,
    zeilenvektor_latex,
)


def _random_vec(rng: random.Random, n: int, low: int = 1, high: int = 9) -> list[int]:
    return [rng.randint(low, high) for _ in range(n)]


def _col(mat: list[list[int]], j: int) -> list[int]:
    """j-te Spalte einer Matrix als Liste."""
    return [mat[i][j] for i in range(len(mat))]


class EkgKennzahlenGenerator(TaskGenerator):
    generator_key = (
        "lineare_algebra.mehrstufige_produktionsprozesse"
        ".ekg_kennzahlen"
    )

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                result = erzeuge_mpp_triple(rng)
                if result is None:
                    continue
                nR, nZ, nE, rz, ze, re = result

                m = _random_vec(rng, nE, low=1, high=9)
                k_R = _random_vec(rng, nR, low=1, high=9)
                k_Z = _random_vec(rng, nZ, low=1, high=9)
                k_E = _random_vec(rng, nE, low=1, high=9)
                K_fix = rng.randint(10, 80) * 100  # 1000 – 8000 in 100er-Schritten

                # Variable Stückkosten: k_v_j = k_R^T · RE_col_j + k_Z^T · ZE_col_j + k_E_j
                k_v = []
                for j in range(nE):
                    kv_j = dot(k_R, _col(re, j)) + dot(k_Z, _col(ze, j)) + k_E[j]
                    k_v.append(kv_j)

                # Preis pro Stück: um Aufgaben spannender zu machen,
                # Preis = k_v_j ± Δ (mal positiv, mal negativ)
                p = []
                for j in range(nE):
                    delta = rng.randint(-200, 600)
                    p.append(k_v[j] + delta)
                # Preise müssen positiv sein
                if any(pj <= 0 for pj in p):
                    continue

                # Stückdeckungsbeiträge
                db = [p[j] - k_v[j] for j in range(nE)]

                # Mengen-basierte Kennzahlen
                z = mat_vec(ze, m)   # Zwischenprodukte
                r = mat_vec(re, m)   # Rohstoffe

                rohstoffkosten = dot(k_R, r)
                fk1 = dot(k_Z, z)    # Fertigungskosten 1. Stufe
                fk2 = dot(k_E, m)    # Fertigungskosten 2. Stufe
                K_var_total = rohstoffkosten + fk1 + fk2
                K_total = K_var_total + K_fix
                erloesval = dot(p, m)
                deckungsbeitrag = erloesval - K_var_total
                gewinn = erloesval - K_total

                # Plausibilität: keine absurd großen Zahlen
                if any(abs(v) > 100000 for v in [rohstoffkosten, K_total, erloesval]):
                    continue

                sig = (
                    tuple(tuple(row) for row in rz),
                    tuple(tuple(row) for row in ze),
                    tuple(m),
                )
                if sig in seen:
                    continue
                seen.add(sig)

                # Einleitung
                einleitung = einleitung_matrizen(
                    {"RZ": rz, "ZE": ze, "RE": re},
                    extras={
                        "m": spaltenvektor_latex("m", m),
                        "k_R": zeilenvektor_latex("k_R", k_R),
                        "k_Z": zeilenvektor_latex("k_Z", k_Z),
                        "k_E": zeilenvektor_latex("k_E", k_E),
                        "K_fix": f"\\( K_{{fix}}={K_fix}\\)",
                        "p": zeilenvektor_latex("p", p),
                    },
                )

                # Fragen & Antworten
                fragen = [
                    f"Berechnen Sie den Vektor der variablen Stückkosten "
                    f"{var_zeilenvektor_latex('k_v', nE)}.",
                    f"Berechnen Sie den Vektor der Stückdeckungsbeiträge "
                    f"{var_zeilenvektor_latex('db', nE)}.",
                    "Berechnen Sie die Rohstoffkosten.",
                    "Berechnen Sie die Fertigungskosten der ersten Produktionsstufe.",
                    "Berechnen Sie die Fertigungskosten der zweiten Produktionsstufe.",
                    "Berechnen Sie die gesamten Kosten.",
                    "Berechnen Sie den Erlös.",
                    "Berechnen Sie den Deckungsbeitrag.",
                    "Berechnen Sie den Gewinn.",
                ]
                antworten = [
                    antwort_zeilenvektor(k_v),
                    antwort_zeilenvektor(db),
                    numerical_int(rohstoffkosten),
                    numerical_int(fk1),
                    numerical_int(fk2),
                    numerical_int(K_total),
                    numerical_int(erloesval),
                    numerical_int(deckungsbeitrag),
                    numerical_int(gewinn),
                ]

                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=fragen,
                    antworten=antworten,
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für EKG-Kennzahlen erzeugen."
                )

        return tasks
