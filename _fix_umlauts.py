"""Replace ASCII umlaut approximations with proper German umlauts in dev_einstieg.yml."""
import re

path = '_data/dev_einstieg.yml'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Word-level replacements (longest first to avoid partial matches)
replacements = {
    'Qualitaetskontrollen': 'Qualitätskontrollen',
    'Qualitaetskontrolle': 'Qualitätskontrolle',
    'Ueberschussnachfrage': 'Überschussnachfrage',
    'Schluesseleigenschaft': 'Schlüsseleigenschaft',
    'Einfuehrungsphase': 'Einführungsphase',
    'Rueckgangsphase': 'Rückgangsphase',
    'zusammengefuegt': 'zusammengefügt',
    'gleichmaessig': 'gleichmäßig',
    'glockenfoermigen': 'glockenförmigen',
    'Zufallsgroessen': 'Zufallsgrößen',
    'Zufallsgroesse': 'Zufallsgröße',
    'Elastizitaeten': 'Elastizitäten',
    'Aenderungsraten': 'Änderungsraten',
    'Aenderungsrate': 'Änderungsrate',
    'urspruenglich': 'ursprünglich',
    'zuverlaessig': 'zuverlässig',
    'ueberpruefen': 'überprüfen',
    'Ueberraschend': 'Überraschend',
    'ueberraschende': 'überraschende',
    'Moeglichkeiten': 'Möglichkeiten',
    'Grundgebuehr': 'Grundgebühr',
    'einschaetzen': 'einschätzen',
    'uebersteigen': 'übersteigen',
    'S-foermigen': 'S-förmigen',
    'Einfuehrung': 'Einführung',
    'ueberprueft': 'überprüft',
    'ueberlagert': 'überlagert',
    'Schaetzfrage': 'Schätzfrage',
    'aufgewaermt': 'aufgewärmt',
    'auszuloesen': 'auszulösen',
    'uebersetzen': 'übersetzen',
    'Elastizitaet': 'Elastizität',
    'puenktlich': 'pünktlich',
    'Hoehepunkt': 'Höhepunkt',
    'Stueckzahl': 'Stückzahl',
    'moeglichen': 'möglichen',
    'verknuepft': 'verknüpft',
    'Verkaeufer': 'Verkäufer',
    'Herzstueck': 'Herzstück',
    'Gluecksrad': 'Glücksrad',
    'veraendern': 'verändern',
    'Schluessel': 'Schlüssel',
    'gewuenschte': 'gewünschte',
    'Eintraegen': 'Einträgen',
    'Rueckgang': 'Rückgang',
    'Broetchen': 'Brötchen',
    'Baeckerei': 'Bäckerei',
    'naechsten': 'nächsten',
    'ungefaehr': 'ungefähr',
    'groesser': 'größer',
    'moegliche': 'mögliche',
    'hoeheren': 'höheren',
    'foermigen': 'förmigen',
    'moeglich': 'möglich',
    'taeglich': 'täglich',
    'Beitraege': 'Beiträge',
    'Loesungen': 'Lösungen',
    'Ertraege': 'Erträge',
    'Ausstoss': 'Ausstoß',
    'Realitaet': 'Realität',
    'Kaeufer': 'Käufer',
    'Wuerfels': 'Würfels',
    'klaeren': 'klären',
    'Duenger': 'Dünger',
    'laenger': 'länger',
    'Loesung': 'Lösung',
    'fuehren': 'führen',
    'Wuerfel': 'Würfel',
    'haeufig': 'häufig',
    'Erloese': 'Erlöse',
    'Stueck': 'Stück',
    'Woerter': 'Wörter',
    'aendert': 'ändert',
    'rueckst': 'rückst',
    'ueberall': 'überall',
    'Faelle': 'Fälle',
    'Muenze': 'Münze',
    'pruefen': 'prüfen',
    'prueft': 'prüft',
    'loesen': 'lösen',
    'ausloest': 'auslöst',
    'haengt': 'hängt',
    'raetst': 'rätst',
    'faellt': 'fällt',
    'faehrt': 'fährt',
    'zaehlt': 'zählt',
    'laesst': 'lässt',
    'loest': 'löst',
    'Unmoeglich': 'Unmöglich',
    'Haelfte': 'Hälfte',
    'enthaelt': 'enthält',
    'dafuer': 'dafür',
    'Ueber ': 'Über ',
    'ueber ': 'über ',
    'fuer ': 'für ',
    'Fuer ': 'Für ',
    # Second pass additions
    'zusaetzlichen': 'zusätzlichen',
    'S-foermige': 'S-förmige',
    'traegt': 'trägt',
    'Umsaetze': 'Umsätze',
    'hoechsten': 'höchsten',
    'Produktverlaeufe': 'Produktverläufe',
    'koennen': 'können',
    'moechte': 'möchte',
    'Erloes ': 'Erlös ',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Check for remaining ASCII-umlaut candidates in quoted strings
remaining = []
for line_no, line in enumerate(content.splitlines(), 1):
    # Skip comment lines and typ: lines
    stripped = line.strip()
    if stripped.startswith('#') or stripped.startswith('typ:'):
        continue
    # Look for ue/oe/ae patterns in text content
    for m in re.finditer(r'[a-zäöü](ue|oe|ae)[a-zäöü]', line, re.IGNORECASE):
        remaining.append(f"  L{line_no}: ...{line[max(0,m.start()-10):m.end()+10]}...")

print(f"Fertig! Ersetzungen durchgeführt.")
if remaining:
    print(f"Verbleibende Stellen ({len(remaining)}):")
    for r in remaining:
        print(r)
else:
    print("Keine verbleibenden ue/oe/ae-Stellen in Texten gefunden.")
