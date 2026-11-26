"""Check 01 – Zinseszinsformel umformen.

Kernidee: Wo die Unbekannte in K_n = K_0 · q^n steht, entscheidet über das Werkzeug:
allein → ausrechnen, Faktor → teilen, Basis → Wurzel, Exponent → Logarithmus.
Beispiel: Musterbeispiel a) bis d) ohne Abweichung.
"""
from manim import BOLD, DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, MathTex, Mobject, VGroup, Write

from mcvideo import MCSzene, auftritt, aufzaehlung, betrag, formel, reihe, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

G_FORMEL = 50
G_GEGEBEN = 40
G_TEXT = 36

# Teile der großen Formel auf der Bühne: K_n = K_0 · q ^n
TEILE = {"K_n": 0, "K_0": 2, "q": 4, "n": 5}


def hervor(zeile: MathTex, *teile: int) -> MathTex:
    """Färbt die Teile einer Formel, die zur gesuchten Größe gehören."""
    for teil in teile:
        zeile[teil].set_color(HERVOR)
    return zeile


def gegeben(*angaben: tuple[str, str, bool]) -> VGroup:
    """Gegebene Werte in einer Zeile: (Name, Wert, Euro). Alle Angaben stehen auf der Höhe ihres Gleichheitszeichens."""
    teile = []
    for name, wert, euro in angaben:
        teile.append(
            betrag(name, "=", wert, groesse=G_GEGEBEN, farbe=TEXT_LEISE) if euro
            else formel(name, "=", wert, groesse=G_GEGEBEN, farbe=TEXT_LEISE)
        )
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


def nebenbei(tex: str) -> MathTex:
    """Umformung am Rand wie im Heft, etwa „| : 5 000“."""
    return formel(tex, groesse=40, farbe=TEXT_LEISE)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.8)
        self.zzf = self.auf_buehne(formel("K_n", "=", "K_0", r"\cdot", "q", "^{n}", groesse=120))
        self.add(karte)

        self.einstieg(
            "Wie formst du die", "Zinseszinsformel um?",
            bild=[Write(self.zzf)],
        )

        # ---------- Zinsfaktor ----------
        definition = formel(r"q=1+\frac{p}{100}", groesse=64)
        beispiel = formel(r"p=3\,\%", r"\quad\Rightarrow\quad", "q=1{,}03", groesse=G_FORMEL)
        merke = text("3 gegeben, 1 gesucht", groesse=44, gewicht=BOLD, farben={"1 gesucht": HERVOR})
        block = self.tafel(definition, beispiel, merke, abstand=0.8)
        with self.sprich(
            "In der Formel stecken vier Größen. Den Zinsfaktor q bilden wir aus dem Zinssatz: "
            "q gleich eins plus p durch hundert. "
            "Bei drei Prozent ist q eins Komma null drei. Drei Größen sind gegeben, eine ist gesucht."
        ):
            self.play(
                *[
                    self.zzf[TEILE[name]].animate(rate_func=lambda a: 4 * a * (1 - a)).scale(1.25)
                    for name in ("K_0", "K_n", "n", "q")
                ],
                run_time=1.2,
            )
            self.warte_bis(0.2)
            self.play(auftritt(definition), welle(self.zzf[TEILE["q"]], HERVOR), run_time=0.6)
            self.warte_bis(0.55)
            self.play(auftritt(beispiel), run_time=0.6)
            self.warte_bis(0.82)
            self.play(auftritt(merke), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- K_n gesucht ----------
        self.fall(
            "K_n", "allein",
            gegeben((r"K_0", r"8\,000", True), ("p", r"3\,\%", False), ("n", "6", False)),
            [
                hervor(formel("K_6", "=", r"8\,000\cdot 1{,}03^{6}", groesse=G_FORMEL), 0),
                ergebnis("K_6", r"9\,552{,}42", euro=True),
            ],
            rechnung_ab=(0.62, 0.85),
            sprechtext="Achttausend Euro, drei Prozent, sechs Jahre: Gesucht ist K n. "
                       "K n steht schon allein. Also nur einsetzen und ausrechnen.",
        )

        # ---------- K_0 gesucht ----------
        self.fall(
            "K_0", "Faktor",
            gegeben((r"K_n", r"12\,000", True), ("p", r"2{,}5\,\%", False), ("n", "10", False)),
            [
                hervor(formel(r"12\,000", "=", "K_0", r"\cdot 1{,}025^{10}", groesse=G_FORMEL), 2),
                hervor(formel("K_0", "=", r"\frac{12\,000}{1{,}025^{10}}", groesse=G_FORMEL), 0),
                ergebnis("K_0", r"9\,374{,}38", euro=True),
            ],
            rechnung_ab=(0.3, 0.72, 0.9),
            sprechtext="Jetzt ist K null gesucht. Nach dem Einsetzen steht K null als Faktor "
                       "vor eins Komma null zwei fünf hoch zehn. Also teilen wir durch diese Potenz.",
        )

        # ---------- p gesucht ----------
        self.fall(
            "q", "Basis",
            gegeben((r"K_0", r"5\,000", True), (r"K_n", r"6\,500", True), ("n", "8", False)),
            [
                reihe(
                    hervor(formel(r"6\,500", "=", r"5\,000\cdot", "q", "^{8}", groesse=G_FORMEL), 3),
                    nebenbei(r"\mid :5\,000"), abstand=0.4,
                ),
                hervor(formel("q", "^{8}", "=", "1{,}3", groesse=G_FORMEL), 0),
                hervor(formel("q", "=", r"\sqrt[8]{1{,}3}", r"\approx", "1{,}0333", groesse=G_FORMEL), 0, 4),
                ergebnis("p", r"3{,}33\,\%"),
            ],
            rechnung_ab=(0.2, 0.45, 0.6, 0.85),
            sprechtext="Ist p gesucht, steht die Unbekannte in der Basis. "
                       "Wir teilen durch K null und ziehen die achte Wurzel. "
                       "Aus q gleich eins Komma null drei drei drei wird p gleich drei Komma drei drei Prozent.",
        )

        # ---------- n gesucht ----------
        log = hervor(formel("n", "=", r"\frac{\ln 1{,}5}{\ln 1{,}04}", r"\approx", "10{,}34", groesse=G_FORMEL), 0, 4)
        self.fall(
            "n", "Exponent",
            gegeben((r"K_0", r"10\,000", True), (r"K_n", r"15\,000", True), ("p", r"4\,\%", False)),
            [
                reihe(
                    hervor(formel(r"15\,000", "=", r"10\,000\cdot 1{,}04", "^{n}", groesse=G_FORMEL), 3),
                    nebenbei(r"\mid :10\,000"), abstand=0.4,
                ),
                hervor(formel("1{,}04", "^{n}", "=", "1{,}5", groesse=G_FORMEL), 1),
                log,
            ],
            rechnung_ab=(0.2, 0.45, 0.72),
            sprechtext="Bei n steht die Unbekannte im Exponenten. Auch hier teilen wir zuerst durch K null. "
                       "Dann holt der Logarithmus n herunter: Nach etwa zehn Komma drei vier Jahren "
                       "sind es fünfzehntausend Euro.",
        )

        # ---------- Kurzfassung ----------
        def gesucht(tex: str) -> MathTex:
            return formel(tex, groesse=60, farbe=HERVOR)

        def schritt(*teile: str) -> VGroup:
            """Kurzer Satz; Teile mit Formelzeichen werden als Formel gesetzt."""
            return reihe(*[
                formel(teil, groesse=54) if any(z in teil for z in "_^") else text(teil, groesse=40)
                for teil in teile
            ], abstand=0.16, grundlinie=True)

        punkte = aufzaehlung(
            (gesucht("K_n"), schritt("einsetzen")),
            (gesucht("K_0"), schritt("durch", "q^n", "teilen")),
            (gesucht("p"), schritt("durch", "K_0", "teilen, Wurzel")),
            (gesucht("n"), schritt("durch", "K_0", "teilen, Logarithmus")),
            abstand=0.6,
        )
        titel = text("gesucht:", groesse=G_TEXT, farbe=TEXT_LEISE)
        self.tafel(titel, punkte, abstand=0.5)
        titel.align_to(punkte, LEFT)
        with self.sprich(
            "Kurz gesagt: K n gesucht: einsetzen. K null gesucht: durch q hoch n teilen. "
            "Bei p und n erst durch K null teilen, dann Wurzel oder Logarithmus."
        ):
            self.play(FadeIn(titel), run_time=0.3)
            for zeile, teil, beginn in zip(punkte, ("K_n", "K_0", "q", "n"), (0.1, 0.32, 0.58, 0.7)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), welle(self.zzf[TEILE[teil]], HERVOR), run_time=0.5)

    def fall(
        self,
        teil: str,
        rolle: str,
        angaben: VGroup,
        rechnung: list[Mobject],
        *,
        rechnung_ab: tuple[float, ...],
        sprechtext: str,
    ) -> None:
        """Ein Fall: Gegebenes, Unbekannte in der Formel auf der Bühne mit ihrer Rolle, Rechnung.

        teil: Teil der großen Formel, der unbekannt ist; rolle: seine Stellung (Faktor, Basis, Exponent).
        rechnung_ab: Anteil des Sprechtexts, bei dem die jeweilige Rechenzeile erscheint.
        """
        stelle = self.zzf[TEILE[teil]]
        # Alle Schilder stehen unter der Formel; das Schild des Exponenten schließt rechts mit ihm ab.
        schild = text(rolle, groesse=28, farbe=TEXT_LEISE).next_to(self.zzf, DOWN, buff=0.12)
        if teil == "n":
            schild.align_to(stelle, RIGHT)
        else:
            schild.set_x(stelle.get_x())
        richtung = DOWN
        block = self.tafel(angaben, *rechnung, abstand=0.5)
        with self.sprich(sprechtext):
            self.play(auftritt(angaben), run_time=0.5)
            self.play(stelle.animate.set_color(HERVOR), FadeIn(schild, shift=0.1 * richtung), welle(stelle, HERVOR),
                      run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(schild), stelle.animate.set_color(TEXT), run_time=0.5)
