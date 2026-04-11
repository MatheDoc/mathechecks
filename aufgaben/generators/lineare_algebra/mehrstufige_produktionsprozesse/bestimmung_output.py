"""Check 5: Bestimmung des Outputs (Endprodukte / Zwischenprodukte).

Zwei der drei Matrizen sind gegeben (dritte ggf. berechnen nötig).
Außerdem ist ein Mengenvektor gegeben:
  - z gegeben  → berechne m  (ZE⁻¹ · z  oder direkt ZE gegeben → m = ZE⁻¹ z)
  - r gegeben  → berechne z = RZ⁻¹ · r  oder  m = RE⁻¹ · r

Hier wird "stromabwärts" gerechnet – die zugehörige Matrix muss invertiert
werden, um vom Input auf den Output zu schließen.
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.mpp_shared import (
    antwort_spaltenvektor,
    einleitung_matrizen,
    erzeuge_mpp_triple,
    inverse_nxn,
    mat_vec,
    spaltenvektor_latex,
    var_spaltenvektor_latex,
)


def _random_vec(rng: random.Random, n: int, low: int = 1, high: int = 9) -> list[int]:
    return [rng.randint(low, high) for _ in range(n)]


class BestimmungOutputGenerator(TaskGenerator):
    generator_key = (
        "lineare_algebra.mehrstufige_produktionsprozesse"
        ".bestimmung_output"
    )

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                aufgabe = rng.choice([
                    "z_gegeben_m_gesucht",   # m = ZE⁻¹ · z  (ZE invertierbar)
                    "r_gegeben_z_gesucht",   # z = RZ⁻¹ · r  (RZ invertierbar)
                    "r_gegeben_m_gesucht",   # m = RE⁻¹ · r  (RE invertierbar)
                ])

                # Invertierbarkeit sicherstellen
                if aufgabe == "z_gegeben_m_gesucht":
                    brauche_inv = "ZE"
                elif aufgabe == "r_gegeben_z_gesucht":
                    brauche_inv = "RZ"
                else:
                    brauche_inv = "RE"

                result = erzeuge_mpp_triple(rng, brauche_inv=brauche_inv)
                if result is None:
                    continue
                nR, nZ, nE, rz, ze, re = result

                # Output-Vektor: wir erzeugen den Output und berechnen daraus den
                # Input, um sicherzustellen, dass der Output ganzzahlig positiv ist.
                if aufgabe == "z_gegeben_m_gesucht":
                    # m (Output) klein wählen, z = ZE · m berechnen
                    m = _random_vec(rng, nE, low=1, high=9)
                    z = mat_vec(ze, m)
                    if any(v > 500 or v < 0 for v in z):
                        continue
                    # Gebe zwei Matrizen, die ZE enthalten oder aus denen ZE abgeleitet werden kann
                    paar = rng.choice(["RZ_ZE", "ZE_RE"])
                    if paar == "RZ_ZE":
                        teile = {"RZ": rz, "ZE": ze}
                    else:
                        teile = {"ZE": ze, "RE": re}

                    frage_gegeben = spaltenvektor_latex("z", z)
                    frage_text = (
                        f"Die Zwischenprodukte {frage_gegeben} sollen vollständig "
                        f"zu Endprodukten verarbeitet werden. Bestimmen Sie die zu "
                        f"produzierenden Endprodukte "
                        f"{var_spaltenvektor_latex('m', nE, start='a')}."
                    )
                    antwort = antwort_spaltenvektor(m)
                    sig_vec = ("z", tuple(z))

                elif aufgabe == "r_gegeben_z_gesucht":
                    # z (Output) klein wählen, r = RZ · z berechnen
                    z = _random_vec(rng, nZ, low=1, high=9)
                    r = mat_vec(rz, z)
                    if any(v > 500 or v < 0 for v in r):
                        continue
                    paar = rng.choice(["RZ_ZE", "RZ_RE"])
                    if paar == "RZ_ZE":
                        teile = {"RZ": rz, "ZE": ze}
                    else:
                        teile = {"RZ": rz, "RE": re}

                    frage_gegeben = spaltenvektor_latex("r", r)
                    frage_text = (
                        f"Die Rohstoffe {frage_gegeben} sollen vollständig "
                        f"zu Zwischenprodukten verarbeitet werden. Bestimmen Sie die zu "
                        f"produzierenden Zwischenprodukte "
                        f"{var_spaltenvektor_latex('z', nZ, start='a')}."
                    )
                    antwort = antwort_spaltenvektor(z)
                    sig_vec = ("r", tuple(r))

                else:  # r_gegeben_m_gesucht
                    # m (Output) klein wählen, r = RE · m berechnen
                    m = _random_vec(rng, nE, low=1, high=9)
                    r = mat_vec(re, m)
                    if any(v > 500 or v < 0 for v in r):
                        continue
                    paar = rng.choice(["RZ_ZE", "RZ_RE", "ZE_RE"])
                    if paar == "RZ_ZE":
                        teile = {"RZ": rz, "ZE": ze}
                    elif paar == "RZ_RE":
                        teile = {"RZ": rz, "RE": re}
                    else:
                        teile = {"ZE": ze, "RE": re}

                    frage_gegeben = spaltenvektor_latex("r", r)
                    frage_text = (
                        f"Die Rohstoffe {frage_gegeben} sollen vollständig "
                        f"zu Endprodukten verarbeitet werden. Bestimmen Sie die zu "
                        f"produzierenden Endprodukte "
                        f"{var_spaltenvektor_latex('m', nE, start='a')}."
                    )
                    antwort = antwort_spaltenvektor(m)
                    sig_vec = ("r", tuple(r))

                sig_key = (
                    aufgabe,
                    tuple(tuple(r) for r in rz),
                    tuple(tuple(r) for r in ze),
                    sig_vec,
                )
                if sig_key in seen:
                    continue
                seen.add(sig_key)

                einleitung = einleitung_matrizen(teile)

                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=[frage_text],
                    antworten=[antwort],
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für Bestimmung Output erzeugen."
                )

        return tasks
