"""Check 03 – Rente im Sachkontext.

Kernidee: Drei Fragen an den Text – wann wird gezahlt (vor- oder nachschüssig), wann wird bewertet
(Endwert oder Barwert), was ist gesucht – führen zur passenden der vier Formeln.
Beispiel: Physiotherapiepraxis wie im Musterbeispiel a) und b). Fall c (Laufzeit) aus dem Skript
(Jonas: 1 200 € nachschüssig, 2,5 %, 10 000 €) auf die Praxis übertragen.
"""
from collections.abc import Callable

from manim import DOWN, LEFT, RIGHT, UP, Animation, FadeOut, Mobject, VGroup, Write

from mcvideo import (
    MCSzene, Rentenstrahl, auftritt, betrag, formel, kurzfassung, reihe, text, welle, wortlaut,
)
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist die gesuchte Größe (im Wortlaut, auf dem Strahl, in der Rechnung); im Wortlaut auch die
# Signalwörter für Zahlungsweise und Bewertungszeitpunkt.
G_FORMEL = 48
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
        self.add(karte)

        self.einstieg(
            "Wie löst du Sachaufgaben", "zur Rentenrechnung?",
            bild=self.strahl.aufbau(),
        )

        # ---------- Drei Fragen ----------
        def frage_zeile(frage: str, *antworten: VGroup) -> VGroup:
            kopf = text(frage, groesse=40)
            return VGroup(kopf, *antworten).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        def antwort(wort: str, *tex: str) -> VGroup:
            return reihe(text(wort, groesse=G_TEXT, farbe=TEXT_LEISE),
                         *[formel(t, groesse=44) for t in tex], abstand=0.2, grundlinie=True)

        zahlung = frage_zeile(
            "Wann wird gezahlt?",
            antwort("Jahresanfang: vorschüssig"), antwort("Jahresende: nachschüssig"),
        )
        bewertung = frage_zeile(
            "Wann wird bewertet?",
            antwort("am Ende: Endwert", r"R_n,\ \overline{R}_n"), antwort("heute: Barwert", r"R_0,\ \overline{R}_0"),
        )
        gesucht = frage_zeile("Was ist gesucht?", reihe(
            text("Wert, Rate", groesse=G_TEXT, farbe=TEXT_LEISE), formel("r", groesse=44),
            text("oder Laufzeit", groesse=G_TEXT, farbe=TEXT_LEISE), formel("n", groesse=44),
            abstand=0.2, grundlinie=True,
        ))
        fragen = kurzfassung(zahlung, bewertung, gesucht)
        block = self.tafel(fragen)
        with self.sprich(
            "Drei Fragen an den Text. Wann wird gezahlt? Jahresanfang heißt vorschüssig, "
            "Jahresende nachschüssig. Wann wird bewertet? Am Ende: Endwert, heute: Barwert. "
            "Und: Was ist gesucht?"
        ):
            self.play(auftritt(fragen[0][0]), auftritt(zahlung[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(auftritt(zahlung[1]), self.strahl.zahlweise(True), run_time=0.8)
            self.warte_bis(0.27)
            self.play(auftritt(zahlung[2]), self.strahl.zahlweise(False), run_time=0.8)
            self.warte_bis(0.42)
            self.play(auftritt(fragen[1][0]), auftritt(bewertung[0]), run_time=0.5)
            self.warte_bis(0.55)
            self.play(auftritt(bewertung[1]), self.strahl.zeige(endwert=wert("R_n", None, RIGHT)), run_time=0.6)
            self.warte_bis(0.7)
            self.play(auftritt(bewertung[2]), self.strahl.zeige(barwert=wert("R_0", None, LEFT)), run_time=0.6)
            self.warte_bis(0.88)
            self.play(auftritt(fragen[2][0]), auftritt(gesucht), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), self.strahl.zeige(barwert=None, endwert=None), run_time=0.4)

        # ---------- a) vorschüssig, Endwert ----------
        ergebnis_a = ergebnis(r"\overline{R}_{15}", r"34\,482{,}39", euro=True)
        self.fall(
            wortlaut(
                "Eine Praxis zahlt 15 Jahre lang", "zu Jahresbeginn 1 800 € auf ein", "Konto mit 3 % ein. Über welchen",
                "Betrag verfügt sie am Ende?",
                signal=("zu Jahresbeginn", "Über welchen", "Betrag", "am Ende?"), groesse=G_WORT,
            ),
            [
                formel(r"\overline{R}_{15}", "=", r"\frac{1\,800\cdot 1{,}03\cdot(1{,}03^{15}-1)}{0{,}03}",
                       groesse=G_FORMEL).set_color_by_tex(r"\overline{R}_{15}", HERVOR),
                ergebnis_a,
            ],
            gegeben=lambda: [self.strahl.raten_zu(r"1\,800", vorschuessig=True)],
            gesucht=lambda: [self.strahl.zeige(endwert=wert(r"\overline{R}_{15}", "?", RIGHT, HERVOR))],
            gegeben_ab=0.55, gesucht_ab=0.68, rechnung_ab=(0.85, 0.95),
            uebernahme=("endwert", wert(r"\overline{R}_{15}", r"\approx 34\,482{,}39", RIGHT, HERVOR), ergebnis_a),
            sprechtext="Eine Praxis zahlt fünfzehn Jahre lang zu Jahresbeginn achtzehnhundert Euro ein, "
                       "zu drei Prozent. Über welchen Betrag verfügt sie am Ende? "
                       "Jahresbeginn heißt vorschüssig. Gesucht ist der Wert am Ende, "
                       "also der vorschüssige Endwert. Einsetzen und ausrechnen.",
        )

        # ---------- b) nachschüssig, Barwert, r gesucht ----------
        self.fall(
            wortlaut(
                "Die Praxis legt heute 40 000 € zu", "2,5 % an und entnimmt 10 Jahre", "lang am Jahresende einen gleich",
                "hohen Betrag. Wie hoch ist er?",
                signal=("heute", "am Jahresende", "gleich", "hohen Betrag.", "Wie hoch ist er?"), groesse=G_WORT,
            ),
            [
                hervor(formel(r"40\,000", "=", "r", r"\cdot\frac{1{,}025^{10}-1}{1{,}025^{10}\cdot 0{,}025}",
                              groesse=G_FORMEL), 2),
                hervor(formel(r"40\,000", "=", "r", r"\cdot 8{,}7521", groesse=G_FORMEL), 2),
                ergebnis("r", r"4\,570{,}35", euro=True),
            ],
            gegeben=lambda: [self.strahl.zahlweise(False), self.strahl.zeige(barwert=wert("R_0", r"40\,000", LEFT))],
            gesucht=lambda: [self.strahl.rate("r", HERVOR)],
            gegeben_ab=0.45, gesucht_ab=0.75, rechnung_ab=(0.82, 0.9, 0.96),
            sprechtext="Die Praxis legt heute vierzigtausend Euro an und entnimmt zehn Jahre lang am Jahresende "
                       "einen gleich hohen Betrag. Am Jahresende heißt nachschüssig. "
                       "Die vierzigtausend Euro liegen heute bereit: Das ist der Barwert. Gesucht ist die Rate r.",
        )

        # ---------- c) nachschüssig, Endwert, n gesucht ----------
        jahr_n = self.strahl.jahre[-1]
        self.fall(
            wortlaut(
                "Die Praxis zahlt am Jahresende", "1 200 € ein (2,5 %). Nach wie", "vielen Jahren sind 10 000 €",
                "erreicht?",
                signal=("am Jahresende", "Nach wie", "vielen Jahren"), groesse=G_WORT,
            ),
            [
                hervor(formel(r"10\,000", "=", r"\frac{1\,200\cdot(1{,}025", "^{n}", r"-1)}{0{,}025}",
                              groesse=G_FORMEL), 3),
                hervor(formel("1{,}025", "^{n}", r"\approx", "1{,}2083", groesse=G_FORMEL), 1),
                hervor(formel("n", r"\approx", "7{,}66", groesse=G_FORMEL), 0, 2),
            ],
            gegeben=lambda: [self.strahl.rate(r"1\,200"), self.strahl.zeige(endwert=wert("R_n", r"10\,000", RIGHT))],
            gesucht=lambda: [jahr_n.animate.set_color(HERVOR), welle(jahr_n, HERVOR)],
            gegeben_ab=0.3, gesucht_ab=0.5, rechnung_ab=(0.56, 0.7, 0.82),
            nachher=lambda: [jahr_n.animate.set_color(TEXT_LEISE)],
            sprechtext="Am Jahresende zwölfhundert Euro: Nach wie vielen Jahren sind zehntausend Euro erreicht? "
                       "Nachschüssig, Endwert, gesucht ist n. Nach q hoch n auflösen, logarithmieren: "
                       "Im achten Jahr ist es geschafft.",
        )

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Vor- oder nachschüssig?", groesse=46),
            text("Endwert oder Barwert?", groesse=46),
            text("Gesuchte Größe erkennen", groesse=46, farben={"Gesuchte Größe": HERVOR}),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Zahlungsweise klären, Endwert oder Barwert wählen, "
            "die gesuchte Größe erkennen und auflösen."
        ):
            for zeile, beginn in zip(schritte, (0.1, 0.35, 0.6)):
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
        """Eine Aufgabe: Wortlaut, Zahlungsweise und Größen auf dem Strahl, Rechnung, Ergebnis auf dem Strahl."""
        block = self.tafel(aufgabe, *rechnung, abstand=0.4)
        aufgabe.shift(0.3 * UP)  # etwas Abstand zwischen Wortlaut und Rechnung
        with self.sprich(sprechtext):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(gegeben_ab)
            self.play(*gegeben(), run_time=0.8)
            self.warte_bis(gesucht_ab)
            self.play(*gesucht(), run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        if uebernahme is not None:
            platz, angabe, quelle = uebernahme
            self.play(self.strahl.uebernimm(platz, angabe, quelle), run_time=0.7)
        self.wait(0.8)
        self.play(
            FadeOut(block, shift=0.25 * UP), self.strahl.zeige(barwert=None, endwert=None), self.strahl.rate("r"),
            *(nachher() if nachher else []), run_time=0.5,
        )
