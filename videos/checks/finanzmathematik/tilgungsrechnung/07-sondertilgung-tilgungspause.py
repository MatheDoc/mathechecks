"""Check 07 – Sondertilgung & Tilgungspause.

Kernidee: Die aktuelle Restschuld ist das neue K_0. Laufzeit fest → neue Annuität (Annuitätenformel);
Annuität fest → neue Laufzeit (A = T_1 · q^n). Eine Sondertilgung senkt die Restschuld, bei einer Tilgungspause
bleibt sie gleich (nur Zinsen).
Beispiel: Fahrradladen wie im Musterbeispiel (100 000 €, 4 %, 15 Jahre, A = 8 994,11 €, Sondertilgung 20 000 €
mit der 5. Annuität); die Tilgungspause als kurzer zweiter Fall wie in der Variante des Musterbeispiels,
dort nur mit Ergebnissen.
"""
from manim import DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, Mobject, VGroup, Write

from mcvideo import (
    MCSzene, Phasenstrahl, aufzaehlung, auftritt, betrag, formel, legende, reihe, text, welle, wortlaut,
)
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist die Größe, die gerade berechnet wird.
G_FORMEL = 50
G_TEXT = 36
G_STRAHL = 36
G_PHASE = 26


def angabe(tex: str, farbe: str = TEXT) -> Mobject:
    return formel(tex, groesse=G_STRAHL, farbe=farbe)


def phase(titel: str, *zeilen: Mobject) -> VGroup:
    return VGroup(text(titel, groesse=G_PHASE, farbe=TEXT_LEISE), *zeilen).arrange(DOWN, buff=0.14)


def dauer(inhalt: str, farbe: str = TEXT) -> Mobject:
    return text(inhalt, groesse=30, farbe=farbe)


def kapital(name: str, wert: str | None = None, farbe: str = TEXT, kante: object = None) -> VGroup:
    zeilen = [angabe(name, farbe)]
    if wert == "?":
        zeilen.append(angabe("?", farbe))
    elif wert is not None:
        zeilen.append(betrag(wert, groesse=G_STRAHL, farbe=farbe))
    gruppe = VGroup(*zeilen)
    return gruppe.arrange(DOWN, buff=0.14, aligned_edge=kante) if kante is not None else gruppe.arrange(DOWN, buff=0.14)


def ergebnis(name: str, rel: str, wert: str, euro: bool = True) -> Mobject:
    zeile = (betrag if euro else formel)(name, rel, wert, groesse=G_FORMEL)
    tex = zeile[0] if euro else zeile
    tex[0].set_color(HERVOR)
    tex[2].set_color(HERVOR)
    if euro:
        zeile[1].set_color(HERVOR)
    return zeile


def ueberschrift(inhalt: str) -> Mobject:
    return text(inhalt, groesse=42)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.4)
        strahl = self.strahl = Phasenstrahl(
            teilung=0.4,
            phase1=phase("bisher", dauer("5 Jahre"), angabe(r"4\,\%")),
            phase2=phase("danach", dauer("10 Jahre")),
            anfang=kapital("K_0", kante=LEFT),
            mitte=kapital("RK_5"),
            ende=kapital("RK", "0", kante=RIGHT),
        )
        self.auf_buehne(strahl)
        self.add(karte)

        self.einstieg(
            "Was ändern Sondertilgung", "und Tilgungspause?",
            bild=strahl.aufbau(),
        )

        # ---------- Aufgabe und Restschuld ----------
        aufgabe = wortlaut(
            "Ein Fahrradladen tilgt 100 000 €", "zu 4 % in 15 Jahren,", "Annuität 8 994,11 €.", "Mit der 5. Annuität zahlt er",
            "20 000 € extra.",
            signal=("extra",), groesse=36,
        )
        block = self.tafel(aufgabe)
        with self.sprich(
            "Ein Fahrradladen tilgt 100.000 Euro zu 4 % in 15 Jahren. "
            "Mit der fünften Annuität zahlt er 20.000 Euro extra."
        ):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(0.15)
            self.play(strahl.zeige(anfang=kapital("K_0", r"100\,000", kante=LEFT)), run_time=0.6)
            self.warte_bis(0.6)
            self.play(strahl.zeige(mitte=kapital("RK_5", "?", HERVOR)), welle(strahl.trenner, HERVOR), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        rk5 = ergebnis("RK_5", r"\approx", r"72\,950{,}29")
        herkunft = text("Restschuldformel", groesse=28, farbe=TEXT_LEISE)
        sonder = betrag(r"-\,20\,000", groesse=G_FORMEL)
        neu = ergebnis("RK_5'", "=", r"52\,950{,}29")
        merke = reihe(text("neues", groesse=G_TEXT, farbe=TEXT_LEISE), formel("K_0", groesse=46, farbe=TEXT_LEISE),
                      abstand=0.15, grundlinie=True)
        block = self.tafel(VGroup(rk5, herkunft).arrange(DOWN, buff=0.12), sonder, neu, merke, abstand=0.4)
        with self.sprich(
            "Die Restschuldformel liefert nach 5 Jahren etwa 72.950 Euro. "
            "Die Sondertilgung senkt sie auf 52.950 Euro. "
            "Das ist jetzt das neue K null."
        ):
            self.play(strahl.phase(1), Write(rk5), FadeIn(herkunft), run_time=0.9)
            self.play(strahl.uebernimm("mitte", kapital("RK_5", r"72\,950{,}29", HERVOR), rk5[0][2]), run_time=0.6)
            self.warte_bis(0.45)
            self.play(auftritt(sonder), run_time=0.5)
            self.play(Write(neu), run_time=0.8)
            self.play(strahl.uebernimm("mitte", kapital("RK_5'", r"52\,950{,}29", HERVOR), neu[0][2]), run_time=0.6)
            self.warte_bis(0.85)
            self.play(auftritt(merke), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), strahl.phase(None),
                  strahl.zeige(mitte=kapital("RK_5'", r"52\,950{,}29")), run_time=0.4)

        # ---------- Laufzeit bleibt ----------
        titel = ueberschrift("Laufzeit bleibt")
        a_neu = formel("A'", "=", r"\frac{52\,950{,}29\cdot 1{,}04^{10}\cdot 0{,}04}{1{,}04^{10}-1}", groesse=G_FORMEL)
        a_neu[0].set_color(HERVOR)
        a_wert = betrag(r"\approx", r"6\,528{,}29", groesse=G_FORMEL)
        a_wert[0][1].set_color(HERVOR)
        a_wert[1].set_color(HERVOR)
        block = self.tafel(titel, a_neu, a_wert, abstand=0.45)
        with self.sprich(
            "Jetzt gibt es 2 Wege. Bleibt die Laufzeit, gibt es für die restlichen 10 Jahre "
            "eine neue Annuität: etwa 6528 Euro."
        ):
            self.play(auftritt(titel), strahl.phase(2), run_time=0.5)
            self.warte_bis(0.25)
            self.play(strahl.zeige(phase2=phase("danach", dauer("10 Jahre"), angabe(r"A'=\,?", HERVOR))), run_time=0.5)
            self.play(Write(a_neu), run_time=1.0)
            self.warte_bis(0.75)
            self.play(Write(a_wert), run_time=0.6)
        self.play(
            strahl.uebernimm("phase2", phase("danach", dauer("10 Jahre"),
                                             betrag(r"A'\approx 6\,528", groesse=G_STRAHL, farbe=HERVOR)), a_wert),
            run_time=0.7,
        )
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Annuität bleibt ----------
        titel = ueberschrift("Annuität bleibt")
        t1 = betrag("T_1'", "=", r"8\,994{,}11-52\,950{,}29\cdot 0{,}04", r"\approx", r"6\,876{,}10", groesse=G_FORMEL)
        gleichung = formel(r"8\,994{,}11", "=", r"6\,876{,}10\cdot 1{,}04", "^{n}", groesse=G_FORMEL)
        gleichung[3].set_color(HERVOR)
        n = ergebnis("n", r"\approx", "6{,}85", euro=False)
        block = self.tafel(titel, t1, gleichung, n, abstand=0.45)
        with self.sprich(
            "Bleibt die Annuität, wird die Laufzeit kürzer. Erst die neue Tilgung T eins, "
            "dann A gleich T eins mal q hoch n: nur noch etwa 6,85 Jahre."
        ):
            self.play(
                auftritt(titel),
                strahl.zeige(phase2=phase("danach", dauer("n = ?", HERVOR), betrag(r"A=8\,994{,}11", groesse=G_STRAHL))),
                run_time=0.6,
            )
            self.warte_bis(0.3)
            self.play(Write(t1), run_time=0.9)
            self.warte_bis(0.6)
            self.play(Write(gleichung), run_time=0.8)
            self.warte_bis(0.85)
            self.play(Write(n), run_time=0.6)
        self.play(
            strahl.uebernimm("phase2", phase("danach", dauer("≈ 6,85 Jahre", HERVOR),
                                             betrag(r"A=8\,994{,}11", groesse=G_STRAHL)), n[2]),
            run_time=0.7,
        )
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), strahl.phase(None), run_time=0.4)

        # ---------- Tilgungspause ----------
        titel = ueberschrift("Tilgungspause statt Sondertilgung")
        zinsen = reihe(
            text("Jahr 6: nur Zinsen", groesse=G_TEXT),
            betrag(r"\approx 2\,918{,}01", groesse=G_FORMEL),
            abstand=0.3, grundlinie=True,
        )
        bleibt = text("Restschuld bleibt gleich", groesse=G_TEXT, farbe=TEXT_LEISE)
        block = self.tafel(titel, zinsen, bleibt, abstand=0.5)
        with self.sprich(
            "Bei einer Tilgungspause zahlt der Laden im sechsten Jahr nur die Zinsen, "
            "etwa 2918 Euro. Die Restschuld bleibt gleich."
        ):
            self.play(
                auftritt(titel),
                strahl.zeige(
                    mitte=kapital("RK_5", r"72\,950{,}29"),
                    phase2=phase("danach", dauer("Pause, dann 9 Jahre")),
                ),
                run_time=0.7,
            )
            self.warte_bis(0.35)
            self.play(auftritt(zinsen), run_time=0.6)
            self.warte_bis(0.75)
            self.play(auftritt(bleibt), strahl.betone("mitte"), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(VGroup(zinsen, bleibt), shift=0.25 * UP), run_time=0.4)

        wege = VGroup(
            VGroup(text("Laufzeit bleibt", groesse=32, farbe=TEXT_LEISE),
                   betrag(r"A'\approx 9\,811{,}30", groesse=G_FORMEL)).arrange(DOWN, buff=0.15),
            VGroup(text("Annuität bleibt", groesse=32, farbe=TEXT_LEISE),
                   text("noch 10 Jahre", groesse=40)).arrange(DOWN, buff=0.15),
        ).arrange(DOWN, buff=0.55)
        wege.next_to(titel, DOWN, buff=0.7).set_x(0)
        with self.sprich(
            "Danach dieselben 2 Wege: Bleibt die Laufzeit, steigt die Annuität für die restlichen 9 Jahre "
            "auf etwa 9811 Euro. Bleibt die Annuität, dauert es danach noch 10 Jahre."
        ):
            self.warte_bis(0.15)
            self.play(auftritt(wege[0]), run_time=0.6)
            self.warte_bis(0.65)
            self.play(auftritt(wege[1]), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(titel, shift=0.25 * UP), FadeOut(wege, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        def stich(inhalt: str) -> Mobject:
            return text(inhalt, groesse=30, farbe=TEXT_LEISE)

        punkte = aufzaehlung(
            (stich("Sondertilgung"), text("Restschuld sinkt", groesse=38)),
            (stich("Tilgungspause"), text("Restschuld bleibt", groesse=38)),
            (stich("Laufzeit fest"), text("Annuitätenformel", groesse=38)),
            (stich("Annuität fest"), formel(r"A=T_1\cdot q^n", groesse=52)),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Die aktuelle Restschuld ist das neue K null. Bei fester Laufzeit die Annuitätenformel, "
            "bei fester Annuität A gleich T eins mal q hoch n."
        ):
            for zeile, beginn in zip(punkte, (0.05, 0.25, 0.5, 0.72)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
