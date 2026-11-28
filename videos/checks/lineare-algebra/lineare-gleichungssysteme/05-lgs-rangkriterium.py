"""Check 05 – Rangkriterium.

Kernidee: Zeilen zählen, die nicht nur Nullen enthalten: links vom Strich (rg(A)) und mit der Spalte hinter
dem Strich (rg(A|y)); das Ergebnis mit n, der Anzahl der Spalten von A, vergleichen. Jeder Fall wird an der
letzten Zeile begründet (0 = 6, x_3 festgelegt, x_3 frei) und dann zum Teil des Rangkriteriums verallgemeinert.
Beispiel: Matrix aus dem Musterbeispiel (keine Lösung); danach wird nur die letzte Zeile geändert,
damit alle drei Fälle an einer Matrix vorkommen: (0 0 4 | 8) eine Lösung, (0 0 0 | 0) unendlich viele.
"""
from manim import BOLD, UP, Create, FadeIn, FadeOut, LaggedStart, MathTex, Mobject, Transform, VGroup, Write

from mcvideo import ErweiterteMatrix, MCSzene, auftritt, aufzaehlung, formel, reihe, text, welle
from mcvideo.theme import BLAU, ROSE, TEXT, TEXT_LEISE, TEXT_SCHWACH, TUERKIS

MATRIX = [
    [2, -1, 3, 4],
    [0, 5, -2, 1],
    [0, 0, 0, 6],
]
RG_A = r"\mathrm{rg}(A)"
RG_AY = r"\mathrm{rg}(A\mid y)"
G_FORMEL = 46


def werte(rg_a: int, rg_ay: int, n: int = 3) -> VGroup:
    """Die drei Kennzahlen nebeneinander; je Kennzahl die Teile (Name mit =, Wert)."""
    teile = [
        formel(RG_A + "=", str(rg_a), groesse=G_FORMEL, farbe=BLAU),
        formel(RG_AY + "=", str(rg_ay), groesse=G_FORMEL, farbe=ROSE),
        formel("n=", str(n), groesse=G_FORMEL, farbe=TUERKIS),
    ]
    return reihe(*teile, abstand=0.6)


def bedingung(*teile: str) -> MathTex:
    """Vergleich der Kennzahlen, jede in ihrer Farbe."""
    zeile = formel(*teile, groesse=G_FORMEL)
    for teil, tex in zip(zeile, teile):
        farbe = {RG_A: BLAU, RG_AY: ROSE, "n": TUERKIS}.get(tex)
        if farbe:
            teil.set_color(farbe)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.0)
        m = ErweiterteMatrix(MATRIX)
        m.remove(*m.namen)
        unbekannte = VGroup(*[
            formel(f"x_{j + 1}", groesse=36, farbe=TUERKIS).next_to(m.eintraege[0][j], UP, buff=0.45)
            for j in range(3)
        ])
        self.matrix = m
        self.auf_buehne(VGroup(m, unbekannte))
        self.unbekannte = unbekannte
        self.add(karte)
        eintraege = [eintrag for zeile in m.eintraege for eintrag in zeile]

        self.einstieg(
            "Wie viele Lösungen", "hat ein LGS?",
            bild=[Create(m.klammern), Create(m.strich), LaggedStart(*[Write(e) for e in eintraege], lag_ratio=0.05)],
            sprechtext="Wie viele Lösungen hat ein lineares Gleichungssystem?",
        )

        # ---------- Rang ----------
        self.kennzahlen = kennzahlen = self.oben_auf_tafel(werte(2, 3))
        regel = VGroup(
            text("Rang", groesse=46, gewicht=BOLD),
            text("Anzahl der Zeilen,", groesse=38),
            text("die nicht nur Nullen enthalten", groesse=38),
        ).arrange(direction=[0, -1, 0], buff=0.25)
        block = self.tafel(regel, unter=kennzahlen)
        with self.sprich(
            "Die Matrix steht schon in Zeilenstufenform. Der Rang ist die Anzahl der Zeilen, "
            "die nicht nur Nullen enthalten."
        ):
            self.warte_bis(0.4)
            self.play(auftritt(regel[0]), run_time=0.5)
            self.play(auftritt(regel[1:]), run_time=0.6)
        self.wait(0.4)

        # ---------- Kennzahlen ----------
        rechts = VGroup(*[zeile[3] for zeile in m.eintraege])
        with self.sprich("Für den Rang von A zählen wir nur links vom Strich: 2 Zeilen."):
            self.play(rechts.animate.set_color(TEXT_SCHWACH), run_time=0.5)
            self.warte_bis(0.5)
            self.play(
                *[VGroup(*m.eintraege[i][:3]).animate.set_color(BLAU) for i in (0, 1)],
                VGroup(*m.eintraege[2][:3]).animate.set_color(TEXT_SCHWACH),
                run_time=0.6,
            )
            self.play(FadeIn(kennzahlen[0], shift=0.2 * UP), run_time=0.5)
        with self.sprich(
            "Mit der Spalte hinter dem Strich zählt auch die dritte Zeile: Der Rang der erweiterten Matrix ist 3."
        ):
            self.play(*[m.zeile(i).animate.set_color(TEXT) for i in range(3)], run_time=0.5)
            self.warte_bis(0.35)
            self.play(m.zeile(2).animate.set_color(ROSE), welle(m.eintraege[2][3], ROSE), run_time=0.6)
            self.play(*[m.zeile(i).animate.set_color(ROSE) for i in (0, 1)], run_time=0.4)
            self.warte_bis(0.8)
            self.play(FadeIn(kennzahlen[1], shift=0.2 * UP), run_time=0.5)
        with self.sprich("n steht für die Anzahl der Unbekannten, also der Spalten von A: 3."):
            self.play(*[m.zeile(i).animate.set_color(TEXT) for i in range(3)], run_time=0.4)
            self.warte_bis(0.3)
            self.play(LaggedStart(*[FadeIn(x, shift=0.15 * UP) for x in unbekannte], lag_ratio=0.3), run_time=0.9)
            self.warte_bis(0.8)
            self.play(FadeIn(kennzahlen[2], shift=0.2 * UP), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Die drei Fälle: letzte Zeile lesen, begründen, verallgemeinern ----------
        self.fall(
            letzte=formel("0=6", groesse=G_FORMEL),
            grund=text("Widerspruch", groesse=34, farbe=TEXT_LEISE),
            urteil="keine Lösung",
            allgemein=bedingung(RG_A, "<", RG_AY),
            sprechtext="Die letzte Zeile heißt 0 gleich 6. Ein Widerspruch: keine Lösung.",
            sprechtext_allgemein=(
                "Allgemein gilt: Ist der Rang von A kleiner als der Rang der erweiterten Matrix, "
                "gibt es keine Lösung."
            ),
        )
        self.fall(
            letzte=formel(r"4x_3=8\ \Rightarrow\ x_3=2", groesse=G_FORMEL),
            grund=text("3 Gleichungen, 3 Unbekannte", groesse=34, farbe=TEXT_LEISE),
            urteil="eine Lösung",
            allgemein=bedingung(RG_A, "=", RG_AY, "=", "n"),
            sprechtext=(
                "Jetzt heißt die letzte Zeile 4 x drei gleich 8, also x drei gleich 2. "
                "3 Gleichungen in Zeilenstufenform für 3 Unbekannte: "
                "Rückwärts eingesetzt gibt es genau ein x zwei und ein x eins."
            ),
            sprechtext_allgemein="Allgemein gilt: Sind beide Ränge gleich n, gibt es genau eine Lösung.",
            neue_zeile=[0, 0, 4, 8],
            neue_werte=(3, 3),
        )
        self.fall(
            letzte=formel(r"0=0\ \Rightarrow\ x_3=t", groesse=G_FORMEL),
            grund=text("2 Gleichungen, 3 Unbekannte", groesse=34, farbe=TEXT_LEISE),
            urteil="unendlich viele Lösungen",
            allgemein=bedingung(RG_A, "=", RG_AY, "<", "n"),
            sprechtext=(
                "Ist die ganze Zeile 0, heißt sie 0 gleich 0. Das stimmt immer. "
                "Es bleiben 2 solche Gleichungen für 3 Unbekannte, x drei ist frei wählbar: "
                "unendlich viele Lösungen."
            ),
            sprechtext_allgemein=(
                "Allgemein gilt: Sind beide Ränge gleich, aber kleiner als n, gibt es unendlich viele."
            ),
            neue_zeile=[0, 0, 0, 0],
            neue_werte=(2, 2),
        )
        self.play(FadeOut(kennzahlen, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        def ergebnis(inhalt: str):
            return text(inhalt, groesse=34)

        punkte = aufzaehlung(
            (bedingung(RG_A, r"\neq", RG_AY), ergebnis("keine Lösung")),
            (bedingung(RG_A, "=", RG_AY, "=", "n"), ergebnis("eine Lösung")),
            (bedingung(RG_A, "=", RG_AY, "<", "n"), ergebnis("unendlich viele")),
            abstand=0.55,
        )
        kopf = text("Rangkriterium", groesse=44, gewicht=BOLD)
        self.tafel(kopf, punkte, abstand=0.6)
        with self.sprich(
            "Kurz gesagt, nach dem Rangkriterium gilt: Ränge verschieden, keine Lösung. "
            "Beide gleich n, eine Lösung. Gleich, aber kleiner als n, unendlich viele."
        ):
            self.play(auftritt(kopf), run_time=0.5)
            for zeile, beginn in zip(punkte, (0.3, 0.55, 0.78)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
        self.wait(1.5)

    def fall(
        self,
        *,
        letzte: MathTex,
        grund: Mobject,
        urteil: str,
        allgemein: MathTex,
        sprechtext: str,
        sprechtext_allgemein: str,
        neue_zeile: list[int] | None = None,
        neue_werte: tuple[int, int] | None = None,
    ) -> None:
        """Ein Fall des Rangkriteriums unter den Kennzahlen: ggf. letzte Zeile ändern, sie lesen, begründen,
        Ergebnis nennen, dann den Teil des Rangkriteriums dazu."""
        m = self.matrix
        zeile = reihe(text("letzte Zeile:", groesse=34, farbe=TEXT_LEISE), letzte, abstand=0.2, grundlinie=True)
        ergebnis = text(urteil, groesse=44, gewicht=BOLD)
        regel = reihe(text("allgemein:", groesse=34, farbe=TEXT_LEISE), allgemein, abstand=0.25, grundlinie=True)
        block = self.tafel(zeile, grund, ergebnis, regel, abstand=0.45, unter=self.kennzahlen)
        with self.sprich(sprechtext):
            if neue_zeile is not None:
                alt = [self.kennzahlen[k][1] for k in (0, 1)]
                neu = [
                    formel(str(wert), groesse=G_FORMEL, farbe=farbe).match_height(teil).move_to(teil)
                    for wert, teil, farbe in zip(neue_werte, alt, (BLAU, ROSE))
                ]
                self.play(
                    m.umformen(2, neue_zeile),
                    *[welle(eintrag, TEXT) for eintrag in m.eintraege[2]],
                    *[Transform(teil, ziel) for teil, ziel in zip(alt, neu)],
                    run_time=0.8,
                )
            self.play(m.betonen(2), auftritt(zeile), run_time=0.6)
            self.warte_bis(0.45)
            self.play(auftritt(grund), run_time=0.5)
            self.warte_bis(0.8)
            self.play(auftritt(ergebnis), run_time=0.5)
        with self.sprich(sprechtext_allgemein):
            self.warte_bis(0.2)
            self.play(auftritt(regel[0]), Write(allgemein), run_time=0.9)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)
