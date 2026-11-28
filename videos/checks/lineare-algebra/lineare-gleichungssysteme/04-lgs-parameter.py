"""Check 04 – LGS mit Parameter.

Kernidee: Der Gauß-Algorithmus liefert eine Nullzeile, also 0 = 0. Damit ist x_3 frei wählbar: x_3 = t,
dann rückwärts einsetzen mit t. Jedes t liefert eine Lösung.
Beispiel: unverändert aus dem Musterbeispiel des Checks; zusätzlich die Lösung für t = 4.
"""
from manim import (
    DOWN,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    LaggedStart,
    MathTex,
    ReplacementTransform,
    TransformFromCopy,
    VGroup,
    Write,
)

from mcvideo import ErweiterteMatrix, MCSzene, auftritt, formel, kurzfassung, legende, reihe, schritt, text, welle
from mcvideo.theme import GRUEN, HERVOR, ROSE, TEXT, TEXT_LEISE

LGS = [
    [1, 1, 2, 5],
    [2, 1, 3, 8],
    [3, 2, 5, 13],
]
G_RECHNUNG = 44
zeilenname = ErweiterteMatrix.zeilenname


def faerben(zeile: MathTex, farben: dict[int, str]) -> MathTex:
    for index, farbe in farben.items():
        zeile[index].set_color(farbe)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.8)
        m = self.auf_buehne(
            ErweiterteMatrix(LGS, breiteste_umformung=zeilenname(2) + r"-3\cdot" + zeilenname(0))
        )
        gleichungen = self.auf_buehne(m.gleichungen())
        self.add(karte)

        self.einstieg(
            "Wie löst du ein LGS", "mit unendlich vielen Lösungen?",
            bild=[LaggedStart(*[Write(zeile) for zeile in gleichungen], lag_ratio=0.35)],
            sprechtext="Wie löst du ein lineares Gleichungssystem mit unendlich vielen Lösungen?",
        )

        # ---------- Schritt 1: Gauß-Algorithmus ----------
        uebergang = m.aus_gleichungen()
        kopf1 = schritt(1, "Gauß-Algorithmus")
        probe = m.nebenrechnung(0, 1, 1, 0)  # legt nur die Höhe fest
        self.tafel(kopf1, probe, abstand=0.6)
        kopf1.set_x(0)
        y = probe[0][0][0].get_y()
        with self.sprich("Schritt 1: der Gauß-Algorithmus in Matrixform, wie immer."):
            self.play(auftritt(kopf1), run_time=0.5)
            self.warte_bis(0.4)
            self.play(*uebergang, run_time=1.5)

        self.zeilenumformung(m, 1, 2, 0, y=y, sprechtext="Zeile 2 minus 2-mal Zeile 1.")
        self.zeilenumformung(m, 2, 3, 0, y=y, sprechtext="Zeile 3 minus 3-mal Zeile 1.")
        nullzeile = m.eintraege[2]
        self.zeilenumformung(
            m, 2, 1, 1, y=y, farben=dict.fromkeys(range(4), HERVOR),
            sprechtext="Jetzt Zeile 3 minus Zeile 2: Die ganze Zeile wird 0.",
        )
        self.play(FadeOut(kopf1, shift=0.25 * UP), run_time=0.4)

        # ---------- Schritt 2: Parameter ----------
        kopf2 = schritt(2, "Parameter")
        nullgleichung = formel(r"0\cdot x_3=0", groesse=G_RECHNUNG)
        jedes = reihe(
            text("gilt für jedes", groesse=34, farbe=TEXT_LEISE), formel("x_3", groesse=40, farbe=TEXT_LEISE),
            abstand=0.15, grundlinie=True,
        )
        parameter = faerben(
            formel("x_3=", "t", r",\quad ", "t", r"\in\mathbb{R}", groesse=G_RECHNUNG), {1: HERVOR, 3: HERVOR},
        )
        self.tafel(kopf2, nullgleichung, jedes, parameter, abstand=0.5)
        with self.sprich(
            "Schritt 2: der Parameter. Die letzte Zeile heißt 0 mal x drei gleich 0. "
            "Das stimmt für jedes x drei. Wir setzen x drei gleich t, für eine beliebige Zahl t."
        ):
            self.play(auftritt(kopf2), run_time=0.5)
            self.warte_bis(0.2)
            self.play(m.betonen(2), Write(nullgleichung), run_time=0.9)
            self.warte_bis(0.5)
            self.play(auftritt(jedes), run_time=0.5)
            self.warte_bis(0.7)
            self.play(Write(parameter), run_time=0.9)
        self.wait(0.5)

        # ---------- Schritt 3: Rückwärtseinsetzen ----------
        kopf3 = schritt(3, "Rückwärts einsetzen")
        g3 = faerben(formel("x_3=", "t", groesse=G_RECHNUNG), {1: HERVOR})
        g2 = faerben(
            formel("-x_2-", "t", "=-2", r"\ \Rightarrow\ x_2=", "2-t", groesse=G_RECHNUNG), {1: HERVOR, 4: ROSE},
        )
        g1 = faerben(
            formel("x_1+(", "2-t", ")+2", "t", "=5", r"\ \Rightarrow\ x_1=", "3-t", groesse=G_RECHNUNG),
            {1: ROSE, 3: HERVOR, 6: GRUEN},
        )
        zeilen = legende(
            (formel(zeilenname(2), groesse=36, farbe=TEXT_LEISE), g3),
            (formel(zeilenname(1), groesse=36, farbe=TEXT_LEISE), g2),
            (formel(zeilenname(0), groesse=36, farbe=TEXT_LEISE), g1),
            abstand=0.6,
        )
        self.tafel(kopf3, zeilen, abstand=0.7)
        unter_diagonale = [m.eintraege[1][0], m.eintraege[2][0], m.eintraege[2][1]]

        self.play(
            FadeOut(VGroup(kopf2, nullgleichung, jedes, parameter[2:]), shift=0.25 * UP),
            ReplacementTransform(parameter[:2], g3),
            FadeIn(zeilen[0][0]),
            auftritt(kopf3),
            *[eintrag.animate.set_color(TEXT_LEISE) for eintrag in {*unter_diagonale, *nullzeile}],
            run_time=0.8,
        )
        with self.sprich(
            "Schritt 3: rückwärts einsetzen. Zeile 2 heißt minus x zwei minus t gleich minus 2. "
            "Also x zwei gleich 2 minus t."
        ):
            self.warte_bis(0.25)
            self.play(m.betonen(1), FadeIn(zeilen[1][0]), run_time=0.5)
            self.play(Write(g2[0]), TransformFromCopy(g3[1], g2[1]), Write(g2[2]), run_time=0.9)
            self.warte_bis(0.75)
            self.play(FadeIn(g2[3]), FadeIn(g2[4], scale=1.4), run_time=0.5)
        with self.sprich("Beides in Zeile 1: x eins gleich 3 minus t."):
            self.play(m.betonen(0), FadeIn(zeilen[2][0]), run_time=0.5)
            self.play(
                Write(g1[0]), TransformFromCopy(g2[4], g1[1]), Write(g1[2]), TransformFromCopy(g3[1], g1[3]),
                Write(g1[4]), run_time=1.0,
            )
            self.warte_bis(0.6)
            self.play(FadeIn(g1[5]), FadeIn(g1[6], scale=1.4), run_time=0.5)
        self.wait(0.8)

        # ---------- Lösung in die Kopfzeile, Beispiel t = 4 ----------
        loesung = faerben(
            self.kopf("x_1=", "3-t", r",\ x_2=", "2-t", r",\ x_3=", "t"), {1: GRUEN, 3: ROSE, 5: HERVOR},
        )
        rest = VGroup(kopf3, *[zeile[0] for zeile in zeilen], g3[0], *g2[:4], *g1[:6])
        self.play(
            FadeOut(rest, shift=0.25 * UP),
            ReplacementTransform(g1[6], loesung[1]),
            ReplacementTransform(g2[4], loesung[3]),
            ReplacementTransform(g3[1], loesung[5]),
            FadeIn(VGroup(loesung[0], loesung[2], loesung[4])),
            *[eintrag.animate.set_color(TEXT) for eintrag in {*unter_diagonale, *nullzeile}],
            run_time=0.9,
        )

        wahl = faerben(formel("t=", "4", groesse=G_RECHNUNG), {1: HERVOR})
        beispiel = VGroup(
            faerben(formel("x_1=3-", "4", "=", "-1", groesse=G_RECHNUNG), {1: HERVOR}),
            faerben(formel("x_2=2-", "4", "=", "-2", groesse=G_RECHNUNG), {1: HERVOR}),
            faerben(formel("x_3=", "4", groesse=G_RECHNUNG), {1: HERVOR}),
        ).arrange(DOWN, buff=0.35)
        for zeile in beispiel[1:]:  # am Gleichheitszeichen nach x_i ausrichten
            zeile.shift((beispiel[0][0][2].get_x() - zeile[0][2].get_x()) * RIGHT)
        kopf4 = text("Jedes t liefert eine Lösung", groesse=40)
        block4 = self.tafel(kopf4, wahl, beispiel, abstand=0.5)
        with self.sprich("Jedes t liefert eine Lösung. Für t gleich 4 etwa: minus 1, minus 2 und 4."):
            self.play(auftritt(kopf4), welle(loesung[5], HERVOR), run_time=0.6)
            self.warte_bis(0.4)
            self.play(Write(wahl), run_time=0.5)
            self.play(LaggedStart(*[Write(zeile) for zeile in beispiel], lag_ratio=0.4), run_time=1.5)
        self.wait(0.6)
        self.play(FadeOut(block4, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        liste = kurzfassung(
            text("Obere Dreiecksform herstellen", groesse=38),
            text("Letzte Variable als Parameter t", groesse=38),
            text("Rückwärts einsetzen mit t", groesse=38),
        )
        self.tafel(liste)
        with self.sprich(
            "Kurz gesagt: auf obere Dreiecksform bringen, die letzte Variable gleich t setzen, rückwärts einsetzen."
        ):
            for zeile, beginn in zip(liste, (0.15, 0.45, 0.75)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
