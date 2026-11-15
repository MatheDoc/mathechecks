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
# Zwei Ebenen:
# - Stimmungsfarbe (MARKE), gedämpft und nur in Flächen und Rändern: Schimmer im
#   Hintergrund, Karte, Schrittnummern, Schlussbild. Nie als Schrift- oder
#   Linienfarbe in der Rechnung. Sie ist in allen Gebieten dieselbe, damit die
#   Objektfarben in jedem Video dasselbe bedeuten.
# - Objektfarben, kräftig: Was zusammengehört, hat dieselbe Farbe (Tangente und
#   ihre Steigung, Hochpunkt im Graphen und in der Rechnung).
# Text, Überschriften und Rechnung bleiben weiß.
HINTERGRUND = "#0f0f14"
FLAECHE = "#16161e"    # Karte hinter der Bühne, unten
RAHMEN = "#2a2a36"
KARTE_TOENUNG = 0.2    # Anteil der Stimmungsfarbe am oberen Kartenrand
TEXT = "#f2f2f5"
TEXT_LEISE = "#a9a9b8"
GRAPH = "#e8e8ee"
ACHSE = "#8a8a9e"
MARKE = "#7c6aff"
HERVOR = "#f5a623"     # das Objekt, um das es gerade geht: Tangente, Kandidaten
ROSE = "#f76c6c"       # erstes Objekt eines Paares, z. B. Hochpunkt
BLAU = "#38bdf8"       # zweites Objekt eines Paares, z. B. Tiefpunkt; Himmelblau, damit es sich vom Violett absetzt
TUERKIS = "#3dd6c8"    # weitere Objekte
GRUEN = "#4ade80"
FELD = "#3b3b4d"       # Felder des Zahlenstrahls
FELD_LEISE = "#24242e"
TEXT_SCHWACH = "#62627a"

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

KOPF_Y = 6.6           # Logo und Titel
KARTE_OBEN = 5.95      # Karte, auf der die Bühne liegt
KARTE_UNTEN = 0.85     # bei voller Höhe; eine flache Bühne endet weiter oben
KARTE_INNENRAND = 0.3
BUEHNE_BREITE = 7.5
TAFEL_ABSTAND = 0.5    # zwischen Karte und Tafel (Rechnung und Text)
TAFEL_LAGE = 0.35      # Anteil des freien Platzes über dem Block; 0 = direkt unter der Karte, 0.5 = mittig
TAFEL_BREITE = 2 * KNOPF_X
