"""Check 03 – Restschuldformel und letzte Annuität.

Kernidee: Restschuld = aufgezinste Darlehenssumme minus Endwert der gezahlten Annuitäten. RK_k ist zugleich
die Restschuld zu Beginn des Jahres k+1 (daraus Zinsen und Tilgung). Im letzten Jahr wird RK_{n-1} getilgt,
die letzte Annuität ist RK_{n-1} · q; ihre Abweichung von A ist die Rundungsdifferenz.
Beispiel: Kfz-Werkstatt wie im Musterbeispiel (200 000 €, 3,5 %, 25 Jahre, A = 12 134,81 €), ohne Abweichung.
"""
from manim import DOWN, UP, Brace, FadeIn, FadeOut, MathTex, VGroup, Write

from mcvideo import MCSzene, Tilgungsplan, aufzaehlung, auftritt, betrag, formel, geld, reihe, text, welle, wortlaut
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist der Wert, der gerade gesucht ist: im Plan und in der Rechnung.
G_FORMEL = 48
G_TEXT = 34
A = 12134.81
RK10 = 139761.53
Z11, T11 = 4891.65, 7243.16
RK24 = 11724.34
A25 = 12134.70


def wert(name: str, rel: str, zahl: float, farbe: str = HERVOR) -> VGroup:
    """Ergebniszeile „Name ≈ Wert €“; Name und Wert in der Farbe der gesuchten Größe."""
    zeile = betrag(name, rel, geld(zahl), groesse=G_FORMEL)
    zeile[0][0].set_color(farbe)
    zeile[0][2].set_color(farbe)
    zeile[1].set_color(farbe)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.6)
        plan = self.auf_buehne(Tilgungsplan((1, None, 10, 11, None, 25)))
        plan.zeige(1, "rk_anfang", geld(200000))
        for jahr in (1, 10, 11):
            plan.zeige(jahr, "annuitaet", geld(A))
        kopf = self.kopf(r"p=3{,}5\,\%", r"\qquad n=25")
        self.add(karte)

        self.einstieg(
            "Wie bestimmst du die", "Restschuld nach k Jahren?",
            zusatz="(und die letzte Annuität)",
            bild=plan.aufbau(),
            kopf=kopf,
        )

        # ---------- Aufgabe ----------
        aufgabe = wortlaut(
            "Eine Kfz-Werkstatt tilgt 200 000 €", "zu 3,5 % in 25 Jahren mit einer", "Annuität von 12 134,81 €.",
            "Wie hoch ist die Restschuld", "nach 10 Jahren?",
            signal=("Restschuld", "nach 10 Jahren?"),
        )
        block = self.tafel(aufgabe)
        with self.sprich(
            "Eine Kfz-Werkstatt tilgt 200.000 Euro zu 3,5 % in 25 Jahren, "
            "mit gleicher Annuität. Wie hoch ist die Restschuld nach 10 Jahren?"
        ):
            self.play(auftritt(aufgabe), run_time=0.6)
            self.warte_bis(0.15)
            self.play(plan.betone((1, "rk_anfang")), run_time=0.6)
            self.warte_bis(0.45)
            self.play(plan.betone((1, "annuitaet"), (10, "annuitaet"), (11, "annuitaet")), run_time=0.6)
            self.warte_bis(0.75)
            self.play(plan.zeile(10), plan.zeige(10, "rk_ende", "?", HERVOR), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Restschuldformel ----------
        rsf = formel("RK_k", "=", r"K_0\cdot q^k", "-", r"\frac{A\cdot(q^k-1)}{q-1}", groesse=56)
        klammer1 = Brace(rsf[2], DOWN, color=TEXT_LEISE)
        klammer2 = Brace(rsf[4], DOWN, color=TEXT_LEISE)
        name1 = text("Darlehen\naufgezinst", groesse=26, farbe=TEXT_LEISE).next_to(klammer1, DOWN, buff=0.1)
        name2 = text("Annuitäten\nmit Zinsen", groesse=26, farbe=TEXT_LEISE).next_to(klammer2, DOWN, buff=0.1)
        formelblock = self.oben_auf_tafel(VGroup(rsf, klammer1, klammer2, name1, name2))
        with self.sprich(
            "Statt 10 Zeilen zu rechnen, nutzen wir die Restschuldformel: "
            "die Darlehenssumme 10 Jahre aufgezinst, minus die 10 Annuitäten samt Zinsen."
        ):
            self.play(Write(rsf), run_time=1.0)
            self.warte_bis(0.45)
            self.play(FadeIn(klammer1), auftritt(name1), run_time=0.5)
            self.warte_bis(0.72)
            self.play(FadeIn(klammer2), auftritt(name2), run_time=0.5)
        self.wait(0.3)

        # ---------- Einsetzen ----------
        einsetzen = formel(
            r"200\,000\cdot 1{,}035^{10}", "-", r"\frac{12\,134{,}81\cdot(1{,}035^{10}-1)}{0{,}035}", groesse=G_FORMEL,
        )
        zeilen = [
            einsetzen,
            formel(r"\approx 282\,119{,}75-142\,358{,}23", groesse=G_FORMEL),
            wert(r"RK_{10}", r"\approx", RK10),
        ]
        rechnung = self.tafel(*zeilen, abstand=0.4, unter=formelblock)
        with self.sprich(
            "Eingesetzt bleiben nach 10 Jahren etwa 139.761 Euro."
        ):
            for zeile, beginn in zip(zeilen, (0.0, 0.3, 0.6)):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.9)
            self.play(plan.zeige(10, "rk_ende", geld(RK10), HERVOR, quelle=zeilen[2][0][2]), run_time=0.7)
        self.wait(0.3)
        self.play(FadeOut(rechnung, shift=0.25 * UP), FadeOut(formelblock, shift=0.25 * UP), run_time=0.4)

        # ---------- Folgejahr ----------
        uebergang = text("Ende von Jahr 10 = Anfang von Jahr 11", groesse=G_TEXT, farbe=TEXT_LEISE)
        z = betrag("Z_{11}", "=", r"139\,761{,}53\cdot 0{,}035", r"\approx", geld(Z11), groesse=G_FORMEL)
        t = betrag("T_{11}", "=", r"12\,134{,}81-4\,891{,}65", "=", geld(T11), groesse=G_FORMEL)
        for zeile in (z, t):
            for teil in (zeile[0][0], zeile[0][4], zeile[1]):
                teil.set_color(HERVOR)
        block = self.tafel(uebergang, z, t, abstand=0.55)
        with self.sprich(
            "Das ist zugleich die Restschuld zu Beginn des elften Jahres. "
            "Daraus folgen wie im Tilgungsplan die Zinsen und die Tilgung des elften Jahres."
        ):
            self.play(auftritt(uebergang), plan.zeile(11), plan.faerbe((10, "rk_ende")), run_time=0.5)
            self.play(plan.uebertrag(10), run_time=0.8)
            self.warte_bis(0.5)
            self.play(Write(z), run_time=0.8)
            self.play(plan.zeige(11, "zinsen", geld(Z11), HERVOR, quelle=z[0][4]), run_time=0.6)
            self.warte_bis(0.8)
            self.play(Write(t), plan.faerbe((11, "zinsen")), run_time=0.8)
            self.play(plan.zeige(11, "tilgung", geld(T11), HERVOR, quelle=t[0][4]), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), plan.faerbe((11, "tilgung")), run_time=0.4)

        # ---------- Letzte Zeile ----------
        tilgung = reihe(
            text("letzte Tilgung", groesse=G_TEXT),
            betrag(r"=RK_{24}\approx", geld(RK24), groesse=G_FORMEL),
            abstand=0.25, grundlinie=True,
        )
        herkunft = text("Restschuldformel mit k = 24", groesse=28, farbe=TEXT_LEISE)
        titel = text("letzte Annuität", groesse=G_TEXT)
        letzte = betrag(r"11\,724{,}34\cdot 1{,}035", r"\approx", geld(A25), groesse=G_FORMEL)
        letzte[0][2].set_color(HERVOR)
        letzte[1].set_color(HERVOR)
        block = self.tafel(
            VGroup(tilgung, herkunft).arrange(DOWN, buff=0.15),
            VGroup(titel, letzte).arrange(DOWN, buff=0.25),
            abstand=0.7,
        )
        with self.sprich(
            "Und die letzte Zeile? Im letzten Jahr wird genau die Restschuld nach 24 Jahren getilgt, "
            "etwa 11.724 Euro. "
            "Die letzte Annuität ist diese Tilgung plus ein Jahr Zinsen."
        ):
            self.play(plan.zeile(25), plan.zeige(25, "annuitaet", "?", HERVOR), run_time=0.5)
            self.warte_bis(0.2)
            self.play(Write(tilgung), FadeIn(herkunft), run_time=0.9)
            self.warte_bis(0.5)
            quelle = tilgung[1][0]
            self.play(
                plan.zeige(25, "rk_anfang", geld(RK24), quelle=quelle),
                plan.zeige(25, "tilgung", geld(RK24), quelle=quelle),
                plan.fuelle((25, "rk_ende", geld(0))),
                run_time=0.7,
            )
            self.warte_bis(0.68)
            self.play(auftritt(titel), run_time=0.4)
            self.play(Write(letzte), run_time=0.8)
        self.play(plan.zeige(25, "annuitaet", geld(A25), HERVOR, quelle=letzte[0][2]), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Rundungsdifferenz ----------
        differenz = betrag(r"12\,134{,}81-12\,134{,}70", "=", r"0{,}11", groesse=G_FORMEL)
        name = text("Rundungsdifferenz", groesse=44, farbe=HERVOR)
        grund = text("A ist auf Cent gerundet", groesse=G_TEXT, farbe=TEXT_LEISE)
        block = self.tafel(differenz, name, grund, abstand=0.5)
        with self.sprich(
            "Das sind 11 Cent weniger als A. "
            "Diese Rundungsdifferenz entsteht, weil A auf Cent gerundet ist."
        ):
            self.play(plan.betone((11, "annuitaet"), (25, "annuitaet")), Write(differenz), run_time=0.9)
            self.warte_bis(0.45)
            self.play(auftritt(name), run_time=0.5)
            self.warte_bis(0.7)
            self.play(auftritt(grund), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), plan.zeile(None), run_time=0.4)

        # ---------- Kurzfassung ----------
        def stichwort(inhalt: str) -> VGroup:
            return text(inhalt, groesse=30, farbe=TEXT_LEISE)

        punkte = aufzaehlung(
            (stichwort("Restschuld"), text("Restschuldformel", groesse=38)),
            (stichwort("Jahr k+1"), text("Zinsen, Tilgung", groesse=38)),
            (stichwort("letzte Annuität"), formel(r"RK_{n-1}\cdot q", groesse=50)),
            (stichwort("Rundung"), text("Abweichung von A", groesse=38)),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Die Restschuld liefert die Restschuldformel, daraus folgen Zinsen und Tilgung "
            "des nächsten Jahres. Die letzte Annuität ist die letzte Restschuld mal q."
        ):
            for zeile, beginn in zip(punkte, (0.08, 0.3, 0.6, 0.85)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
