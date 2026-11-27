"""Check 06 – Zinssatzwechsel im Darlehen.

Kernidee: Die Restschuld beim Wechsel wird noch mit dem alten Zinssatz und der alten Annuität berechnet und ist
dann das neue Darlehen; mit Restlaufzeit und neuem Zinssatz folgt die neue Annuität.
Beispiel: Pflegedienst wie im Musterbeispiel (250 000 €, 20 Jahre, 3 %, nach 5 Jahren 4,5 %), ohne Abweichung.
"""
from manim import DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, Mobject, VGroup, Write

from mcvideo import MCSzene, Phasenstrahl, auftritt, betrag, formel, kurzfassung, reihe, schritt, text, welle, wortlaut
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist der Wert, der gerade berechnet wird: erst A_1, dann RK_5, dann A_2.
G_FORMEL = 50
G_TEXT = 36
G_STRAHL = 36
G_PHASE = 26


def angabe(tex: str, farbe: str = TEXT) -> Mobject:
    return formel(tex, groesse=G_STRAHL, farbe=farbe)


def phase(nr: int, dauer: str, zins: str, annuitaet: Mobject | None = None) -> VGroup:
    """Angabe über einer Phase: Titel, Dauer und Zinssatz, darunter die Annuität dieser Phase."""
    zeilen = [
        text(f"Phase {nr}", groesse=G_PHASE, farbe=TEXT_LEISE),
        reihe(text(dauer, groesse=30), angabe(zins), abstand=0.3, grundlinie=True),
    ]
    if annuitaet is not None:
        zeilen.append(annuitaet)
    return VGroup(*zeilen).arrange(DOWN, buff=0.14)


def ann(name: str, wert: str | None = None, farbe: str = TEXT) -> Mobject:
    if wert is None:
        return angabe(f"{name}=\\,?", farbe)
    return betrag(f"{name}\\approx {wert}", groesse=G_STRAHL, farbe=farbe)


def kapital(name: str, wert: str | None = None, farbe: str = TEXT, kante: object = None) -> VGroup:
    """Angabe unter dem Strahl: Name, darunter Wert in Euro oder ein Fragezeichen."""
    zeilen = [angabe(name, farbe)]
    if wert == "?":
        zeilen.append(angabe("?", farbe))
    elif wert is not None:
        zeilen.append(betrag(wert, groesse=G_STRAHL, farbe=farbe))
    gruppe = VGroup(*zeilen)
    return gruppe.arrange(DOWN, buff=0.14, aligned_edge=kante) if kante is not None else gruppe.arrange(DOWN, buff=0.14)


def ergebnis(name: str, rechnung: str, wert: str) -> VGroup:
    """Zeile „Name = Rechnung“ und darunter „≈ Wert €“; Name und Wert orange."""
    oben = formel(name, "=", rechnung, groesse=G_FORMEL)
    oben[0].set_color(HERVOR)
    unten = betrag(r"\approx", wert, groesse=G_FORMEL)
    unten[0][1].set_color(HERVOR)
    unten[1].set_color(HERVOR)
    return VGroup(oben, unten).arrange(DOWN, buff=0.3)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.7)
        self.strahl = Phasenstrahl(
            teilung=0.4,
            phase1=phase(1, "5 Jahre", r"3\,\%"),
            phase2=phase(2, "15 Jahre", r"4{,}5\,\%"),
            anfang=kapital("K_0", kante=LEFT),
            mitte=kapital("RK_5"),
            ende=kapital("RK_{20}", kante=RIGHT),
        )
        strahl = self.strahl
        self.auf_buehne(strahl)
        self.add(karte)

        self.einstieg(
            "Wie rechnest du bei einem", "Zinssatzwechsel im Darlehen?",
            bild=strahl.aufbau(),
        )

        # ---------- Aufgabe ----------
        aufgabe = wortlaut(
            "Ein Pflegedienst tilgt 250 000 €", "in 20 Jahren, zunächst zu 3 %.", "Nach 5 Jahren steigt der Zinssatz",
            "auf 4,5 %; die Laufzeit bleibt.",
        )
        block = self.tafel(aufgabe)
        with self.sprich(
            "Ein Pflegedienst tilgt zweihundertfünfzigtausend Euro in zwanzig Jahren, zunächst zu drei Prozent. "
            "Nach fünf Jahren steigt der Zinssatz auf viereinhalb Prozent, die Gesamtlaufzeit bleibt."
        ):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(0.15)
            self.play(strahl.zeige(anfang=kapital("K_0", r"250\,000", kante=LEFT)), run_time=0.6)
            self.warte_bis(0.35)
            self.play(strahl.zeige(ende=kapital("RK_{20}", "0", kante=RIGHT)), strahl.phase(1), run_time=0.6)
            self.warte_bis(0.6)
            self.play(strahl.phase(2), welle(strahl.trenner, HERVOR), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), strahl.phase(None), run_time=0.4)

        # ---------- 1 Erste Annuität ----------
        titel = schritt(1, "Erste Annuität")
        a1 = ergebnis("A_1", r"\frac{250\,000\cdot 1{,}03^{20}\cdot 0{,}03}{1{,}03^{20}-1}", r"16\,803{,}93")
        hinweis = text("n = 20: die ganze Laufzeit", groesse=30, farbe=TEXT_LEISE)
        block = self.tafel(titel, a1, hinweis, abstand=0.5)
        with self.sprich(
            "Die erste Annuität ist so geplant, als bliebe es bei drei Prozent: "
            "mit der ganzen Laufzeit von zwanzig Jahren. Etwa sechzehntausendachthundertvier Euro."
        ):
            self.play(
                auftritt(titel), strahl.zeige(phase1=phase(1, "5 Jahre", r"3\,\%", ann("A_1", farbe=HERVOR))),
                run_time=0.6,
            )
            self.warte_bis(0.3)
            self.play(Write(a1[0]), run_time=0.9)
            self.play(auftritt(hinweis), run_time=0.5)
            self.warte_bis(0.8)
            self.play(Write(a1[1]), run_time=0.6)
        self.play(
            strahl.uebernimm("phase1", phase(1, "5 Jahre", r"3\,\%", ann("A_1", r"16\,804", HERVOR)), a1[1]),
            run_time=0.7,
        )
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP),
                  strahl.zeige(phase1=phase(1, "5 Jahre", r"3\,\%", ann("A_1", r"16\,804"))), run_time=0.4)

        # ---------- 2 Restschuld beim Wechsel ----------
        titel = schritt(2, "Restschuld beim Wechsel")
        rk5 = ergebnis("RK_5", r"250\,000\cdot 1{,}03^{5}", r"200\,604{,}17")
        abzug = formel(r"-\frac{16\,803{,}93\cdot(1{,}03^{5}-1)}{0{,}03}", groesse=G_FORMEL)
        abzug.next_to(rk5[0], DOWN, buff=0.25).align_to(rk5[0][2], LEFT)
        rk5[1].next_to(abzug, DOWN, buff=0.3).set_x(rk5[0].get_x())
        rk5.insert(1, abzug)
        hinweis = text("noch mit 3 % und der ersten Annuität", groesse=30, farbe=TEXT_LEISE)
        block = self.tafel(titel, rk5, hinweis, abstand=0.5)
        with self.sprich(
            "Bis zum Wechsel galten drei Prozent. Mit der Restschuldformel bleiben nach fünf Jahren "
            "etwa zweihunderttausendsechshundertvier Euro."
        ):
            self.play(auftritt(titel), strahl.phase(1), strahl.zeige(mitte=kapital("RK_5", "?", HERVOR)), run_time=0.6)
            self.play(auftritt(hinweis), run_time=0.5)
            self.warte_bis(0.35)
            self.play(Write(rk5[0]), run_time=0.7)
            self.play(Write(rk5[1]), run_time=0.8)
            self.warte_bis(0.75)
            self.play(Write(rk5[2]), run_time=0.6)
        self.play(strahl.uebernimm("mitte", kapital("RK_5", r"200\,604{,}17", HERVOR), rk5[2]), run_time=0.7)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), strahl.phase(None), run_time=0.4)

        # ---------- 3 Neue Annuität ----------
        titel = schritt(3, "Neue Annuität")
        neu = reihe(
            text("neues Darlehen:", groesse=30, farbe=TEXT_LEISE),
            formel(r"K_0=RK_5,\ n=15,\ q=1{,}045", groesse=40, farbe=TEXT_LEISE),
            abstand=0.25, grundlinie=True,
        )
        a2 = ergebnis("A_2", r"\frac{200\,604{,}17\cdot 1{,}045^{15}\cdot 0{,}045}{1{,}045^{15}-1}", r"18\,679{,}02")
        block = self.tafel(titel, neu, a2, abstand=0.5)
        with self.sprich(
            "Diese Restschuld behandeln wir wie ein neues Darlehen: fünfzehn Jahre zu viereinhalb Prozent. "
            "Die neue Annuität beträgt etwa achtzehntausendsechshundertneunundsiebzig Euro."
        ):
            self.play(
                auftritt(titel), strahl.phase(2),
                strahl.zeige(
                    mitte=kapital("RK_5", r"200\,604{,}17"),
                    phase2=phase(2, "15 Jahre", r"4{,}5\,\%", ann("A_2", farbe=HERVOR)),
                ),
                run_time=0.6,
            )
            self.play(strahl.betone("mitte"), auftritt(neu), run_time=0.7)
            self.warte_bis(0.45)
            self.play(Write(a2[0]), run_time=1.0)
            self.warte_bis(0.8)
            self.play(Write(a2[1]), run_time=0.6)
        self.play(
            strahl.uebernimm("phase2", phase(2, "15 Jahre", r"4{,}5\,\%", ann("A_2", r"18\,679", HERVOR)), a2[1]),
            run_time=0.7,
        )
        self.wait(0.5)
        self.play(FadeOut(block, shift=0.25 * UP), strahl.phase(None), run_time=0.4)

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            VGroup(
                text("Erste Annuität", groesse=G_TEXT),
                text("mit der ganzen Laufzeit", groesse=30, farbe=TEXT_LEISE),
            ).arrange(DOWN, buff=0.12, aligned_edge=LEFT),
            VGroup(
                text("Restschuld beim Wechsel", groesse=G_TEXT),
                reihe(text("= neues", groesse=30, farbe=TEXT_LEISE), formel("K_0", groesse=40, farbe=TEXT_LEISE),
                      abstand=0.15, grundlinie=True),
            ).arrange(DOWN, buff=0.12, aligned_edge=LEFT),
            VGroup(
                text("Neue Annuität", groesse=G_TEXT),
                text("mit Restlaufzeit und neuem Zinssatz", groesse=30, farbe=TEXT_LEISE),
            ).arrange(DOWN, buff=0.12, aligned_edge=LEFT),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Erste Annuität mit der ganzen Laufzeit. Die Restschuld beim Wechsel ist das neue K null. "
            "Daraus die neue Annuität mit Restlaufzeit und neuem Zinssatz."
        ):
            for zeile, beginn in zip(schritte, (0.08, 0.35, 0.65)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

