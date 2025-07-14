import os
import json
import genanki
import pandas as pd
import re

# Pfade
excel_datei = 'kompetenzliste.xlsx'
json_ordner = 'json'
anki_ordner = 'anki'


def parse_mixed_answer_text(text):
    """
    Ersetzt alle Moodle-Antwort-Formate im Text durch die jeweils korrekte Lösung.
    Unterstützt NUMERICAL und MC gemischt im selben Text.
    """

    if not isinstance(text, str):
        return text

    # Numerische Werte ersetzen
    def repl_numerical(match):
        return match.group(1).strip()

    text = re.sub(r'\{[^{}]*?:NUMERICAL:=([\d\,\.\-]+)[^{}]*?\}', repl_numerical, text)

    # Multiple-Choice-Werte ersetzen
    def repl_mc(match):
        mc_body = match.group(1)
        correct_match = re.search(r'=(.*?)(~|$)', mc_body)
        if correct_match:
            return correct_match.group(1).strip()
        return match.group(0)  # falls kein = gefunden, Originaltext behalten

    text = re.sub(r'\{[^{}]*?:MC:(.*?)\}', repl_mc, text)

    return text


# Konstante Anzahl Items in jeder JSON
ITEM_COUNT = 20

# Hilfsfunktion: Lade JSON-Datei mit korrektem Encoding
def lade_json(pfad):
    with open(pfad, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

# Lade Excel-Tabelle mit utf-8-sig
df = pd.read_excel(excel_datei, dtype=str)

# Filter auf Typ = interaktiv & Ankityp = einzeln
df = df[(df['Typ'] == 'interaktiv') & (df['Ankityp'] == 'einzeln')]

# Iteriere über alle passenden Zeilen
for _, zeile in df.iterrows():
    gebiet = zeile['Gebiet']
    lernbereich = zeile['Lernbereich']
    nummer = zeile['Nummer']
    sammlung = zeile['Sammlung']

    json_pfad = os.path.join(json_ordner, sammlung + '.json')
    daten = lade_json(json_pfad)

    # Prüfe Konvention: exakt 20 Items
    if len(daten) != ITEM_COUNT:
        print(f"Warnung: {sammlung} hat {len(daten)} Items (nicht 20). Überspringe.")
        continue

    # Anzahl Teilfragen pro Item (angenommen konstant)
    teilfragen_anzahl = len(daten[0]['fragen'])

    # Dictionary: modelname -> (model, liste von notes)
    model_note_map = {}

    for teilfrage_index in range(teilfragen_anzahl):
        modelname = f'Interaktiv_Einzeln_Teilfrage_{teilfrage_index+1}'
        model_id = 1000 + teilfrage_index  # verschiedene IDs, aber reproduzierbar

        # Felder für 20 Items
        fields = [f'Item{i+1}_Frage' for i in range(ITEM_COUNT)] + [f'Item{i+1}_Antwort' for i in range(ITEM_COUNT)]

        # Templates
        templates = []
        for i in range(ITEM_COUNT):
            template = {
                'name': f'Karte_Item{i+1}',
                'qfmt': f'{{{{Item{i+1}_Frage}}}}',
                'afmt': f'{{{{Item{i+1}_Frage}}}}<hr id="answer">{{{{Item{i+1}_Antwort}}}}',
            }

            templates.append(template)

        model = genanki.Model(
            model_id,
            modelname,
            fields=[{'name': f} for f in fields],
            templates=templates
        )

        # Fülle die 20 Karten dieser Teilfrageposition in eine Note
        note_fields = []
        for item in daten:
            einleitung = item['einleitung'].strip()
            frage = item['fragen'][teilfrage_index].strip()
            antwort = item['antworten'][teilfrage_index].strip()

            # Parsen der Frage und Antwort auf MC- und numerische Inhalte
            frage_parsed = parse_mixed_answer_text(frage)
            antwort_parsed = parse_mixed_answer_text(antwort)

            # Zusammensetzen der Felder: Einleitung + Frage
            frage_feld = f'{einleitung}<br><br>{frage_parsed}'
            note_fields.append(frage_feld)

        # Antworten parsen und anhängen
        for item in daten:
            antwort = item['antworten'][teilfrage_index].strip()
            antwort_parsed = parse_mixed_answer_text(antwort)
            note_fields.append(antwort_parsed)

        note = genanki.Note(
            model=model,
            fields=note_fields,
            guid=genanki.guid_for(sammlung + f'_Teilfrage_{teilfrage_index+1}')
        )

        # Modell speichern (nur einmal pro Typ)
        if modelname not in model_note_map:
            model_note_map[modelname] = (model, [])

        model_note_map[modelname][1].append(note)

    # Baue das Deck
    deck_id = 2000 + int(nummer)
    deck_name = f'MatheChecks::{gebiet}::{lernbereich}::Check{nummer}'
    deck = genanki.Deck(deck_id, deck_name)

    # Alle Notes & Modelle hinzufügen
    for model, notes in model_note_map.values():
        for note in notes:
            deck.add_note(note)

    # Zielverzeichnis erstellen
    zielverzeichnis = os.path.join(anki_ordner, gebiet, lernbereich)
    os.makedirs(zielverzeichnis, exist_ok=True)
    zielpfad = os.path.join(zielverzeichnis, f'Check{nummer}.apkg')

    # Exportieren
    genanki.Package(deck).write_to_file(zielpfad)
    print(f'✔️  Exportiert: {zielpfad}')
