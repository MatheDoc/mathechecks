"""Check 02 – Zinseszins im Sachkontext.

Kernidee: Der frühere Betrag ist K_0, der spätere K_n; der Fragesatz verrät die gesuchte Größe.
Dann in K_n = K_0 · q^n einsetzen und auflösen.
Beispiel: Schulförderverein wie im Musterbeispiel (K_n und n unverändert). Die Fälle K_0 und p stammen
mit ihren Zahlen aus dem Warm-Up und sind auf den Verein übertragen.
"""
import re

from manim import BOLD, DOWN, LEFT, RIGHT, UP, FadeOut, MathTex, Mobject, Text, VGroup, Write

from mcvideo import MCSzene, Zeitstrahl, auftritt, betrag, formel, kurzfassung, legende, reihe, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist allein die gesuchte Größe: im Fragesatz, auf dem Zeitstrahl und in der Rechnung.
# Alles Gegebene bleibt weiß; zugeordnet wird es über seinen Platz auf dem Zeitstrahl.
TEILE = {"K_n": 0, "K_0": 2, "q": 4, "n": 5}  # Teile von K_n = K_0 · q ^n

# Die flache Bühne lässt der Tafel viel Platz; der Wortlaut braucht ihn.
G_FORMEL = 50
G_TEXT = 36
G_WORT = 32
G_STRAHL = 40
G_ZEIT = 28


def tausender(inhalt: str) -> str:
    """Setzt in Zahlen wie 12 000 ein schmales Leerzeichen."""
    return re.sub(r"(?<=\d) (?=\d{3})", "\u202f", inhalt)


def wortlaut(*zeilen: str, signal: tuple[str, ...]) -> VGroup:
    """Wortlaut der Aufgabe in Anführungszeichen, eine Bildzeile je Argument.

    signal: Wörter des Fragesatzes, die die gesuchte Größe verraten.
    """
    zeilen = (f"„{zeilen[0]}", *zeilen[1:-1], f"{zeilen[-1]}“")
    farben = {wort: HERVOR for wort in signal}
    bild = [text(tausender(zeile), groesse=G_WORT, gewicht=BOLD, farben=farben) for zeile in zeilen]
    return VGroup(*bild).arrange(DOWN, buff=0.2, aligned_edge=LEFT)


def hervor(zeile: MathTex, *teile: int) -> MathTex:
    """Färbt die Teile einer Formel, die zur gesuchten Größe gehören."""
    for teil in teile:
        zeile[teil].set_color(HERVOR)
    return zeile


def zinseszins(kn: str, k0: str, q: str, n: str, gesucht: str | None = None, groesse: float = G_FORMEL) -> MathTex:
    """Zinseszinsformel mit eingesetzten Werten; gesucht nennt die Größe, die noch unbekannt ist."""
    zeile = formel(kn, "=", k0, r"\cdot", q, f"^{{{n}}}", groesse=groesse)
    return hervor(zeile, TEILE[gesucht]) if gesucht else zeile


def naeherung(name: str, wert: str, euro: bool = False) -> Mobject:
    """Ergebniszeile „Name ≈ Wert“ für die gesuchte Größe."""
    zeile = (betrag if euro else formel)(name, r"\approx", wert, groesse=G_FORMEL, farbe=HERVOR)
    (zeile[0] if euro else zeile)[1].set_color(TEXT)
    return zeile


def angabe(tex: str, farbe: str = TEXT) -> MathTex:
    return formel(tex, groesse=G_STRAHL, farbe=farbe)


def kapital(name: str, kante: object, wert: str | None, farbe: str) -> VGroup:
    """Angabe an einem Ende des Zeitstrahls: der Name der Größe, darunter ihr Wert in Euro oder ein Fragezeichen."""
    zeilen = [angabe(name, farbe)]
    if wert == "?":
        zeilen.append(angabe("?", farbe))
    elif wert is not None:
        zeilen.append(betrag(wert, groesse=G_STRAHL, farbe=farbe))
    return VGroup(*zeilen).arrange(DOWN, buff=0.18, aligned_edge=kante)


def anfang(wert: str | None = None, farbe: str = TEXT) -> VGroup:
    return kapital("K_0", LEFT, wert, farbe)


def ende(wert: str | None = None, farbe: str = TEXT) -> VGroup:
    return kapital("K_n", RIGHT, wert, farbe)


def zeitpunkt(inhalt: str, farbe: str = TEXT) -> Text:
    return text(inhalt, groesse=G_ZEIT, farbe=farbe)


def allgemein() -> dict[str, Mobject]:
    """Zeitstrahl ohne Zahlen: die vier Größen an ihrem Platz."""
    return {
        "frueher": zeitpunkt("früher", TEXT_LEISE),
        "dauer": reihe(angabe("n"), text("Jahre", groesse=G_ZEIT), abstand=0.14, grundlinie=True),
        "spaeter": zeitpunkt("später", TEXT_LEISE),
        "anfang": anfang(),
        "zins": angabe(r"p\,\%"),
        "ende": ende(),
    }


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.8)
        # Unter den Namen der Kapitalien erscheinen später ihre Werte, deshalb sitzt der Strahl über der Mitte.
        self.strahl = self.auf_buehne(Zeitstrahl(**allgemein())).shift(0.22 * UP)
        kopf = self.kopf(r"K_n=K_0\cdot q^{n}")
        self.add(karte)

        self.einstieg(
            "Wie löst du Sachaufgaben", "zum Zinseszins?",
            bild=self.strahl.aufbau(),
            kopf=kopf,
        )

        # ---------- Idee: vier Größen, drei gegeben ----------
        groessen = legende(
            (formel("K_0", groesse=G_FORMEL), text("Anfangskapital", groesse=G_TEXT)),
            (
                formel("K_n", groesse=G_FORMEL),
                reihe(
                    text("Kapital nach", groesse=G_TEXT), formel("n", groesse=44),
                    text("Jahren", groesse=G_TEXT), abstand=0.2, grundlinie=True,
                ),
            ),
            (formel("p", groesse=G_FORMEL), text("Zinssatz", groesse=G_TEXT)),
            (formel("n", groesse=G_FORMEL), text("Laufzeit in Jahren", groesse=G_TEXT)),
        )
        zinsfaktor = reihe(
            text("Zinsfaktor:", groesse=G_TEXT, farbe=TEXT_LEISE), formel(r"q=1+\frac{p}{100}", groesse=44), abstand=0.35,
        )
        merke = text("3 gegeben, 1 gesucht", groesse=44, gewicht=BOLD, farben={"1 gesucht": HERVOR})
        idee = self.tafel(groessen, zinsfaktor, merke, abstand=0.65)
        with self.sprich(
            "In jeder Aufgabe stecken 4 Größen: das Anfangskapital K null, das Kapital nach n Jahren, "
            "der Zinssatz und die Laufzeit. 3 stehen im Text, die vierte ist gesucht."
        ):
            for zeile, platz, beginn in zip(groessen, ("anfang", "ende", "zins", "dauer"), (0.2, 0.36, 0.53, 0.63)):
                self.warte_bis(beginn)
                self.play(
                    auftritt(zeile), self.strahl.betone(platz),
                    *([auftritt(zinsfaktor)] if platz == "zins" else []), run_time=0.5,
                )
            self.warte_bis(0.75)
            self.play(auftritt(merke), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(idee, shift=0.25 * UP), run_time=0.4)

        # ---------- K_n gesucht ----------
        ergebnis = naeherung("K_7", r"14\,264{,}23", euro=True)
        self.fall(
            wortlaut(
                "Der Verein legt 12 000 €", "zu 2,5 % an.", "Über welchen Betrag kann er", "nach 7 Jahren verfügen?",
                signal=("Über welchen Betrag", "verfügen?"),
            ),
            [zinseszins("K_7", r"12\,000", "1{,}025", "7", gesucht="K_n"), ergebnis],
            gegeben={"anfang": anfang(r"12\,000"), "zins": angabe(r"p=2{,}5\,\%"), "dauer": angabe("n=7")},
            gesucht=("ende", ende("?", HERVOR)),
            ergebnis=(ergebnis, ende(r"\approx 14\,264{,}23", HERVOR)),
            gegeben_ab=0.5, betont_ab=0.6, betont=("anfang",), gesucht_ab=0.7, rechnung_ab=(0.9, 0.97),
            sprechtext="Ein Verein legt 12.000 Euro zu 2,5 % an. "
                       "Über welchen Betrag kann er nach 7 Jahren verfügen? "
                       "Angelegt wird am Anfang, das ist K null. Gesucht ist der Betrag am Ende, also K n. "
                       "Einsetzen und ausrechnen.",
        )

        # ---------- K_0 gesucht ----------
        bruch = hervor(formel("K_0", "=", r"\frac{10\,000}{1{,}03^{6}}", groesse=G_FORMEL), 0)
        ergebnis = naeherung("K_0", r"8\,374{,}84", euro=True)
        self.fall(
            wortlaut(
                "Der Verein möchte in 6 Jahren", "über 10 000 € verfügen.", "Welchen Betrag muss er heute",
                "zu 3 % anlegen?",
                signal=("Welchen Betrag", "heute", "anlegen?"),
            ),
            [zinseszins(r"10\,000", "K_0", "1{,}03", "6", gesucht="K_0"), bruch, ergebnis],
            gegeben={
                "frueher": zeitpunkt("heute"),
                "spaeter": zeitpunkt("in 6 Jahren"),
                "ende": ende(r"10\,000"),
                "zins": angabe(r"p=3\,\%"),
                "dauer": angabe("n=6"),
            },
            gesucht=("anfang", anfang("?", HERVOR)),
            ergebnis=(ergebnis, anfang(r"\approx 8\,374{,}84", HERVOR)),
            gegeben_ab=0.52, betont_ab=0.66, betont=("spaeter", "ende"), gesucht_ab=0.78,
            rechnung_ab=(0.83, 0.9, 0.97),
            sprechtext="In 6 Jahren will der Verein über 10.000 Euro verfügen. "
                       "Welchen Betrag muss er heute zu 3 % anlegen? "
                       "Die 10.000 Euro sind der spätere Betrag, also K n. "
                       "Gesucht ist K null: durch q hoch 6 teilen.",
        )

        # ---------- n gesucht ----------
        logarithmus = hervor(
            formel("n", "=", r"\frac{\ln 1{,}3333}{\ln 1{,}03}", r"\approx", "9{,}73", groesse=G_FORMEL), 0, 4,
        )
        self.fall(
            wortlaut(
                "Der Verein legt 3 000 €", "zu 3 % an.", "Nach wie vielen Jahren", "ist das Guthaben auf 4 000 €",
                "angewachsen?",
                signal=("Nach wie vielen Jahren",),
            ),
            [
                zinseszins(r"4\,000", r"3\,000", "1{,}03", "n", gesucht="n"),
                hervor(formel("1{,}03", "^{n}", r"\approx", "1{,}3333", groesse=G_FORMEL), 1),
                logarithmus,
            ],
            gegeben={"anfang": anfang(r"3\,000"), "zins": angabe(r"p=3\,\%"), "ende": ende(r"4\,000")},
            gesucht=("dauer", angabe(r"n=\,?", HERVOR)),
            ergebnis=(logarithmus[4], angabe(r"n\approx 9{,}73", HERVOR)),
            gegeben_ab=0.3, gesucht_ab=0.57, rechnung_ab=(0.66, 0.75, 0.87),
            sprechtext="3000 Euro zu 3 %: Nach wie vielen Jahren sind es 4000 Euro? "
                       "Gesucht ist n. Durch 3000 teilen, dann den Logarithmus anwenden.",
        )

        # ---------- p gesucht ----------
        wurzel = hervor(formel("q", "=", r"\sqrt[12]{1{,}45}", r"\approx", "1{,}0314", groesse=G_FORMEL), 0, 4)
        ergebnis = naeherung("p", r"3{,}14\,\%")
        self.fall(
            wortlaut(
                "Der Verein hat vor 12 Jahren", "8 000 € angelegt; heute", "beträgt das Guthaben 11 600 €.",
                "Mit welchem Zinssatz wurde", "das Kapital verzinst?",
                signal=("Mit welchem Zinssatz",),
            ),
            [zinseszins(r"11\,600", r"8\,000", "q", "12", gesucht="q"), wurzel, ergebnis],
            gegeben={
                "frueher": zeitpunkt("vor 12 Jahren"),
                "spaeter": zeitpunkt("heute"),
                "anfang": anfang(r"8\,000"),
                "ende": ende(r"11\,600"),
                "dauer": angabe("n=12"),
            },
            gesucht=("zins", angabe(r"p=\,?", HERVOR)),
            ergebnis=(ergebnis, angabe(r"p\approx 3{,}14\,\%", HERVOR)),
            gegeben_ab=0.45, betont_ab=0.56, betont=("spaeter", "ende"), gesucht_ab=0.7,
            rechnung_ab=(0.78, 0.85, 0.94),
            sprechtext="Vor 12 Jahren 8000 Euro angelegt, heute sind es 11.600. "
                       "Mit welchem Zinssatz? Heute ist diesmal das Ende, also K n. "
                       "Gesucht ist p: teilen, zwölfte Wurzel ziehen, dann p berechnen.",
        )

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Gegebene Werte notieren", groesse=G_TEXT),
            text("Gesuchte Größe erkennen", groesse=G_TEXT, farben={"Gesuchte Größe": HERVOR}),
            text("Einsetzen und auflösen", groesse=G_TEXT),
        )
        formel_gross = zinseszins("K_n", "K_0", "q", "n", groesse=72)
        self.tafel(schritte, formel_gross, abstand=0.8)
        with self.sprich(
            "Kurz gesagt: Gegebene Werte notieren, gesuchte Größe erkennen, in die Formel einsetzen und auflösen."
        ):
            for zeile, beginn in zip((*schritte, formel_gross), (0.14, 0.37, 0.58, 0.7)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def fall(
        self,
        aufgabe: VGroup,
        rechnung: list[Mobject],
        *,
        gegeben: dict[str, Mobject],
        gesucht: tuple[str, Mobject],
        ergebnis: tuple[Mobject, Mobject],
        sprechtext: str,
        gegeben_ab: float,
        gesucht_ab: float,
        rechnung_ab: tuple[float, ...],
        betont_ab: float | None = None,
        betont: tuple[str, ...] = (),
    ) -> None:
        """Eine Aufgabe: Wortlaut, Größen auf dem Zeitstrahl, Rechnung, Ergebnis auf dem Zeitstrahl.

        gegeben: Angaben für den Zeitstrahl, Platz → Angabe.
        gesucht: Platz der gesuchten Größe und ihre Angabe mit Fragezeichen.
        ergebnis: Ergebnis in der Rechnung und die Angabe, die das Fragezeichen ersetzt.
        betont: Plätze, deren Angaben kurz pulsieren, wenn der Sprechtext den früheren oder späteren Betrag nennt.
        Die Werte *_ab geben an, bei welchem Anteil des Sprechtexts der Teil erscheint.
        """
        block = self.tafel(aufgabe, VGroup(*rechnung).arrange(DOWN, buff=0.45), abstand=0.8)
        platz, offen = gesucht
        quelle, wert = ergebnis
        with self.sprich(sprechtext):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(gegeben_ab)
            self.play(self.strahl.zeige(**gegeben), run_time=0.7)
            if betont_ab is not None:
                self.warte_bis(betont_ab)
                self.play(self.strahl.betone(*betont), run_time=0.6)
            self.warte_bis(gesucht_ab)
            self.play(self.strahl.zeige(**{platz: offen}), welle(offen, HERVOR), run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.play(self.strahl.uebernimm(platz, wert, quelle), run_time=0.7)
        self.wait(0.8)
        self.play(FadeOut(block, shift=0.25 * UP), self.strahl.zeige(**allgemein()), run_time=0.5)
