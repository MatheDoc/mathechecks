"""Check 05 – Tilgungsplan vervollständigen.

Kernidee: Drei Beziehungen verbinden die Zellen einer Zeile (Zinsen = p % der Restschuld am Anfang,
Annuität = Zinsen + Tilgung, Ende = Anfang − Tilgung); jede Zelle folgt aus zwei anderen. Rückwärts in die Zeile
davor: Annuität addieren, durch q teilen.
Beispiel: Zeilen 4 und 5 aus dem Musterbeispiel. Abweichung: Der Teil „rückwärts“ ersetzt Teilaufgabe c) durch die
Lückenart des Trainings (p gegeben, in Zeile 5 nur Zinsen, Tilgung und Restschuld am Ende); gleiche Zahlen.
Übersicht vor Vollständigkeit: je Bild höchstens drei Zeilen; Zeile 5 vorwärts füllt sich ohne Rechnung
(Schema aus Check 01).
"""
from manim import DOWN, LEFT, UP, FadeIn, FadeOut, MathTex, VGroup, Write

from mcvideo import MCSzene, Tilgungsplan, aufzaehlung, auftritt, formel, geld, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist die Zelle, die gerade gesucht ist, und ihr Wert in der Rechnung. Lücken sind grau.
G_FORMEL = 52
G_TEXT = 38
G_STICH = 32

PLAN = {
    4: dict(rk_anfang=44682.76, zinsen=2010.72, tilgung=5572.01, annuitaet=7582.73, rk_ende=39110.75),
    5: dict(rk_anfang=39110.75, zinsen=1759.98, tilgung=5822.75, annuitaet=7582.73, rk_ende=33288.00),
}
SPALTEN = Tilgungsplan.SPALTEN


def luecke() -> str:
    return "?"


def rechnung(term: str, wert: float, ungefaehr: bool = False) -> MathTex:
    zeile = formel(term, r"\approx" if ungefaehr else "=", geld(wert), groesse=G_FORMEL)
    zeile[2].set_color(HERVOR)
    return zeile


def stich(inhalt: str) -> VGroup:
    return text(inhalt, groesse=G_STICH, farbe=TEXT_LEISE)



def gestapelt(*paare: tuple) -> VGroup:
    """Je Rechnung das Stichwort klein darüber; so bleibt die Rechnung groß."""
    return VGroup(*[VGroup(stichwort, zeile).arrange(DOWN, buff=0.15) for stichwort, zeile in paare]).arrange(
        DOWN, buff=0.5,
    )


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=2.5)
        plan = self.plan = self.auf_buehne(Tilgungsplan((4, 5)))
        bekannt = {4: ("rk_anfang", "zinsen", "annuitaet"), 5: ()}
        for jahr in (4, 5):
            for spalte in SPALTEN:
                if spalte in bekannt[jahr]:
                    plan.zeige(jahr, spalte, geld(PLAN[jahr][spalte]))
                else:
                    plan.zeige(jahr, spalte, luecke(), TEXT_LEISE)
        self.add(karte)

        self.einstieg("Wie vervollständigst du", "einen Tilgungsplan?", bild=plan.aufbau())

        # ---------- Drei Beziehungen ----------
        beziehungen = VGroup(
            text("Zinsen = p % der Restschuld", groesse=G_TEXT),
            text("Annuität = Zinsen + Tilgung", groesse=G_TEXT),
            text("Ende = Anfang − Tilgung", groesse=G_TEXT),
        ).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        block = self.tafel(beziehungen)
        with self.sprich(
            "Von diesem Tilgungsplan kennen wir nur einzelne Werte. 3 Beziehungen helfen: "
            "Zinsen sind p Prozent der Restschuld am Anfang. Annuität ist Zinsen plus Tilgung. "
            "Restschuld am Ende ist Anfang minus Tilgung."
        ):
            for zeile, zellen, beginn in zip(
                beziehungen,
                ([(4, "zinsen"), (4, "rk_anfang")], [(4, "annuitaet"), (4, "zinsen")], [(4, "rk_anfang")]),
                (0.35, 0.62, 0.8),
            ):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), plan.betone(*zellen), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Zinssatz ----------
        p = formel("p", "=", r"\frac{2\,010{,}72}{44\,682{,}76}\cdot 100", r"\approx", r"4{,}5\,\%", groesse=G_FORMEL)
        p[0].set_color(HERVOR)
        p[4].set_color(HERVOR)
        block = self.tafel(VGroup(stich("Zinsen : Restschuld"), p).arrange(DOWN, buff=0.35))
        kopf = self.kopf(r"p=4{,}5\,\%")
        with self.sprich(
            "Restschuld und Zinsen stehen in Zeile 4. Zinsen durch Restschuld ergibt den Zinssatz: "
            "4,5 %."
        ):
            self.play(plan.zeile(4), plan.betone((4, "rk_anfang"), (4, "zinsen")), auftritt(block[0]), run_time=0.7)
            self.warte_bis(0.4)
            self.play(Write(p), run_time=1.0)
        self.play(FadeIn(kopf, target_position=p[4]), run_time=0.7)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Zeile 4 ergänzen ----------
        t4 = rechnung(r"7\,582{,}73-2\,010{,}72", PLAN[4]["tilgung"])
        rk4 = rechnung(r"44\,682{,}76-5\,572{,}01", PLAN[4]["rk_ende"])
        paare = gestapelt((stich("Tilgung"), t4), (stich("Ende"), rk4))
        block = self.tafel(paare)
        with self.sprich(
            "Die Tilgung ist Annuität minus Zinsen. Die Restschuld am Ende ist Anfang minus Tilgung."
        ):
            self.play(plan.zeige(4, "tilgung", luecke(), HERVOR), auftritt(paare[0][0]), run_time=0.5)
            self.play(Write(t4), run_time=0.8)
            self.play(plan.zeige(4, "tilgung", geld(PLAN[4]["tilgung"]), HERVOR, quelle=t4[2]), run_time=0.6)
            self.warte_bis(0.5)
            self.play(
                plan.faerbe((4, "tilgung")), plan.zeige(4, "rk_ende", luecke(), HERVOR), auftritt(paare[1][0]),
                run_time=0.5,
            )
            self.play(Write(rk4), run_time=0.8)
            self.play(plan.zeige(4, "rk_ende", geld(PLAN[4]["rk_ende"]), HERVOR, quelle=rk4[2]), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), plan.faerbe((4, "rk_ende")), run_time=0.4)

        # ---------- Zeile 5 ----------
        hinweis = text("gleiches Schema wie beim Aufstellen", groesse=G_STICH, farbe=TEXT_LEISE)
        block = self.tafel(hinweis)
        with self.sprich("Zeile 5 beginnt mit dieser Restschuld und läuft nach demselben Schema."):
            self.play(plan.zeile(5), plan.uebertrag(4), run_time=0.8)
            self.play(auftritt(hinweis), run_time=0.4)
            self.warte_bis(0.5)
            for spalte in ("zinsen", "tilgung", "annuitaet", "rk_ende"):
                self.play(plan.zeige(5, spalte, geld(PLAN[5][spalte])), run_time=0.35)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), plan.zeile(None), run_time=0.4)

        # ---------- Rückwärts: Lücken wie im Training ----------
        bekannt = {4: (), 5: ("zinsen", "tilgung", "rk_ende")}
        neu = []
        for jahr in (4, 5):
            for spalte in SPALTEN:
                if spalte in bekannt[jahr]:
                    neu.append(plan.zeige(jahr, spalte, geld(PLAN[jahr][spalte])))
                else:
                    neu.append(plan.zeige(jahr, spalte, luecke(), TEXT_LEISE))
        titel = text("rückwärts", groesse=48)
        a = rechnung(r"1\,759{,}98+5\,822{,}75", PLAN[5]["annuitaet"])
        anfang = rechnung(r"33\,288{,}00+5\,822{,}75", PLAN[5]["rk_anfang"])
        paare = gestapelt((stich("Annuität"), a), (stich("Anfang"), anfang))
        block = self.tafel(titel, paare, abstand=0.7)
        with self.sprich(
            "Jetzt rückwärts. Von Zeile 5 kennen wir nur Zinsen, Tilgung und die Restschuld am Ende. "
            "Zinsen plus Tilgung ergibt die Annuität, sie ist in jeder Zeile gleich. "
            "Und der Anfang ist Ende plus Tilgung."
        ):
            self.play(*neu, auftritt(titel), run_time=0.8)
            self.play(plan.zeile(5), run_time=0.4)
            self.warte_bis(0.38)
            self.play(plan.zeige(5, "annuitaet", luecke(), HERVOR), auftritt(paare[0][0]), Write(a), run_time=0.9)
            wert_a = geld(PLAN[5]["annuitaet"])
            self.play(
                plan.zeige(5, "annuitaet", wert_a, HERVOR, quelle=a[2]),
                plan.zeige(4, "annuitaet", wert_a, quelle=a[2]),
                run_time=0.7,
            )
            self.warte_bis(0.78)
            self.play(
                plan.faerbe((5, "annuitaet")), plan.zeige(5, "rk_anfang", luecke(), HERVOR),
                auftritt(paare[1][0]), Write(anfang), run_time=0.9,
            )
        wert = geld(PLAN[5]["rk_anfang"])
        self.play(
            plan.zeige(5, "rk_anfang", wert, HERVOR, quelle=anfang[2]),
            plan.zeige(4, "rk_ende", wert, quelle=anfang[2]),
            run_time=0.7,
        )
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), plan.faerbe((5, "rk_anfang")), run_time=0.4)

        # ---------- In die Zeile davor ----------
        vorwaerts = VGroup(
            stich("vorwärts"), formel(r"RK_4=RK_3\cdot q-A", groesse=44, farbe=TEXT_LEISE),
        ).arrange(DOWN, buff=0.2)
        regel = formel("RK_3", "=", r"\frac{RK_4+A}{q}", groesse=60)
        regel[0].set_color(HERVOR)
        zahlen = rechnung(r"\frac{39\,110{,}75+7\,582{,}73}{1{,}045}", PLAN[4]["rk_anfang"], ungefaehr=True)
        block = self.tafel(vorwaerts, regel, zahlen, abstand=0.55)
        with self.sprich(
            "Für den Anfang von Zeile 4: Vorwärts wächst die Restschuld ein Jahr mit Zinsen, "
            "dann wird die Annuität abgezogen. Rückwärts also: Annuität addieren und durch q teilen. "
            "Danach folgen Zinsen und Tilgung wie gewohnt."
        ):
            self.play(plan.zeile(4), plan.zeige(4, "rk_anfang", luecke(), HERVOR), auftritt(vorwaerts), run_time=0.7)
            self.warte_bis(0.45)
            self.play(Write(regel), welle(regel[2], HERVOR), run_time=0.9)
            self.play(Write(zahlen), run_time=0.9)
            self.play(plan.zeige(4, "rk_anfang", geld(PLAN[4]["rk_anfang"]), HERVOR, quelle=zahlen[2]), run_time=0.6)
            self.warte_bis(0.85)
            self.play(
                plan.faerbe((4, "rk_anfang")),
                plan.zeige(4, "zinsen", geld(PLAN[4]["zinsen"])),
                plan.zeige(4, "tilgung", geld(PLAN[4]["tilgung"])),
                run_time=0.6,
            )
        self.wait(0.5)
        self.play(FadeOut(block, shift=0.25 * UP), plan.zeile(None), run_time=0.4)

        # ---------- Kurzfassung ----------
        punkte = aufzaehlung(
            text("Zinsen = p % der Restschuld", groesse=G_TEXT),
            text("Annuität = Zinsen + Tilgung", groesse=G_TEXT),
            text("Ende = Anfang − Tilgung", groesse=G_TEXT),
            VGroup(
                text("rückwärts in die Zeile davor:", groesse=G_TEXT),
                text("+ Annuität, dann : q", groesse=G_TEXT),
            ).arrange(DOWN, buff=0.15, aligned_edge=LEFT),
            abstand=0.5,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: 3 Beziehungen füllen jede Zeile. "
            "In die Zeile davor kommst du rückwärts: Annuität addieren und durch q teilen."
        ):
            for zeile, beginn in zip(punkte, (0.08, 0.2, 0.32, 0.5)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
