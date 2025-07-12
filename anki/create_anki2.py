import json
import genanki
import re

# --- Konfiguration ---
json_file_path = 'ihre_daten.json'  # Pfad zur JSON-Datei
output_anki_file = 'anki_deck.apkg'
deck_name = 'Mathematik-Deck (Gesamtkarte)'

# --- 1. JSON-Daten laden ---
try:
    with open(json_file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Fehler: Die Datei '{json_file_path}' wurde nicht gefunden.")
    exit()
except json.JSONDecodeError:
    print(f"Fehler: Die Datei '{json_file_path}' enthält ungültiges JSON.")
    exit()

# --- 2. Anki-Modell definieren ---
my_model_id = 1607997999
my_model = genanki.Model(
    my_model_id,
    'Mathematik-Gesamtkarte-Vorlage',
    fields=[
        {'name': 'Einleitung'},
        {'name': 'Vorderseite_Fragen'},
        {'name': 'Rückseite_Antworten'}
    ],
    templates=[
        {
            'name': 'Gesamtkarte',
            'qfmt': '{{Einleitung}}<br><br>{{Vorderseite_Fragen}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Rückseite_Antworten}}',
        },
    ],
    css="""
        .card {
            font-family: Arial;
            font-size: 20px;
            text-align: left;
            color: black;
            background-color: white;
        }
        .math {
            font-size: 1.2em;
        }
        ol {
            margin-left: 20px;
            padding-left: 0;
        }
        li {
            margin-bottom: 8px;
        }
    """
)

# --- 3. Anki-Deck erstellen ---
my_deck_id = 2059400111
my_deck = genanki.Deck(
    my_deck_id,
    deck_name
)

# --- Hilfsfunktion zum Parsen der Antwort-Strings ---
def parse_antwort_string(antwort_str):
    """
    Diese Funktion ersetzt bekannte Antwortformate durch saubere MathJax-Darstellungen.
    Unterstützt mehrfaches Auftreten von {1:NUMERICAL:=...:...} im String.
    """

    # Mehrfaches Ersetzen von NUMERICAL-Blöcken
    def ersetze_numerical(match):
        value = match.group(1).replace(',', '.')
        return f"\\({value}\\)"

    antwort_str = re.sub(r'{1:NUMERICAL:=(.*?):(.*?)}', ersetze_numerical, antwort_str)

    # Optional: Ersetzen von einfachen MC-Formaten (erste richtige Antwort anzeigen)
    def ersetze_mc(match):
        korrekt = match.group(1)
        return korrekt

    antwort_str = re.sub(r'{1:MC:.*?~=(.*?)(?:~|})', ersetze_mc, antwort_str)

    return antwort_str

# --- 4. Notizen hinzufügen ---
for item_index, item in enumerate(data):
    einleitung_feld_inhalt = item.get('einleitung', '')

    fragen_list = item.get('fragen', [])
    antworten_list = item.get('antworten', [])

    # Fragen zusammenstellen
    fragen_html = "<ol>"
    for frage in fragen_list:
        fragen_html += f"<li>{frage}</li>"
    fragen_html += "</ol>"

    # Antworten zusammenstellen
    antworten_html = "<ol>"
    for antwort in antworten_list:
        aufbereitete_antwort = parse_antwort_string(antwort)
        antworten_html += f"<li>{aufbereitete_antwort}</li>"
    antworten_html += "</ol>"

    try:
        my_note = genanki.Note(
            model=my_model,
            fields=[einleitung_feld_inhalt, fragen_html, antworten_html]
        )
        my_deck.add_note(my_note)
    except Exception as e:
        print(f"Ein Fehler bei Eintrag {item_index + 1}: {e}")

# --- 5. Anki-Paket speichern ---
try:
    genanki.Package(my_deck).write_to_file(output_anki_file)
    print(f"Anki-Deck erfolgreich erstellt: {output_anki_file}")
except Exception as e:
    print(f"Fehler beim Speichern des Anki-Decks: {e}")
