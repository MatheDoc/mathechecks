"""Basisszene: jedes Check-Video erbt von MCSzene und füllt nur inhalt()."""
import json
import os
from collections.abc import Iterator, Sequence
from contextlib import contextmanager

from manim import (
    BOLD,
    DOWN,
    RIGHT,
    SEMIBOLD,
    UP,
    Animation,
    Axes,
    DashedLine,
    FadeIn,
    FadeOut,
    Group,
    LaggedStart,
    ManimColor,
    MathTex,
    Mobject,
    RoundedRectangle,
    VGroup,
    interpolate_color,
    rate_functions,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.tracker import VoiceoverTracker

from . import theme as t
from .bausteine import auftritt, einpassen, formel, frage, lichthof, logo, text
from .stimme import EIGEN, aufnahme_name, sprachdienst

_TOLERANZ = 0.02
_LOGO_KLEIN = 0.7
_LOGO_GROSS = 1.7  # in der Begrüßung; im Schlussbild ist das Logo noch größer


class MCSzene(VoiceoverScene):
    # Begrüßung und Schluss aller Videos; hier ändern, dann neu rendern.
    begruessung = "MatheChecks zeigt's dir."
    schlussbild = "Jetzt bist du dran."
    schlusston = "Jetzt bist du dran. Bis zum nächsten Check!"

    def inhalt(self) -> None:
        """Inhalt des Videos; beginnt mit self.einstieg(...)."""
        raise NotImplementedError

    def construct(self) -> None:
        self.check_id = os.environ["MC_CHECK_ID"]  # setzt render.py aus dem Dateipfad
        self.camera.background_color = t.HINTERGRUND
        self.set_speech_service(sprachdienst(os.environ["MC_ABLAGE"]), create_subcaption=False)
        self._abschnitte: list[dict[str, object]] = []
        self._verstoesse: dict[str, float] = {}
        self._standbilder = bool(os.environ.get("MC_STANDBILDER"))
        self._bildordner = t.VIDEOS / "media" / "pruefung" / self.check_id
        if self._standbilder and self._bildordner.exists():
            for alt in self._bildordner.glob("*.png"):
                alt.unlink()

        self.marke = logo(_LOGO_GROSS)
        self._karte_unten = t.KARTE_UNTEN
        self.schimmer = lichthof(8, t.MARKE, staerke=0.45).move_to([0, t.HOEHE / 2, 0])
        self._hintergrund = [self.schimmer]  # Farbflächen ohne Inhalt, von der Randprüfung ausgenommen
        self.add(self.schimmer)

        self.inhalt()
        self.abschluss()
        self._bericht()

    # ---------- Einstieg ----------
    def einstieg(
        self,
        *zeilen: str,
        bild: Sequence[Animation],
        kopf: Mobject | None = None,
        zusatz: str | None = None,
        sprechtext: str | None = None,
    ) -> None:
        """Fester Beginn: Das Bild entsteht, die Frage erscheint, dann die Begrüßung mit Logo und Adresse.

        zeilen: die Frage, eine Bildzeile je Argument.
        bild: Animationen, die das kennzeichnende Bild des Videos aufbauen.
        kopf: Kopfzeile (self.kopf), die nach der Begrüßung eingeblendet wird.
        zusatz: Ergänzung zur Frage, kleiner darunter, etwa „(mit bedingten Wahrscheinlichkeiten)“.
        sprechtext: gesprochene Frage, falls sie von den Bildzeilen (samt Zusatz) abweicht.
        """
        fragezeilen = frage(*zeilen, zusatz=zusatz)
        adresse = text("mathechecks.de", groesse=32, farbe=t.TEXT_LEISE, gewicht=SEMIBOLD)
        self.tafel(fragezeilen, VGroup(self.marke, adresse).arrange(DOWN, buff=0.35), abstand=0.8)
        hof = lichthof(1.3 * self.marke.height, t.MARKE).move_to(self.marke).set_z_index(-1)
        self._hintergrund.append(hof)
        with self.sprich(sprechtext or " ".join([*zeilen, *([zusatz] if zusatz else [])])):
            self.play(*bild, LaggedStart(*[auftritt(zeile) for zeile in fragezeilen], lag_ratio=0.5), run_time=1.4)

        with self.sprich(self.begruessung):
            self.play(
                FadeIn(self.marke, scale=0.6, rate_func=rate_functions.ease_out_back),
                FadeIn(hof),
                run_time=0.6,
            )
            self.play(FadeIn(adresse), run_time=0.4)

        breite_klein = self.marke.width / self.marke.height * _LOGO_KLEIN
        self.play(
            FadeOut(fragezeilen, shift=0.25 * UP),
            FadeOut(adresse),
            FadeOut(hof),
            self.marke.animate.scale_to_fit_height(_LOGO_KLEIN).move_to([t.RAND_LINKS + breite_klein / 2, t.KOPF_Y, 0]),
            *([FadeIn(kopf)] if kopf is not None else []),
            run_time=0.6,
        )

    # ---------- Aufbau ----------
    def kopf(self, *tex: str) -> MathTex:
        """Kopfzeile neben dem Logo: das Gegebene, auf das sich die Rechnung bezieht, oder am Ende das Ergebnis.

        Mehrere Teile lassen sich einzeln färben.
        """
        titel = formel(*tex, groesse=t.S_TITEL)
        einpassen(titel, t.BREITE - 4 * _LOGO_KLEIN)
        return titel.move_to([0, t.KOPF_Y, 0])

    def buehne(self, hoehe: float | None = None) -> RoundedRectangle:
        """Karte, auf der Graph, Diagramm oder Skizze liegen; oben in der Stimmungsfarbe getönt.

        hoehe: Höhe der Karte. Eine flache Karte (etwa für einen Zahlenstrahl) lässt der
        Tafel darunter mehr Platz. Vor achsen(), auf_buehne() und tafel() aufrufen.
        """
        if hoehe is not None:
            self._karte_unten = t.KARTE_OBEN - hoehe
        karte = RoundedRectangle(
            width=t.RAND_RECHTS - t.RAND_LINKS, height=t.KARTE_OBEN - self._karte_unten, corner_radius=0.35,
            stroke_color=interpolate_color(ManimColor(t.RAHMEN), ManimColor(t.MARKE), 0.35), stroke_width=2,
        )
        karte.set_fill(color=[self._kartenfarbe(t.KARTE_OBEN), self._kartenfarbe(self._karte_unten)], opacity=1)
        karte.set_sheen_direction(DOWN)
        return karte.move_to([0, (t.KARTE_OBEN + self._karte_unten) / 2, 0])

    def auf_buehne(self, bild: Mobject) -> Mobject:
        """Passt ein Bild in die Karte ein und setzt es in ihre Mitte."""
        einpassen(bild, t.BUEHNE_BREITE, t.KARTE_OBEN - self._karte_unten - 2 * t.KARTE_INNENRAND)
        return bild.move_to([0, (t.KARTE_OBEN + self._karte_unten) / 2, 0])

    def _kartenfarbe(self, y: float) -> ManimColor:
        """Farbe der Karte auf der Höhe y (Verlauf von getönt oben nach neutral unten)."""
        hoehe = (y - self._karte_unten) / (t.KARTE_OBEN - self._karte_unten)
        return interpolate_color(ManimColor(t.FLAECHE), ManimColor(t.MARKE), t.KARTE_TOENUNG * hoehe)

    def achsen(
        self,
        x: tuple[float, float, float],
        y: tuple[float, float, float],
        x_zahlen: tuple[float, ...] | None = None,
        y_zahlen: tuple[float, ...] | None = None,
    ) -> Axes:
        """Beschriftetes Koordinatensystem, eingepasst in die Bühne.

        x_zahlen, y_zahlen: nur diese Werte beschriften, etwa wenn der Graph sonst
        durch eine Achsenzahl läuft. Ohne Angabe wird jeder Teilstrich beschriftet.
        """
        hoehe = t.KARTE_OBEN - self._karte_unten - 2 * t.KARTE_INNENRAND
        achsen = Axes(
            x_range=list(x),
            y_range=list(y),
            x_length=t.BUEHNE_BREITE,
            y_length=hoehe,
            axis_config={
                "color": t.ACHSE, "stroke_width": 3, "include_tip": False,
                "include_numbers": True, "font_size": 32,
            },
            x_axis_config={"numbers_to_include": x_zahlen},
            y_axis_config={"numbers_to_include": y_zahlen},
        )
        achsen.add(
            formel("x", groesse=36, farbe=t.ACHSE).next_to(achsen.x_axis.get_end(), UP, buff=0.15),
            formel("y", groesse=36, farbe=t.ACHSE).next_to(achsen.y_axis.get_end(), RIGHT, buff=0.2),
        )
        return self.auf_buehne(achsen)

    def senkrechte(self, achsen: Axes, x: float, farbe: str = t.HERVOR) -> DashedLine:
        """Gestrichelte Hilfslinie an der Stelle x; die Achsenzahl dort bleibt lesbar."""
        unten, oben = achsen.y_range[0], achsen.y_range[1]
        linie = DashedLine(achsen.c2p(x, unten), achsen.c2p(x, oben), color=farbe, stroke_width=3, dash_length=0.12)
        for zahl in achsen.x_axis.numbers:
            if abs(zahl.number - x) < 1e-9:
                zahl.add_background_rectangle(color=self._kartenfarbe(zahl.get_y()), opacity=1, buff=0.06)
                zahl.set_z_index(1)
        return linie

    def tafel(self, *zeilen: Mobject, abstand: float = 0.38) -> VGroup:
        """Ordnet Zeilen untereinander an und setzt sie in den Rechenbereich unter der Karte.

        Eine zu breite Zeile wird allein verkleinert; die übrigen behalten ihre Größe.
        Bleibt Platz frei, rückt der Block ein Stück nach unten (theme.TAFEL_LAGE), damit das Bild
        gleichmäßiger gefüllt ist.
        """
        oben = self._karte_unten - t.TAFEL_ABSTAND
        for zeile in zeilen:
            einpassen(zeile, t.TAFEL_BREITE)
        block = VGroup(*zeilen).arrange(DOWN, buff=abstand)
        einpassen(block, hoehe=oben - t.RAND_UNTEN)
        frei = oben - t.RAND_UNTEN - block.height
        return block.move_to([0, oben - t.TAFEL_LAGE * frei - block.height / 2, 0])

    # ---------- Ton ----------
    @contextmanager
    def sprich(self, sprechtext: str) -> Iterator[VoiceoverTracker]:
        """Spricht den Text; die Animationen im Block laufen dazu.

        sprechtext: so geschrieben, wie es gesprochen wird („f Strich von x“).
        """
        beginn = self.renderer.time
        with self.voiceover(text=sprechtext) as verlauf:
            yield verlauf
        self._abschnitte.append({
            "beginn": round(beginn, 2),
            "sprechtext": sprechtext,
            "bild": self._standbild(),
            "aufnahme": aufnahme_name(len(self._abschnitte) + 1, sprechtext),
            "eigene_stimme": (verlauf.data.get("input_data") or {}).get("service") == EIGEN,
        })

    def warte_bis(self, anteil: float) -> None:
        """Wartet, bis dieser Anteil (0 bis 1) des laufenden Sprechtexts gesprochen ist.

        So bleiben Einblendungen beim Wort, auch wenn die Stimme wechselt.
        """
        ton = self.current_tracker
        vergangen = ton.duration - ton.get_remaining_duration()
        self.safe_wait(ton.duration * anteil - vergangen)

    def play(self, *args: object, **kwargs: object) -> None:
        super().play(*args, **kwargs)
        self._pruefe_rand()

    # ---------- Schluss ----------
    def abschluss(self) -> None:
        """Schlussbild: Das Logo wandert aus der Ecke in die Bildmitte."""
        rest = [m for m in self.mobjects if m is not self.marke and m is not self.schimmer]
        mitte = (t.RAND_OBEN + t.RAND_UNTEN) / 2
        ziel = [0, mitte + 1.3, 0]
        hof = lichthof(3.2, t.MARKE).move_to(ziel).set_z_index(-1)
        self._hintergrund.append(hof)
        ruf = text(self.schlussbild, groesse=54, gewicht=BOLD)
        adresse = text("mathechecks.de", groesse=38, farbe=t.TEXT_LEISE, gewicht=SEMIBOLD)
        VGroup(ruf, adresse).arrange(DOWN, buff=0.45).move_to([0, mitte - 1.6, 0])

        if rest:
            self.play(*[FadeOut(m) for m in rest], run_time=0.4)
        with self.sprich(self.schlusston):
            self.play(
                self.marke.animate(rate_func=rate_functions.ease_out_back).scale_to_fit_height(2.6).move_to(ziel),
                FadeIn(hof),
                run_time=0.8,
            )
            self.play(auftritt(ruf), run_time=0.4)
            self.play(FadeIn(adresse), run_time=0.4)
        self.wait(0.6)

    # ---------- Prüfung ----------
    def _blaetter(self, mobs: list[Mobject]) -> Iterator[Mobject]:
        for mob in mobs:
            if any(mob is flaeche for flaeche in self._hintergrund):  # darf über den sichtbaren Bereich reichen
                continue
            if type(mob) in (VGroup, Group):
                yield from self._blaetter(mob.submobjects)
            elif mob.family_members_with_points():
                yield mob

    def _pruefe_rand(self) -> None:
        """Merkt sich jedes Objekt, das den sichtbaren Bereich verlässt."""
        for mob in self._blaetter(self.mobjects):
            links, rechts = mob.get_left()[0], mob.get_right()[0]
            unten, oben = mob.get_bottom()[1], mob.get_top()[1]
            raender = []
            if links < t.RAND_LINKS - _TOLERANZ:
                raender.append("links")
            if rechts > t.RAND_RECHTS + _TOLERANZ:
                raender.append("rechts")
            if oben > t.RAND_OBEN + _TOLERANZ:
                raender.append("oben")
            if unten < t.RAND_UNTEN - _TOLERANZ:
                raender.append("unten")
            if rechts > t.KNOPF_X + _TOLERANZ and unten < t.KNOPF_Y - _TOLERANZ:
                raender.append("Bedienleiste")
            if raender:
                inhalt = getattr(mob, "original_text", None) or getattr(mob, "tex_string", "")
                name = f"{type(mob).__name__} {inhalt[:40]!r}: {', '.join(raender)}"
                self._verstoesse.setdefault(name, round(self.renderer.time, 1))

    def _standbild(self) -> str | None:
        """Speichert im Entwurf das aktuelle Bild und gibt den Dateinamen zurück."""
        if not self._standbilder:
            return None
        self._bildordner.mkdir(parents=True, exist_ok=True)
        name = f"{len(self._abschnitte) + 1:02d}.png"
        self.renderer.update_frame(self)
        self.renderer.camera.get_image().save(self._bildordner / name)
        return name

    def _bericht(self) -> None:
        ordner = t.VIDEOS / "media" / "berichte"
        ordner.mkdir(parents=True, exist_ok=True)
        bericht = {
            "check_id": self.check_id,
            "qualitaet": t.QUALITAET,
            "sekunden": round(self.renderer.time, 1),
            "woerter": sum(len(str(a["sprechtext"]).split()) for a in self._abschnitte),
            "verstoesse": [f"{zeit} s  {name}" for name, zeit in self._verstoesse.items()],
            "abschnitte": self._abschnitte,
            "video": str(self.renderer.file_writer.movie_file_path),
        }
        (ordner / f"{self.check_id}.json").write_text(json.dumps(bericht, ensure_ascii=False, indent=2), encoding="utf-8")
