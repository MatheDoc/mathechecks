"""Gestaltungsstandards für MatheChecks-Videos im Hochformat (9:16).

Farben und Schrift folgen den Design-Tokens der Website (assets/css/shared.css).
"""
import os
from pathlib import Path

import manimpango
from manim import config

VIDEOS = Path(__file__).resolve().parent.parent
REPO = VIDEOS.parent

# ---------- Bild ----------
BREITE = 9.0
HOEHE = 16.0
QUALITAETEN = {
    "entwurf": (540, 960, 15),
    "final": (1080, 1920, 30),
}
QUALITAET = os.environ.get("MC_QUALITAET", "entwurf")

config.pixel_width, config.pixel_height, config.frame_rate = QUALITAETEN[QUALITAET]
config.frame_width = BREITE
config.frame_height = HOEHE
config.media_dir = str(VIDEOS / "media")

# ---------- Farben ----------
HINTERGRUND = "#0f0f14"
TEXT = "#f2f2f5"
TEXT_LEISE = "#a9a9b8"
MARKE = "#7c6aff"      # Markenfarbe: Schrittnummern, Logo-Umfeld
AKZENT = "#a78bfa"     # hellere Markenfarbe für Schrift
HERVOR = "#f5a623"     # „schau hierhin“: Tangente, Kandidaten, Stolperstein
ROSE = "#f76c6c"       # erstes Objekt eines Paares (z. B. Hochpunkt)
BLAU = "#4c9aff"       # zweites Objekt eines Paares (z. B. Tiefpunkt)
TUERKIS = "#3dd6c8"
GRUEN = "#4ade80"      # nur für das Check-Häkchen
GRAPH = "#e8e8ee"
ACHSE = "#8a8a9e"

# ---------- Schrift ----------
SCHRIFT = "Inter"
for _datei in sorted((Path(__file__).parent / "fonts").glob("*.ttf")):
    manimpango.register_font(str(_datei))

S_GROSS = 60
S_FORMEL = 46
S_TITEL = 42
S_SCHRITT = 36
S_TEXT = 32
S_KLEIN = 26

# ---------- Aufteilung ----------
# Sichtbarer Bereich: die Shorts-Oberfläche überdeckt den unteren Rand (Kanal,
# Titel) und rechts unten die Bedienleiste. Richtwerte, am Handy gegenprüfen.
RAND_LINKS = -4.1
RAND_RECHTS = 4.1
RAND_OBEN = 7.0
RAND_UNTEN = -5.0
KNOPF_X = 3.3          # rechts davon liegt unterhalb von KNOPF_Y die Bedienleiste
KNOPF_Y = -0.5

KOPF_Y = 6.45          # Logo und Titel
BUEHNE_MITTE_Y = 3.3   # Graph, Diagramm, Skizze
BUEHNE_BREITE = 8.0
BUEHNE_HOEHE = 4.8
TAFEL_OBEN = 0.35      # Rechnung und Text
TAFEL_BREITE = 2 * KNOPF_X
TAFEL_HOEHE = TAFEL_OBEN - RAND_UNTEN
