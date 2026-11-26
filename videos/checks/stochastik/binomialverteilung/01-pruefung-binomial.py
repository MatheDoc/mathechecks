"""Check 01 – Eigenschaften Binomialverteilung.

Kernidee: X ist binomialverteilt, wenn X die Treffer zählt und drei Bedingungen gelten: n fest, pro Versuch
zwei Ausgänge, p konstant. Ist eine verletzt, ist X nicht binomialverteilt.
Beispiel: die vier Situationen des Musterbeispiels (Lose mit und ohne Zurücklegen, Passwort, Würfel),
die Lose ohne Zurücklegen mit konkreten Zahlen (2 Gewinne unter 5 Losen); beim Würfel zusätzlich
„wie oft eine 6“ als binomialverteilter Gegenfall.
"""
from manim import BOLD, DOWN, LEFT, UP, FadeIn, FadeOut, Mobject, VGroup, Write

from mcvideo import MCSzene, Versuche, auftritt, aufzaehlung, formel, reihe, text, wortlaut
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE, TUERKIS

G_TEXT = 38
G_FORMEL = 52

BEDINGUNGEN = ("n fest", "zwei Ausgänge", "p konstant")


def bedingung(inhalt: str, erfuellt: bool) -> VGroup:
    """Eine Bedingung mit Haken (erfüllt) oder Kreuz in Orange (verletzt)."""
    zeichen = formel(r"\checkmark" if erfuellt else r"\times", groesse=G_FORMEL, farbe=TEXT_LEISE if erfuellt else HERVOR)
    wort = text(inhalt, groesse=G_TEXT, farbe=TEXT if erfuellt else HERVOR)
    return reihe(zeichen, wort, abstand=0.3)


def urteil(ja: bool) -> Mobject:
    return text("binomialverteilt" if ja else "nicht binomialverteilt", groesse=44, gewicht=BOLD)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.5)
        self.add(karte)
        zuege = self.auf_buehne(Versuche(10, titel="Zug"))

        self.einstieg(
            "Wann ist eine Zufallsgröße", "binomialverteilt?",
            bild=zuege.aufbau(),
        )

        # ---------- Idee: drei Bedingungen ----------
        liste = VGroup(*[bedingung(b, True) for b in BEDINGUNGEN]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        block = self.tafel(
            wortlaut("10-mal ein Los ziehen,", "mit Zurücklegen", signal=("mit Zurücklegen",), groesse=40),
            reihe(formel("X", groesse=G_FORMEL), text("zählt die Gewinne.", groesse=G_TEXT), abstand=0.25),
            liste,
            urteil(True),
            abstand=0.55,
        )
        with self.sprich(
            "Wir ziehen zehnmal ein Los mit Zurücklegen, X zählt die Gewinne. Drei Fragen: "
            "Steht die Anzahl der Versuche fest? Gibt es pro Versuch nur Treffer oder Niete? "
            "Ist p konstant, bleibt die Trefferwahrscheinlichkeit also gleich? "
            "Dreimal ja, also ist X binomialverteilt."
        ):
            self.play(auftritt(block[0]), run_time=0.5)
            self.play(auftritt(block[1]), zuege.markiere(2, 5, 9), run_time=0.7)
            for zeile, beginn in zip(liste, (0.22, 0.4, 0.58)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.4)
            self.warte_bis(0.86)
            self.play(auftritt(block[3]), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(zuege), run_time=0.4)

        # ---------- Ohne Zurücklegen ----------
        box = self.auf_buehne(Versuche(5, titel="Lose in der Box"))
        vorher = formel(r"P(\text{Gewinn})=\frac{2}{5}", groesse=G_FORMEL)
        nachher = formel(r"\text{danach: }\frac{1}{4}", groesse=G_FORMEL)
        block = self.tafel(
            wortlaut("3 Lose ziehen,", "ohne Zurücklegen", signal=("ohne Zurücklegen",), groesse=40),
            reihe(vorher, nachher, abstand=0.6),
            bedingung("p konstant", False),
            urteil(False),
            abstand=0.55,
        )
        with self.sprich(
            "Ohne Zurücklegen ändert sich die Box: Erst sind zwei von fünf Losen Gewinne, "
            "nach einem Gewinn nur noch eins von vier. p ist nicht konstant. "
            "Genauso, wenn jemand mit der Zeit müde wird."
        ):
            self.play(FadeIn(box), auftritt(block[0]), run_time=0.6)
            self.play(box.markiere(1, 2), run_time=0.5)
            self.warte_bis(0.15)
            self.play(Write(vorher), run_time=0.7)
            self.warte_bis(0.4)
            self.play(FadeOut(VGroup(box.felder[0], box.zahlen[0])), Write(nachher), run_time=0.8)
            self.warte_bis(0.6)
            self.play(auftritt(block[2]), auftritt(block[3]), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(box), run_time=0.4)

        # ---------- Keine feste Anzahl ----------
        offen = formel("n=", "\\,?", groesse=110)
        offen[1].set_color(HERVOR)
        self.auf_buehne(offen)
        block = self.tafel(
            wortlaut("Passwort eingeben,", "bis es stimmt", signal=("bis",), groesse=40),
            bedingung("n fest", False),
            urteil(False),
            abstand=0.55,
        )
        with self.sprich("Ein Passwort eingeben, bis es stimmt: Die Anzahl der Versuche steht nicht fest."):
            self.play(auftritt(block[0]), run_time=0.5)
            self.warte_bis(0.45)
            self.play(FadeIn(offen, scale=0.8), auftritt(block[1]), auftritt(block[2]), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(offen), run_time=0.4)

        # ---------- Würfel: was wird gezählt? ----------
        augen = self.auf_buehne(Versuche(6, titel="Augenzahl"))
        summe = VGroup(
            wortlaut("Augensumme", groesse=40),
            bedingung("zwei Ausgänge", False),
        ).arrange(DOWN, buff=0.4)
        sechsen = VGroup(
            wortlaut("Wie oft eine 6?", groesse=40),
            reihe(text("Treffer: 6", groesse=G_TEXT, farben={"6": TUERKIS}), text("Niete: keine 6", groesse=G_TEXT), abstand=0.6),
            urteil(True),
        ).arrange(DOWN, buff=0.4)
        block = self.tafel(text("3-mal würfeln", groesse=44, gewicht=BOLD), summe, sechsen, abstand=0.7)
        with self.sprich(
            "Dreimal würfeln und die Augensumme bilden: Jede Augenzahl zählt, das sind sechs Ausgänge. "
            "Zählst du nur die Sechsen, sind es wieder zwei: Sechs oder keine Sechs. Das ist binomialverteilt."
        ):
            self.play(FadeIn(augen), auftritt(block[0]), run_time=0.6)
            self.play(auftritt(summe[0]), augen.markiere(1, 2, 3, 4, 5, 6, farbe=HERVOR), run_time=0.7)
            self.warte_bis(0.3)
            self.play(auftritt(summe[1]), run_time=0.4)
            self.warte_bis(0.5)
            self.play(auftritt(sechsen[0]), augen.markiere(6), run_time=0.7)
            self.play(auftritt(sechsen[1]), run_time=0.5)
            self.warte_bis(0.82)
            self.play(auftritt(sechsen[2]), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        punkte = aufzaehlung(*[text(b, groesse=46) for b in BEDINGUNGEN], abstand=0.55)
        schluss = text("alle drei: binomialverteilt", groesse=42, gewicht=BOLD)
        self.tafel(punkte, schluss, abstand=0.8)
        with self.sprich("Kurz gesagt: n fest, zwei Ausgänge, p konstant. Nur wenn alle drei passen, ist X binomialverteilt."):
            for zeile, beginn in zip((*punkte, schluss), (0.1, 0.25, 0.42, 0.62)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
            self.play(augen.neutral(), run_time=0.5)
