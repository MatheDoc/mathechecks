"""Rendert ein Check-Video und prüft Umfang und Bildränder.

    videos\\.venv\\Scripts\\python videos\\render.py <szene.py>            Entwurf mit Prüfbogen
    videos\\.venv\\Scripts\\python videos\\render.py <szene.py> --final    1080 x 1920 nach videos/ausgabe/

Die Szene liegt unter videos/checks/<gebiet>/<lernbereich>/<nr>-<name>.py,
gleich benannt wie das Musterbeispiel des Checks.
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


def schreibe_pruefbogen(check: dict, bericht: dict, fehler: list[str]) -> Path:
    """Standbild, Sprechtext und Untertitel je Abschnitt zum Durchsehen."""

    def zelle(inhalt: str | None) -> str:
        return (inhalt or "").replace("|", "\\|")

    zeilen = [
        f"# Prüfbogen: {check['Schlagwort']} (Check {check['Nummer']})",
        "",
        f"Ich kann {check['Ich kann']}",
        "",
        f"{bericht['sekunden']} s, {bericht['woerter']} Wörter, "
        + ("Ränder in Ordnung" if not fehler else "Fehler: " + "; ".join(fehler)),
        "",
        "| Zeit | Bild | Sprechtext | Untertitel, falls abweichend |",
        "|---|---|---|---|",
    ]
    for abschnitt in bericht["abschnitte"]:
        minuten, sekunden = divmod(int(abschnitt["beginn"]), 60)
        untertitel = abschnitt["untertitel"] if abschnitt["untertitel"] != abschnitt["sprechtext"] else None
        zeilen.append(
            f"| {minuten}:{sekunden:02d} | <img src=\"{abschnitt['bild']}\" width=\"220\"> "
            f"| {zelle(abschnitt['sprechtext'])} | {zelle(untertitel)} |"
        )
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

    umgebung = dict(os.environ, MC_CHECK_ID=check_id, MC_QUALITAET=qualitaet, PYTHONPATH=str(VIDEOS), PYTHONUTF8="1")
    if not args.final:
        umgebung["MC_STANDBILDER"] = "1"
    bericht_datei = VIDEOS / "media" / "berichte" / f"{check_id}.json"
    bericht_datei.unlink(missing_ok=True)

    befehl = [sys.executable, "-m", "manim", "render", "-v", "WARNING", "--progress_bar", "none", str(szene), "Video"]
    if subprocess.run(befehl, cwd=VIDEOS, env=umgebung).returncode != 0 or not bericht_datei.exists():
        print("Rendern fehlgeschlagen.")
        return 1

    bericht = json.loads(bericht_datei.read_text(encoding="utf-8"))
    video = Path(bericht["video"])
    fehler = list(bericht["verstoesse"])
    if bericht["sekunden"] > MAX_SEKUNDEN:
        fehler.append(f"Video ist länger als {MAX_SEKUNDEN} s.")

    print(f"\n{check_id} ({qualitaet})")
    print(f"  Dauer:   {bericht['sekunden']} s (Ziel {ZIEL_SEKUNDEN[0]}–{ZIEL_SEKUNDEN[1]} s)")
    print(f"  Wörter:  {bericht['woerter']} (Richtwert höchstens {MAX_WOERTER})")
    print(f"  Ränder:  {'in Ordnung' if not bericht['verstoesse'] else 'Objekte außerhalb des sichtbaren Bereichs'}")
    for zeile in fehler:
        print(f"    - {zeile}")
    if not args.final:
        print(f"  Video:   {video}")
        print(f"  Prüfen:  {schreibe_pruefbogen(check, bericht, fehler)}")

    if fehler:
        return 1
    if args.final:
        ziel = VIDEOS / "ausgabe"
        ziel.mkdir(exist_ok=True)
        shutil.copyfile(video, ziel / f"{check_id}.mp4")
        if video.with_suffix(".srt").exists():
            shutil.copyfile(video.with_suffix(".srt"), ziel / f"{check_id}.srt")
        print(f"  Video:   {ziel / (check_id + '.mp4')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
