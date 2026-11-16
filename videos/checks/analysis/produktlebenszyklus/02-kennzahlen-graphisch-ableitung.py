"""Check 02 – Graph der Ableitung einer Produktlebenszyklusfunktion interpretieren.

Kernidee: Der Graph zeigt die Änderung des monatlichen Absatzes, nicht den Absatz selbst. Seine y-Werte sind
Änderungsraten; aus Vorzeichen, Nullstelle und Extrema liest man die Kennzahlen ab.
Beispiel: a(t) = t^2 * e^(-0,25 t) + 3 aus dem Musterbeispiel des Checks, a'(t) = (2t - 0,25 t^2) * e^(-0,25 t).
Im Video steht nur der Graph von a'. Die Teilaufgaben des Trainings sind abgedeckt (höchster Absatz, stärkster
Anstieg und Rückgang, Änderungsrate zu einem Zeitpunkt, wachsend oder fallend); Randstellen fehlen bewusst.
"""
import math

from manim import BOLD, DOWN, LEFT, UP, Create, DashedLine, Dot, FadeOut, GrowFromCenter, Line, VGroup, Write

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
)
from mcvideo.theme import BLAU, BREITE, GRAPH, GRUEN, HERVOR, KOPF_Y, ROSE, TEXT_LEISE

T_MAX = 30
Y_MIN, Y_MAX = -1.2, 2.4
T_WERT = 5  # Zeitpunkt für „Änderungsrate nach 5 Monaten“
T_NULL = 8  # Nullstelle von a'


def da(t: float) -> float:
    return (2 * t - 0.25 * t**2) * math.exp(-0.25 * t)


# a''(t) = 0 für a'(t) = (2t - 0,25 t^2) e^(-0,25 t): t^2 - 16 t + 32 = 0
T_HOCH = 8 - math.sqrt(32)
T_TIEF = 8 + math.sqrt(32)


def titel(inhalt: str):
    return text(inhalt, groesse=40, gewicht=BOLD)


def merkmal(*teile: str):
    """Leise Zeile; ein Teil in $…$ wird als Formel gesetzt (etwa a'), der Rest als Text."""
    return reihe(
        *[
            formel(teil[1:-1], groesse=40, farbe=TEXT_LEISE) if teil.startswith("$") else text(teil, farbe=TEXT_LEISE)
            for teil in teile
        ],
        abstand=0.15,
        grundlinie=True,
    )


def wert(*tex: str, farbe: str):
    zeile = formel(*tex)
    zeile[-1].set_color(farbe)
    return zeile


def hilfslinien(achsen, t: float, farbe: str) -> VGroup:
    """Senkrecht von der t-Achse und waagrecht von der y-Achse bis zum Graphen."""
    ort = achsen.c2p(t, da(t))
    return VGroup(
        DashedLine(achsen.c2p(t, 0), ort, color=farbe, stroke_width=3, dash_length=0.12),
        DashedLine(achsen.c2p(0, da(t)), ort, color=farbe, stroke_width=3, dash_length=0.12),
    )


class Video(MCSzene):
    def inhalt(self) -> None:
        achsen = self.achsen(
            x=(0, T_MAX, 5), y=(Y_MIN, Y_MAX, 1), x_zahlen=(10, 20, 30), y_zahlen=(-1, 1, 2),
            namen=("t", "a'(t)"),
        )
        # Der Graph taucht unter die t-Achse: Die Zahlen der t-Achse stehen deshalb am unteren Rand der Bühne.
        for zahl in achsen.x_axis.numbers:
            zahl.set_y(achsen.c2p(0, Y_MIN)[1] + 0.25)
        beschriftung_y = achsen.submobjects[-1]
        graph = achsen.plot(da, x_range=[0, T_MAX], color=GRAPH, stroke_width=6).set_z_index(1)
        glanz = schein(graph)
        for g in glanz:
            g.set_z_index(1)
        self.add(self.buehne(), achsen)

        kopf = reihe(
            formel("a'(t)", groesse=36),
            text(": Änderung des monatlichen Absatzes", groesse=28),
            abstand=0.12,
        )
        einpassen(kopf, BREITE - 3).move_to([0.4, KOPF_Y, 0])

        self.einstieg(
            "Was liest du am Graphen der Ableitung", "der Produktlebenszyklusfunktion ab?",
            bild=[*[Create(g) for g in glanz], Create(graph), lichtpunkt(graph.copy())],
            kopf=kopf,
        )

        # ---------- Sachzusammenhang: a' ist die Änderung ----------
        bedeutung = legende(
            (formel("a(t)"), text("monatlicher Absatz", groesse=30)),
            (formel("a'(t)", farbe=BLAU), text("Änderung des monatlichen Absatzes", groesse=30, gewicht=BOLD, farbe=BLAU)),
            (formel("t"), text("Monate seit Markteinführung", groesse=30)),
            abstand=0.45,
        )
        self.tafel(bedeutung)
        with self.sprich(
            "Der monatliche Absatz einer Spielkonsole wird durch a von t beschrieben. "
            "Aufpassen: Dieser Graph zeigt a Strich: die Änderung des monatlichen Absatzes!"
        ):
            self.play(auftritt(bedeutung[0]), run_time=0.6)
            self.warte_bis(0.45)
            self.play(
                auftritt(bedeutung[1]), welle(beschriftung_y.get_center(), BLAU),
                run_time=0.8,
            )
            self.warte_bis(0.8)
            self.play(auftritt(bedeutung[2]), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(bedeutung, shift=0.25 * UP), run_time=0.4)

        # ---------- Änderungsrate ablesen ----------
        ort_wert = achsen.c2p(T_WERT, da(T_WERT))
        punkt_wert = Dot(ort_wert, color=BLAU, radius=0.13).set_z_index(3)
        linien_wert = hilfslinien(achsen, T_WERT, BLAU)
        rate = self.tafel(
            titel("Änderungsrate"),
            merkmal("y-Wert von", "$a'$", "ablesen"),
            reihe(wert(r"a'(5)\approx", "1{,}1", farbe=BLAU), text("ME/Monat pro Monat", farbe=TEXT_LEISE)),
            abstand=0.4,
        )
        with self.sprich(
            "Ein y-Wert ist deshalb kein Absatz, sondern eine Änderungsrate: "
            "Nach fünf Monaten wächst der Absatz um etwa eins Komma eins ME pro Monat pro Monat."
        ):
            self.play(auftritt(rate[0]), run_time=0.5)
            self.warte_bis(0.3)
            self.play(Create(linien_wert[0]), auftritt(rate[1]), run_time=0.8)
            self.play(GrowFromCenter(punkt_wert), run_time=0.3)
            self.warte_bis(0.6)
            self.play(Create(linien_wert[1]), run_time=0.7)
            self.warte_bis(0.75)
            self.play(Write(rate[2]), run_time=0.9)
        self.wait(0.4)
        self.play(FadeOut(rate, shift=0.25 * UP), FadeOut(linien_wert), run_time=0.4)

        # ---------- Wachsend oder fallend ----------
        # Intervalle auf der t-Achse: a' positiv (Absatz wachsend) bzw. negativ (Absatz fallend)
        intervall_plus = Line(achsen.c2p(0, 0), achsen.c2p(T_NULL, 0), color=GRUEN, stroke_width=10).set_z_index(2)
        intervall_minus = Line(achsen.c2p(T_NULL, 0), achsen.c2p(T_MAX, 0), color=ROSE, stroke_width=10).set_z_index(2)
        vorzeichen = self.tafel(
            titel("Absatz wachsend oder fallend"),
            merkmal("Vorzeichen von", "$a'$"),
            legende(
                (formel("a'(t)>0", farbe=GRUEN), text("Absatz wachsend", farbe=GRUEN)),
                (formel("a'(t)<0", farbe=ROSE), text("Absatz fallend", farbe=ROSE)),
                abstand=0.4,
            ),
            abstand=0.4,
        )
        with self.sprich(
            "Oberhalb der t-Achse ist a Strich positiv, der Absatz wächst. "
            "Unterhalb ist a Strich negativ, der Absatz fällt."
        ):
            self.play(auftritt(vorzeichen[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(auftritt(vorzeichen[1]), run_time=0.4)
            self.warte_bis(0.2)
            self.play(Create(intervall_plus), auftritt(vorzeichen[2][0]), run_time=0.8)
            self.warte_bis(0.62)
            self.play(Create(intervall_minus), auftritt(vorzeichen[2][1]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(vorzeichen, shift=0.25 * UP), run_time=0.4)

        # ---------- Höchster Absatz ----------
        ort_null = achsen.c2p(T_NULL, 0)
        punkt_null = Dot(ort_null, color=HERVOR, radius=0.13).set_z_index(3)
        null = self.tafel(
            titel("Höchster Absatz"),
            merkmal("Nullstelle"),
            reihe(text("Vorzeichenwechsel", farbe=TEXT_LEISE), formel(r"+\ \to\ -")),
            wert("t=", "8", farbe=HERVOR),
            text("Absatzhöhe: nicht ablesbar", groesse=28, farbe=TEXT_LEISE),
            abstand=0.35,
        )
        with self.sprich(
            "Der Absatz ist am höchsten, wo er von wachsend zu fallend wechselt: an der Nullstelle mit Vorzeichenwechsel "
            "von plus nach minus, hier nach acht Monaten. Die Absatzhöhe verrät dieser Graph nicht."
        ):
            self.play(auftritt(null[0]), run_time=0.5)
            self.warte_bis(0.3)
            self.play(GrowFromCenter(punkt_null), welle(ort_null, HERVOR), auftritt(null[1]), run_time=0.7)
            self.warte_bis(0.45)
            self.play(auftritt(null[2]), run_time=0.6)
            self.warte_bis(0.6)
            self.play(Write(null[3]), run_time=0.7)
            self.warte_bis(0.82)
            self.play(auftritt(null[4]), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(null, shift=0.25 * UP), run_time=0.4)

        # ---------- Stärkster Anstieg und Rückgang ----------
        orte_extrem = [achsen.c2p(t, da(t)) for t in (T_HOCH, T_TIEF)]
        punkte_extrem = [
            Dot(orte_extrem[0], color=GRUEN, radius=0.13).set_z_index(3),
            Dot(orte_extrem[1], color=ROSE, radius=0.13).set_z_index(3),
        ]
        marken = [
            DashedLine(achsen.c2p(t, 0), ort, color=farbe, stroke_width=3, dash_length=0.12)
            for t, ort, farbe in zip((T_HOCH, T_TIEF), orte_extrem, (GRUEN, ROSE))
        ]
        extrem = self.tafel(
            titel("Anstieg und Rückgang"),
            merkmal("Hoch- und Tiefpunkt von", "$a'$"),
            legende(
                (text("stärkster Anstieg"), wert(r"t\approx", "2{,}3", farbe=GRUEN)),
                (text("stärkster Rückgang"), wert(r"t\approx", "13{,}7", farbe=ROSE)),
                abstand=0.4,
            ),
            abstand=0.4,
        )
        with self.sprich(
            "Am stärksten steigt der Absatz im Hochpunkt von a Strich, nach etwa zwei Komma drei Monaten. "
            "Am stärksten fällt er im Tiefpunkt, nach etwa dreizehn Komma sieben Monaten."
        ):
            self.play(auftritt(extrem[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(auftritt(extrem[1]), run_time=0.5)
            self.warte_bis(0.22)
            self.play(
                GrowFromCenter(punkte_extrem[0]), Create(marken[0]), welle(orte_extrem[0], GRUEN),
                auftritt(extrem[2][0]), run_time=0.8,
            )
            self.warte_bis(0.62)
            self.play(
                GrowFromCenter(punkte_extrem[1]), Create(marken[1]), welle(orte_extrem[1], ROSE),
                auftritt(extrem[2][1]), run_time=0.8,
            )
        self.wait(0.4)
        self.play(FadeOut(extrem, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        def stichwort(inhalt: str):
            return text(inhalt, groesse=30, farbe=TEXT_LEISE)

        def zeilen(*paare: tuple[str, str]) -> VGroup:
            """Mehrzeiliges Stichwort bzw. mehrzeilige Angabe: je Zeile eine Farbe."""
            return VGroup(*[text(inhalt, groesse=32, farbe=farbe) for inhalt, farbe in paare]).arrange(
                DOWN, buff=0.15, aligned_edge=LEFT,
            )

        punkte = aufzaehlung(
            (
                stichwort("Änderungsrate"),
                reihe(
                    text("y-Werte von", groesse=32, farbe=BLAU), formel("a'", groesse=40, farbe=BLAU),
                    abstand=0.15, grundlinie=True,
                ),
            ),
            (
                stichwort("wachsend / fallend"),
                reihe(formel("a'>0", groesse=40, farbe=GRUEN), formel("/"), formel("a'<0", groesse=40, farbe=ROSE), abstand=0.2),
            ),
            (
                stichwort("höchster Absatz"),
                reihe(text("Nullstelle", groesse=32, farbe=HERVOR), formel(r"+\to-", farbe=HERVOR), abstand=0.2),
            ),
            (
                VGroup(*[stichwort(z) for z in ("stärkster Anstieg", "stärkster Rückgang")]).arrange(
                    DOWN, buff=0.15, aligned_edge=LEFT,
                ),
                zeilen(("Hochpunkt", GRUEN), ("Tiefpunkt", ROSE)),
            ),
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Die y-Werte sind Änderungen des Absatzes. Das Vorzeichen gibt an, ob wachsend oder fallend, "
            "die Nullstelle den höchsten Absatz, Hoch- und Tiefpunkt zeigen den stärksten Anstieg und Rückgang."
        ):
            self.warte_bis(0.05)
            self.play(auftritt(punkte[0]), welle(ort_wert, BLAU), run_time=0.5)
            self.warte_bis(0.3)
            self.play(
                auftritt(punkte[1]), welle(achsen.c2p(4, 0), GRUEN), welle(achsen.c2p(20, 0), ROSE), run_time=0.5,
            )
            self.warte_bis(0.55)
            self.play(auftritt(punkte[2]), welle(ort_null, HERVOR), run_time=0.5)
            self.warte_bis(0.75)
            self.play(
                auftritt(punkte[3]), welle(orte_extrem[0], GRUEN), welle(orte_extrem[1], ROSE), run_time=0.5,
            )
        self.wait(1.5)
