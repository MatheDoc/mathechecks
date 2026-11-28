"""Check 03 – Zinssatzwechsel.

Kernidee: Der Zwischenwert K_{n_1} verbindet beide Zinsphasen. Er wird aus der vollständig bekannten Phase
berechnet: vorwärts, wenn die Unbekannte in Phase 2 liegt, rückwärts, wenn sie in Phase 1 liegt.
Danach bleibt in der anderen Phase eine gewöhnliche Zinseszinsaufgabe.
Beispiel: Tischlerei wie im Musterbeispiel samt Variante (p_1 gesucht), ohne Abweichung.
"""
from manim import BOLD, DOWN, LEFT, UP, FadeOut, MathTex, Mobject, VGroup, Write

from mcvideo import MCSzene, Phasenstrahl, auftritt, betrag, formel, kurzfassung, reihe, text, welle, wortlaut
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist die Größe, die gerade berechnet wird: erst der Zwischenwert, dann der gesuchte Zinssatz.
G_FORMEL = 50
G_TEXT = 36
G_STRAHL = 40
G_PHASE = 28


def hervor(zeile: MathTex, *teile: int) -> MathTex:
    for teil in teile:
        zeile[teil].set_color(HERVOR)
    return zeile


def angabe(tex: str, farbe: str = TEXT) -> MathTex:
    return formel(tex, groesse=G_STRAHL, farbe=farbe)


def phase(nr: int, dauer: str, zins: str, farbe: str = TEXT) -> VGroup:
    """Angabe über einer Phase: Titel, darunter Dauer und Zinssatz."""
    zeilen = VGroup(
        text(f"Phase {nr}", groesse=G_PHASE, farbe=TEXT_LEISE),
        angabe(dauer),
        angabe(zins, farbe),
    )
    return zeilen.arrange(DOWN, buff=0.14)


def kapital(name: str, wert: str | None = None, farbe: str = TEXT, kante: object = None) -> VGroup:
    """Angabe unter dem Strahl: Name, darunter Wert in Euro oder ein Fragezeichen."""
    zeilen = [angabe(name, farbe)]
    if wert == "?":
        zeilen.append(angabe("?", farbe))
    elif wert is not None:
        zeilen.append(betrag(wert, groesse=G_STRAHL, farbe=farbe))
    gruppe = VGroup(*zeilen)
    return gruppe.arrange(DOWN, buff=0.16, aligned_edge=kante) if kante is not None else gruppe.arrange(DOWN, buff=0.16)


def ergebnis(name: str, rechnung: str, wert: str, euro: bool = False) -> Mobject:
    """Zeile „Name = Rechnung ≈ Wert“; Name und Wert in der Farbe der gesuchten Größe."""
    teile = (name, "=", rechnung, r"\approx", wert)
    zeile = (betrag if euro else formel)(*teile, groesse=G_FORMEL)
    tex = zeile[0] if euro else zeile
    hervor(tex, 0, 4)
    if euro:
        zeile[1].set_color(HERVOR)
    return zeile


def richtung(lage: str, wort: str) -> VGroup:
    """Überschrift „Unbekannte in Phase …: vorwärts/rückwärts“."""
    return reihe(
        text(f"Unbekannte in {lage}:", groesse=G_TEXT, farbe=TEXT_LEISE),
        text(wort, groesse=40, gewicht=BOLD),
        abstand=0.25, grundlinie=True,
    )


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.4)
        self.strahl = Phasenstrahl(
            phase1=phase(1, "n_1", "p_1"),
            phase2=phase(2, "n_2", "p_2"),
            anfang=kapital("K_0", kante=LEFT),
            mitte=kapital("K_{n_1}"),
            ende=kapital("K_n", kante=LEFT * -1),
        )
        self.auf_buehne(self.strahl)
        kopf = self.kopf(r"K_n=K_0\cdot q^{n}")
        self.add(karte)

        self.einstieg(
            "Wie rechnest du bei einem", "Zinssatzwechsel?",
            bild=self.strahl.aufbau(),
            kopf=kopf,
        )

        # ---------- Zwei Phasen ----------
        aufgabe = wortlaut(
            "Eine Tischlerei legt 20 000 € an:", "3 Jahre zu 2 %, danach 5 Jahre", "zu einem anderen Zinssatz.",
            "Am Ende sind es 25 200 €.",
        )
        self.tafel(aufgabe)
        with self.sprich(
            "Eine Tischlerei legt 20.000 Euro an: 3 Jahre zu 2 %, "
            "danach 5 Jahre zu einem anderen Zinssatz. Am Ende sind es 25.200 Euro."
        ):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(0.15)
            self.play(self.strahl.zeige(anfang=kapital("K_0", r"20\,000", kante=LEFT)), run_time=0.6)
            self.warte_bis(0.35)
            self.play(self.strahl.zeige(phase1=phase(1, "n_1=3", r"p_1=2\,\%")), run_time=0.6)
            self.warte_bis(0.6)
            self.play(self.strahl.zeige(phase2=phase(2, "n_2=5", r"p_2=\,?", HERVOR)), run_time=0.6)
            self.warte_bis(0.8)
            self.play(self.strahl.zeige(ende=kapital("K_8", r"25\,200", kante=LEFT * -1)), run_time=0.6)
        self.wait(0.4)

        schluessel = VGroup(
            reihe(text("Zwischenwert", groesse=40, gewicht=BOLD), formel("K_3", groesse=G_FORMEL), abstand=0.3,
                  grundlinie=True),
            text("Ende von Phase 1", groesse=G_TEXT),
            text("= Anfang von Phase 2", groesse=G_TEXT),
        ).arrange(DOWN, buff=0.35)
        self.tafel(schluessel)
        with self.sprich(
            "Am Übergang der beiden Zinsphasen steht der Zwischenwert K drei: "
            "das Endkapital der ersten und das Anfangskapital der zweiten Phase."
        ):
            self.play(FadeOut(aufgabe, shift=0.25 * UP), run_time=0.4)
            self.play(
                self.strahl.zeige(mitte=kapital("K_3", "?")), auftritt(schluessel[0]), run_time=0.6,
            )
            self.play(welle(self.strahl.trenner, HERVOR), run_time=0.6)
            self.warte_bis(0.5)
            self.play(self.strahl.phase(1), auftritt(schluessel[1]), run_time=0.6)
            self.warte_bis(0.75)
            self.play(self.strahl.phase(2), auftritt(schluessel[2]), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(schluessel, shift=0.25 * UP), self.strahl.phase(None), run_time=0.4)

        # ---------- Vorwärts ----------
        titel = richtung("Phase 2", "vorwärts")
        k3 = ergebnis("K_3", r"20\,000\cdot 1{,}02^{3}", r"21\,224{,}16", euro=True)
        block = self.tafel(titel, k3, abstand=0.7)
        with self.sprich(
            "Gesucht ist p zwei, die Unbekannte liegt also in Phase 2. Phase 1 kennen wir ganz. "
            "Also rechnen wir K drei vorwärts aus."
        ):
            self.play(self.strahl.betone("phase2"), run_time=0.6)
            self.warte_bis(0.25)
            self.play(auftritt(titel), run_time=0.5)
            self.warte_bis(0.5)
            self.play(self.strahl.phase(1), self.strahl.zeige(mitte=kapital("K_3", "?", HERVOR)), run_time=0.6)
            self.warte_bis(0.75)
            self.play(Write(k3), run_time=0.9)
        self.play(self.strahl.uebernimm("mitte", kapital("K_3", r"21\,224{,}16", HERVOR), k3[0][4]), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Phase 2 lösen ----------
        rechnung = [
            hervor(formel(r"25\,200", "=", r"21\,224{,}16\cdot", "q_2^{5}", groesse=G_FORMEL), 3),
            hervor(formel("q_2^{5}", r"\approx", "1{,}1873", groesse=G_FORMEL), 0),
            hervor(formel("q_2", "=", r"\sqrt[5]{1{,}1873}", r"\approx", "1{,}0349", groesse=G_FORMEL), 0, 4),
            hervor(formel("p_2", r"\approx", r"3{,}49\,\%", groesse=G_FORMEL), 0, 2),
        ]
        block = self.tafel(*rechnung, abstand=0.45)
        with self.sprich(
            "In Phase 2 ist K drei das Anfangskapital. Durch K drei teilen, fünfte Wurzel ziehen: "
            "p zwei ist etwa 3,49 %."
        ):
            self.play(
                self.strahl.phase(2),
                self.strahl.zeige(mitte=kapital("K_3", r"21\,224{,}16")),
                run_time=0.6,
            )
            for zeile, beginn in zip(rechnung, (0.1, 0.45, 0.6, 0.8)):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.7)
        self.play(
            self.strahl.uebernimm("phase2", phase(2, "n_2=5", r"p_2\approx 3{,}49\,\%", HERVOR), rechnung[-1][2]),
            run_time=0.7,
        )
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), self.strahl.phase(None), run_time=0.4)

        # ---------- Rückwärts ----------
        titel = richtung("Phase 1", "rückwärts")
        k3 = ergebnis("K_3", r"\frac{25\,200}{1{,}035^{5}}", r"21\,217{,}72", euro=True)
        q1 = hervor(
            formel("q_1", "=", r"\sqrt[3]{\frac{21\,217{,}72}{20\,000}}", r"\approx", "1{,}0199", groesse=G_FORMEL), 0, 4,
        )
        p1 = hervor(formel("p_1", r"\approx", r"1{,}99\,\%", groesse=G_FORMEL), 0, 2)
        block = self.tafel(titel, k3, q1, p1, abstand=0.55)
        with self.sprich(
            "Ist dagegen p eins gesucht und p zwei bekannt, kommen wir in Phase 1 nicht vorwärts. "
            "Dann rechnen wir rückwärts: K acht durch 1,035 hoch 5. "
            "Danach in Phase 1 auflösen: p eins ist etwa 1,99 %."
        ):
            self.play(
                self.strahl.zeige(
                    phase1=phase(1, "n_1=3", r"p_1=\,?", HERVOR),
                    phase2=phase(2, "n_2=5", r"p_2=3{,}5\,\%"),
                    mitte=kapital("K_3", "?", HERVOR),
                ),
                run_time=0.7,
            )
            self.warte_bis(0.2)
            self.play(auftritt(titel), run_time=0.5)
            self.warte_bis(0.38)
            self.play(self.strahl.phase(2), run_time=0.5)
            self.play(Write(k3), run_time=0.9)
            self.play(self.strahl.uebernimm("mitte", kapital("K_3", r"21\,217{,}72", HERVOR), k3[0][4]), run_time=0.7)
            self.warte_bis(0.7)
            self.play(
                self.strahl.phase(1), self.strahl.zeige(mitte=kapital("K_3", r"21\,217{,}72")), Write(q1),
                run_time=0.9,
            )
            self.warte_bis(0.88)
            self.play(Write(p1), run_time=0.6)
        self.play(
            self.strahl.uebernimm("phase1", phase(1, "n_1=3", r"p_1\approx 1{,}99\,\%", HERVOR), p1[2]),
            run_time=0.7,
        )
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), self.strahl.phase(None), run_time=0.4)

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Phase der Unbekannten erkennen", groesse=G_TEXT),
            reihe(formel("K_{n_1}", groesse=50), text("in der anderen Phase berechnen", groesse=G_TEXT), abstand=0.2,
                  grundlinie=True),
            VGroup(
                text("Nach der Unbekannten auflösen", groesse=G_TEXT),
                text("3 von 4 Größen sind jetzt bekannt", groesse=G_TEXT, farbe=TEXT_LEISE),
            ).arrange(DOWN, buff=0.18, aligned_edge=LEFT),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Erkennen, in welcher Phase die Unbekannte steckt. "
            "Den Zwischenwert in der anderen Phase berechnen. "
            "Dann sind 3 von 4 Größen bekannt, und wir lösen nach der Unbekannten auf."
        ):
            for zeile, beginn in zip(schritte, (0.1, 0.4, 0.68)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
