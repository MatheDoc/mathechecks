"""Stimme der Videos: eigene Aufnahmen, wo vorhanden, sonst die Entwurfsstimme.

Eigene Aufnahmen liegen je Check unter videos/aufnahmen/<gebiet>/<lernbereich>/<NN>-<sammlung>/
(dieselbe Ablage wie die Szene) und entstehen mit videos/aufnahme.py. Eine Aufnahme gehört zu genau einem Sprechtext; ändert sich der Text,
passt sie nicht mehr und der Abschnitt wird wieder von der Entwurfsstimme gesprochen.
"""
import hashlib
import os
from pathlib import Path

from manim_voiceover._typing import VoiceoverData
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import PathLike, SpeechService, initialize_speech_service
from manim_voiceover.services.gtts import GTTSService
from slugify import slugify

from . import theme as t

AUFNAHMEN = t.VIDEOS / "aufnahmen"
EIGEN = "aufnahme"  # Kennung des Dienstes im Bericht


def _kennung(sprechtext: str) -> str:
    return hashlib.sha256(" ".join(sprechtext.split()).encode("utf-8")).hexdigest()[:8]


def aufnahme_name(nr: int, sprechtext: str) -> str:
    """Dateiname der Aufnahme zu einem Sprechtext; die Kennung am Ende hängt nur vom Text ab."""
    return f"{nr:02d}-{slugify(sprechtext, max_length=40, word_boundary=True)}-{_kennung(sprechtext)}.mp3"


def finde_aufnahme(ablage: str, sprechtext: str) -> Path | None:
    return next((AUFNAHMEN / ablage).glob(f"*-{_kennung(sprechtext)}.mp3"), None)


class EigeneStimme(SpeechService):
    """Spielt die Aufnahme zum Sprechtext; fehlt sie, spricht die Entwurfsstimme."""

    def __init__(self, ablage: str, entwurf: SpeechService, **kwargs: object) -> None:
        initialize_speech_service(self, kwargs)
        self.ablage = ablage
        self.entwurf = entwurf

    def generate_from_text(
        self,
        text: str,
        cache_dir: PathLike | None = None,
        path: PathLike | None = None,
        **kwargs: object,
    ) -> VoiceoverData:
        cache_dir = cache_dir or self.cache_dir
        aufnahme = finde_aufnahme(self.ablage, text)
        if aufnahme is None:
            return self.entwurf.generate_from_text(text, cache_dir=cache_dir, path=path, **kwargs)
        return {
            "input_text": text,
            "input_data": {"input_text": remove_bookmarks(text), "service": EIGEN},
            "original_audio": os.path.relpath(aufnahme, cache_dir),
        }


def sprachdienst(ablage: str) -> SpeechService:
    """Sprachdienst für ein Video; ablage ist <gebiet>/<lernbereich>/<NN>-<sammlung>.

    Die Entwurfsstimme wird hier zentral gewechselt.
    """
    return EigeneStimme(ablage, entwurf=GTTSService(lang="de", tld="de"))
