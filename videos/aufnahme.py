"""Eigene Stimme einsprechen: lokale Seite im Browser, Abschnitt für Abschnitt.

    videos\\.venv\\Scripts\\python videos\\aufnahme.py <szene.py>

Voraussetzung ist ein gerenderter Entwurf der Szene (render.py). Die Seite zeigt je Abschnitt den
stummen Videoausschnitt und den Sprechtext und nimmt dazu das Mikrofon auf. Die Aufnahmen landen als
MP3 unter videos/aufnahmen/<gebiet>/<lernbereich>/<nr>-<name>/ und werden von render.py automatisch verwendet.
"""
import argparse
import io
import json
import os
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from render import VIDEOS, ablage, check_aus_pfad

AUFNAHMEN = VIDEOS / "aufnahmen"
RATE = 44100
MAX_BYTES = 50_000_000


def verarbeite(roh: bytes, ziel: Path) -> float:
    """Schneidet Tastenanschlag und Stille ab, gleicht die Lautstärke an und speichert als MP3.

    Gibt die Länge in Sekunden zurück.
    """
    import av
    import numpy as np

    with av.open(io.BytesIO(roh)) as quelle:
        umsetzer = av.AudioResampler(format="flt", layout="mono", rate=RATE)
        teile = [neu.to_ndarray()[0] for bild in quelle.decode(audio=0) for neu in umsetzer.resample(bild)]
        teile += [neu.to_ndarray()[0] for neu in umsetzer.resample(None)]
    ton = np.concatenate(teile) if teile else np.zeros(0, dtype=np.float32)
    ton = ton[int(0.12 * RATE): len(ton) - int(0.2 * RATE)]  # Tastenanschlag am Anfang und am Ende

    fenster = int(0.02 * RATE)
    anzahl = len(ton) // fenster
    if anzahl < 10:
        raise ValueError("Die Aufnahme ist zu kurz.")
    pegel = np.sqrt((ton[: anzahl * fenster].reshape(anzahl, fenster) ** 2).mean(axis=1))
    if pegel.max() < 0.003:
        raise ValueError("Die Aufnahme ist still. Ist das richtige Mikrofon gewählt?")
    # Sprache ist, was mindestens drei Fenster (60 ms) lang laut bleibt; ein Knacken zählt nicht.
    laut = pegel > np.percentile(pegel, 95) * 10 ** (-30 / 20)
    anhaltend = np.flatnonzero(laut[:-2] & laut[1:-1] & laut[2:])
    if not len(anhaltend):
        raise ValueError("In der Aufnahme ist keine Sprache zu erkennen.")
    start = max(0, anhaltend[0] * fenster - int(0.15 * RATE))
    ende = min(len(ton), (anhaltend[-1] + 3) * fenster + int(0.25 * RATE))
    sprechpegel = pegel[anhaltend[0]: anhaltend[-1] + 3][laut[anhaltend[0]: anhaltend[-1] + 3]].mean()
    ton = ton[start:ende]

    # Gleiche Lautstärke in allen Abschnitten: Sprechpegel auf -20 dB, ohne zu übersteuern.
    ton = ton * min(0.1 / sprechpegel, 0.9 / np.abs(ton).max())

    ziel.parent.mkdir(parents=True, exist_ok=True)
    neu = ziel.with_name(ziel.name + ".neu")
    with av.open(str(neu), "w", format="mp3") as ausgabe:
        strom = ausgabe.add_stream("libmp3lame", rate=RATE, layout="mono")
        strom.bit_rate = 96_000
        bild = av.AudioFrame.from_ndarray((ton * 32767).astype(np.int16)[None, :], format="s16", layout="mono")
        bild.sample_rate = RATE
        passend = av.AudioResampler(format=strom.format, layout="mono", rate=RATE, frame_size=strom.frame_size or 1152)
        for stueck in [*passend.resample(bild), *passend.resample(None)]:
            ausgabe.mux(strom.encode(stueck))
        ausgabe.mux(strom.encode(None))
    for alt in ziel.parent.glob("*-" + ziel.name.rsplit("-", 1)[1]):  # frühere Aufnahme desselben Texts
        alt.unlink()
    neu.replace(ziel)
    return len(ton) / RATE


class Seite(BaseHTTPRequestHandler):
    szene: Path
    check: dict
    ordner: Path  # Aufnahmen dieses Checks
    rendert = threading.Lock()

    def log_message(self, *args: object) -> None:
        pass

    # ---------- Daten ----------
    def bericht(self) -> dict | None:
        datei = VIDEOS / "media" / "berichte" / f"{self.check['check_id']}.json"
        return json.loads(datei.read_text(encoding="utf-8")) | {"_datei": datei} if datei.exists() else None

    def aufnahme(self, abschnitt: dict) -> Path | None:
        """Vorhandene Aufnahme zum Sprechtext des Abschnitts; die Kennung am Ende des Namens entscheidet."""
        kennung = abschnitt["aufnahme"].rsplit("-", 1)[1]
        return next(self.ordner.glob("*-" + kennung), None)

    def daten(self) -> dict:
        from mutagen.mp3 import MP3

        titel = f"{self.check['Schlagwort']} ({self.check['LernbereichAnzeigename']}, Check {self.check['Nummer']})"
        bericht = self.bericht()
        if bericht is None or not bericht["abschnitte"] or "aufnahme" not in bericht["abschnitte"][0]:
            return {"titel": titel, "fehler": "Zu dieser Szene gibt es noch keinen aktuellen Entwurf."}
        abschnitte = bericht["abschnitte"]
        liste = []
        for i, abschnitt in enumerate(abschnitte):
            datei = self.aufnahme(abschnitt)
            liste.append({
                "text": abschnitt["sprechtext"],
                "beginn": abschnitt["beginn"],
                "ende": abschnitte[i + 1]["beginn"] if i + 1 < len(abschnitte) else bericht["sekunden"],
                "aufnahme": datei is not None,
                "dauer": round(MP3(datei).info.length, 1) if datei else None,
                "im_video": abschnitt["eigene_stimme"],
            })
        video = Path(bericht["video"])
        return {
            "titel": titel,
            "abschnitte": liste,
            "version": int(video.stat().st_mtime),
            "qualitaet": bericht["qualitaet"],
            "veraltet": self.szene.stat().st_mtime > bericht["_datei"].stat().st_mtime,
        }

    def rendere(self, final: bool) -> dict:
        befehl = [sys.executable, str(VIDEOS / "render.py"), str(self.szene), *(["--final"] if final else [])]
        with self.rendert:
            lauf = subprocess.run(
                befehl, capture_output=True, text=True, encoding="utf-8", errors="replace",
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            )
        zeilen = lauf.stdout.strip().splitlines()
        anfang = max((i for i, zeile in enumerate(zeilen) if zeile.startswith(self.check["check_id"])), default=None)
        if anfang is None:
            zeilen = (lauf.stdout + lauf.stderr).strip().splitlines()[-25:]
        else:
            zeilen = zeilen[anfang:]
        return {"ok": lauf.returncode == 0, "ausgabe": "\n".join(zeilen)}

    # ---------- Antworten ----------
    def sende_json(self, daten: dict, status: int = 200) -> None:
        inhalt = json.dumps(daten, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(inhalt)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(inhalt)

    def sende_datei(self, pfad: Path | None, typ: str) -> None:
        """Liefert eine Datei aus, auch in Teilen (Range), damit der Browser im Video springen kann."""
        if pfad is None or not pfad.exists():
            self.send_error(404)
            return
        groesse = pfad.stat().st_size
        start, ende = 0, groesse - 1
        bereich = self.headers.get("Range", "")
        if bereich.startswith("bytes="):
            von, _, bis = bereich[6:].partition("-")
            if von:
                start, ende = int(von), min(int(bis), ende) if bis else ende
            else:
                start = max(0, groesse - int(bis))
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{ende}/{groesse}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(ende - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            with pfad.open("rb") as datei:
                datei.seek(start)
                rest = ende - start + 1
                while rest > 0 and (stueck := datei.read(min(rest, 1 << 16))):
                    self.wfile.write(stueck)
                    rest -= len(stueck)
        except (BrokenPipeError, ConnectionError):
            pass  # der Browser bricht Teilabrufe ab, sobald er genug hat

    def abschnitt(self, pfad: str) -> dict | None:
        bericht = self.bericht()
        nummer = pfad.rsplit("/", 1)[1]
        if bericht and nummer.isdigit() and int(nummer) < len(bericht["abschnitte"]):
            return bericht["abschnitte"][int(nummer)]
        return None

    def do_GET(self) -> None:
        pfad = urlparse(self.path).path
        if pfad == "/":
            self.sende_datei(VIDEOS / "aufnahme.html", "text/html; charset=utf-8")
        elif pfad == "/daten":
            self.sende_json(self.daten())
        elif pfad == "/video":
            bericht = self.bericht()
            self.sende_datei(Path(bericht["video"]) if bericht else None, "video/mp4")
        elif pfad.startswith("/aufnahme/"):
            abschnitt = self.abschnitt(pfad)
            self.sende_datei(self.aufnahme(abschnitt) if abschnitt else None, "audio/mpeg")
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        pfad = urlparse(self.path).path
        laenge = int(self.headers.get("Content-Length", 0))
        if laenge > MAX_BYTES:
            self.sende_json({"fehler": "Die Aufnahme ist zu groß."}, 413)
            return
        inhalt = self.rfile.read(laenge)
        if pfad.startswith("/aufnahme/"):
            abschnitt = self.abschnitt(pfad)
            if abschnitt is None:
                self.sende_json({"fehler": "Diesen Abschnitt gibt es nicht."}, 404)
                return
            try:
                dauer = verarbeite(inhalt, self.ordner / abschnitt["aufnahme"])
            except Exception as fehler:  # noqa: BLE001 – die Seite soll jede Ursache anzeigen
                self.sende_json({"fehler": str(fehler) or type(fehler).__name__}, 400)
                return
            self.sende_json({"dauer": round(dauer, 1)})
        elif pfad == "/rendern":
            self.sende_json(self.rendere(final=json.loads(inhalt or b"{}").get("final", False)))
        else:
            self.send_error(404)


def main() -> int:
    parser = argparse.ArgumentParser(description="Eigene Stimme zu einem Check-Video einsprechen")
    parser.add_argument("szene", type=Path, help="Pfad zur Szenendatei")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--ohne-browser", action="store_true", help="Seite nicht automatisch öffnen")
    args = parser.parse_args()

    Seite.szene = args.szene.resolve()
    Seite.check = check_aus_pfad(Seite.szene)
    Seite.ordner = AUFNAHMEN / ablage(Seite.szene)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Seite)
    adresse = f"http://localhost:{args.port}/"
    print(f"Aufnahme für {Seite.check['check_id']}: {adresse}  (Beenden mit Strg+C)")
    if not args.ohne_browser:
        webbrowser.open(adresse)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
