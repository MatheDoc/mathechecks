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

    result = []
    index = 0
    while index < len(text):
        start = text.find('{', index)
        if start == -1:
            result.append(text[index:])
            break

        result.append(text[index:start])

        # Prüfen, ob es ein MC-Block ist
        mc_head = text[start:start+10]
        if ":MC:" not in mc_head:
            result.append("{")
            index = start + 1
            continue

        # Klammern balancieren
        brace_level = 1
        end = start + 1
        while end < len(text) and brace_level > 0:
            if text[end] == '{':
                brace_level += 1
            elif text[end] == '}':
                brace_level -= 1
            end += 1

        full_block = text[start:end]
        # MC-Inhalt extrahieren (nach dem ":MC:")
        inner_start = full_block.find(":MC:") + 4
        inner_content = full_block[inner_start:-1]  # ohne die schließende }

        # Optionen anhand unescaped ~ trennen
        import re
        options = re.split(r'(?<!\\)~', inner_content)
        correct = next((opt[1:].strip() for opt in options if opt.strip().startswith('=')), '')

        result.append(correct)
        index = end

    return ''.join(result)


# JSON laden
def lade_json(pfad):
    with open(pfad, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

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
#lernbereich_filter = input("Gib den gewünschten Lernbereich ein (leer für alle): ").strip()
lernbereich_filter = ""
# Excel einlesen und filtern
df = pd.read_excel(excel_datei, dtype=str)

# 

# Nach Lernbereich filtern
if lernbereich_filter:
    df = df[df['Lernbereich'] == lernbereich_filter]

# Logo
logo = '<div style="background-color:#156082; color:white; text-align:center; font-size:2rem; font-weight:bold; padding: 0.5rem; margin-bottom: 1rem;"> <a href="https://www.mathechecks.de/index.html" style="color:white; text-decoration:none;">MatheChecks</a></div>'

# Gruppierung nach Lernbereich für Export
lernbereich_decks = {}

for _, zeile in df.iterrows():
    # Liste der Pflichtfelder
    pflichtfelder = ['Gebiet', 'Lernbereich', 'Nummer', 'Sammlung', 'Typ', 'Ankityp', 'LernbereichAnzeigename']
    
    # Prüfen, ob eines der Felder leer oder nur aus Leerzeichen besteht
    if any(pd.isna(zeile[f]) or str(zeile[f]).strip() == '' for f in pflichtfelder):
        print(f"⚠️  Zeile übersprungen wegen fehlender Pflichtangaben: {zeile.to_dict()}")
        continue

    gebiet = zeile['Gebiet']
    lernbereich = zeile['Lernbereich']
    nummer = zeile['Nummer']
    sammlung = zeile['Sammlung']
    typ = zeile['Typ']
    ankityp = zeile['Ankityp']
    lernbereichAnzeigename = zeile['LernbereichAnzeigename']

    head = logo + f'<h1>{lernbereichAnzeigename} {nummer}<a href="https://www.mathechecks.de/lernbereiche/{gebiet}/{lernbereich}/skript.html#check-{nummer}" style="text-decoration:none; margin-left:10px; font-size:0.8em;vertical-align:middle;" title="Info zu Check {nummer}"><span style="display:inline-block;width:22px;height:22px;border-radius:50%;background-color:#156082;color:white;text-align:center;line-height:22px;font-weight:bold;font-family:sans-serif;font-size:14px;top:-5px;">i</span></a></h1>'

    json_pfad = os.path.join(json_ordner, sammlung + '.json')
    daten = lade_json(json_pfad)
    item_count = len(daten)

    if item_count < 1:
        print(f"⚠️  {sammlung} enthält keine Items. Überspringe.")
        continue

    deck_id = 2000 + int(nummer)
    deck_name = f'MatheChecks::{gebiet}::{lernbereich}::Check{int(nummer):02d}'
    deck = genanki.Deck(deck_id, deck_name)

    kombination = f"{typ}_{ankityp}"

    if kombination == 'interaktiv_einzeln':
        teilfragen_anzahl = len(daten[0]['fragen'])
        for teilfrage_index in range(teilfragen_anzahl):
            modelname = f'Interaktiv_Einzeln_Teilfrage_{teilfrage_index+1}'
            model_id = 1000 + teilfrage_index
            fields = ['Head'] + [f'Item{i+1}_Frage' for i in range(item_count)] + [f'Item{i+1}_Antwort' for i in range(item_count)]
            templates = []
            for i in range(item_count):
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
        
    elif kombination == 'interaktiv_gruppiert':
        model_id = 3000  # Einheitlich für alle Gruppiert-Notizen
        modelname = 'Interaktiv_Gruppiert'
    
        fields = ['Head'] + [f'Item{i+1}_Frage' for i in range(item_count)] + [f'Item{i+1}_Antwort' for i in range(item_count)]
        templates = []
        for i in range(item_count):
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

    elif kombination == 'statisch_einzeln':
        model_id = 4000
        modelname = 'Statisch_Einzeln'
        model = genanki.Model(
            model_id,
            modelname,
            fields=[{'name': 'Head'}, {'name': 'Frage'}, {'name': 'Antwort'}],
            templates=[{
                'name': 'Karte',
                'qfmt': '{{Head}}<br>{{Frage}}',
                'afmt': '{{Head}}<br>{{Frage}}<hr id="answer">{{Antwort}}',
            }],
            css=css_template
        )
        for index, item in enumerate(daten):
            einleitung = item['einleitung'].strip()
            fragen = item['fragen']
            antworten = item['antworten']
            for i, (frage, antwort) in enumerate(zip(fragen, antworten)):
                frage_parsed = parse_mixed_answer_text(frage.strip())
                antwort_parsed = parse_mixed_answer_text(antwort.strip())
                note = genanki.Note(
                    model=model,
                    fields=[head, f'{einleitung}<br><br>{frage_parsed}', antwort_parsed],
                    guid=genanki.guid_for(f'{sammlung}_Item{index+1}_Frage{i+1}')
                )
                deck.add_note(note)

    elif kombination == 'statisch_gruppiert':
        model_id = 5000
        modelname = 'Statisch_Gruppiert'
        model = genanki.Model(
            model_id,
            modelname,
            fields=[{'name': 'Head'}, {'name': 'Frage'}, {'name': 'Antwort'}],
            templates=[{
                'name': 'Karte',
                'qfmt': '{{Head}}<br>{{Frage}}',
                'afmt': '{{Head}}<br>{{Frage}}<hr id="answer">{{Antwort}}',
            }],
            css=css_template
        )
        for index, item in enumerate(daten):
            einleitung = item['einleitung'].strip()
            fragen = item['fragen']
            antworten = item['antworten']
            fragen_parsed = [parse_mixed_answer_text(f.strip()) for f in fragen]
            antworten_parsed = [parse_mixed_answer_text(a.strip()) for a in antworten]
            frage_block = einleitung + '<br><br><ol>' + ''.join(f'<li>{f}</li>' for f in fragen_parsed) + '</ol>'
            antwort_block = '<ol>' + ''.join(f'<li>{a}</li>' for a in antworten_parsed) + '</ol>'
            note = genanki.Note(
                model=model,
                fields=[head, frage_block, antwort_block],
                guid=genanki.guid_for(f'{sammlung}_Item{index+1}_Gruppiert')
            )
            deck.add_note(note)
    else:
        raise ValueError(f"Unbekannte Kombination: Typ={typ}, Ankityp={ankityp}")


      
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
