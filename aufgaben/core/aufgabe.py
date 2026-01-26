from abc import ABC, abstractmethod

class Aufgabe(ABC):  # Erbt von ABC
    def __init__(self, nummer):
        self.nummer = nummer

    @abstractmethod  # Das ist eine abstrakte Methode!
    def einleitung(self):
        pass

    @abstractmethod
    def fragen(self):
        pass

    @abstractmethod
    def antworten(self):
        pass

    def to_json(self):
        return {
            "titel": f"Aufgabe {self.nummer}",
            "einleitung": self.einleitung(),
            "fragen": self.fragen(),
            "antworten": self.antworten()
        }