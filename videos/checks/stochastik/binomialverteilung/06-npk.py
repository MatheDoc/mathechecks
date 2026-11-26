"""Check 06 – n, p oder k bestimmen.

Kernidee: Bedingung als Ungleichung notieren, die gesuchte Größe in der Wertetabelle schrittweise ändern und
den Übergang suchen: ein Wert erfüllt die Bedingung, sein Nachbar nicht. Dann kleinsten oder größten Wert wählen.
Beispiel: Restaurant wie im Musterbeispiel. n gesucht ausführlich (p = 0,61, P(X ≥ 144) ≥ 0,29: n = 228 → 0,2753,
n = 229 → 0,3042), p gesucht kurz (n = 200, P(X ≥ 130) ≥ 0,5: 0,64 → 0,4151, 0,65 → 0,5325).
k gesucht bewusst weggelassen: kommt in Abituraufgaben seltener vor und bei den Hypothesentests wieder.
"""
from manim import BOLD, DOWN, UP, FadeIn, FadeOut, Mobject, SurroundingRectangle, VGroup, Write

from mcvideo import MCSzene, auftritt, formel, kurzfassung, reihe, tabelle, text, wortlaut
from mcvideo.theme import HERVOR, TEXT_LEISE, TEXT_SCHWACH

G_FORMEL = 54
G_TEXT = 38
G_TABELLE = 44


def wertetabelle(kopf: tuple[str, str], zeilen: list[tuple[str, str]]) -> VGroup:
    """Wertetabelle wie im Taschenrechner: Kopfzeile grau, darunter die Zeilen."""
    return tabelle(
        tuple(formel(tex, groesse=G_TABELLE, farbe=TEXT_LEISE) for tex in kopf),
        *[tuple(formel(tex, groesse=G_TABELLE) for tex in zeile) for zeile in zeilen],
        abstand=(1.4, 0.28),
    )


def bedingung(tex: str) -> Mobject:
    zeile = formel(tex, groesse=G_FORMEL)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.6)
        self.add(karte)
        werte_n = [("226", "0{,}2215"), ("227", "0{,}2477"), ("228", "0{,}2753"), ("229", "0{,}3042"), ("230", "0{,}3342")]
        tab = self.auf_buehne(wertetabelle(("n", r"P(X\geq 144)"), werte_n))
        kopf = self.kopf(r"p=0{,}61\qquad k=144")

        self.einstieg(
            "Wie bestimmst du", "n oder p?",
            zusatz="(Bedingung an eine Wahrscheinlichkeit)",
            sprechtext="Wie bestimmst du n oder p, wenn eine Wahrscheinlichkeit eine Bedingung erfüllen soll?",
            bild=[FadeIn(tab[0]), *[FadeIn(zeile, shift=0.1 * DOWN) for zeile in tab[1:]]],
            kopf=kopf,
        )
        self.play(FadeOut(tab[1:]), run_time=0.4)

        # ---------- Aufgabe ----------
        aufgabe = self.tafel(
            text("Restaurant: 61 % vegetarisch", groesse=44, gewicht=BOLD),
            wortlaut("Wie viele Bestellungen mindestens,", "damit mindestens 144 vegetarische",
                     "mit mindestens 29 % dabei sind?", signal=("Bestellungen",), groesse=34),
            abstand=0.5,
        )
        with self.sprich(
            "Einundsechzig Prozent der Gäste eines Restaurants bestellen vegetarisch. Wie viele Bestellungen brauchen wir "
            "mindestens, damit mit mindestens neunundzwanzig Prozent mindestens hundertvierundvierzig vegetarische dabei sind?"
        ):
            self.play(auftritt(aufgabe[0]), run_time=0.5)
            self.warte_bis(0.3)
            self.play(auftritt(aufgabe[1]), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(aufgabe, shift=0.25 * UP), run_time=0.4)

        # ---------- Ungleichung und Richtung ----------
        gesucht = reihe(text("gesucht:", groesse=G_TEXT, farbe=TEXT_LEISE), formel("n", groesse=G_FORMEL, farbe=HERVOR),
                        abstand=0.25, grundlinie=True)
        ungleichung = bedingung(r"P(X\geq 144)\geq 0{,}29")
        richtung = reihe(formel("n", r"\uparrow", groesse=G_FORMEL), formel(r"\Rightarrow", groesse=G_FORMEL),
                         formel(r"P", r"\uparrow", groesse=G_FORMEL), abstand=0.4)
        richtung[0][0].set_color(HERVOR)
        block = self.tafel(gesucht, ungleichung, richtung, abstand=0.6)
        with self.sprich(
            "Gesucht ist n. Als Ungleichung: P von X größer gleich hundertvierundvierzig ist mindestens null Komma zwei neun. "
            "Mit mehr Bestellungen wird das wahrscheinlicher, also erhöhen wir n."
        ):
            self.play(auftritt(gesucht), run_time=0.5)
            self.warte_bis(0.2)
            self.play(Write(ungleichung), run_time=1.0)
            self.warte_bis(0.62)
            self.play(auftritt(richtung), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Probieren ----------
        self.probieren(
            tab, uebergang=3, ungleichung=r"P(X\geq 144)\geq 0{,}29",
            ergebnis=formel("n=229", groesse=G_FORMEL + 6, farbe=HERVOR),
            vergleich=(r"0{,}2753<0{,}29", r"0{,}3042\geq 0{,}29"),
            sprechtext="In der Wertetabelle suchen wir den Übergang: Bei zweihundertachtundzwanzig ist es zu wenig, "
                       "bei zweihundertneunundzwanzig reicht es. Das kleinste n ist zweihundertneunundzwanzig.",
        )
        self.play(FadeOut(tab), FadeOut(kopf), run_time=0.4)

        # ---------- p gesucht ----------
        werte_p = [("0{,}63", "0{,}3058"), ("0{,}64", "0{,}4151"), ("0{,}65", "0{,}5325"), ("0{,}66", "0{,}6480")]
        tab_p = self.auf_buehne(wertetabelle(("p", r"P(X\geq 130)"), werte_p))
        kopf_p = self.kopf(r"n=200\qquad k=130")
        block = self.tafel(
            reihe(text("gesucht:", groesse=G_TEXT, farbe=TEXT_LEISE), formel("p", groesse=G_FORMEL, farbe=HERVOR),
                  abstand=0.25, grundlinie=True),
            bedingung(r"P(X\geq 130)\geq 0{,}5"),
            reihe(formel("p", r"\uparrow", groesse=G_FORMEL), formel(r"\Rightarrow", groesse=G_FORMEL),
                  formel(r"P", r"\uparrow", groesse=G_FORMEL), abstand=0.4),
            abstand=0.6,
        )
        block[2][0][0].set_color(HERVOR)
        with self.sprich(
            "Genauso mit p: Bei zweihundert Bestellungen sollen mit mindestens fünfzig Prozent "
            "mindestens hundertdreißig vegetarisch sein. Größeres p macht das wahrscheinlicher."
        ):
            self.play(FadeIn(kopf_p), FadeIn(tab_p[0]), auftritt(block[0]), run_time=0.6)
            self.warte_bis(0.25)
            self.play(Write(block[1]), run_time=0.9)
            self.warte_bis(0.72)
            self.play(auftritt(block[2]), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)
        self.probieren(
            tab_p, uebergang=2, ungleichung=r"P(X\geq 130)\geq 0{,}5",
            ergebnis=formel("p=0{,}65", groesse=G_FORMEL + 6, farbe=HERVOR),
            vergleich=(r"0{,}4151<0{,}5", r"0{,}5325\geq 0{,}5"),
            sprechtext="Wir erhöhen p in Hundertsteln: Bei null Komma sechs vier reicht es nicht, "
                       "bei null Komma sechs fünf schon.",
        )

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Ungleichung notieren", groesse=48),
            text("schrittweise ändern", groesse=48),
            text("Übergang suchen", groesse=48),
            text("kleinster oder größter Wert?", groesse=48),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Ungleichung notieren, schrittweise ändern, Übergang suchen. "
            "Und prüfen: Ist der kleinste oder der größte Wert gesucht?"
        ):
            for zeile, beginn in zip(schritte, (0.1, 0.3, 0.5, 0.68)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def probieren(
        self,
        tab: VGroup,
        *,
        uebergang: int,
        ungleichung: str,
        ergebnis: Mobject,
        vergleich: tuple[str, str],
        sprechtext: str,
    ) -> None:
        """Wertetabelle zeilenweise füllen, den Übergang (Zeile uebergang und die davor) markieren, Ergebnis."""
        zu_wenig, reicht = tab[uebergang], tab[uebergang + 1]
        rahmen = SurroundingRectangle(reicht, color=HERVOR, buff=0.12, corner_radius=0.1)
        block = self.tafel(
            formel(ungleichung, groesse=G_FORMEL, farbe=TEXT_LEISE),
            formel(vergleich[0], groesse=G_FORMEL),
            formel(vergleich[1], groesse=G_FORMEL),
            ergebnis,
            abstand=0.45,
        )
        with self.sprich(sprechtext):
            self.play(auftritt(block[0]), *[FadeIn(zeile, shift=0.1 * DOWN) for zeile in tab[1:]], run_time=0.9)
            self.warte_bis(0.3)
            self.play(zu_wenig.animate.set_color(TEXT_SCHWACH), Write(block[1]), run_time=0.7)
            self.warte_bis(0.55)
            self.play(reicht.animate.set_color(HERVOR), FadeIn(rahmen), Write(block[2]), run_time=0.7)
            self.warte_bis(0.82)
            self.play(Write(ergebnis), run_time=0.6)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(rahmen), run_time=0.4)
