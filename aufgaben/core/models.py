from dataclasses import dataclass


@dataclass
class Task:
    einleitung: str
    fragen: list[str]
    antworten: list[str]
    visual: dict | None = None

    def to_dict(self) -> dict:
        payload = {
            "einleitung": self.einleitung,
            "fragen": self.fragen,
            "antworten": self.antworten,
        }
        if self.visual is not None:
            payload["visual"] = self.visual
        return payload
