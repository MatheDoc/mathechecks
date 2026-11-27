"""Check 05 – Kapitalauf- und -abbau im Sachkontext.

Kernidee: Startkapital und regelmäßige Zahlungen zugleich → Kombination E_n = K_0 · q^n ± R_n.
Einzahlungen plus, Entnahmen minus; „aufgebraucht“ heißt E_n = 0. Zahlungsweise und gesuchte Größe aus dem Text.
Beispiel: Ingenieurbüro wie im Musterbeispiel a) und b). Fall c (K_0 gesucht) mit eigenen Zahlen:
10 Jahre am Jahresende 4 000 € entnehmen, danach noch 10 000 €, 2 % → K_0 ≈ 44 133,82 €.
"""
from collections.abc import Callable

from manim import DOWN, LEFT, RIGHT, UP, Animation, FadeOut, Mobject, VGroup, Write

from mcvideo import MCSzene, Rentenstrahl, auftritt, betrag, formel, kurzfassung, text, welle, wortlaut
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist die gesuchte Größe (Wortlaut, Strahl, Rechnung); im Wortlaut auch die Signalwörter.
G_FORMEL = 46
G_TEXT = 36
G_WORT = 32
G_STRAHL = 46


def hervor(zeile, *teile: int):
    for teil in teile:
        zeile[teil].set_color(HERVOR)
    return zeile


def ergebnis(name: str, wert: str, euro: bool = False) -> Mobject:
    zeile = (betrag if euro else formel)(name, r"\approx", wert, groesse=G_FORMEL, farbe=HERVOR)
    (zeile[0] if euro else zeile)[1].set_color(TEXT)
    return zeile


def wert(name: str, inhalt: str | None, kante, farbe: str = TEXT) -> VGroup:
    """Angabe unter dem Strahl: Name, darunter Betrag in Euro oder Fragezeichen."""
    zeilen = [formel(name, groesse=G_STRAHL, farbe=farbe)]
    if inhalt == "?":
        zeilen.append(formel("?", groesse=G_STRAHL, farbe=farbe))
    elif inhalt is not None:
        zeilen.append(betrag(inhalt, groesse=G_STRAHL, farbe=farbe))
    return VGroup(*zeilen).arrange(DOWN, buff=0.15, aligned_edge=kante)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.3)
        self.strahl = self.auf_buehne(Rentenstrahl()).shift(0.45 * UP)
        kopf = self.kopf(r"E_n=K_0\cdot q^n\pm R_n")
        self.add(karte)

        self.einstieg(
            "Wie erkennst du Kapitalauf-", "und -abbau im Text?",
            bild=self.strahl.aufbau(),
            kopf=kopf,
        )

        # ---------- a) Aufbau, nachschüssig, E_n gesucht ----------
        ergebnis_a = ergebnis("E_{12}", r"78\,220{,}11", euro=True)
        self.fall(
            wortlaut(
                "Ein Büro hat bereits 25 000 €", "angespart und zahlt 12 Jahre lang", "am Jahresende 3 000 € ein (3 %).",
                "Wie hoch ist das Guthaben am Ende?",
                signal=("bereits", "zahlt", "ein (", "am Jahresende", "Wie hoch ist das Guthaben am Ende?"),
                groesse=G_WORT,
            ),
            [
                hervor(formel("E_{12}", "=", r"25\,000\cdot 1{,}03^{12}+\frac{3\,000\cdot(1{,}03^{12}-1)}{0{,}03}",
                              groesse=G_FORMEL), 0),
                hervor(formel("E_{12}", r"\approx", r"35\,644{,}02+42\,576{,}09", groesse=G_FORMEL), 0),
                ergebnis_a,
            ],
            gegeben=lambda: [
                self.strahl.zeige(barwert=wert("K_0", r"25\,000", LEFT)), self.strahl.rate(r"+3\,000"),
            ],
            gesucht=lambda: [self.strahl.zeige(endwert=wert("E_{12}", "?", RIGHT, HERVOR))],
            gegeben_ab=0.5, gesucht_ab=0.82, rechnung_ab=(0.86, 0.92, 0.97),
            uebernahme=("endwert", wert("E_{12}", r"\approx 78\,220{,}11", RIGHT, HERVOR), ergebnis_a),
            sprechtext="Ein Büro hat bereits fünfundzwanzigtausend Euro angespart und zahlt zwölf Jahre lang "
                       "am Jahresende dreitausend Euro ein. Wie hoch ist das Guthaben am Ende? "
                       "Startkapital und Raten zugleich: Das ist eine Kombination. Eingezahlt wird, also plus, "
                       "und zwar nachschüssig. Gesucht ist E zwölf.",
        )

        # ---------- b) Abbau, vorschüssig, n gesucht ----------
        jahr_n = self.strahl.jahre[-1]
        self.fall(
            wortlaut(
                "Das Büro hat 60 000 € zu 2 %", "angelegt und entnimmt jeweils", "zu Jahresbeginn 5 000 €. Wann ist",
                "das Kapital aufgebraucht?",
                signal=("entnimmt", "zu Jahresbeginn", "Wann ist", "aufgebraucht?"), groesse=G_WORT,
            ),
            [
                hervor(formel("0", "=", r"60\,000\cdot 1{,}02", "^{n}",
                              r"-\frac{5\,000\cdot 1{,}02\cdot(1{,}02", "^{n}", r"-1)}{0{,}02}", groesse=G_FORMEL), 3, 5),
                hervor(formel("1{,}02", "^{n}", r"\approx", "1{,}3077", groesse=G_FORMEL), 1),
                hervor(formel("n", r"\approx", "13{,}55", groesse=G_FORMEL), 0, 2),
            ],
            gegeben=lambda: [
                self.strahl.zeige(barwert=wert("K_0", r"60\,000", LEFT)),
                self.strahl.raten_zu(r"-5\,000", vorschuessig=True),
            ],
            gesucht=lambda: [
                self.strahl.zeige(endwert=wert(r"\overline{E}_n", "0", RIGHT)),
                jahr_n.animate.set_color(HERVOR), welle(jahr_n, HERVOR),
            ],
            gegeben_ab=0.3, gesucht_ab=0.55, rechnung_ab=(0.66, 0.78, 0.86),
            nachher=lambda: [jahr_n.animate.set_color(TEXT_LEISE)],
            sprechtext="Jetzt hat das Büro sechzigtausend Euro angelegt und entnimmt zu Jahresbeginn "
                       "fünftausend Euro: also minus, und vorschüssig. Aufgebraucht heißt: E n gleich null. "
                       "Gesucht ist n. Nach q hoch n auflösen, logarithmieren: "
                       "Das reicht für dreizehn volle Entnahmen.",
        )

        # ---------- c) Abbau, nachschüssig, K_0 gesucht ----------
        ergebnis_c = ergebnis("K_0", r"44\,133{,}82", euro=True)
        self.fall(
            wortlaut(
                "Das Büro möchte 10 Jahre lang", "am Jahresende 4 000 € entnehmen", "und danach noch 10 000 € haben.",
                "Was muss es heute zu 2 % anlegen?",
                signal=("am Jahresende", "entnehmen", "Was muss es heute", "anlegen?"), groesse=G_WORT,
            ),
            [
                hervor(formel(r"10\,000", "=", "K_0", r"\cdot 1{,}02^{10}-\frac{4\,000\cdot(1{,}02^{10}-1)}{0{,}02}",
                              groesse=G_FORMEL), 2),
                hervor(formel(r"10\,000", "=", "K_0", r"\cdot 1{,}02^{10}-43\,798{,}88", groesse=G_FORMEL), 2),
                hervor(formel("K_0", "=", r"\frac{53\,798{,}88}{1{,}02^{10}}", groesse=G_FORMEL), 0),
                ergebnis_c,
            ],
            gegeben=lambda: [
                self.strahl.raten_zu(r"-4\,000", vorschuessig=False), self.strahl.zeige(endwert=wert("E_{10}", r"10\,000", RIGHT)),
            ],
            gesucht=lambda: [self.strahl.zeige(barwert=wert("K_0", "?", LEFT, HERVOR))],
            gegeben_ab=0.25, gesucht_ab=0.55, rechnung_ab=(0.64, 0.75, 0.86, 0.94),
            uebernahme=("barwert", wert("K_0", r"\approx 44\,133{,}82", LEFT, HERVOR), ergebnis_c),
            sprechtext="Und umgekehrt: Zehn Jahre lang am Jahresende viertausend Euro entnehmen, danach sollen "
                       "noch zehntausend übrig sein. Gesucht ist das Startkapital K null. "
                       "Wir rechnen den Rentenanteil aus und lösen nach K null auf.",
        )

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Vor- oder nachschüssig?", groesse=46),
            text("Einzahlung +, Entnahme −", groesse=46),
            text("Gesuchte Größe erkennen", groesse=46, farben={"Gesuchte Größe": HERVOR}),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Zahlungsweise klären. Startkapital und Raten kombinieren: Einzahlungen plus, "
            "Entnahmen minus. Dann die gesuchte Größe erkennen und auflösen."
        ):
            for zeile, beginn in zip(schritte, (0.05, 0.3, 0.7)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def fall(
        self,
        aufgabe: VGroup,
        rechnung: list[Mobject],
        *,
        gegeben: Callable[[], list[Animation]],
        gesucht: Callable[[], list[Animation]],
        sprechtext: str,
        gegeben_ab: float,
        gesucht_ab: float,
        rechnung_ab: tuple[float, ...],
        uebernahme: tuple[str, Mobject, Mobject] | None = None,
        nachher: Callable[[], list[Animation]] | None = None,
    ) -> None:
        """Eine Aufgabe: Wortlaut, Startkapital, Raten und Endwert auf dem Strahl, Rechnung, Ergebnis auf dem Strahl."""
        block = self.tafel(aufgabe, *rechnung, abstand=0.38)
        aufgabe.shift(0.3 * UP)  # etwas Abstand zwischen Wortlaut und Rechnung
        with self.sprich(sprechtext):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(gegeben_ab)
            self.play(*gegeben(), run_time=0.8)
            self.warte_bis(gesucht_ab)
            self.play(*gesucht(), run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.7)
        if uebernahme is not None:
            platz, angabe, quelle = uebernahme
            self.play(self.strahl.uebernimm(platz, angabe, quelle), run_time=0.7)
        self.wait(0.8)
        self.play(
            FadeOut(block, shift=0.25 * UP), self.strahl.zeige(barwert=None, endwert=None), self.strahl.rate("r"),
            *(nachher() if nachher else []), run_time=0.5,
        )
