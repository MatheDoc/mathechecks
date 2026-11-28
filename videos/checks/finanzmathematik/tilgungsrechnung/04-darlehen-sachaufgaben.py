"""Check 04 – Darlehen im Sachkontext.

Kernidee: Vier Größen (K_0, p, n, A); drei stehen im Text, der Fragesatz verrät die gesuchte und damit die Formel.
Beispiel: Cateringbetrieb wie im Musterbeispiel, Teilaufgaben a) bis c) mit denselben Zahlen.
K_0 und RK_k (im Training ebenfalls gefragt) erscheinen nur mit ihrem Signalwort; vorgerechnet sind sie in den
Videos zu Check 02 und 03.
"""
from manim import DOWN, LEFT, RIGHT, UP, AnimationGroup, FadeIn, FadeOut, Mobject, VGroup, Write

from mcvideo import MCSzene, aufzaehlung, auftritt, betrag, formel, legende, reihe, text, welle, wortlaut
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist allein die gesuchte Größe: im Fragesatz, auf der Bühne und in der Rechnung.
G_FORMEL = 48
G_TEXT = 34
G_BUEHNE = 44
NAMEN = ("K_0", "p", "n", "A")


class Groessen(VGroup):
    """Die vier Größen eines Annuitätendarlehens nebeneinander, darunter ihr Wert oder ein Fragezeichen."""

    def __init__(self, breite: float = 5.4) -> None:
        super().__init__()
        self.xs = [breite * (i / 3 - 0.5) for i in range(4)]
        self.namen = {
            name: formel(name, groesse=G_BUEHNE * 1.15).move_to([x, 0.45, 0]) for name, x in zip(NAMEN, self.xs)
        }
        self.werte: dict[str, Mobject] = {}
        self.add(*self.namen.values())

    def aufbau(self) -> list:
        return [FadeIn(name, shift=0.15 * DOWN) for name in self.namen.values()]

    def zeige(self, gesucht: str | None = None, **werte: Mobject) -> AnimationGroup:
        """Setzt Werte (TeX-Objekte) unter die Namen; gesucht färbt Name und Fragezeichen orange."""
        schritte = []
        for name, wert in werte.items():
            alt = self.werte.pop(name, None)
            if alt is not None:
                self.remove(alt)
                schritte.append(FadeOut(alt))
            wert.move_to([self.namen[name].get_x(), self.namen[name].get_y() - 0.85, 0])
            self.werte[name] = wert
            self.add(wert)
            schritte.append(FadeIn(wert, shift=0.15 * DOWN))
        for name in NAMEN:
            ziel = HERVOR if name == gesucht else TEXT
            if self.namen[name].get_color().to_hex().lower() != ziel.lower():
                schritte.append(self.namen[name].animate.set_color(ziel))
        return AnimationGroup(*schritte)

    def leer(self) -> AnimationGroup:
        schritte = [FadeOut(w) for w in self.werte.values()]
        for w in self.werte.values():
            self.remove(w)
        self.werte = {}
        schritte += [n.animate.set_color(TEXT) for n in self.namen.values()]
        return AnimationGroup(*schritte)


def euro(wert: str) -> VGroup:
    return betrag(wert, groesse=G_BUEHNE)


def zahl(wert: str, farbe: str = TEXT) -> Mobject:
    return formel(wert, groesse=G_BUEHNE, farbe=farbe)


def frage_zeichen() -> Mobject:
    return zahl("?", HERVOR)


def hervor(zeile, *teile: int):
    for teil in teile:
        zeile[teil].set_color(HERVOR)
    return zeile


def euro_hervor(zeile: VGroup, *teile: int) -> VGroup:
    """Färbt Teile eines Geldbetrags; das Eurozeichen bekommt die Farbe des Werts."""
    hervor(zeile[0], *teile)
    zeile[1].set_color(HERVOR)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.6)
        self.groessen = self.auf_buehne(Groessen())
        self.add(karte)

        self.einstieg(
            "Wie erkennst du, was bei", "einem Darlehen gesucht ist?",
            bild=self.groessen.aufbau(),
        )

        # ---------- Vier Größen ----------
        namen = legende(
            (formel("K_0", groesse=G_FORMEL), text("Darlehenssumme", groesse=G_TEXT)),
            (formel("p", groesse=G_FORMEL), text("Zinssatz", groesse=G_TEXT)),
            (formel("n", groesse=G_FORMEL), text("Laufzeit", groesse=G_TEXT)),
            (formel("A", groesse=G_FORMEL), text("Annuität (jährliche Rate)", groesse=G_TEXT)),
        )
        merke = text("3 im Text, 1 im Fragesatz", groesse=42, farben={"1 im Fragesatz": HERVOR})
        block = self.tafel(namen, merke, abstand=0.7)
        with self.sprich(
            "Es geht um 4 Größen: Darlehenssumme, Zinssatz, Laufzeit und Annuität. "
            "3 stehen im Text, die vierte verrät der Fragesatz."
        ):
            for zeile, name, beginn in zip(namen, NAMEN, (0.15, 0.3, 0.4, 0.5)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), welle(self.groessen.namen[name], HERVOR), run_time=0.5)
            self.warte_bis(0.72)
            self.play(auftritt(merke), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Jahresrate ----------
        self.fall(
            wortlaut(
                "Ein Cateringbetrieb nimmt 80 000 €", "zu 4 % auf, getilgt in 10 Jahren durch",
                "gleich hohe Jahresraten.", "Wie hoch ist die jährliche Rate?",
                signal=("gleich hohe Jahresraten", "jährliche Rate"),
            ),
            werte=dict(K_0=euro(r"80\,000"), p=zahl(r"4\,\%"), n=zahl("10")),
            gesucht="A",
            rechnung=[
                hervor(formel("A", "=", r"\frac{80\,000\cdot 1{,}04^{10}\cdot 0{,}04}{1{,}04^{10}-1}",
                              groesse=G_FORMEL), 0),
                euro_hervor(betrag("A", r"\approx", r"9\,863{,}28", groesse=G_FORMEL), 0, 2),
            ],
            ergebnis=euro(r"9\,863{,}28").set_color(HERVOR),
            werte_ab=0.25, gesucht_ab=0.55, rechnung_ab=(0.7, 0.88),
            sprechtext="Ein Cateringbetrieb nimmt 80.000 Euro zu 4 % auf, getilgt in 10 Jahren "
                       "durch gleich hohe Jahresraten. Wie hoch ist die jährliche Rate? "
                       "Gleich hohe Jahresraten: Das ist die Annuität. "
                       "Annuitätenformel: etwa 9863 Euro.",
        )

        # ---------- Dauer ----------
        self.fall(
            wortlaut(
                "Ein Darlehen über 120 000 € zu 3 %", "wird mit 10 000 € jährlich getilgt.",
                "Nach wie vielen Jahren ist", "das Darlehen getilgt?",
                signal=("Nach wie vielen Jahren",),
            ),
            werte=dict(K_0=euro(r"120\,000"), p=zahl(r"3\,\%"), A=euro(r"10\,000")),
            gesucht="n",
            rechnung=[
                betrag("T_1", "=", r"10\,000-3\,600", "=", r"6\,400", groesse=G_FORMEL),
                hervor(formel(r"10\,000", "=", r"6\,400\cdot 1{,}03", "^{n}", groesse=G_FORMEL), 3),
                hervor(formel("n", "=", r"\frac{\ln 1{,}5625}{\ln 1{,}03}", r"\approx", "15{,}10",
                              groesse=G_FORMEL), 0, 4),
            ],
            ergebnis=zahl(r"\approx 15{,}1", HERVOR),
            werte_ab=0.2, gesucht_ab=0.45, rechnung_ab=(0.62, 0.78, 0.88),
            sprechtext="Ein Darlehen über 120.000 Euro zu 3 % wird mit 10.000 Euro "
                       "jährlich getilgt. Nach wie vielen Jahren? Gesucht ist die Laufzeit. "
                       "Erst T eins, dann A gleich T eins mal q hoch n: etwa 15,1 Jahre.",
        )

        # ---------- Gesamtzinsen ----------
        self.fall(
            wortlaut(
                "Wie viel Zinsen zahlt der Betrieb", "für das erste Darlehen", "über die gesamte Laufzeit?",
                signal=("Zinsen", "gesamte Laufzeit"),
            ),
            werte=dict(K_0=euro(r"80\,000"), p=zahl(r"4\,\%"), n=zahl("10"), A=euro(r"9\,863{,}28")),
            gesucht=None,
            rechnung=[
                formel(r"n\cdot A-K_0", groesse=G_FORMEL * 1.15),
                formel(r"=10\cdot 9\,863{,}28-80\,000", groesse=G_FORMEL),
                euro_hervor(betrag("=", r"18\,632{,}80", groesse=G_FORMEL), 1),
            ],
            ergebnis=None,
            werte_ab=0.05, gesucht_ab=None, rechnung_ab=(0.55, 0.7, 0.85),
            sprechtext="Und die Zinsen insgesamt? Alle Annuitäten zusammen enthalten die Darlehenssumme "
                       "und sämtliche Zinsen. Also 10 mal A minus K null: "
                       "18.632 Euro 80.",
        )

        # ---------- Weitere Signalwörter ----------
        def signal(*wort: str, ziel: str) -> VGroup:
            return VGroup(
                wortlaut(*wort, groesse=40),
                reihe(formel(r"\downarrow", groesse=48, farbe=TEXT_LEISE), formel(ziel, groesse=64, farbe=HERVOR),
                      abstand=0.25),
            ).arrange(DOWN, buff=0.25)

        k0 = signal("Welche Darlehenssumme", "ist möglich?", ziel="K_0")
        rk = signal("Restschuld nach k Jahren?", ziel="RK_k")
        block = self.tafel(k0, rk, abstand=0.8)
        with self.sprich(
            "Fragt der Text, welche Darlehenssumme möglich ist, ist K null gesucht. "
            "Und die Schulden nach k Jahren liefert die Restschuldformel."
        ):
            self.play(self.groessen.zeige(gesucht="K_0"), auftritt(k0), run_time=0.6)
            self.warte_bis(0.55)
            self.play(self.groessen.zeige(gesucht=None), auftritt(rk), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        def paar(wort: str, ziel: str) -> tuple:
            return text(wort, groesse=40), formel(ziel, groesse=54, farbe=HERVOR)

        punkte = aufzaehlung(
            paar("jährliche Rate", "A"),
            paar("welcher Kredit möglich?", "K_0"),
            paar("wie lange?", "n"),
            paar("Schulden nach k Jahren", "RK_k"),
            paar("Zinsen insgesamt", r"n\cdot A-K_0"),
            abstand=0.5,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Gegebene Werte notieren, im Fragesatz die gesuchte Größe erkennen, "
            "dann die passende Formel wählen und auflösen."
        ):
            for zeile, beginn in zip(punkte, (0.05, 0.2, 0.35, 0.5, 0.65)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.45)

    def fall(
        self,
        aufgabe: VGroup,
        *,
        werte: dict[str, Mobject],
        gesucht: str | None,
        rechnung: list[Mobject],
        ergebnis: Mobject | None,
        werte_ab: float,
        gesucht_ab: float | None,
        rechnung_ab: tuple[float, ...],
        sprechtext: str,
    ) -> None:
        """Eine Aufgabe: Wortlaut, Werte auf der Bühne, gesuchte Größe, Rechnung, Ergebnis auf die Bühne."""
        block = self.tafel(aufgabe, VGroup(*rechnung).arrange(DOWN, buff=0.4), abstand=0.7)
        with self.sprich(sprechtext):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(werte_ab)
            self.play(self.groessen.zeige(**werte), run_time=0.7)
            if gesucht is not None:
                self.warte_bis(gesucht_ab)
                self.play(self.groessen.zeige(gesucht=gesucht, **{gesucht: frage_zeichen()}), run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        if ergebnis is not None:
            self.play(self.groessen.zeige(gesucht=gesucht, **{gesucht: ergebnis}), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), self.groessen.leer(), run_time=0.5)
