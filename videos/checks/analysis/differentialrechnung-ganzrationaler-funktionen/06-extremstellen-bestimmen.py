"""Check 06 – Einfache Extrempunkte.

Kernidee: Am Hoch- und Tiefpunkt liegt die Tangente waagrecht, deshalb f'(x) = 0.
Beispiel: f(x) = x^3 - 3x + 1, unverändert aus dem Musterbeispiel des Checks.
"""
import numpy as np
from manim import (
    BOLD,
    DOWN,
    RIGHT,
    UP,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Indicate,
    Line,
    ValueTracker,
    VGroup,
    Write,
    always_redraw,
)

from mcvideo import Dezimalzahl, MCSzene, formel, rezept, schritt, stolperstein, text, ueberschrift
from mcvideo.theme import BLAU, GRAPH, HERVOR, ROSE, S_FORMEL, S_GROSS, S_TEXT, TEXT_LEISE


def f(x: float) -> float:
    return x**3 - 3 * x + 1


def f1(x: float) -> float:
    return 3 * x**2 - 3


class Video(MCSzene):
    kompetenz = "Ich kann Extrempunkte bestimmen."
    schlusssatz = "Extrempunkte bestimmen? Check!"

    def inhalt(self) -> None:
        # Nur -1 und 1 beschriften: Der Graph läuft sonst durch die Achsenzahl -2.
        achsen = self.achsen(x=(-2.5, 2.5, 1), y=(-2, 4, 1), x_zahlen=(-1, 1))
        graph = achsen.plot(f, x_range=[-2.1, 2.1], color=GRAPH, stroke_width=6)
        self.add(achsen, self.kopf(r"f(x)=x^3-3x+1"))

        # ---------- Frage ----------
        frage = self.tafel(
            text("Ein Hügel, ein Tal.", groesse=S_GROSS, gewicht=BOLD),
            text("Wo genau?", groesse=S_GROSS, farbe=HERVOR, gewicht=BOLD),
        )
        with self.sprich("Ein Hügel und ein Tal. Aber wo genau liegen Hochpunkt und Tiefpunkt?"):
            self.play(Create(graph), FadeIn(frage[0], shift=0.2 * UP), run_time=1.6)
            self.play(FadeIn(frage[1], shift=0.2 * UP), run_time=0.6)
        self.play(FadeOut(frage), run_time=0.4)

        # ---------- Idee: waagrechte Tangente ----------
        stelle = ValueTracker(-1.9)

        def tangente() -> Line:
            x0 = stelle.get_value()
            ort = achsen.c2p(x0, f(x0))
            richtung = achsen.c2p(x0 + 1, f(x0) + f1(x0)) - ort
            richtung = richtung / np.linalg.norm(richtung)
            return Line(ort - 1.1 * richtung, ort + 1.1 * richtung, color=HERVOR, stroke_width=5)

        linie = always_redraw(tangente)
        punkt = always_redraw(lambda: Dot(achsen.c2p(stelle.get_value(), f(stelle.get_value())), color=HERVOR, radius=0.11))
        steigung = Dezimalzahl(f1(stelle.get_value()), font_size=S_FORMEL, color=HERVOR)
        steigung.add_updater(lambda zahl: zahl.set_value(f1(stelle.get_value())))
        idee = self.tafel(
            text("Am Hoch- und Tiefpunkt:", farbe=TEXT_LEISE),
            text("Tangente waagrecht", groesse=48, gewicht=BOLD),
            VGroup(text("Steigung der Tangente:"), steigung).arrange(RIGHT, buff=0.3),
        )

        with self.sprich(
            "Schau auf die Tangente: Am Hochpunkt und am Tiefpunkt liegt sie waagrecht. "
            "Ihre Steigung ist dort null."
        ):
            self.play(FadeIn(linie), FadeIn(punkt), FadeIn(idee), run_time=0.6)
            self.play(stelle.animate.set_value(-1), run_time=2)
            self.wait(0.7)
            self.play(stelle.animate.set_value(1), run_time=2.4)
            self.wait(0.7)
        steigung.clear_updaters()
        self.play(FadeOut(idee), FadeOut(linie), FadeOut(punkt), run_time=0.4)

        # ---------- Schritt 1 ----------
        kopf1 = schritt(1, "Notwendige Bedingung")
        ableitung = formel(r"f'(x)=3x^2-3")
        gleichung = formel(r"3x^2-3=0")
        vereinfacht = formel(r"x^2-1=0")
        kandidaten = formel(r"x=-1", r"\ \text{oder}\ ", r"x=1")
        kandidaten[0].set_color(HERVOR)
        kandidaten[2].set_color(HERVOR)
        warnung = stolperstein("Das sind erst Kandidaten!")
        block1 = self.tafel(kopf1, ableitung, gleichung, vereinfacht, kandidaten, warnung)
        marken = {x: self.senkrechte(achsen, x) for x in (-1, 1)}

        with self.sprich(
            "Schritt eins: die notwendige Bedingung. Wir bilden die erste Ableitung.",
            untertitel="Schritt 1: die notwendige Bedingung. Wir bilden die erste Ableitung.",
        ):
            self.play(FadeIn(kopf1, shift=0.2 * UP), run_time=0.5)
            self.wait(2.3)
            self.play(Write(ableitung), run_time=1.2)
        with self.sprich("Die setzen wir gleich null."):
            self.play(Write(gleichung), run_time=1)
        with self.sprich(
            "Geteilt durch drei bleibt: x Quadrat minus eins gleich null.",
            untertitel="Geteilt durch 3 bleibt: x² − 1 = 0.",
        ):
            self.wait(1.5)
            self.play(Write(vereinfacht), run_time=1)
        with self.sprich(
            "Also x gleich minus eins oder x gleich eins.",
            untertitel="Also x = −1 oder x = 1.",
        ):
            self.play(Write(kandidaten), run_time=1.2)
            self.play(Create(marken[-1]), Create(marken[1]), run_time=0.8)
        with self.sprich(
            "Stolperstein: Das sind erst Kandidaten. "
            "Ob dort wirklich ein Hoch- oder Tiefpunkt liegt, zeigt Schritt zwei.",
            untertitel="Stolperstein: Das sind erst Kandidaten. "
                       "Ob dort wirklich ein Hoch- oder Tiefpunkt liegt, zeigt Schritt 2.",
        ):
            self.play(FadeIn(warnung, shift=0.2 * UP), run_time=0.5)
        self.play(FadeOut(block1), run_time=0.4)

        # ---------- Schritt 2 ----------
        kopf2 = schritt(2, "Hinreichende Bedingung")
        zweite = formel(r"f''(x)=6x")
        hoch = formel(r"f''(-1)=-6<0", r"\ \Rightarrow\ ", r"\text{Hochpunkt}")
        hoch[2].set_color(ROSE)
        tief = formel(r"f''(1)=6>0", r"\ \Rightarrow\ ", r"\text{Tiefpunkt}")
        tief[2].set_color(BLAU)
        block2 = self.tafel(kopf2, zweite, hoch, tief, abstand=0.5)

        with self.sprich(
            "Schritt zwei: die hinreichende Bedingung. Die zweite Ableitung entscheidet.",
            untertitel="Schritt 2: die hinreichende Bedingung. Die zweite Ableitung entscheidet.",
        ):
            self.play(FadeIn(kopf2, shift=0.2 * UP), run_time=0.5)
            self.wait(2.3)
            self.play(Write(zweite), run_time=1.2)
        with self.sprich(
            "Bei minus eins ist sie negativ. Also Hochpunkt.",
            untertitel="Bei x = −1 ist sie negativ. Also Hochpunkt.",
        ):
            self.play(Write(hoch[0]), run_time=1.2)
            self.wait(1)
            self.play(Write(hoch[1:]), marken[-1].animate.set_color(ROSE), run_time=0.8)
        with self.sprich(
            "Bei eins ist sie positiv. Also Tiefpunkt.",
            untertitel="Bei x = 1 ist sie positiv. Also Tiefpunkt.",
        ):
            self.play(Write(tief[0]), run_time=1.2)
            self.wait(0.8)
            self.play(Write(tief[1:]), marken[1].animate.set_color(BLAU), run_time=0.8)
        self.play(FadeOut(block2), run_time=0.4)

        # ---------- Schritt 3 ----------
        kopf3 = schritt(3, "y-Werte berechnen")
        einsetzen_h = formel(r"f(-1)=(-1)^3-3\cdot(-1)+1")
        wert_h = formel(r"=-1+3+1=", r"3")
        wert_h[1].set_color(ROSE)
        einsetzen_t = formel(r"f(1)=1^3-3\cdot 1+1")
        wert_t = formel(r"=1-3+1=", r"-1")
        wert_t[1].set_color(BLAU)
        block3 = self.tafel(kopf3, einsetzen_h, wert_h, einsetzen_t, wert_t)
        punkt_h = Dot(achsen.c2p(-1, 3), color=ROSE, radius=0.13)
        punkt_t = Dot(achsen.c2p(1, -1), color=BLAU, radius=0.13)

        with self.sprich(
            "Schritt drei: die y-Werte. Wir setzen minus eins in f ein und erhalten drei.",
            untertitel="Schritt 3: die y-Werte. Wir setzen −1 in f ein und erhalten 3.",
        ):
            self.play(FadeIn(kopf3, shift=0.2 * UP), run_time=0.5)
            self.wait(2)
            self.play(Write(einsetzen_h), run_time=1.3)
            self.play(Write(wert_h), run_time=1)
            self.play(GrowFromCenter(punkt_h), run_time=0.4)
        with self.sprich(
            "Und f von eins ergibt minus eins.",
            untertitel="Und f(1) ergibt −1.",
        ):
            self.play(Write(einsetzen_t), run_time=1.1)
            self.play(Write(wert_t), run_time=0.9)
            self.play(GrowFromCenter(punkt_t), run_time=0.4)
        self.play(FadeOut(block3), FadeOut(marken[-1]), FadeOut(marken[1]), run_time=0.4)

        # ---------- Ergebnis ----------
        ergebnis_h = formel(r"H(-1\mid 3)", groesse=S_GROSS, farbe=ROSE)
        ergebnis_t = formel(r"T(1\mid -1)", groesse=S_GROSS, farbe=BLAU)
        block4 = self.tafel(ueberschrift("Ergebnis"), ergebnis_h, ergebnis_t, abstand=0.55)
        name_h = formel("H", groesse=40, farbe=ROSE).next_to(punkt_h, UP, buff=0.15)
        name_t = formel("T", groesse=40, farbe=BLAU).next_to(punkt_t, DOWN, buff=0.15)

        with self.sprich(
            "Das Ergebnis: Der Hochpunkt liegt bei minus eins, drei. Der Tiefpunkt bei eins, minus eins.",
            untertitel="Das Ergebnis: Hochpunkt H(−1 | 3), Tiefpunkt T(1 | −1).",
        ):
            self.play(FadeIn(block4[0], shift=0.2 * UP), run_time=0.5)
            self.wait(1)
            self.play(Write(ergebnis_h), FadeIn(name_h), Indicate(punkt_h, color=ROSE, scale_factor=1.6), run_time=1.2)
            self.wait(2.5)
            self.play(Write(ergebnis_t), FadeIn(name_t), Indicate(punkt_t, color=BLAU, scale_factor=1.6), run_time=1.2)
        self.play(FadeOut(block4), run_time=0.4)

        # ---------- Rezept ----------
        liste = rezept(
            formel(r"f'(x)=0\ \text{lösen}", groesse=42),
            formel(r"f''(x)\ \text{prüfen}", groesse=42),
            formel(r"y=f(x)\ \text{berechnen}", groesse=42),
        )
        block5 = self.tafel(ueberschrift("Dein Rezept"), liste, abstand=0.55)

        with self.sprich(
            "Dein Rezept: Erste Ableitung null setzen. Mit der zweiten Ableitung prüfen. y-Wert berechnen."
        ):
            self.play(FadeIn(block5[0], shift=0.2 * UP), run_time=0.5)
            for zeile, pause in zip(liste, (0.7, 1.6, 1.8)):
                self.wait(pause)
                self.play(FadeIn(zeile, shift=0.3 * RIGHT), run_time=0.6)
