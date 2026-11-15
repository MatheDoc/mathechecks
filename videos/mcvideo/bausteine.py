"""Wiederkehrende Bildelemente der MatheChecks-Videos."""
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


def frage(*zeilen: str) -> VGroup:
    """Einstiegsfrage in großer weißer Schrift, eine Zeile je Argument."""
    block = VGroup(*[text(zeile, groesse=t.S_GROSS, gewicht=BOLD) for zeile in zeilen])
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


class Dezimalzahl(DecimalNumber):
    """Veränderliche Zahl mit Dezimalkomma."""

    def __init__(self, zahl: float = 0, stellen: int = 1, **kwargs: object) -> None:
        super().__init__(zahl, num_decimal_places=stellen, group_with_commas=False, **kwargs)

    def _get_num_string(self, number: float | complex) -> str:
        return super()._get_num_string(number).replace(".", ",")
