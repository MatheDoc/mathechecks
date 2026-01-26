import random
from aufgabe import Aufgabe
from antwortformate import Antwortformat
from latex_utils import latex_polynomial

class QuadratischeNullstellen(Aufgabe):
    def __init__(self, nummer):
        super().__init__(nummer)

        self.x1 = random.randint(-5, 5)
        self.x2 = random.randint(-5, 5)
        while self.x2 == self.x1:
            self.x2 = random.randint(-5, 5)

        self.a = random.choice([-1, 1]) * random.randint(1, 3)

        # Koeffizienten berechnen
        self.b = -self.a * (self.x1 + self.x2)
        self.c = self.a * self.x1 * self.x2

    def einleitung(self):
        return (
            f"Gegeben ist die Funktion "
            f"{latex_polynomial([self.a, self.b, self.c])}."
        )

    def fragen(self):
        return ["Bestimmen Sie die Nullstellen von \\(f(x)\\)."]

    def antworten(self):
        return [
            Antwortformat.numerical(self.x1),
            Antwortformat.numerical(self.x2)
        ]