"""Rendert ein Check-Video und prüft Umfang und Bildränder.

    videos\\.venv\\Scripts\\python videos\\render.py <szene.py>            Entwurf mit Prüfbogen
    videos\\.venv\\Scripts\\python videos\\render.py <szene.py> --final    1080 x 1920 nach videos/ausgabe/

Die Szene liegt unter videos/checks/<gebiet>/<lernbereich>/<nr>-<name>.py,
gleich benannt wie das Musterbeispiel des Checks. Die eigenen Aufnahmen liegen unter demselben
Teilpfad in videos/aufnahmen/. Das fertige Video heißt wie sein YouTube-Titel:
videos/ausgabe/<gebiet>/<lernbereich>/<NN> <Schlagwort> <Lernbereichsname>.mp4.

Gibt es zum Check eigene Aufnahmen (videos/aufnahme.py), werden sie verwendet; Abschnitte ohne
passende Aufnahme spricht die Entwurfsstimme. Ein finales Video entsteht nur mit einer Stimme.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

VIDEOS = Path(__file__).resolve().parent
REPO = VIDEOS.parent

MAX_WOERTER = 200
ZIEL_SEKUNDEN = (60, 90)
MAX_SEKUNDEN = 180  # Obergrenze für Shorts
MAX_TITEL = 100     # Zeichen eines YouTube-Titels
VERBOTENE_ZEICHEN = '<>:"/\\|?*'  # in Windows-Dateinamen nicht erlaubt


def check_aus_pfad(szene: Path) -> dict:
    try:
        gebiet, lernbereich, datei = szene.relative_to(VIDEOS / "checks").parts
    except ValueError:
        sys.exit(f"Die Szene muss unter videos/checks/<gebiet>/<lernbereich>/ liegen: {szene}")
    check_id = f"{gebiet}__{lernbereich}__{datei[:2]}"
    checks = json.loads((REPO / "_data" / "checks.json").read_text(encoding="utf-8"))
    for check in checks:
        if check["check_id"] == check_id:
            return check
    sys.exit(f"Kein Check mit der ID {check_id} in _data/checks.json.")


def ablage(szene: Path) -> Path:
    """Teilpfad <gebiet>/<lernbereich>/<nr>-<name>, unter dem die Aufnahmen des Checks liegen."""
    return szene.relative_to(VIDEOS / "checks").with_suffix("")


def videoname(check: dict) -> str:
    """Dateiname des fertigen Videos ohne Endung. YouTube übernimmt ihn beim Hochladen als Titel."""
    name = f"{check['Nummer']:02d} {check['Schlagwort']} {check['LernbereichAnzeigename']}"
    unzulaessig = sorted({zeichen for zeichen in name if zeichen in VERBOTENE_ZEICHEN or ord(zeichen) < 32})
    if unzulaessig:
        sys.exit(
            f"„{name}“ taugt nicht als Dateiname und YouTube-Titel: unzulässige Zeichen {' '.join(unzulaessig)}. "
            "Bitte Schlagwort oder Lernbereichsname in _data/checks.json anpassen."
        )
    if name != name.strip() or name.endswith(".") or len(name) > MAX_TITEL:
        sys.exit(
            f"„{name}“ taugt nicht als Dateiname und YouTube-Titel: höchstens {MAX_TITEL} Zeichen, "
            "kein Leerzeichen am Rand, kein Punkt am Ende."
        )
    return name


def schreibe_pruefbogen(check: dict, bericht: dict, fehler: list[str]) -> Path:
    """Standbild und Sprechtext je Abschnitt zum Durchsehen."""

    zeilen = [
        f"# Prüfbogen: {check['Schlagwort']} (Check {check['Nummer']})",
        "",
        f"Ich kann {check['Ich kann']}",
        "",
        f"{bericht['sekunden']} s, {bericht['woerter']} Wörter, "
        + ("Ränder in Ordnung" if not fehler else "Fehler: " + "; ".join(fehler)),
        "",
        "| Zeit | Bild | Sprechtext |",
        "|---|---|---|",
    ]
    for abschnitt in bericht["abschnitte"]:
        minuten, sekunden = divmod(int(abschnitt["beginn"]), 60)
        sprechtext = abschnitt["sprechtext"].replace("|", "\\|")
        zeilen.append(f"| {minuten}:{sekunden:02d} | <img src=\"{abschnitt['bild']}\" width=\"220\"> | {sprechtext} |")
    datei = VIDEOS / "media" / "pruefung" / check["check_id"] / "pruefbogen.md"
    datei.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    return datei


def main() -> int:
    parser = argparse.ArgumentParser(description="Check-Video rendern")
    parser.add_argument("szene", type=Path, help="Pfad zur Szenendatei")
    parser.add_argument("--final", action="store_true", help="in voller Auflösung nach videos/ausgabe/ rendern")
    args = parser.parse_args()

    szene = args.szene.resolve()
    check = check_aus_pfad(szene)
    check_id = check["check_id"]
    qualitaet = "final" if args.final else "entwurf"
    if args.final:
        ziel = VIDEOS / "ausgabe" / ablage(szene).parent / (videoname(check) + ".mp4")

    umgebung = dict(
        os.environ, MC_CHECK_ID=check_id, MC_ABLAGE=ablage(szene).as_posix(), MC_QUALITAET=qualitaet,
        PYTHONPATH=str(VIDEOS), PYTHONUTF8="1",
    )
    if not args.final:
        umgebung["MC_STANDBILDER"] = "1"
    bericht_datei = VIDEOS / "media" / "berichte" / f"{check_id}.json"
    bericht_datei.unlink(missing_ok=True)

    # manim-voiceover lädt beim Start das Paket sox, das ohne installiertes SoX bei jedem Lauf warnt.
    # SoX wird nur für ein verändertes Sprechtempo gebraucht, deshalb bleibt die Warnung stumm.
    start = "import logging; logging.getLogger('sox').disabled = True; from manim.__main__ import main; main()"
    befehl = [sys.executable, "-c", start, "render", "-v", "WARNING", "--progress_bar", "none", str(szene), "Video"]
    if subprocess.run(befehl, cwd=VIDEOS, env=umgebung).returncode != 0 or not bericht_datei.exists():
        print("Rendern fehlgeschlagen.")
        return 1

    bericht = json.loads(bericht_datei.read_text(encoding="utf-8"))
    video = Path(bericht["video"])
    fehler = list(bericht["verstoesse"])
    if bericht["sekunden"] > MAX_SEKUNDEN:
        fehler.append(f"Video ist länger als {MAX_SEKUNDEN} s.")
    eigene = [abschnitt["eigene_stimme"] for abschnitt in bericht["abschnitte"]]
    if any(eigene) and not all(eigene):
        fehlend = ", ".join(str(nr) for nr, eigen in enumerate(eigene, start=1) if not eigen)
        stimme = f"eigene Aufnahmen für {sum(eigene)} von {len(eigene)} Abschnitten; Entwurfsstimme in Abschnitt {fehlend}"
        if args.final:
            fehler.append("Aufnahmen unvollständig: Entwurfsstimme in Abschnitt " + fehlend)
    else:
        stimme = "eigene Aufnahmen" if all(eigene) else "Entwurfsstimme"

    print(f"\n{check_id} ({qualitaet})")
    print(f"  Dauer:   {bericht['sekunden']} s (Ziel {ZIEL_SEKUNDEN[0]}–{ZIEL_SEKUNDEN[1]} s)")
    print(f"  Wörter:  {bericht['woerter']} (Richtwert höchstens {MAX_WOERTER})")
    print(f"  Stimme:  {stimme}")
    print(f"  Ränder:  {'in Ordnung' if not bericht['verstoesse'] else 'Objekte außerhalb des sichtbaren Bereichs'}")
    for zeile in fehler:
        print(f"    - {zeile}")
    if not args.final:
        print(f"  Video:   {video}")
        print(f"  Prüfen:  {schreibe_pruefbogen(check, bericht, fehler)}")

    if fehler:
        return 1
    if args.final:
        ziel.parent.mkdir(parents=True, exist_ok=True)
        for alt in ziel.parent.glob(f"{check['Nummer']:02d} *.mp4"):
            if alt != ziel:
                alt.unlink()  # Video desselben Checks unter früherem Schlagwort
        shutil.copyfile(video, ziel)
        print(f"  Video:   {ziel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
