"""Check 01 – E-Regel anwenden + Fehler-Wkt.

Kernidee: Die Entscheidungsregel teilt die Anzahlen in Annahme- und Ablehnungsbereich. Liegt das Ergebnis
im Ablehnungsbereich, wird H_0 verworfen. Fehler 1. Art: Ablehnungsbereich mit p_0; Fehler 2. Art:
Annahmebereich mit p_1.
Beispiel: Lootboxen wie im Warm-Up (n = 50, p_0 = 0,2, Regel „höchstens 5“, p_1 = 0,1) statt des
Versandhändlers im Musterbeispiel; linksseitig ausführlich, rechtsseitig nur kurz.
"""
from manim import BOLD, DOWN, LEFT, UP, Arrow, FadeOut, MathTex, Mobject, VGroup, Write

from mcvideo import Histogramm, MCSzene, auftritt, aufzaehlung, formel, reihe, tabelle, text, welle
from mcvideo.theme import BLAU, HERVOR, ROSE, TEXT_LEISE

G_FORMEL = 44
G_TEXT = 34


def bereich(name: str, menge: str, erklaerung: str, farbe: str) -> VGroup:
    """Zelle der Hypothesentabelle: Menge in ihrer Farbe, darunter ihr Name."""
    return VGroup(
        formel(name, "=", menge, groesse=G_FORMEL, farbe=farbe),
        text(erklaerung, groesse=24, farbe=TEXT_LEISE),
    ).arrange(DOWN, buff=0.15)


def hypothesen(zeichen: str, annahme: str, ablehnung: str) -> VGroup:
    """Hypothesen, darunter Annahme- und Ablehnungsbereich, wie in der Tabelle des Musterbeispiels."""
    return tabelle(
        (formel("H_0: p=0{,}2", groesse=G_FORMEL), formel(f"H_1: p{zeichen}0{{,}}2", groesse=G_FORMEL)),
        (
            bereich("A", annahme, "Annahmebereich", BLAU),
            bereich(r"\overline{A}", ablehnung, "Ablehnungsbereich", ROSE),
        ),
    )


def bcd(links: str, a: str, b: str, p: str, farbe: str) -> MathTex:
    """Wahrscheinlichkeit eines Bereichs als Taschenrechner-Eingabe; die Grenzen in der Farbe des Bereichs."""
    zeile = formel(links, "=Bcd(", a, ";", b, ";50;", p, ")", groesse=G_FORMEL)
    zeile[2].set_color(farbe)
    zeile[4].set_color(farbe)
    return zeile


def satz(*teile: str | MathTex) -> VGroup:
    """Textzeile, in der kleine Formeln auf der Schriftgrundlinie stehen."""
    return reihe(
        *[text(teil, groesse=G_TEXT) if isinstance(teil, str) else teil for teil in teile],
        abstand=0.18, grundlinie=True,
    )


def titel(inhalt: str) -> Mobject:
    return text(inhalt, groesse=40, gewicht=BOLD)


def fehlerfall(bereich_tex: str, p_tex: str) -> VGroup:
    """„Ergebnis in <Bereich>, aber <p> stimmt“; das Komma sitzt direkt am Bereich."""
    zeile = satz("Ergebnis in", formel(bereich_tex), ", aber", formel(p_tex), "stimmt")
    VGroup(*zeile[2:]).shift(0.14 * LEFT)
    return zeile


def punkt(stichwort: str, *zeilen: Mobject) -> VGroup:
    """Punkt der Kurzfassung: Stichwort in Grau, darunter der Inhalt."""
    return VGroup(text(stichwort, groesse=28, farbe=TEXT_LEISE), *zeilen).arrange(DOWN, buff=0.15, aligned_edge=LEFT)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.0)
        hist = self.auf_buehne(Histogramm(50, 0.2, bis=20, y_max=0.19, hoehe=2.9, p_tex="p_0=0{,}2"))
        self.add(karte)

        self.einstieg(
            "Wie entscheidest du bei", "einem Hypothesentest?",
            zusatz="(einseitig)",
            sprechtext="Wie entscheidest du bei einem Hypothesentest?",
            bild=hist.aufbau(),
        )

        # ---------- Sachzusammenhang ----------
        lage = self.tafel(
            text("Lootboxen", groesse=46, gewicht=BOLD),
            text("Hersteller: 20 % mit seltenem Item", groesse=G_TEXT),
            text("Vermutung: Anteil niedriger", groesse=G_TEXT),
            satz(formel("X", groesse=G_FORMEL), "zählt die seltenen Items in 50 Boxen."),
            abstand=0.45,
        )
        with self.sprich(
            "Ein Hersteller verspricht: In zwanzig Prozent der Lootboxen steckt ein seltenes Item. "
            "Die Community vermutet weniger. Ein Spieler testet fünfzig Boxen."
        ):
            self.play(auftritt(lage[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(auftritt(lage[1]), run_time=0.5)
            self.warte_bis(0.6)
            self.play(auftritt(lage[2]), run_time=0.5)
            self.warte_bis(0.8)
            self.play(auftritt(lage[3]), run_time=0.5)
        self.play(FadeOut(lage, shift=0.25 * UP), run_time=0.4)

        # ---------- Hypothesen und Regel ----------
        tabelle_links = self.oben_auf_tafel(hypothesen("<", r"\{6,\ldots,50\}", r"\{0,\ldots,5\}"))
        regel = self.tafel(
            text("„Höchstens 5 seltene Items:", groesse=G_TEXT, gewicht=BOLD, farben={"Höchstens 5": ROSE}),
            text("Anteil niedriger.“", groesse=G_TEXT, gewicht=BOLD),
            text("linksseitiger Test", groesse=G_TEXT, farbe=TEXT_LEISE),
            abstand=0.2, unter=tabelle_links,
        )
        regel[2].shift(0.3 * DOWN)
        with self.sprich("Nullhypothese: der versprochene Anteil. Gegenhypothese: die Vermutung."):
            self.play(auftritt(tabelle_links[0][0]), run_time=0.5)
            self.warte_bis(0.5)
            self.play(auftritt(tabelle_links[0][1]), run_time=0.5)
        with self.sprich(
            "Die Regel: Bei höchstens fünf seltenen Items gehen wir von einem niedrigeren Anteil aus. "
            "Null bis fünf ist der Ablehnungsbereich, ab sechs der Annahmebereich. "
            "Der Ablehnungsbereich liegt links: ein linksseitiger Test."
        ):
            self.play(auftritt(regel[:2]), run_time=0.6)
            self.warte_bis(0.4)
            self.play(hist.faerbe((0, 5, ROSE)), auftritt(tabelle_links[1][1]), run_time=0.7)
            self.warte_bis(0.6)
            self.play(hist.faerbe((0, 5, ROSE), (6, 50, BLAU)), auftritt(tabelle_links[1][0]), run_time=0.7)
            self.warte_bis(0.8)
            self.play(auftritt(regel[2]), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(regel, shift=0.25 * UP), run_time=0.4)

        # ---------- Entscheidung ----------
        zeiger = Arrow(hist.ort(4) + 1.1 * UP, hist.ort(4) + 0.1 * UP, color=HERVOR, buff=0, stroke_width=6)
        lage_4 = formel("4", r"\in", r"\overline{A}", groesse=G_FORMEL)
        lage_4[0].set_color(HERVOR)
        lage_4[2].set_color(ROSE)
        entscheidung = self.tafel(
            satz("Ergebnis:", formel("4", groesse=G_FORMEL, farbe=HERVOR), "seltene Items"),
            lage_4,
            satz(formel("H_0", groesse=G_FORMEL), "wird verworfen"),
            abstand=0.45, unter=tabelle_links,
        )
        with self.sprich(
            "Der Spieler findet bei dem Test nun vier seltene Items. Vier liegt im Ablehnungsbereich, "
            "also verwerfen wir die Nullhypothese."
        ):
            self.play(auftritt(entscheidung[0]), run_time=0.5)
            self.play(Write(zeiger), welle(hist.ort(4), HERVOR), run_time=0.6)
            self.warte_bis(0.45)
            self.play(Write(lage_4), run_time=0.7)
            self.warte_bis(0.75)
            self.play(auftritt(entscheidung[2]), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(entscheidung, shift=0.25 * UP), FadeOut(zeiger), run_time=0.4)

        # ---------- Fehler 1. Art ----------
        f1_rechnung = bcd(r"P(X\leq 5)", "0", "5", "0{,}2", ROSE)
        f1_ergebnis = formel(r"\approx 0{,}0480", groesse=G_FORMEL)
        fehler1 = self.tafel(
            titel("Fehler 1. Art"),
            satz(formel("H_0", groesse=G_FORMEL), "stimmt, wird aber verworfen"),
            f1_rechnung, f1_ergebnis,
            abstand=0.4, unter=tabelle_links,
        )
        with self.sprich(
            "Fehler erster Art: Die Nullhypothese stimmt, wird aber verworfen. "
            "Das Ergebnis liegt also im Ablehnungsbereich, obwohl p gleich null Komma zwei ist."
        ):
            self.play(auftritt(fehler1[0]), run_time=0.5)
            self.warte_bis(0.2)
            self.play(auftritt(fehler1[1]), run_time=0.5)
            self.warte_bis(0.6)
            self.play(hist.faerbe((0, 5, ROSE)), welle(tabelle_links[1][1], ROSE), run_time=0.7)
            self.warte_bis(0.8)
            self.play(Write(f1_rechnung), run_time=0.9)
            self.play(auftritt(f1_ergebnis), run_time=0.4)
        self.wait(0.6)
        self.play(FadeOut(fehler1, shift=0.25 * UP), run_time=0.4)

        # ---------- Fehler 2. Art ----------
        f2_rechnung = bcd(r"P(X\geq 6)", "6", "50", "0{,}1", BLAU)
        f2_ergebnis = formel(r"\approx 0{,}3839", groesse=G_FORMEL)
        fehler2 = self.tafel(
            titel("Fehler 2. Art"),
            satz("tatsächlich", formel("p_1=0{,}1", groesse=G_FORMEL)),
            satz(formel("H_0", groesse=G_FORMEL), "wird aber beibehalten"),
            f2_rechnung, f2_ergebnis,
            abstand=0.4, unter=tabelle_links,
        )
        with self.sprich(
            "Fehler zweiter Art: Der Anteil ist nun wirklich gesunken, und zwar auf zehn Prozent, "
            "wir bleiben aber bei der Nullhypothese. Das Ergebnis liegt also im Annahmebereich, obwohl p gleich null Komma eins ist."
        ):
            self.play(auftritt(fehler2[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(auftritt(fehler2[1]), hist.zu(0.1, "p_1=0{,}1"), run_time=1.0)
            self.warte_bis(0.45)
            self.play(
                auftritt(fehler2[2]), hist.faerbe((6, 50, BLAU)), welle(tabelle_links[1][0], BLAU), run_time=0.7,
            )
            self.warte_bis(0.8)
            self.play(Write(f2_rechnung), run_time=0.9)
            self.play(auftritt(f2_ergebnis), run_time=0.4)
        self.wait(0.6)
        self.play(FadeOut(fehler2, shift=0.25 * UP), FadeOut(tabelle_links, shift=0.25 * UP), run_time=0.4)

        # ---------- Rechtsseitig ----------
        tabelle_rechts = self.oben_auf_tafel(hypothesen(">", r"\{0,\ldots,15\}", r"\{16,\ldots,50\}"))
        f1_rechts = formel(r"P(X\geq 16)=Bcd(", "16", ";", "50", r";50;0{,}2)\approx 0{,}0308", groesse=G_FORMEL)
        f1_rechts[1].set_color(ROSE)
        f1_rechts[3].set_color(ROSE)
        rechts = self.tafel(
            text("„Mindestens 16 seltene Items:", groesse=G_TEXT, gewicht=BOLD, farben={"Mindestens 16": ROSE}),
            text("Anteil erhöht.“", groesse=G_TEXT, gewicht=BOLD),
            text("rechtsseitiger Test", groesse=G_TEXT, farbe=TEXT_LEISE),
            text("Fehler 1. Art:", groesse=G_TEXT),
            f1_rechts,
            abstand=0.2, unter=tabelle_rechts,
        )
        rechts[2:].shift(0.3 * DOWN)
        rechts[3:].shift(0.3 * DOWN)
        with self.sprich(
            "Vermutet man einen höheren Anteil, etwa mit der Regel mindestens sechzehn, "
            "liegt der Ablehnungsbereich rechts: ein rechtsseitiger Test. Gerechnet wird ähnlich."
        ):
            self.play(
                hist.zu(0.2, "p_0=0{,}2"), auftritt(tabelle_rechts[0]), auftritt(rechts[:2]), run_time=0.9,
            )
            self.warte_bis(0.4)
            self.play(hist.faerbe((0, 15, BLAU), (16, 50, ROSE)), auftritt(tabelle_rechts[1]), run_time=0.8)
            self.warte_bis(0.65)
            self.play(auftritt(rechts[2]), run_time=0.5)
            self.warte_bis(0.82)
            self.play(auftritt(rechts[3]), Write(f1_rechts), run_time=0.9)
        self.wait(0.6)
        self.play(FadeOut(rechts, shift=0.25 * UP), FadeOut(tabelle_rechts, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        punkte = aufzaehlung(
            punkt("Entscheidung", satz("Ergebnis im Ablehnungsbereich:"), satz(formel("H_0"), "verwerfen")),
            punkt("Fehler 1. Art", fehlerfall(r"\overline{A}", "p_0")),
            punkt("Fehler 2. Art", fehlerfall("A", "p_1")),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Liegt das Ergebnis im Ablehnungsbereich, wird die Nullhypothese verworfen, ansonsten beibehalten. "
            "Fehler erster Art: Ist die Wahrscheinlichkeit, dass das Ergebnis im Ablehnungsbereich liegt, obwohl p null stimmt. Fehler zweiter Art: Ist die Wahrscheinlichkeit, dass das Ergebnis im Annahmebereich liegt, obwohl p eins stimmt."
        ):
            self.play(hist.faerbe((0, 5, ROSE), (6, 50, BLAU)), auftritt(punkte[0]), run_time=0.6)
            self.warte_bis(0.3)
            self.play(hist.faerbe((0, 5, ROSE)), auftritt(punkte[1]), run_time=0.5)
            self.warte_bis(0.63)
            self.play(hist.faerbe((6, 50, BLAU)), auftritt(punkte[2]), run_time=0.5)
        self.wait(1.0)
