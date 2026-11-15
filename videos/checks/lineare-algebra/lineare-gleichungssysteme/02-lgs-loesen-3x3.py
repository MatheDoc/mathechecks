"""Check 02 – LGS 3x3.

Kernidee: Der Gauß-Algorithmus erzeugt Zeile für Zeile Nullen unter der Diagonale. Aus der oberen
Dreiecksform ergeben sich die Unbekannten von unten nach oben.
Beispiel: unverändert aus dem Musterbeispiel des Checks.
"""
from manim import (
    BOLD,
    DOWN,
    RIGHT,
    UP,
    Create,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MathTex,
    ReplacementTransform,
    TransformFromCopy,
    VGroup,
    Write,
    rate_functions,
)

from mcvideo import ErweiterteMatrix, MCSzene, auftritt, einpassen, formel, kurzfassung, legende, schritt, text
from mcvideo.theme import ACHSE, BLAU, GRUEN, HERVOR, ROSE, TAFEL_BREITE, TEXT_LEISE

LGS = [
    [1, 1, 1, 3],
    [4, 2, 1, 14],
    [16, -4, 1, 8],
]
ZEILENABSTAND = 0.8  # in der Nebenrechnung
zeilenname = ErweiterteMatrix.zeilenname


def gleichung(koeffizienten: list[int], rechts: int) -> tuple[MathTex, list[VGroup | None]]:
    """Eine Gleichung des LGS und zu jedem Koeffizienten die Teile, die ihn zeigen (None, wenn er nicht dasteht)."""
    teile: list[str] = []
    stellen: list[list[int] | None] = []
    for j, a in enumerate(koeffizienten, start=1):
        vorzeichen = []
        if a < 0:
            teile.append("-")
            vorzeichen = [len(teile) - 1]
        elif j > 1:
            teile.append("+")
        if abs(a) == 1:
            stellen.append(None)
        else:
            teile.append(str(abs(a)))
            stellen.append([*vorzeichen, len(teile) - 1])
        teile.append(f"x_{j}")
    zeile = formel(*teile, "=", str(rechts), groesse=52)
    return zeile, [VGroup(*[zeile[k] for k in stelle]) if stelle else None for stelle in stellen]


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.8)
        self.matrix = m = self.auf_buehne(
            ErweiterteMatrix(LGS, breiteste_umformung=zeilenname(2) + r"-16\cdot" + zeilenname(0))
        )
        self.werte = [list(zeile) for zeile in LGS]

        paare = [gleichung(zeile[:-1], zeile[-1]) for zeile in LGS]
        gleichungen = VGroup(*[zeile for zeile, _ in paare]).arrange(DOWN, buff=0.5)
        for zeile in gleichungen:  # am Gleichheitszeichen ausrichten
            zeile.shift((gleichungen[0][-2].get_x() - zeile[-2].get_x()) * RIGHT)
        self.auf_buehne(gleichungen)
        self.add(karte)

        self.einstieg(
            "Wie löst du ein LGS", "mit drei Unbekannten?",
            bild=[LaggedStart(*[Write(zeile) for zeile in gleichungen], lag_ratio=0.35)],
            sprechtext="Wie löst du ein lineares Gleichungssystem mit drei Unbekannten?",
        )

        # ---------- Schritt 1: Matrixform ----------
        uebergang = [Create(m.klammern), Create(m.strich), *[FadeIn(name) for name in m.namen]]
        for i, (zeile, quellen) in enumerate(paare):
            benutzt = {id(zeile[-1])}
            for j, quelle in enumerate(quellen):
                if quelle is None:
                    uebergang.append(FadeIn(m.eintraege[i][j], scale=0.5))
                else:
                    uebergang.append(ReplacementTransform(quelle, m.eintraege[i][j]))
                    benutzt |= {id(teil) for teil in quelle}
            uebergang.append(ReplacementTransform(zeile[-1], m.eintraege[i][-1]))
            uebergang.append(FadeOut(VGroup(*[teil for teil in zeile if id(teil) not in benutzt])))

        kopf1 = schritt(1, "Matrixform")
        block1 = self.tafel(kopf1, text("nur die Zahlen aufschreiben", groesse=38, farbe=TEXT_LEISE), abstand=0.5)
        with self.sprich(
            "Schritt eins: die Matrixform. Wir schreiben nur noch die Zahlen auf.",
            untertitel="Schritt 1: die Matrixform. Wir schreiben nur noch die Zahlen auf.",
        ):
            self.play(auftritt(kopf1), run_time=0.5)
            self.warte_bis(0.45)
            self.play(*uebergang, auftritt(block1[1]), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(block1, shift=0.25 * UP), run_time=0.4)

        # ---------- Schritt 2: Gauß-Algorithmus ----------
        kopf2 = schritt(2, "Gauß-Algorithmus")
        probe = self.nebenrechnung(0, LGS[1], LGS[1], LGS[1], zeilenname(1), zeilenname(0), {})  # legt nur die Höhe fest
        self.tafel(kopf2, probe, abstand=0.6)
        kopf2.set_x(0)
        self.y_rechnung = probe[0][0][0].get_y()
        ziel = VGroup(
            text("Ziel: obere Dreiecksform", groesse=42, gewicht=BOLD),
            text("Nullen unter der Diagonale", groesse=38, farbe=HERVOR),
        ).arrange(DOWN, buff=0.35)
        einpassen(ziel, TAFEL_BREITE).move_to([0, self.y_rechnung - ZEILENABSTAND, 0])
        unter_diagonale = [m.eintraege[1][0], m.eintraege[2][0], m.eintraege[2][1]]

        with self.sprich(
            "Schritt zwei: der Gauß-Algorithmus. Unter der Diagonale sollen Nullen stehen. "
            "Das ist die obere Dreiecksform.",
            untertitel="Schritt 2: der Gauß-Algorithmus. Unter der Diagonale sollen Nullen stehen. "
                       "Das ist die obere Dreiecksform.",
        ):
            self.play(auftritt(kopf2), run_time=0.5)
            self.warte_bis(0.35)
            self.play(*[eintrag.animate.set_color(HERVOR) for eintrag in unter_diagonale], auftritt(ziel[1]), run_time=0.7)
            self.warte_bis(0.75)
            self.play(auftritt(ziel[0]), run_time=0.5)
        self.play(FadeOut(ziel, shift=0.25 * UP), run_time=0.4)

        self.umformung(
            1, 4, 0,
            sprechtext="Zeile zwei minus viermal Zeile eins: Aus der Vier wird eine Null.",
            untertitel="Zeile II minus 4-mal Zeile I: Aus der 4 wird eine 0.",
        )
        self.umformung(
            2, 16, 0,
            sprechtext="Genauso: Zeile drei minus sechzehnmal Zeile eins.",
            untertitel="Genauso: Zeile III minus 16-mal Zeile I.",
        )
        self.umformung(
            2, 10, 1,
            sprechtext="Jetzt die zweite Spalte: Zeile drei minus zehnmal Zeile zwei.",
            untertitel="Jetzt die zweite Spalte: Zeile III minus 10-mal Zeile II.",
        )
        erreicht = text("Obere Dreiecksform", groesse=42, gewicht=BOLD).move_to(ziel)
        with self.sprich("Fertig ist die obere Dreiecksform."):
            self.play(
                auftritt(erreicht),
                *[eintrag.animate(rate_func=rate_functions.there_and_back).scale(1.5) for eintrag in unter_diagonale],
                run_time=0.8,
            )
        self.play(FadeOut(VGroup(kopf2, erreicht), shift=0.25 * UP), run_time=0.4)

        # ---------- Schritt 3: Rückwärtseinsetzen ----------
        kopf3 = schritt(3, "Rückwärtseinsetzen")
        g3 = formel("15", "x_3=", "-60", r"\ \Rightarrow\ x_3=", "-4", groesse=44)
        g2 = formel(r"-2x_2-3\cdot(", "-4", ")=2", r"\ \Rightarrow\ x_2=", "5", groesse=44)
        g1 = formel("x_1+", "5", "-4", "=3", r"\ \Rightarrow\ x_1=", "2", groesse=44)
        for teil in (g3[4], g2[1], g1[2]):
            teil.set_color(BLAU)
        for teil in (g2[4], g1[1]):
            teil.set_color(ROSE)
        g1[5].set_color(GRUEN)
        zeilen = legende(
            (formel(zeilenname(2), groesse=36, farbe=TEXT_LEISE), g3),
            (formel(zeilenname(1), groesse=36, farbe=TEXT_LEISE), g2),
            (formel(zeilenname(0), groesse=36, farbe=TEXT_LEISE), g1),
            abstand=0.6,
        )
        self.tafel(kopf3, zeilen, abstand=0.7)

        with self.sprich(
            "Schritt drei: rückwärts einsetzen. Die letzte Zeile heißt: fünfzehn x drei gleich minus sechzig. "
            "Also x drei gleich minus vier.",
            untertitel="Schritt 3: rückwärts einsetzen. Die letzte Zeile heißt: 15x₃ = −60. Also x₃ = −4.",
        ):
            self.play(
                auftritt(kopf3), *[eintrag.animate.set_color(TEXT_LEISE) for eintrag in unter_diagonale], run_time=0.5,
            )
            self.warte_bis(0.25)
            self.play(m.betonen(2), FadeIn(zeilen[0][0]), run_time=0.5)
            self.play(
                TransformFromCopy(m.eintraege[2][2], g3[0]), FadeIn(g3[1]),
                TransformFromCopy(m.eintraege[2][3], g3[2]), run_time=0.9,
            )
            self.warte_bis(0.75)
            self.play(FadeIn(g3[3]), FadeIn(g3[4], scale=1.4), run_time=0.5)
        with self.sprich(
            "Das setzen wir in Zeile zwei ein: x zwei gleich fünf.",
            untertitel="Das setzen wir in Zeile II ein: x₂ = 5.",
        ):
            self.play(m.betonen(1), FadeIn(zeilen[1][0]), run_time=0.5)
            self.play(Write(g2[0]), TransformFromCopy(g3[4], g2[1]), Write(g2[2]), run_time=0.9)
            self.warte_bis(0.65)
            self.play(FadeIn(g2[3]), FadeIn(g2[4], scale=1.4), run_time=0.5)
        with self.sprich(
            "Und beides in Zeile eins: x eins gleich zwei.",
            untertitel="Und beides in Zeile I: x₁ = 2.",
        ):
            self.play(m.betonen(0), FadeIn(zeilen[2][0]), run_time=0.5)
            self.play(
                Write(g1[0]), TransformFromCopy(g2[4], g1[1]), TransformFromCopy(g3[4], g1[2]), Write(g1[3]),
                run_time=0.9,
            )
            self.warte_bis(0.65)
            self.play(FadeIn(g1[4]), FadeIn(g1[5], scale=1.4), run_time=0.5)
        self.wait(0.8)

        # ---------- Lösung in die Kopfzeile, Kurzfassung ----------
        loesung = self.kopf("x_1=", "2", r"\quad x_2=", "5", r"\quad x_3=", "-4")
        loesung[1].set_color(GRUEN)
        loesung[3].set_color(ROSE)
        loesung[5].set_color(BLAU)
        rest = VGroup(kopf3, *[zeile[0] for zeile in zeilen], *g3[:4], *g2[:4], *g1[:5])
        self.play(
            FadeOut(rest, shift=0.25 * UP),
            ReplacementTransform(g1[5], loesung[1]),
            ReplacementTransform(g2[4], loesung[3]),
            ReplacementTransform(g3[4], loesung[5]),
            FadeIn(VGroup(loesung[0], loesung[2], loesung[4])),
            run_time=0.9,
        )

        liste = kurzfassung(
            text("Matrixform aufschreiben", groesse=38),
            text("Obere Dreiecksform herstellen", groesse=38),
            text("Rückwärts einsetzen", groesse=38),
        )
        self.tafel(liste)
        with self.sprich("Kurz gesagt: Matrixform aufschreiben, auf obere Dreiecksform bringen, rückwärts einsetzen."):
            for zeile, beginn in zip(liste, (0.15, 0.4, 0.75)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def nebenrechnung(
        self,
        y: float,
        oben: list[int],
        abzug: list[int],
        ergebnis: list[int],
        name_oben: str,
        name_abzug: str,
        farben: dict[int, str],
    ) -> VGroup:
        """Schriftliche Subtraktion zweier Zeilen in den Spalten der Matrix; y ist die Höhe der oberen Zeile.

        Ergibt vier Teile: obere Zeile, abgezogene Zeile, Rechenstrich, Ergebnis.
        """
        m = self.matrix
        links, rechts = m.klammern.get_left()[0], m.klammern.get_right()[0]
        y_abzug = y - ZEILENABSTAND
        minus = m.randnotiz("-", y_abzug, m.zeile(0)[0].get_color()).set_x(links)
        return VGroup(
            VGroup(m.zahlenzeile(oben, y, farben), m.randnotiz(name_oben, y)),
            VGroup(minus, m.zahlenzeile(abzug, y_abzug), m.randnotiz(name_abzug, y_abzug)),
            Line([links - 0.15, y_abzug - 0.5, 0], [rechts + 0.15, y_abzug - 0.5, 0], color=ACHSE, stroke_width=2.5),
            m.zahlenzeile(ergebnis, y - 2 * ZEILENABSTAND - 0.2, farben),
        )

    def umformung(self, zeile: int, faktor: int, basis: int, sprechtext: str, untertitel: str) -> None:
        """Zeilenumformung „zeile − faktor · basis“: Nebenrechnung zeigen, dann die Zeile der Matrix ersetzen."""
        m = self.matrix
        alt = self.werte[zeile]
        abzug = [faktor * wert for wert in self.werte[basis]]
        neu = [a - b for a, b in zip(alt, abzug)]
        farben = {j: HERVOR for j in range(zeile)}  # die Spalten unter der Diagonale
        oben, mitte, strich, unten = rechnung = self.nebenrechnung(
            self.y_rechnung, alt, abzug, neu, zeilenname(zeile), rf"{faktor}\cdot" + zeilenname(basis), farben,
        )
        with self.sprich(sprechtext, untertitel=untertitel):
            self.play(m.umformung(zeile, zeilenname(zeile) + rf"-{faktor}\cdot" + zeilenname(basis)), run_time=0.5)
            self.play(TransformFromCopy(m.zeile(zeile), oben[0]), FadeIn(oben[1]), run_time=0.7)
            self.play(FadeIn(mitte, shift=0.15 * DOWN), run_time=0.5)
            self.warte_bis(0.7)
            self.play(Create(strich), FadeIn(unten, shift=0.15 * DOWN), run_time=0.6)
        self.wait(0.6)
        self.play(
            m.umformen(zeile, neu, farben), m.benennen(zeile), FadeOut(rechnung, shift=0.25 * UP), run_time=0.8,
        )
        self.werte[zeile] = neu
