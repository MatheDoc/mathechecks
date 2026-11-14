"""Basisszene: jedes Check-Video erbt von MCSzene und füllt nur inhalt()."""
import json
import os
from collections.abc import Iterator
from contextlib import contextmanager

from manim import (
    DOWN,
    RIGHT,
    SEMIBOLD,
    UP,
    Axes,
    Create,
    DashedLine,
    FadeIn,
    FadeOut,
    Group,
    MathTex,
    Mobject,
    RoundedRectangle,
    VGroup,
    VMobject,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.tracker import VoiceoverTracker

from . import theme as t
from .bausteine import einpassen, formel, logo, text
from .stimme import sprachdienst

_TOLERANZ = 0.02


class MCSzene(VoiceoverScene):
    kompetenz = ""     # kurzer Kompetenzsatz der Schlusskarte, z. B. „Ich kann Extrempunkte bestimmen.“
    schlusssatz = ""   # gesprochener Schluss, z. B. „Extrempunkte bestimmen? Check!“

    def inhalt(self) -> None:
        raise NotImplementedError

    def construct(self) -> None:
        self.check_id = os.environ["MC_CHECK_ID"]  # setzt render.py aus dem Dateipfad
        self.camera.background_color = t.HINTERGRUND
        self.set_speech_service(sprachdienst())
        self._abschnitte: list[dict[str, object]] = []
        self._verstoesse: dict[str, float] = {}
        self._standbilder = bool(os.environ.get("MC_STANDBILDER"))
        self._bildordner = t.VIDEOS / "media" / "pruefung" / self.check_id
        if self._standbilder and self._bildordner.exists():
            for alt in self._bildordner.glob("*.png"):
                alt.unlink()

        self.marke = logo()
        self.marke.move_to([t.RAND_LINKS + self.marke.width / 2, t.KOPF_Y, 0])
        self.add(self.marke)

        self.inhalt()
        self.abschluss()
        self._bericht()

    # ---------- Aufbau ----------
    def kopf(self, tex: str) -> MathTex:
        """Titelzeile neben dem Logo, z. B. der Funktionsterm."""
        titel = formel(tex, groesse=t.S_TITEL)
        einpassen(titel, t.BREITE - 4 * self.marke.width)
        return titel.move_to([0, t.KOPF_Y, 0])

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
        achsen = Axes(
            x_range=list(x),
            y_range=list(y),
            x_length=t.BUEHNE_BREITE,
            y_length=t.BUEHNE_HOEHE,
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
        einpassen(achsen, t.BUEHNE_BREITE, t.BUEHNE_HOEHE)
        return achsen.move_to([0, t.BUEHNE_MITTE_Y, 0])

    def senkrechte(self, achsen: Axes, x: float, farbe: str = t.HERVOR) -> DashedLine:
        """Gestrichelte Hilfslinie an der Stelle x; die Achsenzahl dort bleibt lesbar."""
        unten, oben = achsen.y_range[0], achsen.y_range[1]
        linie = DashedLine(achsen.c2p(x, unten), achsen.c2p(x, oben), color=farbe, stroke_width=3, dash_length=0.12)
        for zahl in achsen.x_axis.numbers:
            if abs(zahl.number - x) < 1e-9:
                zahl.add_background_rectangle(color=t.HINTERGRUND, opacity=1, buff=0.06)
                zahl.set_z_index(1)
        return linie

    def tafel(self, *zeilen: Mobject, abstand: float = 0.38) -> VGroup:
        """Ordnet Zeilen untereinander an und passt sie in den Rechenbereich ein."""
        block = VGroup(*zeilen).arrange(DOWN, buff=abstand)
        einpassen(block, t.TAFEL_BREITE, t.TAFEL_HOEHE)
        return block.move_to([0, t.TAFEL_OBEN - block.height / 2, 0])

    # ---------- Ton ----------
    @contextmanager
    def sprich(self, sprechtext: str, untertitel: str | None = None) -> Iterator[VoiceoverTracker]:
        """Spricht den Text; die Animationen im Block laufen dazu.

        sprechtext: so geschrieben, wie es gesprochen wird („f Strich von x“).
        untertitel: Lesefassung für die Untertiteldatei, falls sie abweicht.
        """
        beginn = self.renderer.time
        with self.voiceover(text=sprechtext, subcaption=untertitel) as verlauf:
            yield verlauf
        self._abschnitte.append({
            "beginn": round(beginn, 1),
            "sprechtext": sprechtext,
            "untertitel": untertitel,
            "bild": self._standbild(),
        })

    def play(self, *args: object, **kwargs: object) -> None:
        super().play(*args, **kwargs)
        self._pruefe_rand()

    # ---------- Schluss ----------
    def abschluss(self) -> None:
        """Schlusskarte: Der Kompetenzsatz wird abgehakt."""
        rest = [m for m in self.mobjects if m is not self.marke]
        kasten = RoundedRectangle(width=1.8, height=1.8, corner_radius=0.38, color=t.TEXT_LEISE, stroke_width=7)
        satz = einpassen(text(self.kompetenz, groesse=46, gewicht=SEMIBOLD), 7.8)
        adresse = text("mathechecks.de", groesse=40, farbe=t.AKZENT, gewicht=SEMIBOLD)
        VGroup(kasten, satz, adresse).arrange(DOWN, buff=0.8).move_to([0, (t.RAND_OBEN + t.RAND_UNTEN) / 2, 0])
        b = kasten.width
        haken = VMobject(color=t.GRUEN, stroke_width=16)
        haken.set_points_as_corners([
            kasten.get_center() + [-0.30 * b, 0.02 * b, 0],
            kasten.get_center() + [-0.06 * b, -0.24 * b, 0],
            kasten.get_center() + [0.44 * b, 0.40 * b, 0],
        ])

        if rest:
            self.play(*[FadeOut(m) for m in rest], run_time=0.5)
        with self.sprich(self.schlusssatz):
            self.play(FadeIn(kasten), FadeIn(satz, shift=0.2 * UP), run_time=0.5)
            self.play(Create(haken), run_time=0.4)
            self.play(FadeIn(adresse), run_time=0.4)
        self.wait(0.8)

    # ---------- Prüfung ----------
    def _blaetter(self, mobs: list[Mobject]) -> Iterator[Mobject]:
        for mob in mobs:
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
