"""Check 06 – Kapitalvergleich mit Renten.

Kernidee: Alle Zahlungen werden auf heute bezogen: Einmalzahlungen mit q^n abgezinst, Renten über den
Rentenbarwert bewertet. Wann die Rente beginnt, entscheidet über die Formel (sofort → vorschüssig,
in einem Jahr → nachschüssig, später → zusätzlich abzinsen).
Beispiel: Landwirtin wie im Musterbeispiel, ohne Abweichung.
"""
from manim import BOLD, DOWN, LEFT, UP, Create, FadeOut, VGroup, Write

from mcvideo import MCSzene, Zahlungsplan, auftritt, aufzaehlung, betrag, formel, kurzfassung, reihe, text
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist, was gerade abgezinst wird: Zahlung, Bogen zurück auf heute, Barwert. Am Ende das gewählte Angebot.
G_FORMEL = 48
G_TEXT = 36
G_PLAN = 38


def spalte(tex: str) -> VGroup:
    """Barwert in der rechten Spalte des Zahlungsplans."""
    return betrag(tex, groesse=G_PLAN)


def wert(tex: str) -> VGroup:
    """„≈ Betrag €“ in Orange, das Ungefähr-Zeichen weiß; steht unter dem Gleichheitszeichen der Zeile darüber."""
    zeile = betrag(r"\approx", tex, groesse=G_FORMEL, farbe=HERVOR)
    zeile[0][0].set_color(TEXT)
    return zeile


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.0)
        self.plan = Zahlungsplan(
            {
                "A": [(r"30\,000", 0)],
                "B": [(r"12\,000", 0), (r"22\,000", 5)],
                "C": [],
            },
            jahre=8,
            jahr_breite=0.6,
            zeilen_abstand=1.3,
            barwert_breite=3.3,
            groesse=G_PLAN,
            renten={"C": (r"4\,500", 1, 8)},
        )
        self.auf_buehne(self.plan)
        self.add(karte)

        self.einstieg(
            "Wie vergleichst du", "Angebote mit Renten?",
            bild=self.plan.aufbau(),
        )

        # ---------- Angebote ----------
        lage = VGroup(
            text("Eine Landwirtin verkauft", groesse=40, gewicht=BOLD),
            text("eine Erntemaschine.", groesse=40, gewicht=BOLD),
            reihe(text("Zinssatz:", groesse=G_TEXT, farbe=TEXT_LEISE), formel(r"p=3\,\%", groesse=G_FORMEL),
                  abstand=0.3, grundlinie=True),
        ).arrange(DOWN, buff=0.3)
        lage[2].shift(0.3 * DOWN)
        block = self.tafel(lage)
        with self.sprich(
            "Eine Landwirtin verkauft eine Erntemaschine. A: 30.000 Euro sofort. "
            "B: 12.000 sofort und 22.000 in 5 Jahren. "
            "C: 8 Jahreszahlungen von je 4500 Euro, die erste in einem Jahr. "
            "Gerechnet wird mit 3 %."
        ):
            self.play(auftritt(lage[:2]), run_time=0.6)
            for name, beginn in (("A", 0.15), ("B", 0.3), ("C", 0.57)):
                self.warte_bis(beginn)
                self.play(self.plan.betone(name), run_time=0.6)
            self.warte_bis(0.88)
            self.play(auftritt(lage[2]), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Idee ----------
        idee = text("Alles auf heute beziehen", groesse=40, gewicht=BOLD)
        regeln = aufzaehlung(
            (text("Einmalzahlung:", groesse=G_TEXT), formel(r"K_0=\frac{K_n}{q^{n}}", groesse=52)),
            (text("Rente:", groesse=G_TEXT), text("Rentenbarwert", groesse=G_TEXT)),
            abstand=0.5,
        )
        block = self.tafel(idee, regeln, abstand=0.7)
        boegen = VGroup(self.plan.bogen("B", 1), self.plan.bogen("C", 0))
        with self.sprich(
            "Verglichen wird heute: Einmalzahlungen zinsen wir ab, Renten bewerten wir mit dem Rentenbarwert."
        ):
            self.play(auftritt(idee), run_time=0.5)
            self.play(*[Create(b) for b in boegen], self.plan.faerbe("B", 1), self.plan.faerbe("C", 0), run_time=1.0)
            self.warte_bis(0.35)
            self.play(auftritt(regeln[0]), run_time=0.5)
            self.warte_bis(0.62)
            self.play(auftritt(regeln[1]), run_time=0.5)
        self.wait(0.4)
        self.play(
            FadeOut(block, shift=0.25 * UP), FadeOut(boegen),
            self.plan.faerbe("B", 1, TEXT), self.plan.faerbe("C", 0, TEXT), run_time=0.4,
        )

        # ---------- A und B ----------
        b_a = betrag("B_A", "=", r"30\,000", groesse=G_FORMEL)
        b_b = formel("B_B", "=", r"12\,000+", r"\frac{22\,000}{1{,}03^{5}}", groesse=G_FORMEL)
        b_b[3].set_color(HERVOR)
        b_b_wert = wert(r"30\,977{,}39")
        block = self.tafel(b_a, b_b, b_b_wert, abstand=0.5)
        b_b_wert.align_to(b_b[1], LEFT)
        bogen = self.plan.bogen("B", 1)
        with self.sprich(
            "A kommt sofort. Bei B zinsen wir die spätere Zahlung ab und addieren."
        ):
            self.play(Write(b_a), run_time=0.7)
            self.play(self.plan.barwert("A", spalte(r"30\,000"), b_a[0][2]), run_time=0.6)
            self.warte_bis(0.35)
            self.play(Create(bogen), self.plan.faerbe("B", 1), run_time=0.7)
            self.play(Write(b_b), run_time=0.8)
            self.warte_bis(0.9)
            self.play(Write(b_b_wert), run_time=0.6)
        self.play(self.plan.barwert("B", spalte(r"\approx 30\,977{,}39"), b_b_wert[0][1]), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(bogen), self.plan.faerbe("B", 1, TEXT), run_time=0.4)

        # ---------- C: Rente ----------
        beginn = VGroup(
            text("erste Zahlung in einem Jahr", groesse=40),
            text("→ nachschüssige Rente", groesse=40, farbe=TEXT_LEISE),
        ).arrange(DOWN, buff=0.2)
        b_c = formel("B_C", "=", "R_0", "=", r"\frac{4\,500\cdot(1{,}03^{8}-1)}{1{,}03^{8}\cdot 0{,}03}",
                     groesse=G_FORMEL)
        b_c[4].set_color(HERVOR)
        b_c_wert = wert(r"31\,588{,}61")
        block = self.tafel(beginn, b_c, b_c_wert, abstand=0.5)
        b_c_wert.align_to(b_c[3], LEFT)
        bogen = self.plan.bogen("C", 0)
        with self.sprich(
            "Bei C kommt die erste Zahlung in einem Jahr: eine nachschüssige Rente. "
            "Ihr Wert heute ist der Rentenbarwert R null."
        ):
            self.play(auftritt(beginn), run_time=0.6)
            self.warte_bis(0.5)
            self.play(Create(bogen), self.plan.faerbe("C", 0), run_time=0.7)
            self.play(Write(b_c), run_time=0.8)
            self.warte_bis(0.9)
            self.play(Write(b_c_wert), run_time=0.6)
        self.play(self.plan.barwert("C", spalte(r"\approx 31\,588{,}61"), b_c_wert[0][1]), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(bogen), self.plan.faerbe("C", 0, TEXT), run_time=0.4)

        # ---------- Beginn der Rente ----------
        titel = text("Wann kommt die erste Zahlung?", groesse=40, gewicht=BOLD)
        faelle = aufzaehlung(
            (text("sofort:", groesse=G_TEXT), formel(r"\overline{R}_0", groesse=52)),
            (text("in einem Jahr:", groesse=G_TEXT), formel("R_0", groesse=52)),
            (text("in k + 1 Jahren:", groesse=G_TEXT), formel(r"\frac{R_0}{q^{k}}", groesse=52)),
            abstand=0.45,
        )
        block = self.tafel(titel, faelle, abstand=0.7)
        with self.sprich(
            "Achte auf den Beginn: Erste Zahlung sofort heißt vorschüssig, in einem Jahr nachschüssig. "
            "Beginnt die Rente später, zinsen wir den Rentenbarwert zusätzlich ab."
        ):
            self.play(auftritt(titel), run_time=0.5)
            for zeile, ab in zip(faelle, (0.2, 0.45, 0.62)):
                self.warte_bis(ab)
                self.play(auftritt(zeile), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Entscheidung ----------
        bekommt = text("Die Landwirtin bekommt das Geld:", groesse=G_TEXT, farbe=TEXT_LEISE)
        wahl = text("höchster Barwert → Angebot C", groesse=44, gewicht=BOLD, farben={"Angebot C": HERVOR})
        kaeufer = text("Wer zahlt, wählt den niedrigsten.", groesse=G_TEXT, farbe=TEXT_LEISE)
        block = self.tafel(VGroup(bekommt, wahl).arrange(DOWN, buff=0.3), kaeufer, abstand=0.8)
        with self.sprich(
            "Die Landwirtin bekommt das Geld, sie wählt also den höchsten Barwert: Angebot C. "
            "Wer kauft und zahlt, wählt den niedrigsten."
        ):
            self.play(auftritt(bekommt), run_time=0.5)
            self.warte_bis(0.35)
            self.play(
                auftritt(wahl), self.plan.barwerte["C"].animate.set_color(HERVOR),
                self.plan.namen["C"].animate.set_color(HERVOR), run_time=0.6,
            )
            self.play(self.plan.betone("C"), run_time=0.6)
            self.warte_bis(0.7)
            self.play(auftritt(kaeufer), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            text("Alles auf heute beziehen", groesse=40),
            text("Einmalzahlungen abzinsen", groesse=40),
            text("Renten: Rentenbarwert", groesse=40),
            text("Barwerte addieren, vergleichen", groesse=40),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Alles auf heute beziehen. Einmalzahlungen abzinsen, "
            "Renten mit dem Rentenbarwert bewerten. Dann pro Angebot addieren und vergleichen."
        ):
            for zeile, ab in zip(schritte, (0.05, 0.3, 0.5, 0.75)):
                self.warte_bis(ab)
                self.play(auftritt(zeile), run_time=0.5)
