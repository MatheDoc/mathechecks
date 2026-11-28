"""Check 01 – Tilgungsplan aufstellen.

Kernidee: Jede Zeile in drei Schritten: Zinsen aus der Restschuld am Jahresanfang, Tilgung = Annuität − Zinsen,
Restschuld am Jahresende = Anfang − Tilgung. Das Ende einer Zeile ist der Anfang der nächsten.
Beispiel: Fotostudio wie im Musterbeispiel (18 000 €, 3,5 %, A = 3 378,03 €), ohne Abweichung.
Die Annuitätenformel bleibt weg: Im Training ist A gegeben (Herleitung in Check 02).
"""
from manim import DOWN, LEFT, RIGHT, UP, FadeOut, MathTex, VGroup, Write

from mcvideo import MCSzene, Tilgungsplan, auftritt, formel, geld, kurzfassung, reihe, schritt, text, welle, wortlaut
from mcvideo.theme import HERVOR, TEXT_LEISE

# Orange ist die Zelle, die gerade berechnet wird, in der Rechnung wie im Plan.
# Die Rechenzeilen tragen keine Symbolnamen: Schritt und Spaltenkopf benennen die Größe.
G_FORMEL = 58
G_TEXT = 38
ERGEBNIS = 2  # Teil der Rechenzeile mit dem Ergebnis


def rechnung(term: str, wert: float, ungefaehr: bool = False) -> MathTex:
    """Zeile „Term = Wert“; der Wert ist orange."""
    zeile = formel(term, r"\approx" if ungefaehr else "=", geld(wert), groesse=G_FORMEL)
    zeile[ERGEBNIS].set_color(HERVOR)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.5)
        plan = self.plan = self.auf_buehne(Tilgungsplan((1, 2)))
        kopf = self.kopf(r"p=3{,}5\,\%")
        self.add(karte)

        self.einstieg("Wie stellst du einen", "Tilgungsplan auf?", bild=plan.aufbau(), kopf=kopf)

        # ---------- Aufgabe ----------
        aufgabe = wortlaut(
            "Ein Fotostudio nimmt ein Darlehen", "über 18 000 € zu 3,5 % auf.", "Die Annuität beträgt 3 378,03 €.",
        )
        idee = text("Annuität = Zinsen + Tilgung", groesse=40)
        block = self.tafel(aufgabe, idee, abstand=0.8)
        with self.sprich(
            "Ein Fotostudio nimmt ein Darlehen über 18.000 Euro zu 3,5 % auf. "
            "Es zahlt jedes Jahr dieselbe Annuität: 3378 Euro und 3 Cent. "
            "Darin stecken Zinsen und Tilgung."
        ):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(0.22)
            self.play(plan.zeige(1, "rk_anfang", geld(18000)), run_time=0.6)
            self.warte_bis(0.5)
            self.play(plan.fuelle((1, "annuitaet", geld(3378.03)), (2, "annuitaet", geld(3378.03))), run_time=0.6)
            self.warte_bis(0.82)
            self.play(auftritt(idee), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Zeile 1 in drei Schritten ----------
        z1 = rechnung(r"18\,000\cdot 0{,}035", 630)
        t1 = rechnung(r"3\,378{,}03-630{,}00", 2748.03)
        rk1 = rechnung(r"18\,000-2\,748{,}03", 15251.97)
        titel = [schritt(1, "Zinsen"), schritt(2, "Tilgung"), schritt(3, "Restschuld")]
        paare = VGroup(*[
            VGroup(kopfzeile, zeile).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
            for kopfzeile, zeile in zip(titel, (z1, t1, rk1))
        ]).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        block = self.tafel(paare)

        self.play(plan.zeile(1), run_time=0.4)
        self.schritt_zeigen(
            paare[0], (1, "zinsen"), None,
            "Erster Schritt: die Zinsen. Sie betragen 3,5 % der Restschuld am Jahresanfang, "
            "also 630 Euro.",
            betont=[(1, "rk_anfang")],
        )
        self.schritt_zeigen(
            paare[1], (1, "tilgung"), (1, "zinsen"),
            "Zweiter Schritt: Der Rest der Annuität ist die Tilgung. "
            "Annuität minus Zinsen ergibt 2748 Euro und 3 Cent.",
            betont=[(1, "annuitaet"), (1, "zinsen")],
        )
        self.schritt_zeigen(
            paare[2], (1, "rk_ende"), (1, "tilgung"),
            "Dritter Schritt: Die Tilgung verringert die Schuld. "
            "Am Jahresende bleiben 15.251 Euro und 97 Cent.",
            betont=[(1, "rk_anfang"), (1, "tilgung")],
        )
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), plan.faerbe((1, "rk_ende")), run_time=0.4)

        # ---------- Zeile 2 ----------
        uebergang = text("Ende von Jahr 1 = Anfang von Jahr 2", groesse=34, farbe=TEXT_LEISE)
        z2 = rechnung(r"15\,251{,}97\cdot 0{,}035", 533.82, ungefaehr=True)
        t2 = rechnung(r"3\,378{,}03-533{,}82", 2844.21)
        rk2 = rechnung(r"15\,251{,}97-2\,844{,}21", 12407.76)
        runden = text("jede Zelle auf Cent runden", groesse=30, farbe=TEXT_LEISE)
        zeilen = VGroup(z2, t2, rk2).arrange(DOWN, buff=0.4, aligned_edge=RIGHT)
        block = self.tafel(uebergang, zeilen, runden, abstand=0.6)
        with self.sprich(
            "Diese Restschuld ist die Restschuld am Anfang des zweiten Jahres. "
            "Dann dasselbe Schema: Zinsen, Tilgung, Restschuld. "
            "Jede Zelle runden wir auf Cent und rechnen mit dem gerundeten Wert weiter."
        ):
            self.play(plan.zeile(2), auftritt(uebergang), run_time=0.5)
            self.play(plan.uebertrag(1), run_time=0.8)
            self.play(welle(plan.zelle(2, "rk_anfang"), HERVOR), run_time=0.5)
            vorher = None
            for zeile, spalte, beginn in zip((z2, t2, rk2), ("zinsen", "tilgung", "rk_ende"), (0.38, 0.47, 0.56)):
                self.warte_bis(beginn)
                self.play(Write(zeile), *([plan.faerbe(vorher)] if vorher else []), run_time=0.6)
                ergebnis = zeile[ERGEBNIS]
                self.play(plan.zeige(2, spalte, ergebnis.get_tex_string(), HERVOR, quelle=ergebnis), run_time=0.5)
                vorher = (2, spalte)
            self.warte_bis(0.75)
            self.play(auftritt(runden), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), plan.zeile(None), plan.faerbe((2, "rk_ende")), run_time=0.4)

        # ---------- Beobachtung ----------
        sinken = reihe(text("Zinsen sinken", groesse=44), formel(r"\searrow", groesse=60), abstand=0.3)
        steigen = reihe(text("Tilgung steigt", groesse=44), formel(r"\nearrow", groesse=60), abstand=0.3)
        block = self.tafel(VGroup(sinken, steigen).arrange(DOWN, buff=0.6, aligned_edge=LEFT))
        with self.sprich("Die Zinsen sinken mit der Restschuld. Bei gleicher Annuität steigt deshalb die Tilgung."):
            self.play(auftritt(sinken), plan.betone((1, "zinsen"), (2, "zinsen")), run_time=0.8)
            self.warte_bis(0.5)
            self.play(auftritt(steigen), plan.betone((1, "tilgung"), (2, "tilgung")), run_time=0.8)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Zinsen: p % der Restschuld", groesse=G_TEXT),
            text("Tilgung = Annuität − Zinsen", groesse=G_TEXT),
            VGroup(
                text("Restschuld − Tilgung", groesse=G_TEXT),
                text("= Anfang der nächsten Zeile", groesse=32, farbe=TEXT_LEISE),
            ).arrange(DOWN, buff=0.15, aligned_edge=LEFT),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Zinsen aus der Restschuld am Jahresanfang. Tilgung ist Annuität minus Zinsen. "
            "Restschuld am Ende ist Anfang minus Tilgung, und sie wird zum Anfang der nächsten Zeile."
        ):
            for zeile, beginn in zip(schritte, (0.1, 0.4, 0.62)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)

    def schritt_zeigen(
        self,
        paar: VGroup,
        ziel: tuple[int, str],
        vorher: tuple[int, str] | None,
        sprechtext: str,
        betont: list[tuple[int, str]],
    ) -> None:
        """Ein Schritt: Überschrift, die Zellen, aus denen gerechnet wird, pulsieren, Rechnung, Wert in den Plan."""
        plan = self.plan
        titel, zeile = paar
        with self.sprich(sprechtext):
            self.play(auftritt(titel), *([plan.faerbe(vorher)] if vorher else []), run_time=0.5)
            self.warte_bis(0.4)
            self.play(plan.betone(*betont), run_time=0.6)
            self.play(Write(zeile), run_time=0.8)
            self.warte_bis(0.85)
            ergebnis = zeile[ERGEBNIS]
            self.play(plan.zeige(*ziel, ergebnis.get_tex_string(), HERVOR, quelle=ergebnis), run_time=0.6)
