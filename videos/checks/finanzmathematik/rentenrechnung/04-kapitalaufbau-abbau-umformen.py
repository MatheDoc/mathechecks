"""Check 04 – Kapitalauf- und -abbau (Formel umformen).

Kernidee: E_n = K_0 · q^n ± R_n – Startkapital und Raten werden getrennt bewertet; Einzahlungen kommen dazu,
Entnahmen werden abgezogen. K_0 oder r gesucht: bekannten Anteil ausrechnen, auflösen; n gesucht: q^n ausklammern,
Logarithmus.
Beispiel: Musterbeispiel a) (E_n) und b) (n). Der Fall „r gesucht“ hat eigene Zahlen
(K_0 = 50 000 €, p = 3 %, n = 10, E_10 = 20 000 €, nachschüssige Entnahmen → r ≈ 4 116,92 €).
"""
from manim import DOWN, LEFT, UP, FadeOut, MathTex, Mobject, ReplacementTransform, VGroup, Write

from mcvideo import MCSzene, aufzaehlung, auftritt, betrag, formel, legende, reihe, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

G_FORMEL = 48
G_GEGEBEN = 36
G_TEXT = 36
G_BUEHNE = 96

# Teile der großen Formel: E_n = K_0 · q^{ n } ± R_n
E, KQ, N, ZEICHEN, R = 0, (2, 3, 4), 3, 5, 6


def hervor(zeile: MathTex, *teile: int) -> MathTex:
    for teil in teile:
        zeile[teil].set_color(HERVOR)
    return zeile


def gegeben(*angaben: tuple[str, str, bool]) -> VGroup:
    """Gegebene Werte in zwei Zeilen: (Name, Wert, Euro), je Zeile auf der Höhe ihres Gleichheitszeichens."""
    teile = [
        betrag(name, "=", wert, groesse=G_GEGEBEN, farbe=TEXT_LEISE) if euro
        else formel(name, "=", wert, groesse=G_GEGEBEN, farbe=TEXT_LEISE)
        for name, wert, euro in angaben
    ]
    zeilen = VGroup()
    for gruppe in (teile[:2], teile[2:]):  # zwei Angaben je Zeile, damit die Schrift groß bleibt
        zeile = VGroup(*gruppe).arrange(buff=0.6)
        gleich = [(t[0] if isinstance(t, VGroup) else t)[1] for t in gruppe]
        for teil, zeichen in zip(gruppe, gleich):
            teil.shift((gleich[0].get_y() - zeichen.get_y()) * UP)
        zeilen.add(zeile)
    return zeilen.arrange(DOWN, buff=0.2)


def ergebnis(name: str, wert: str, euro: bool = False) -> Mobject:
    zeile = (betrag if euro else formel)(name, r"\approx", wert, groesse=G_FORMEL, farbe=HERVOR)
    (zeile[0] if euro else zeile)[1].set_color(TEXT)
    return zeile


def art(inhalt: str) -> Mobject:
    """Art der Aufgabe über den gegebenen Werten, etwa „Kapitalaufbau, nachschüssig“."""
    return text(inhalt, groesse=G_TEXT)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.3)
        self.bild = self.buehnenbild("E_n", r"\pm", "R_n")
        self.add(karte)

        self.einstieg(
            "Wie rechnest du mit", "Startkapital und Raten?",
            zusatz="(Kapitalauf- und -abbau)",
            bild=[Write(self.bild[0]), auftritt(self.bild[1])],
        )

        # ---------- Idee ----------
        teile = legende(
            (formel("+", groesse=60), text("Einzahlungen: Kapitalaufbau", groesse=G_TEXT)),
            (formel("-", groesse=60), text("Entnahmen: Kapitalabbau", groesse=G_TEXT)),
        )
        vor = reihe(
            text("vorschüssig:", groesse=G_TEXT, farbe=TEXT_LEISE),
            formel(r"\overline{E}_n=K_0\cdot q^n\pm\overline{R}_n", groesse=44, farbe=TEXT_LEISE),
            abstand=0.3, grundlinie=True,
        )
        block = self.tafel(teile, vor, abstand=0.8)
        f, schilder = self.bild
        with self.sprich(
            "Startkapital und Raten kommen zusammen: Das Startkapital wächst mit Zinseszins, "
            "die Raten bewerten wir mit dem Rentenendwert. Einzahlungen plus, Entnahmen minus. "
            "Vorschüssig mit Querstrich."
        ):
            self.warte_bis(0.08)
            self.play(welle(VGroup(*[f[i] for i in KQ]), TEXT), schilder[0].animate.set_color(TEXT), run_time=0.7)
            self.warte_bis(0.32)
            self.play(welle(f[R], TEXT), schilder[1].animate.set_color(TEXT), run_time=0.7)
            self.warte_bis(0.6)
            self.play(auftritt(teile[0]), welle(f[ZEICHEN], TEXT), run_time=0.5)
            self.warte_bis(0.72)
            self.play(auftritt(teile[1]), run_time=0.5)
            self.warte_bis(0.86)
            self.play(auftritt(vor), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), schilder.animate.set_color(TEXT_LEISE), run_time=0.4)

        # ---------- E_n gesucht (Aufbau, nachschüssig) ----------
        self.wechsel("E_n", "+", "R_n")
        self.fall(
            [E],
            art("Kapitalaufbau, nachschüssig"),
            gegeben(("K_0", r"10\,000", True), ("r", r"1\,200", True), ("p", r"3\,\%", False), ("n", "8", False)),
            [
                betrag(r"K_0\cdot q^n", "=", r"10\,000\cdot 1{,}03^{8}\approx 12\,667{,}70", groesse=G_FORMEL),
                betrag("R_8", "=", r"\frac{1\,200\cdot(1{,}03^{8}-1)}{0{,}03}\approx 10\,670{,}80", groesse=G_FORMEL),
                hervor(formel("E_8", "=", r"12\,667{,}70+10\,670{,}80", groesse=G_FORMEL), 0),
                ergebnis("E_8", r"23\,338{,}50", euro=True),
            ],
            rechnung_ab=(0.42, 0.58, 0.74, 0.88),
            sprechtext="Kapitalaufbau mit nachschüssigen Raten, gesucht ist E n. "
                       "Beide Anteile ausrechnen und addieren.",
        )

        # ---------- r gesucht (Abbau, nachschüssig) ----------
        self.wechsel("E_n", "-", "R_n")
        self.fall(
            [R],
            art("Kapitalabbau, nachschüssig"),
            gegeben(("K_0", r"50\,000", True), (r"E_{10}", r"20\,000", True), ("p", r"3\,\%", False),
                    ("n", "10", False)),
            [
                hervor(formel(r"20\,000", "=", r"50\,000\cdot 1{,}03^{10}-", "r", r"\cdot\frac{1{,}03^{10}-1}{0{,}03}",
                              groesse=G_FORMEL), 3),
                hervor(formel(r"20\,000", "=", r"67\,195{,}82-", "r", r"\cdot 11{,}4639", groesse=G_FORMEL), 3),
                hervor(formel("r", r"\cdot 11{,}4639=47\,195{,}82", groesse=G_FORMEL), 0),
                ergebnis("r", r"4\,116{,}92", euro=True),
            ],
            rechnung_ab=(0.35, 0.52, 0.66, 0.78),
            sprechtext="Kapitalabbau: Nach zehn Jahren sollen noch zwanzigtausend Euro übrig sein. "
                       "Gesucht ist die Rate r. Zinseszinsanteil und Bruch ausrechnen, nach r auflösen. "
                       "Genauso geht es bei K null.",
        )

        # ---------- n gesucht (Abbau, vorschüssig) ----------
        self.wechsel(r"\overline{E}_n", "-", r"\overline{R}_n")
        self.fall(
            [N],
            art("Kapitalabbau, vorschüssig, bis aufgebraucht"),
            gegeben(("K_0", r"80\,000", True), ("r", r"7\,000", True), ("p", r"2\,\%", False),
                    (r"\overline{E}_n", "0", False)),
            [
                hervor(formel("0", "=", r"80\,000\cdot 1{,}02", "^{n}",
                              r"-\frac{7\,000\cdot 1{,}02\cdot(1{,}02", "^{n}", r"-1)}{0{,}02}", groesse=G_FORMEL), 3, 5),
                hervor(formel("0", "=", r"-277\,000\cdot 1{,}02", "^{n}", r"+357\,000", groesse=G_FORMEL), 3),
                hervor(formel("1{,}02", "^{n}", r"\approx", "1{,}2888", groesse=G_FORMEL), 1),
                hervor(formel("n", "=", r"\frac{\ln 1{,}2888}{\ln 1{,}02}", r"\approx", "12{,}81", groesse=G_FORMEL),
                       0, 4),
            ],
            rechnung_ab=(0.3, 0.5, 0.64, 0.8),
            sprechtext="Jetzt vorschüssig und bis das Kapital aufgebraucht ist, also E n gleich null. "
                       "Bruch ausrechnen, q hoch n ausklammern, auflösen, logarithmieren: "
                       "Das Kapital reicht etwa zwölf Komma acht Jahre.",
        )

        # ---------- Kurzfassung ----------
        def satz(*teile: str) -> VGroup:
            return reihe(*[
                formel(teil, groesse=48) if any(z in teil for z in "_^") else text(teil, groesse=36)
                for teil in teile
            ], abstand=0.16, grundlinie=True)

        def stichwort(tex: str, farbe: str = TEXT) -> VGroup:
            return reihe(formel(tex, groesse=54, farbe=farbe), text(":", groesse=42), abstand=0.08, grundlinie=True)

        punkte = aufzaehlung(
            (stichwort("+R_n"), satz("Einzahlungen")),
            (stichwort("-R_n"), satz("Entnahmen")),
            (stichwort(r"K_0,\ r", HERVOR), satz("Anteil ausrechnen, auflösen")),
            (stichwort("n", HERVOR), satz("q^n", "ausklammern, Logarithmus")),
            abstand=0.5,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Einzahlungen plus, Entnahmen minus. Ist K null oder r gesucht, den bekannten Anteil "
            "ausrechnen und auflösen. Ist n gesucht, q hoch n ausklammern und logarithmieren."
        ):
            for zeile, beginn in zip(punkte, (0.05, 0.15, 0.3, 0.65)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def buehnenbild(self, e: str, zeichen: str, rn: str) -> VGroup:
        """Formel E = K_0 · q^n ± R auf der Bühne, darunter die Schilder „Startkapital“ und „Raten“."""
        f = formel(e, "=", r"K_0\cdot q^{", "n", "}", zeichen, rn, groesse=G_BUEHNE)
        start = text("Startkapital", groesse=30, farbe=TEXT_LEISE).next_to(VGroup(*[f[i] for i in KQ]), DOWN, buff=0.2)
        raten = text("Raten", groesse=30, farbe=TEXT_LEISE).next_to(f[R], DOWN, buff=0.2)
        raten.align_to(start, UP)
        bild = VGroup(f, VGroup(start, raten))
        return self.auf_buehne(bild)

    def wechsel(self, e: str, zeichen: str, rn: str) -> None:
        neu = self.buehnenbild(e, zeichen, rn)
        self.play(ReplacementTransform(self.bild, neu), run_time=0.6)
        self.bild = neu

    def fall(
        self,
        stellen: list[int],
        titel: Mobject,
        angaben: VGroup,
        rechnung: list[Mobject],
        *,
        rechnung_ab: tuple[float, ...],
        sprechtext: str,
    ) -> None:
        """Ein Fall: Art und Gegebenes, gesuchte Stelle in der Formel auf der Bühne, Rechnung."""
        f = self.bild[0]
        stelle = VGroup(*[f[i] for i in stellen])
        block = self.tafel(titel, angaben, *rechnung, abstand=0.4)
        with self.sprich(sprechtext):
            self.play(auftritt(titel), run_time=0.5)
            self.play(auftritt(angaben), run_time=0.5)
            self.warte_bis(rechnung_ab[0] - 0.12)
            self.play(stelle.animate.set_color(HERVOR), welle(stelle, HERVOR), run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), stelle.animate.set_color(TEXT), run_time=0.5)
