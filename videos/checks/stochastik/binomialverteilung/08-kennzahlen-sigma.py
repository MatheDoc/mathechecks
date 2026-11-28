"""Check 08 – Kenngrößen aus σ berechnen.

Kernidee: Ist σ gegeben, wird zuerst quadriert: σ² = n·p·(1−p). Mit p wird nach n umgestellt;
mit μ wird n·p durch μ ersetzt, σ² = μ·(1−p), und nach p umgestellt. Die übrige Größe folgt aus μ = n·p.
Beispiel: Musterbeispiel (Maschine p = 0,1, σ = 4,6476 → n ≈ 240,002 → 240, μ = 24;
Wahl μ = 175, σ = 10,6653 → 1 − p ≈ 0,65, p = 0,35, n = 500).
"""
from manim import BOLD, DOWN, UP, FadeOut, Mobject, ReplacementTransform, VGroup, Write

from mcvideo import MCSzene, auftritt, formel, kurzfassung, reihe, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

G_FORMEL = 54
G_GEGEBEN = 50
G_TEXT = 38
G_BUEHNE = 96


def gegeben(*angaben: str) -> VGroup:
    return reihe(*[formel(a, groesse=G_GEGEBEN, farbe=TEXT_LEISE) for a in angaben], abstand=0.6)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.8)
        self.add(karte)
        wurzel = self.auf_buehne(formel(r"\sigma=\sqrt{n\cdot p\cdot (1-p)}", groesse=G_BUEHNE))
        quadrat = self.auf_buehne(formel(r"\sigma^2", "=", "n", r"\cdot p", r"\cdot (1-p)", groesse=G_BUEHNE))
        mit_mu = self.auf_buehne(formel(r"\sigma^2", "=", r"\mu", r"\cdot (1-p)", groesse=G_BUEHNE))

        self.einstieg(
            "Wie rechnest du", "mit gegebenem σ?",
            sprechtext="Wie berechnest du Kenngrößen aus der Standardabweichung?",
            bild=[Write(wurzel)],
        )

        # ---------- Idee: quadrieren ----------
        idee = self.tafel(
            text("σ gegeben", groesse=44, gewicht=BOLD),
            text("Die Wurzel muss weg:", groesse=G_TEXT, farbe=TEXT_LEISE),
            text("zuerst quadrieren", groesse=44, gewicht=BOLD, farben={"quadrieren": HERVOR}),
            abstand=0.45,
        )
        with self.sprich(
            "Jetzt ist die Standardabweichung gegeben. Die gesuchte Größe steckt unter der Wurzel. "
            "Also quadrieren wir zuerst: Sigma Quadrat ist n mal p mal 1 minus p."
        ):
            self.play(auftritt(idee[0]), run_time=0.5)
            self.warte_bis(0.3)
            self.play(auftritt(idee[1]), run_time=0.5)
            self.warte_bis(0.6)
            self.play(auftritt(idee[2]), ReplacementTransform(wurzel, quadrat), run_time=1.0)
        self.wait(0.4)
        self.play(FadeOut(idee, shift=0.25 * UP), run_time=0.4)

        # ---------- p gegeben ----------
        hoch = formel(r"4{,}6476", "^2", r"=n\cdot 0{,}1\cdot 0{,}9", groesse=G_FORMEL)
        hoch[1].set_color(HERVOR)
        self.fall(
            text("Maschine: jedes 10. Bauteil defekt", groesse=G_TEXT, gewicht=BOLD),
            gegeben(r"p=0{,}1", r"\sigma=4{,}6476"),
            [
                hoch,
                formel(r"21{,}6002=n\cdot 0{,}09\quad|:0{,}09", groesse=G_FORMEL),
                formel(r"n\approx 240", groesse=G_FORMEL, farbe=HERVOR),
                formel(r"\mu=240\cdot 0{,}1=24", groesse=G_FORMEL, farbe=HERVOR),
            ],
            stelle=quadrat[2],
            rechnung_ab=(0.25, 0.45, 0.62, 0.85),
            sprechtext="Jedes zehnte Bauteil einer Maschine ist defekt, Sigma ist 4,6476. "
                       "Wir setzen ein und teilen durch 0,09. "
                       "n ist etwa 240, als Anzahl eine ganze Zahl. Dann ist mü gleich 24.",
        )

        # ---------- μ gegeben ----------
        with self.sprich(
            "Ist statt p der Erwartungswert gegeben, hilft ein Trick: n mal p ist mü. "
            "Also ist Sigma Quadrat gleich mü mal 1 minus p, und nur p ist unbekannt."
        ):
            self.play(welle(VGroup(quadrat[2], quadrat[3]), HERVOR), run_time=0.6)
            self.warte_bis(0.45)
            self.play(ReplacementTransform(quadrat, mit_mu), run_time=1.0)
        self.wait(0.3)
        self.fall(
            text("Wahl: unentschlossene Befragte", groesse=G_TEXT, gewicht=BOLD),
            gegeben(r"\mu=175", r"\sigma=10{,}6653"),
            [
                formel(r"10{,}6653^2=175\cdot (1-p)\quad|:175", groesse=G_FORMEL),
                formel(r"0{,}65\approx 1-p", groesse=G_FORMEL),
                formel(r"p=0{,}35=35\,\%", groesse=G_FORMEL, farbe=HERVOR),
                formel(r"n=\frac{175}{0{,}35}=500", groesse=G_FORMEL, farbe=HERVOR),
            ],
            stelle=mit_mu[3],
            rechnung_ab=(0.2, 0.42, 0.6, 0.8),
            sprechtext="Bei einer Wahlumfrage ist mü 175 und Sigma 10,6653. "
                       "Wir teilen durch 175: 1 minus p ist 0,65, "
                       "also p gleich 35 %. Und n ist mü durch p, also 500.",
        )

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("quadrieren", groesse=46),
            reihe(formel("p", groesse=62), text("gegeben: nach", groesse=46), formel("n", groesse=62),
                  text("umstellen", groesse=46), abstand=0.2, grundlinie=True),
            reihe(formel(r"\mu", groesse=62), text("gegeben:", groesse=46), formel(r"\sigma^2=\mu\cdot (1-p)", groesse=62),
                  abstand=0.2, grundlinie=True),
            reihe(text("Rest aus", groesse=46), formel(r"\mu=n\cdot p", groesse=62), abstand=0.2, grundlinie=True),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: zuerst quadrieren. Mit p nach n umstellen, mit mü Sigma Quadrat gleich mü mal 1 minus p nutzen. "
            "Den Rest liefert mü gleich n mal p."
        ):
            for zeile, beginn in zip(schritte, (0.08, 0.25, 0.42, 0.75)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def fall(
        self,
        lage: Mobject,
        angaben: VGroup,
        rechnung: list[Mobject],
        *,
        stelle: Mobject,
        rechnung_ab: tuple[float, ...],
        sprechtext: str,
    ) -> None:
        """Ein Fall: Sachzusammenhang, Gegebenes, Unbekannte in der Formel auf der Bühne orange, Rechnung."""
        block = self.tafel(lage, angaben, *rechnung, abstand=0.42)
        with self.sprich(sprechtext):
            self.play(auftritt(lage), auftritt(angaben), run_time=0.6)
            self.play(stelle.animate.set_color(HERVOR), welle(stelle, HERVOR), run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), stelle.animate.set_color(TEXT), run_time=0.5)
