"""Check 02 – Baumdiagramm vervollständigen bei Unabhängigkeit.

Kernidee: Bei Unabhängigkeit sieht die zweite Stufe oben und unten gleich aus; die Werte werden übertragen.
Den Rest liefern die Regeln wie gewohnt: Summe 1 am Knoten, Pfadmultiplikation (auch rückwärts),
Pfadaddition.
Beispiel: Zahlen und gegebene Felder (⑦ = 0,12, ⑧ = 0,28) wie im Musterbeispiel, ohne Sachzusammenhang:
Die Bedeutung von A und B spielt für das Vervollständigen keine Rolle. Das Training gibt andere Paare von
Feldern vor; Runden kommt nicht vor.
"""
from manim import BOLD, DOWN, LEFT, UP, FadeIn, FadeOut, Indicate, Text, VGroup, Write

from mcvideo import Baumdiagramm, MCSzene, auftritt, aufzaehlung, einpassen, feldnummer, formel, reihe, text
from mcvideo.theme import BLAU, BREITE, HERVOR, KOPF_Y, TEXT_LEISE

G_FORMEL = 52
G_NUMMER = 40


def titel(inhalt: str) -> Text:
    """Überschrift eines Abschnitts. Ohne Nummer: Die Reihenfolge hängt von den gegebenen Feldern ab."""
    return text(inhalt, groesse=40, gewicht=BOLD)


def zeile(nr: int, *teile: str, farben: dict[int, str]) -> VGroup:
    """Rechnung für ein Feld: Feldnummer wie im Baum, dann die Formelteile; farben färbt Teile (Index → Farbe)."""
    rechnung = formel(*teile, groesse=G_FORMEL)
    for index, farbe in farben.items():
        rechnung[index].set_color(farbe)
    return reihe(feldnummer(nr, groesse=G_NUMMER, farbe=farben.get(-1, HERVOR)), rechnung, abstand=0.2)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.7)
        baum = self.auf_buehne(Baumdiagramm(pa=0.4, pba=0.3, pbna=0.3, luecken=(1, 2, 3, 4, 5, 6, 9, 10)))
        self.add(karte)

        self.einstieg(
            "Wie vervollständigst du", "das Baumdiagramm?",
            zusatz="(bei Unabhängigkeit)",
            bild=baum.aufbau(),
        )

        # ---------- Gegeben ----------
        def unabhaengig(groesse: float) -> VGroup:
            """„A und B sind stochastisch unabhängig.“ mit dem Signalwort in Orange."""
            return reihe(
                formel("A", groesse=groesse * 1.35), text("und", groesse=groesse), formel("B", groesse=groesse * 1.35),
                text("sind stochastisch unabhängig.", groesse=groesse, farben={"stochastisch unabhängig": HERVOR}),
                abstand=0.2, grundlinie=True,
            )

        gegeben = VGroup(
            reihe(formel("A", groesse=66), text("und", groesse=48), formel("B", groesse=66), text("sind", groesse=48),
                  abstand=0.25, grundlinie=True),
            text("stochastisch unabhängig.", groesse=48, farben={"stochastisch unabhängig": HERVOR}),
        ).arrange(DOWN, buff=0.25)
        sach = self.tafel(gegeben)
        kopf = einpassen(unabhaengig(26), BREITE - 3).move_to([0.4, KOPF_Y, 0])
        with self.sprich("Gegeben sind zwei Pfadenden, und: A und B sind stochastisch unabhängig. Das brauchen wir gleich."):
            self.play(baum.markiere(enden={"AB": HERVOR, "AnB": HERVOR}), run_time=0.6)
            self.warte_bis(0.3)
            self.play(auftritt(gegeben), baum.markiere(), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(sach, target_position=kopf, scale=0.5), FadeIn(kopf), run_time=0.6)

        # ---------- Pfadadditionsregel ----------
        feld1 = zeile(1, "=", "0{,}12", "+", "0{,}28", "=", "0{,}4", farben={1: BLAU, 3: BLAU, 5: HERVOR})
        block1 = self.tafel(titel("Pfadadditionsregel"), feld1, abstand=0.7)
        with self.sprich(
            "Die beiden Pfade über A ergeben zusammen P von A: "
            "null Komma eins zwei plus null Komma zwei acht gleich null Komma vier."
        ):
            self.play(auftritt(block1[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(baum.markiere(enden={"AB": BLAU, "AnB": BLAU}), run_time=0.6)
            self.warte_bis(0.35)
            self.play(baum.markiere(aeste={"A": HERVOR}, enden={"AB": BLAU, "AnB": BLAU}), run_time=0.5)
            self.warte_bis(0.55)
            self.play(Write(feld1), run_time=1.2)
            self.play(baum.fuelle(1, quelle=feld1[1][5]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(block1, shift=0.25 * UP), baum.markiere(), run_time=0.4)

        # ---------- Pfadmultiplikationsregel rückwärts ----------
        # Bekannte Felder stehen schon als Zahl da, nur das gesuchte als Feldnummer.
        ansatz = reihe(
            formel("0{,}4", groesse=G_FORMEL, farbe=BLAU), formel(r"\cdot", groesse=G_FORMEL),
            feldnummer(3, groesse=G_NUMMER, farbe=HERVOR), formel("=", groesse=G_FORMEL),
            formel("0{,}12", groesse=G_FORMEL, farbe=BLAU), abstand=0.2,
        )
        feld3 = zeile(3, "=", r"\frac{0{,}12}{0{,}4}", "=", "0{,}3", farben={1: BLAU, 3: HERVOR})
        block2 = self.tafel(titel("Pfadmultiplikationsregel"), ansatz, feld3, abstand=0.6)
        with self.sprich(
            "Null Komma vier mal Feld drei ergibt null Komma eins zwei. Also teilen wir: Feld drei ist null Komma drei."
        ):
            self.play(
                auftritt(block2[0]), baum.markiere(aeste={"A": BLAU, "AB": HERVOR}, enden={"AB": BLAU}), run_time=0.6,
            )
            self.play(auftritt(ansatz), run_time=0.6)
            self.warte_bis(0.5)
            self.play(Write(feld3), run_time=1.0)
            self.play(baum.fuelle(3, quelle=feld3[1][3]), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(block2, shift=0.25 * UP), baum.markiere(), run_time=0.4)

        # ---------- An jedem Knoten: Summe 1 ----------
        feld4 = zeile(4, "=", "1-", "0{,}3", "=", "0{,}7", farben={2: BLAU, 4: HERVOR})
        feld2 = zeile(2, "=", "1-", "0{,}4", "=", "0{,}6", farben={2: BLAU, 4: HERVOR})
        block3 = self.tafel(titel("An jedem Knoten: Summe 1"), feld4, feld2, abstand=0.6)
        with self.sprich("An jedem Knoten ergeben die Äste zusammen eins. Das liefert Feld vier und Feld zwei."):
            self.play(auftritt(block3[0]), run_time=0.5)
            self.warte_bis(0.2)
            self.play(baum.markiere(aeste={"AB": BLAU, "AnB": HERVOR}), Write(feld4), run_time=1.0)
            self.play(baum.fuelle(4, quelle=feld4[1][4]), run_time=0.7)
            self.warte_bis(0.6)
            self.play(baum.markiere(aeste={"A": BLAU, "nA": HERVOR}), Write(feld2), run_time=1.0)
            self.play(baum.fuelle(2, quelle=feld2[1][4]), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(block3, shift=0.25 * UP), baum.markiere(), run_time=0.4)

        # ---------- Unabhängigkeit ----------
        # Zwei Schritte, je ein Paar Äste in einer Farbe: erst B oben und unten, dann nicht B.
        ueber_b = zeile(5, "=", "P_A(B)", "=", "0{,}3", farben={1: HERVOR, 3: HERVOR})
        ueber_nb = zeile(6, "=", r"P_A(\overline{B})", "=", "0{,}7", farben={-1: BLAU, 1: BLAU, 3: BLAU})
        block4 = self.tafel(titel("Unabhängigkeit"), ueber_b, ueber_nb, abstand=0.6)
        with self.sprich(
            "Jetzt nutzen wir, dass A und B unabhängig sind. Dann ist die Wahrscheinlichkeit für B "
            "unten dieselbe wie oben: null Komma drei."
        ):
            self.play(auftritt(block4[0]), Indicate(kopf, color=kopf.get_color(), scale_factor=1.15), run_time=0.8)
            self.warte_bis(0.4)
            self.play(baum.markiere(aeste={"AB": HERVOR, "nAB": HERVOR}, knoten=False), Write(ueber_b), run_time=1.0)
            self.warte_bis(0.8)
            self.play(baum.fuelle(5, quelle=baum.werte["AB"]), run_time=0.9)
        with self.sprich("Genauso für nicht B: null Komma sieben."):
            self.play(
                baum.markiere(aeste={"AB": HERVOR, "nAB": HERVOR, "AnB": BLAU, "nAnB": BLAU}, knoten=False),
                Write(ueber_nb), run_time=1.0,
            )
            self.play(baum.fuelle(6, quelle=baum.werte["AnB"], farbe=BLAU), run_time=0.9)
        self.wait(0.6)
        self.play(FadeOut(block4, shift=0.25 * UP), baum.markiere(), run_time=0.4)

        # ---------- Rest wie gewohnt ----------
        feld9 = zeile(9, "=", "0{,}6", r"\cdot", "0{,}3", "=", "0{,}18", farben={1: BLAU, 3: BLAU, 5: HERVOR})
        feld10 = zeile(10, "=", "0{,}6", r"\cdot", "0{,}7", "=", "0{,}42", farben={1: BLAU, 3: BLAU, 5: HERVOR})
        block5 = self.tafel(titel("Pfadmultiplikationsregel"), feld9, feld10, abstand=0.6)
        with self.sprich("Der Rest wie gewohnt: entlang des Pfades multiplizieren."):
            self.play(
                auftritt(block5[0]), baum.markiere(aeste={"nA": BLAU, "nAB": BLAU}, enden={"nAB": HERVOR}),
                run_time=0.5,
            )
            self.play(Write(feld9), run_time=0.9)
            self.play(baum.fuelle(9, quelle=feld9[1][5]), run_time=0.7)
            self.play(baum.markiere(aeste={"nA": BLAU, "nAnB": BLAU}, enden={"nAnB": HERVOR}), Write(feld10), run_time=0.9)
            self.play(baum.fuelle(10, quelle=feld10[1][5]), run_time=0.7)
        self.wait(0.6)
        self.play(FadeOut(block5, shift=0.25 * UP), baum.markiere(), run_time=0.4)

        # ---------- Kurzfassung ----------
        def stichwort(inhalt: str) -> Text:
            return text(inhalt, groesse=34, farbe=TEXT_LEISE)

        def regeltext(inhalt: str) -> Text:
            return text(inhalt, groesse=34)

        punkte = aufzaehlung(
            (stichwort("unabhängig"), formel(r"P_{\overline{A}}(B)=P_A(B)", groesse=44)),
            (stichwort("Knoten"), regeltext("Summe 1")),
            (stichwort("Pfad"), regeltext("multiplizieren")),
            (stichwort("Pfadenden"), regeltext("addieren → 1. Stufe")),
        )
        VGroup(*punkte[1:]).shift(0.3 * DOWN)  # die übrigen Regeln wie gewohnt, etwas abgesetzt
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Bei Unabhängigkeit ist die zweite Stufe oben und unten gleich. "
            "Ansonsten wie gewohnt: Am Knoten ergänzt du zu eins, entlang des Pfades multiplizierst du, "
            "Pfadenden addierst du, um die erste Stufe zu bekommen."
        ):
            # oben und unten gleich: erst die beiden B-Äste, dann die beiden anderen kurz aufleuchten lassen
            self.play(auftritt(punkte[0]), run_time=0.5)
            self.warte_bis(0.12)
            self.play(baum.markiere(aeste={"AB": HERVOR, "nAB": HERVOR}, knoten=False), run_time=0.4)
            self.wait(0.3)
            self.play(baum.markiere(aeste={"AnB": HERVOR, "nAnB": HERVOR}, knoten=False), run_time=0.4)
            self.wait(0.3)
            self.play(baum.markiere(), run_time=0.4)
            self.warte_bis(0.45)
            self.play(auftritt(punkte[1]), run_time=0.4)
            self.warte_bis(0.62)
            self.play(auftritt(punkte[2]), run_time=0.4)
            self.warte_bis(0.8)
            self.play(auftritt(punkte[3]), run_time=0.4)
        self.wait(1.5)
