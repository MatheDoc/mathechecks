"""Check 03 – Kennzahlen des Produktlebenszyklus berechnen (ohne Integration).

Kernidee: Die e-Funktion wird nie null. Bei a'(t) = 0 und a''(t) = 0 genügt es deshalb, die Klammer null zu setzen;
alle Kennzahlen folgen demselben Muster (Bedingung aufstellen, Klammer null, einsetzen).
Beispiel: a(t) = (4t + 2) * e^(-0,2 t) + 3 aus dem Musterbeispiel des Checks, ohne Abweichung.
Didaktisch reduziert: Gerechnet werden höchster Absatz, stärkster Rückgang (mit Anstieg am Rand) und langfristiger
Absatz. Markteinführung a(0), Änderungsrate a'(t0) und Zeitraum über c (Rechner) stehen nur in der Kurzfassung;
die hinreichende Bedingung nur über den Vorzeichenwechsel, a'' < 0 fehlt bewusst.
"""
import math

from manim import BOLD, DOWN, UP, Create, DashedLine, Dot, FadeOut, GrowFromCenter, VGroup, Write

from mcvideo import (
    MCSzene,
    auftritt,
    aufzaehlung,
    formel,
    lichtpunkt,
    reihe,
    schein,
    text,
    welle,
)
from mcvideo.theme import BLAU, GRAPH, GRUEN, HERVOR, ROSE, TEXT_LEISE

T_MAX = 30
Y_MAX = 12


def a(t: float) -> float:
    return (4 * t + 2) * math.exp(-0.2 * t) + 3


def da(t: float) -> float:
    return (-0.8 * t + 3.6) * math.exp(-0.2 * t)


T_HOCH = 3.6 / 0.8  # 4,5
T_WENDE = 1.52 / 0.16  # 9,5
assert abs(a(T_HOCH) - 11.13) < 0.005
assert abs(da(T_WENDE) + 0.60) < 0.005 and abs(da(0) - 3.6) < 1e-9


def titel(inhalt: str):
    return text(inhalt, groesse=40, gewicht=BOLD)


def leise(inhalt: str, groesse: float = 30):
    return text(inhalt, groesse=groesse, farbe=TEXT_LEISE)


def mit_einheit(zeile, einheit: str):
    return reihe(zeile, leise(einheit), abstand=0.2, grundlinie=True)


class Video(MCSzene):
    def inhalt(self) -> None:
        achsen = self.achsen(
            x=(0, T_MAX, 5), y=(0, Y_MAX, 2), x_zahlen=(10, 20, 30), y_zahlen=(4, 8, 12),
            namen=("t", "a(t)"),
        )
        graph = achsen.plot(a, x_range=[0, T_MAX], color=GRAPH, stroke_width=6).set_z_index(1)
        glanz = schein(graph)
        self.add(self.buehne(), achsen)

        kopf = self.kopf(r"a(t)=(4t+2)\cdot e^{-0{,}2t}+3")

        self.einstieg(
            "Wie berechnest du die Kennzahlen", "eines Produktlebenszyklus?",
            zusatz="(ohne Integral)",
            sprechtext="Wie berechnest du die Kennzahlen eines Produktlebenszyklus, ohne Integral?",
            bild=[*[Create(g) for g in glanz], Create(graph), lichtpunkt(graph.copy())],
            kopf=kopf,
        )

        # ---------- Der Trick: e-Funktion wird nie null ----------
        trick = self.tafel(
            titel("Der Trick"),
            reihe(formel(r"e^{-0{,}2t}>0"), leise("wird nie null"), abstand=0.35, grundlinie=True),
            formel(r"(\dots)", r"\cdot e^{-0{,}2t}=0"),
            formel(r"\Leftrightarrow\quad", r"(\dots)", r"=0"),
            abstand=0.45,
        )
        trick[2][0].set_color(HERVOR)
        trick[3][1].set_color(HERVOR)
        with self.sprich(
            "Die Ableitungen haben immer die Form Klammer mal e hoch minus null Komma zwei t. "
            "Die e-Funktion wird nie null. Also setzen wir einfach die Klammer null."
        ):
            self.play(auftritt(trick[0]), run_time=0.5)
            self.warte_bis(0.1)
            self.play(auftritt(trick[2]), run_time=0.6)
            self.warte_bis(0.5)
            self.play(auftritt(trick[1]), run_time=0.6)
            self.warte_bis(0.75)
            self.play(Write(trick[3]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(trick, shift=0.25 * UP), run_time=0.4)

        # ---------- Höchster Absatz ----------
        ort_hoch = achsen.c2p(T_HOCH, a(T_HOCH))
        punkt_hoch = Dot(ort_hoch, color=ROSE, radius=0.13).set_z_index(3)
        linie_hoch = DashedLine(achsen.c2p(T_HOCH, 0), ort_hoch, color=ROSE, stroke_width=3, dash_length=0.12)
        ableitung = formel(r"a'(t)=", r"(-0{,}8t+3{,}6)", r"\cdot e^{-0{,}2t}")
        ableitung[1].set_color(HERVOR)
        loesung = formel(r"-0{,}8t+3{,}6=0", r"\ \Rightarrow\ ", r"t=4{,}5")
        loesung[0].set_color(HERVOR)
        loesung[2].set_color(ROSE)
        hoehe = formel(r"a(4{,}5)\approx", r"11{,}13")
        hoehe[1].set_color(ROSE)
        hoch = self.tafel(
            titel("Höchster Absatz"),
            ableitung,
            loesung,
            reihe(leise("Vorzeichenwechsel"), formel(r"+\to-", groesse=40), leise("Maximum"), abstand=0.25, grundlinie=True),
            mit_einheit(hoehe, "ME/Monat"),
            abstand=0.4,
        )
        with self.sprich(
            "Höchster Absatz: a Strich gleich null. Die Klammer ist null bei t gleich vier Komma fünf "
            "und wechselt dort von plus nach minus: ein Maximum. "
            "Eingesetzt in a: etwa elf Komma eins drei ME pro Monat."
        ):
            self.play(auftritt(hoch[0]), run_time=0.5)
            self.play(auftritt(hoch[1]), run_time=0.6)
            self.warte_bis(0.2)
            self.play(Write(hoch[2]), run_time=0.9)
            self.play(Create(linie_hoch), GrowFromCenter(punkt_hoch), welle(ort_hoch, ROSE), run_time=0.7)
            self.warte_bis(0.45)
            self.play(auftritt(hoch[3]), run_time=0.6)
            self.warte_bis(0.75)
            self.play(Write(hoch[4]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(hoch, shift=0.25 * UP), run_time=0.4)

        # ---------- Stärkster Rückgang und Anstieg ----------
        ort_wende = achsen.c2p(T_WENDE, a(T_WENDE))
        punkt_wende = Dot(ort_wende, color=BLAU, radius=0.13).set_z_index(3)
        linie_wende = DashedLine(achsen.c2p(T_WENDE, 0), ort_wende, color=BLAU, stroke_width=3, dash_length=0.12)
        ort_start = achsen.c2p(0, a(0))
        punkt_start = Dot(ort_start, color=BLAU, radius=0.13).set_z_index(3)
        zweite = formel(r"a''(t)=", r"(0{,}16t-1{,}52)", r"\cdot e^{-0{,}2t}")
        zweite[1].set_color(HERVOR)
        wende = formel(r"0{,}16t-1{,}52=0", r"\ \Rightarrow\ ", r"t=9{,}5")
        wende[0].set_color(HERVOR)
        wende[2].set_color(BLAU)
        rueckgang = formel(r"a'(9{,}5)\approx", r"-0{,}60")
        rueckgang[1].set_color(BLAU)
        anstieg = formel(r"a'(0)=", r"3{,}6")
        anstieg[1].set_color(BLAU)
        rate = self.tafel(
            titel("Stärkster Rückgang"),
            zweite,
            wende,
            mit_einheit(rueckgang, "ME/Monat pro Monat"),
            reihe(leise("stärkster Anstieg am Rand:"), anstieg, abstand=0.3, grundlinie=True),
            abstand=0.4,
        )
        with self.sprich(
            "Stärkster Rückgang: a zwei Strich gleich null, also t gleich neun Komma fünf. "
            "Dort fällt der Absatz um etwa null Komma sechs ME pro Monat pro Monat. "
            "Eine weitere Wendestelle gibt es nicht, der stärkste Anstieg liegt deshalb am Rand: "
            "bei der Markteinführung, mit drei Komma sechs."
        ):
            self.play(auftritt(rate[0]), run_time=0.5)
            self.play(auftritt(rate[1]), run_time=0.6)
            self.warte_bis(0.12)
            self.play(Write(rate[2]), run_time=0.9)
            self.play(Create(linie_wende), GrowFromCenter(punkt_wende), welle(ort_wende, BLAU), run_time=0.7)
            self.warte_bis(0.3)
            self.play(Write(rate[3]), run_time=0.8)
            self.warte_bis(0.72)
            self.play(GrowFromCenter(punkt_start), welle(ort_start, BLAU), auftritt(rate[4]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(rate, shift=0.25 * UP), run_time=0.4)

        # ---------- Langfristiger Absatz ----------
        asymptote = DashedLine(
            achsen.c2p(0, 3), achsen.c2p(T_MAX, 3), color=GRUEN, stroke_width=4, dash_length=0.15,
        ).set_z_index(2)
        grenzwert = formel(r"\lim_{t\to\infty}a(t)=", r"0", r"+3=", r"3")
        grenzwert[3].set_color(GRUEN)
        langfristig = self.tafel(
            titel("Langfristiger Absatz"),
            reihe(formel(r"(4t+2)\cdot e^{-0{,}2t}\to 0"), abstand=0.3),
            mit_einheit(grenzwert, "ME/Monat"),
            VGroup(
                leise("ohne Konstante: Marktaustritt,", groesse=28),
                leise("positive Nullstelle der Klammer", groesse=28),
            ).arrange(DOWN, buff=0.15),
            abstand=0.4,
        )
        with self.sprich(
            "Langfristig geht Klammer mal e-Funktion gegen null, übrig bleibt die Drei: "
            "Auf Dauer werden etwa drei ME pro Monat abgesetzt. "
            "Ohne die Konstante endet der Zyklus meist mit dem Marktaustritt, an der positiven Nullstelle der Klammer."
        ):
            self.play(auftritt(langfristig[0]), run_time=0.5)
            self.play(auftritt(langfristig[1]), run_time=0.6)
            self.warte_bis(0.25)
            self.play(Write(langfristig[2]), Create(asymptote), run_time=1.0)
            self.warte_bis(0.6)
            self.play(auftritt(langfristig[3]), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(langfristig, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        def stichwort(inhalt: str):
            return text(inhalt, groesse=30, farbe=TEXT_LEISE)

        punkte = aufzaehlung(
            (stichwort("Markteinführung"), formel("a(0)", groesse=40)),
            (stichwort("höchster Absatz"), formel("a'(t)=0", groesse=40, farbe=ROSE)),
            (
                stichwort("Anstieg, Rückgang"),
                reihe(formel("a''(t)=0", groesse=40, farbe=BLAU), text(", Rand", groesse=32, farbe=BLAU), abstand=0.1, grundlinie=True),
            ),
            (stichwort("langfristig"), formel(r"\lim\limits_{t\to\infty}a(t)", groesse=40, farbe=GRUEN)),
            (stichwort("Absatz über c"), formel("a(t)=c", groesse=40)),
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Markteinführung: a von null. Höchster Absatz: a Strich gleich null. "
            "Stärkster Anstieg oder Rückgang: a zwei Strich gleich null, Randstellen mitprüfen. "
            "Langfristig: der Grenzwert. Und über einem Wert c liegt der Absatz zwischen den Lösungen von a von t gleich c."
        ):
            self.warte_bis(0.03)
            self.play(auftritt(punkte[0]), welle(ort_start, GRAPH), run_time=0.5)
            self.warte_bis(0.17)
            self.play(auftritt(punkte[1]), welle(ort_hoch, ROSE), run_time=0.5)
            self.warte_bis(0.33)
            self.play(auftritt(punkte[2]), welle(ort_wende, BLAU), welle(ort_start, BLAU), run_time=0.5)
            self.warte_bis(0.6)
            self.play(auftritt(punkte[3]), welle(achsen.c2p(25, 3), GRUEN), run_time=0.5)
            self.warte_bis(0.72)
            self.play(auftritt(punkte[4]), run_time=0.5)
        self.wait(1.5)
