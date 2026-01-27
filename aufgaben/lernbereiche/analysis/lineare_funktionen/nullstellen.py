import random
from aufgaben.core.aufgabe import Aufgabe
from aufgaben.core.antwortformate import Antwortformat
from aufgaben.utils.latex_utils import latex_polynomial

class LineareNullstelle(Aufgabe):
    def __init__(self, nummer):
        super().__init__(nummer)
        self.a = random.randint(1,9) * random.choice([-1,1])
        self.b = random.randint(-9, 9)

    def einleitung(self):
        return f"Gegeben ist die Funktion {latex_polynomial([self.a, self.b])}."

    def fragen(self):
        return ["Bestimmen Sie die Nullstelle von \\(f(x)\\)."]

    def antworten(self):
        x0 = -self.b / self.a
        return [Antwortformat.numerical(x0)]