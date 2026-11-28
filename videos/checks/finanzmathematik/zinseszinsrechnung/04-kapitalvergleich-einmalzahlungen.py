"""Check 04 – Kapitalvergleich mit Einmalzahlungen.

Kernidee: Zahlungen sind nur zum gleichen Zeitpunkt vergleichbar. Jede Zahlung wird auf heute abgezinst
(Barwert), die Barwerte werden pro Angebot addiert. Der Verkäufer wählt den höchsten, der Käufer den niedrigsten.
Beispiel: Fahrschule wie im Musterbeispiel, ohne Abweichung.
"""
from manim import BOLD, DOWN, LEFT, UP, Create, FadeOut, VGroup, Write

from mcvideo import MCSzene, Zahlungsplan, auftritt, betrag, formel, kurzfassung, reihe, text
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

# Orange ist, was gerade abgezinst wird: Zahlung, Bogen zurück auf heute, Barwert. Am Ende das gewählte Angebot.
G_FORMEL = 50
G_TEXT = 36
G_PLAN = 30


def spalte(tex: str) -> VGroup:
    """Barwert in der rechten Spalte des Zahlungsplans."""
    return betrag(tex, groesse=G_PLAN)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=4.0)
        self.plan = Zahlungsplan(
            {
                "A": [(r"50\,000", 0)],
                "B": [(r"20\,000", 0), (r"35\,000", 4)],
                "C": [(r"60\,000", 3)],
            },
            jahre=4,
            groesse=G_PLAN,
        )
        self.auf_buehne(self.plan)
        self.add(karte)

        self.einstieg(
            "Wie vergleichst du Angebote", "mit späteren Zahlungen?",
            zusatz="(Zinseszinsrechnung)",
            bild=self.plan.aufbau(),
        )

        # ---------- Angebote ----------
        lage = VGroup(
            text("Eine Fahrschule verkauft", groesse=40, gewicht=BOLD),
            text("einen Kleinbus.", groesse=40, gewicht=BOLD),
            reihe(text("Zinssatz:", groesse=G_TEXT, farbe=TEXT_LEISE), formel(r"p=4\,\%", groesse=G_FORMEL),
                  abstand=0.3, grundlinie=True),
        ).arrange(DOWN, buff=0.3)
        lage[2].shift(0.3 * DOWN)
        block = self.tafel(lage)
        with self.sprich(
            "Eine Fahrschule verkauft einen Kleinbus. Angebot A: 50.000 Euro sofort. "
            "B: 20.000 sofort und 35.000 in 4 Jahren. "
            "C: 60.000 in 3 Jahren. Gerechnet wird mit 4 %."
        ):
            self.play(auftritt(lage[:2]), run_time=0.6)
            for name, beginn in (("A", 0.18), ("B", 0.36), ("C", 0.68)):
                self.warte_bis(beginn)
                self.play(self.plan.betone(name), run_time=0.6)
            self.warte_bis(0.85)
            self.play(auftritt(lage[2]), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Barwert ----------
        idee = text("Vergleichbar nur zum", groesse=40, gewicht=BOLD)
        idee2 = text("gleichen Zeitpunkt", groesse=40, gewicht=BOLD)
        barwert = reihe(
            text("Barwert:", groesse=G_TEXT, farbe=TEXT_LEISE), formel(r"K_0=\frac{K_n}{q^{n}}", groesse=60), abstand=0.35,
        )
        block = self.tafel(VGroup(idee, idee2).arrange(DOWN, buff=0.2), barwert, abstand=0.8)
        boegen = VGroup(self.plan.bogen("B", 1), self.plan.bogen("C", 0))
        with self.sprich(
            "Geld von heute kann man anlegen. Darum vergleichen wir nur zum gleichen Zeitpunkt: "
            "Jede Zahlung wird auf heute abgezinst. Das ist ihr Barwert."
        ):
            self.warte_bis(0.25)
            self.play(auftritt(idee), auftritt(idee2), run_time=0.6)
            self.warte_bis(0.6)
            self.play(
                *[Create(b) for b in boegen], self.plan.faerbe("B", 1), self.plan.faerbe("C", 0), run_time=1.0,
            )
            self.warte_bis(0.85)
            self.play(auftritt(barwert), run_time=0.5)
        self.wait(0.4)
        self.play(
            FadeOut(block, shift=0.25 * UP), FadeOut(boegen),
            self.plan.faerbe("B", 1, TEXT), self.plan.faerbe("C", 0, TEXT), run_time=0.4,
        )

        # ---------- A und B ----------
        b_a = betrag("B_A", "=", r"50\,000", groesse=G_FORMEL)
        b_b = formel("B_B", "=", r"20\,000+", r"\frac{35\,000}{1{,}04^{4}}", groesse=G_FORMEL)
        b_b[3].set_color(HERVOR)
        b_b_wert = betrag(r"\approx", r"49\,918{,}15", groesse=G_FORMEL, farbe=HERVOR)
        b_b_wert[0][0].set_color(TEXT)
        block = self.tafel(b_a, b_b, b_b_wert, abstand=0.5)
        b_b_wert.align_to(b_b[1], LEFT)
        bogen = self.plan.bogen("B", 1)
        with self.sprich(
            "A kommt sofort, da gibt es nichts abzuzinsen. "
            "Bei B wird nur die spätere Zahlung abgezinst, dann wird addiert."
        ):
            self.play(Write(b_a), run_time=0.7)
            self.play(self.plan.barwert("A", spalte(r"50\,000"), b_a[0][2]), run_time=0.6)
            self.warte_bis(0.5)
            self.play(Create(bogen), self.plan.faerbe("B", 1), run_time=0.7)
            self.play(Write(b_b), run_time=0.8)
            self.warte_bis(0.88)
            self.play(Write(b_b_wert), run_time=0.6)
        self.play(self.plan.barwert("B", spalte(r"\approx 49\,918{,}15"), b_b_wert[0][1]), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(bogen), self.plan.faerbe("B", 1, TEXT), run_time=0.4)

        # ---------- C ----------
        b_c = formel("B_C", "=", r"\frac{60\,000}{1{,}04^{3}}", groesse=G_FORMEL)
        b_c[2].set_color(HERVOR)
        b_c_wert = betrag(r"\approx", r"53\,339{,}78", groesse=G_FORMEL, farbe=HERVOR)
        b_c_wert[0][0].set_color(TEXT)
        block = self.tafel(b_c, b_c_wert, abstand=0.5)
        b_c_wert.align_to(b_c[1], LEFT)
        bogen = self.plan.bogen("C", 0)
        with self.sprich("C: 60.000 durch 1,04 hoch 3."):
            self.play(Create(bogen), self.plan.faerbe("C", 0), run_time=0.7)
            self.play(Write(b_c), run_time=0.8)
            self.play(Write(b_c_wert), run_time=0.6)
        self.play(self.plan.barwert("C", spalte(r"\approx 53\,339{,}78"), b_c_wert[0][1]), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(block, shift=0.25 * UP), FadeOut(bogen), self.plan.faerbe("C", 0, TEXT), run_time=0.4)

        # ---------- Entscheidung ----------
        bekommt = text("Die Fahrschule bekommt das Geld:", groesse=G_TEXT, farbe=TEXT_LEISE)
        wahl = text("höchster Barwert → Angebot C", groesse=44, gewicht=BOLD, farben={"Angebot C": HERVOR})
        summe = VGroup(
            reihe(text("B: insgesamt", groesse=G_TEXT), betrag(r"55\,000", groesse=44), abstand=0.25),
            text("heute aber weniger wert als A", groesse=G_TEXT),
        ).arrange(DOWN, buff=0.2)
        block = self.tafel(VGroup(bekommt, wahl).arrange(DOWN, buff=0.3), summe, abstand=0.7)
        with self.sprich(
            "Die Fahrschule bekommt das Geld, sie wählt also den höchsten Barwert: Angebot C. "
            "B bringt zwar mehr als A, ist heute aber weniger wert."
        ):
            self.play(auftritt(bekommt), run_time=0.5)
            self.warte_bis(0.4)
            self.play(
                auftritt(wahl), self.plan.barwerte["C"].animate.set_color(HERVOR),
                self.plan.namen["C"].animate.set_color(HERVOR), run_time=0.6,
            )
            self.play(self.plan.betone("C"), run_time=0.6)
            self.warte_bis(0.66)
            self.play(auftritt(summe), self.plan.betone("B"), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(block, shift=0.25 * UP), run_time=0.4)

        # ---------- Kurzfassung ----------
        schritte = kurzfassung(
            reihe(text("Jede Zahlung abzinsen:", groesse=G_TEXT), formel(r"K_0=\frac{K_n}{q^{n}}", groesse=48),
                  abstand=0.25),
            text("Barwerte pro Angebot addieren", groesse=G_TEXT),
            VGroup(
                text("Verkäufer wählt den höchsten Barwert,", groesse=G_TEXT),
                text("Käufer den niedrigsten", groesse=G_TEXT),
            ).arrange(DOWN, buff=0.18, aligned_edge=LEFT),
        )
        self.tafel(schritte)
        with self.sprich(
            "Kurz gesagt: Jede Zahlung auf heute abzinsen, die Barwerte pro Angebot addieren. "
            "Der Verkäufer wählt den höchsten Barwert, der Käufer den niedrigsten."
        ):
            for zeile, beginn in zip(schritte, (0.1, 0.38, 0.62)):
                self.warte_bis(beginn)
                self.play(auftritt(zeile), run_time=0.5)
