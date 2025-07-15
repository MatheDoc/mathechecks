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

# JSON laden
def lade_json(pfad):
    with open(pfad, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

# Konstanten
ITEM_COUNT = 20

css_template = """
.card {
    font-family: 'Arial';
    font-size: 18px;
}
h1 {
    color: #156082;
    padding: 0.5rem 0.5rem;
    margin-top: 0px;
    margin-bottom: 0px;
    text-align: center;
    font-size: 1.25rem;
}
table {
    border-collapse: collapse;
    width: 100%;
}
table, th, td {
    border: 1px solid #444;
    padding: 6px 8px;
    text-align: center;
}
ol {
    padding-left: 1.2em;
}
li {
    margin-bottom: 0.5em;
}
a span {
    cursor: pointer;
}
"""

# Lernbereichsfilter
lernbereich_filter = input("Gib den gewünschten Lernbereich ein (leer für alle): ").strip()

# Excel einlesen und filtern
df = pd.read_excel(excel_datei, dtype=str)
df = df[df['Typ'] == 'interaktiv']
if lernbereich_filter:
    df = df[df['Lernbereich'] == lernbereich_filter]

# Logo
logo = '<div style="background-color:#156082; color:white; text-align:center; font-size:2rem; font-weight:bold; padding: 0.5rem; margin-bottom: 1rem;"> <a href="https://www.mathechecks.de/index.html" style="color:white; text-decoration:none;">MatheChecks</a></div>'

# Gruppierung nach Lernbereich für Export
lernbereich_decks = {}

for _, zeile in df.iterrows():
    gebiet = zeile['Gebiet']
    lernbereich = zeile['Lernbereich']
    nummer = zeile['Nummer']
    sammlung = zeile['Sammlung']
    ankityp = zeile['Ankityp']
    lernbereichAnzeigename = zeile['LernbereichAnzeigename']

    head = logo + f'<h1>{lernbereichAnzeigename} {nummer}<a href="https://www.mathechecks.de/lernbereiche/{gebiet}/{lernbereich}/skript.html#check-{nummer}" style="text-decoration:none; margin-left:10px; font-size:0.8em;vertical-align:middle;" title="Info zu Check {nummer}"><span style="display:inline-block;width:22px;height:22px;border-radius:50%;background-color:#156082;color:white;text-align:center;line-height:22px;font-weight:bold;font-family:sans-serif;font-size:14px;top:-5px;">i</span></a></h1>'

    json_pfad = os.path.join(json_ordner, sammlung + '.json')
    daten = lade_json(json_pfad)

    if len(daten) != ITEM_COUNT:
        print(f"⚠️  {sammlung} hat {len(daten)} Items (nicht 20). Überspringe.")
        continue

    deck_id = 2000 + int(nummer)
    deck_name = f'MatheChecks::{gebiet}::{lernbereich}::Check{int(nummer):02d}'
    deck = genanki.Deck(deck_id, deck_name)

    if ankityp == 'einzeln':
        teilfragen_anzahl = len(daten[0]['fragen'])
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
            model = genanki.Model(model_id, modelname, fields=[{'name': f} for f in fields], templates=templates, css=css_template)
            note_fields = [head]
            for item in daten:
                einleitung = item['einleitung'].strip()
                frage = item['fragen'][teilfrage_index].strip()
                frage_parsed = parse_mixed_answer_text(frage)
                note_fields.append(f'{einleitung}<br><br>{frage_parsed}')
            for item in daten:
                antwort = item['antworten'][teilfrage_index].strip()
                antwort_parsed = parse_mixed_answer_text(antwort)
                note_fields.append(antwort_parsed)
            note = genanki.Note(model=model, fields=note_fields, guid=genanki.guid_for(sammlung + f'_Teilfrage_{teilfrage_index+1}'))
            deck.add_note(note)

    elif ankityp == 'gruppiert':
        model_id = 3000  # Einheitlich für alle Gruppiert-Notizen
        modelname = 'Interaktiv_Gruppiert'
        fields = ['Head'] + [f'Item{i+1}_Frage' for i in range(ITEM_COUNT)] + [f'Item{i+1}_Antwort' for i in range(ITEM_COUNT)]
        templates = []
        for i in range(ITEM_COUNT):
            templates.append({
                'name': f'Karte_Item{i+1}',
                'qfmt': '{{Head}}<br>{{' + f'Item{i+1}_Frage' + '}}',
                'afmt': '{{Head}}<br>{{' + f'Item{i+1}_Frage' + '}}<hr id="answer">{{' + f'Item{i+1}_Antwort' + '}}',
            })
        model = genanki.Model(model_id, modelname, fields=[{'name': f} for f in fields], templates=templates, css=css_template)
        note_fields = [head]
        for item in daten:
            einleitung = item['einleitung'].strip()
            fragen = item['fragen']
            fragen_parsed = [parse_mixed_answer_text(f.strip()) for f in fragen]
            frage_block = einleitung + '<br><br><ol>' + ''.join(f'<li>{f}</li>' for f in fragen_parsed) + '</ol>'
            note_fields.append(frage_block)
        for item in daten:
            antworten = item['antworten']
            antworten_parsed = [parse_mixed_answer_text(a.strip()) for a in antworten]
            antwort_block = '<ol>' + ''.join(f'<li>{a}</li>' for a in antworten_parsed) + '</ol>'
            note_fields.append(antwort_block)
        note = genanki.Note(model=model, fields=note_fields, guid=genanki.guid_for(sammlung + '_gruppiert'))
        deck.add_note(note)

    # Speichern
    key = (gebiet, lernbereich)
    if key not in lernbereich_decks:
        lernbereich_decks[key] = []
    lernbereich_decks[key].append(deck)

# Export aller Lernbereiche
for (gebiet, lernbereich), decks in lernbereich_decks.items():
    paket = genanki.Package(decks)
    zielverzeichnis = os.path.join(anki_ordner, gebiet)
    os.makedirs(zielverzeichnis, exist_ok=True)
    zielpfad = os.path.join(zielverzeichnis, f'{lernbereich}.apkg')
    paket.write_to_file(zielpfad)
    print(f'📦 Exportiert: {zielpfad}')
