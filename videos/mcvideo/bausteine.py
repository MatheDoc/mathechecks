"""Wiederkehrende Bildelemente der MatheChecks-Videos."""
from collections.abc import Mapping

import numpy as np
from manim import (
    BOLD,
    DOWN,
    LEFT,
    NORMAL,
    ORIGIN,
    RIGHT,
    SEMIBOLD,
    UP,
    Animation,
    AnimationGroup,
    ArcBetweenPoints,
    Circle,
    Create,
    DecimalNumber,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    RoundedRectangle,
    SVGMobject,
    Text,
    Transform,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    interpolate,
    rate_functions,
)

from . import theme as t


def text(
    inhalt: str,
    groesse: float = t.S_TEXT,
    farbe: str = t.TEXT,
    gewicht: str = NORMAL,
    farben: dict[str, str] | None = None,
) -> Text:
    """Text in der Hausschrift. farben färbt einzelne Wörter, z. B. {"Tangente": HERVOR}."""
    return Text(inhalt, font=t.SCHRIFT, font_size=groesse, color=farbe, weight=gewicht, line_spacing=1.0, t2c=farben)


def formel(*tex: str, groesse: float = t.S_FORMEL, farbe: str = t.TEXT) -> MathTex:
    return MathTex(*tex, font_size=groesse, color=farbe)


def einpassen(mob: Mobject, breite: float | None = None, hoehe: float | None = None) -> Mobject:
    """Verkleinert ein Objekt, bis es in die angegebene Breite und Höhe passt."""
    if breite is not None and mob.width > breite:
        mob.scale_to_fit_width(breite)
    if hoehe is not None and mob.height > hoehe:
        mob.scale_to_fit_height(hoehe)
    return mob


def logo(hoehe: float = 0.7, farbe: str = t.TEXT) -> SVGMobject:
    bild = SVGMobject(str(t.REPO / "assets" / "img" / "logo-dark-mode.svg"), height=hoehe)
    bild.set_fill(farbe, opacity=1).set_stroke(width=0)
    return bild


def nummer(nr: int, durchmesser: float = 0.62) -> VGroup:
    kreis = Circle(radius=durchmesser / 2, color=t.MARKE, fill_opacity=1, stroke_width=0)
    ziffer = text(str(nr), groesse=t.S_SCHRITT * 0.8, gewicht=BOLD)
    ziffer.move_to(kreis)
    return VGroup(kreis, ziffer)


def schritt(nr: int, titel: str) -> VGroup:
    """Überschrift eines Rechenschritts: Nummer in Markenfarbe und Titel."""
    zeile = VGroup(nummer(nr), text(titel, groesse=t.S_SCHRITT, gewicht=SEMIBOLD))
    zeile.arrange(RIGHT, buff=0.28)
    return einpassen(zeile, t.TAFEL_BREITE)


def frage(*zeilen: str, zusatz: str | None = None) -> VGroup:
    """Einstiegsfrage in großer weißer Schrift, eine Zeile je Argument; zusatz steht kleiner darunter."""
    block = VGroup(*[text(zeile, groesse=t.S_GROSS, gewicht=BOLD) for zeile in zeilen])
    if zusatz:
        block.add(text(zusatz, groesse=36, farbe=t.TEXT_LEISE, gewicht=SEMIBOLD))
    block.arrange(DOWN, buff=0.3)
    return einpassen(block, t.TAFEL_BREITE)


def reihe(*teile: Mobject, abstand: float = 0.25) -> VGroup:
    """Setzt Formeln und Wörter nebeneinander in eine Zeile."""
    return VGroup(*teile).arrange(RIGHT, buff=abstand)


def legende(*paare: tuple[Mobject, Mobject], abstand: float = 0.4) -> VGroup:
    """Zweispaltige Erklärung: links das Zeichen, rechts seine Bedeutung, beide Spalten bündig."""
    spalte = max(zeichen.width for zeichen, _ in paare)
    zeilen = VGroup()
    for zeichen, bedeutung in paare:
        zeichen.move_to(ORIGIN)
        bedeutung.next_to(spalte / 2 * RIGHT, RIGHT, buff=0.3)
        zeile = VGroup(zeichen, bedeutung)
        if len(zeilen) > 0:
            zeile.shift((zeilen[-1].get_bottom()[1] - abstand - zeile.get_top()[1]) * UP)
        zeilen.add(zeile)
    return zeilen


def kurzfassung(*zeilen: Mobject) -> VGroup:
    """Nummerierte Zusammenfassung der Schritte am Ende."""
    reihen = VGroup(*[reihe(nummer(i), zeile, abstand=0.35) for i, zeile in enumerate(zeilen, start=1)])
    reihen.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
    return einpassen(reihen, t.TAFEL_BREITE)


def aufzaehlung(*zeilen: Mobject | tuple[Mobject, Mobject], abstand: float = 0.4) -> VGroup:
    """Übersicht ohne Reihenfolge: wie kurzfassung, aber mit Punkten in der Stimmungsfarbe statt Nummern.

    Eine Zeile kann ein Paar (Stichwort, Inhalt) sein; die Inhalte stehen dann bündig untereinander.
    """
    paare = [zeile if isinstance(zeile, tuple) else (zeile, None) for zeile in zeilen]
    spalte = max((stichwort.width for stichwort, inhalt in paare if inhalt is not None), default=0)
    reihen = VGroup()
    for stichwort, inhalt in paare:
        punkt = Circle(radius=0.11, color=t.MARKE, fill_opacity=1, stroke_width=0)
        stichwort.next_to(punkt, RIGHT, buff=0.28)
        zeile = VGroup(punkt, stichwort)
        if inhalt is not None:
            zeile.add(inhalt.next_to(punkt, RIGHT, buff=0.28 + spalte + 0.3))
        reihen.add(zeile)
    reihen.arrange(DOWN, buff=abstand, aligned_edge=LEFT)
    return einpassen(reihen, t.TAFEL_BREITE)


def schein(linie: VMobject) -> VGroup:
    """Weicher Lichtschein um eine Linie; vor der Linie einblenden."""
    breite = linie.get_stroke_width()
    return VGroup(*[
        linie.copy().set_stroke(width=breite * faktor, opacity=deckkraft)
        for faktor, deckkraft in ((5, 0.05), (2.8, 0.09))
    ])


def lichtpunkt(pfad: VMobject) -> Animation:
    """Lichtpunkt in der Stimmungsfarbe, der einen Pfad entlangläuft und am Ende verblasst."""
    kurven = pfad.get_num_curves()
    hof = Circle(radius=0.3, color=t.MARKE, fill_opacity=0.3, stroke_width=0)
    kern = Dot(radius=0.1, color=t.MARKE)

    def folge(punkt: Mobject, anteil: float) -> None:
        stelle = min(anteil * kurven, kurven - 1e-6)
        punkt.move_to(pfad.get_nth_curve_function(int(stelle))(stelle % 1))
        sichtbar = min(1.0, (1 - anteil) / 0.15)
        hof.set_fill(opacity=0.3 * sichtbar)
        kern.set_fill(opacity=sichtbar)

    return UpdateFromAlphaFunc(VGroup(hof, kern), folge, remover=True)


def zeichnen(linie: VMobject) -> list[Animation]:
    """Zeichnet eine Linie mit Lichtschein; ein Lichtpunkt läuft an der Spitze mit."""
    return [*[Create(glanz) for glanz in schein(linie)], Create(linie), lichtpunkt(linie.copy())]


def lichthof(radius: float, farbe: str, staerke: float = 1.0) -> VGroup:
    """Nach außen auslaufender Farbfleck, etwa hinter dem Logo."""
    stufen = 24
    return VGroup(*[
        Circle(radius=radius * i / stufen, color=farbe, fill_opacity=0.011 * staerke, stroke_width=0)
        for i in range(1, stufen + 1)
    ])


def auftritt(mob: Mobject) -> Animation:
    """Einblenden mit leichtem Anheben; Standard für Text und Überschriften."""
    return FadeIn(mob, shift=0.25 * UP, scale=0.94, rate_func=rate_functions.ease_out_cubic)


def welle(ort: object, farbe: str) -> Animation:
    """Ring, der sich von einem Punkt ausbreitet und verblasst: „hier passiert es“."""
    ring = Circle(radius=0.14, color=farbe, stroke_width=5).move_to(ort)
    return FadeOut(ring, scale=4.5, rate_func=rate_functions.ease_out_cubic)


class _Leiste(VGroup):
    """Reihe nummerierter Felder mit Beschriftung; einzelne Felder lassen sich hervorheben."""

    def __init__(self, werte: range, titel: str, rund: bool, breite: float) -> None:
        super().__init__()
        self.werte = list(werte)
        raster = breite / len(self.werte)
        if rund:
            form = Circle(radius=0.43 * raster, fill_color=t.FELD, fill_opacity=1, stroke_width=0)
        else:
            form = RoundedRectangle(
                width=0.86 * raster, height=0.6, corner_radius=0.07,
                fill_color=t.FELD, fill_opacity=1, stroke_width=0,
            )
        self.felder = VGroup(*[form.copy().move_to([i * raster, 0, 0]) for i in range(len(self.werte))])
        self.zahlen = VGroup(*[
            text(str(wert), groesse=17, farbe=t.TEXT_LEISE).next_to(feld, DOWN, buff=0.14)
            for wert, feld in zip(self.werte, self.felder)
        ])
        self.titel = text(titel, groesse=22, farbe=t.TEXT_LEISE).next_to(self.felder, UP, buff=0.22)
        self.add(self.titel, self.felder, self.zahlen)

    def aufbau(self) -> list[Animation]:
        """Die Leiste entsteht von links nach rechts, ein Lichtpunkt läuft mit."""
        spur = Line(self.felder[0].get_center(), self.felder[-1].get_center())
        paare = [VGroup(feld, zahl) for feld, zahl in zip(self.felder, self.zahlen)]
        return [
            FadeIn(self.titel),
            LaggedStart(*[FadeIn(paar, scale=0.6) for paar in paare], lag_ratio=0.06),
            lichtpunkt(spur),
        ]

    def _hervorheben(self, aktiv: set[int], betont: set[int], farbe: str) -> Animation:
        """Färbt die Felder der Werte in aktiv; die Zahlen der Werte in betont bekommen ebenfalls die Farbe."""
        innen, aussen = [], []
        for wert, feld, zahl in zip(self.werte, self.felder, self.zahlen):
            if wert in aktiv:
                innen += [feld.animate.set_fill(farbe), zahl.animate.set_color(farbe if wert in betont else t.TEXT)]
            else:
                aussen += [feld.animate.set_fill(t.FELD_LEISE), zahl.animate.set_color(t.TEXT_SCHWACH)]
        return AnimationGroup(*aussen, LaggedStart(*innen, lag_ratio=0.05))

    def neutral(self) -> Animation:
        """Nimmt die Hervorhebung zurück."""
        return AnimationGroup(
            *[feld.animate.set_fill(t.FELD) for feld in self.felder],
            *[zahl.animate.set_color(t.TEXT_LEISE) for zahl in self.zahlen],
        )


class Zahlenstrahl(_Leiste):
    """Die möglichen Anzahlen 0 bis n als Leiste aus Feldern."""

    def __init__(self, n: int, titel: str = "Anzahl", breite: float = t.BUEHNE_BREITE) -> None:
        super().__init__(range(n + 1), titel, rund=False, breite=breite)

    def bereich(self, *grenzen: tuple[int, int], farbe: str = t.HERVOR) -> Animation:
        """Hebt einen oder mehrere Bereiche (von, bis) hervor, die Grenzen auch in der Beschriftung."""
        aktiv = {k for von, bis in grenzen for k in range(von, bis + 1)}
        return self._hervorheben(aktiv, {k for paar in grenzen for k in paar}, farbe)

    def ort(self, wert: float) -> np.ndarray:
        """Punkt an der Oberkante der Leiste zum Wert, auch zwischen zwei Anzahlen (etwa 2,6)."""
        return interpolate(self.felder[0].get_top(), self.felder[-1].get_top(), wert / (len(self.felder) - 1))


class Versuche(_Leiste):
    """Die Versuche 1 bis n als Reihe aus Kreisen: Hier geht es um bestimmte Versuche, nicht um eine Anzahl."""

    def __init__(self, n: int, titel: str = "Versuch", breite: float = t.BUEHNE_BREITE) -> None:
        super().__init__(range(1, n + 1), titel, rund=True, breite=breite)

    def markiere(self, *nummern: int, farbe: str = t.TUERKIS) -> Animation:
        """Hebt einzelne Versuche hervor."""
        return self._hervorheben(set(nummern), set(nummern), farbe)


def _zahl(wert: float) -> str:
    """Zahl als TeX mit Dezimalkomma."""
    return f"{wert:g}".replace(".", "{,}")


class ErweiterteMatrix(VGroup):
    """Erweiterte Koeffizientenmatrix (A | b). Rechts stehen die Zeilennamen I, II, III und die Umformungen.

    breiteste_umformung: längste Umformung des Videos als TeX. Sie reserviert rechts Platz, damit
    die Matrix beim Einpassen nicht zu groß wird.
    """

    NAMEN = ("I", "II", "III", "IV", "V")

    def __init__(
        self,
        zeilen: list[list[float]],
        breiteste_umformung: str | None = None,
        groesse: float = t.S_FORMEL,
        spalte: float = 1.0,
        zeile: float = 0.95,
    ) -> None:
        super().__init__()
        self._groesse = groesse
        self._spalte = spalte
        anzahl = len(zeilen[0])
        xs = [j * spalte for j in range(anzahl - 1)] + [(anzahl - 1) * spalte + 0.3]
        ys = [-i * zeile for i in range(len(zeilen))]
        self.eintraege = [
            [formel(_zahl(wert), groesse=groesse).move_to([x, y, 0]) for wert, x in zip(werte, xs)]
            for werte, y in zip(zeilen, ys)
        ]
        oben, unten = ys[0] + 0.5, ys[-1] - 0.5
        links, rechts = xs[0] - 0.6, xs[-1] + 0.6
        self.klammern = VGroup(
            ArcBetweenPoints(np.array([links, oben, 0]), np.array([links, unten, 0]), angle=0.6),
            ArcBetweenPoints(np.array([rechts, unten, 0]), np.array([rechts, oben, 0]), angle=0.6),
        ).set_stroke(t.TEXT, width=3.5)
        mitte = (xs[-2] + xs[-1]) / 2
        self.strich = Line([mitte, oben - 0.12, 0], [mitte, unten + 0.12, 0], color=t.ACHSE, stroke_width=2.5)
        self.namen = [
            formel(self.zeilenname(i), groesse=0.8 * groesse, farbe=t.TEXT_LEISE).move_to([rechts + 0.5, y, 0], aligned_edge=LEFT)
            for i, y in enumerate(ys)
        ]
        self.add(self.klammern, self.strich, *[eintrag for werte in self.eintraege for eintrag in werte], *self.namen)
        if breiteste_umformung:
            platz = formel(breiteste_umformung, groesse=0.8 * groesse).move_to(self.namen[0], aligned_edge=LEFT)
            self.add(platz.set_opacity(0))

    @classmethod
    def zeilenname(cls, i: int) -> str:
        """Name der Zeile i als TeX (aufrechte römische Zahl), auch als Baustein für Umformungen."""
        return rf"\mathrm{{{cls.NAMEN[i]}}}"

    def _massstab(self) -> float:
        """Aktuelle Größe im Verhältnis zur Größe beim Anlegen."""
        return (self.eintraege[0][1].get_x() - self.eintraege[0][0].get_x()) / self._spalte

    def zeile(self, i: int) -> VGroup:
        return VGroup(*self.eintraege[i])

    def zahlenzeile(self, werte: list[float], y: float, farben: dict[int, str] | None = None) -> VGroup:
        """Zahlen in den Spalten der Matrix auf der Höhe y, etwa für eine Nebenrechnung darunter."""
        groesse = self._groesse * self._massstab()
        return VGroup(*[
            formel(_zahl(wert), groesse=groesse, farbe=(farben or {}).get(j, t.TEXT)).move_to([oben.get_x(), y, 0])
            for j, (wert, oben) in enumerate(zip(werte, self.eintraege[0]))
        ])

    def randnotiz(self, tex: str, y: float, farbe: str = t.TEXT_LEISE) -> MathTex:
        """Beschriftung in der Spalte der Zeilennamen auf der Höhe y."""
        notiz = formel(tex, groesse=0.8 * self._groesse * self._massstab(), farbe=farbe)
        return notiz.move_to([self.namen[0].get_left()[0], y, 0], aligned_edge=LEFT)

    def umformung(self, i: int, tex: str) -> Animation:
        """Schreibt eine Umformung an die Zeile i, z. B. zeilenname(1) + "-4\\cdot" + zeilenname(0)."""
        return Transform(self.namen[i], self.randnotiz(tex, self.namen[i].get_y(), t.HERVOR))

    def benennen(self, i: int) -> Animation:
        """Setzt an die Zeile i wieder ihren Namen."""
        return Transform(self.namen[i], self.randnotiz(self.zeilenname(i), self.namen[i].get_y()))

    def umformen(self, i: int, werte: list[float], farben: dict[int, str] | None = None) -> Animation:
        """Ersetzt die Zeile i durch neue Werte; farben färbt einzelne Spalten."""
        neu = self.zahlenzeile(werte, self.eintraege[i][0].get_y(), farben)
        return AnimationGroup(*[Transform(alt, ziel) for alt, ziel in zip(self.eintraege[i], neu)])

    def betonen(self, i: int) -> Animation:
        """Die Zeile i pulsiert kurz: „um diese Zeile geht es“."""
        return AnimationGroup(*[
            eintrag.animate(rate_func=rate_functions.there_and_back).scale(1.3) for eintrag in self.eintraege[i]
        ])


class Baumdiagramm(VGroup):
    """Zweistufiges Baumdiagramm zu zwei Ereignissen A und B, aufgebaut wie auf der Website.

    Äste und Pfadenden heißen nach ihrem Pfad: "A" und "nA" (erste Stufe), "AB", "AnB", "nAB" und
    "nAnB" (zweite Stufe und Pfadenden). An jedem Ast steht seine Wahrscheinlichkeit, rechts neben
    jedem Pfadende das Produkt.
    """

    PFADE = ("AB", "AnB", "nAB", "nAnB")

    def __init__(self, pa: float, pba: float, pbna: float, breite: float = t.BUEHNE_BREITE, hoehe: float = 4.3) -> None:
        super().__init__()
        aeste = {"A": pa, "nA": 1 - pa, "AB": pba, "AnB": 1 - pba, "nAB": pbna, "nAnB": 1 - pbna}
        hoehen = {"A": 0.75, "nA": 0.25, "AB": 0.875, "AnB": 0.625, "nAB": 0.375, "nAnB": 0.125}
        namen = {"A": "A", "nA": r"\overline{A}", "AB": "B", "AnB": r"\overline{B}", "nAB": "B", "nAnB": r"\overline{B}"}
        orte = {"": np.array([0, hoehe / 2, 0])}
        for ast, anteil in hoehen.items():
            orte[ast] = np.array([(0.36 if ast in ("A", "nA") else 0.72) * breite, anteil * hoehe, 0])

        self.wurzel = Dot(orte[""], radius=0.07, color=t.ACHSE)
        self.kanten, self.werte, self.kreise, self.namen, self.enden = {}, {}, {}, {}, {}
        for ast, p in aeste.items():
            start, ziel = orte[self._vorgaenger(ast)], orte[ast]
            richtung = (ziel - start) / np.linalg.norm(ziel - start)
            aussen = np.array([-richtung[1], richtung[0], 0]) * (1 if richtung[1] > 0 else -1)
            self.kanten[ast] = Line(start, ziel, color=t.ACHSE, stroke_width=3)
            self.werte[ast] = formel(_zahl(p), groesse=38).move_to((start + ziel) / 2 + 0.38 * aussen)
            self.kreise[ast] = Circle(
                radius=0.36, stroke_color=t.ACHSE, stroke_width=3, fill_color=t.FELD, fill_opacity=1,
            ).move_to(ziel).set_z_index(1)
            self.namen[ast] = formel(namen[ast], groesse=36).move_to(ziel).set_z_index(2)
        for pfad in self.PFADE:
            produkt = aeste[self._vorgaenger(pfad)] * aeste[pfad]
            self.enden[pfad] = formel(_zahl(produkt), groesse=42).next_to(self.kreise[pfad], RIGHT, buff=0.3)
        self.add(
            *self.kanten.values(), self.wurzel, *self.kreise.values(), *self.namen.values(),
            *self.werte.values(), *self.enden.values(),
        )

    @staticmethod
    def _vorgaenger(ast: str) -> str:
        if ast in ("A", "nA"):
            return ""
        return "nA" if ast.startswith("n") else "A"

    def aufbau(self) -> list[Animation]:
        """Der Baum wächst von links nach rechts, ein Lichtpunkt läuft den obersten Pfad entlang."""

        def stufe(aeste: tuple[str, ...]) -> Animation:
            return AnimationGroup(
                *[Create(self.kanten[ast]) for ast in aeste],
                *[FadeIn(self.werte[ast]) for ast in aeste],
                *[FadeIn(VGroup(self.kreise[ast], self.namen[ast]), scale=0.6) for ast in aeste],
            )

        spur = VMobject().set_points_as_corners(
            [self.kanten["A"].get_start(), self.kanten["A"].get_end(), self.kanten["AB"].get_end()]
        )
        enden = FadeIn(VGroup(*self.enden.values()), shift=0.2 * RIGHT)
        return [
            FadeIn(self.wurzel),
            LaggedStart(stufe(("A", "nA")), stufe(self.PFADE), enden, lag_ratio=0.6),
            lichtpunkt(spur),
        ]

    def markiere(self, aeste: Mapping[str, str] | None = None, enden: Mapping[str, str] | None = None) -> Animation:
        """Färbt Äste (mit ihrem Wert) und Pfadenden, jeweils Name → Farbe; alles Übrige tritt zurück.

        Ohne Angaben kehrt der Baum in den Grundzustand zurück.
        """
        aeste, enden = aeste or {}, enden or {}
        ruhig = t.TEXT_LEISE if aeste or enden else t.TEXT
        schritte = []
        for ast in self.kanten:
            farbe = aeste.get(ast)
            schritte += [
                self.kanten[ast].animate.set_stroke(farbe or t.ACHSE, width=5 if farbe else 3),
                self.werte[ast].animate.set_color(farbe or ruhig),
                self.kreise[ast].animate.set_stroke(farbe or enden.get(ast) or t.ACHSE),
            ]
        schritte += [self.enden[pfad].animate.set_color(enden.get(pfad) or ruhig) for pfad in self.PFADE]
        return AnimationGroup(*schritte)

    def betone(self, *aeste: str) -> Animation:
        """Die Knoten am Ende der genannten Äste pulsieren kurz."""
        return AnimationGroup(*[
            teil.animate(rate_func=rate_functions.there_and_back).scale(1.35)
            for ast in aeste for teil in (self.kreise[ast], self.namen[ast])
        ])


class Dezimalzahl(DecimalNumber):
    """Veränderliche Zahl mit Dezimalkomma."""

    def __init__(self, zahl: float = 0, stellen: int = 1, **kwargs: object) -> None:
        super().__init__(zahl, num_decimal_places=stellen, group_with_commas=False, **kwargs)

    def _get_num_string(self, number: float | complex) -> str:
        return super()._get_num_string(number).replace(".", ",")
