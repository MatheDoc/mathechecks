"""Check 02 – E-Regel herleiten.

Kernidee: Der Ablehnungsbereich liegt dort, wohin die Gegenhypothese zeigt. Mit p_0 wird k probiert:
linksseitig das größte k mit P(X ≤ k) ≤ α, rechtsseitig das kleinste k mit P(X ≥ k) ≤ α.
Beispiel: Lootboxen wie in Check 01 (n = 50, p_0 = 0,2, α = 5 %) statt des Versandhändlers im Musterbeispiel;
das Ergebnis ist die Regel „höchstens 5“ aus Check 01. Linksseitig ausführlich, rechtsseitig nur kurz.
"""
from manim import BOLD, DOWN, UP, FadeOut, MathTex, Mobject, Transform, VGroup, Write

from mcvideo import Histogramm, MCSzene, auftritt, formel, kurzfassung, reihe, tabelle, text, welle
from mcvideo.theme import BLAU, HERVOR, ROSE, TEXT_LEISE

G_FORMEL = 44
G_TEXT = 34


def menge(name: str, *teile: str, farbe: str, k: int | None = None) -> MathTex:
    """Annahme- oder Ablehnungsbereich in seiner Farbe; der Teil mit k an Stelle k ist orange."""
    zeile = formel(name, "=", *teile, groesse=G_FORMEL, farbe=farbe)
    if k is not None:
        zeile[k].set_color(HERVOR)
    return zeile


def hypothesen(zeichen: str, annahme: MathTex, ablehnung: MathTex) -> VGroup:
    """Hypothesen, darunter Annahme- und Ablehnungsbereich mit ihren Namen."""
    return tabelle(
        (formel("H_0: p=0{,}2", groesse=G_FORMEL), formel(f"H_1: p{zeichen}0{{,}}2", groesse=G_FORMEL)),
        (
            VGroup(annahme, text("Annahmebereich", groesse=24, farbe=TEXT_LEISE)).arrange(DOWN, buff=0.15),
            VGroup(ablehnung, text("Ablehnungsbereich", groesse=24, farbe=TEXT_LEISE)).arrange(DOWN, buff=0.15),
        ),
    )


def ersetze(alt: MathTex, neu: MathTex) -> Transform:
    """Ersetzt eine Menge in der Tabelle an derselben Stelle und in derselben Größe."""
    neu.scale(alt[0].height / neu[0].height)
    return Transform(alt, neu.move_to(alt))


def satz(*teile: str | Mobject) -> VGroup:
    """Textzeile, in der kleine Formeln auf der Schriftgrundlinie stehen."""
    return reihe(
        *[text(teil, groesse=G_TEXT) if isinstance(teil, str) else teil for teil in teile],
        abstand=0.18, grundlinie=True,
    )


def k_formel(*teile: str) -> MathTex:
    """Formel, in der k orange ist (gesucht)."""
    zeile = formel(*teile, groesse=G_FORMEL)
    for teil in zeile:
        if teil.tex_string == "k":
            teil.set_color(HERVOR)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.0)
        hist = self.auf_buehne(Histogramm(50, 0.2, bis=20, y_max=0.19, hoehe=2.9, p_tex="p_0=0{,}2"))
        self.add(karte)

        self.einstieg(
            "Wie leitest du die", "Entscheidungsregel her?",
            zusatz="(einseitiger Hypothesentest)",
            sprechtext="Wie leitest du die Entscheidungsregel her?",
            bild=hist.aufbau(),
        )

        # ---------- Sachzusammenhang ----------
        lage = self.tafel(
            text("Lootboxen", groesse=46, gewicht=BOLD),
            text("Hersteller: 20 % mit seltenem Item", groesse=G_TEXT),
            text("Vermutung: Anteil gesenkt", groesse=G_TEXT),
            text("Test mit 50 Boxen", groesse=G_TEXT),
            satz("Signifikanzniveau", formel(r"\alpha=5\,\%", groesse=G_FORMEL)),
            abstand=0.45,
        )
        with self.sprich(
            "Ein Hersteller eines Computerspiels verspricht: In zwanzig Prozent der Lootboxen steckt ein seltenes Item. "
            "Die Community vermutet weniger und testet fünfzig Boxen. Das Signifikanzniveau ist fünf Prozent."
        ):
            self.play(auftritt(lage[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(auftritt(lage[1]), run_time=0.5)
            self.warte_bis(0.55)
            self.play(auftritt(lage[2]), auftritt(lage[3]), run_time=0.5)
            self.warte_bis(0.78)
            self.play(auftritt(lage[4]), run_time=0.5)
        self.play(FadeOut(lage, shift=0.25 * UP), run_time=0.4)

        # ---------- Ansatz ----------
        tab = self.oben_auf_tafel(hypothesen(
            "<",
            menge("A", r"\{", "k", r"+1,\ldots,50\}", farbe=BLAU, k=2),
            menge(r"\overline{A}", r"\{0,\ldots,", "k", r"\}", farbe=ROSE, k=3),
        ))
        bedingung = k_formel(r"P(X\leq ", "k", r")\leq 0{,}05")
        ansatz = self.tafel(
            satz("gesucht: größtes", formel("k", groesse=G_FORMEL, farbe=HERVOR), "mit"),
            bedingung,
            abstand=0.3, unter=tab,
        )
        with self.sprich(
            "Die Gegenhypothese besagt, dass p kleiner ist als vom Hersteller behauptet. "
            "Also liegt der Ablehnungsbereich links: null bis k. "
            "Seine Wahrscheinlichkeit ist der Fehler erster Art und darf höchstens fünf Prozent sein. "
            "Er soll aber möglichst groß sein. Gesucht ist also das größte k."
        ):
            self.play(auftritt(tab[0]), run_time=0.6)
            self.play(welle(tab[0][1], HERVOR), run_time=0.6)
            self.warte_bis(0.26)
            self.play(auftritt(tab[1]), welle(hist.ort(0), ROSE), run_time=0.7)
            self.warte_bis(0.55)
            self.play(Write(bedingung), run_time=0.9)
            self.warte_bis(0.87)
            self.play(auftritt(ansatz[0]), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(ansatz, shift=0.25 * UP), run_time=0.4)

        # ---------- Probieren ----------
        versuch5 = formel(r"P(X\leq 5)=Bcd(0;5;50;0{,}2)", groesse=G_FORMEL)
        wert5 = formel(r"\approx 0{,}0480\leq 0{,}05", groesse=G_FORMEL)
        versuch6 = formel(r"P(X\leq 6)=Bcd(0;6;50;0{,}2)", groesse=G_FORMEL)
        wert6 = formel(r"\approx 0{,}1034>0{,}05", groesse=G_FORMEL)
        probieren = self.tafel(
            satz("Probieren mit", formel("p_0=0{,}2", groesse=G_FORMEL)),
            VGroup(versuch5, wert5).arrange(DOWN, buff=0.2),
            VGroup(versuch6, wert6).arrange(DOWN, buff=0.2),
            abstand=0.5, unter=tab,
        )
        with self.sprich(
            "Wir probieren mit p null. Null bis fünf: null Komma null vier acht, das passt. "
            "Null bis sechs: schon über zehn Prozent, zu viel."
        ):
            self.play(auftritt(probieren[0]), run_time=0.5)
            self.warte_bis(0.2)
            self.play(hist.faerbe((0, 5, ROSE)), Write(versuch5), run_time=0.9)
            self.warte_bis(0.45)
            self.play(auftritt(wert5), run_time=0.5)
            self.warte_bis(0.62)
            self.play(hist.faerbe((0, 5, ROSE), (6, 6, HERVOR)), Write(versuch6), run_time=0.9)
            self.warte_bis(0.85)
            self.play(auftritt(wert6), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(probieren, shift=0.25 * UP), run_time=0.4)

        # ---------- Ergebnis ----------
        ergebnis = self.tafel(
            formel("k=5", groesse=60, farbe=HERVOR),
            text("„Höchstens 5 seltene Items:", groesse=G_TEXT, gewicht=BOLD, farben={"Höchstens 5": ROSE}),
            satz(formel("H_0", groesse=G_FORMEL), "verwerfen.“"),
            abstand=0.3, unter=tab,
        )
        ergebnis[1:].shift(0.3 * DOWN)
        with self.sprich(
            "Also ist k gleich fünf. Bei höchstens fünf seltenen Items wird die Nullhypothese verworfen."
        ):
            self.play(auftritt(ergebnis[0]), run_time=0.5)
            self.play(
                hist.faerbe((0, 5, ROSE), (6, 50, BLAU)),
                ersetze(tab[1][0][0], menge("A", r"\{6,\ldots,50\}", farbe=BLAU)),
                ersetze(tab[1][1][0], menge(r"\overline{A}", r"\{0,\ldots,5\}", farbe=ROSE)),
                run_time=0.9,
            )
            self.warte_bis(0.45)
            self.play(auftritt(ergebnis[1:]), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(ergebnis, shift=0.25 * UP), FadeOut(tab, shift=0.25 * UP), run_time=0.4)

        # ---------- Rechtsseitig ----------
        tab_rechts = self.oben_auf_tafel(hypothesen(
            ">",
            menge("A", r"\{0,\ldots,", "k", r"-1\}", farbe=BLAU, k=3),
            menge(r"\overline{A}", r"\{", "k", r",\ldots,50\}", farbe=ROSE, k=2),
        ))
        bedingung_rechts = k_formel(r"P(X\geq ", "k", r")\leq 0{,}05")
        rechts = self.tafel(
            satz("gesucht: kleinstes", formel("k", groesse=G_FORMEL, farbe=HERVOR), "mit"),
            bedingung_rechts,
            formel(r"P(X\geq 15)\approx 0{,}0607>0{,}05", groesse=G_FORMEL),
            formel(r"P(X\geq 16)\approx 0{,}0308\leq 0{,}05", groesse=G_FORMEL),
            abstand=0.3, unter=tab_rechts,
        )
        rechts[2:].shift(0.3 * DOWN)
        with self.sprich(
            "Vermutet man einen höheren Anteil, liegt der Ablehnungsbereich rechts. "
            "Dann suchst du das kleinste k: Ab fünfzehn ist es noch zu viel, ab sechzehn passt es."
        ):
            self.play(hist.faerbe(), auftritt(tab_rechts), run_time=0.7)
            self.warte_bis(0.3)
            self.play(auftritt(rechts[:2]), run_time=0.6)
            self.warte_bis(0.6)
            self.play(hist.faerbe((15, 50, HERVOR)), auftritt(rechts[2]), run_time=0.7)
            self.warte_bis(0.82)
            self.play(
                hist.faerbe((0, 15, BLAU), (16, 50, ROSE)), auftritt(rechts[3]),
                ersetze(tab_rechts[1][0][0], menge("A", r"\{0,\ldots,15\}", farbe=BLAU)),
                ersetze(tab_rechts[1][1][0], menge(r"\overline{A}", r"\{16,\ldots,50\}", farbe=ROSE)),
                run_time=0.9,
            )
        self.wait(0.8)
        self.play(FadeOut(rechts, shift=0.25 * UP), FadeOut(tab_rechts, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Hypothesen aufstellen", groesse=G_TEXT),
            text("Ablehnungsbereich links oder rechts?", groesse=G_TEXT),
            satz(
                formel("k", groesse=G_FORMEL, farbe=HERVOR), "mit", formel("p_0", groesse=G_FORMEL), "probieren:",
                formel(r"P\leq\alpha", groesse=G_FORMEL),
            ),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Hypothesen aufstellen. Liegt der Ablehnungsbereich links oder rechts? "
            "Dann k mit p null probieren, bis die Wahrscheinlichkeit höchstens alpha ist."
        ):
            self.play(hist.faerbe((0, 5, ROSE), (6, 50, BLAU)), auftritt(schritte[0]), run_time=0.5)
            self.warte_bis(0.25)
            self.play(auftritt(schritte[1]), run_time=0.5)
            self.warte_bis(0.6)
            self.play(auftritt(schritte[2]), run_time=0.5)
        self.wait(1.0)
