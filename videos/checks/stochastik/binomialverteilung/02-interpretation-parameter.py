"""Check 02 – Bernoulli-Parameter.

Kernidee: In der Bernoulli-Formel stehen Anzahlen (n, k, n − k) und Wahrscheinlichkeiten für einen Versuch
(p, 1 − p); das Ergebnis ist die Wahrscheinlichkeit für genau k Treffer. Der Exponent verbindet jede
Wahrscheinlichkeit mit ihrer Anzahl.
Beispiel: Pakete wie im Musterbeispiel, binom(8,2) · 0,1² · 0,9⁶ = 0,1488 (28 · 0,01 · 0,531441 = 0,14880).
"""
from manim import BOLD, DOWN, UP, FadeOut, VGroup, Write

from mcvideo import MCSzene, Versuche, auftritt, aufzaehlung, formel, legende, reihe, text, welle
from mcvideo.theme import BLAU, HERVOR, TEXT_LEISE

G_FORMEL = 60
G_TEXT = 40

# Teile der Formel auf der Bühne
BINOM, P, K, Q, NK, ERG = 0, 2, 3, 5, 6, 8


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.0)
        self.add(karte)
        bernoulli = formel(
            r"\binom{8}{2}", r"\cdot", "0{,}1", "^{2}", r"\cdot", "0{,}9", "^{6}", "=", "0{,}1488", groesse=96,
        )
        pakete = Versuche(8, titel="Paket")
        self.f = bernoulli
        self.pakete = pakete
        self.auf_buehne(VGroup(bernoulli, pakete).arrange(DOWN, buff=0.55))
        binom = bernoulli[BINOM]
        acht, zwei = binom[1], binom[2]  # Glyphen in \binom{8}{2}: Klammer, 8, 2, Klammer

        self.einstieg(
            "Was bedeuten die Zahlen", "in der Bernoulli-Formel?",
            bild=[Write(bernoulli), *pakete.aufbau()],
        )

        # ---------- Sachzusammenhang ----------
        lage = self.tafel(
            text("Pakete", groesse=46, gewicht=BOLD),
            text("Ein kleiner Teil kommt zu spät.", groesse=G_TEXT),
            abstand=0.4,
        )
        with self.sprich("Ein kleiner Teil der Pakete wird zu spät geliefert. Jemand rechnet so."):
            self.play(auftritt(lage[0]), run_time=0.5)
            self.warte_bis(0.3)
            self.play(auftritt(lage[1]), run_time=0.5)
        self.play(FadeOut(lage, shift=0.25 * UP), run_time=0.4)

        # ---------- Anzahlen ----------
        anzahlen = legende(
            (formel("8", groesse=G_FORMEL), text("alle Pakete", groesse=G_TEXT)),
            (formel("2", groesse=G_FORMEL, farbe=HERVOR), text("Pakete zu spät", groesse=G_TEXT)),
            (formel("6", groesse=G_FORMEL, farbe=BLAU), text("Pakete pünktlich", groesse=G_TEXT)),
        )
        block = self.tafel(text("Anzahlen", groesse=G_TEXT, farbe=TEXT_LEISE), anzahlen, abstand=0.5)
        with self.sprich(
            "8 ist die Anzahl aller Pakete. 2 Pakete kommen zu spät, die übrigen 6 pünktlich."
        ):
            self.play(auftritt(block[0]), auftritt(anzahlen[0]), welle(acht, HERVOR), run_time=0.6)
            self.warte_bis(0.35)
            self.play(
                auftritt(anzahlen[1]), zwei.animate.set_color(HERVOR), bernoulli[K].animate.set_color(HERVOR),
                pakete.markiere(3, 7, farbe=HERVOR), run_time=0.7,
            )
            self.warte_bis(0.7)
            self.play(auftritt(anzahlen[2]), bernoulli[NK].animate.set_color(BLAU), run_time=0.6)
        self.wait(0.5)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Wahrscheinlichkeiten ----------
        wkt = legende(
            (formel("0{,}1", groesse=G_FORMEL, farbe=HERVOR), text("ein Paket zu spät", groesse=G_TEXT)),
            (formel("0{,}9", groesse=G_FORMEL, farbe=BLAU), text("ein Paket pünktlich", groesse=G_TEXT)),
        )
        block = self.tafel(text("Wahrscheinlichkeiten", groesse=G_TEXT, farbe=TEXT_LEISE), wkt, abstand=0.5)
        with self.sprich(
            "0,1 hat den Exponenten 2, gehört also zu den verspäteten Paketen: "
            "Das ist die Wahrscheinlichkeit, dass ein Paket zu spät kommt. "
            "0,9 ist die Wahrscheinlichkeit, dass ein Paket pünktlich kommt."
        ):
            self.play(auftritt(block[0]), run_time=0.4)
            self.play(bernoulli[P].animate.set_color(HERVOR), welle(bernoulli[K], HERVOR), run_time=0.6)
            self.warte_bis(0.35)
            self.play(auftritt(wkt[0]), run_time=0.5)
            self.warte_bis(0.72)
            self.play(auftritt(wkt[1]), bernoulli[Q].animate.set_color(BLAU), run_time=0.6)
        self.wait(0.5)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Binomialkoeffizient ----------
        koeff = formel(r"\binom{8}{2}=28", groesse=G_FORMEL)
        block = self.tafel(
            koeff,
            text("Möglichkeiten, welche 2 der 8", groesse=G_TEXT),
            text("Pakete zu spät kommen", groesse=G_TEXT),
            abstand=0.3,
        )
        block[0].shift(0.2 * UP)
        with self.sprich(
            "8 über 2 zählt die Möglichkeiten, welche 2 der 8 Pakete zu spät kommen: "
            "das erste und das zweite, das erste und das dritte, und so weiter. "
            "Das sind 28 Möglichkeiten."
        ):
            self.play(welle(binom, HERVOR), Write(koeff), run_time=0.8)
            self.play(auftritt(block[1:]), run_time=0.5)
            self.warte_bis(0.42)
            self.play(pakete.markiere(1, 2, farbe=HERVOR), run_time=0.5)
            self.warte_bis(0.58)
            self.play(pakete.markiere(1, 3, farbe=HERVOR), run_time=0.5)
            self.warte_bis(0.72)
            self.play(pakete.markiere(5, 8, farbe=HERVOR), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Ergebnis ----------
        block = self.tafel(
            formel("0{,}1488", groesse=G_FORMEL),
            text("Wahrscheinlichkeit, dass genau 2", groesse=G_TEXT, farben={"genau 2": HERVOR}),
            text("von 8 Paketen zu spät kommen", groesse=G_TEXT),
            abstand=0.3,
        )
        block[0].shift(0.2 * UP)
        with self.sprich(
            "Das Ergebnis ist die Wahrscheinlichkeit, dass genau 2 von 8 Paketen zu spät kommen."
        ):
            self.play(welle(bernoulli[ERG], HERVOR), Write(block[0]), pakete.markiere(3, 7, farbe=HERVOR), run_time=0.8)
            self.warte_bis(0.4)
            self.play(auftritt(block[1:]), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        punkte = aufzaehlung(
            (text("Anzahlen", groesse=G_TEXT, farbe=TEXT_LEISE),
             reihe(formel("n,\\ k,\\ n-k", groesse=54), abstand=0.2)),
            (text("ein Versuch", groesse=G_TEXT, farbe=TEXT_LEISE),
             reihe(formel("p,\\ 1-p", groesse=54), abstand=0.2)),
            (text("Ergebnis", groesse=G_TEXT, farbe=TEXT_LEISE),
             reihe(text("genau", groesse=G_TEXT), formel("k", groesse=46), text("von", groesse=G_TEXT),
                   formel("n", groesse=46), abstand=0.18, grundlinie=True)),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Im Koeffizienten und in den Exponenten stehen Anzahlen. "
            "Die Basen sind Wahrscheinlichkeiten für einen einzelnen Versuch. "
            "Das Ergebnis gilt für genau k Treffer von n."
        ):
            for punkt, beginn in zip(punkte, (0.1, 0.42, 0.72)):
                self.warte_bis(beginn)
                self.play(auftritt(punkt), run_time=0.5)

