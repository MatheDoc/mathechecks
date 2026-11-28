"""Check 01 – Rentenendwertformel umformen.

Kernidee: Wo die Unbekannte in der Rentenendwertformel steht, entscheidet über das Werkzeug:
R_n allein → einsetzen, r Faktor → Bruch ohne r ausrechnen und teilen, n im Exponenten → nach q^n auflösen,
Logarithmus. Nebenbei: Vorschüssig kommt ein Faktor q hinzu.
Beispiel: Musterbeispiel a), b) und c), ohne Abweichung.
"""
from manim import DOWN, LEFT, UP, FadeIn, FadeOut, MathTex, Mobject, ReplacementTransform, VGroup, Write

from mcvideo import MCSzene, auftritt, aufzaehlung, betrag, formel, legende, reihe, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

G_FORMEL = 52
G_GEGEBEN = 40
G_TEXT = 36
G_BUEHNE = 92

# Teile der großen Formel auf der Bühne, nachschüssig und vorschüssig
NACH = ("R_n", "=", "{", "r", r"\cdot(q^{", "n", "}-1)", r"\over", "q-1}")
VOR = (r"\overline{R}_n", "=", "{", "r", r"\cdot", "q", r"\cdot(q^{", "n", "}-1)", r"\over", "q-1}")
TEILE_NACH = {"R": 0, "r": 3, "n": 5}
TEILE_VOR = {"R": 0, "r": 3, "q": 5, "n": 7}


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
    """Umformung am Rand wie im Heft, etwa „| · 0,04“."""
    return formel(tex, groesse=38, farbe=TEXT_LEISE)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.3)
        self.ref = self.auf_buehne(formel(*NACH, groesse=G_BUEHNE)).shift(0.2 * UP)
        self.teile = TEILE_NACH
        self.add(karte)

        self.einstieg(
            "Wie formst du die", "Rentenendwertformel um?",
            bild=[Write(self.ref)],
        )

        # ---------- Größen ----------
        groessen = legende(
            (formel("R_n", groesse=G_FORMEL), text("Wert aller Raten am Ende", groesse=G_TEXT)),
            (formel("r", groesse=G_FORMEL), text("Rate (jährliche Zahlung)", groesse=G_TEXT)),
            (formel("q", groesse=G_FORMEL), reihe(
                text("Zinsfaktor", groesse=G_TEXT), formel(r"q=1+\frac{p}{100}", groesse=40, farbe=TEXT_LEISE),
                abstand=0.3,
            )),
            (formel("n", groesse=G_FORMEL), text("Laufzeit in Jahren", groesse=G_TEXT)),
        )
        merke = text("3 gegeben, 1 gesucht", groesse=44, farben={"1 gesucht": HERVOR})
        block = self.tafel(groessen, merke, abstand=0.7)
        with self.sprich(
            "Der Rentenendwert R n ist der Wert aller Raten am Ende. "
            "Dazu kommen die Rate r, der Zinsfaktor q und die Laufzeit n. "
            "3 Größen sind gegeben, eine ist gesucht."
        ):
            for zeile, name, beginn in zip(groessen, ("R", "r", None, "n"), (0.05, 0.4, 0.52, 0.64)):
                self.warte_bis(beginn)
                puls = [] if name is None else [self.puls(name)]
                self.play(auftritt(zeile), *puls, run_time=0.6)
            self.warte_bis(0.8)
            self.play(auftritt(merke), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- R_n gesucht ----------
        self.fall(
            "R", "allein",
            gegeben(("r", r"2\,000", True), ("p", r"3\,\%", False), ("n", "8", False)),
            [
                hervor(formel("R_8", "=", r"\frac{2\,000\cdot(1{,}03^{8}-1)}{0{,}03}", groesse=G_FORMEL), 0),
                ergebnis("R_8", r"17\,784{,}67", euro=True),
            ],
            rechnung_ab=(0.5, 0.8),
            sprechtext="Ist R n gesucht, steht es schon allein: einsetzen und ausrechnen.",
        )

        # ---------- vorschüssig ----------
        vor = formel(*VOR, groesse=G_BUEHNE)
        self.auf_buehne(vor).shift(0.2 * UP)
        hinweis = VGroup(
            text("vorschüssig: am Jahresanfang", groesse=40),
            text("jede Rate 1 Jahr länger verzinst", groesse=G_TEXT, farbe=TEXT_LEISE),
            reihe(text("zusätzlicher Faktor", groesse=40), formel("q", groesse=60),
                  abstand=0.25, grundlinie=True),
        )
        block = self.tafel(*hinweis, abstand=0.4)
        with self.sprich(
            "Wird vorschüssig gezahlt, also am Jahresanfang, wird jede Rate ein Jahr länger verzinst. "
            "Dann steht in der Formel ein zusätzlicher Faktor q."
        ):
            self.play(auftritt(hinweis[0]), run_time=0.5)
            self.warte_bis(0.35)
            self.play(auftritt(hinweis[1]), run_time=0.5)
            self.warte_bis(0.6)
            self.play(ReplacementTransform(self.ref, vor), auftritt(hinweis[2]), run_time=0.9)
            self.ref, self.teile = vor, TEILE_VOR
            self.play(welle(self.ref[TEILE_VOR["q"]], TEXT), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- r gesucht (vorschüssig) ----------
        self.fall(
            "r", "Faktor",
            gegeben((r"\overline{R}_n", r"30\,000", True), ("p", r"2\,\%", False), ("n", "10", False)),
            [
                hervor(formel(r"30\,000", "=", "r", r"\cdot\frac{1{,}02\cdot(1{,}02^{10}-1)}{0{,}02}",
                              groesse=G_FORMEL), 2),
                hervor(formel(r"30\,000", "=", "r", r"\cdot 11{,}1687", groesse=G_FORMEL), 2),
                ergebnis("r", r"2\,686{,}07", euro=True),
            ],
            rechnung_ab=(0.3, 0.55, 0.8),
            sprechtext="Jetzt ist bei einer vorschüssigen Rente r gesucht. r steht als Faktor im Zähler. "
                       "Wir rechnen den Bruch ohne r aus und teilen 30.000 "
                       "durch 11,1687.",
        )

        # zurück zur nachschüssigen Formel
        nach = formel(*NACH, groesse=G_BUEHNE)
        self.auf_buehne(nach).shift(0.2 * UP)
        self.play(ReplacementTransform(self.ref, nach), run_time=0.7)
        self.ref, self.teile = nach, TEILE_NACH

        # ---------- n gesucht ----------
        self.fall(
            "n", "Exponent",
            gegeben(("r", r"1\,500", True), ("R_n", r"20\,000", True), ("p", r"4\,\%", False)),
            [
                reihe(
                    hervor(formel(r"20\,000", "=", r"\frac{1\,500\cdot(1{,}04", "^{n}", r"-1)}{0{,}04}",
                                  groesse=G_FORMEL), 3),
                    nebenbei(r"\mid\cdot 0{,}04"), abstand=0.3,
                ),
                reihe(
                    hervor(formel(r"800", "=", r"1\,500\cdot(1{,}04", "^{n}", "-1)", groesse=G_FORMEL), 3),
                    nebenbei(r"\mid :1\,500"), abstand=0.3,
                ),
                reihe(
                    hervor(formel("1{,}04", "^{n}", r"-1\approx 0{,}5333", groesse=G_FORMEL), 1),
                    nebenbei(r"\mid +1"), abstand=0.3,
                ),
                hervor(formel("1{,}04", "^{n}", r"\approx", "1{,}5333", groesse=G_FORMEL), 1),
                hervor(formel("n", "=", r"\frac{\ln 1{,}5333}{\ln 1{,}04}", r"\approx", "10{,}90",
                              groesse=G_FORMEL), 0, 4),
            ],
            rechnung_ab=(0.1, 0.25, 0.37, 0.48, 0.7),
            sprechtext="Bei n steht die Unbekannte im Exponenten. Wir lösen zuerst nach q hoch n auf: "
                       "mal 0,04, durch 1500, plus 1. "
                       "Dann holt der Logarithmus n herunter: Nach knapp 11 Jahren "
                       "sind 20.000 Euro erreicht.",
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
            (gesucht("R_n"), satz("einsetzen")),
            (gesucht("r"), satz("Bruch ausrechnen, teilen")),
            (gesucht("n"), VGroup(
                satz("nach", "q^n", "auflösen,"),
                satz("dann Logarithmus"),
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: R n gesucht: einsetzen. r gesucht: Bruch ausrechnen und teilen. "
            "n gesucht: nach q hoch n auflösen, dann Logarithmus."
        ):
            for zeile, name, beginn in zip(punkte, ("R", "r", "n"), (0.1, 0.35, 0.65)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), welle(self.ref[self.teile[name]], HERVOR), run_time=0.5)

    def puls(self, name: str):
        return self.ref[self.teile[name]].animate(rate_func=lambda a: 4 * a * (1 - a)).scale(1.25)

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
        stelle = self.ref[self.teile[name]]
        schild = text(rolle, groesse=28, farbe=TEXT_LEISE).next_to(self.ref, DOWN, buff=0.12)
        schild.set_x(stelle.get_x())
        block = self.tafel(angaben, *rechnung, abstand=0.4)
        with self.sprich(sprechtext):
            self.play(auftritt(angaben), run_time=0.5)
            self.play(stelle.animate.set_color(HERVOR), FadeIn(schild, shift=0.1 * DOWN), welle(stelle, HERVOR),
                      run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(schild), stelle.animate.set_color(TEXT), run_time=0.5)
