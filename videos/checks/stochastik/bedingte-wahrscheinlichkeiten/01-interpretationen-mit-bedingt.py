"""Check 01 – Bedingte Wkt symbolisch.

Kernidee: Der Index ist die Bedingung und legt fest, worauf sich die Wahrscheinlichkeit bezieht (das Ganze);
die Klammer sagt, was über diese Gruppe gefragt ist. Ohne Index bezieht sie sich auf alle.
Beispiel: Ereignisse aus dem Musterbeispiel (Zähneputzen). Zusätzlich ein Feld mit 30 Personen, A und B als
Kästen wie im Kontextbild; jede Wahrscheinlichkeit erscheint als Teil durch Ganzes (wie im Skript „Das Ganze
und der Teil“). Die Kästen reichen nicht über das ganze Feld, sonst wären A und B unabhängig (P_A(B) = P(B)).
Zahlen: |A| = 10, |B| = 12, |A ∩ B| = 6, also P(A ∩ B) = 20 %, P_A(B) = 60 %, P_B(A) = 50 %, P_nA(B) = 30 %.
Aus dem Training fehlen Einzelwahrscheinlichkeit und die Sonderfälle (entweder–oder, Summe, P(A ∪ nicht A));
die Vereinigung kommt nur in der Kurzfassung vor.
"""
from manim import BOLD, DOWN, LEFT, UP, FadeIn, FadeOut, VGroup, Write

from mcvideo import MCSzene, Punktefeld, auftritt, aufzaehlung, einpassen, formel, legende, reihe, text
from mcvideo.theme import BLAU, BREITE, GRUEN, HERVOR, KOPF_Y, TEXT_LEISE

G_FORMEL = 52
G_TEXT = 40
G_WORTLAUT = 32


def deutung(symbol: str, *wortlaut: str) -> VGroup:
    """Symbol mit „ist die Wahrscheinlichkeit, dass“ (klein, wie im Training) und darunter der Wortlaut,
    eine Bildzeile je Argument; höchstens etwa 26 Zeichen pro Zeile, damit nichts verkleinert wird."""
    kopf = reihe(formel(symbol, groesse=44), text("ist die Wahrscheinlichkeit, dass", groesse=26, farbe=TEXT_LEISE),
                 grundlinie=True)
    zeilen = VGroup(*[text(zeile, groesse=G_WORTLAUT, gewicht=BOLD) for zeile in wortlaut]).arrange(DOWN, buff=0.15)
    return VGroup(kopf, zeilen).arrange(DOWN, buff=0.25)


def anteil(teil: int, ganzes: int, prozent: int, gruppe: str | None, farbe: str = TEXT_LEISE) -> VGroup:
    """Teil durch Ganzes, der Teil in der Farbe der markierten Personen; daneben, worauf sich der Anteil bezieht."""
    bruch = formel(rf"\frac{{{teil}}}{{{ganzes}}}", rf"={prozent}\,\%", groesse=G_FORMEL)
    bruch[0][:len(str(teil))].set_color(HERVOR)
    wer = formel(gruppe, groesse=40, farbe=farbe) if gruppe else text("alle", groesse=32, farbe=farbe)
    return reihe(bruch, reihe(text("Ganzes:", groesse=32, farbe=TEXT_LEISE), wer, abstand=0.15), abstand=0.5)


class Video(MCSzene):
    def inhalt(self) -> None:
        karte = self.buehne(hoehe=3.4)  # flach: Die Tafel braucht Platz für zwei Fälle untereinander
        feld = self.auf_buehne(Punktefeld(5, 6, {
            "A": (range(0, 2), range(0, 5), BLAU, "links"),
            "B": (range(0, 3), range(2, 6), GRUEN, "rechts"),
        }))
        self.add(karte)
        a, b, na = feld.mengen["A"], feld.mengen["B"], feld.ohne("A")

        self.einstieg(
            "Wie übersetzt du", "Wahrscheinlichkeiten", "in Worte?",
            zusatz="(mit bedingten Wahrscheinlichkeiten)",
            bild=feld.aufbau(),
        )

        # ---------- Sachzusammenhang ----------
        ereignisse = legende(
            (formel("A", groesse=54, farbe=BLAU), text("putzt regelmäßig die Zähne", groesse=G_TEXT)),
            (formel("B", groesse=54, farbe=GRUEN), text("hat gesunde Zähne", groesse=G_TEXT)),
            abstand=0.5,
        )
        sach = self.tafel(ereignisse)
        kopf = reihe(
            reihe(formel("A", groesse=36, farbe=BLAU), text("putzt", groesse=26), abstand=0.18),
            reihe(formel("B", groesse=36, farbe=GRUEN), text("gesunde Zähne", groesse=26), abstand=0.18),
            abstand=0.7,
        )
        einpassen(kopf, BREITE - 3).move_to([0.4, KOPF_Y, 0])
        with self.sprich(
            "30 Personen. 10 putzen regelmäßig die Zähne, das ist A. "
            "12 haben gesunde Zähne, das ist B."
        ):
            self.play(auftritt(ereignisse[0]), run_time=0.5)
            self.warte_bis(0.15)
            self.play(feld.zeige("A"), run_time=0.8)
            self.warte_bis(0.6)
            self.play(auftritt(ereignisse[1]), feld.zeige("B"), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(sach, target_position=kopf, scale=0.5), FadeIn(kopf), run_time=0.6)

        # ---------- Ohne Index ----------
        schnitt = deutung(r"P(A\cap B)", "eine Person regelmäßig", "die Zähne putzt und", "gesunde Zähne hat.")
        schnitt_anteil = anteil(6, 30, 20, None)
        block1 = self.tafel(text("Ohne Index", groesse=40, gewicht=BOLD), schnitt, schnitt_anteil, abstand=0.6)
        with self.sprich(
            "P von A und B ist die Wahrscheinlichkeit, dass eine Person regelmäßig die Zähne putzt "
            "und gesunde Zähne hat. Ohne Index bezieht sich das auf alle 30. 6 haben beides."
        ):
            self.play(auftritt(block1[0]), run_time=0.4)
            self.play(auftritt(schnitt), run_time=0.6)
            self.warte_bis(0.6)
            self.play(feld.markiere(feld.alle), run_time=0.4)
            self.warte_bis(0.82)
            self.play(feld.markiere(feld.alle, a & b), Write(schnitt_anteil), run_time=0.9)
        self.wait(0.6)
        self.play(FadeOut(block1, shift=0.25 * UP), feld.markiere(), run_time=0.4)

        # ---------- Mit Index: Bedingung A, umgedreht Bedingung B ----------
        bed_a = deutung("P_A(B)", "eine Person, die regelmäßig", "die Zähne putzt,", "gesunde Zähne hat.")
        anteil_a = anteil(6, 10, 60, "A", farbe=BLAU)
        bed_b = deutung("P_B(A)", "eine Person mit gesunden", "Zähnen regelmäßig", "die Zähne putzt.")
        anteil_b = anteil(6, 12, 50, "B", farbe=GRUEN)
        fall_a = VGroup(bed_a, anteil_a).arrange(DOWN, buff=0.3)
        fall_b = VGroup(bed_b, anteil_b).arrange(DOWN, buff=0.3)
        block2 = self.tafel(text("Mit Index", groesse=40, gewicht=BOLD), fall_a, fall_b, abstand=0.6)
        with self.sprich(
            "Mit Index: P von B unter der Bedingung A ist die Wahrscheinlichkeit, dass eine Person, "
            "die regelmäßig die Zähne putzt, gesunde Zähne hat. Der Index ist die Bedingung. "
            "Jetzt geht es nur um die 10, die putzen. 6 davon haben gesunde Zähne."
        ):
            self.play(auftritt(block2[0]), run_time=0.4)
            self.play(auftritt(bed_a), run_time=0.6)
            self.warte_bis(0.64)
            self.play(feld.markiere(a, kasten="A"), run_time=0.6)
            self.warte_bis(0.85)
            self.play(feld.markiere(a, a & b, kasten="A"), Write(anteil_a), run_time=0.9)
        with self.sprich(
            "Umgedreht, P von A unter der Bedingung B: Jetzt geht es nur um die 12 mit gesunden Zähnen. "
            "6 davon putzen regelmäßig. Ein anderer Wert."
        ):
            self.play(auftritt(bed_b), feld.markiere(), run_time=0.6)
            self.warte_bis(0.3)
            self.play(feld.markiere(b, kasten="B"), run_time=0.6)
            self.warte_bis(0.62)
            self.play(feld.markiere(b, a & b, kasten="B"), Write(anteil_b), run_time=0.9)
        self.wait(0.8)
        self.play(FadeOut(block2, shift=0.25 * UP), feld.markiere(), run_time=0.4)

        # ---------- Gegenereignis im Index ----------
        bed_na = deutung(r"P_{\overline{A}}(B)", "eine Person, die nicht", "regelmäßig die Zähne putzt,",
                         "dennoch gesunde Zähne hat.")
        anteil_na = anteil(6, 20, 30, r"\overline{A}")
        block3 = self.tafel(text("Gegenereignis im Index", groesse=40, gewicht=BOLD), bed_na, anteil_na, abstand=0.6)
        with self.sprich(
            "Steht nicht A im Index, geht es um die 20 außerhalb von A: Sie putzen nicht regelmäßig. "
            "6 davon haben dennoch gesunde Zähne."
        ):
            self.play(auftritt(block3[0]), auftritt(bed_na), run_time=0.6)
            self.warte_bis(0.25)
            self.play(feld.markiere(na), run_time=0.6)
            self.warte_bis(0.75)
            self.play(feld.markiere(na, na & b), Write(anteil_na), run_time=0.9)
        self.wait(0.6)
        self.play(FadeOut(block3, shift=0.25 * UP), feld.markiere(), run_time=0.4)

        # ---------- Kurzfassung ----------
        def bedeutung(inhalt: str) -> VGroup:
            return text(inhalt, groesse=G_TEXT, farbe=TEXT_LEISE)

        ohne = text("ohne Index: alle", groesse=38, gewicht=BOLD)
        mit = text("mit Index: nur die Bedingung", groesse=38, gewicht=BOLD)
        punkte = aufzaehlung(
            (formel(r"P(A\cap B)", groesse=G_FORMEL), bedeutung("A und B")),
            (formel(r"P(A\cup B)", groesse=G_FORMEL), bedeutung("A oder B")),
            (formel("P_A(B)", groesse=G_FORMEL), bedeutung("B unter der Bedingung A")),
            (formel("P_B(A)", groesse=G_FORMEL), bedeutung("A unter der Bedingung B")),
        )
        uebersicht = VGroup(ohne, *punkte[:2], mit, *punkte[2:]).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        VGroup(mit, *punkte[2:]).shift(0.3 * DOWN)
        self.tafel(uebersicht)
        with self.sprich(
            "Kurz gesagt: Ohne Index sprichst du über alle. Und ist der Schnitt, oder die Vereinigung. "
            "Mit Index sprichst du nur über die Bedingung."
        ):
            self.play(auftritt(ohne), feld.markiere(feld.alle), run_time=0.4)
            self.warte_bis(0.3)
            self.play(auftritt(punkte[0]), run_time=0.4)
            self.warte_bis(0.45)
            self.play(auftritt(punkte[1]), run_time=0.4)
            self.warte_bis(0.62)
            self.play(auftritt(mit), feld.markiere(a, kasten="A"), run_time=0.4)
            self.play(auftritt(punkte[2]), run_time=0.4)
            self.play(auftritt(punkte[3]), feld.markiere(b, kasten="B"), run_time=0.4)
        self.wait(1.5)
