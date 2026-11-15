"""Check 05 – Intervall-Wkt berechnen.

Kernidee: Der Text beschreibt einen Bereich von Anzahlen. Der Taschenrechner braucht davon die
kleinste und die größte, dazu n und p: Bcd(a;b;n;p).
Beispiel: Basketball mit n = 20 und p = 0,1 wie im Musterbeispiel, aber nur fünf der dreizehn
Ereignisse (je eines pro Schwierigkeit) und nur der Weg über Bcd, ohne kumulierte Wahrscheinlichkeiten.
"""
from manim import BOLD, DOWN, UP, FadeIn, FadeOut, Indicate, Line, MathTex, Mobject, VGroup, Write

from mcvideo import MCSzene, Versuche, Zahlenstrahl, auftritt, formel, kurzfassung, legende, reihe, text
from mcvideo.theme import HERVOR, ROSE, TEXT_LEISE, TUERKIS

# Die flache Bühne lässt der Tafel viel Platz, deshalb größere Schrift als üblich.
G_FORMEL = 60
G_ZEICHEN = 50
G_TEXT = 38


def ereignis(*zeilen: str, farben: dict[str, str]) -> VGroup:
    """Wortlaut des Ereignisses in Anführungszeichen, eine Bildzeile je Argument."""
    zeilen = (f"„{zeilen[0]}", *zeilen[1:])
    zeilen = (*zeilen[:-1], f"{zeilen[-1]}“")
    return VGroup(*[text(zeile, groesse=44, gewicht=BOLD, farben=farben) for zeile in zeilen]).arrange(DOWN, buff=0.2)


def eingabe(vorzeichen: str, a: str, b: str, p: str = "0{,}1") -> MathTex:
    """Taschenrechner-Eingabe mit farbigen Grenzen."""
    zeile = formel(vorzeichen + "Bcd(", a, ";", b, ";20;", p, ")", groesse=G_FORMEL)
    zeile[1].set_color(HERVOR)
    zeile[3].set_color(HERVOR)
    return zeile


def naeherung(wert: str) -> MathTex:
    return formel(r"\approx " + wert, groesse=G_FORMEL)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.5)
        self.strahl = self.auf_buehne(Zahlenstrahl(20))
        kopf = self.kopf(r"n=20\qquad p=0{,}1")
        self.add(karte)

        self.einstieg(
            "Wie berechnest du", "Intervallwahrscheinlichkeiten?",
            bild=self.strahl.aufbau(),
            kopf=kopf,
        )

        # ---------- Sachzusammenhang ----------
        lage = self.tafel(
            text("Basketball: 20 Würfe", groesse=46, gewicht=BOLD),
            text("Jeder Wurf trifft mit 10 %.", groesse=G_TEXT),
            reihe(formel("X", groesse=G_ZEICHEN), text("zählt die Treffer.", groesse=G_TEXT)),
            abstand=0.5,
        )
        with self.sprich(
            "Eine Basketballspielerin wirft zwanzigmal und trifft jeweils mit zehn Prozent. X zählt die Treffer."
        ):
            self.play(auftritt(lage[0]), run_time=0.5)
            self.warte_bis(0.35)
            self.play(auftritt(lage[1]), run_time=0.5)
            self.warte_bis(0.7)
            self.play(auftritt(lage[2]), run_time=0.5)
        self.play(FadeOut(lage, shift=0.25 * UP), run_time=0.4)

        # ---------- Idee: vier Angaben ----------
        schablone = formel("Bcd(", "a", ";", "b", ";n;p)", groesse=72)
        schablone[1].set_color(HERVOR)
        schablone[3].set_color(HERVOR)
        angaben = legende(
            (formel("a", groesse=G_ZEICHEN, farbe=HERVOR), text("kleinste Anzahl", groesse=G_TEXT)),
            (formel("b", groesse=G_ZEICHEN, farbe=HERVOR), text("größte Anzahl", groesse=G_TEXT)),
            (formel("n", groesse=G_ZEICHEN), text("Anzahl der Versuche", groesse=G_TEXT)),
            (formel("p", groesse=G_ZEICHEN), text("Trefferwahrscheinlichkeit", groesse=G_TEXT)),
        )
        idee = self.tafel(text("Vier Angaben:", groesse=G_TEXT, farbe=TEXT_LEISE), schablone, angaben, abstand=0.6)
        with self.sprich(
            "Dein Taschenrechner braucht vier Angaben: die kleinste und die größte Anzahl, dazu n und p."
        ):
            self.play(auftritt(idee[0]), Write(schablone), run_time=1.2)
            self.warte_bis(0.42)
            self.play(auftritt(angaben[0]), run_time=0.4)
            self.warte_bis(0.6)
            self.play(auftritt(angaben[1]), run_time=0.4)
            self.warte_bis(0.8)
            self.play(
                auftritt(angaben[2]), auftritt(angaben[3]),
                Indicate(kopf, color=kopf.get_color(), scale_factor=1.15), run_time=0.7,
            )
        self.wait(0.5)
        self.play(FadeOut(idee, shift=0.25 * UP), run_time=0.4)

        # ---------- Bereiche ----------
        self.fall(
            ereignis("höchstens 4 Treffer", farben={"höchstens 4": HERVOR}),
            [formel(r"P(X\leq 4)", groesse=G_FORMEL), eingabe("=", "0", "4"), naeherung("0{,}9568")],
            bereiche=[(0, 4)], bereich_ab=0.25, eingabe_ab=0.5,
            sprechtext="Höchstens vier Treffer: Das sind null bis vier. Also null und vier eintippen, dann n und p.",
        )
        self.fall(
            ereignis("weniger als 4 oder", "mehr als 7 Treffer", farben={"weniger als 4": HERVOR, "mehr als 7": HERVOR}),
            [
                reihe(
                    formel("P(X<4", groesse=G_FORMEL), text("oder", groesse=G_TEXT), formel("X>7)", groesse=G_FORMEL),
                ),
                eingabe("=", "0", "3"),
                eingabe("+", "8", "20"),
                naeherung("0{,}8675"),
            ],
            bereiche=[(0, 3), (8, 20)], bereich_ab=0.4, eingabe_ab=0.6,
            sprechtext="Weniger als vier oder mehr als sieben Treffer: Vier und sieben zählen nicht mit. "
                       "Zwei Bereiche, also beide berechnen und addieren.",
        )

        grenze = self.strahl.ort(2.6)
        marke = VGroup(
            Line(grenze + 0.12 * UP, grenze + 0.72 * DOWN, color=HERVOR, stroke_width=4),
            formel("2{,}6", groesse=36, farbe=HERVOR).next_to(grenze, UP, buff=0.2),
        )
        umrechnung = formel(r"0{,}13\cdot 20=", "2{,}6", groesse=G_FORMEL)
        umrechnung[1].set_color(HERVOR)
        self.fall(
            ereignis("in höchstens 13 % der Würfe", farben={"höchstens 13 %": HERVOR}),
            [formel(r"P(X\leq 2{,}6)", groesse=G_FORMEL), eingabe("=", "0", "2"), naeherung("0{,}6769")],
            bereiche=[(0, 2)], zwischen=umrechnung, zusatz=marke, zwischen_ab=0.3, bereich_ab=0.65, eingabe_ab=0.85,
            sprechtext="In höchstens dreizehn Prozent der Würfe: Das sind zwei Komma sechs Würfe. "
                       "Mehr ist nicht erlaubt, also null bis zwei.",
        )

        fehlwurf = eingabe("=", "0", "15", p="0{,}9")
        fehlwurf[5].set_color(ROSE)
        gezaehlt = reihe(
            formel("Y", groesse=G_ZEICHEN),
            text("zählt die Fehlwürfe:", groesse=G_TEXT, farben={"Fehlwürfe": ROSE}),
            formel("p=", "0{,}9", groesse=G_ZEICHEN),
        )
        gezaehlt[2][1].set_color(ROSE)
        self.fall(
            ereignis("höchstens 15 Fehlwürfe", farben={"höchstens 15": HERVOR, "Fehlwürfe": ROSE}),
            [formel(r"P(Y\leq 15)", groesse=G_FORMEL), fehlwurf, naeherung("0{,}0432")],
            bereiche=[(0, 15)], zwischen=gezaehlt, zwischen_ab=0.45, bereich_ab=0.75, eingabe_ab=0.9,
            sprechtext="Höchstens fünfzehn Fehlwürfe: Jetzt werden Fehlwürfe gezählt. "
                       "Deshalb ist p gleich null Komma neun.",
        )

        # ---------- Nicht binomialverteilt: bestimmte Würfe ----------
        wuerfe = self.auf_buehne(Versuche(20, titel="Wurf"))
        produkt = formel("P=", "0{,}1", r"\cdot", "0{,}1", "=0{,}01", groesse=G_FORMEL)
        produkt[1].set_color(TUERKIS)
        produkt[3].set_color(TUERKIS)
        sonderfall = self.tafel(
            ereignis("im 3. und 14. Wurf ein Treffer", farben={"3. und 14. Wurf": TUERKIS}),
            text("keine Anzahl, sondern bestimmte Würfe", groesse=G_TEXT, farbe=TEXT_LEISE),
            text("nicht binomialverteilt", groesse=46, gewicht=BOLD),
            produkt,
            abstand=0.6,
        )
        self.play(FadeOut(self.strahl), FadeIn(wuerfe), run_time=0.5)
        with self.sprich(
            "Im dritten und vierzehnten Wurf ein Treffer: Hier wird nichts gezählt, es geht um bestimmte Würfe. "
            "Also keine Binomialverteilung, du multiplizierst einfach."
        ):
            self.play(auftritt(sonderfall[0]), wuerfe.markiere(3, 14), run_time=0.9)
            self.warte_bis(0.35)
            self.play(auftritt(sonderfall[1]), run_time=0.4)
            self.warte_bis(0.65)
            self.play(auftritt(sonderfall[2]), run_time=0.4)
            self.warte_bis(0.82)
            self.play(Write(produkt), run_time=0.9)
        self.wait(0.8)

        # ---------- Kurzfassung ----------
        self.strahl = self.auf_buehne(Zahlenstrahl(20))
        self.play(FadeOut(sonderfall, shift=0.25 * UP), FadeOut(wuerfe), FadeIn(self.strahl), run_time=0.5)
        fragen = kurzfassung(
            text("Geht es um eine Anzahl?", groesse=42),
            text("Was wird gezählt?", groesse=42),
            text("Von wo bis wo?", groesse=42),
        )
        self.tafel(fragen, schablone, abstand=0.8)
        with self.sprich("Kurz gesagt: Geht es um eine Anzahl? Was wird gezählt? Von wo bis wo? Dann eintippen."):
            for zeile, beginn in zip((*fragen, schablone), (0.15, 0.4, 0.6, 0.8)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def fall(
        self,
        wortlaut: Mobject,
        zeilen: list[Mobject],
        *,
        bereiche: list[tuple[int, int]],
        sprechtext: str,
        bereich_ab: float,
        eingabe_ab: float,
        zwischen: Mobject | None = None,
        zwischen_ab: float = 0.3,
        zusatz: Mobject | None = None,
    ) -> None:
        """Ein Ereignis: Wortlaut, ggf. Zwischenzeile, Bereich auf dem Zahlenstrahl, Rechnung.

        zeilen: gesuchte Wahrscheinlichkeit, eine oder mehrere Eingaben, Ergebnis.
        Die Werte *_ab geben an, bei welchem Anteil des Sprechtexts der Teil erscheint.
        zusatz erscheint mit der Zwischenzeile auf der Bühne und verschwindet am Ende.
        """
        block = self.tafel(wortlaut, *([zwischen] if zwischen is not None else []), *zeilen, abstand=0.6)
        with self.sprich(sprechtext):
            self.play(auftritt(wortlaut), run_time=0.5)
            if zwischen is not None:
                self.warte_bis(zwischen_ab)
                self.play(auftritt(zwischen), *([FadeIn(zusatz)] if zusatz is not None else []), run_time=0.5)
            self.warte_bis(bereich_ab)
            self.play(self.strahl.bereich(*bereiche), run_time=0.9)
            self.warte_bis(eingabe_ab)
            self.play(auftritt(zeilen[0]), run_time=0.5)
            for zeile in zeilen[1:-1]:
                self.play(Write(zeile), run_time=0.8)
            self.play(auftritt(zeilen[-1]), run_time=0.4)
        self.wait(0.8)
        self.play(
            FadeOut(block, shift=0.25 * UP), *([FadeOut(zusatz)] if zusatz is not None else []), run_time=0.4,
        )
