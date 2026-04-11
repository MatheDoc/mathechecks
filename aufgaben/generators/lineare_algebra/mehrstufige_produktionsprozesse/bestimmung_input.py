"""Check 4: Bestimmung des Inputs (Rohstoffe / Zwischenprodukte).

Zwei der drei Matrizen sind gegeben (dritte ggf. berechnen nötig).
Außerdem ist ein Mengenvektor gegeben:
  - z gegeben  → berechne r = RZ · z
  - m gegeben  → berechne z = ZE · m  oder  r = RE · m

(Output → Input: "stromaufwärts")
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.mpp_shared import (
    antwort_spaltenvektor,
    einleitung_matrizen,
    erzeuge_mpp_triple,
    mat_vec,
    var_spaltenvektor_latex,
)


def _random_vec(rng: random.Random, n: int, low: int = 1, high: int = 9) -> list[int]:
    return [rng.randint(low, high) for _ in range(n)]


class BestimmungInputGenerator(TaskGenerator):
    generator_key = (
        "lineare_algebra.mehrstufige_produktionsprozesse"
        ".bestimmung_input"
    )

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                # Aufgabentyp wählen
                aufgabe = rng.choice([
                    "z_gegeben_r_gesucht",   # r = RZ · z
                    "m_gegeben_z_gesucht",   # z = ZE · m
                    "m_gegeben_r_gesucht",   # r = RE · m
                ])

                # Welche Matrizen werden gebraucht / gegeben?
                if aufgabe == "z_gegeben_r_gesucht":
                    # Brauche RZ. Gebe RZ + eine weitere.
                    result = erzeuge_mpp_triple(rng)
                elif aufgabe == "m_gegeben_z_gesucht":
                    # Brauche ZE. Gebe ZE + eine weitere.
                    result = erzeuge_mpp_triple(rng)
                else:  # m_gegeben_r_gesucht
                    # Brauche RE. Gebe zwei beliebige (RE wird ggf. berechnet).
                    result = erzeuge_mpp_triple(rng)

                if result is None:
                    continue
                nR, nZ, nE, rz, ze, re = result

                # Gegeben-Vektoren und Zielvektoren bestimmen
                if aufgabe == "z_gegeben_r_gesucht":
                    z = _random_vec(rng, nZ)
                    r = mat_vec(rz, z)
                    if any(v > 500 for v in r):
                        continue
                    # Gebe RZ und ZE (oder RE) – wähle Paar
                    paar = rng.choice(["RZ_ZE", "RZ_RE"])
                    if paar == "RZ_ZE":
                        teile = {"RZ": rz, "ZE": ze}
                    else:
                        teile = {"RZ": rz, "RE": re}
                    teile_vec = {"z": z}
                    frage_text = (
                        f"Die Zwischenprodukte {var_spaltenvektor_latex('z', nZ)} "
                        f"sollen produziert werden. Bestimmen Sie die dafür "
                        f"benötigten Rohstoffe "
                        f"{var_spaltenvektor_latex('r', nR, start='a')}."
                    )
                    antwort = antwort_spaltenvektor(r)

                elif aufgabe == "m_gegeben_z_gesucht":
                    m = _random_vec(rng, nE)
                    z = mat_vec(ze, m)
                    if any(v > 500 for v in z):
                        continue
                    paar = rng.choice(["RZ_ZE", "ZE_RE"])
                    if paar == "RZ_ZE":
                        teile = {"RZ": rz, "ZE": ze}
                    else:
                        teile = {"ZE": ze, "RE": re}
                    teile_vec = {"m": m}
                    frage_text = (
                        f"Die Endprodukte {var_spaltenvektor_latex('m', nE)} "
                        f"sollen produziert werden. Bestimmen Sie die dafür "
                        f"benötigten Zwischenprodukte "
                        f"{var_spaltenvektor_latex('z', nZ, start='a')}."
                    )
                    antwort = antwort_spaltenvektor(z)

                else:  # m_gegeben_r_gesucht
                    m = _random_vec(rng, nE)
                    r = mat_vec(re, m)
                    if any(v > 500 for v in r):
                        continue
                    paar = rng.choice(["RZ_ZE", "RZ_RE", "ZE_RE"])
                    if paar == "RZ_ZE":
                        teile = {"RZ": rz, "ZE": ze}
                    elif paar == "RZ_RE":
                        teile = {"RZ": rz, "RE": re}
                    else:
                        teile = {"ZE": ze, "RE": re}
                    teile_vec = {"m": m}
                    frage_text = (
                        f"Die Endprodukte {var_spaltenvektor_latex('m', nE)} "
                        f"sollen produziert werden. Bestimmen Sie die dafür "
                        f"benötigten Rohstoffe "
                        f"{var_spaltenvektor_latex('r', nR, start='a')}."
                    )
                    antwort = antwort_spaltenvektor(r)

                # Deduplizierung
                sig_key = (aufgabe, tuple(tuple(r) for r in rz),
                           tuple(tuple(r) for r in ze),
                           tuple(teile_vec.get("z", [])),
                           tuple(teile_vec.get("m", [])))
                if sig_key in seen:
                    continue
                seen.add(sig_key)

                # Einleitung: Matrizen + Vektor in Gegeben
                # Ersetze Variablen-Vektoren durch echte Werte in Einleitung
                einleitung = einleitung_matrizen(teile)

                # Frage enthält den gegebenen Vektor + den gesuchten als Variablen
                # Der gegebene Vektor steht im Fragetext mit echten Werten
                # Wir müssen den gegebenen Vektor als echten LaTeX in die Frage einbauen
                if "z" in teile_vec:
                    from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.mpp_shared import (
                        spaltenvektor_latex,
                    )
                    gegeben_latex = spaltenvektor_latex("z", teile_vec["z"])
                    frage_text = frage_text.replace(
                        var_spaltenvektor_latex("z", len(teile_vec["z"])),
                        gegeben_latex,
                    )
                if "m" in teile_vec:
                    from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.mpp_shared import (
                        spaltenvektor_latex,
                    )
                    gegeben_latex = spaltenvektor_latex("m", teile_vec["m"])
                    frage_text = frage_text.replace(
                        var_spaltenvektor_latex("m", len(teile_vec["m"])),
                        gegeben_latex,
                    )

                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=[frage_text],
                    antworten=[antwort],
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für Bestimmung Input erzeugen."
                )

        return tasks
