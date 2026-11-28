"""Check 01 – Graph einer Produktlebenszyklusfunktion interpretieren.

Kernidee: Jede Kennzahl im Sachzusammenhang ist ein Merkmal des Graphen (y-Achsenabschnitt, Hochpunkt,
Wendepunkte, waagrechte Asymptote, Nullstelle bei Marktaustritt); man liest sie am Graphen ab.
Beispiel: a(t) = (0,1 t^3 + 0,1 t^2 - 2) * e^(-0,25 t) + 5, ein Produkt wie im Skript, aber mit anderen Zahlen:
a(0) = 3 ist weder 0 noch der langfristige Absatz 5; der erste Wendepunkt liegt weit genug rechts, um gut
erkennbar zu sein. Der Term steht nicht im Video, nur der Graph. Für den Marktaustritt zeigt die Kurzfassung
den Graphen aus dem Musterbeispiel (a_1(t) = (-0,1 t^3 + 2 t^2) * e^(-0,2 t), Nullstelle t = 20).
Die Teilaufgaben des Trainings sind abgedeckt, der Marktaustritt nur in der Kurzfassung;
progressiv/degressiv fehlt bewusst.
"""
import math

import numpy as np
from manim import (
    BOLD,
    UP,
    Create,
    DashedLine,
    Dot,
    FadeOut,
    GrowFromCenter,
    Line,
    VGroup,
    Write,
)

from mcvideo import (
    MCSzene,
    auftritt,
    aufzaehlung,
    einpassen,
    formel,
    legende,
    lichtpunkt,
    reihe,
    schein,
    text,
    welle,
    zeichnen,
)
from mcvideo.theme import BLAU, BREITE, GRAPH, GRUEN, HERVOR, KOPF_Y, ROSE, TEXT, TEXT_LEISE, TUERKIS

T_MAX = 40
T_WERT = 4  # Zeitpunkt für „Absatz nach 4 Monaten“
T_AUSTRITT = 20  # Nullstelle des Graphen mit Marktaustritt

# a(t) = p(t) * e^(-c t) + d mit p(t) = AL t^3 + BE t^2 + DE
AL, BE, DE, C, D = 0.1, 0.1, -2, 0.25, 5


def a(t: float) -> float:
    return (AL * t**3 + BE * t**2 + DE) * math.exp(-C * t) + D


def da(t: float) -> float:
    return ((3 * AL * t**2 + 2 * BE * t) - C * (AL * t**3 + BE * t**2 + DE)) * math.exp(-C * t)


def austritt(t: float) -> float:
    return (-0.1 * t**3 + 2 * t**2) * math.exp(-0.2 * t)


def _positive_nullstellen(koeffizienten: np.ndarray) -> list[float]:
    return sorted(w.real for w in np.roots(koeffizienten) if abs(w.imag) < 1e-9 and w.real > 0)


# Extremstelle: p' - c p = 0; Wendestellen: p'' - 2c p' + c^2 p = 0 (die e-Funktion kürzt sich)
_P = np.array([AL, BE, 0, DE])
_P1, _P2 = np.polyder(_P), np.polyder(np.polyder(_P))
(T_HOCH,) = _positive_nullstellen(np.polysub(_P1, C * _P))
T_WENDE_1, T_WENDE_2 = _positive_nullstellen(np.polyadd(np.polysub(_P2, 2 * C * _P1), C * C * _P))


def titel(inhalt: str):
    return text(inhalt, groesse=40, gewicht=BOLD)


def merkmal(inhalt: str):
    return text(inhalt, farbe=TEXT_LEISE)


def wert(*tex: str, farbe: str):
    zeile = formel(*tex)
    zeile[-1].set_color(farbe)
    return zeile


def hilfslinien(achsen, t: float, farbe: str) -> VGroup:
    """Senkrecht von der x-Achse und waagrecht von der y-Achse bis zum Graphen."""
    ort = achsen.c2p(t, a(t))
    return VGroup(
        DashedLine(achsen.c2p(t, 0), ort, color=farbe, stroke_width=3, dash_length=0.12),
        DashedLine(achsen.c2p(0, a(t)), ort, color=farbe, stroke_width=3, dash_length=0.12),
    )


class Video(MCSzene):
    def inhalt(self) -> None:
        achsen = self.achsen(
            x=(0, T_MAX, 5), y=(0, 18, 4), x_zahlen=(10, 20, 30), y_zahlen=(4, 8, 12, 16),
            namen=("t", "a(t)"),
        )
        graph = achsen.plot(a, x_range=[0, T_MAX - 0.5], color=GRAPH, stroke_width=6)
        glanz = schein(graph)
        haupt = VGroup(*glanz, graph)  # wird in der Kurzfassung durch den Graphen mit Marktaustritt ersetzt
        self.add(self.buehne(), achsen)

        kopf = reihe(formel("a(t)", groesse=36), text(": monatlicher Absatz", groesse=28), abstand=0.12)
        einpassen(kopf, BREITE - 3).move_to([0.4, KOPF_Y, 0])

        self.einstieg(
            "Was liest du am Graphen der", "Produktlebenszyklusfunktion ab?",
            bild=[*[Create(g) for g in glanz], Create(graph), lichtpunkt(graph.copy())],
            kopf=kopf,
        )

        # ---------- Sachzusammenhang ----------
        bedeutung = legende(
            (formel("a(t)"), text("Absatz in ME/Monat")),
            (formel("t"), text("Monate seit Markteinführung")),
            abstand=0.45,
        )
        self.tafel(bedeutung)
        with self.sprich(
            "Der Graph zeigt den monatlichen Absatz einer Spielkonsole. t ist die Zeit in Monaten seit der Markteinführung."
        ):
            self.play(auftritt(bedeutung[0]), run_time=0.6)
            self.warte_bis(0.45)
            self.play(auftritt(bedeutung[1]), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(bedeutung, shift=0.25 * UP), run_time=0.4)

        # ---------- Markteinführung ----------
        ort_start = achsen.c2p(0, a(0))
        punkt_start = Dot(ort_start, color=HERVOR, radius=0.13)
        start = self.tafel(
            titel("Markteinführung"),
            merkmal("y-Achsenabschnitt"),
            reihe(wert("a(0)=", "3", farbe=HERVOR), text("ME/Monat", farbe=TEXT_LEISE)),
            abstand=0.4,
        )
        with self.sprich("Den Absatz bei der Markteinführung liest du am y-Achsenabschnitt ab: 3 ME pro Monat."):
            self.play(auftritt(start[0]), run_time=0.5)
            self.warte_bis(0.3)
            self.play(GrowFromCenter(punkt_start), welle(ort_start, HERVOR), auftritt(start[1]), run_time=0.7)
            self.warte_bis(0.7)
            self.play(Write(start[2]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(start, shift=0.25 * UP), run_time=0.4)

        # ---------- Hochpunkt ----------
        ort_hoch = achsen.c2p(T_HOCH, a(T_HOCH))
        punkt_hoch = Dot(ort_hoch, color=ROSE, radius=0.13)
        linien_hoch = hilfslinien(achsen, T_HOCH, ROSE)
        hoch = self.tafel(
            titel("Höchster Absatz"),
            merkmal("Hochpunkt"),
            legende(
                (text("Zeitpunkt"), wert(r"t\approx", "11{,}8", farbe=ROSE)),
                (text("Absatz"), wert(r"a\approx", "14{,}2", farbe=ROSE)),
                abstand=0.4,
            ),
            abstand=0.4,
        )
        with self.sprich(
            "Der höchste Absatz ist der Hochpunkt. Sein x-Wert ist der Zeitpunkt: etwa 11,8 Monate. "
            "Sein y-Wert ist der Absatz: 14,2 ME pro Monat."
        ):
            self.play(auftritt(hoch[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(GrowFromCenter(punkt_hoch), welle(ort_hoch, ROSE), auftritt(hoch[1]), run_time=0.7)
            self.warte_bis(0.4)
            self.play(Create(linien_hoch[0]), auftritt(hoch[2][0]), run_time=0.8)
            self.warte_bis(0.75)
            self.play(Create(linien_hoch[1]), auftritt(hoch[2][1]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(hoch, shift=0.25 * UP), FadeOut(linien_hoch), run_time=0.4)

        # ---------- Absatz nach 4 Monaten ----------
        ort_wert = achsen.c2p(T_WERT, a(T_WERT))
        punkt_wert = Dot(ort_wert, color=TUERKIS, radius=0.13)
        linien_wert = hilfslinien(achsen, T_WERT, TUERKIS)
        nach = self.tafel(
            titel("Absatz zu einem Zeitpunkt"),
            merkmal("Funktionswert ablesen"),
            reihe(wert(r"a(4)\approx", "7", farbe=TUERKIS), text("ME/Monat", farbe=TEXT_LEISE)),
            abstand=0.4,
        )
        with self.sprich(
            "Der Absatz zu einem bestimmten Zeitpunkt, z.B. nach 4 Monaten, ist der entsprechende Funktionswert. Etwa 7 ME pro Monat."
        ):
            self.play(auftritt(nach[0]), run_time=0.5)
            self.warte_bis(0.3)
            self.play(Create(linien_wert[0]), auftritt(nach[1]), run_time=0.8)
            self.play(GrowFromCenter(punkt_wert), run_time=0.3)
            self.warte_bis(0.62)
            self.play(Create(linien_wert[1]), run_time=0.7)
            self.warte_bis(0.82)
            self.play(Write(nach[2]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(nach, shift=0.25 * UP), FadeOut(linien_wert), FadeOut(punkt_wert), run_time=0.4)

        # ---------- Wendepunkte ----------
        def tangente(t: float) -> Line:
            ort = achsen.c2p(t, a(t))
            richtung = achsen.c2p(t + 1, a(t) + da(t)) - ort
            richtung = richtung / np.linalg.norm(richtung)
            return Line(ort - 1.0 * richtung, ort + 1.0 * richtung, color=BLAU, stroke_width=5)

        orte_wende = [achsen.c2p(t, a(t)) for t in (T_WENDE_1, T_WENDE_2)]
        punkte_wende = [Dot(ort, color=BLAU, radius=0.13) for ort in orte_wende]
        tangenten = [tangente(t) for t in (T_WENDE_1, T_WENDE_2)]
        wende = self.tafel(
            titel("Anstieg und Rückgang"),
            merkmal("Wendepunkte"),
            legende(
                (text("am stärksten steigend"), wert(r"t\approx", "4{,}5", farbe=BLAU)),
                (text("am stärksten fallend"), wert(r"t\approx", "18{,}7", farbe=BLAU)),
                abstand=0.4,
            ),
            abstand=0.4,
        )
        with self.sprich(
            "Am stärksten steigt der Absatz im ersten Wendepunkt, nach etwa 4,5 Monaten. "
            "Am stärksten fällt er im zweiten, nach knapp 19 Monaten."
        ):
            self.play(auftritt(wende[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(auftritt(wende[1]), run_time=0.5)
            self.warte_bis(0.25)
            self.play(
                GrowFromCenter(punkte_wende[0]), Create(tangenten[0]), welle(orte_wende[0], BLAU),
                auftritt(wende[2][0]), run_time=0.8,
            )
            self.warte_bis(0.65)
            self.play(
                GrowFromCenter(punkte_wende[1]), Create(tangenten[1]), welle(orte_wende[1], BLAU),
                auftritt(wende[2][1]), run_time=0.8,
            )
        self.wait(0.4)
        self.play(FadeOut(wende, shift=0.25 * UP), FadeOut(VGroup(*tangenten)), run_time=0.4)

        # ---------- Langfristiger Absatz ----------
        asymptote = DashedLine(
            achsen.c2p(0, D), achsen.c2p(T_MAX, D), color=GRUEN, stroke_width=4, dash_length=0.2,
        )
        langfristig = self.tafel(
            titel("Langfristiger Absatz"),
            merkmal("waagrechte Asymptote"),
            reihe(wert("y=", "5", farbe=GRUEN), text("ME/Monat", farbe=TEXT_LEISE)),
            abstand=0.4,
        )
        with self.sprich(
            "Für große t nähert sich der Graph einer waagrechten Asymptote. Sie zeigt den langfristigen Absatz: 5 ME pro Monat."
        ):
            self.play(auftritt(langfristig[0]), run_time=0.5)
            self.warte_bis(0.25)
            self.play(Create(asymptote), auftritt(langfristig[1]), run_time=1.2)
            self.warte_bis(0.7)
            self.play(Write(langfristig[2]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(langfristig, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        def stichwort(inhalt: str):
            return text(inhalt, groesse=30, farbe=TEXT_LEISE)

        def kennzahl(inhalt: str, farbe: str = TEXT):
            return text(inhalt, groesse=32, farbe=farbe)

        punkte = aufzaehlung(
            (stichwort("Markteinführung"), kennzahl("y-Achsenabschnitt", HERVOR)),
            (stichwort("höchster Absatz"), kennzahl("Hochpunkt", ROSE)),
            (stichwort("Anstieg, Rückgang"), kennzahl("Wendepunkte", BLAU)),
            (stichwort("langfristig"), kennzahl("waagrechte Asymptote", GRUEN)),
            (stichwort("Marktaustritt"), kennzahl("positive Nullstelle")),
        )
        self.tafel(punkte)
        kurve_austritt = achsen.plot(austritt, x_range=[0, T_AUSTRITT], color=GRAPH, stroke_width=6)
        ort_austritt = achsen.c2p(T_AUSTRITT, 0)
        punkt_austritt = Dot(ort_austritt, color=TEXT, radius=0.14).set_z_index(2)
        with self.sprich(
            "Kurz gesagt: Jede Kennzahl hat ihr Merkmal am Graphen. "
            "Endet der Zyklus mit einem Marktaustritt, ist das die positive Nullstelle."
        ):
            self.warte_bis(0.08)
            self.play(auftritt(punkte[0]), welle(ort_start, HERVOR), run_time=0.5)
            self.warte_bis(0.16)
            self.play(auftritt(punkte[1]), welle(ort_hoch, ROSE), run_time=0.5)
            self.warte_bis(0.24)
            self.play(auftritt(punkte[2]), welle(orte_wende[0], BLAU), welle(orte_wende[1], BLAU), run_time=0.5)
            self.warte_bis(0.34)
            self.play(auftritt(punkte[3]), welle(achsen.c2p(30, D), GRUEN), run_time=0.5)
            self.warte_bis(0.62)
            self.play(
                auftritt(punkte[4]),
                FadeOut(haupt), FadeOut(asymptote), FadeOut(punkt_start), FadeOut(punkt_hoch),
                *[FadeOut(punkt) for punkt in punkte_wende],
                run_time=0.6,
            )
            self.play(*zeichnen(kurve_austritt), run_time=1.2)
            self.play(GrowFromCenter(punkt_austritt), welle(ort_austritt, TEXT), run_time=0.6)
        self.wait(1.5)
