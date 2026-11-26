"""Check 04 – Histogramm Einzel-Wkt.

Kernidee: Die Höhe des Balkens über k ist P(X = k). Für einen Bereich werden die Balken addiert;
sind es viele, ist 1 minus der Rest schneller.
Beispiel: n = 10, p = 0,4 wie im Musterbeispiel (P(X = 2) ≈ 0,12, P(X ≥ 7) ≈ 0,05), dazu „mehr als 3 und
höchstens 5“ und „höchstens 6“ wie im Training. Exakt: P(X=4) = 0,2508, P(X=5) = 0,2007, P(X≥7) = 0,0548.
"""
from manim import BOLD, UP, Create, FadeOut, Mobject, VGroup, Write

from mcvideo import Histogramm, MCSzene, auftritt, aufzaehlung, formel, reihe, text, wortlaut
from mcvideo.theme import HERVOR, TEXT_LEISE

G_FORMEL = 56
G_TEXT = 40


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.4)
        self.add(karte)
        self.hist = self.auf_buehne(Histogramm(
            10, 0.4, bis=10, y_max=0.27, zahlen=tuple(range(11)), hoehe=3.4, y_werte=(0.1, 0.2),
        ))

        self.einstieg(
            "Wie nutzt du ein", "Histogramm?",
            zusatz="(Einzelwahrscheinlichkeiten)",
            sprechtext="Wie nutzt du ein Histogramm der Einzelwahrscheinlichkeiten?",
            bild=self.hist.aufbau(),
        )

        # ---------- Idee ----------
        idee = self.tafel(
            reihe(text("Balken über", groesse=G_TEXT), formel("k", groesse=G_FORMEL), text(":", groesse=G_TEXT),
                  abstand=0.15, grundlinie=True),
            formel("P(X=k)", groesse=G_FORMEL + 8),
            text("genau k Treffer", groesse=G_TEXT, farbe=TEXT_LEISE),
            abstand=0.4,
        )
        with self.sprich(
            "Das Histogramm zeigt eine Binomialverteilung mit n gleich zehn. "
            "Die Höhe jedes Balkens ist die Wahrscheinlichkeit für genau diese Anzahl von Treffern."
        ):
            self.play(auftritt(idee[0]), run_time=0.5)
            self.warte_bis(0.5)
            self.play(Write(idee[1]), auftritt(idee[2]), run_time=0.8)
        self.wait(0.5)
        self.play(FadeOut(idee, shift=0.25 * UP), run_time=0.4)

        # ---------- Fälle ----------
        self.fall(
            wortlaut("genau 2", signal=("genau 2",), groesse=44),
            [formel(r"P(X=2)\approx 0{,}12", groesse=G_FORMEL)],
            bereiche=[(2, 2)], ablesen=[2],
            sprechtext="Genau zwei: Wir lesen die Höhe des Balkens über zwei ab, etwa null Komma eins zwei.",
        )
        self.fall(
            wortlaut("mehr als 3 und höchstens 5", signal=("mehr als 3", "höchstens 5"), groesse=44),
            [
                formel(r"P(X=4)+P(X=5)", groesse=G_FORMEL),
                formel(r"\approx 0{,}25+0{,}20=0{,}45", groesse=G_FORMEL),
            ],
            bereiche=[(4, 5)], ablesen=[4, 5],
            sprechtext="Mehr als drei und höchstens fünf: Das sind vier und fünf. "
                       "Wir addieren beide Balken: null Komma zwei fünf plus null Komma zwei, also null Komma vier fünf.",
        )
        self.fall(
            wortlaut("mindestens 7", signal=("mindestens 7",), groesse=44),
            [
                formel(r"P(X\geq 7)", groesse=G_FORMEL),
                formel(r"\approx 0{,}04+0{,}01+0+0\approx 0{,}05", groesse=G_FORMEL),
            ],
            bereiche=[(7, 10)], ablesen=[7, 8],
            sprechtext="Mindestens sieben: Die Balken von sieben bis zehn sind sehr niedrig, zusammen etwa null Komma null fünf.",
        )
        self.fall(
            wortlaut("höchstens 6", signal=("höchstens 6",), groesse=44),
            [
                formel(r"P(X\leq 6)=1-P(X\geq 7)", groesse=G_FORMEL),
                formel(r"\approx 1-0{,}05=0{,}95", groesse=G_FORMEL),
            ],
            bereiche=[(0, 6)], ablesen=[],
            sprechtext="Höchstens sechs wären sieben Balken. Schneller geht es mit dem Rest: "
                       "eins minus null Komma null fünf, also null Komma neun fünf.",
        )

        # ---------- Kurzfassung ----------
        punkte = aufzaehlung(
            text("genau: Balkenhöhe ablesen", groesse=46, farben={"genau:": TEXT_LEISE}),
            text("Bereich: Balken addieren", groesse=46, farben={"Bereich:": TEXT_LEISE}),
            text("viele Balken: 1 minus Rest", groesse=46, farben={"viele Balken:": TEXT_LEISE}),
            abstand=0.7,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Für genau eine Anzahl liest du die Balkenhöhe ab. Für einen Bereich addierst du die Balken. "
            "Sind es viele, rechnest du eins minus den Rest."
        ):
            self.play(self.hist.faerbe(), run_time=0.5)
            for punkt, beginn in zip(punkte, (0.1, 0.42, 0.7)):
                self.warte_bis(beginn)
                self.play(auftritt(punkt), run_time=0.5)

    def fall(
        self,
        frage: Mobject,
        zeilen: list[Mobject],
        *,
        bereiche: list[tuple[int, int]],
        ablesen: list[int],
        sprechtext: str,
    ) -> None:
        """Ein Ereignis: Wortlaut, Balken färben, Höhen ablesen, Rechnung."""
        block = self.tafel(frage, *zeilen, abstand=0.5)
        linien = VGroup(*[self.hist.ablesen(k) for k in ablesen])
        with self.sprich(sprechtext):
            self.play(auftritt(frage), run_time=0.5)
            self.play(self.hist.faerbe(*[(a, b, HERVOR) for a, b in bereiche]), run_time=0.7)
            self.warte_bis(0.35)
            if len(linien):
                self.play(*[Create(linie) for linie in linien], run_time=0.6)
            for zeile, beginn in zip(zeilen, (0.4, 0.7)):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(linien), run_time=0.4)
