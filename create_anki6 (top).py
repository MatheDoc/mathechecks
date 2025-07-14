import os
import json
import genanki
import pandas as pd
import re

# Pfade
excel_datei = 'kompetenzliste.xlsx'
json_ordner = 'json'
anki_ordner = 'anki'

# Antwortparser für gemischte MC/Numerisch
def parse_mixed_answer_text(text):
    if not isinstance(text, str):
        return text

    def repl_numerical(match):
        return match.group(1).strip()

    text = re.sub(r'\{[^{}]*?:NUMERICAL:=([\d\,\.\-]+)[^{}]*?\}', repl_numerical, text)

    def repl_mc(match):
        mc_body = match.group(1)
        correct_match = re.search(r'=(.*?)(~|$)', mc_body)
        if correct_match:
            return correct_match.group(1).strip()
        return match.group(0)

    text = re.sub(r'\{[^{}]*?:MC:(.*?)\}', repl_mc, text)
    return text

# JSON-Ladefunktion
def lade_json(pfad):
    with open(pfad, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

# Konstante Anzahl Items
ITEM_COUNT = 20

# Lernbereich optional abfragen
lernbereich_filter = input("Gib den gewünschten Lernbereich ein (leer für alle): ").strip()

# Excel einlesen und filtern
df = pd.read_excel('kompetenzliste.xlsx', dtype=str)
df = df[(df['Typ'] == 'interaktiv') & (df['Ankityp'] == 'einzeln')]

if lernbereich_filter:
    df = df[df['Lernbereich'] == lernbereich_filter]

# Struktur: (gebiet, lernbereich) → Liste von Decks
lernbereich_decks = {}

for _, zeile in df.iterrows():
    gebiet = zeile['Gebiet']
    lernbereich = zeile['Lernbereich']
    nummer = zeile['Nummer']
    sammlung = zeile['Sammlung']

    json_pfad = os.path.join(json_ordner, sammlung + '.json')
    daten = lade_json(json_pfad)

    if len(daten) != ITEM_COUNT:
        print(f"⚠️  {sammlung} hat {len(daten)} Items (nicht 20). Überspringe.")
        continue

    teilfragen_anzahl = len(daten[0]['fragen'])
    model_note_map = {}

    for teilfrage_index in range(teilfragen_anzahl):
        modelname = f'Interaktiv_Einzeln_Teilfrage_{teilfrage_index+1}'
        model_id = 1000 + teilfrage_index
        fields = [f'Item{i+1}_Frage' for i in range(ITEM_COUNT)] + [f'Item{i+1}_Antwort' for i in range(ITEM_COUNT)]

        templates = []
        for i in range(ITEM_COUNT):
            templates.append({
                'name': f'Karte_Item{i+1}',
                'qfmt': f'{{{{Item{i+1}_Frage}}}}',
                'afmt': f'{{{{Item{i+1}_Frage}}}}<hr id="answer">{{{{Item{i+1}_Antwort}}}}',
            })

        model = genanki.Model(
            model_id,
            modelname,
            fields=[{'name': f} for f in fields],
            templates=templates
        )

        note_fields = []
        for item in daten:
            einleitung = item['einleitung'].strip()
            frage = item['fragen'][teilfrage_index].strip()
            frage_parsed = parse_mixed_answer_text(frage)
            frage_feld = f'{einleitung}<br><br>{frage_parsed}'
            note_fields.append(frage_feld)

        for item in daten:
            antwort = item['antworten'][teilfrage_index].strip()
            antwort_parsed = parse_mixed_answer_text(antwort)
            note_fields.append(antwort_parsed)

        note = genanki.Note(
            model=model,
            fields=note_fields,
            guid=genanki.guid_for(sammlung + f'_Teilfrage_{teilfrage_index+1}')
        )

        if modelname not in model_note_map:
            model_note_map[modelname] = (model, [])
        model_note_map[modelname][1].append(note)

    # Check-Deck erstellen
    deck_id = 2000 + int(nummer)
    deck_name = f'MatheChecks::{gebiet}::{lernbereich}::Check{nummer}'
    deck = genanki.Deck(deck_id, deck_name)

    for model, notes in model_note_map.values():
        for note in notes:
            deck.add_note(note)

    key = (gebiet, lernbereich)
    if key not in lernbereich_decks:
        lernbereich_decks[key] = []

    lernbereich_decks[key].append(deck)

# Export pro Lernbereich
for (gebiet, lernbereich), decks in lernbereich_decks.items():
    paket = genanki.Package(decks)
    zielverzeichnis = os.path.join(anki_ordner, gebiet)
    os.makedirs(zielverzeichnis, exist_ok=True)
    zielpfad = os.path.join(zielverzeichnis, f'{lernbereich}.apkg')
    paket.write_to_file(zielpfad)
    print(f'📦 Exportiert: {zielpfad}')
