"""Check 09 – Umgebungen des Erwartungswerts.

Kernidee: Abweichung bestimmen (d, r·μ oder c·σ), Grenzen μ ± Abweichung, auf ganze Anzahlen runden:
„höchstens“ → innerhalb, nach innen runden; „mindestens“ → außerhalb, links ab-, rechts aufrunden, beide Seiten addieren.
Beispiel: Musterbeispiel n = 25, p = 0,3, μ = 7,5, σ ≈ 2,29 (exakt 2,2913):
höchstens 2 → P(6 ≤ X ≤ 9) ≈ 0,6171; mindestens 10 % → P(X ≤ 6) + P(X ≥ 9) ≈ 0,6637;
höchstens 2σ → Grenzen 2,92 und 12,08 → P(3 ≤ X ≤ 12) ≈ 0,9736.
"""
from manim import BOLD, DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, Line, Mobject, VGroup, Write

from mcvideo import MCSzene, Zahlenstrahl, auftritt, formel, kurzfassung, reihe, text, wortlaut
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

G_FORMEL = 56
G_TEXT = 40


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.6)
        self.add(karte)
        self.strahl = self.auf_buehne(Zahlenstrahl(25, titel=" "))
        kopf = self.kopf(r"n=25\qquad p=0{,}3")
        mu = self.grenzmarke(7.5, r"\mu", TEXT)

        self.einstieg(
            "Wie berechnest du", "Umgebungen von μ?",
            sprechtext="Wie berechnest du Wahrscheinlichkeiten für Umgebungen des Erwartungswerts?",
            bild=self.strahl.aufbau(),
            kopf=kopf,
        )

        # ---------- Idee ----------
        idee = self.tafel(
            formel(r"\mu=25\cdot 0{,}3=7{,}5", groesse=G_FORMEL),
            formel(r"\sigma=\sqrt{25\cdot 0{,}3\cdot 0{,}7}\approx 2{,}29", groesse=G_FORMEL),
            reihe(text("Abweichung:", groesse=G_TEXT, farbe=TEXT_LEISE),
                  formel(r"d,\ \ r\cdot\mu\ \ \text{oder}\ \ c\cdot\sigma", groesse=G_FORMEL), abstand=0.3),
            abstand=0.5,
        )
        with self.sprich(
            "Zuerst berechnen wir mü und Sigma: mü ist 7,5, Sigma etwa 2,29. "
            "Gefragt ist, wie weit X von mü abweicht: um einen festen Wert, einen Prozentsatz von mü "
            "oder ein Vielfaches von Sigma."
        ):
            self.play(Write(idee[0]), FadeIn(mu), run_time=0.8)
            self.warte_bis(0.25)
            self.play(Write(idee[1]), run_time=0.8)
            self.warte_bis(0.55)
            self.play(auftritt(idee[2]), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(idee, shift=0.25 * UP), run_time=0.4)

        # ---------- absolut ----------
        self.fall(
            wortlaut("höchstens 2 vom Erwartungswert", signal=("höchstens",), groesse=42),
            [
                formel(r"7{,}5\pm 2:\ \ 5{,}5\ \ \text{und}\ \ 9{,}5", groesse=G_FORMEL),
                formel(r"P(6\leq X\leq 9)\approx 0{,}6171", groesse=G_FORMEL),
            ],
            grenzen=(5.5, 9.5), bereiche=[(6, 9)],
            sprechtext="Höchstens 2 vom Erwartungswert entfernt: Die Grenzen sind 5,5 und 9,5. "
                       "Höchstens heißt innerhalb, also 6 bis 9. Das ergibt 0,6171.",
            ab=(0.15, 0.45, 0.75),
        )

        # ---------- relativ ----------
        self.fall(
            wortlaut("mindestens 10 % vom Erwartungswert", signal=("mindestens",), groesse=42),
            [
                formel(r"0{,}1\cdot 7{,}5=0{,}75", groesse=G_FORMEL),
                formel(r"7{,}5\pm 0{,}75:\ \ 6{,}75\ \ \text{und}\ \ 8{,}25", groesse=G_FORMEL),
                formel(r"P(X\leq 6)+P(X\geq 9)\approx 0{,}6637", groesse=G_FORMEL),
            ],
            grenzen=(6.75, 8.25), bereiche=[(0, 6), (9, 25)],
            sprechtext="Mindestens 10 %: Die Abweichung ist 10 % von mü, also 0,75. "
                       "Mindestens heißt außerhalb: links abrunden, rechts aufrunden und beide Seiten addieren. "
                       "Ergebnis: 0,6637.",
            ab=(0.12, 0.35, 0.55, 0.85),
        )

        # ---------- Sigma ----------
        self.fall(
            wortlaut("höchstens die doppelte", "Standardabweichung", signal=("höchstens",), groesse=42),
            [
                formel(r"2\sigma\approx 4{,}58", groesse=G_FORMEL),
                formel(r"7{,}5\pm 4{,}58:\ \ 2{,}92\ \ \text{und}\ \ 12{,}08", groesse=G_FORMEL),
                formel(r"P(3\leq X\leq 12)\approx 0{,}9736", groesse=G_FORMEL),
            ],
            grenzen=(2.92, 12.08), bereiche=[(3, 12)],
            sprechtext="Höchstens die doppelte Standardabweichung: Die Abweichung ist etwa 4,58. "
                       "Innerhalb liegen 3 bis 12, das ergibt 0,9736.",
            ab=(0.12, 0.3, 0.5, 0.8),
        )

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Abweichung bestimmen", groesse=46),
            reihe(text("Grenzen", groesse=46), formel(r"\mu\pm\text{Abweichung}", groesse=60), abstand=0.25,
                  grundlinie=True),
            text("auf ganze Anzahlen runden", groesse=46),
            text("höchstens: innen, mindestens: außen", groesse=46, farben={"höchstens": HERVOR, "mindestens": HERVOR}),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Abweichung bestimmen, Grenzen berechnen, auf ganze Anzahlen runden. "
            "Höchstens heißt innen, mindestens heißt außen."
        ):
            self.play(self.strahl.neutral(), run_time=0.5)
            for zeile, beginn in zip(schritte, (0.08, 0.3, 0.48, 0.72)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def grenzmarke(self, wert: float, tex: str, farbe: str, seite: int = 0) -> VGroup:
        """Senkrechte Marke an einer Stelle des Zahlenstrahls mit Beschriftung darüber.

        seite: 0 = Beschriftung mittig über der Marke (μ); -1/+1 = höher und links/rechts neben der Marke (Grenzen),
        damit nahe beieinanderliegende Grenzen sich nicht überdecken.
        """
        ort = self.strahl.ort(wert)
        linie = Line(ort + (0.12 if seite == 0 else 0.6) * UP, ort + 0.72 * DOWN, color=farbe, stroke_width=4)
        schild = formel(tex, groesse=34, farbe=farbe)
        if seite == 0:
            schild.next_to(ort, UP, buff=0.2)
        else:
            schild.next_to(linie.get_top(), LEFT if seite < 0 else RIGHT, buff=0.08).align_to(linie, UP)
        return VGroup(linie, schild)

    def fall(
        self,
        frage: Mobject,
        zeilen: list[Mobject],
        *,
        grenzen: tuple[float, float],
        bereiche: list[tuple[int, int]],
        sprechtext: str,
        ab: tuple[float, ...],
    ) -> None:
        """Eine Umgebung: Wortlaut, Grenzen als Marken, Rechnung, gerundeter Bereich auf dem Zahlenstrahl.

        ab: Anteile des Sprechtexts für die Zeilen; der Bereich erscheint mit der letzten Zeile.
        """
        marken = VGroup(*[
            self.grenzmarke(g, f"{g:g}".replace(".", "{,}"), HERVOR, seite) for g, seite in zip(grenzen, (-1, 1))
        ])
        block = self.tafel(frage, *zeilen, abstand=0.5)
        with self.sprich(sprechtext):
            self.play(auftritt(frage), run_time=0.5)
            for i, (zeile, beginn) in enumerate(zip(zeilen, ab)):
                self.warte_bis(beginn)
                if i == len(zeilen) - 2:
                    self.play(Write(zeile), FadeIn(marken), run_time=0.8)
                elif i == len(zeilen) - 1:
                    self.play(self.strahl.bereich(*bereiche), run_time=0.8)
                    self.play(Write(zeile), run_time=0.8)
                else:
                    self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(marken), run_time=0.4)
