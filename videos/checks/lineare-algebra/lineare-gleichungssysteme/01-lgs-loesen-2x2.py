"""Check 01 – LGS 2x2.

Kernidee: Die Gleichungen werden so kombiniert, dass nur noch eine Unbekannte übrig bleibt. Die drei Verfahren
sind drei Wege dorthin und führen alle auf dieselbe Gleichung 5x = 20.
Beispiel: LGS aus dem Skript (2x + y = 13, 3x − y = 7) statt des Musterbeispiels, das beim Gleichsetzen auf
Dezimalzahlen führt. Variablen x und y wie in Skript und Musterbeispiel.
"""
from manim import (
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Animation,
    Create,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    ReplacementTransform,
    Text,
    TransformFromCopy,
    VGroup,
    Write,
    rate_functions,
)

from mcvideo import MCSzene, auftritt, aufzaehlung, formel, legende, reihe, text, welle
from mcvideo.theme import ACHSE, BLAU, HERVOR, ROSE, TEXT, TEXT_LEISE, TEXT_SCHWACH

G_FORMEL = 60


def titel(inhalt: str) -> Text:
    """Überschrift eines Abschnitts. Ohne Nummer: Die drei Verfahren sind Alternativen, kein Ablauf."""
    return text(inhalt, groesse=46, gewicht=BOLD)


def name(roemisch: str, groesse: float = 44) -> MathTex:
    return formel(rf"\mathrm{{{roemisch}}}", groesse=groesse, farbe=TEXT_LEISE)


def gleichungen(*zeilen: tuple[MathTex | None, MathTex, int | None], abstand: float = 0.35) -> VGroup:
    """Gleichungen untereinander, am Gleichheitszeichen ausgerichtet; links davon die Zeilennamen.

    zeilen: (Name oder None, Gleichung, Index des Gleichheitszeichens oder None für zentriert).
    """
    terme = VGroup(*[gleichung for _, gleichung, _ in zeilen]).arrange(DOWN, buff=abstand)
    for gleichung, (_, _, gleich) in zip(terme, zeilen):
        gleichung.shift(-(gleichung.get_x() if gleich is None else gleichung[gleich].get_x()) * RIGHT)
    block = VGroup()
    for (zeilenname, gleichung, _) in zeilen:
        if zeilenname is None:
            block.add(VGroup(gleichung))
        else:
            zeilenname.next_to(gleichung, LEFT, buff=0.35)
            block.add(VGroup(zeilenname, gleichung))
    return block


def gl(*teile: str, farben: dict[int, str] | None = None, groesse: float = G_FORMEL) -> MathTex:
    zeile = formel(*teile, groesse=groesse)
    for index, farbe in (farben or {}).items():
        zeile[index].set_color(farbe)
    return zeile


class Video(MCSzene):
    WEGE = ("gleichsetzen", "einsetzen", "addieren")

    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.0)
        self.lgs = lgs = self.auf_buehne(gleichungen(
            (name("I", 48), gl("2x", "+", "y", "=", "13", groesse=66), 3),
            (name("II", 48), gl("3x", "-", "y", "=", "7", groesse=66), 3),
            abstand=0.5,
        ))
        self.i, self.ii = lgs[0][1], lgs[1][1]
        self.add(karte)

        self.einstieg(
            "Wie löst du ein LGS", "mit zwei Unbekannten?",
            bild=[LaggedStart(*[Write(zeile) for zeile in lgs], lag_ratio=0.35)],
            sprechtext="Wie löst du ein lineares Gleichungssystem mit 2 Unbekannten?",
        )

        self.idee()
        self.gleichsetzen()
        self.einsetzen()
        self.addieren()
        self.loesen()
        self.y_bestimmen()
        self.zusammenfassen()

    # ---------- Abschnitte ----------
    def idee(self) -> None:
        ziel = text("Ziel: nur noch eine Unbekannte", groesse=46, gewicht=BOLD)
        wege = reihe(
            *[text(wort, groesse=38, farbe=TEXT_LEISE) for wort in self.WEGE],
            abstand=0.6,
        )
        block = self.tafel(ziel, wege, abstand=0.7)
        unbekannte = [self.i[0], self.i[2], self.ii[0], self.ii[2]]
        with self.sprich(
            "In jeder Gleichung stecken x und y. Wir kombinieren die Gleichungen so, "
            "dass nur noch eine Unbekannte übrig bleibt. Dafür gibt es 3 Wege."
        ):
            self.play(
                *[teil.animate(rate_func=rate_functions.there_and_back).scale(1.35) for teil in unbekannte],
                run_time=1.0,
            )
            self.warte_bis(0.3)
            self.play(auftritt(ziel), run_time=0.6)
            self.warte_bis(0.8)
            self.play(LaggedStart(*[auftritt(wort) for wort in wege], lag_ratio=0.3), run_time=0.9)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

    def gleichsetzen(self) -> None:
        kopf = titel("Gleichsetzungsverfahren")
        rechnung = gleichungen(
            (name("I"), gl("y", "=", "13-2x", farben={0: HERVOR}), 1),
            (name("II"), gl("y", "=", "3x-7", farben={0: HERVOR}), 1),
            (None, gl("13-2x", "=", "3x-7"), 1),
            (None, gl("5x", "=", "20"), 1),
            abstand=0.45,
        )
        y_i, y_ii, gleich, ergebnis = rechnung
        self.tafel(kopf, rechnung, abstand=0.6)
        with self.sprich(
            "Erstens, das Gleichsetzungsverfahren: beide Gleichungen nach y auflösen "
            "und die rechten Seiten gleichsetzen. Das y ist weg."
        ):
            self.play(auftritt(kopf), run_time=0.5)
            self.warte_bis(0.2)
            self.play(self.y_faerben(HERVOR), welle(self.i[2], HERVOR), welle(self.ii[2], HERVOR), run_time=0.6)
            self.play(Write(y_i), Write(y_ii), run_time=1.0)
            self.warte_bis(0.6)
            self.play(
                TransformFromCopy(y_i[1][2], gleich[0][0]), FadeIn(gleich[0][1]),
                TransformFromCopy(y_ii[1][2], gleich[0][2]),
                run_time=0.9,
            )
            self.warte_bis(0.85)
            self.play(auftritt(ergebnis), run_time=0.5)
        self.abschnitt_ende(kopf, rechnung)

    def einsetzen(self) -> None:
        kopf = titel("Einsetzungsverfahren")
        rechnung = gleichungen(
            (name("II"), gl("y", "=", "3x-7", farben={0: HERVOR}), None),
            (name("I"), gl("2x+", "(3x-7)", "=", "13"), None),
            (None, gl("5x", "=", "20"), None),
            abstand=0.45,
        )
        aufgeloest, eingesetzt, ergebnis = rechnung
        self.tafel(kopf, rechnung, abstand=0.6)
        with self.sprich(
            "Zweitens, das Einsetzungsverfahren: Gleichung 2 nach y auflösen "
            "und in Gleichung 1 einsetzen. Auch hier ist das y weg."
        ):
            self.play(auftritt(kopf), run_time=0.5)
            self.warte_bis(0.25)
            self.play(self.ii[2].animate.set_color(HERVOR), welle(self.ii[2], HERVOR), Write(aufgeloest), run_time=0.9)
            self.warte_bis(0.55)
            self.play(self.i[2].animate.set_color(HERVOR), welle(self.i[2], HERVOR), run_time=0.5)
            self.play(
                FadeIn(eingesetzt[0]), FadeIn(eingesetzt[1][0]), FadeIn(eingesetzt[1][2:]),
                TransformFromCopy(aufgeloest[1][2], eingesetzt[1][1]),
                run_time=0.9,
            )
            self.warte_bis(0.85)
            self.play(auftritt(ergebnis), run_time=0.5)
        self.abschnitt_ende(kopf, rechnung)

    def addieren(self) -> None:
        kopf = titel("Additionsverfahren")
        rechnung = gleichungen(
            (name("I"), gl("2x", "+", "y", "=", "13", farben={1: HERVOR, 2: HERVOR}), 3),
            (name("II"), gl("3x", "-", "y", "=", "7", farben={1: HERVOR, 2: HERVOR}), 3),
        )
        oben, unten = rechnung[0][1], rechnung[1][1]
        plus = formel("+", groesse=G_FORMEL, farbe=TEXT_LEISE).next_to(rechnung[1][0], LEFT, buff=0.2)
        rechnung[1].add(plus)
        # Schriftliche Addition: x-Glied, Gleichheitszeichen und rechte Seite in den Spalten der Gleichungen.
        strich_y = unten.get_bottom()[1] - 0.25
        strich = Line(
            [plus.get_left()[0], strich_y, 0], [oben.get_right()[0] + 0.1, strich_y, 0], color=ACHSE, stroke_width=2.5,
        )
        summe = gl("5x", "=", "20")
        summe.set_y(strich_y - 0.3 - summe.height / 2)
        summe[0].set_x(oben[0].get_x())
        summe[1].set_x(oben[3].get_x())
        summe[2].align_to(oben[4], LEFT)
        schriftlich = VGroup(rechnung, strich, summe)
        notiz = VGroup(
            text("Fällt nichts weg: vorher eine oder beide", groesse=34, farbe=TEXT_LEISE),
            text("Gleichungen mit geeigneten Zahlen", groesse=34, farbe=TEXT_LEISE),
            text("multiplizieren.", groesse=34, farbe=TEXT_LEISE),
        ).arrange(DOWN, buff=0.15)
        self.tafel(kopf, schriftlich, notiz, abstand=0.6)
        weg = VGroup(oben[1:3], unten[1:3])
        with self.sprich(
            "Drittens, das Additionsverfahren. Wir addieren beide Gleichungen: "
            "Plus y und minus y heben sich auf."
        ):
            self.play(auftritt(kopf), run_time=0.5)
            self.warte_bis(0.25)
            self.play(self.y_faerben(HERVOR, mit_vorzeichen=True), FadeIn(rechnung), run_time=0.8)
            self.warte_bis(0.5)
            self.play(Create(strich), run_time=0.4)
            self.warte_bis(0.7)
            self.play(
                weg.animate.set_color(TEXT_SCHWACH), welle(oben[2], HERVOR), welle(unten[2], HERVOR),
                FadeIn(summe, shift=0.15 * DOWN),
                run_time=0.8,
            )
        with self.sprich("Fällt nichts weg, multiplizieren wir vorher eine oder beide Gleichungen mit geeigneten Zahlen."):
            self.play(auftritt(notiz), run_time=0.6)
        self.wait(0.4)
        self.abschnitt_ende(kopf, VGroup(schriftlich, notiz))

    def loesen(self) -> None:
        wege = legende(
            *[(text(wort, groesse=38, farbe=TEXT_LEISE), gl("5x", "=", "20")) for wort in self.WEGE],
            abstand=0.35,
        )
        ziel = gl("5x", "=", "20")
        x_ist = gl("x", "=", "4", farben={2: BLAU})
        ergebnis = VGroup(ziel, x_ist).arrange(DOWN, buff=0.4)
        self.tafel(wege, ergebnis, abstand=0.8)
        self.loesung = loesung = self.kopf("x=", "4", r"\quad y=", "5")
        loesung[1].set_color(BLAU)
        loesung[3].set_color(ROSE)
        with self.sprich("Jeder Weg führt auf 5 x gleich 20. Also x gleich 4."):
            self.play(LaggedStart(*[auftritt(zeile) for zeile in wege], lag_ratio=0.25), run_time=1.0)
            self.warte_bis(0.45)
            self.play(
                *[ReplacementTransform(zeile[1].copy(), ziel) for zeile in wege],
                *[zeile[0].animate.set_color(TEXT_SCHWACH) for zeile in wege],
                run_time=0.8,
            )
            self.warte_bis(0.75)
            self.play(auftritt(x_ist), run_time=0.5)
        self.wait(0.4)
        self.play(
            FadeOut(VGroup(wege, ziel), shift=0.25 * UP),
            ReplacementTransform(x_ist[:2], loesung[0]),
            ReplacementTransform(x_ist[2], loesung[1]),
            run_time=0.8,
        )

    def y_bestimmen(self) -> None:
        loesung = self.loesung
        kopf = titel("In Gleichung I einsetzen")
        einsatz = gl(r"2\cdot", "4", "+y=13", farben={1: BLAU})
        y_ist = gl("y", "=", "5", farben={2: ROSE})
        self.tafel(kopf, einsatz, y_ist, abstand=0.5)
        with self.sprich(
            "Das setzen wir in Gleichung 1 ein: 2 mal 4 plus y gleich 13. Also y gleich 5."
        ):
            self.play(
                auftritt(kopf),
                *[teil.animate(rate_func=rate_functions.there_and_back).scale(1.25) for teil in self.i],
                run_time=0.7,
            )
            self.warte_bis(0.2)
            self.play(Write(einsatz[0]), TransformFromCopy(loesung[1], einsatz[1]), Write(einsatz[2]), run_time=1.0)
            self.warte_bis(0.75)
            self.play(auftritt(y_ist), run_time=0.5)
        self.wait(0.6)
        self.play(
            FadeOut(VGroup(kopf, einsatz, y_ist[:2]), shift=0.25 * UP),
            ReplacementTransform(y_ist[2], loesung[3]),
            FadeIn(loesung[2]),
            run_time=0.9,
        )

    def zusammenfassen(self) -> None:
        def punkt(stichwort: str, erklaerung: str) -> VGroup:
            return VGroup(
                text(stichwort, groesse=40, gewicht=BOLD),
                text(erklaerung, groesse=32, farbe=TEXT_LEISE),
            ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)

        punkte = aufzaehlung(
            punkt("Gleichsetzungsverfahren", "beide nach y auflösen, gleichsetzen"),
            punkt("Einsetzungsverfahren", "eine nach y auflösen, einsetzen"),
            punkt("Additionsverfahren", "addieren, sodass y wegfällt"),
            abstand=0.55,
        )
        dann = text("Dann ausrechnen und einsetzen.", groesse=38)
        self.tafel(punkte, dann, abstand=0.7)
        with self.sprich(
            "Kurz gesagt: gleichsetzen, einsetzen oder addieren, bis nur noch eine Unbekannte übrig ist. "
            "Dann ausrechnen und einsetzen."
        ):
            for zeile, beginn in zip(punkte, (0.1, 0.25, 0.4)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
            self.warte_bis(0.75)
            self.play(auftritt(dann), run_time=0.5)
        self.wait(1.5)

    # ---------- Hilfen ----------
    def y_faerben(self, farbe: str, mit_vorzeichen: bool = False) -> Animation:
        """Färbt y (auf Wunsch mit Vorzeichen) in beiden Gleichungen auf der Bühne."""
        teile = VGroup(self.i[2], self.ii[2], *([self.i[1], self.ii[1]] if mit_vorzeichen else []))
        return teile.animate.set_color(farbe)

    def abschnitt_ende(self, *rest: Mobject) -> None:
        self.wait(0.6)
        self.play(FadeOut(VGroup(*rest), shift=0.25 * UP), self.y_faerben(TEXT, mit_vorzeichen=True), run_time=0.5)
