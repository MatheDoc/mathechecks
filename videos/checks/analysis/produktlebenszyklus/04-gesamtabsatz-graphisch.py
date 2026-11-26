"""Check 04 – Gesamtabsatz als Fläche unter dem Graphen deuten und abschätzen.

Kernidee: Monatsbalken (Höhe mal Breite) ergeben zusammen die Fläche unter dem Graphen, den Gesamtabsatz in ME.
Abgeschätzt wird mit Rechtecken; die Höhe des Rechtecks mit gleicher Fläche ist der durchschnittliche Absatz.
Beispiel: a(t) = t^2 * e^(-0,25 t) + 3 aus dem Musterbeispiel des Checks, ohne Abweichung (Zeitraum [6;12],
Aussage „mindestens 60 ME im ersten Halbjahr“). Die Teilaufgaben des Trainings sind abgedeckt (Ausdruck und
Bedeutung des Integrals, Schätzwert, Durchschnitt, Aussage prüfen). Die Grenzen 61 < Fläche < 70 fehlen bewusst.
"""
import math

from manim import BOLD, DOWN, UP, Create, DashedLine, FadeIn, FadeOut, Rectangle, ReplacementTransform, VGroup, Write

from mcvideo import (
    MCSzene,
    auftritt,
    aufzaehlung,
    einpassen,
    formel,
    lichtpunkt,
    reihe,
    schein,
    text,
    welle,
    wortlaut,
)
from mcvideo.theme import BLAU, BREITE, GRAPH, HERVOR, KOPF_Y, ROSE, TEXT_LEISE

T_MAX = 24
Y_MAX = 13
HOEHE_SCHAETZ = 11.2  # Höhe des Rechtecks mit (etwa) gleicher Fläche auf [6;12]


def a(t: float) -> float:
    return t**2 * math.exp(-0.25 * t) + 3


# Gerundete Balkenhöhen a(1) … a(6) wie im Musterbeispiel
BALKEN_0_6 = [round(a(k), 1) for k in range(1, 7)]
assert BALKEN_0_6 == [3.8, 5.4, 7.3, 8.9, 10.2, 11.0]
assert abs(sum(BALKEN_0_6) - 46.6) < 1e-9


def titel(inhalt: str):
    return text(inhalt, groesse=40, gewicht=BOLD)


def leise(inhalt: str, groesse: float = 30):
    return text(inhalt, groesse=groesse, farbe=TEXT_LEISE)


def mit_einheit(zeile, einheit: str):
    return reihe(zeile, leise(einheit), abstand=0.2, grundlinie=True)


class Video(MCSzene):
    def inhalt(self) -> None:
        achsen = self.achsen(
            x=(0, T_MAX, 2), y=(0, Y_MAX, 2), x_zahlen=(6, 12, 18, 24), y_zahlen=(4, 8, 12),
            namen=("t", "a(t)"),
        )
        graph = achsen.plot(a, x_range=[0, T_MAX], color=GRAPH, stroke_width=6).set_z_index(2)
        glanz = schein(graph)
        for g in glanz:
            g.set_z_index(2)
        self.add(self.buehne(), achsen)

        kopf = reihe(formel("a(t)", groesse=36), text(": monatlicher Absatz in ME/Monat", groesse=28), abstand=0.12)
        einpassen(kopf, BREITE - 3).move_to([0.4, KOPF_Y, 0])

        self.einstieg(
            "Wie liest du den Gesamtabsatz", "am Graphen ab?",
            bild=[*[Create(g) for g in glanz], Create(graph), lichtpunkt(graph.copy())],
            kopf=kopf,
        )

        def balken(von: int, hoehe: float, farbe: str) -> Rectangle:
            unten_links, oben_rechts = achsen.c2p(von, 0), achsen.c2p(von + 1, hoehe)
            return Rectangle(
                width=oben_rechts[0] - unten_links[0], height=oben_rechts[1] - unten_links[1],
                stroke_color=farbe, stroke_width=2, fill_color=farbe, fill_opacity=0.35,
            ).move_to((unten_links + oben_rechts) / 2).set_z_index(1)

        # ---------- Fläche = Gesamtabsatz ----------
        balken_6_12 = VGroup(*[balken(k, a(k + 0.5), BLAU) for k in range(6, 12)])
        flaeche = achsen.get_area(graph, x_range=(6, 12), color=BLAU, opacity=0.4).set_z_index(1)
        integral = formel(r"\int_6^{12} a(t)\,dt", farbe=BLAU)
        deutung = VGroup(
            leise("Gesamtabsatz vom Ende des 6."), leise("bis zum Ende des 12. Monats"),
        ).arrange(DOWN, buff=0.12)
        gesamt = self.tafel(
            titel("Gesamtabsatz = Fläche"),
            leise("ein Monat: Höhe · Breite = ME"),
            integral,
            deutung,
            abstand=0.45,
        )
        with self.sprich(
            "a von t gibt an, wie viel pro Monat verkauft wird. In einem Monat sind das Höhe mal Breite: "
            "ein schmaler Balken. Alle Balken vom sechsten bis zum zwölften Monat zusammen ergeben die Fläche "
            "unter dem Graphen: das Integral von sechs bis zwölf, der Gesamtabsatz im zweiten Halbjahr."
        ):
            self.play(auftritt(gesamt[0]), run_time=0.5)
            self.warte_bis(0.2)
            self.play(FadeIn(balken_6_12[0]), auftritt(gesamt[1]), run_time=0.6)
            self.warte_bis(0.35)
            self.play(FadeIn(balken_6_12[1:], lag_ratio=0.3), run_time=1.2)
            self.warte_bis(0.55)
            self.play(ReplacementTransform(balken_6_12, flaeche), run_time=1.0)
            self.warte_bis(0.7)
            self.play(Write(gesamt[2]), run_time=0.8)
            self.warte_bis(0.85)
            self.play(auftritt(gesamt[3]), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(gesamt, shift=0.25 * UP), run_time=0.4)

        # ---------- Schätzen und Durchschnitt ----------
        ecke_links, ecke_rechts = achsen.c2p(6, 0), achsen.c2p(12, HOEHE_SCHAETZ)
        rechteck = Rectangle(
            width=ecke_rechts[0] - ecke_links[0], height=ecke_rechts[1] - ecke_links[1],
            stroke_color=HERVOR, stroke_width=4, fill_color=HERVOR, fill_opacity=0.18,
        ).move_to((ecke_links + ecke_rechts) / 2).set_z_index(3)
        hoehe_linie = DashedLine(
            achsen.c2p(0, HOEHE_SCHAETZ), achsen.c2p(6, HOEHE_SCHAETZ), color=HERVOR, stroke_width=3, dash_length=0.12,
        ).set_z_index(3)
        schaetzwert = formel(r"6\cdot 11{,}2\approx", "67")
        schaetzwert[1].set_color(BLAU)
        durchschnitt = formel("11{,}2", farbe=HERVOR)
        schaetzen = self.tafel(
            titel("Schätzen"),
            leise("Rechteck mit gleicher Fläche"),
            mit_einheit(schaetzwert, "ME"),
            reihe(leise("Durchschnitt:"), mit_einheit(durchschnitt, "ME/Monat"), abstand=0.3, grundlinie=True),
            abstand=0.45,
        )
        with self.sprich(
            "Zum Schätzen legen wir ein Rechteck darüber, das gleich viel Fläche hat: Was oben übersteht, "
            "füllt die Lücken. Höhe etwa elf Komma zwei, Breite sechs: rund siebenundsechzig ME. "
            "Die Höhe des Rechtecks ist der durchschnittliche monatliche Absatz, etwa elf Komma zwei ME pro Monat."
        ):
            self.play(auftritt(schaetzen[0]), run_time=0.5)
            self.warte_bis(0.1)
            self.play(Create(rechteck), auftritt(schaetzen[1]), run_time=1.0)
            self.warte_bis(0.42)
            self.play(Create(hoehe_linie), run_time=0.6)
            self.warte_bis(0.55)
            self.play(Write(schaetzen[2]), run_time=0.8)
            self.warte_bis(0.75)
            self.play(auftritt(schaetzen[3]), welle(achsen.c2p(0, HOEHE_SCHAETZ), HERVOR), run_time=0.7)
        self.wait(0.4)
        self.play(
            FadeOut(schaetzen, shift=0.25 * UP), FadeOut(rechteck), FadeOut(hoehe_linie), FadeOut(flaeche),
            run_time=0.4,
        )

        # ---------- Aussage prüfen ----------
        balken_0_6 = VGroup(*[balken(k, h, ROSE) for k, h in zip(range(6), BALKEN_0_6)])
        summe = formel(r"\int_0^6 a(t)\,dt", r"<3{,}8+5{,}4+\dots+11{,}0")
        summe[1].set_color(ROSE)
        vergleich = formel(r"=46{,}6<60")
        aussage = self.tafel(
            wortlaut("Im ersten Halbjahr werden", "mindestens 60 ME abgesetzt.", signal=("mindestens",)),
            leise("Balken: Höhe am rechten Rand"),
            summe,
            vergleich,
            text("Die Aussage ist falsch.", gewicht=BOLD),
            abstand=0.4,
        )
        with self.sprich(
            "Stimmt die Aussage: Im ersten Halbjahr werden mindestens sechzig ME abgesetzt? "
            "Die Balken mit der Höhe am rechten Rand ragen über den Graphen. Zusammen sind das nur etwa "
            "sechsundvierzig Komma sechs ME, die echte Fläche ist also noch kleiner. Die Aussage ist falsch."
        ):
            self.play(auftritt(aussage[0]), run_time=0.6)
            self.warte_bis(0.3)
            self.play(FadeIn(balken_0_6, lag_ratio=0.25), auftritt(aussage[1]), run_time=1.4)
            self.warte_bis(0.55)
            self.play(Write(aussage[2]), run_time=0.9)
            self.play(Write(aussage[3]), run_time=0.6)
            self.warte_bis(0.88)
            self.play(auftritt(aussage[4]), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(aussage, shift=0.25 * UP), FadeOut(balken_0_6), run_time=0.4)

        # ---------- Kurzfassung ----------
        def stichwort(inhalt: str):
            return text(inhalt, groesse=30, farbe=TEXT_LEISE)

        punkte = aufzaehlung(
            (
                stichwort("Gesamtabsatz"),
                VGroup(
                    text("Fläche unter dem Graphen", groesse=32, farbe=BLAU),
                    formel(r"\int_{t_1}^{t_2} a(t)\,dt", groesse=40, farbe=BLAU),
                ).arrange(DOWN, buff=0.15, aligned_edge=[-1, 0, 0]),
            ),
            (stichwort("schätzen"), text("Rechtecke", groesse=32)),
            (
                stichwort("Durchschnitt"),
                VGroup(
                    text("Höhe des Rechtecks", groesse=32, farbe=HERVOR),
                    text("mit gleicher Fläche", groesse=32, farbe=HERVOR),
                ).arrange(DOWN, buff=0.12, aligned_edge=[-1, 0, 0]),
            ),
        )
        self.tafel(punkte)
        flaeche_ende = achsen.get_area(graph, x_range=(6, 12), color=BLAU, opacity=0.4).set_z_index(1)
        with self.sprich(
            "Kurz gesagt: Der Gesamtabsatz ist die Fläche unter dem Graphen, geschrieben als Integral. "
            "Geschätzt wird mit Rechtecken, Breite mal Höhe. "
            "Der Durchschnitt ist die Höhe des Rechtecks mit gleicher Fläche."
        ):
            self.warte_bis(0.03)
            self.play(auftritt(punkte[0]), FadeIn(flaeche_ende), run_time=0.6)
            self.warte_bis(0.45)
            self.play(auftritt(punkte[1]), run_time=0.5)
            self.warte_bis(0.68)
            self.play(auftritt(punkte[2]), Create(rechteck), run_time=0.8)
        self.wait(1.5)
