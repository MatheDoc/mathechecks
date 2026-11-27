"""Wiederkehrende Bildelemente der MatheChecks-Videos."""
import math
import re
from collections.abc import Iterable, Mapping

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
    DashedLine,
    DecimalNumber,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    GrowFromEdge,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    Rectangle,
    ReplacementTransform,
    TransformFromCopy,
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


def betrag(*tex: str, groesse: float = t.S_FORMEL, farbe: str = t.TEXT) -> VGroup:
    """Geldbetrag: Formel, die mit einer Ziffer endet, und dahinter das Eurozeichen in der Hausschrift.

    LaTeX setzt hier kein Eurozeichen. Ergebnis ist die Gruppe (Formel, Eurozeichen).
    """
    zahl = formel(*tex, groesse=groesse, farbe=farbe)
    ziffer = zahl[-1][-1]
    zeichen = text("€", groesse=groesse, farbe=farbe).scale_to_fit_height(ziffer.height)
    zeichen.next_to(zahl, RIGHT, buff=0.4 * ziffer.height).align_to(ziffer, DOWN)
    return VGroup(zahl, zeichen)


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


def _grundlinie(teil: Mobject) -> float:
    """Höhe der Schriftgrundlinie eines Teils. Unterlängen zählen nicht mit: bei Text g, p, y …,
    bei Formeln Indizes (H_0) und das Dezimalkomma (0{,}2)."""
    if isinstance(teil, MathTex):
        # LaTeX setzt ein vorangestelltes x auf dieselbe Grundlinie; dessen Unterkante ist die Grundlinie.
        probe = MathTex(r"\mathrm{x}", teil.get_tex_string())
        massstab = teil.height / probe[1].height
        return teil.get_bottom()[1] + (probe[0].get_bottom()[1] - probe[1].get_bottom()[1]) * massstab
    if not isinstance(teil, Text):
        return teil.get_bottom()[1]
    ohne_unterlaenge = Text(
        re.sub(r"[gjpqy,;()]", "o", teil.text), font=teil.font, font_size=teil.font_size, weight=teil.weight,
    )
    return teil.get_top()[1] - (ohne_unterlaenge.get_top()[1] - ohne_unterlaenge.get_bottom()[1])


def reihe(*teile: Mobject, abstand: float = 0.25, grundlinie: bool = False) -> VGroup:
    """Setzt Formeln und Wörter nebeneinander in eine Zeile.

    grundlinie: Teile sitzen auf einer gemeinsamen Schriftgrundlinie statt mittig; nötig, wenn eine kleine
    Formel (etwa a') in einem Satz steht. Nur für einzeilige Texte.
    """
    zeile = VGroup(*teile).arrange(RIGHT, buff=abstand)
    if grundlinie:
        erste = _grundlinie(teile[0])
        for teil in teile[1:]:
            teil.shift((erste - _grundlinie(teil)) * UP)
    return zeile


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


def tabelle(*zeilen: tuple[Mobject, ...], abstand: tuple[float, float] = (0.9, 0.45)) -> VGroup:
    """Zellen in Zeilen und Spalten, jede Spalte mittig ausgerichtet; Ergebnis ist die Gruppe der Zeilen.

    abstand: (zwischen den Spalten, zwischen den Zeilen).
    """
    spalten = len(zeilen[0])
    zellen = VGroup(*[zelle for zeile in zeilen for zelle in zeile])
    zellen.arrange_in_grid(rows=len(zeilen), cols=spalten, buff=abstand)
    return VGroup(*[VGroup(*zellen[i * spalten:(i + 1) * spalten]) for i in range(len(zeilen))])


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


class Histogramm(VGroup):
    """Histogramm der Binomialverteilung B(n; p) für die Anzahlen 0 bis bis.

    Rechts oben steht der Wert von p, rechts neben der Grundlinie „… n“, wenn nicht alle Anzahlen zu sehen sind.
    Beschriftet sind die Anzahlen in zahlen; beim Färben eines Bereichs kommen seine Grenzen dazu.
    y_max legt die Höhe fest, damit beim Wechsel von p (zu) die Balken vergleichbar bleiben.
    p_tex: Anzeige von p, falls sie vom Wert abweicht (etwa "p_0=\\,?").
    kumuliert: Balkenhöhe P(X ≤ k) statt P(X = k).
    y_werte: Hilfslinien mit Beschriftung links (etwa (0.1, 0.2, 0.3)), damit sich Balkenhöhen ablesen lassen;
    ablesen(k) zieht dann eine gestrichelte Linie vom Balken zur Beschriftung.
    """

    def __init__(
        self,
        n: int,
        p: float,
        bis: int,
        y_max: float,
        zahlen: tuple[int, ...] = (0, 5, 10, 15, 20),
        breite: float = t.BUEHNE_BREITE,
        hoehe: float = 3.2,
        p_tex: str | None = None,
        kumuliert: bool = False,
        y_werte: tuple[float, ...] = (),
    ) -> None:
        super().__init__()
        self.n, self.p, self.y_max, self.hoehe = n, p, y_max, hoehe
        self.kumuliert = kumuliert
        self.werte = list(range(bis + 1))
        self._zahlen = set(zahlen)
        if y_werte:
            breite -= 0.9  # Platz für die Beschriftung der Hilfslinien
        raster = breite / (len(self.werte) + (1.2 if bis < n else 0))
        self.grundlinie = Line([-0.5 * raster, 0, 0], [(bis + 0.5) * raster, 0, 0], color=t.ACHSE, stroke_width=3)
        self.hilfslinien = VGroup()
        for y in y_werte:
            hoehe_y = y / y_max * hoehe
            linie = Line([-0.5 * raster, hoehe_y, 0], [(bis + 0.5) * raster, hoehe_y, 0],
                         color=t.FELD, stroke_width=1.5)
            zahl = text(f"{y:g}".replace(".", ","), groesse=20, farbe=t.TEXT_LEISE).next_to(linie, LEFT, buff=0.12)
            self.hilfslinien.add(VGroup(linie, zahl))
        self.add(self.hilfslinien)
        self._laenge = self.grundlinie.get_length()
        self.balken = VGroup(*[
            Rectangle(
                width=0.82 * raster, height=self._hoehe(k, p), fill_color=t.FELD, fill_opacity=1, stroke_width=0,
            ).move_to([k * raster, 0, 0], aligned_edge=DOWN)
            for k in self.werte
        ])
        groesse = 20 if raster > 0.3 else 16
        self.zahlen = VGroup(*[
            text(str(k), groesse=groesse, farbe=t.TEXT_LEISE).next_to(self.grundlinie, DOWN, buff=0.14).set_x(k * raster)
            for k in self.werte
        ])
        for k, zahl in zip(self.werte, self.zahlen):
            if k not in self._zahlen:
                zahl.set_opacity(0)
        self.add(self.grundlinie, self.balken, self.zahlen)
        if bis < n:
            self.ende = text(f"… {n}", groesse=groesse, farbe=t.TEXT_LEISE)
            self.ende.next_to(self.grundlinie, RIGHT, buff=0.12).align_to(self.zahlen[0], DOWN)
            self.add(self.ende)
        self.p_text = self._p_text(p_tex or f"p={_zahl(p)}")
        self.add(self.p_text)

    def _massstab(self) -> float:
        """Aktuelle Größe im Verhältnis zur Größe beim Anlegen (auf_buehne verkleinert das Histogramm)."""
        return self.grundlinie.get_length() / self._laenge

    def wahrscheinlichkeit(self, k: int, p: float | None = None) -> float:
        """Höhe des Balkens k als Wahrscheinlichkeit: P(X = k), bei kumuliert P(X ≤ k)."""
        p = self.p if p is None else p
        werte = range(k + 1) if self.kumuliert else (k,)
        return sum(math.comb(self.n, i) * p**i * (1 - p) ** (self.n - i) for i in werte)

    def _hoehe(self, k: int, p: float) -> float:
        hoehe = self.wahrscheinlichkeit(k, p) / self.y_max * self.hoehe
        return max(hoehe * self._massstab(), 0.002)

    def _p_text(self, tex: str) -> MathTex:
        massstab = self._massstab()
        return formel(tex, groesse=40 * massstab).move_to(
            [self.grundlinie.get_right()[0], self.grundlinie.get_y() + self.hoehe * massstab, 0],
            aligned_edge=UP + RIGHT,
        )

    def aufbau(self) -> list[Animation]:
        """Die Balken wachsen von links nach rechts aus der Grundlinie, ein Lichtpunkt läuft mit."""
        sichtbar = [zahl for k, zahl in zip(self.werte, self.zahlen) if k in self._zahlen]
        return [
            Create(self.grundlinie),
            *([FadeIn(self.hilfslinien)] if len(self.hilfslinien) else []),
            LaggedStart(*[GrowFromEdge(balken, DOWN) for balken in self.balken], lag_ratio=0.04),
            FadeIn(VGroup(*sichtbar, *([self.ende] if hasattr(self, "ende") else []), self.p_text)),
            lichtpunkt(self.grundlinie.copy()),
        ]

    def faerbe(self, *bereiche: tuple[int, int, str]) -> Animation:
        """Färbt Bereiche (von, bis, Farbe) samt ihren Grenzen in der Beschriftung; übrige Balken treten zurück.

        Ohne Angaben kehrt das Histogramm in den Grundzustand zurück.
        """
        farben: dict[int, str] = {}
        grenzen: dict[int, str] = {}
        for von, bis, farbe in bereiche:
            for k in range(von, bis + 1):
                farben[k] = farbe
            grenzen[von] = grenzen[bis] = farbe
        schritte = []
        for k, balken, zahl in zip(self.werte, self.balken, self.zahlen):
            if not bereiche:
                fuellung = t.FELD
            else:
                fuellung = farben.get(k, t.FELD_LEISE)
            schritte.append(balken.animate.set_fill(fuellung))
            if k in grenzen:
                schritte.append(zahl.animate.set_color(grenzen[k]).set_opacity(1))
            elif k in self._zahlen and not any(abs(k - g) <= 1 for g in grenzen):
                schritte.append(zahl.animate.set_color(t.TEXT_LEISE).set_opacity(1))
            else:
                schritte.append(zahl.animate.set_opacity(0))
        return AnimationGroup(*schritte)

    def zu(self, p: float, p_tex: str | None = None) -> Animation:
        """Wechselt zur Verteilung mit einem anderen p; die Färbung bleibt."""
        self.p = p
        neu = self._p_text(p_tex or f"p={_zahl(p)}")
        alt, self.p_text = self.p_text, neu
        self.remove(alt).add(neu)
        return AnimationGroup(
            *[
                balken.animate.stretch_to_fit_height(self._hoehe(k, p), about_edge=DOWN)
                for k, balken in zip(self.werte, self.balken)
            ],
            FadeOut(alt),
            FadeIn(neu),
        )

    def ort(self, k: int) -> np.ndarray:
        """Oberkante des Balkens zur Anzahl k."""
        return self.balken[k].get_top()

    def ablesen(self, k: int, farbe: str = t.HERVOR) -> DashedLine:
        """Gestrichelte Linie von der Oberkante des Balkens k waagerecht zur Beschriftung der Hilfslinien."""
        oben = self.balken[k].get_top()
        links = np.array([self.grundlinie.get_left()[0], oben[1], 0])
        return DashedLine(oben, links, color=farbe, stroke_width=3, dash_length=0.08)


class Zeitstrahl(VGroup):
    """Zeitstrahl mit zwei Zeitpunkten: links der frühere, rechts der spätere.

    Sechs Plätze nehmen Angaben auf. Über dem Strahl steht die Zeit ("frueher", "dauer", "spaeter"),
    darunter stehen Beträge und Zins ("anfang", "zins", "ende"). Die äußeren Angaben schließen bündig
    mit den Enden des Strahls ab, die mittleren stehen mittig. Eine Angabe unter dem Strahl darf
    mehrzeilig sein, etwa der Name einer Größe und darunter ihr Wert.
    """

    # Name: (Anteil der Strahllänge, über dem Strahl[, Bezugspunkt der Angabe]). Der Bezugspunkt (0 links,
    # 0,5 Mitte, 1 rechts) liegt an der Stelle; ohne Angabe ist er gleich dem Anteil (außen bündig, innen mittig).
    _PLAETZE: dict[str, tuple] = {
        "frueher": (0.0, True), "dauer": (0.5, True), "spaeter": (1.0, True),
        "anfang": (0.0, False), "zins": (0.5, False), "ende": (1.0, False),
    }

    def __init__(self, breite: float = t.BUEHNE_BREITE, abstand: float = 0.32, **angaben: Mobject) -> None:
        super().__init__()
        self._abstand = abstand
        radius = 0.11
        self.strahl = Line([-breite / 2 + radius, 0, 0], [breite / 2, 0, 0], color=t.ACHSE, stroke_width=4)
        self.strahl.add_tip(tip_length=0.26, tip_width=0.26)
        self.beginn = Dot(self.strahl.get_start(), radius=radius, color=t.ACHSE)
        self.angaben: dict[str, Mobject] = {}
        self.add(self.strahl, self.beginn)
        for platz, angabe in angaben.items():
            self._setze(platz, angabe)

    def _setze(self, platz: str, angabe: Mobject) -> None:
        """Stellt eine Angabe an ihren Platz: oben auf gemeinsamer Grundlinie, unten mit gemeinsamer Oberkante."""
        anteil, oben, *bezug = self._PLAETZE[platz]
        links, rechts, y = self.beginn.get_left()[0], self.strahl.get_end()[0], self.beginn.get_y()
        if oben:
            angabe.shift((y + self._abstand - _grundlinie(angabe)) * UP)
        else:
            angabe.shift((y - self._abstand - angabe.get_top()[1]) * UP)
        stelle = interpolate(angabe.get_left()[0], angabe.get_right()[0], bezug[0] if bezug else anteil)
        angabe.shift((interpolate(links, rechts, anteil) - stelle) * RIGHT)
        self.angaben[platz] = angabe
        self.add(angabe)

    def _entferne(self, platz: str) -> list[Animation]:
        alt = self.angaben.pop(platz, None)
        if alt is None:
            return []
        self.remove(alt)
        return [FadeOut(alt)]

    def aufbau(self) -> list[Animation]:
        """Der Strahl entsteht von links nach rechts, ein Lichtpunkt läuft mit; die Angaben folgen."""
        spur = Line(self.beginn.get_center(), self.strahl.get_end())
        return [
            FadeIn(self.beginn, scale=0.6),
            Create(self.strahl),
            lichtpunkt(spur),
            LaggedStart(*[FadeIn(angabe) for angabe in self.angaben.values()], lag_ratio=0.15),
        ]

    def zeige(self, **angaben: Mobject | None) -> Animation:
        """Ersetzt die Angaben der genannten Plätze (None leert den Platz); die übrigen bleiben stehen."""
        schritte = []
        for platz, angabe in angaben.items():
            schritte += self._entferne(platz)
            if angabe is not None:
                self._setze(platz, angabe)
                schritte.append(FadeIn(angabe))
        return AnimationGroup(*schritte)

    def uebernimm(self, platz: str, angabe: Mobject, quelle: Mobject) -> Animation:
        """Ein Ergebnis wandert aus der Rechnung (quelle) an seinen Platz und ersetzt die bisherige Angabe."""
        schritte = self._entferne(platz)
        self._setze(platz, angabe)
        return AnimationGroup(*schritte, FadeIn(angabe, target_position=quelle))

    def betone(self, *plaetze: str) -> Animation:
        """Die Angaben der genannten Plätze pulsieren kurz."""
        return AnimationGroup(*[
            self.angaben[platz].animate(rate_func=rate_functions.there_and_back).scale(1.3) for platz in plaetze
        ])


class Phasenstrahl(Zeitstrahl):
    """Zeitstrahl mit zwei Zinsphasen (Zinssatzwechsel): ein Teilstrich am Übergang trennt die Phasen.

    Plätze über dem Strahl: "phase1", "phase2" (mittig über ihrer Phase, etwa Dauer und Zinssatz).
    Plätze darunter: "anfang" (bündig links), "mitte" (mittig am Übergang, der Zwischenwert), "ende" (bündig rechts).
    teilung: Lage des Übergangs als Anteil der Strahllänge. Der Strahl ist schematisch, nicht maßstäblich,
    damit die drei Beträge darunter nebeneinander Platz haben.
    """

    def __init__(self, teilung: float = 0.45, breite: float = t.BUEHNE_BREITE, abstand: float = 0.32,
                 **angaben: Mobject) -> None:
        self._PLAETZE = {
            "phase1": (teilung / 2, True, 0.5), "phase2": ((1 + teilung) / 2, True, 0.5),
            "anfang": (0.0, False), "mitte": (teilung, False, 0.5), "ende": (1.0, False),
        }
        self.teilung = teilung
        super().__init__(breite=breite, abstand=abstand, **angaben)
        self.trenner = Line(0.16 * UP, 0.16 * DOWN, color=t.ACHSE, stroke_width=4).move_to(self._ort(teilung))
        self.band: Mobject | None = None
        self.add(self.trenner)

    def _ort(self, anteil: float) -> np.ndarray:
        links, rechts = self.beginn.get_center()[0], self.strahl.get_end()[0]
        return np.array([interpolate(links, rechts, anteil), self.beginn.get_y(), 0])

    def aufbau(self) -> list[Animation]:
        return [*super().aufbau(), FadeIn(self.trenner)]

    def phase(self, nr: int | None) -> Animation:
        """Legt eine Fläche in der Stimmungsfarbe unter die Phase nr (1 oder 2), in der gerade gerechnet wird.

        None nimmt sie wieder weg.
        """
        schritte = []
        if self.band is not None:
            self.remove(self.band)
            schritte.append(FadeOut(self.band))
            self.band = None
        if nr is not None:
            von, bis = (0.0, self.teilung) if nr == 1 else (self.teilung, 1.0)
            start, ende = self._ort(von), self._ort(bis)
            self.band = RoundedRectangle(
                width=ende[0] - start[0], height=0.36, corner_radius=0.18,
                fill_color=t.MARKE, fill_opacity=0.3, stroke_width=0,
            ).move_to((start + ende) / 2)
            self.add_to_back(self.band)  # unter Strahl und Angaben, aber über der Karte
            schritte.append(FadeIn(self.band))
        return AnimationGroup(*schritte)


class Zahlungsplan(VGroup):
    """Angebote mit Einmalzahlungen zu verschiedenen Zeitpunkten (Kapitalvergleich).

    Eine Zeile je Angebot: links der Name, dann ein Strahl über die Jahre mit den Zahlungen an ihren Jahren,
    rechts eine Spalte für den Barwert. Oben stehen die Jahre („heute“, 1, 2, …) und der Spaltenkopf „Barwert“.
    angebote: Name → Liste von (Betrag als TeX, Jahr), etwa {"B": [(r"20\\,000", 0), (r"35\\,000", 4)]}.
    """

    def __init__(
        self,
        angebote: Mapping[str, list[tuple[str, int]]],
        jahre: int,
        jahr_breite: float = 1.05,
        zeilen_abstand: float = 1.05,
        barwert_breite: float = 2.6,
        groesse: float = 30,
        renten: Mapping[str, tuple[str, int, int]] | None = None,
    ) -> None:
        """renten: Name → (Rate als TeX, erstes Jahr, letztes Jahr). Eine Rente steht als Punkt an jedem
        Zahlungsjahr mit einer gemeinsamen Beschriftung „je … €“; sie ist die Zahlung nr 0 ihrer Zeile."""
        super().__init__()
        self._groesse = groesse
        self._x0 = 0.9                                # Strahlbeginn rechts der Namen
        self._jahr = jahr_breite
        self._spalte = self._x0 + jahre * jahr_breite + 0.6 + barwert_breite / 2  # Mitte der Barwert-Spalte
        self.namen: dict[str, Mobject] = {}
        self.strahlen: dict[str, VGroup] = {}
        self.zahlungen: dict[str, list[VGroup]] = {}
        self.barwerte: dict[str, Mobject] = {}

        kopf_y = 0.0
        self.kopf = VGroup(
            *[
                text("heute" if j == 0 else str(j), groesse=24, farbe=t.TEXT_LEISE).move_to([self._x(j), kopf_y, 0])
                for j in range(jahre + 1)
            ],
            text("Barwert", groesse=24, farbe=t.TEXT_LEISE).move_to([self._spalte, kopf_y, 0]),
        )
        heute = self.kopf[0]
        if heute.width > 0.9 * jahr_breite:  # enge Jahresspalten: „heute“ endet am Strich, statt die 1 zu berühren
            heute.shift((self._x(0) + 0.12 - heute.get_right()[0]) * RIGHT)
        self._kopf_hoehe = self.kopf[-1].height
        self.add(self.kopf)

        for i, (name, zahlungen) in enumerate(angebote.items()):
            y = kopf_y - 0.75 - i * zeilen_abstand
            self.namen[name] = text(name, groesse=36, gewicht=BOLD).move_to([0.25, y, 0])
            linie = Line([self._x(0), y, 0], [self._x(jahre) + 0.3, y, 0], color=t.ACHSE, stroke_width=3)
            striche = VGroup(*[
                Line([self._x(j), y + 0.08, 0], [self._x(j), y - 0.08, 0], color=t.ACHSE, stroke_width=3)
                for j in range(jahre + 1)
            ])
            self.strahlen[name] = VGroup(linie, striche)
            self.zahlungen[name] = []
            if renten and name in renten:
                rate, erstes, letztes = renten[name]
                punkte = VGroup(*[
                    Dot([self._x(j), y, 0], radius=0.08, color=t.TEXT) for j in range(erstes, letztes + 1)
                ])
                je = reihe(text("je", groesse=groesse * 0.75), betrag(rate, groesse=groesse), abstand=0.15,
                           grundlinie=True)
                je.next_to(punkte, UP, buff=0.12)
                self.zahlungen[name].append(VGroup(punkte, je))
            for betrag_tex, jahr in zahlungen:
                punkt = Dot([self._x(jahr), y, 0], radius=0.08, color=t.TEXT)
                wert = betrag(betrag_tex, groesse=groesse).next_to(punkt, UP, buff=0.12)
                if jahr == 0:
                    wert.align_to(punkt, LEFT).shift(0.12 * LEFT)
                self.zahlungen[name].append(VGroup(punkt, wert))
            self.add(self.namen[name], self.strahlen[name], *self.zahlungen[name])

    def _x(self, jahr: float) -> float:
        return self._x0 + jahr * self._jahr

    def aufbau(self, *namen: str, kopf: bool = True) -> list[Animation]:
        """Die genannten Zeilen (ohne Angabe: alle) erscheinen, mit kopf auch die Jahre und der Spaltenkopf."""
        namen = namen or tuple(self.namen)
        return [
            *([FadeIn(self.kopf)] if kopf else []),
            *[
                AnimationGroup(
                    FadeIn(self.namen[name]), Create(self.strahlen[name]),
                    LaggedStart(*[FadeIn(z, shift=0.15 * DOWN) for z in self.zahlungen[name]], lag_ratio=0.3),
                )
                for name in namen
            ],
        ]

    def bogen(self, name: str, nr: int, farbe: str = t.HERVOR) -> VMobject:
        """Pfeil von der Zahlung nr eines Angebots unter dem Strahl zurück auf heute: abzinsen."""
        # Lagen aus den Objekten selbst lesen: Der Plan wird nach dem Bau noch eingepasst und verschoben.
        punkt = self.zahlungen[name][nr][0].get_center()
        heute = self.strahlen[name][1][0].get_center()  # Teilstrich bei Jahr 0
        abstand = 1.5 * self.zahlungen[name][nr][0].height * DOWN
        pfeil = ArcBetweenPoints(punkt + abstand, heute + abstand, angle=-0.8, color=farbe, stroke_width=4)
        pfeil.add_tip(tip_length=0.18, tip_width=0.18)
        return pfeil

    def faerbe(self, name: str, nr: int, farbe: str = t.HERVOR) -> Animation:
        """Färbt eine Zahlung (Punkt und Betrag)."""
        return self.zahlungen[name][nr].animate.set_color(farbe)

    def barwert(self, name: str, angabe: Mobject, quelle: Mobject | None = None) -> Animation:
        """Setzt den Barwert eines Angebots in die rechte Spalte; mit quelle wandert er aus der Rechnung dorthin."""
        massstab = self.kopf[-1].height / self._kopf_hoehe  # wie stark der Plan seit dem Bau verkleinert wurde
        angabe.scale(massstab).move_to([0, self.namen[name].get_y(), 0])
        angabe.shift((self.kopf[-1].get_right()[0] - angabe.get_right()[0]) * RIGHT)  # rechtsbündig unter dem Kopf
        alt = self.barwerte.pop(name, None)
        self.barwerte[name] = angabe
        self.add(angabe)
        schritte = [FadeIn(angabe, target_position=quelle) if quelle is not None else FadeIn(angabe)]
        if alt is not None:
            self.remove(alt)
            schritte.append(FadeOut(alt))
        return AnimationGroup(*schritte)

    def betone(self, name: str) -> Animation:
        """Name und Barwert eines Angebots pulsieren kurz."""
        teile = [self.namen[name], *([self.barwerte[name]] if name in self.barwerte else [])]
        return AnimationGroup(*[
            teil.animate(rate_func=rate_functions.there_and_back).scale(1.25) for teil in teile
        ])


class Rentenstrahl(VGroup):
    """Schematischer Zeitstrahl einer Rente: Jahre 0, 1, 2, …, n−1, n, Raten als Punkte mit „r“ darüber.

    Nachschüssig liegen die Raten am Ende der Jahre (1, 2, …, n), vorschüssig am Anfang (0, 1, …, n−1);
    zahlweise lässt sie um ein Jahr wandern. Unter dem Strahl nehmen zwei Plätze Angaben auf:
    "barwert" links unter dem Jahr 0, "endwert" rechts unter dem Jahr n (Name und Wert, mehrzeilig erlaubt).
    """

    JAHRE = ("0", "1", "2", "n-1", "n")

    def __init__(
        self,
        vorschuessig: bool = False,
        rate: str = "r",
        breite: float = t.BUEHNE_BREITE,
        groesse: float = 44,
    ) -> None:
        super().__init__()
        self._groesse = groesse
        # Rand links und rechts, damit Beschriftungen wie „−5 000“ an den äußeren Raten nicht überstehen
        links, rechts = -breite / 2 + 0.6, breite / 2 - 0.6
        schritt = (rechts - links) / (len(self.JAHRE) - 1)
        xs = [links + schritt * i for i in range(len(self.JAHRE))]
        self._schritt = schritt
        luecke = (xs[2] + xs[3]) / 2
        teil1 = Line([xs[0], 0, 0], [luecke - 0.38 * schritt, 0, 0], color=t.ACHSE, stroke_width=4)
        teil2 = Line([luecke + 0.38 * schritt, 0, 0], [breite / 2, 0, 0], color=t.ACHSE, stroke_width=4)
        teil2.add_tip(tip_length=0.24, tip_width=0.24)
        punkte = formel(r"\cdots", groesse=groesse, farbe=t.ACHSE).move_to([luecke, 0, 0])
        self.linie = VGroup(teil1, punkte, teil2)
        self.striche = VGroup(*[
            Line([x, 0.1, 0], [x, -0.1, 0], color=t.ACHSE, stroke_width=4) for x in xs
        ])
        self.jahre = VGroup(*[
            formel(jahr, groesse=groesse * 0.8, farbe=t.TEXT_LEISE).next_to([x, -0.1, 0], DOWN, buff=0.14)
            for jahr, x in zip(self.JAHRE, xs)
        ])
        # gemeinsame Oberkante der Jahreszahlen
        oben = max(j.get_top()[1] for j in self.jahre)
        for j in self.jahre:
            j.shift((oben - j.get_top()[1]) * UP)
        self._hoehe_bezug = self.striche[0].height
        self.vorschuessig = vorschuessig
        self._tex, self._farbe = rate, t.TEXT
        self.raten = VGroup(*[self._rate(rate) for _ in range(4)])
        self._lege_raten(vorschuessig)
        self.angaben: dict[str, Mobject] = {}
        self.add(self.linie, self.striche, self.jahre, self.raten)

    def _massstab(self) -> float:
        return self.striche[0].height / self._hoehe_bezug

    def _rate(self, tex: str, farbe: str = t.TEXT) -> VGroup:
        punkt = Dot(ORIGIN, radius=0.1, color=farbe)
        name = formel(tex, groesse=self._groesse, farbe=farbe)
        einpassen(name, 0.8 * self._schritt)  # Beträge wie „+3 000“ dürfen sich nicht berühren
        name.next_to(punkt, UP, buff=0.16)
        return VGroup(punkt, name)

    def _stellen(self, vorschuessig: bool) -> list[int]:
        return [0, 1, 2, 3] if vorschuessig else [1, 2, 3, 4]

    def _lege_raten(self, vorschuessig: bool) -> None:
        for rate, i in zip(self.raten, self._stellen(vorschuessig)):
            rate.shift(self.striche[i].get_center() - rate[0].get_center())

    def aufbau(self) -> list[Animation]:
        """Strahl und Jahre entstehen, dann erscheinen die Raten nacheinander."""
        return [
            Create(self.linie),
            FadeIn(self.striche),
            FadeIn(self.jahre),
            LaggedStart(*[FadeIn(r, shift=0.15 * DOWN) for r in self.raten], lag_ratio=0.25),
            *[FadeIn(a) for a in self.angaben.values()],
        ]

    def raten_zu(
        self, tex: str | None = None, farbe: str | None = None, vorschuessig: bool | None = None,
    ) -> Animation:
        """Ändert Beschriftung, Farbe und Zahlungsweise der Raten in einem Schritt (je Rate eine Animation).

        tex: neue Beschriftung, etwa "+r", "-r" oder ein Betrag; vorschuessig: Raten an den Anfang (True)
        oder das Ende (False) der Jahre. Nicht genannte Eigenschaften bleiben.
        """
        if tex is not None:
            self._tex = tex
        if farbe is not None:
            self._farbe = farbe
        if vorschuessig is not None:
            self.vorschuessig = vorschuessig
        massstab = self._massstab()
        schritte = []
        for rate, i in zip(self.raten, self._stellen(self.vorschuessig)):
            neu = self._rate(self._tex, self._farbe).scale(massstab)
            neu.shift(self.striche[i].get_center() - neu[0].get_center())
            schritte.append(Transform(rate, neu))
        return AnimationGroup(*schritte)

    def zahlweise(self, vorschuessig: bool) -> Animation:
        """Die Raten wandern an den Anfang (vorschüssig) oder das Ende (nachschüssig) der Jahre."""
        return self.raten_zu(vorschuessig=vorschuessig)

    def rate(self, tex: str, farbe: str = t.TEXT) -> Animation:
        """Ersetzt die Beschriftung aller Raten, etwa durch "+r", "-r" oder einen Betrag."""
        return self.raten_zu(tex=tex, farbe=farbe)

    def _setze(self, platz: str, angabe: Mobject) -> None:
        massstab = self._massstab()
        angabe.scale(massstab)
        oben = self.jahre.get_bottom()[1] - 0.22 * massstab
        angabe.shift((oben - angabe.get_top()[1]) * UP)
        if platz == "barwert":
            angabe.shift((self.striche[0].get_x() - 0.15 * massstab - angabe.get_left()[0]) * RIGHT)
        else:
            angabe.shift((self.striche[-1].get_x() + 0.15 * massstab - angabe.get_right()[0]) * RIGHT)
        self.angaben[platz] = angabe
        self.add(angabe)

    def _entferne(self, platz: str) -> list[Animation]:
        alt = self.angaben.pop(platz, None)
        if alt is None:
            return []
        self.remove(alt)
        return [FadeOut(alt)]

    def zeige(self, **angaben: Mobject | None) -> Animation:
        """Ersetzt die Angaben der Plätze "barwert" und "endwert" (None leert den Platz)."""
        schritte = []
        for platz, angabe in angaben.items():
            schritte += self._entferne(platz)
            if angabe is not None:
                self._setze(platz, angabe)
                schritte.append(FadeIn(angabe))
        return AnimationGroup(*schritte)

    def uebernimm(self, platz: str, angabe: Mobject, quelle: Mobject) -> Animation:
        """Ein Ergebnis wandert aus der Rechnung an seinen Platz und ersetzt die bisherige Angabe."""
        schritte = self._entferne(platz)
        self._setze(platz, angabe)
        return AnimationGroup(*schritte, FadeIn(angabe, target_position=quelle))

    def betone(self, *plaetze: str) -> Animation:
        """Die Angaben der Plätze pulsieren kurz; "raten" lässt die Raten pulsieren."""
        teile = [teil for platz in plaetze for teil in ([*self.raten] if platz == "raten" else [self.angaben[platz]])]
        return AnimationGroup(*[
            teil.animate(rate_func=rate_functions.there_and_back).scale(1.3) for teil in teile
        ])


def wortlaut(*zeilen: str, signal: tuple[str, ...] = (), groesse: float = 32) -> VGroup:
    """Wortlaut einer Aufgabe in Anführungszeichen, eine Bildzeile je Argument, linksbündig.

    signal: Wörter, die orange erscheinen (Signalwörter). In Zahlen wie 12 000 wird ein schmales Leerzeichen gesetzt.
    """
    zeilen = (f"„{zeilen[0]}", *zeilen[1:-1], f"{zeilen[-1]}“") if len(zeilen) > 1 else (f"„{zeilen[0]}“",)
    farben = {wort: t.HERVOR for wort in signal}
    bild = [
        text(re.sub(r"(?<=\d) (?=\d{3})", " ", zeile), groesse=groesse, gewicht=BOLD, farben=farben)
        for zeile in zeilen
    ]
    return VGroup(*bild).arrange(DOWN, buff=0.2, aligned_edge=LEFT)


def _zahl(wert: float) -> str:
    """Zahl als TeX mit Dezimalkomma."""
    return f"{wert:g}".replace(".", "{,}")


def geld(wert: float, cent: bool = True) -> str:
    r"""Geldbetrag als TeX mit schmalem Tausenderabstand und Dezimalkomma, etwa 15\,251{,}97; ohne cent ganze Euro."""
    return f"{wert:,.{2 if cent else 0}f}".replace(",", "X").replace(".", "{,}").replace("X", r"\,")


class Tilgungsplan(VGroup):
    """Tilgungsplan wie im Training: eine Zeile je Jahr, Spalten Restschuld (Anfang), Zinsen, Tilgung,
    Annuität, Restschuld (Ende).

    jahre: Jahre der Zeilen, etwa (1, 2) oder (1, None, 10, 11, None, 24, 25); None ist eine ausgelassene
    Strecke (⋮). Zellen werden mit zeige gefüllt, als TeX (etwa geld(630)) oder "?" für eine Lücke.
    Die Lage der Zellen wird aus Kopf und Jahreszahlen gelesen: Der Plan darf nach dem Bau eingepasst werden.
    """

    SPALTEN = ("rk_anfang", "zinsen", "tilgung", "annuitaet", "rk_ende")
    _KOPF = {
        "rk_anfang": ("Restschuld", "Anfang"), "zinsen": ("Zinsen",), "tilgung": ("Tilgung",),
        "annuitaet": ("Annuität",), "rk_ende": ("Restschuld", "Ende"),
    }

    def __init__(
        self,
        jahre: Iterable[int | None],
        groesse: float = 32,
        spalte: float = 1.48,
        jahr_spalte: float = 0.55,
        zeile: float = 0.66,
        luecke: float = 0.5,
    ) -> None:
        super().__init__()
        self._groesse = groesse
        xs = [0.0] + [jahr_spalte / 2 + 0.1 + spalte * (i + 0.5) for i in range(len(self.SPALTEN))]
        kopf = [VGroup(text("Jahr", groesse=20, farbe=t.TEXT_LEISE))]
        for name in self.SPALTEN:
            kopf.append(VGroup(*[text(wort, groesse=20, farbe=t.TEXT_LEISE) for wort in self._KOPF[name]])
                        .arrange(DOWN, buff=0.08))
        for teil, x in zip(kopf, xs):
            teil.move_to([x, 0, 0]).align_to([0, 0, 0], DOWN)
        self.kopf = VGroup(*kopf)
        self._kopf_hoehe = self.kopf[0].height
        links, rechts = -jahr_spalte / 2, xs[-1] + spalte / 2
        self.linie = Line([links, -0.15, 0], [rechts, -0.15, 0], color=t.RAHMEN, stroke_width=3)
        self._breite = (links, rechts)
        self.marken: dict[int, Mobject] = {}
        self.auslassungen = VGroup()
        y = -0.15
        for jahr in jahre:
            hoehe = zeile if jahr is not None else luecke
            y -= hoehe / 2
            if jahr is None:
                self.auslassungen.add(*[
                    formel(r"\vdots", groesse=26, farbe=t.TEXT_SCHWACH).move_to([x, y, 0]) for x in xs
                ])
            else:
                self.marken[jahr] = text(str(jahr), groesse=groesse * 0.9, farbe=t.TEXT_LEISE).move_to([0, y, 0])
            y -= hoehe / 2
        self.zellen: dict[tuple[int, str], Mobject] = {}
        self.band: Mobject | None = None
        self.add(self.kopf, self.linie, *self.marken.values(), self.auslassungen)

    def _massstab(self) -> float:
        return self.kopf[0].height / self._kopf_hoehe

    def ort(self, jahr: int, spalte: str) -> np.ndarray:
        return np.array([self.kopf[1 + self.SPALTEN.index(spalte)].get_x(), self.marken[jahr].get_y(), 0])

    def _setze(self, jahr: int, spalte: str, inhalt: str, farbe: str) -> Mobject:
        zelle = formel(inhalt, groesse=self._groesse, farbe=farbe).scale(self._massstab())
        zelle.move_to(self.ort(jahr, spalte))
        self.zellen[(jahr, spalte)] = zelle
        self.add(zelle)
        return zelle

    def zelle(self, jahr: int, spalte: str) -> Mobject:
        return self.zellen[(jahr, spalte)]

    def aufbau(self) -> list[Animation]:
        """Kopf und Linie erscheinen, dann Jahre und schon gesetzte Zellen."""
        return [
            FadeIn(self.kopf),
            Create(self.linie),
            LaggedStart(
                *[FadeIn(m) for m in (*self.marken.values(), *self.auslassungen, *self.zellen.values())],
                lag_ratio=0.1,
            ),
        ]

    def zeige(self, jahr: int, spalte: str, inhalt: str, farbe: str = t.TEXT, quelle: Mobject | None = None) -> Animation:
        """Setzt eine Zelle (ersetzt den bisherigen Inhalt); mit quelle wandert der Wert aus der Rechnung dorthin.

        inhalt: TeX, etwa geld(630) oder "?".
        """
        schritte = []
        alt = self.zellen.pop((jahr, spalte), None)
        if alt is not None:
            self.remove(alt)
            schritte.append(FadeOut(alt))
        neu = self._setze(jahr, spalte, inhalt, farbe)
        schritte.append(FadeIn(neu, target_position=quelle) if quelle is not None else FadeIn(neu))
        return AnimationGroup(*schritte)

    def fuelle(self, *zellen: tuple[int, str, str], farbe: str = t.TEXT) -> Animation:
        """Setzt mehrere Zellen ohne Herkunft: (Jahr, Spalte, Inhalt)."""
        return AnimationGroup(*[self.zeige(jahr, spalte, inhalt, farbe) for jahr, spalte, inhalt in zellen])

    def uebertrag(self, jahr: int, farbe: str = t.TEXT) -> Animation:
        """Die Restschuld am Ende von jahr wandert an den Anfang des Folgejahres."""
        quelle = self.zellen[(jahr, "rk_ende")]
        return self.zeige(jahr + 1, "rk_anfang", quelle.get_tex_string(), farbe, quelle=quelle)

    def faerbe(self, *zellen: tuple[int, str], farbe: str = t.TEXT) -> Animation:
        return AnimationGroup(*[self.zellen[z].animate.set_color(farbe) for z in zellen])

    def betone(self, *zellen: tuple[int, str]) -> Animation:
        """Die genannten Zellen pulsieren kurz."""
        return AnimationGroup(*[
            self.zellen[z].animate(rate_func=rate_functions.there_and_back).scale(1.3) for z in zellen
        ])

    def zeile(self, jahr: int | None) -> Animation:
        """Legt eine Fläche in der Stimmungsfarbe unter die Zeile, in der gerade gerechnet wird; None nimmt sie weg."""
        schritte = []
        if self.band is not None:
            self.remove(self.band)
            schritte.append(FadeOut(self.band))
            self.band = None
        if jahr is not None:
            massstab = self._massstab()
            links = self.kopf[0].get_left()[0] - 0.15 * massstab
            rechts = self.kopf[-1].get_right()[0] + 0.15 * massstab
            self.band = RoundedRectangle(
                width=rechts - links, height=0.56 * massstab, corner_radius=0.16 * massstab,
                fill_color=t.MARKE, fill_opacity=0.25, stroke_width=0,
            ).move_to([(links + rechts) / 2, self.marken[jahr].get_y(), 0])
            self.add_to_back(self.band)
            schritte.append(FadeIn(self.band))
        return AnimationGroup(*schritte)


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
        self.werte = [list(werte) for werte in zeilen]  # aktueller Stand, umformen() hält ihn mit
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
        self.werte[i] = list(werte)
        neu = self.zahlenzeile(werte, self.eintraege[i][0].get_y(), farben)
        return AnimationGroup(*[Transform(alt, ziel) for alt, ziel in zip(self.eintraege[i], neu)])

    def betonen(self, i: int) -> Animation:
        """Die Zeile i pulsiert kurz: „um diese Zeile geht es“."""
        return AnimationGroup(*[
            eintrag.animate(rate_func=rate_functions.there_and_back).scale(1.3) for eintrag in self.eintraege[i]
        ])

    @classmethod
    def vielfaches(cls, faktor: int, i: int) -> str:
        """Vielfaches der Zeile i als TeX, etwa „4·I“; der Faktor 1 entfällt."""
        return (rf"{faktor}\cdot" if faktor != 1 else "") + cls.zeilenname(i)

    def gleichungen(self, groesse: float = 52) -> VGroup:
        """Das LGS der Matrix als Gleichungen, am Gleichheitszeichen ausgerichtet; Lage wie die Matrix setzen.

        Gegenstück zu aus_gleichungen(): Die Koeffizienten wandern von dort in die Matrix.
        """
        zeilen = VGroup()
        self._quellen: list[list[VGroup | None]] = []
        for werte in self.werte:
            teile: list[str] = []
            stellen: list[list[int] | None] = []
            for j, a in enumerate(werte[:-1], start=1):
                vorzeichen = []
                if a < 0:
                    teile.append("-")
                    vorzeichen = [len(teile) - 1]
                elif j > 1:
                    teile.append("+")
                if abs(a) == 1:
                    stellen.append(None)
                else:
                    teile.append(_zahl(abs(a)))
                    stellen.append([*vorzeichen, len(teile) - 1])
                teile.append(f"x_{j}")
            zeile = formel(*teile, "=", _zahl(werte[-1]), groesse=groesse)
            zeilen.add(zeile)
            self._quellen.append([VGroup(*[zeile[k] for k in stelle]) if stelle else None for stelle in stellen])
        zeilen.arrange(DOWN, buff=0.5)
        for zeile in zeilen:
            zeile.shift((zeilen[0][-2].get_x() - zeile[-2].get_x()) * RIGHT)
        self._gleichungen = zeilen
        return zeilen

    def aus_gleichungen(self) -> list[Animation]:
        """Übergang von gleichungen() zur Matrix: Klammern und Strich entstehen, die Koeffizienten wandern hinein."""
        animationen: list[Animation] = [Create(self.klammern), Create(self.strich), *[FadeIn(n) for n in self.namen]]
        for i, (zeile, quellen) in enumerate(zip(self._gleichungen, self._quellen)):
            benutzt = {id(zeile[-1])}
            for j, quelle in enumerate(quellen):
                if quelle is None:
                    animationen.append(FadeIn(self.eintraege[i][j], scale=0.5))
                else:
                    animationen.append(ReplacementTransform(quelle, self.eintraege[i][j]))
                    benutzt |= {id(teil) for teil in quelle}
            animationen.append(ReplacementTransform(zeile[-1], self.eintraege[i][-1]))
            animationen.append(FadeOut(VGroup(*[teil for teil in zeile if id(teil) not in benutzt])))
        return animationen

    def nebenrechnung(
        self,
        y: float,
        zeile: int,
        faktor: int,
        basis: int,
        farben: dict[int, str] | None = None,
        zeilenabstand: float = 0.8,
    ) -> VGroup:
        """Schriftliche Rechnung „zeile − faktor · basis“ in den Spalten der Matrix; y ist die Höhe der oberen Zeile.

        Ergibt vier Teile: obere Zeile (mit Namen), abgezogene Zeile (mit Minus und Namen), Rechenstrich, Ergebnis.
        """
        oben = self.werte[zeile]
        abzug = [faktor * wert for wert in self.werte[basis]]
        ergebnis = [a - b for a, b in zip(oben, abzug)]
        links, rechts = self.klammern.get_left()[0], self.klammern.get_right()[0]
        y_abzug = y - zeilenabstand
        minus = self.randnotiz("-", y_abzug, t.TEXT).set_x(links)
        return VGroup(
            VGroup(self.zahlenzeile(oben, y, farben), self.randnotiz(self.zeilenname(zeile), y)),
            VGroup(minus, self.zahlenzeile(abzug, y_abzug), self.randnotiz(self.vielfaches(faktor, basis), y_abzug)),
            Line([links - 0.15, y_abzug - 0.5, 0], [rechts + 0.15, y_abzug - 0.5, 0], color=t.ACHSE, stroke_width=2.5),
            self.zahlenzeile(ergebnis, y - 2 * zeilenabstand - 0.2, farben),
        )


class Punktefeld(VGroup):
    """Gitter aus Punkten (etwa Personen); Ereignisse sind durchsichtige Kästen in ihrer Farbe, ihr Name steht
    außen daneben (wie im Kontextbild aus Ergebnissen und Ereignissen).

    Damit lässt sich eine Wahrscheinlichkeit als Teil durch Ganzes zeigen: markiere(ganzes, teil, kasten) lässt
    alle Punkte außerhalb des Ganzen zurücktreten, färbt den Teil und hebt den Kasten der Bedingung hervor.
    Punkte heißen nach ihrer Lage (zeile, spalte), gezählt ab 0 von links oben.
    """

    def __init__(
        self,
        zeilen: int,
        spalten: int,
        mengen: Mapping[str, tuple[range, range, str, str]],
        abstand: float = 0.8,
    ) -> None:
        """mengen: Name (LaTeX) → (Zeilen, Spalten, Farbe, Seite des Namens: "links" oder "rechts")."""
        super().__init__()
        self.punkte = {
            (z, s): Circle(radius=0.17, stroke_width=0, fill_color=t.TEXT, fill_opacity=1).move_to(
                [s * abstand, -z * abstand, 0]).set_z_index(1)  # vor den Kästen
            for z in range(zeilen) for s in range(spalten)
        }
        self.mengen: dict[str, set[tuple[int, int]]] = {}
        self.kaesten: dict[str, VGroup] = {}
        rand = 0.36 * abstand
        for i, (name, (z_bereich, s_bereich, farbe, seite)) in enumerate(mengen.items()):
            self.mengen[name] = {(z, s) for z in z_bereich for s in s_bereich}
            versatz = 0.06 * (1 if i % 2 else -1)  # Kästen, die an derselben Kante enden, liegen nicht aufeinander
            links, rechts = s_bereich[0] * abstand - rand + versatz, s_bereich[-1] * abstand + rand + versatz
            oben, unten = -z_bereich[0] * abstand + rand + versatz, -z_bereich[-1] * abstand - rand + versatz
            kasten = RoundedRectangle(
                width=rechts - links, height=oben - unten, corner_radius=0.12,
                stroke_color=farbe, stroke_width=3, fill_color=farbe, fill_opacity=0.16,
            ).move_to([(links + rechts) / 2, (oben + unten) / 2, 0])
            schild = formel(name, groesse=56, farbe=farbe)
            schild.next_to(kasten, LEFT if seite == "links" else RIGHT, buff=0.2)
            self.kaesten[name] = VGroup(kasten, schild)
        self.add(*self.kaesten.values(), *self.punkte.values())

    @property
    def alle(self) -> set[tuple[int, int]]:
        return set(self.punkte)

    def ohne(self, name: str) -> set[tuple[int, int]]:
        """Das Gegenereignis: alle Punkte außerhalb des Kastens."""
        return self.alle - self.mengen[name]

    def aufbau(self) -> list[Animation]:
        """Die Punkte erscheinen Zeile für Zeile."""
        return [LaggedStart(*[FadeIn(punkt, scale=0.4) for punkt in self.punkte.values()], lag_ratio=0.02)]

    def zeige(self, name: str) -> Animation:
        """Der Kasten eines Ereignisses erscheint mit seinem Namen."""
        kasten, schild = self.kaesten[name]
        return AnimationGroup(GrowFromCenter(kasten), FadeIn(schild, scale=0.6))

    def markiere(
        self,
        ganzes: Iterable[tuple[int, int]] | None = None,
        teil: Iterable[tuple[int, int]] = (),
        kasten: str | None = None,
        farbe: str = t.HERVOR,
    ) -> Animation:
        """Punkte außerhalb des Ganzen treten zurück, der Teil wird gefärbt; der Kasten der Bedingung tritt
        hervor, die übrigen Kästen zurück. Ohne Angaben: Grundzustand."""
        ganzes = self.alle if ganzes is None else set(ganzes)
        teil = set(teil)
        schritte = [
            punkt.animate.set_fill(farbe if person in teil else t.TEXT if person in ganzes else t.TEXT_SCHWACH)
            for person, punkt in self.punkte.items()
        ]
        for name, (rahmen, schild) in self.kaesten.items():
            staerke = 1.0 if kasten is None else (1.8 if name == kasten else 0.35)
            schritte += [
                rahmen.animate.set_fill(opacity=min(0.16 * staerke, 0.3)).set_stroke(
                    width=3 * min(staerke, 1.6), opacity=min(staerke, 1)),
                schild.animate.set_opacity(min(staerke, 1)),
            ]
        return AnimationGroup(*schritte)


def feldnummer(nr: int, groesse: float = 30, farbe: str = t.TEXT_LEISE) -> VGroup:
    """Nummer eines Feldes im Baumdiagramm wie ① auf der Website: Ziffer im Kreis."""
    ziffer = text(str(nr), groesse=groesse, farbe=farbe, gewicht=SEMIBOLD)
    kreis = Circle(radius=0.5 * groesse / 48 + 0.07 * len(str(nr)), color=farbe, stroke_width=2.5).move_to(ziffer)
    return VGroup(kreis, ziffer)


class Baumdiagramm(VGroup):
    """Zweistufiges Baumdiagramm zu zwei Ereignissen A und B, aufgebaut wie auf der Website.

    Äste und Pfadenden heißen nach ihrem Pfad: "A" und "nA" (erste Stufe), "AB", "AnB", "nAB" und
    "nAnB" (zweite Stufe und Pfadenden). An jedem Ast steht seine Wahrscheinlichkeit, rechts neben
    jedem Pfadende das Produkt.

    luecken: Felder (Nummern 1 bis 10 wie auf der Website), deren Wert noch fehlt; dort steht die
    Feldnummer, bis fuelle() den Wert einsetzt.
    """

    PFADE = ("AB", "AnB", "nAB", "nAnB")
    # Feldnummern wie auf der Website: 1–6 die Äste, 7–10 die Pfadenden.
    FELDER = {
        1: ("ast", "A"), 2: ("ast", "nA"), 3: ("ast", "AB"), 4: ("ast", "AnB"), 5: ("ast", "nAB"),
        6: ("ast", "nAnB"), 7: ("ende", "AB"), 8: ("ende", "AnB"), 9: ("ende", "nAB"), 10: ("ende", "nAnB"),
    }

    def __init__(
        self,
        pa: float,
        pba: float,
        pbna: float,
        breite: float = t.BUEHNE_BREITE,
        hoehe: float = 4.3,
        luecken: tuple[int, ...] = (),
    ) -> None:
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
        # Offene Felder: Die Nummer steht an der Stelle des Werts. Der Wert gehört unsichtbar zum Baum, damit er
        # beim Einpassen mitwandert, und wird erst mit fuelle() sichtbar.
        self.nummern: dict[int, VGroup] = {}
        for nr in luecken:
            art, name = self.FELDER[nr]
            wert = self.werte[name] if art == "ast" else self.enden[name]
            marke = feldnummer(nr)
            if art == "ast":
                marke.move_to(wert)
            else:
                marke.next_to(self.kreise[name], RIGHT, buff=0.3)
            self.nummern[nr] = marke
            wert.set_opacity(0)
        self.add(
            *self.kanten.values(), self.wurzel, *self.kreise.values(), *self.namen.values(),
            *[self.feld(nr) for nr in self.FELDER], *[self.wert(nr) for nr in luecken],
        )

    def wert(self, nr: int) -> MathTex:
        """Der Wert eines Feldes, auch wenn er noch nicht eingesetzt ist."""
        art, name = self.FELDER[nr]
        return self.werte[name] if art == "ast" else self.enden[name]

    def feld(self, nr: int) -> Mobject:
        """Was im Feld gerade zu sehen ist: die Nummer, solange es offen ist, sonst der Wert."""
        return self.nummern.get(nr) or self.wert(nr)

    def fuelle(self, nr: int, quelle: Mobject | None = None, farbe: str = t.HERVOR) -> Animation:
        """Setzt den Wert in ein offenes Feld ein; mit quelle wandert er sichtbar aus der Rechnung dorthin."""
        marke, wert = self.nummern.pop(nr), self.wert(nr)
        self.remove(marke)
        wert.set_opacity(1).set_color(farbe)
        ankunft = TransformFromCopy(quelle, wert) if quelle is not None else FadeIn(wert, scale=1.4)
        return AnimationGroup(FadeOut(marke, scale=0.6), ankunft)

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
                *[FadeIn(self.feld(nr)) for nr, (art, name) in self.FELDER.items() if art == "ast" and name in aeste],
                *[FadeIn(VGroup(self.kreise[ast], self.namen[ast]), scale=0.6) for ast in aeste],
            )

        spur = VMobject().set_points_as_corners(
            [self.kanten["A"].get_start(), self.kanten["A"].get_end(), self.kanten["AB"].get_end()]
        )
        enden = FadeIn(VGroup(*[self.feld(nr) for nr in range(7, 11)]), shift=0.2 * RIGHT)
        return [
            FadeIn(self.wurzel),
            LaggedStart(stufe(("A", "nA")), stufe(self.PFADE), enden, lag_ratio=0.6),
            lichtpunkt(spur),
        ]

    def markiere(
        self, aeste: Mapping[str, str] | None = None, enden: Mapping[str, str] | None = None, knoten: bool = True,
    ) -> Animation:
        """Färbt Äste (mit ihrem Wert) und Pfadenden, jeweils Name → Farbe; alles Übrige tritt zurück.

        Ohne Angaben kehrt der Baum in den Grundzustand zurück.
        knoten: die Kreise am Ende gefärbter Äste mitfärben; ohne, wenn nur die Werte verglichen werden.
        Offene Felder behalten ihre Nummer; ist ihr Ast oder Pfadende markiert, nimmt die Nummer die Farbe an.
        """
        aeste, enden = aeste or {}, enden or {}
        ruhig = t.TEXT_LEISE if aeste or enden else t.TEXT
        schritte = []
        for ast in self.kanten:
            farbe = aeste.get(ast)
            schritte += [
                self.kanten[ast].animate.set_stroke(farbe or t.ACHSE, width=5 if farbe else 3),
                self.kreise[ast].animate.set_stroke((farbe if knoten else None) or enden.get(ast) or t.ACHSE),
            ]
        for nr, (art, name) in self.FELDER.items():
            farbe = (aeste if art == "ast" else enden).get(name)
            offen = nr in self.nummern
            schritte.append(self.feld(nr).animate.set_color(farbe or (t.TEXT_LEISE if offen else ruhig)))
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
