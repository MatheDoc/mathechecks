from abc import abstractmethod
import random
from aufgaben.core.aufgabe import Aufgabe
from aufgaben.utils.latex_utils import latex_polynomial

class Basis(Aufgabe):
    def __init__(self, nummer):
        super().__init__(nummer)
        self._erzeuge_parameter()
        self._berechne_koeffizienten()

    @abstractmethod
    def _erzeuge_parameter(self):
        pass

    @abstractmethod
    def _berechne_koeffizienten(self):
        pass

    @abstractmethod
    def einleitung(self):
        pass

    def fragen(self):
        return ["Bestimmen Sie die Nullstellen von \\(f(x)\\) und geben Sie sie in aufsteigender Reihenfolge an."]
    

class Normalform(Basis):
    def _erzeuge_parameter(self):
        self.x1 = random.choice([-1, 1]) * random.randint(1, 9)
        self.x2 = random.choice([-1, 1]) * random.randint(1, 9)
        # Sicherstellen, dass die Nullstellen sich nicht um ein Vorzeichen unterscheiden
        while self.x1 == -self.x2:
            random.choice([-1, 1]) * random.randint(1, 9)
        
        self.a = random.choice([-1, 1]) * random.randint(1, 21) / 10

    def _berechne_koeffizienten(self):
        self.b = -self.a * (self.x1 + self.x2)
        self.c = self.a * self.x1 * self.x2

    def einleitung(self):
        return f"Gegeben ist die Funktion {latex_polynomial([self.a, self.b, self.c])}."

class Produktform(Basis):
    def _erzeuge_parameter(self):
        self.x1 = random.randint(-5, 5)
        self.x2 = random.randint(-5, 5)
        while self.x1 == self.x2:
            self.x2 = random.randint(-5, 5)
        
        self.a = random.choice([-1, 1]) * random.randint(1, 3)

    def _berechne_koeffizienten(self):
        self.b = -self.a * (self.x1 + self.x2)
        self.c = self.a * self.x1 * self.x2

    def einleitung(self):
        return f"Gegeben ist die Funktion {latex_polynomial([self.a, 0, -self.a * (self.x1 + self.x2), self.a * self.x1 * self.x2])}."
