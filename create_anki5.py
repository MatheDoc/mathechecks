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

# Filterung: interaktiv, sowohl einzeln als auch gruppiert
df = df[df['Typ'] == 'interaktiv']

if lernbereich_filter:
    df = df[df['Lernbereich'] == lernbereich_filter]

# Struktur für Export
lernbereich_decks = {}

# Logo
logo = '<div style="background-color:#156082; color:white; text-align:center; font-size:2rem; font-weight:bold; padding: 0.5rem; margin-bottom: 1rem;"> <a href="https://www.mathechecks.de/index.html" style="color:white; text-decoration:none;">MatheChecks</a></div>'

for _, zeile in df.iterrows():
    ankityp = zeile['Ankityp']
    gebiet = zeile['Gebiet']
    lernbereich = zeile['Lernbereich']
    nummer = zeile['Nummer']
    sammlung = zeile['Sammlung']
    lernbereichAnzeigename = zeile['LernbereichAnzeigename']
    head = logo + f'<h1>{lernbereichAnzeigename} {nummer}<a href="https://www.mathechecks.de/lernbereiche/{gebiet}/{lernbereich}/skript.html#check-{nummer}" style="text-decoration:none; margin-left:10px; font-size:0.8em;vertical-align:middle;" title="Info zu Check {nummer}"><span style="display:inline-block;width:22px;height:22px;border-radius:50%;background-color:#156082;color:white;text-align:center;line-height:22px;font-weight:bold;font-family:sans-serif;font-size:14px;top:-5px;">i</span></a></h1>'

    json_pfad = os.path.join(json_ordner, sammlung + '.json')
    daten = lade_json(json_pfad)

    if len(daten) != ITEM_COUNT:
        print(f"⚠️  {sammlung} hat {len(daten)} Items (nicht 20). Überspringe.")
        continue

    if ankityp == 'einzeln':
        # Gleicher Code wie bisher (siehe oben), ggf. in eine Funktion auslagern
        teilfragen_anzahl = len(daten[0]['fragen'])
        model_note_map = {}

        for teilfrage_index in range(teilfragen_anzahl):
            modelname = f'Interaktiv_Einzeln_Teilfrage_{teilfrage_index+1}'
            model_id = 1000 + teilfrage_index
            fields = ['Head'] + [f'Item{i+1}_Frage' for i in range(ITEM_COUNT)] + [f'Item{i+1}_Antwort' for i in range(ITEM_COUNT)]

            templates = []
            for i in range(ITEM_COUNT):
                templates.append({
                    'name': f'Karte_Item{i+1}',
                    'qfmt': '{{Head}}<br>{{' + f'Item{i+1}_Frage' + '}}',
                    'afmt': '{{Head}}<br>{{' + f'Item{i+1}_Frage' + '}}<hr id="answer">{{' + f'Item{i+1}_Antwort' + '}}',
                })

            model = genanki.Model(
                model_id,
                modelname,
                fields=[{'name': f} for f in fields],
                templates=templates,
                css="..."  # CSS wie bisher
            )

            note_fields = [head]

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

        deck_id = 2000 + int(nummer)
        deck_name = f'MatheChecks::{gebiet}::{lernbereich}::Check{int(nummer):02d}'
        deck = genanki.Deck(deck_id, deck_name)

        for model, notes in model_note_map.values():
            for note in notes:
                deck.add_note(note)

        key = (gebiet, lernbereich)
        if key not in lernbereich_decks:
            lernbereich_decks[key] = []

        lernbereich_decks[key].append(deck)

    elif ankityp == 'gruppiert':
        # Neue Logik: eine Note mit 20 Karten, jede Karte = 1 Item mit allen Teilfragen
        model_id = 3000 + int(nummer)
        modelname = f'Interaktiv_Gruppiert_Check_{nummer}'

        fields = ['Head'] + [f'Item{i+1}_Frage' for i in range(ITEM_COUNT)] + [f'Item{i+1}_Antwort' for i in range(ITEM_COUNT)]

        templates = []
        for i in range(ITEM_COUNT):
            templates.append({
                'name': f'Karte_Item{i+1}',
                'qfmt': '{{Head}}<br>{{' + f'Item{i+1}_Frage' + '}}',
                'afmt': '{{Head}}<br>{{' + f'Item{i+1}_Frage' + '}}<hr id="answer">{{' + f'Item{i+1}_Antwort' + '}}',
            })

        model = genanki.Model(
            model_id,
            modelname,
            fields=[{'name': f} for f in fields],
            templates=templates,
            css="..."  # Ggf. CSS übernehmen oder zentral definieren
        )

        note_fields = [head]

        for item in daten:
            einleitung = item['einleitung'].strip()
            fragen_html = ""
            antworten_html = ""

            for frage, antwort in zip(item['fragen'], item['antworten']):
                frage_html = parse_mixed_answer_text(frage.strip())
                antwort_html = parse_mixed_answer_text(antwort.strip())
                fragen_html += f'<p>{frage_html}</p>'
                antworten_html += f'<p>{antwort_html}</p>'

            frage_feld = f'{einleitung}<br><br>{fragen_html}'
            note_fields.append(frage_feld)
            note_fields.append(antworten_html)

        note = genanki.Note(
            model=model,
            fields=note_fields,
            guid=genanki.guid_for(sammlung + '_Gruppiert')
        )

        deck_id = 4000 + int(nummer)
        deck_name = f'MatheChecks::{gebiet}::{lernbereich}::Check{int(nummer):02d}'
        deck = genanki.Deck(deck_id, deck_name)
        deck.add_note(note)

        key = (gebiet, lernbereich)
        if key not in lernbereich_decks:
            lernbereich_decks[key] = []

        lernbereich_decks[key].append(deck)

# Export
for (gebiet, lernbereich), decks in lernbereich_decks.items():
    paket = genanki.Package(decks)
    zielverzeichnis = os.path.join(anki_ordner, gebiet)
    os.makedirs(zielverzeichnis, exist_ok=True)
    zielpfad = os.path.join(zielverzeichnis, f'{lernbereich}.apkg')
    paket.write_to_file(zielpfad)
    print(f'📦 Exportiert: {zielpfad}')