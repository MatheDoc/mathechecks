"""Sprachdienst für alle Videos. Hier wird die Stimme zentral gewechselt."""
from manim_voiceover.services.base import SpeechService
from manim_voiceover.services.gtts import GTTSService


def sprachdienst() -> SpeechService:
    return GTTSService(lang="de", tld="de")
