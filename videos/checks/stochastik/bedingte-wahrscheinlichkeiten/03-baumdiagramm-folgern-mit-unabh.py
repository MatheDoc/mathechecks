"""Check 03 – Baumdiagramm interpretieren (mit bed Wkt).

Kernidee: Im Baum stehen P(A), die bedingten Wahrscheinlichkeiten mit Bedingung A und die
Pfadenden. Mit Bedingung B steht nichts im Baum: P_B(A) muss berechnet werden.
Beispiel: Ereignisse und Zahlen aus dem Musterbeispiel des Checks. Die Fragen folgen den
Teilaufgaben der Trainingsaufgabe (Einzelwahrscheinlichkeit, Schnitt, Vereinigung, beide Arten
bedingter Wahrscheinlichkeit, Unabhängigkeit); die Sonderfälle wie P(A ∪ nicht A) fehlen.
"""
from manim import BOLD, DOWN, LEFT, UP, FadeIn, FadeOut, Text, VGroup, Write

from mcvideo import Baumdiagramm, MCSzene, auftritt, aufzaehlung, einpassen, formel, legende, reihe, text
from mcvideo.theme import BLAU, BREITE, GRUEN, HERVOR, KOPF_Y, ROSE, TEXT_LEISE

G_FORMEL = 46


def titel(inhalt: str) -> Text:
    """Überschrift eines Abschnitts. Ohne Nummer: Die Abschnitte sind kein Ablauf."""
    return text(inhalt, groesse=40, gewicht=BOLD)


def gleichung(*teile: str, farben: dict[int, str]) -> VGroup:
    """Formelzeile; farben färbt einzelne Teile (Index → Farbe)."""
    zeile = formel(*teile, groesse=G_FORMEL)
    for index, farbe in farben.items():
        zeile[index].set_color(farbe)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.7)  # knapp um den Baum, damit die zweizeilige Rechnung darunter Platz hat
        baum = self.auf_buehne(Baumdiagramm(pa=0.5, pba=0.4, pbna=0.1))
        self.add(karte)

        self.einstieg(
            "Was liest du im", "Baumdiagramm ab?",
            zusatz="(mit bedingten Wahrscheinlichkeiten)",
            bild=baum.aufbau(),
        )

        # ---------- Sachzusammenhang ----------
        ereignisse = legende(
            (formel("A", groesse=54), text("putzt regelmäßig die Zähne", groesse=36)),
            (formel("B", groesse=54), text("hat gesunde Zähne", groesse=36)),
            abstand=0.5,
        )
        self.tafel(ereignisse)
        kopf = reihe(
            reihe(formel("A", groesse=36), text("putzt Zähne", groesse=26), abstand=0.18),
            reihe(formel("B", groesse=36), text("gesunde Zähne", groesse=26), abstand=0.18),
            abstand=0.7,
        )
        einpassen(kopf, BREITE - 3).move_to([0.4, KOPF_Y, 0])
        with self.sprich("A bedeutet: Jemand putzt regelmäßig die Zähne. B: Die Zähne sind gesund."):
            self.play(auftritt(ereignisse[0]), baum.betone("A"), run_time=0.6)
            self.warte_bis(0.6)
            self.play(auftritt(ereignisse[1]), baum.betone("AB", "nAB"), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(ereignisse, target_position=kopf, scale=0.5), FadeIn(kopf), run_time=0.6)

        # ---------- Was im Baum steht ----------
        kopf1 = titel("Das steht im Baum")
        stufe1 = formel("P(A)=", "0{,}5", r",\quad P(\overline{A})=", "0{,}5", groesse=42)
        stufe2 = VGroup(
            formel("P_A(B)=", "0{,}4", r",\quad P_A(\overline{B})=", "0{,}6", groesse=42),
            formel(r"P_{\overline{A}}(B)=", "0{,}1", r",\quad P_{\overline{A}}(\overline{B})=", "0{,}9", groesse=42),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        pfadende = VGroup(
            formel(r"P(A\cap B)=", "0{,}2", r",\quad P(A\cap\overline{B})=", "0{,}3", groesse=42),
            formel(
                r"P(\overline{A}\cap B)=", "0{,}05", r",\quad P(\overline{A}\cap\overline{B})=", "0{,}45", groesse=42,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        for zeile in (stufe1, *stufe2, *pfadende):
            for wert in zeile[1::2]:
                wert.set_color(HERVOR)
        stellen = legende(
            (text("1. Stufe", farbe=TEXT_LEISE), stufe1),
            (text("2. Stufe", farbe=TEXT_LEISE), stufe2),
            (text("Pfadende", farbe=TEXT_LEISE), pfadende),
            abstand=0.5,
        )
        block1 = self.tafel(kopf1, stellen, abstand=0.7)
        alle = dict.fromkeys(baum.PFADE, HERVOR)
        with self.sprich(
            "Im Baum stehen 3 Dinge. Erste Stufe: P von A und P von nicht A. "
            "Zweite Stufe: P von B unter der Bedingung A, dazu die Varianten mit Gegenereignissen. "
            "Am Pfadende: P von A und B, dazu wieder die Varianten."
        ):
            self.play(auftritt(kopf1), run_time=0.5)
            self.warte_bis(0.13)
            self.play(baum.markiere(aeste={"A": HERVOR, "nA": HERVOR}), auftritt(stellen[0]), run_time=0.6)
            self.warte_bis(0.34)
            self.play(
                baum.markiere(aeste={"AB": HERVOR}), auftritt(VGroup(stellen[1][0], stufe2[0][:2])), run_time=0.6,
            )
            self.warte_bis(0.56)
            self.play(
                baum.markiere(aeste=alle), FadeIn(VGroup(stufe2[0][2:], stufe2[1]), shift=0.2 * UP), run_time=0.6,
            )
            self.warte_bis(0.74)
            self.play(
                baum.markiere(aeste={"A": HERVOR, "AB": HERVOR}, enden={"AB": HERVOR}),
                auftritt(VGroup(stellen[2][0], pfadende[0][:2])),
                run_time=0.6,
            )
            self.warte_bis(0.9)
            self.play(
                baum.markiere(enden=alle), FadeIn(VGroup(pfadende[0][2:], pfadende[1]), shift=0.2 * UP), run_time=0.6,
            )
        self.wait(0.6)
        self.play(FadeOut(block1, shift=0.25 * UP), run_time=0.4)

        # ---------- Pfadenden addieren ----------
        kopf2 = titel("Pfadenden addieren")
        summe_b = gleichung("P(B)=", "0{,}2", "+", "0{,}05", "=", "0{,}25", farben={1: BLAU, 3: BLAU, 5: BLAU})
        summe_oder = gleichung(
            r"P(A\cup B)=", "0{,}2", "+", "0{,}3", "+", "0{,}05", "=", "0{,}55",
            farben={1: ROSE, 3: ROSE, 5: ROSE, 7: ROSE},
        )
        summe_variante = gleichung(
            r"P(\overline{A}\cup B)=", "0{,}2", "+", "0{,}05", "+", "0{,}45", "=", "0{,}7",
            farben={1: GRUEN, 3: GRUEN, 5: GRUEN, 7: GRUEN},
        )
        block2 = self.tafel(kopf2, summe_b, summe_oder, summe_variante, abstand=0.6)
        with self.sprich(
            "P von B steht nicht im Baum. Du addierst die beiden Pfadenden mit B: 0,25."
        ):
            self.play(auftritt(kopf2), baum.markiere(), run_time=0.5)
            self.warte_bis(0.3)
            self.play(baum.markiere(enden={"AB": BLAU, "nAB": BLAU}), Write(summe_b[0]), run_time=0.7)
            self.warte_bis(0.65)
            self.play(Write(summe_b[1:]), run_time=0.9)
        with self.sprich("Zu A oder B gehören 3 Pfadenden."):
            self.play(
                baum.markiere(enden={"AB": ROSE, "AnB": ROSE, "nAB": ROSE}), Write(summe_oder[0]), run_time=0.7,
            )
            self.play(Write(summe_oder[1:]), run_time=1.1)
        with self.sprich("Zu nicht A oder B gehören diese 3."):
            self.play(
                baum.markiere(enden={"AB": GRUEN, "nAB": GRUEN, "nAnB": GRUEN}), Write(summe_variante[0]),
                run_time=0.7,
            )
            self.play(Write(summe_variante[1:]), run_time=1.1)
        self.wait(0.6)
        self.play(FadeOut(block2, shift=0.25 * UP), run_time=0.4)

        # ---------- Bedingung A ablesen, Bedingung B rechnen ----------
        ablesen = VGroup(
            text("Bedingung A: ablesen", groesse=38, gewicht=BOLD),
            text("putzt  →  gesunde Zähne?", farbe=TEXT_LEISE),
            gleichung("P_A(B)=", "0{,}4", farben={1: HERVOR}),
        ).arrange(DOWN, buff=0.25)
        bruch = formel("P_B(A)", "=", r"\frac{P(A\cap B)}{P(B)}", groesse=42)
        zahlen = formel(
            "=", r"\frac{0{,}2}{0{,}2+0{,}05}", "=", r"\frac{0{,}2}{0{,}25}", "=", "0{,}8", groesse=42,
        )
        # Zeichen eines Bruchs: erst der Zähler, dann der Bruchstrich, dann der Nenner.
        for teil, zaehler in ((bruch[2], 6), (zahlen[1], 3), (zahlen[3], 3)):
            teil[:zaehler].set_color(HERVOR)
            teil[zaehler + 1:].set_color(BLAU)
        rechnen = VGroup(
            text("Bedingung B: rechnen", groesse=38, gewicht=BOLD),
            text("gesunde Zähne  →  putzt?", farbe=TEXT_LEISE),
            bruch,
            zahlen,
        ).arrange(DOWN, buff=0.25)
        block3 = self.tafel(ablesen, rechnen, abstand=0.6)
        with self.sprich(
            "Die Wahrscheinlichkeit von B unter der Bedingung A (von allen, die putzen, haben 40 % gesunde Zähne) kannst du ablesen."
        ):
            self.play(baum.markiere(), auftritt(ablesen[0]), run_time=0.5)
            self.warte_bis(0.25)
            self.play(baum.betone("A"), auftritt(ablesen[1]), run_time=0.6)
            self.warte_bis(0.55)
            self.play(baum.markiere(aeste={"AB": HERVOR}), Write(ablesen[2]), run_time=0.8)
        with self.sprich(
            "Umgedreht: Die Wahrscheinlichkeit von A unter der Bedingung B (von allen mit gesunden Zähnen, wie viele putzen?, steht nicht im Baum. Du rechnest: P von A und B geteilt durch P von B. "
            "Und B ist die Summe der beiden Pfadenden."
        ):
            self.play(auftritt(rechnen[0]), baum.markiere(), run_time=0.5)
            self.warte_bis(0.15)
            self.play(
                baum.markiere(enden={"AB": BLAU, "nAB": BLAU}), baum.betone("AB", "nAB"), auftritt(rechnen[1]),
                run_time=0.7,
            )
            self.warte_bis(0.4)
            self.play(Write(bruch[0]), run_time=0.5)
            self.warte_bis(0.54)
            self.play(
                baum.markiere(enden={"AB": HERVOR, "nAB": BLAU}), FadeIn(bruch[1]), Write(bruch[2]), run_time=0.9,
            )
            self.warte_bis(0.72)
            self.play(FadeIn(zahlen[0]), Write(zahlen[1]), baum.betone("AB", "nAB"), run_time=0.9)
            self.warte_bis(0.9)
            self.play(FadeIn(zahlen[2:5]), run_time=0.5)
            self.play(FadeIn(zahlen[5], scale=1.4), run_time=0.4)
        self.wait(0.8)
        self.play(FadeOut(block3, shift=0.25 * UP), run_time=0.4)

        # ---------- Unabhängigkeit ----------
        kopf4 = titel("Unabhängig?")
        vergleich = reihe(
            gleichung("P_A(B)=", "0{,}4", farben={1: HERVOR}),
            formel(r"\neq", groesse=G_FORMEL),
            gleichung(r"P_{\overline{A}}(B)=", "0{,}1", farben={1: HERVOR}),
        )
        urteil = text("stochastisch abhängig", groesse=44, gewicht=BOLD)
        block4 = self.tafel(kopf4, vergleich, urteil, abstand=0.7)
        with self.sprich(
            "Sind A und B unabhängig? Vergleiche dazu die zweite Stufe: 0,4 und 0,1 sind verschieden, also hängt B davon ab, ob A eingetreten ist: Putzen bewirkt was."
        ):
            self.play(auftritt(kopf4), baum.markiere(), run_time=0.5)
            self.warte_bis(0.25)
            self.play(
                baum.markiere(aeste={"AB": HERVOR, "nAB": HERVOR}), FadeIn(vergleich[0]), FadeIn(vergleich[2]),
                run_time=0.7,
            )
            self.warte_bis(0.68)
            self.play(FadeIn(vergleich[1], scale=1.4), auftritt(urteil), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(block4, shift=0.25 * UP), baum.markiere(), run_time=0.5)

        # ---------- Kurzfassung ----------
        def stichwort(inhalt: str) -> Text:
            return text(inhalt, groesse=30, farbe=TEXT_LEISE)

        def terme(*teile: str, hervor: int | None = None) -> VGroup:
            zeile = formel(*teile, groesse=36)
            if hervor is not None:
                zeile[hervor].set_color(HERVOR)
            return zeile

        punkte = aufzaehlung(
            (stichwort("1. Stufe"), terme(r"P(A),\ P(\overline{A})")),
            (stichwort("2. Stufe"), terme(
                "P_A(B)", r",\ P_A(\overline{B}),\ P_{\overline{A}}(B),\ P_{\overline{A}}(\overline{B})", hervor=0,
            )),
            (stichwort("Pfadende"), terme(r"P(A\cap B),\ P(A\cap\overline{B}),\ \dots")),
            (stichwort("addieren"), terme(r"P(B),\ P(\overline{B}),\ P(A\cup B),\ \dots")),
            (stichwort("dividieren"), terme("P_B(A)", r",\ P_B(\overline{A}),\ \dots", hervor=0)),
        )
        ablesen, rechnen = text("ablesen", groesse=38, gewicht=BOLD), text("rechnen", groesse=38, gewicht=BOLD)
        uebersicht = VGroup(ablesen, *punkte[:3], rechnen, *punkte[3:]).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        VGroup(rechnen, *punkte[3:]).shift(0.3 * DOWN)
        self.tafel(uebersicht)
        alle_pfade = dict.fromkeys(baum.PFADE, HERVOR)
        with self.sprich(
            "Kurz gesagt: Die Stufen und die Pfadenden liest du ab. Die andere Wahrscheinlichkeiten berechnest du."
        ):
            self.play(auftritt(ablesen), run_time=0.4)
            self.warte_bis(0.15)
            self.play(baum.markiere(aeste={"A": HERVOR, "nA": HERVOR}), auftritt(punkte[0]), run_time=0.5)
            self.play(baum.markiere(aeste=alle_pfade), auftritt(punkte[1]), run_time=0.5)
            self.warte_bis(0.38)
            self.play(baum.markiere(enden=alle_pfade), auftritt(punkte[2]), run_time=0.5)
            self.warte_bis(0.55)
            self.play(baum.markiere(), auftritt(rechnen), run_time=0.4)
            self.warte_bis(0.75)
            self.play(auftritt(punkte[3]), run_time=0.4)
            self.warte_bis(0.88)
            self.play(auftritt(punkte[4]), run_time=0.4)
        self.wait(1.5)
