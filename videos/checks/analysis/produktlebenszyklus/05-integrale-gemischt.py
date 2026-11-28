"""Check 05 – Kennzahlen des Produktlebenszyklus mit Integralen berechnen.

Kernidee: Pro Monat ist ein Funktionswert (ME/Monat), insgesamt eine Fläche, also ein Integral (ME). Beim Zeitpunkt
zu einem Gesamtabsatz ist die Fläche bekannt und die obere Grenze gesucht.
Beispiel: a(t) = (-0,1 t^3 + 2 t^2) * e^(-0,2 t) aus dem Musterbeispiel des Checks, ohne Abweichung (Marktaustritt
nach 20 Monaten). Die Teilaufgaben des Trainings sind abgedeckt; die Frage „Werden 200 ME erreicht?“ aus dem
Musterbeispiel fehlt bewusst, weil das Training sie nicht stellt.
"""
import math

from manim import (
    BOLD,
    DOWN,
    LEFT,
    UP,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Rectangle,
    ValueTracker,
    VGroup,
    Write,
    always_redraw,
)

from mcvideo import (
    Dezimalzahl,
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
from mcvideo.theme import BLAU, GRAPH, HERVOR, ROSE, TEXT_LEISE

T_ENDE = 20  # Marktaustritt: t^2 (-0,1 t + 2) = 0
Y_MAX = 18
T_WERT = 8
ZIEL = 100  # Gesamtabsatz, dessen Zeitpunkt gesucht ist


def a(t: float) -> float:
    return (-0.1 * t**3 + 2 * t**2) * math.exp(-0.2 * t)


def integral(von: float, bis: float, n: int = 200) -> float:
    """Simpsonregel (n gerade)."""
    h = (bis - von) / n
    summe = a(von) + a(bis) + sum((4 if k % 2 else 2) * a(von + k * h) for k in range(1, n))
    return summe * h / 3


def obere_grenze(ziel: float) -> float:
    """Löst integral(0, z) = ziel durch Halbieren (der Gesamtabsatz wächst auf [0; T_ENDE])."""
    unten, oben = 0.0, float(T_ENDE)
    for _ in range(60):
        mitte = (unten + oben) / 2
        unten, oben = (mitte, oben) if integral(0, mitte) < ziel else (unten, mitte)
    return (unten + oben) / 2


DURCHSCHNITT = integral(0, 6) / 6
Z = obere_grenze(ZIEL)
assert abs(a(T_WERT) - 15.51) < 0.005
assert abs(integral(3, 9) - 83.63) < 0.005
assert abs(integral(0, T_ENDE) - 168.50) < 0.005
assert abs(DURCHSCHNITT - 7.93) < 0.005
assert abs(Z - 9.42) < 0.005


def titel(inhalt: str):
    return text(inhalt, groesse=40, gewicht=BOLD)


def leise(inhalt: str, groesse: float = 30):
    return text(inhalt, groesse=groesse, farbe=TEXT_LEISE)


def mit_einheit(zeile, einheit: str):
    return reihe(zeile, leise(einheit), abstand=0.2, grundlinie=True)


def wert(*tex: str, farbe: str):
    zeile = formel(*tex)
    zeile[-1].set_color(farbe)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        achsen = self.achsen(
            x=(0, 22, 2), y=(0, Y_MAX, 2), x_zahlen=(4, 8, 12, 16, 20), y_zahlen=(5, 10, 15),
            namen=("t", "a(t)"),
        )
        graph = achsen.plot(a, x_range=[0, T_ENDE], color=GRAPH, stroke_width=6).set_z_index(2)
        glanz = schein(graph)
        for g in glanz:
            g.set_z_index(2)
        self.add(self.buehne(), achsen)

        kopf = self.kopf(r"a(t)=(-0{,}1t^3+2t^2)\cdot e^{-0{,}2t}")

        self.einstieg(
            "Wie berechnest du Gesamtabsatz", "und Durchschnitt mit Integralen?",
            bild=[*[Create(g) for g in glanz], Create(graph), lichtpunkt(graph.copy())],
            kopf=kopf,
        )

        def flaeche(von: float, bis: float, farbe: str = BLAU):
            return achsen.get_area(graph, x_range=(von, bis), color=farbe, opacity=0.4).set_z_index(1)

        # ---------- Monatlich oder gesamt ----------
        ort_wert = achsen.c2p(T_WERT, a(T_WERT))
        punkt_wert = Dot(ort_wert, color=ROSE, radius=0.13).set_z_index(3)
        linie_wert = DashedLine(achsen.c2p(T_WERT, 0), ort_wert, color=ROSE, stroke_width=3, dash_length=0.12)
        flaeche_3_9 = flaeche(3, 9)
        unterscheidung = self.tafel(
            titel("Monatlich oder gesamt?"),
            leise("Funktionswert"),
            mit_einheit(wert(r"a(8)\approx", "15{,}51", farbe=ROSE), "ME/Monat"),
            leise("Fläche: Integral"),
            mit_einheit(wert(r"\int_3^9 a(t)\,dt\approx", "83{,}63", farbe=BLAU), "ME"),
            abstand=0.35,
        )
        with self.sprich(
            "Zuerst die wichtigste Unterscheidung. Der monatliche Absatz ist ein Funktionswert: "
            "nach 8 Monaten etwa 15,51 ME pro Monat. "
            "Der Gesamtabsatz ist eine Fläche, also ein Integral: Vom Ende des dritten bis zum Ende des neunten "
            "Monats sind das etwa 83,63 ME."
        ):
            self.play(auftritt(unterscheidung[0]), run_time=0.5)
            self.warte_bis(0.12)
            self.play(auftritt(unterscheidung[1]), Create(linie_wert), GrowFromCenter(punkt_wert), run_time=0.7)
            self.warte_bis(0.25)
            self.play(Write(unterscheidung[2]), welle(ort_wert, ROSE), run_time=0.8)
            self.warte_bis(0.5)
            self.play(auftritt(unterscheidung[3]), FadeIn(flaeche_3_9), run_time=0.8)
            self.warte_bis(0.75)
            self.play(Write(unterscheidung[4]), run_time=0.9)
        self.wait(0.4)
        self.play(
            FadeOut(unterscheidung, shift=0.25 * UP), FadeOut(punkt_wert), FadeOut(linie_wert), FadeOut(flaeche_3_9),
            run_time=0.4,
        )

        # ---------- Ganzer Lebenszyklus ----------
        ort_ende = achsen.c2p(T_ENDE, 0)
        punkt_ende = Dot(ort_ende, color=HERVOR, radius=0.13).set_z_index(3)
        flaeche_ganz = flaeche(0, T_ENDE)
        zyklus = self.tafel(
            titel("Ganzer Lebenszyklus"),
            leise("Ende: angegeben oder Marktaustritt"),
            wert(r"t^2\cdot(-0{,}1t+2)=0\ \Rightarrow\ ", "t=20", farbe=HERVOR),
            mit_einheit(wert(r"\int_0^{20} a(t)\,dt\approx", "168{,}50", farbe=BLAU), "ME"),
            abstand=0.4,
        )
        with self.sprich(
            "Für den ganzen Lebenszyklus integrieren wir von 0 bis zum Ende. "
            "Hier wird das Produkt nach 20 Monaten vom Markt genommen, da ist die Klammer 0. "
            "Insgesamt: etwa 168,5 ME."
        ):
            self.play(auftritt(zyklus[0]), run_time=0.5)
            self.play(auftritt(zyklus[1]), run_time=0.5)
            self.warte_bis(0.4)
            self.play(Write(zyklus[2]), GrowFromCenter(punkt_ende), welle(ort_ende, HERVOR), run_time=0.9)
            self.warte_bis(0.75)
            self.play(FadeIn(flaeche_ganz), Write(zyklus[3]), run_time=0.9)
        self.wait(0.4)
        self.play(FadeOut(zyklus, shift=0.25 * UP), FadeOut(flaeche_ganz), FadeOut(punkt_ende), run_time=0.4)

        # ---------- Durchschnitt ----------
        flaeche_0_6 = flaeche(0, 6)
        links, rechts = achsen.c2p(0, 0), achsen.c2p(6, DURCHSCHNITT)
        rechteck = Rectangle(
            width=rechts[0] - links[0], height=rechts[1] - links[1],
            stroke_color=HERVOR, stroke_width=4, fill_color=HERVOR, fill_opacity=0.18,
        ).move_to((links + rechts) / 2).set_z_index(3)
        mittel = self.tafel(
            titel("Durchschnitt"),
            mit_einheit(wert(r"\frac{1}{6-0}\int_0^6 a(t)\,dt\approx", "7{,}93", farbe=HERVOR), "ME/Monat"),
            VGroup(leise("Höhe des Rechtecks"), leise("mit gleicher Fläche")).arrange(DOWN, buff=0.12),
            abstand=0.45,
        )
        with self.sprich(
            "Durchschnittlicher monatlicher Absatz in den ersten 6 Monaten: Gesamtabsatz geteilt durch 6 Monate. "
            "Das ist die Höhe des Rechtecks mit gleicher Fläche, etwa 7,93 ME pro Monat."
        ):
            self.play(auftritt(mittel[0]), FadeIn(flaeche_0_6), run_time=0.6)
            self.warte_bis(0.2)
            self.play(Write(mittel[1]), run_time=1.0)
            self.warte_bis(0.55)
            self.play(Create(rechteck), auftritt(mittel[2]), run_time=1.0)
        self.wait(0.4)
        self.play(FadeOut(mittel, shift=0.25 * UP), FadeOut(rechteck), FadeOut(flaeche_0_6), run_time=0.4)

        # ---------- Zeitpunkt zu einem Gesamtabsatz ----------
        anteil = ValueTracker(0.001)  # Anteil von Z; bleibt zwischen 0 und 1, damit die Randprüfung nicht anschlägt

        def grenze() -> float:
            return anteil.get_value() * Z

        wachsend = always_redraw(lambda: flaeche(0, grenze()))
        marke = always_redraw(lambda: DashedLine(
            achsen.c2p(grenze(), 0), achsen.c2p(grenze(), Y_MAX - 1),
            color=HERVOR, stroke_width=3, dash_length=0.12,
        ).set_z_index(3))
        zaehler = Dezimalzahl(0, stellen=0, font_size=40, color=BLAU)
        einheit = text("ME", groesse=30, farbe=BLAU).move_to(achsen.c2p(17.5, 15))
        anzeige = VGroup(zaehler, einheit)

        def zaehlen(m) -> None:
            """Die Zahl wächst nach links, das „ME“ bleibt stehen."""
            m.set_value(integral(0, grenze()))
            m.next_to(einheit, LEFT, buff=0.15).align_to(einheit, DOWN)

        zaehlen(zaehler)
        zaehler.add_updater(zaehlen)
        zeitpunkt = self.tafel(
            titel("Zeitpunkt für 100 ME"),
            leise("Fläche bekannt, obere Grenze gesucht"),
            formel(r"\int_0^z a(t)\,dt=100"),
            wert(r"z\approx", "9{,}42", farbe=HERVOR),
            abstand=0.45,
        )
        with self.sprich(
            "Und wann sind insgesamt 100 ME verkauft? Jetzt ist die Fläche bekannt und die obere Grenze gesucht. "
            "Der Rechner löst die Gleichung: nach etwa 9,42 Monaten."
        ):
            self.play(auftritt(zeitpunkt[0]), run_time=0.5)
            self.warte_bis(0.25)
            self.add(wachsend, marke)
            self.play(auftritt(zeitpunkt[1]), FadeIn(anzeige), run_time=0.5)
            self.play(Write(zeitpunkt[2]), anteil.animate.set_value(1), run_time=2.5)
            self.warte_bis(0.75)
            self.play(Write(zeitpunkt[3]), welle(achsen.c2p(Z, 0), HERVOR), run_time=0.8)
        zaehler.clear_updaters()
        self.wait(0.4)
        self.play(FadeOut(zeitpunkt, shift=0.25 * UP), FadeOut(wachsend), FadeOut(marke), FadeOut(anzeige), run_time=0.4)

        # ---------- Kurzfassung ----------
        def stichwort(inhalt: str):
            return text(inhalt, groesse=30, farbe=TEXT_LEISE)

        punkte = aufzaehlung(
            (stichwort("pro Monat"), formel("a(t_0)", groesse=40, farbe=ROSE)),
            (stichwort("insgesamt"), formel(r"\int_{t_1}^{t_2} a(t)\,dt", groesse=40, farbe=BLAU)),
            (stichwort("Durchschnitt"), formel(r"\frac{1}{t_2-t_1}\int_{t_1}^{t_2} a(t)\,dt", groesse=40, farbe=HERVOR)),
            (
                stichwort("Zeitpunkt"),
                VGroup(formel(r"\int_0^z a(t)\,dt=X", groesse=40), text("nach z lösen", groesse=30)).arrange(
                    DOWN, buff=0.12, aligned_edge=LEFT,
                ),
            ),
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: pro Monat der Funktionswert, insgesamt das Integral, der Durchschnitt ist das Integral "
            "geteilt durch die Dauer, und für den Zeitpunkt löst du nach der oberen Grenze."
        ):
            self.warte_bis(0.03)
            self.play(auftritt(punkte[0]), run_time=0.5)
            self.warte_bis(0.2)
            self.play(auftritt(punkte[1]), run_time=0.5)
            self.warte_bis(0.4)
            self.play(auftritt(punkte[2]), run_time=0.5)
            self.warte_bis(0.7)
            self.play(auftritt(punkte[3]), run_time=0.5)
        self.wait(1.5)
