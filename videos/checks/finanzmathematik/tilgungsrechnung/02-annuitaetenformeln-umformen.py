"""Check 02 – Annuitätenformeln umformen.

Kernidee: Wo die Unbekannte in der Annuitätenformel steht, entscheidet über den Weg:
A allein → einsetzen; K_0 Faktor → Bruch ohne K_0 ausrechnen, teilen; n zweimal im Exponenten →
Umweg über T_1 und A = T_1 · q^n, dann Logarithmus.
Beispiel: Musterbeispiel a), b) und c), ohne Abweichung.
"""
from manim import DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, MathTex, Mobject, VGroup, Write

from mcvideo import MCSzene, auftritt, aufzaehlung, betrag, formel, legende, reihe, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

G_FORMEL = 56
G_GEGEBEN = 42
G_TEXT = 38

# Teile der großen Formel auf der Bühne: A = K_0 · q^n · (q − 1) / (q^n − 1)
TEILE = {"A": (0,), "K_0": (3,), "q": (4, 6, 8), "n": (5, 9)}


def hervor(zeile: MathTex, *teile: int) -> MathTex:
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
    zeile = VGroup(*teile).arrange(buff=0.55)
    gleich = [(t[0] if isinstance(t, VGroup) else t)[1] for t in teile]
    for teil, zeichen in zip(teile, gleich):
        teil.shift((gleich[0].get_y() - zeichen.get_y()) * UP)
    return zeile


def ergebnis(name: str, wert: str, euro: bool = False) -> Mobject:
    """Ergebniszeile „Name ≈ Wert“ in der Farbe der gesuchten Größe."""
    zeile = (betrag if euro else formel)(name, r"\approx", wert, groesse=G_FORMEL, farbe=HERVOR)
    (zeile[0] if euro else zeile)[1].set_color(TEXT)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.9)
        self.af = self.auf_buehne(formel(
            "A", "=", "{", "K_0", r"\cdot q^{", "n", r"}\cdot(q-1)", r"\over", "q^{", "n", "}-1}", groesse=96,
        )).shift(0.18 * UP)  # Platz für die Schilder unter der Formel
        self.add(karte)

        self.einstieg(
            "Wie formst du die", "Annuitätenformel um?",
            zusatz="(Annuität, Darlehenssumme, Laufzeit)",
            bild=[Write(self.af)],
        )

        # ---------- Vier Größen ----------
        groessen = legende(
            (formel("A", groesse=G_FORMEL), text("Annuität", groesse=G_TEXT)),
            (formel("K_0", groesse=G_FORMEL), text("Darlehenssumme", groesse=G_TEXT)),
            (formel("q", groesse=G_FORMEL), reihe(
                text("Zinsfaktor", groesse=G_TEXT), formel(r"q=1+\frac{p}{100}", groesse=40, farbe=TEXT_LEISE),
                abstand=0.3,
            )),
            (formel("n", groesse=G_FORMEL), text("Laufzeit in Jahren", groesse=G_TEXT)),
        )
        merke = text("3 gegeben, 1 gesucht", groesse=44, farben={"1 gesucht": HERVOR})
        block = self.tafel(groessen, merke, abstand=0.7)
        with self.sprich(
            "Die Annuitätenformel verbindet 4 Größen: Annuität A, Darlehenssumme K null, "
            "Zinsfaktor q und Laufzeit n. 3 sind gegeben, die vierte ist gesucht."
        ):
            for zeile, name, beginn in zip(groessen, ("A", "K_0", "q", "n"), (0.2, 0.36, 0.5, 0.62)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), *self.puls(name), run_time=0.6)
            self.warte_bis(0.78)
            self.play(auftritt(merke), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- A gesucht ----------
        self.fall(
            "A", "allein",
            gegeben(("K_0", r"150\,000", True), ("p", r"4\,\%", False), ("n", "20", False)),
            [
                hervor(formel("A", "=", r"\frac{150\,000\cdot 1{,}04^{20}\cdot 0{,}04}{1{,}04^{20}-1}",
                              groesse=G_FORMEL), 0),
                ergebnis("A", r"11\,037{,}26", euro=True),
            ],
            rechnung_ab=(0.35, 0.7),
            sprechtext="Ist A gesucht, steht es schon allein. Einsetzen und ausrechnen: "
                       "Bei 150.000 Euro, 4 % und 20 Jahren "
                       "sind das etwa 11.037 Euro.",
        )

        # ---------- K_0 gesucht ----------
        self.fall(
            "K_0", "Faktor",
            gegeben(("A", r"12\,000", True), ("p", r"3\,\%", False), ("n", "15", False)),
            [
                hervor(formel(r"12\,000", "=", "K_0", r"\cdot\frac{1{,}03^{15}\cdot 0{,}03}{1{,}03^{15}-1}",
                              groesse=G_FORMEL), 2),
                hervor(formel(r"12\,000", "=", "K_0", r"\cdot 0{,}08377", groesse=G_FORMEL), 2),
                ergebnis("K_0", r"143\,255{,}22", euro=True),
            ],
            rechnung_ab=(0.25, 0.5, 0.78),
            sprechtext="Ist K null gesucht, steht es als Faktor im Zähler. Wir rechnen den Bruch ohne K null aus: "
                       "0,08377. Dann teilen wir 12.000 durch diesen Faktor: "
                       "etwa 143.255 Euro.",
        )

        # ---------- n gesucht ----------
        stelle = VGroup(*[self.af[i] for i in TEILE["n"]])
        schild = text("Exponent, zweimal", groesse=28, farbe=TEXT_LEISE).next_to(self.af, DOWN, buff=0.12)
        schild.align_to(self.af, RIGHT)
        angaben = gegeben(("K_0", r"100\,000", True), ("A", r"9\,000", True), ("p", r"4\,\%", False))
        werkzeug = hervor(formel("A", "=", "T_1", r"\cdot q^{", "n", "}", groesse=64), 4)
        erklaerung = reihe(
            formel("T_1", groesse=40, farbe=TEXT_LEISE), text(": Tilgung im 1. Jahr", groesse=32, farbe=TEXT_LEISE),
            abstand=0.1, grundlinie=True,
        )
        t1 = betrag("T_1", "=", r"9\,000-100\,000\cdot 0{,}04", "=", r"5\,000", groesse=G_FORMEL)
        block = self.tafel(angaben, werkzeug, erklaerung, t1, abstand=0.5)
        with self.sprich(
            "Bei n wird es knifflig: n steht 2-mal im Exponenten. Hier hilft die zweite Formel: "
            "A gleich T eins mal q hoch n. T eins ist die Tilgung im ersten Jahr, "
            "also Annuität minus Zinsen: 5000 Euro."
        ):
            self.play(auftritt(angaben), run_time=0.5)
            self.play(stelle.animate.set_color(HERVOR), FadeIn(schild, shift=0.1 * DOWN),
                      *[welle(teil, HERVOR) for teil in stelle], run_time=0.6)
            self.warte_bis(0.35)
            self.play(auftritt(werkzeug), run_time=0.6)
            self.warte_bis(0.58)
            self.play(auftritt(erklaerung), run_time=0.5)
            self.warte_bis(0.75)
            self.play(Write(t1), run_time=0.9)
        self.wait(0.4)

        loesung = [
            hervor(formel(r"9\,000", "=", r"5\,000\cdot 1{,}04", "^{n}", groesse=G_FORMEL), 3),
            hervor(formel("1{,}04", "^{n}", "=", "1{,}8", groesse=G_FORMEL), 1),
            hervor(formel("n", "=", r"\frac{\ln 1{,}8}{\ln 1{,}04}", r"\approx", "14{,}99", groesse=G_FORMEL), 0, 4),
        ]
        rechnung = VGroup(*loesung).arrange(DOWN, buff=0.5)
        rechnung.next_to(angaben, DOWN, buff=0.6).set_x(0)
        with self.sprich(
            "Jetzt einsetzen, durch 5000 teilen und logarithmieren: n ist etwa 14,99. "
            "Nach rund 15 Jahren ist das Darlehen getilgt."
        ):
            self.play(FadeOut(VGroup(werkzeug, erklaerung, t1), shift=0.25 * UP), run_time=0.4)
            for zeile, beginn in zip(loesung, (0.1, 0.3, 0.5)):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(
            FadeOut(angaben, shift=0.25 * UP), FadeOut(rechnung, shift=0.25 * UP), FadeOut(schild),
            stelle.animate.set_color(TEXT), run_time=0.5,
        )

        # ---------- Kurzfassung ----------
        def gesucht(tex: str) -> VGroup:
            return reihe(formel(tex, groesse=56, farbe=HERVOR), text(":", groesse=44), abstand=0.08, grundlinie=True)

        def satz(*teile: str) -> VGroup:
            return reihe(*[
                formel(teil, groesse=50) if any(z in teil for z in "_^=") else text(teil, groesse=38)
                for teil in teile
            ], abstand=0.16, grundlinie=True)

        punkte = aufzaehlung(
            (gesucht("A"), satz("einsetzen")),
            (gesucht("K_0"), satz("Bruch ausrechnen, teilen")),
            (gesucht("n"), VGroup(
                satz("erst", "T_1", "berechnen"),
                satz("A=T_1\\cdot q^n,", "Logarithmus"),
            ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: A gesucht: einsetzen. K null gesucht: Bruch ausrechnen und teilen. "
            "n gesucht: erst T eins, dann A gleich T eins mal q hoch n und logarithmieren."
        ):
            for zeile, name, beginn in zip(punkte, ("A", "K_0", "n"), (0.1, 0.3, 0.6)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), *[welle(self.af[i], HERVOR) for i in TEILE[name]], run_time=0.5)

    def puls(self, name: str) -> list:
        return [
            self.af[i].animate(rate_func=lambda a: 4 * a * (1 - a)).scale(1.25) for i in TEILE[name]
        ]

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
        stelle = VGroup(*[self.af[i] for i in TEILE[name]])
        schild = text(rolle, groesse=28, farbe=TEXT_LEISE).next_to(self.af, DOWN, buff=0.12).set_x(stelle.get_x())
        if name == "A":
            schild.align_to(stelle, LEFT)
        block = self.tafel(angaben, *rechnung, abstand=0.5)
        with self.sprich(sprechtext):
            self.play(auftritt(angaben), run_time=0.5)
            self.play(stelle.animate.set_color(HERVOR), FadeIn(schild, shift=0.1 * DOWN), welle(stelle, HERVOR),
                      run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(schild), stelle.animate.set_color(TEXT), run_time=0.5)
