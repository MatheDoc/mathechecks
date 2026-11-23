"""Wiederkehrende Bildelemente der MatheChecks-Videos."""
import math
import re
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
    GrowFromEdge,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    Rectangle,
    ReplacementTransform,
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
    ) -> None:
        super().__init__()
        self.n, self.p, self.y_max, self.hoehe = n, p, y_max, hoehe
        self.werte = list(range(bis + 1))
        self._zahlen = set(zahlen)
        raster = breite / (len(self.werte) + (1.2 if bis < n else 0))
        self.grundlinie = Line([-0.5 * raster, 0, 0], [(bis + 0.5) * raster, 0, 0], color=t.ACHSE, stroke_width=3)
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

    def _hoehe(self, k: int, p: float) -> float:
        hoehe = math.comb(self.n, k) * p**k * (1 - p) ** (self.n - k) / self.y_max * self.hoehe
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


class Zeitstrahl(VGroup):
    """Zeitstrahl mit zwei Zeitpunkten: links der frühere, rechts der spätere.

    Sechs Plätze nehmen Angaben auf. Über dem Strahl steht die Zeit ("frueher", "dauer", "spaeter"),
    darunter stehen Beträge und Zins ("anfang", "zins", "ende"). Die äußeren Angaben schließen bündig
    mit den Enden des Strahls ab, die mittleren stehen mittig. Eine Angabe unter dem Strahl darf
    mehrzeilig sein, etwa der Name einer Größe und darunter ihr Wert.
    """

    _PLAETZE = {  # Name: (Anteil der Strahllänge, über dem Strahl)
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
        anteil, oben = self._PLAETZE[platz]
        links, rechts, y = self.beginn.get_left()[0], self.strahl.get_end()[0], self.beginn.get_y()
        if oben:
            angabe.shift((y + self._abstand - _grundlinie(angabe)) * UP)
        else:
            angabe.shift((y - self._abstand - angabe.get_top()[1]) * UP)
        stelle = interpolate(angabe.get_left()[0], angabe.get_right()[0], anteil)
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
