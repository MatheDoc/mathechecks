"""Check 07 – Kenngrößen direkt berechnen.

Kernidee: μ = n·p und σ = √(n·p·(1−p)) verbinden n, p, μ und σ. Sind n und p gegeben, wird eingesetzt;
fehlt n oder p, wird zuerst μ = n·p umgestellt, danach σ berechnet.
Beispiel: die drei Fälle des Musterbeispiels (Münze n = 20, p = 0,5; Polizei n = 200, μ = 25 → p = 0,125;
Parkplatz p = 0,15, μ = 12 → n = 80), σ auf 2 Nachkommastellen wie im Training (2,24; 4,68; 3,19).
"""
from manim import BOLD, DOWN, UP, FadeOut, Mobject, VGroup, Write

from mcvideo import MCSzene, auftritt, aufzaehlung, formel, reihe, text, welle
from mcvideo.theme import HERVOR, TEXT, TEXT_LEISE

G_FORMEL = 54
G_GEGEBEN = 50
G_TEXT = 38

# Teile von μ = n · p
MU, N, P = 0, 2, 4


def gegeben(*angaben: str) -> VGroup:
    return reihe(*[formel(a, groesse=G_GEGEBEN, farbe=TEXT_LEISE) for a in angaben], abstand=0.6)



def ergebnis(tex: str) -> Mobject:
    return formel(tex, groesse=G_FORMEL, farbe=HERVOR)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.4)
        self.add(karte)
        self.mu = formel(r"\mu", "=", "n", r"\cdot", "p", groesse=100)
        self.sigma = formel(r"\sigma=\sqrt{n\cdot p\cdot (1-p)}", groesse=80)
        self.auf_buehne(VGroup(self.mu, self.sigma).arrange(DOWN, buff=0.45))

        self.einstieg(
            "Wie berechnest du", "μ und σ?",
            zusatz="(bei der Binomialverteilung)",
            sprechtext="Wie berechnest du Erwartungswert und Standardabweichung bei der Binomialverteilung?",
            bild=[Write(self.mu), Write(self.sigma)],
        )

        # ---------- Idee ----------
        idee = self.tafel(
            reihe(formel(r"\mu", groesse=72), text("Erwartungswert", groesse=G_TEXT), abstand=0.3),
            reihe(formel(r"\sigma", groesse=72), text("Standardabweichung", groesse=G_TEXT), abstand=0.3),
            text("2 der Größen gegeben", groesse=44, gewicht=BOLD),
            abstand=0.5,
        )
        with self.sprich(
            "Der Erwartungswert mü ist n mal p. Die Standardabweichung Sigma ist die Wurzel aus n mal p mal 1 minus p. "
            "2 der Größen sind gegeben, den Rest berechnen wir."
        ):
            self.play(auftritt(idee[0]), welle(self.mu, HERVOR), run_time=0.6)
            self.warte_bis(0.3)
            self.play(auftritt(idee[1]), welle(self.sigma, HERVOR), run_time=0.6)
            self.warte_bis(0.75)
            self.play(auftritt(idee[2]), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(idee, shift=0.25 * UP), run_time=0.4)

        # ---------- n und p gegeben ----------
        self.fall(
            text("Münze, 20 Würfe, X zählt Kopf", groesse=G_TEXT, gewicht=BOLD),
            gegeben("n=20", "p=0{,}5"),
            [
                ergebnis(r"\mu=20\cdot 0{,}5=10"),
                ergebnis(r"\sigma=\sqrt{20\cdot 0{,}5\cdot 0{,}5}\approx 2{,}24"),
            ],
            fehlt=None,
            rechnung_ab=(0.45, 0.7),
            sprechtext="Eine Münze wird 20-mal geworfen, X zählt Kopf. n und p sind gegeben, also nur einsetzen: "
                       "mü gleich 10, Sigma etwa 2,24.",
        )

        # ---------- p fehlt ----------
        self.fall(
            text("200 Fahrer, im Mittel 25 alkoholisiert", groesse=G_TEXT, gewicht=BOLD),
            gegeben("n=200", r"\mu=25"),
            [
                formel(r"25=200\cdot p\quad|:200", groesse=G_FORMEL),
                ergebnis(r"p=0{,}125"),
                ergebnis(r"\sigma=\sqrt{200\cdot 0{,}125\cdot 0{,}875}\approx 4{,}68"),
            ],
            fehlt=P,
            rechnung_ab=(0.35, 0.6, 0.8),
            sprechtext="200 Autofahrer werden kontrolliert, im Mittel sind 25 alkoholisiert. "
                       "Jetzt fehlt p. Wir stellen mü gleich n mal p um: p ist 0,125. "
                       "Dann Sigma: etwa 4,68.",
        )

        # ---------- n fehlt ----------
        self.fall(
            text("15 % ohne Parkschein, im Mittel 12", groesse=G_TEXT, gewicht=BOLD),
            gegeben(r"p=0{,}15", r"\mu=12"),
            [
                formel(r"12=n\cdot 0{,}15\quad|:0{,}15", groesse=G_FORMEL),
                ergebnis(r"n=80"),
                ergebnis(r"\sigma=\sqrt{80\cdot 0{,}15\cdot 0{,}85}\approx 3{,}19"),
            ],
            fehlt=N,
            rechnung_ab=(0.35, 0.6, 0.8),
            sprechtext="15 % parken ohne Parkschein, im Mittel sollen 12 erwischt werden. "
                       "Jetzt fehlt n: 12 durch 0,15 ist 80. "
                       "Sigma ist etwa 3,19.",
        )

        # ---------- Kurzfassung ----------
        punkte = aufzaehlung(
            reihe(formel("n,\\ p", groesse=68), text("gegeben: einsetzen", groesse=44), abstand=0.25, grundlinie=True),
            reihe(text("sonst zuerst", groesse=44), formel(r"\mu=n\cdot p", groesse=68), text("umstellen", groesse=44),
                  abstand=0.25, grundlinie=True),
            reihe(text("danach", groesse=44), formel(r"\sigma", groesse=68), abstand=0.25, grundlinie=True),
            abstand=0.6,
        )
        self.tafel(punkte)
        with self.sprich(
            "Kurz gesagt: Sind n und p gegeben, setzt du ein. Sonst stellst du zuerst mü gleich n mal p um. "
            "Danach berechnest du Sigma."
        ):
            for punkt, beginn in zip(punkte, (0.1, 0.4, 0.75)):
                self.warte_bis(beginn)
                self.play(auftritt(punkt), run_time=0.5)

    def fall(
        self,
        lage: Mobject,
        angaben: VGroup,
        rechnung: list[Mobject],
        *,
        fehlt: int | None,
        rechnung_ab: tuple[float, ...],
        sprechtext: str,
    ) -> None:
        """Ein Fall: Sachzusammenhang, Gegebenes, fehlende Größe in μ = n·p orange, Rechnung."""
        block = self.tafel(lage, angaben, *rechnung, abstand=0.45)
        stelle = self.mu[fehlt] if fehlt is not None else None
        with self.sprich(sprechtext):
            self.play(auftritt(lage), run_time=0.5)
            self.play(auftritt(angaben), run_time=0.5)
            if stelle is not None:
                self.play(stelle.animate.set_color(HERVOR), welle(stelle, HERVOR), run_time=0.6)
            for zeile, beginn in zip(rechnung, rechnung_ab):
                self.warte_bis(beginn)
                self.play(Write(zeile), run_time=0.8)
        self.wait(0.8)
        self.play(
            FadeOut(block, shift=0.25 * UP),
            *([stelle.animate.set_color(TEXT)] if stelle is not None else []),
            run_time=0.5,
        )
