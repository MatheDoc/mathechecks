"""Check 05 – Histogramm Kumul-Wkt.

Kernidee: Der Balken über k ist P(X ≤ k). „Höchstens“ liest man direkt ab; alles andere ist eine Differenz
zweier Balken (oder 1 minus ein Balken).
Beispiel: n = 10, p = 0,4 wie im Musterbeispiel (P(X ≤ 2) ≈ 0,17, P(X = 5) ≈ 0,83 − 0,63, P(X ≥ 7) ≈ 1 − 0,95),
dazu „weniger als 5“ und „mehr als 3 und höchstens 7“ wie im Training.
Exakt: P(X≤2) = 0,1673, P(X≤3) = 0,3823, P(X≤4) = 0,6331, P(X≤5) = 0,8338, P(X≤6) = 0,9452, P(X≤7) = 0,9877.
"""
from manim import UP, Create, FadeOut, Mobject, VGroup, Write

from mcvideo import Histogramm, MCSzene, auftritt, aufzaehlung, formel, reihe, text, wortlaut
from mcvideo.theme import BLAU, HERVOR, TEXT_LEISE

G_FORMEL = 56
G_TEXT = 40


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.4)
        self.add(karte)
        self.hist = self.auf_buehne(Histogramm(
            10, 0.4, bis=10, y_max=1.3, zahlen=tuple(range(11)), hoehe=3.4, kumuliert=True,
            y_werte=(0.2, 0.4, 0.6, 0.8, 1.0),
        ))

        self.einstieg(
            "Wie nutzt du ein", "kumuliertes Histogramm?",
            bild=self.hist.aufbau(),
        )

        # ---------- Idee mit „höchstens 2“ ----------
        linie = self.hist.ablesen(2)
        idee = self.tafel(
            reihe(text("Balken über", groesse=G_TEXT), formel("k", groesse=G_FORMEL), text(":", groesse=G_TEXT),
                  abstand=0.15, grundlinie=True),
            formel(r"P(X\leq k)", groesse=G_FORMEL + 8),
            wortlaut("höchstens 2", signal=("höchstens 2",), groesse=44),
            formel(r"P(X\leq 2)\approx 0{,}17", groesse=G_FORMEL),
            abstand=0.4,
        )
        with self.sprich(
            "Im kumulierten Histogramm ist jeder Balken die Wahrscheinlichkeit für höchstens diese Anzahl. "
            "Deshalb wachsen die Balken bis 1. Höchstens 2 liest du direkt ab: etwa 0,17."
        ):
            self.play(auftritt(idee[0]), run_time=0.5)
            self.warte_bis(0.2)
            self.play(Write(idee[1]), run_time=0.8)
            self.warte_bis(0.62)
            self.play(auftritt(idee[2]), self.hist.faerbe((2, 2, HERVOR)), run_time=0.6)
            self.play(Create(linie), Write(idee[3]), run_time=0.8)
        self.wait(0.5)
        self.play(FadeOut(idee, shift=0.25 * UP), FadeOut(linie), run_time=0.4)

        # ---------- Fälle ----------
        self.fall(
            wortlaut("weniger als 5", signal=("weniger als 5",), groesse=44),
            [formel(r"P(X\leq 4)\approx 0{,}63", groesse=G_FORMEL)],
            balken=[(4, HERVOR)],
            sprechtext="Weniger als 5 heißt höchstens 4. Also Balken 4: etwa 0,63.",
        )
        self.fall(
            wortlaut("genau 5", signal=("genau 5",), groesse=44),
            [
                formel(r"P(X=5)=P(X\leq 5)-P(X\leq 4)", groesse=G_FORMEL),
                formel(r"\approx 0{,}83-0{,}63=0{,}20", groesse=G_FORMEL),
            ],
            balken=[(5, HERVOR), (4, BLAU)],
            sprechtext="Genau 5 ist die Stufe von Balken 4 zu Balken 5: "
                       "0,83 minus 0,63, also 0,2.",
        )
        self.fall(
            wortlaut("mindestens 7", signal=("mindestens 7",), groesse=44),
            [
                formel(r"P(X\geq 7)=1-P(X\leq 6)", groesse=G_FORMEL),
                formel(r"\approx 1-0{,}95=0{,}05", groesse=G_FORMEL),
            ],
            balken=[(6, BLAU)],
            sprechtext="Mindestens 7 ist der Rest über Balken 6: 1 minus 0,95, "
                       "also 0,05.",
        )
        self.fall(
            wortlaut("mehr als 3 und höchstens 7", signal=("mehr als 3", "höchstens 7"), groesse=44),
            [
                formel(r"P(X\leq 7)-P(X\leq 3)", groesse=G_FORMEL),
                formel(r"\approx 0{,}99-0{,}38=0{,}61", groesse=G_FORMEL),
            ],
            balken=[(7, HERVOR), (3, BLAU)],
            sprechtext="Mehr als 3 und höchstens 7: Balken 7 minus Balken 3, "
                       "0,99 minus 0,38, also 0,61.",
        )

        # ---------- Kurzfassung ----------
        def regel(stichwort: str, tex: str) -> tuple[Mobject, Mobject]:
            return text(stichwort, groesse=40, farbe=TEXT_LEISE), formel(tex, groesse=50)

        punkte = aufzaehlung(
            regel("höchstens k", r"P(X\leq k)"),
            regel("genau k", r"P(X\leq k)-P(X\leq k-1)"),
            regel("mindestens k", r"1-P(X\leq k-1)"),
            regel("a bis b", r"P(X\leq b)-P(X\leq a-1)"),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Höchstens liest du direkt ab. Für genau, mindestens und Bereiche "
            "ziehst du einen Balken von einem anderen oder von 1 ab."
        ):
            self.play(self.hist.faerbe(), run_time=0.5)
            for punkt, beginn in zip(punkte, (0.1, 0.4, 0.55, 0.75)):
                self.warte_bis(beginn)
                self.play(auftritt(punkt), run_time=0.5)

    def fall(
        self,
        frage: Mobject,
        zeilen: list[Mobject],
        *,
        balken: list[tuple[int, str]],
        sprechtext: str,
    ) -> None:
        """Ein Ereignis: Wortlaut, abzulesende Balken färben und ablesen, Rechnung."""
        block = self.tafel(frage, *zeilen, abstand=0.5)
        linien = VGroup(*[self.hist.ablesen(k, farbe) for k, farbe in balken])
        with self.sprich(sprechtext):
            self.play(auftritt(frage), run_time=0.5)
            self.warte_bis(0.3)
            self.play(self.hist.faerbe(*[(k, k, farbe) for k, farbe in balken]), run_time=0.7)
            self.play(*[Create(linie) for linie in linien], run_time=0.6)
            for zeile, beginn in zip(zeilen, (0.45, 0.7)):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(linien), run_time=0.4)
