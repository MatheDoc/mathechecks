"""Check 03 – p oder n aus Fehler-Wkt bestimmen.

Kernidee: Die Intervallwahrscheinlichkeit mit der Unbekannten notieren, mit der gegebenen Fehlerwahrscheinlichkeit
gleichsetzen und die Unbekannte durch Probieren bestimmen.
Beispiel: Lootboxen wie in Check 01 und 02 (n = 80, Regel „höchstens 9“, Fehler 1. Art 0,0287, gesucht p_0 = 0,2)
statt der Kronkorken im Musterbeispiel. Durchgerechnet wird nur p_0 (Probieren nur im Histogramm, nur der Treffer
als Rechnung); n nur als kurzer Hinweis, der Fehler 2. Art fehlt.
"""
from manim import BOLD, DOWN, LEFT, UP, FadeOut, MathTex, Mobject, VGroup, Write

from mcvideo import Histogramm, MCSzene, auftritt, formel, kurzfassung, reihe, text, welle
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
        frage_p0 = formel("p_0", "?", groesse=G_FORMEL)
        frage_p0[0].set_color(HERVOR)
        nullhypothese = formel("H_0:", r"\ p=", "p_0", groesse=G_FORMEL)
        nullhypothese[2].set_color(HERVOR)
        ablehnung_kurz = formel(r"\{0,\ldots,9\}", groesse=G_FORMEL, farbe=ROSE)
        lage = self.tafel(
            text("Lootboxen", groesse=46, gewicht=BOLD),
            VGroup(
                nullhypothese,
                text("Wahrscheinlichkeit für ein seltenes Item", groesse=24, farbe=TEXT_LEISE),
            ).arrange(DOWN, buff=0.15),
            text("bekannt:", groesse=28, farbe=TEXT_LEISE),
            satz("Fehler 1. Art:", formel("0{,}0287", groesse=G_FORMEL)),
            satz("Stichprobenumfang:", formel("n=80", groesse=G_FORMEL)),
            satz("Ablehnungsbereich:", ablehnung_kurz),
            satz("Wie groß ist", frage_p0),
            abstand=0.35,
        )
        lage[2:].shift(0.2 * DOWN)
        lage[6].shift(0.3 * DOWN)
        with self.sprich(
            "Die Nullhypothese eines Tests besagt, dass Lootboxen in einem Computerspiel mit einer "
            "Wahrscheinlichkeit von p null ein seltenes Item enthalten. "
            "Bekannt ist der Fehler erster Art, der Stichprobenumfang und der Ablehnungsbereich. "
            "Wie groß ist p null?"
        ):
            self.play(auftritt(lage[0]), run_time=0.5)
            self.warte_bis(0.1)
            self.play(auftritt(lage[1]), run_time=0.6)
            self.warte_bis(0.55)
            self.play(auftritt(lage[2]), run_time=0.4)
            self.warte_bis(0.62)
            self.play(auftritt(lage[3]), run_time=0.5)
            self.warte_bis(0.72)
            self.play(auftritt(lage[4]), run_time=0.5)
            self.warte_bis(0.8)
            self.play(auftritt(lage[5]), hist.faerbe((0, 9, ROSE)), run_time=0.7)
            self.warte_bis(0.9)
            self.play(auftritt(lage[6]), run_time=0.5)
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
        erklaerung = VGroup(
            satz("Fehler 1. Art:", formel("X", groesse=G_FORMEL), "im Ablehnungsbereich,"),
            satz("obwohl", formel("p_0", groesse=G_FORMEL, farbe=HERVOR), "zutrifft"),
        ).arrange(DOWN, buff=0.15)
        ansatz = self.tafel(erklaerung, gleichung, abstand=0.5, unter=oben)
        with self.sprich(
            "Der Fehler erster Art ist die Wahrscheinlichkeit, dass X im Ablehnungsbereich liegt, "
            "obwohl p null zutrifft. Diese Wahrscheinlichkeit setzen wir gleich null Komma null zwei acht sieben."
        ):
            self.play(auftritt(oben), welle(hist.ort(9), ROSE), run_time=0.6)
            self.warte_bis(0.1)
            self.play(auftritt(erklaerung[0]), run_time=0.5)
            self.warte_bis(0.4)
            self.play(auftritt(erklaerung[1]), run_time=0.5)
            self.warte_bis(0.6)
            self.play(Write(gleichung), run_time=1.1)
        self.wait(0.4)

        # ---------- Probieren ----------
        treffer = eingabe("80", "0{,}2", r"\approx 0{,}0287\ \checkmark", gesucht=7)
        ergebnis = formel("p_0=0{,}2", groesse=60, farbe=HERVOR)
        probieren = self.tafel(gleichung.copy(), treffer, ergebnis, abstand=0.5, unter=oben)
        ergebnis.shift(0.2 * DOWN)
        with self.sprich(
            "Jetzt probieren wir verschiedene Werte für p null aus, bis die Wahrscheinlichkeit passt. "
            "Bei null Komma zwei stimmt sie genau."
        ):
            self.play(
                FadeOut(ansatz[0], shift=0.25 * UP), gleichung.animate.move_to(probieren[0]), run_time=0.6,
            )
            self.remove(gleichung)
            self.add(probieren[0])
            for p, beginn in ((0.15, 0.15), (0.17, 0.3), (0.19, 0.45), (0.2, 0.62)):
                self.warte_bis(beginn)
                self.play(hist.zu(p, f"p_0={p:g}".replace(".", "{,}")), run_time=0.7)
            self.warte_bis(0.75)
            self.play(Write(treffer), run_time=0.9)
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
        def p_oder_n(*davor: str, danach: str) -> VGroup:
            return satz(
                *davor, formel("p", groesse=G_FORMEL, farbe=HERVOR), "oder",
                formel("n", groesse=G_FORMEL, farbe=HERVOR), danach,
            )

        schritte = kurzfassung(
            VGroup(text("Intervallwahrscheinlichkeit mit", groesse=G_TEXT), p_oder_n("unbekanntem", danach="notieren"))
            .arrange(DOWN, buff=0.15, aligned_edge=LEFT),
            VGroup(text("mit gegebener Fehler-", groesse=G_TEXT), text("wahrscheinlichkeit gleichsetzen", groesse=G_TEXT))
            .arrange(DOWN, buff=0.15, aligned_edge=LEFT),
            p_oder_n(danach="durch Probieren bestimmen"),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Die Intervallwahrscheinlichkeit mit unbekanntem p oder n notieren, "
            "mit der gegebenen Fehlerwahrscheinlichkeit gleichsetzen und dann p oder n durch Probieren bestimmen."
        ):
            self.play(auftritt(schritte[0]), run_time=0.5)
            self.warte_bis(0.45)
            self.play(auftritt(schritte[1]), run_time=0.5)
            self.warte_bis(0.75)
            self.play(auftritt(schritte[2]), run_time=0.5)
        self.wait(1.0)
