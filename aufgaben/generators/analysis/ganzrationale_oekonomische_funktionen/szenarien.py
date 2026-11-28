"""Szenario-Pool für ganzrationale ökonomische Funktionen.

Jedes Szenario liefert einen Einleitungssatz für das Angebotspolypol (ein Anbieter
unter vielen, Marktpreis fest) und einen für das Angebotsmonopol (alleinige
Anbieterin nach einer Neuerung, Preis frei wählbar). Die Sätze enthalten keine
Zahlen und nennen die Marktform nicht ausdrücklich: Sie soll aus dem Kontext
bzw. aus den Funktionen erkannt werden.

Einheiten bleiben abstrakt (ME, GE), wie in den Abiturprüfungen.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Szenario:
    polypol: str
    monopol: str

    def satz(self, marktform: str) -> str:
        if marktform == "polypol":
            return self.polypol
        if marktform == "monopol":
            return self.monopol
        raise ValueError(f"Unbekannte Marktform: {marktform}")


SZENARIEN: tuple[Szenario, ...] = (
    Szenario(
        polypol="Die Rösterei Bohnenwerk verkauft Espressobohnen auf einem Markt mit vielen Anbietern.",
        monopol="Die Rösterei Bohnenwerk ist alleinige Anbieterin kompostierbarer Kaffeekapseln, für die sie ein Patent hält.",
    ),
    Szenario(
        polypol="Die Velotec GmbH ist einer von vielen Herstellern von Fahrradanhängern.",
        monopol="Die Velotec GmbH bietet als einziges Unternehmen einen faltbaren Lastenanhänger mit patentierter Kupplung an.",
    ),
    Szenario(
        polypol="Die Brauerei Hopfenhof verkauft ihr Pils auf einem Markt mit zahlreichen Konkurrenten.",
        monopol="Die Brauerei Hopfenhof ist alleinige Anbieterin eines alkoholfreien Craft-Biers nach eigenem, geschütztem Verfahren.",
    ),
    Szenario(
        polypol="Die Klangwerk AG stellt Bluetooth-Lautsprecher her, die sich kaum von denen anderer Anbieter unterscheiden.",
        monopol="Die Klangwerk AG hat einen wasserdichten Lautsprecher mit patentierter Akkutechnik entwickelt und ist damit alleinige Anbieterin.",
    ),
    Szenario(
        polypol="Die Möbelmanufaktur Lindner verkauft Esstische zum üblichen Marktpreis.",
        monopol="Die Möbelmanufaktur Lindner ist mit ihrem patentierten, stufenlos ausziehbaren Esstisch alleinige Anbieterin.",
    ),
    Szenario(
        polypol="Die Agrargenossenschaft Elbtal verkauft Speisekartoffeln an den Großhandel, der Preis ergibt sich am Markt.",
        monopol="Die Agrargenossenschaft Elbtal hat eine eigene Kartoffelsorte gezüchtet und ist durch den Sortenschutz alleinige Anbieterin.",
    ),
    Szenario(
        polypol="Die Druckerei Papyrus fertigt Visitenkarten und steht dabei im Wettbewerb mit vielen Online-Druckereien.",
        monopol="Die Druckerei Papyrus bietet als Einzige Visitenkarten aus Graspapier nach einem patentierten Verfahren an.",
    ),
    Szenario(
        polypol="Die Solaris GmbH verkauft Standard-Solarmodule auf einem stark umkämpften Markt.",
        monopol="Die Solaris GmbH ist mit ihrem patentierten, biegsamen Solarmodul alleinige Anbieterin.",
    ),
    Szenario(
        polypol="Die Textilfirma Nordfaden produziert Baumwoll-T-Shirts, wie sie auch viele andere Hersteller anbieten.",
        monopol="Die Textilfirma Nordfaden ist alleinige Anbieterin von T-Shirts aus einer selbst entwickelten Algenfaser.",
    ),
    Szenario(
        polypol="Die Spielwaren GmbH Holzwurm verkauft Holzbausteine zum marktüblichen Preis.",
        monopol="Die Spielwaren GmbH Holzwurm bietet als einziges Unternehmen magnetische Holzbausteine mit patentiertem Stecksystem an.",
    ),
    Szenario(
        polypol="Die Mühle Kornblume verkauft Weizenmehl auf einem Markt mit vielen Anbietern.",
        monopol="Die Mühle Kornblume ist alleinige Anbieterin eines Mehls aus einer geschützten Urgetreidesorte.",
    ),
    Szenario(
        polypol="Die Frischwerk GmbH ist einer von vielen Herstellern von Fruchtsäften.",
        monopol="Die Frischwerk GmbH ist mit einem Saft, der nach einem patentierten Kaltverfahren haltbar gemacht wird, alleinige Anbieterin.",
    ),
)


def szenario_folge(rng: random.Random, count: int) -> list[Szenario]:
    """Liefert ``count`` Szenarien, möglichst ohne Wiederholung hintereinander."""
    folge: list[Szenario] = []
    while len(folge) < count:
        runde = list(SZENARIEN)
        rng.shuffle(runde)
        folge.extend(runde)
    return folge[:count]
