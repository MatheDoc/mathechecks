"""Check 03 – p oder n aus Fehler-Wkt bestimmen.

Kernidee: Die gegebene Fehlerwahrscheinlichkeit als Bcd mit der Unbekannten schreiben, gleichsetzen und probieren.
Fehler 1. Art: Ablehnungsbereich mit p_0; Fehler 2. Art: Annahmebereich mit p_1.
Beispiel: Lootboxen wie in Check 01 und 02 (n = 80, Regel „höchstens 9“, Fehler 1. Art 0,0287, gesucht p_0 = 0,2)
statt der Kronkorken im Musterbeispiel. Durchgerechnet wird nur p_0; n und der Fehler 2. Art nur als Hinweis.
"""
from manim import BOLD, DOWN, LEFT, UP, FadeOut, MathTex, Mobject, VGroup, Write

from mcvideo import Histogramm, MCSzene, auftritt, aufzaehlung, formel, reihe, text, welle
from mcvideo.theme import HERVOR, ROSE, TEXT_LEISE

G_FORMEL = 44
G_TEXT = 34


def satz(*teile: str | Mobject) -> VGroup:
    """Textzeile, in der kleine Formeln auf der Schriftgrundlinie stehen."""
    return reihe(
        *[text(teil, groesse=G_TEXT) if isinstance(teil, str) else teil for teil in teile],
        abstand=0.18, grundlinie=True,
    )


def eingabe(n: str, p: str, rechts: str, gesucht: int) -> MathTex:
    """Bcd(0;9;n;p) mit Ergebnis; die Grenzen in der Farbe des Ablehnungsbereichs, Teil gesucht orange."""
    zeile = formel("Bcd(", "0", ";", "9", ";", n, ";", p, ")", rechts, groesse=G_FORMEL)
    zeile[1].set_color(ROSE)
    zeile[3].set_color(ROSE)
    zeile[gesucht].set_color(HERVOR)
    return zeile


def punkt(stichwort: str, *zeilen: Mobject) -> VGroup:
    """Punkt der Kurzfassung: Stichwort in Grau, darunter der Inhalt."""
    return VGroup(text(stichwort, groesse=28, farbe=TEXT_LEISE), *zeilen).arrange(DOWN, buff=0.15, aligned_edge=LEFT)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.0)
        hist = self.auf_buehne(Histogramm(
            80, 0.15, bis=30, y_max=0.13, hoehe=2.9, zahlen=(0, 10, 20, 30), p_tex=r"p_0=\,?",
        ))
        self.add(karte)

        self.einstieg(
            "Wie findest du p oder n aus", "einer Fehlerwahrscheinlichkeit?",
            zusatz="(einseitiger Hypothesentest)",
            sprechtext="Wie findest du p oder n aus einer Fehlerwahrscheinlichkeit?",
            bild=hist.aufbau(),
        )

        # ---------- Sachzusammenhang ----------
        lage = self.tafel(
            text("Lootboxen: linksseitiger Test", groesse=42, gewicht=BOLD),
            text("Test mit 80 Boxen", groesse=G_TEXT),
            satz("höchstens 9 seltene Items:"),
            satz(formel("H_0", groesse=G_FORMEL), "verwerfen"),
            satz("Fehler 1. Art:", formel("0{,}0287", groesse=G_FORMEL)),
            satz("Welcher Anteil", formel("p_0", groesse=G_FORMEL, farbe=HERVOR), "wurde getestet?"),
            abstand=0.4,
        )
        mitte = lage[2:4].get_center()
        lage[2:4].arrange(DOWN, buff=0.15).move_to(mitte)
        lage[5].shift(0.3 * DOWN)
        with self.sprich(
            "Ein linksseitiger Test mit achtzig Lootboxen: Bei höchstens neun seltenen Items wird die "
            "Nullhypothese verworfen. Der Fehler erster Art hat die Wahrscheinlichkeit null Komma null zwei acht sieben. "
            "Welcher Anteil p null wurde getestet?"
        ):
            self.play(auftritt(lage[0]), auftritt(lage[1]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(auftritt(lage[2:4]), hist.faerbe((0, 9, ROSE)), run_time=0.7)
            self.warte_bis(0.5)
            self.play(auftritt(lage[4]), run_time=0.5)
            self.warte_bis(0.85)
            self.play(auftritt(lage[5]), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(lage, shift=0.25 * UP), run_time=0.4)

        # ---------- Ansatz ----------
        ablehnung = VGroup(
            formel(r"\overline{A}=\{0,\ldots,9\}", groesse=G_FORMEL, farbe=ROSE),
            text("Ablehnungsbereich", groesse=24, farbe=TEXT_LEISE),
        ).arrange(DOWN, buff=0.15)
        oben = self.oben_auf_tafel(ablehnung)
        gleichung = formel(r"P(X\leq 9)=", "Bcd(", "0", ";", "9", ";80;", "p_0", ")=0{,}0287", groesse=G_FORMEL)
        gleichung[2].set_color(ROSE)
        gleichung[4].set_color(ROSE)
        gleichung[6].set_color(HERVOR)
        ansatz = self.tafel(
            satz("Fehler 1. Art: Ablehnungsbereich mit", formel("p_0", groesse=G_FORMEL, farbe=HERVOR)),
            gleichung,
            abstand=0.45, unter=oben,
        )
        with self.sprich(
            "Fehler erster Art heißt: Ablehnungsbereich, gerechnet mit p null. "
            "Das setzen wir gleich null Komma null zwei acht sieben."
        ):
            self.play(auftritt(oben), welle(hist.ort(9), ROSE), run_time=0.6)
            self.warte_bis(0.15)
            self.play(auftritt(ansatz[0]), run_time=0.5)
            self.warte_bis(0.55)
            self.play(Write(gleichung), run_time=1.1)
        self.wait(0.4)

        # ---------- Probieren ----------
        versuche = [
            ("0{,}15", r"\approx 0{,}2211", 0.15),
            ("0{,}19", r"\approx 0{,}0459", 0.19),
            ("0{,}2", r"\approx 0{,}0287\ \checkmark", 0.2),
        ]
        zeilen = [eingabe("80", p, rechts, gesucht=7) for p, rechts, _ in versuche]
        ergebnis = formel("p_0=0{,}2", groesse=60, farbe=HERVOR)
        block = VGroup(gleichung.copy(), *zeilen, ergebnis)
        probieren = self.tafel(*block, abstand=0.4, unter=oben)
        ergebnis.shift(0.2 * DOWN)
        with self.sprich(
            "Jetzt probieren wir. Bei null Komma eins fünf ist der Ablehnungsbereich viel zu wahrscheinlich. "
            "Ein größeres p schiebt die Verteilung nach rechts. "
            "Bei null Komma eins neun noch etwas zu viel, bei null Komma zwei passt es genau."
        ):
            self.play(
                FadeOut(ansatz[0], shift=0.25 * UP), gleichung.animate.move_to(probieren[0]), run_time=0.6,
            )
            self.remove(gleichung)
            self.add(probieren[0])
            self.play(Write(zeilen[0]), hist.zu(0.15, "p_0=0{,}15"), run_time=0.9)
            for zeile, (_, _, p), beginn in zip(zeilen[1:], versuche[1:], (0.5, 0.75)):
                self.warte_bis(beginn)
                self.play(hist.zu(p, f"p_0={p:g}".replace(".", "{,}")), run_time=0.9)
                self.play(Write(zeile), run_time=0.8)
            self.play(auftritt(ergebnis), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(probieren, shift=0.25 * UP), run_time=0.4)

        # ---------- n gesucht ----------
        n_gleichung = eingabe("n", "0{,}2", "=0{,}0287", gesucht=5)
        hinweis = self.tafel(
            satz("Ist", formel("n", groesse=G_FORMEL, farbe=HERVOR), "gesucht:"),
            n_gleichung,
            satz(formel("n", groesse=G_FORMEL, farbe=HERVOR), "genauso probieren"),
            abstand=0.4, unter=oben,
        )
        with self.sprich("Ist stattdessen n gesucht, setzt du p ein und probierst n genauso durch."):
            self.play(auftritt(hinweis[0]), run_time=0.5)
            self.warte_bis(0.3)
            self.play(Write(n_gleichung), run_time=0.9)
            self.warte_bis(0.7)
            self.play(auftritt(hinweis[2]), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(hinweis, shift=0.25 * UP), FadeOut(oben, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        punkte = aufzaehlung(
            punkt("Fehler 1. Art", satz("Ablehnungsbereich mit", formel("p_0"))),
            punkt("Fehler 2. Art", satz("Annahmebereich mit", formel("p_1"))),
            punkt("dann", satz("gleichsetzen,", formel("p"), "oder", formel("n"), "probieren")),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Fehler erster Art heißt Ablehnungsbereich mit p null, "
            "Fehler zweiter Art Annahmebereich mit p eins. Dann gleichsetzen und p oder n probieren."
        ):
            self.play(auftritt(punkte[0]), run_time=0.5)
            self.warte_bis(0.4)
            self.play(auftritt(punkte[1]), run_time=0.5)
            self.warte_bis(0.75)
            self.play(auftritt(punkte[2]), run_time=0.5)
        self.wait(1.0)
