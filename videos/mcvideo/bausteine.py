"""Wiederkehrende Bildelemente der MatheChecks-Videos."""
from manim import (
    BOLD,
    DOWN,
    LEFT,
    NORMAL,
    RIGHT,
    SEMIBOLD,
    Circle,
    DecimalNumber,
    MathTex,
    Mobject,
    RoundedRectangle,
    SVGMobject,
    Text,
    VGroup,
    VMobject,
)

from . import theme as t


def text(inhalt: str, groesse: float = t.S_TEXT, farbe: str = t.TEXT, gewicht: str = NORMAL) -> Text:
    return Text(inhalt, font=t.SCHRIFT, font_size=groesse, color=farbe, weight=gewicht, line_spacing=1.0)


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


def ueberschrift(titel: str, farbe: str = t.AKZENT) -> Text:
    return einpassen(text(titel, groesse=t.S_SCHRITT, farbe=farbe, gewicht=SEMIBOLD), t.TAFEL_BREITE)


def stolperstein(hinweis: str) -> VGroup:
    """Fester Baustein für den typischen Fehler."""
    marke = text("Stolperstein", groesse=t.S_KLEIN, farbe=t.HINTERGRUND, gewicht=BOLD)
    feld = RoundedRectangle(
        width=marke.width + 0.5, height=marke.height + 0.32, corner_radius=0.16,
        color=t.HERVOR, fill_opacity=1, stroke_width=0,
    )
    marke.move_to(feld)
    block = VGroup(VGroup(feld, marke), text(hinweis, groesse=t.S_TEXT, farbe=t.HERVOR))
    block.arrange(DOWN, buff=0.25)
    return einpassen(block, t.TAFEL_BREITE)


def rezept(*zeilen: VMobject) -> VGroup:
    """Nummerierte Zusammenfassung der Schritte."""
    reihen = VGroup(*[VGroup(nummer(i), zeile).arrange(RIGHT, buff=0.35) for i, zeile in enumerate(zeilen, start=1)])
    reihen.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
    return einpassen(reihen, t.TAFEL_BREITE)


class Dezimalzahl(DecimalNumber):
    """Veränderliche Zahl mit Dezimalkomma."""

    def __init__(self, zahl: float = 0, stellen: int = 1, **kwargs: object) -> None:
        super().__init__(zahl, num_decimal_places=stellen, group_with_commas=False, **kwargs)

    def _get_num_string(self, number: float | complex) -> str:
        return super()._get_num_string(number).replace(".", ",")
