"""Erzeugt das Frontmatter-Grundgeruest (Pruefungs-Index + Aufgabe-Stubs) fuer eine neue
Pruefung, rein aus einer YAML-Spezifikation - ohne KI-Einsatz. Die inhaltliche Transkription
(Aufgabenstellung, Erwartungshorizont, LaTeX-Formeln) bleibt bewusst als TODO im Fliesstext
stehen und muss danach separat (Chat oder API) ergaenzt werden.

Aufruf: python scaffold.py <spec.yaml>

Format von <spec.yaml>: siehe scaffold.example.yaml im selben Ordner.
"""
import pathlib
import sys

import yaml

MD_ROOT = pathlib.Path(__file__).resolve().parent.parent


def slug_aufgabe(aufgabe: str) -> str:
    return aufgabe.replace(".", "-")


def build_aufgabe_frontmatter(pruefung, a):
    fm = {
        "id": f"{pruefung['pruefung_id']}-a{slug_aufgabe(a['aufgabe'])}",
        "land": pruefung["land"],
        "schulform": pruefung["schulform"],
    }
    if pruefung.get("fachrichtung"):
        fm["fachrichtung"] = pruefung["fachrichtung"]
    fm.update(
        {
            "jahr": pruefung["jahr"],
            "termin": pruefung["termin"],
            "niveau": pruefung["niveau"],
        }
    )
    if pruefung.get("niveau_original"):
        fm["niveau_original"] = pruefung["niveau_original"]
    fm["fach"] = "mathematik"
    fm["aufgabe"] = a["aufgabe"]
    fm["hilfsmittel"] = a["hilfsmittel"]
    fm["themenbereich"] = a["themenbereich"]
    fm["punkte"] = a["punkte"]
    if a.get("teilaufgaben"):
        fm["teilaufgaben"] = a["teilaufgaben"]
    fm["erwartungshorizont"] = {"status": "keine"}
    quelle = {"aufgabe": a["quelle_aufgabe"]}
    if a.get("quelle_loesung"):
        quelle["loesung"] = a["quelle_loesung"]
    fm["quelle"] = quelle
    fm["enthaelt_grafik"] = bool(a.get("enthaelt_grafik", False))
    return fm


def build_aufgabe_body(pruefung, a):
    titel = a.get("titel", f"Aufgabe {a['aufgabe']}")
    return f"""# {titel} ({a['punkte']} Punkte)

<!-- STUB: Inhalt fehlt noch, per Chat/KI-Transkription oder manuell ergaenzen. -->

## Aufgabenstellung

TODO: Aufgabentext aus `{a['quelle_aufgabe']['datei']}` uebertragen.

## Erwartungshorizont

TODO: Erwartungshorizont aus{' `' + a['quelle_loesung']['datei'] + '`' if a.get('quelle_loesung') else ' der Loesungsquelle'} uebertragen,
danach `erwartungshorizont.status` im Frontmatter auf `vollstaendig`/`teilweise` setzen.
"""


def build_index_frontmatter(pruefung):
    fm = {
        "id": pruefung["pruefung_id"],
        "land": pruefung["land"],
        "schulform": pruefung["schulform"],
    }
    if pruefung.get("fachrichtung"):
        fm["fachrichtung"] = pruefung["fachrichtung"]
    fm.update(
        {
            "jahr": pruefung["jahr"],
            "termin": pruefung["termin"],
            "niveau": pruefung["niveau"],
        }
    )
    if pruefung.get("niveau_original"):
        fm["niveau_original"] = pruefung["niveau_original"]
    fm["fach"] = "mathematik"
    hilfsmittel = sorted({a["hilfsmittel"] for a in pruefung["aufgaben"]})
    fm["hilfsmittel"] = hilfsmittel
    fm["gesamtpunkte"] = pruefung["gesamtpunkte"]
    if pruefung.get("bearbeitungszeit_minuten"):
        fm["bearbeitungszeit_minuten"] = pruefung["bearbeitungszeit_minuten"]
    fm["quelle"] = pruefung["quelle"]
    fm["aufgaben"] = [
        {"id": f"{pruefung['pruefung_id']}-a{slug_aufgabe(a['aufgabe'])}", "datei": f"a{slug_aufgabe(a['aufgabe'])}.md"}
        for a in pruefung["aufgaben"]
    ]
    return fm


def build_index_body(pruefung):
    titel = pruefung.get("titel", pruefung["pruefung_id"])
    aufbau = pruefung.get("aufbau_markdown", "TODO: Aufbau der Pruefung (Teile, Punkteverteilung, Auswahlregeln) ergaenzen.")
    rows = "\n".join(
        f"| [a{slug_aufgabe(a['aufgabe'])}.md](a{slug_aufgabe(a['aufgabe'])}.md) | {a['aufgabe']} | {a['themenbereich']} | {a['hilfsmittel']} | {a['punkte']} |"
        for a in pruefung["aufgaben"]
    )
    return f"""# {titel}

<!-- STUB: automatisch generiertes Grundgeruest, Inhalt der Aufgaben-Dateien noch nicht transkribiert. -->

## Aufbau der Pruefung

{aufbau}

## Aufgaben

| Datei | Aufgabe | Themenbereich | Hilfsmittel | Punkte |
|---|---|---|---|---|
{rows}

## Bekannte Luecken dieser Konvertierung

TODO: nach der inhaltlichen Transkription ergaenzen (Boilerplate-Ausschluesse, beschnittene Grafiken, Sonderfaelle).
"""


def dump_frontmatter(fm: dict) -> str:
    return "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n"


def main(spec_path: str):
    spec = yaml.safe_load(pathlib.Path(spec_path).read_text(encoding="utf-8"))

    pruefung_id = f"{spec['land']}-{spec['ordner_slug']}-{spec['jahr']}-{spec['termin']}-{spec['niveau']}"
    spec["pruefung_id"] = pruefung_id

    gesamtpunkte = spec.get("gesamtpunkte")
    if gesamtpunkte is None:
        gesamtpunkte = sum(a["punkte"] for a in spec["aufgaben"])
    spec["gesamtpunkte"] = gesamtpunkte

    ziel = MD_ROOT / spec["land"] / spec["ordner_slug"] / spec["niveau"] / pruefung_id
    (ziel / "_assets").mkdir(parents=True, exist_ok=True)

    index_text = dump_frontmatter(build_index_frontmatter(spec)) + build_index_body(spec)
    (ziel / "_index.md").write_text(index_text, encoding="utf-8")
    print("erzeugt:", ziel / "_index.md")

    for a in spec["aufgaben"]:
        fm = build_aufgabe_frontmatter(spec, a)
        body = build_aufgabe_body(spec, a)
        path = ziel / f"a{slug_aufgabe(a['aufgabe'])}.md"
        path.write_text(dump_frontmatter(fm) + body, encoding="utf-8")
        print("erzeugt:", path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Aufruf: python scaffold.py <spec.yaml>")
        sys.exit(1)
    main(sys.argv[1])
