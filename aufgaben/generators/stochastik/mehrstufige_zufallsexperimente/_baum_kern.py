"""Kern für komplexe Baumdiagramme: Struktur, Löser, Struktur-Mutationen.

Baumstruktur
    Ein Knoten wird über seinen Pfad adressiert: das Tupel der Labels von der
    Wurzel (exklusive) bis zum Knoten, z. B. ("B", "V"). Die Wurzel ist ().
    Kurzschreibweise zum Anlegen: ``Baum.parse("B(R V) F(H K) Z")``.

Löser
    Unbekannte sind die Kantenwerte e[p] (Wahrscheinlichkeit der Kante zum
    Knoten p) und die Knotenwerte q[p] (Pfadwahrscheinlichkeit bis p, q[()] = 1).
    Regeln, jede liefert genau eine fehlende Größe:
      knotensumme    Kanten an einem Knoten summieren sich zu 1
      multiplikation q[p] = q[Eltern] * e[p]               (vorwärts)
      division       e[p] = q[p] / q[Eltern] bzw. q[Eltern] = q[p] / e[p]
      pfadaddition   q[p] = Summe der q[Kinder]
      summe          gegebene Summe von Pfadwahrscheinlichkeiten
      gesamtsumme    alle Pfadwahrscheinlichkeiten summieren sich zu 1
    Division wird nur genutzt, wenn keine andere Regel weiterhilft. So zählt der
    Löser nur die Rückwärtsschritte, die wirklich nötig sind.

Mutationen
    Strukturell falsche Bäume für die Baumwahl (nie nur vertauschte Stufen).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

Pfad = tuple[str, ...]


# ---------------------------------------------------------------------------
# Baumstruktur
# ---------------------------------------------------------------------------

class Baum:
    """Unbeschriftete Baumstruktur (nur Ereignis-Labels, keine Werte)."""

    def __init__(self, kinder: dict[Pfad, list[Pfad]]):
        self._kinder = kinder

    # -- Anlegen ------------------------------------------------------------

    @classmethod
    def parse(cls, text: str) -> "Baum":
        """Liest die Kurzschreibweise, z. B. ``"B(R V) F(H K) Z"``."""
        tokens = text.replace("(", " ( ").replace(")", " ) ").split()
        kinder: dict[Pfad, list[Pfad]] = {(): []}
        stack: list[Pfad] = [()]
        letzter: Pfad | None = None
        for tok in tokens:
            if tok == "(":
                if letzter is None:
                    raise ValueError(f"'(' ohne Knoten in {text!r}")
                stack.append(letzter)
            elif tok == ")":
                stack.pop()
                if not stack:
                    raise ValueError(f"Klammerfehler in {text!r}")
            else:
                eltern = stack[-1]
                pfad = eltern + (tok,)
                kinder[eltern].append(pfad)
                kinder[pfad] = []
                letzter = pfad
        if len(stack) != 1:
            raise ValueError(f"Klammerfehler in {text!r}")
        return cls(kinder)

    def kopie(self) -> "Baum":
        return Baum({p: list(k) for p, k in self._kinder.items()})

    # -- Abfragen -----------------------------------------------------------

    def kinder(self, pfad: Pfad) -> list[Pfad]:
        return self._kinder[pfad]

    def knoten(self) -> list[Pfad]:
        """Alle Knoten außer der Wurzel, in Präordnung."""
        out: list[Pfad] = []

        def rek(p: Pfad) -> None:
            for k in self._kinder[p]:
                out.append(k)
                rek(k)

        rek(())
        return out

    def innere(self) -> list[Pfad]:
        """Alle Knoten mit Kindern, inklusive Wurzel."""
        return [()] + [p for p in self.knoten() if self._kinder[p]]

    def blaetter(self) -> list[Pfad]:
        return [p for p in self.knoten() if not self._kinder[p]]

    def ist_blatt(self, pfad: Pfad) -> bool:
        return not self._kinder[pfad]

    def tiefe(self) -> int:
        return max(len(p) for p in self.blaetter())

    def freiheitsgrade(self) -> int:
        """Anzahl unabhängiger Kantenwerte = benötigte Angaben."""
        return sum(len(self._kinder[p]) - 1 for p in self.innere())

    def labels(self) -> set[str]:
        return {p[-1] for p in self.knoten()}

    # -- Ausgabe ------------------------------------------------------------

    def kanon(self, pfad: Pfad = ()) -> tuple:
        """Vergleichsform: Reihenfolge der Geschwister spielt keine Rolle."""
        return tuple(sorted((k[-1], self.kanon(k)) for k in self._kinder[pfad]))

    def to_spec(self, pfad: Pfad = ()) -> dict:
        """Verschachteltes JSON-Format für das Visual."""
        out: dict = {}
        if pfad:
            out["label"] = pfad[-1]
        kinder = [self.to_spec(k) for k in self._kinder[pfad]]
        if kinder:
            out["children"] = kinder
        return out

    def kurz(self, pfad: Pfad = ()) -> str:
        teile = []
        for k in self._kinder[pfad]:
            if self._kinder[k]:
                teile.append(f"{k[-1]}({self.kurz(k)})")
            else:
                teile.append(k[-1])
        return " ".join(teile)

    # -- Ändern (für Mutationen) ---------------------------------------------

    def _entferne_teilbaum(self, pfad: Pfad) -> None:
        for k in list(self._kinder[pfad]):
            self._entferne_teilbaum(k)
        del self._kinder[pfad]

    def _setze_kinder_wie(self, ziel: Pfad, vorlage: Pfad) -> None:
        """Ersetzt die Teilbäume unter ziel durch eine Kopie der unter vorlage."""
        for k in list(self._kinder[ziel]):
            self._entferne_teilbaum(k)
        self._kinder[ziel] = []

        def kopiere(von: Pfad, nach: Pfad) -> None:
            for k in self._kinder_snapshot[von]:
                neu = nach + (k[-1],)
                self._kinder[nach].append(neu)
                self._kinder[neu] = []
                kopiere(k, neu)

        kopiere(vorlage, ziel)


# ---------------------------------------------------------------------------
# Mutationen
# ---------------------------------------------------------------------------

def _mit_snapshot(baum: Baum) -> Baum:
    neu = baum.kopie()
    neu._kinder_snapshot = baum.kopie()._kinder  # type: ignore[attr-defined]
    return neu


def mutationen(baum: Baum) -> list[tuple[str, Baum]]:
    """Alle einfachen, strukturell falschen Abwandlungen von baum.

    Arten:
      fortsetzen  ein endender Pfad bekommt die Verzweigung desselben Ereignisses
                  aus einem anderen Ast oder die eines Geschwisters
      kappen      ein verzweigender Knoten endet
      angleichen  alle Knoten einer Stufe bekommen dieselbe Verzweigung
      tauschen    zwei Geschwister tauschen ihre Verzweigungen
      weglassen   ein Ausgang an einem Knoten mit drei Ästen fehlt
    """
    out: list[tuple[str, Baum]] = []
    knoten = baum.knoten()
    nach_tiefe: dict[int, list[Pfad]] = {}
    for p in knoten:
        nach_tiefe.setdefault(len(p), []).append(p)

    # fortsetzen: Blatt erhält Verzweigung eines Knotens gleicher Tiefe
    for p in baum.blaetter():
        vorlagen = [v for v in nach_tiefe[len(p)] if v != p and baum.kinder(v)]
        # bevorzugt dasselbe Ereignis aus einem anderen Ast, dann ein Geschwister
        gleich = [v for v in vorlagen if v[-1] == p[-1]]
        geschwister = [v for v in vorlagen if v[:-1] == p[:-1]]
        for v in (gleich or geschwister)[:1]:
            neu = _mit_snapshot(baum)
            neu._setze_kinder_wie(p, v)
            out.append(("fortsetzen", neu))

    # kappen: innerer Knoten (nicht Wurzel) endet
    for p in knoten:
        if baum.kinder(p):
            neu = baum.kopie()
            for k in list(neu.kinder(p)):
                neu._entferne_teilbaum(k)
            neu._kinder[p] = []
            out.append(("kappen", neu))

    # angleichen: verschiedene Verzweigungen auf einer Stufe vereinheitlichen
    for tiefe, ps in nach_tiefe.items():
        verzweigt = [p for p in ps if baum.kinder(p)]
        formen = {baum.kanon(p) for p in verzweigt}
        if len(formen) < 2:
            continue
        for vorlage in verzweigt:
            neu = _mit_snapshot(baum)
            for p in ps:
                if p != vorlage:
                    neu._setze_kinder_wie(p, vorlage)
            out.append(("angleichen", neu))

    # tauschen: zwei verzweigende Geschwister mit verschiedener Verzweigung
    for p in baum.innere():
        ks = [k for k in baum.kinder(p) if baum.kinder(k)]
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                a, b = ks[i], ks[j]
                if baum.kanon(a) == baum.kanon(b):
                    continue
                neu = _mit_snapshot(baum)
                neu._setze_kinder_wie(a, b)
                neu._setze_kinder_wie(b, a)
                out.append(("tauschen", neu))

    # weglassen: Ausgang an einem Knoten mit drei Ästen fehlt
    for p in baum.innere():
        if len(baum.kinder(p)) >= 3:
            for k in baum.kinder(p):
                neu = baum.kopie()
                neu._entferne_teilbaum(k)
                neu._kinder[p] = [x for x in neu._kinder[p] if x != k]
                out.append(("weglassen", neu))

    # Duplikate und Bäume gleich dem Original entfernen
    gesehen = {baum.kanon()}
    eindeutig: list[tuple[str, Baum]] = []
    for art, b in out:
        k = b.kanon()
        if k in gesehen:
            continue
        gesehen.add(k)
        eindeutig.append((art, b))
    return eindeutig


# ---------------------------------------------------------------------------
# Angaben und Löser
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Angabe:
    """Eine Angabe im Sachtext.

    art:
      kante   Wert der Kante zu ziel[0] (bei Stufe 1 zugleich Anteil der Gruppe)
      knoten  Pfadwahrscheinlichkeit bis ziel[0] (Tiefe >= 2), meist Pfadende
      summe   Summe der Pfadwahrscheinlichkeiten aller Blätter in ziel
    darstellung: prozent | bruch | absolut
    """
    art: str
    ziel: tuple[Pfad, ...]
    wert: Fraction
    darstellung: str


@dataclass
class Schritt:
    regel: str
    groesse: tuple[str, Pfad]  # ("e", pfad) oder ("q", pfad)
    wert: Fraction


@dataclass
class Loesung:
    vollstaendig: bool
    werte: dict[tuple[str, Pfad], Fraction]
    schritte: list[Schritt] = field(default_factory=list)

    @property
    def rueckwaerts(self) -> int:
        return sum(1 for s in self.schritte if s.regel == "division")


def wahre_werte(baum: Baum, kanten: dict[Pfad, Fraction]) -> dict[tuple[str, Pfad], Fraction]:
    """Alle e- und q-Werte aus den Kantenwerten."""
    werte: dict[tuple[str, Pfad], Fraction] = {("q", ()): Fraction(1)}
    for p in baum.knoten():
        werte[("e", p)] = kanten[p]
        werte[("q", p)] = werte[("q", p[:-1])] * kanten[p]
    return werte


def loese(baum: Baum, angaben: list[Angabe], ereignisse: list[tuple[Pfad, ...]] = ()) -> Loesung:
    """Füllt den Baum schrittweise aus den Angaben."""
    bekannt: dict[tuple[str, Pfad], Fraction] = {("q", ()): Fraction(1)}
    for a in angaben:
        if a.art == "kante":
            bekannt[("e", a.ziel[0])] = a.wert
            if len(a.ziel[0]) == 1:
                bekannt[("q", a.ziel[0])] = a.wert
        elif a.art == "knoten":
            bekannt[("q", a.ziel[0])] = a.wert

    # Lineare Gleichungen: (regel, [(koeffizient, groesse)], rechte Seite)
    linear: list[tuple[str, list[tuple[int, tuple[str, Pfad]]], Fraction]] = []
    for p in baum.innere():
        ks = baum.kinder(p)
        linear.append(("knotensumme", [(1, ("e", k)) for k in ks], Fraction(1)))
        if p:
            linear.append(("pfadaddition", [(1, ("q", k)) for k in ks] + [(-1, ("q", p))], Fraction(0)))
    for p in baum.knoten():
        if len(p) == 1:
            # Stufe 1: Kantenwert = Pfadwahrscheinlichkeit
            linear.append(("multiplikation", [(1, ("q", p)), (-1, ("e", p))], Fraction(0)))
    linear.append(("gesamtsumme", [(1, ("q", b)) for b in baum.blaetter()], Fraction(1)))
    for a in angaben:
        if a.art == "summe":
            linear.append(("summe", [(1, ("q", b)) for b in a.ziel], a.wert))

    schritte: list[Schritt] = []

    def setze(regel: str, g: tuple[str, Pfad], w: Fraction) -> None:
        bekannt[g] = w
        schritte.append(Schritt(regel, g, w))

    tief = [p for p in baum.knoten() if len(p) >= 2]
    while True:
        fortschritt = False
        for regel, terme, rhs in linear:
            offen = [(c, g) for c, g in terme if g not in bekannt]
            if len(offen) == 1:
                c, g = offen[0]
                rest = sum((c2 * bekannt[g2] for c2, g2 in terme if g2 in bekannt), Fraction(0))
                setze(regel, g, (rhs - rest) / c)
                fortschritt = True
        for p in tief:
            e, q, qe = ("e", p), ("q", p), ("q", p[:-1])
            if e in bekannt and qe in bekannt and q not in bekannt:
                setze("multiplikation", q, bekannt[qe] * bekannt[e])
                fortschritt = True
        if fortschritt:
            continue
        # Nur wenn nichts anderes geht: ein Divisionsschritt
        for p in tief:
            e, q, qe = ("e", p), ("q", p), ("q", p[:-1])
            if q in bekannt and qe in bekannt and e not in bekannt:
                setze("division", e, bekannt[q] / bekannt[qe])
                fortschritt = True
                break
            if q in bekannt and e in bekannt and qe not in bekannt:
                setze("division", qe, bekannt[q] / bekannt[e])
                fortschritt = True
                break
        if not fortschritt:
            break

    alle = [("e", p) for p in baum.knoten()] + [("q", p) for p in baum.knoten()]
    vollstaendig = all(g in bekannt for g in alle)
    return Loesung(vollstaendig, bekannt, schritte)


def hat_hoechstens_dezimalen(wert: Fraction, stellen: int = 4) -> bool:
    return (wert * 10 ** stellen).denominator == 1
