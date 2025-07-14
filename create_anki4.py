import os
import json
import pandas as pd
import genanki
from pathlib import Path

EXCEL_PATH = "kompetenzliste.xlsx"
JSON_DIR = "json"
ANKI_DIR = "anki"

def get_check_metadata_from_excel():
    df = pd.read_excel(EXCEL_PATH)
    df = df[df["Typ"] == "interaktiv"]
    df = df[df["Ankityp"] == "einzeln"]
    return df

def create_note_for_question_index(question_index, items):
    model_id = 1607392319 + question_index
    fields = []
    templates = []

    for i in range(1, 21):  # 20 Items
        fields.append(f"Item{i}_Einleitung")
        fields.append(f"Item{i}_Frage")
        fields.append(f"Item{i}_Antwort")
        templates.append({
            "name": f"Karte_Item{i}",
            "qfmt": f"{{{{Item{i}_Einleitung}}}}<hr>{{{{Item{i}_Frage}}}}",
            "afmt": f"{{{{FrontSide}}}}<hr>{{{{Item{i}_Antwort}}}}"
        })

    model = genanki.Model(
        model_id,
        f"Interaktiv_Einzeln_Question{question_index + 1}",
        fields=[{"name": f} for f in fields],
        templates=templates,
        css=".card { font-family: arial; font-size: 14px; }"
    )

    note_fields = []
    for item in items:
        einleitung = item["einleitung"]
        frage = item["fragen"][question_index]
        antwort = item["antworten"][question_index]
        note_fields.extend([einleitung, frage, antwort])

    note = genanki.Note(model=model, fields=note_fields, guid=genanki.guid_for(str(question_index)))
    return note

def generate_apkg_for_check(row):
    sammlung = row["Sammlung"]
    nummer = row["Nummer"]
    lernbereich = row["Lernbereich"]
    gebiet = row["Gebiet"]

    json_path = Path(JSON_DIR) / f"{sammlung}.json"
    with open(json_path, encoding="utf-8-sig") as f:
        items = json.load(f)

    if len(items) != 20:
        raise ValueError(f"JSON-Datei '{sammlung}' enthält nicht exakt 20 Items.")

    n_teilfragen = len(items[0]["fragen"])

    deck_name = f"MatheChecks::{gebiet}::{lernbereich}::Check{nummer}"
    deck_id = abs(hash(deck_name)) % (10**10)
    deck = genanki.Deck(deck_id, deck_name)

    for i in range(n_teilfragen):
        note = create_note_for_question_index(i, items)
        deck.add_note(note)

    output_path = Path(ANKI_DIR) / gebiet / lernbereich
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / f"Check{nummer}.apkg"
    genanki.Package(deck).write_to_file(output_file)
    print(f"✅ Exportiert: {output_file}")

# Variante mit nur erstem Check (kann ersetzt werden durch Schleife)
if __name__ == "__main__":
    metadata_df = get_check_metadata_from_excel()
    if not metadata_df.empty:
        generate_apkg_for_check(metadata_df.iloc[0])
