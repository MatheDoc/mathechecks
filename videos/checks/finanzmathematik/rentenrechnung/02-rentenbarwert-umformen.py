"""Check 02 – Rentenbarwertformel umformen.

Kernidee: Der Barwert ist der abgezinste Endwert, deshalb steht q^n zusätzlich im Nenner. Wo die Unbekannte
steht, entscheidet über den Weg: R_0 allein → einsetzen, r Faktor → Bruch ausrechnen und teilen,
n zweimal im Exponenten → erst mit dem Nenner multiplizieren, q^n sammeln, dann Logarithmus.
Beispiel: Musterbeispiel a), b) und c), ohne Abweichung.
"""
from manim import DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, MathTex, Mobject, ReplacementTransform, VGroup, Write

from mcvideo import MCSzene, auftritt, aufzaehlung, betrag, formel, reihe, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

G_FORMEL = 50
G_GEGEBEN = 40
G_TEXT = 36
G_BUEHNE = 88

# Teile der großen Formel auf der Bühne, nachschüssig und vorschüssig (gleiche Nummern)
NACH = ("R_0", "=", "{", "r", r"\cdot(q^{", "n", "}-1)", r"\over", "q^{", "n", r"}\cdot(q-1)}")
VOR = (r"\overline{R}_0", "=", "{", "r", r"\cdot q\cdot(q^{", "n", "}-1)", r"\over", "q^{", "n", r"}\cdot(q-1)}")
TEILE = {"R": (0,), "r": (3,), "n": (5, 9)}
NENNER_QN = (8, 9)


def hervor(zeile: MathTex, *teile: int) -> MathTex:
    """Färbt die Teile einer Formel, die zur gesuchten Größe gehören."""
    for teil in teile:
        zeile[teil].set_color(HERVOR)
    return zeile


def gegeben(*angaben: tuple[str, str, bool]) -> VGroup:
    """Gegebene Werte in einer Zeile: (Name, Wert, Euro), alle auf der Höhe ihres Gleichheitszeichens."""
    teile = [
        betrag(name, "=", wert, groesse=G_GEGEBEN, farbe=TEXT_LEISE) if euro
        else formel(name, "=", wert, groesse=G_GEGEBEN, farbe=TEXT_LEISE)
        for name, wert, euro in angaben
    ]
    zeile = VGroup(*teile).arrange(buff=0.5)
    gleich = [(t[0] if isinstance(t, VGroup) else t)[1] for t in teile]
    for teil, zeichen in zip(teile, gleich):
        teil.shift((gleich[0].get_y() - zeichen.get_y()) * UP)
    return zeile


def ergebnis(name: str, wert: str, euro: bool = False) -> Mobject:
    """Ergebniszeile „Name ≈ Wert“ in der Farbe der gesuchten Größe."""
    zeile = (betrag if euro else formel)(name, r"\approx", wert, groesse=G_FORMEL, farbe=HERVOR)
    (zeile[0] if euro else zeile)[1].set_color(TEXT)
    return zeile


def nebenbei(tex: str) -> MathTex:
    """Umformung am Rand wie im Heft."""
    return formel(tex, groesse=36, farbe=TEXT_LEISE)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.3)
        self.ref = self.buehnenformel(NACH)
        self.add(karte)

        self.einstieg(
            "Wie formst du die", "Rentenbarwertformel um?",
            bild=[Write(self.ref)],
        )

        # ---------- Idee: abgezinster Endwert ----------
        bedeutung = text("Wert aller Raten heute", groesse=40)
        abzinsen = reihe(
            formel("R_0", "=", r"{R_n", r"\over", "q^n}", groesse=72),
            text("Endwert, abgezinst", groesse=G_TEXT, farbe=TEXT_LEISE), abstand=0.5,
        )
        merke = text("3 gegeben, 1 gesucht", groesse=44, farben={"1 gesucht": HERVOR})
        block = self.tafel(bedeutung, abzinsen, merke, abstand=0.7)
        nenner = VGroup(*[self.ref[i] for i in NENNER_QN])
        with self.sprich(
            "Der Rentenbarwert R null ist der Wert aller Raten heute: der Endwert, auf heute abgezinst. "
            "Deshalb steht im Nenner zusätzlich q hoch n. 3 Größen sind gegeben, eine ist gesucht."
        ):
            self.play(auftritt(bedeutung), welle(self.ref[0], TEXT), run_time=0.6)
            self.warte_bis(0.25)
            self.play(auftritt(abzinsen), run_time=0.6)
            self.warte_bis(0.5)
            self.play(welle(nenner, TEXT), abzinsen[0][4].animate(rate_func=lambda a: 4 * a * (1 - a)).scale(1.3),
                      run_time=0.8)
            self.warte_bis(0.78)
            self.play(auftritt(merke), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- R_0 gesucht ----------
        self.fall(
            "R", "allein",
            gegeben(("r", r"6\,000", True), ("p", r"4\,\%", False), ("n", "12", False)),
            [
                hervor(formel("R_0", "=", r"\frac{6\,000\cdot(1{,}04^{12}-1)}{1{,}04^{12}\cdot 0{,}04}",
                              groesse=G_FORMEL), 0),
                ergebnis("R_0", r"56\,310{,}44", euro=True),
            ],
            rechnung_ab=(0.45, 0.75),
            sprechtext="Ist R null gesucht, steht es schon allein: einsetzen und ausrechnen.",
        )

        # ---------- r gesucht (vorschüssig) ----------
        vor = self.buehnenformel(VOR)
        self.play(ReplacementTransform(self.ref, vor), run_time=0.7)
        self.ref = vor
        self.fall(
            "r", "Faktor",
            gegeben((r"\overline{R}_0", r"50\,000", True), ("p", r"3\,\%", False), ("n", "10", False)),
            [
                hervor(formel(r"50\,000", "=", "r",
                              r"\cdot\frac{1{,}03\cdot(1{,}03^{10}-1)}{1{,}03^{10}\cdot 0{,}03}", groesse=G_FORMEL), 2),
                hervor(formel(r"50\,000", "=", "r", r"\cdot 8{,}7861", groesse=G_FORMEL), 2),
                ergebnis("r", r"5\,690{,}80", euro=True),
            ],
            rechnung_ab=(0.35, 0.6, 0.82),
            sprechtext="Jetzt eine vorschüssige Rente, mit dem zusätzlichen Faktor q im Zähler. Gesucht ist r. "
                       "r ist ein Faktor: Wir rechnen den Bruch ohne r aus und teilen.",
        )

        nach = self.buehnenformel(NACH)
        self.play(ReplacementTransform(self.ref, nach), run_time=0.7)
        self.ref = nach

        # ---------- n gesucht ----------
        self.fall(
            "n", "Exponent, zweimal",
            gegeben(("r", r"5\,000", True), ("R_0", r"40\,000", True), ("p", r"2{,}5\,\%", False)),
            [
                hervor(formel(r"40\,000", "=", r"\frac{5\,000\cdot(1{,}025", "^{n}", r"-1)}{1{,}025",
                              "^{n}", r"\cdot 0{,}025}", groesse=G_FORMEL), 3, 5),
                hervor(formel(r"1\,000\cdot 1{,}025", "^{n}", "=", r"5\,000\cdot 1{,}025", "^{n}", r"-5\,000",
                              groesse=G_FORMEL), 1, 4),
                hervor(formel(r"5\,000", "=", r"4\,000\cdot 1{,}025", "^{n}", groesse=G_FORMEL), 3),
                hervor(formel("1{,}025", "^{n}", "=", "1{,}25", groesse=G_FORMEL), 1),
                hervor(formel("n", "=", r"\frac{\ln 1{,}25}{\ln 1{,}025}", r"\approx", "9{,}04",
                              groesse=G_FORMEL), 0, 4),
            ],
            rechnung_ab=(0.08, 0.3, 0.48, 0.62, 0.78),
            sprechtext="Bei n steht q hoch n 2-mal in der Formel. Darum multiplizieren wir zuerst mit dem Nenner. "
                       "Dann bringen wir q hoch n auf eine Seite und teilen. Der Logarithmus liefert n: "
                       "Rund 9 Jahre lang reicht das Geld.",
        )

        # ---------- Kurzfassung ----------
        def gesucht(tex: str) -> VGroup:
            return reihe(formel(tex, groesse=56, farbe=HERVOR), text(":", groesse=44), abstand=0.08, grundlinie=True)

        def satz(*teile: str) -> VGroup:
            return reihe(*[
                formel(teil, groesse=50) if any(z in teil for z in "_^") else text(teil, groesse=38)
                for teil in teile
            ], abstand=0.16, grundlinie=True)

        punkte = aufzaehlung(
            (gesucht("R_0"), satz("einsetzen")),
            (gesucht("r"), satz("Bruch ausrechnen, teilen")),
            (gesucht("n"), VGroup(
                satz("mal Nenner,"),
                satz("q^n", "sammeln, Logarithmus"),
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: R null gesucht: einsetzen. r gesucht: Bruch ausrechnen und teilen. "
            "n gesucht: mal Nenner, q hoch n sammeln, dann Logarithmus."
        ):
            for zeile, name, beginn in zip(punkte, ("R", "r", "n"), (0.1, 0.33, 0.6)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), *[welle(self.ref[i], HERVOR) for i in TEILE[name]], run_time=0.5)

    def buehnenformel(self, teile: tuple[str, ...]) -> MathTex:
        return self.auf_buehne(formel(*teile, groesse=G_BUEHNE)).shift(0.2 * UP)

    def fall(
        self,
        name: str,
        rolle: str,
        angaben: VGroup,
        rechnung: list[Mobject],
        *,
        rechnung_ab: tuple[float, ...],
        sprechtext: str,
    ) -> None:
        """Ein Fall: Gegebenes, Unbekannte in der Formel auf der Bühne mit ihrer Rolle, Rechnung."""
        stelle = VGroup(*[self.ref[i] for i in TEILE[name]])
        schild = text(rolle, groesse=28, farbe=TEXT_LEISE).next_to(self.ref, DOWN, buff=0.12)
        if name == "n":
            schild.align_to(self.ref, RIGHT)
        elif name == "R":
            schild.align_to(self.ref, LEFT)
        else:
            schild.set_x(stelle.get_x())
        block = self.tafel(angaben, *rechnung, abstand=0.4)
        with self.sprich(sprechtext):
            self.play(auftritt(angaben), run_time=0.5)
            self.play(stelle.animate.set_color(HERVOR), FadeIn(schild, shift=0.1 * DOWN),
                      *[welle(teil, HERVOR) for teil in stelle], run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(schild), stelle.animate.set_color(TEXT), run_time=0.5)
