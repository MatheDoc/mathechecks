"""Check 06 – Einfache Extrempunkte.

Kernidee: Am Hoch- und Tiefpunkt liegt die Tangente waagrecht, deshalb f'(x) = 0.
Beispiel: f(x) = x^3 - 3x + 1, unverändert aus dem Musterbeispiel des Checks.
"""
import numpy as np
from manim import (
    BOLD,
    DOWN,
    RIGHT,
    SEMIBOLD,
    UP,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Line,
    ValueTracker,
    Write,
    always_redraw,
)

from mcvideo import (
    Dezimalzahl,
    MCSzene,
    auftritt,
    formel,
    kurzfassung,
    reihe,
    schritt,
    text,
    welle,
    zeichnen,
)
from mcvideo.theme import BLAU, GRAPH, HERVOR, ROSE, S_FORMEL, S_GROSS, S_KLEIN, TEXT_LEISE


def f(x: float) -> float:
    return x**3 - 3 * x + 1


def f1(x: float) -> float:
    return 3 * x**2 - 3


class Video(MCSzene):
    def inhalt(self) -> None:
        # Nur -1 und 1 beschriften: Der Graph läuft sonst durch die Achsenzahl -2.
        achsen = self.achsen(x=(-2.5, 2.5, 1), y=(-2, 4, 1), x_zahlen=(-1, 1))
        graph = achsen.plot(f, x_range=[-2.1, 2.1], color=GRAPH, stroke_width=6)
        ort_h, ort_t = achsen.c2p(-1, 3), achsen.c2p(1, -1)
        self.add(self.buehne(), achsen)

        self.einstieg(
            "Wie bestimmst du", "Hoch- und Tiefpunkte?",
            bild=zeichnen(graph),
            kopf=self.kopf(r"f(x)=x^3-3x+1"),
        )

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
            text("Tangente waagrecht", groesse=48, gewicht=BOLD, farben={"Tangente": HERVOR}),
            reihe(text("Steigung:"), formel("f'(x)="), steigung),
        )

        with self.sprich(
            "Die Idee: Am Hochpunkt und am Tiefpunkt liegt die Tangente waagrecht. "
            "Ihre Steigung, also die erste Ableitung, ist dort null."
        ):
            self.play(FadeIn(linie), FadeIn(punkt), auftritt(idee), run_time=0.5)
            self.play(stelle.animate.set_value(-1), run_time=2.2)
            self.play(welle(ort_h, HERVOR), run_time=0.8)
            self.play(stelle.animate.set_value(1), run_time=2.8)
            self.play(welle(ort_t, HERVOR), run_time=0.8)
        steigung.clear_updaters()
        self.play(FadeOut(idee, shift=0.25 * UP), FadeOut(linie), FadeOut(punkt), run_time=0.4)

        # ---------- Schritt 1 ----------
        kopf1 = schritt(1, "Notwendige Bedingung")
        ableitung = formel(r"f'(x)=3x^2-3")
        gleichung = formel(r"3x^2-3=0")
        vereinfacht = formel(r"x^2-1=0")
        kandidaten = reihe(formel("x=-1", farbe=HERVOR), text("oder"), formel("x=1", farbe=HERVOR))
        hinweis = text("Kandidaten für Extremstellen", groesse=S_KLEIN, farbe=TEXT_LEISE)
        block1 = self.tafel(kopf1, ableitung, gleichung, vereinfacht, kandidaten, hinweis)
        marken = {x: self.senkrechte(achsen, x) for x in (-1, 1)}

        with self.sprich("Schritt eins: die notwendige Bedingung. Wir bilden die erste Ableitung"):
            self.play(auftritt(kopf1), run_time=0.5)
            self.warte_bis(0.55)
            self.play(Write(ableitung), run_time=1.2)
        with self.sprich("und setzen sie gleich null."):
            self.play(Write(gleichung), run_time=1)
        with self.sprich("Durch drei geteilt bleibt: x Quadrat minus eins gleich null."):
            self.warte_bis(0.35)
            self.play(Write(vereinfacht), run_time=1)
        with self.sprich("Also x gleich minus eins oder x gleich eins. Das sind unsere Kandidaten."):
            self.play(Write(kandidaten), run_time=1.2)
            self.play(Create(marken[-1]), Create(marken[1]), run_time=0.8)
            self.warte_bis(0.65)
            self.play(auftritt(hinweis), run_time=0.4)
        self.play(FadeOut(block1, shift=0.25 * UP), run_time=0.4)

        # ---------- Schritt 2 ----------
        kopf2 = schritt(2, "Hinreichende Bedingung")
        zweite = formel(r"f''(x)=6x")
        hoch = reihe(formel(r"f''(-1)=-6<0"), formel(r"\Rightarrow"), text("Hochpunkt", farbe=ROSE, gewicht=SEMIBOLD))
        tief = reihe(formel(r"f''(1)=6>0"), formel(r"\Rightarrow"), text("Tiefpunkt", farbe=BLAU, gewicht=SEMIBOLD))
        block2 = self.tafel(kopf2, zweite, hoch, tief, abstand=0.5)

        with self.sprich(
            "Schritt zwei: die hinreichende Bedingung. Hoch oder tief? Das verrät die zweite Ableitung."
        ):
            self.play(auftritt(kopf2), run_time=0.5)
            self.warte_bis(0.6)
            self.play(Write(zweite), run_time=1.2)
        with self.sprich("Bei minus eins ist sie negativ: Hochpunkt."):
            self.play(Write(hoch[0]), run_time=1.2)
            self.warte_bis(0.65)
            self.play(FadeIn(hoch[1:], shift=0.2 * RIGHT), marken[-1].animate.set_color(ROSE), run_time=0.6)
        with self.sprich("Bei eins ist sie positiv: Tiefpunkt."):
            self.play(Write(tief[0]), run_time=1.2)
            self.warte_bis(0.65)
            self.play(FadeIn(tief[1:], shift=0.2 * RIGHT), marken[1].animate.set_color(BLAU), run_time=0.6)
        self.play(FadeOut(block2, shift=0.25 * UP), run_time=0.4)

        # ---------- Schritt 3 ----------
        kopf3 = schritt(3, "y-Werte berechnen")
        einsetzen_h = formel(r"f(-1)=(-1)^3-3\cdot(-1)+1")
        wert_h = formel(r"=-1+3+1=", r"3")
        wert_h[1].set_color(ROSE)
        einsetzen_t = formel(r"f(1)=1^3-3\cdot 1+1")
        wert_t = formel(r"=1-3+1=", r"-1")
        wert_t[1].set_color(BLAU)
        block3 = self.tafel(kopf3, einsetzen_h, wert_h, einsetzen_t, wert_t)
        punkt_h = Dot(ort_h, color=ROSE, radius=0.13)
        punkt_t = Dot(ort_t, color=BLAU, radius=0.13)

        with self.sprich("Schritt drei: Fehlen noch die y-Werte. Minus eins in f eingesetzt ergibt drei."):
            self.play(auftritt(kopf3), run_time=0.5)
            self.warte_bis(0.4)
            self.play(Write(einsetzen_h), run_time=1.3)
            self.play(Write(wert_h), run_time=1)
            self.play(GrowFromCenter(punkt_h), welle(ort_h, ROSE), run_time=0.6)
        with self.sprich("Und f von eins ergibt minus eins."):
            self.play(Write(einsetzen_t), run_time=1.1)
            self.play(Write(wert_t), run_time=0.9)
            self.play(GrowFromCenter(punkt_t), welle(ort_t, BLAU), run_time=0.6)
        self.play(FadeOut(block3, shift=0.25 * UP), FadeOut(marken[-1]), FadeOut(marken[1]), run_time=0.4)

        # ---------- Ergebnis ----------
        ergebnis = self.tafel(
            formel(r"H(-1\mid 3)", groesse=S_GROSS, farbe=ROSE),
            formel(r"T(1\mid -1)", groesse=S_GROSS, farbe=BLAU),
            abstand=0.5,
        )
        name_h = formel("H", groesse=40, farbe=ROSE).next_to(punkt_h, UP, buff=0.15)
        name_t = formel("T", groesse=40, farbe=BLAU).next_to(punkt_t, DOWN, buff=0.15)

        with self.sprich("Fertig! Hochpunkt bei minus eins, drei. Tiefpunkt bei eins, minus eins."):
            self.warte_bis(0.12)
            self.play(auftritt(ergebnis[0]), FadeIn(name_h), welle(ort_h, ROSE), run_time=0.7)
            self.warte_bis(0.58)
            self.play(auftritt(ergebnis[1]), FadeIn(name_t), welle(ort_t, BLAU), run_time=0.7)
        self.play(FadeOut(ergebnis, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        liste = kurzfassung(
            reihe(formel(r"f'(x)=0"), text("lösen")),
            reihe(formel(r"f''(x)"), text("prüfen")),
            reihe(formel(r"y=f(x)"), text("berechnen")),
        )
        self.tafel(liste)

        with self.sprich("Kurz gesagt: Erste Ableitung null setzen, mit der zweiten prüfen, y-Wert berechnen."):
            for zeile, beginn in zip(liste, (0.15, 0.45, 0.75)):
                self.warte_bis(beginn)
                self.play(FadeIn(zeile, shift=0.3 * RIGHT), run_time=0.5)
