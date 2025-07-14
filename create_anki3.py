import json
import genanki
import re
import os
import pandas as pd
import random # Neu importieren!

# --- Konfiguration ---
excel_file_path = 'kompetenzliste.xlsx' # Pfad zur Excel-Datei mit den Lernbereichen
base_json_dir = 'json' # Basisverzeichnis für deine JSON-Daten
output_base_dir = 'anki' # Basisverzeichnis für die erzeugten Anki-Decks
deck_name_prefix = 'MatheChecks' # Präfix für den Decknamen

# --- 1. Excel-Daten laden ---
try:
    df = pd.read_excel(excel_file_path)
except FileNotFoundError:
    print(f"Fehler: Die Excel-Datei '{excel_file_path}' wurde nicht gefunden.")
    exit()
except Exception as e:
    print(f"Fehler beim Laden der Excel-Datei: {e}")
    exit()

# --- 2. Lernbereich vom Benutzer abfragen ---
print("Verfügbare Lernbereiche (Sammlungen):")
for i, sammlung in enumerate(df['Sammlung'].unique()):
    # Überspringe NaN-Werte, die durch leere Zellen in Excel entstehen können
    if pd.isna(sammlung):
        continue
    print(f"{i+1}. {sammlung}")

selected_sammlung_name = input("\nBitte geben Sie den Namen des Lernbereichs (Sammlung) ein, für den Sie Anki-Karten erstellen möchten: ")

# Validieren der Eingabe
selected_rows = df[df['Sammlung'] == selected_sammlung_name]
if selected_rows.empty:
    print(f"Fehler: Lernbereich '{selected_sammlung_name}' wurde in der Excel-Datei nicht gefunden. Bitte überprüfen Sie die genaue Schreibweise.")
    exit()

# --- 3. Anki-Modell definieren ---
# IDs müssen Integer sein. Wir nutzen random.randrange für eine zufällige, aber konsistente ID.
# Eine gute Praxis ist, eine ID auf Basis eines Strings zu generieren, der sich nicht ändert.
# genanki.guid_for gibt einen String zurück, den wir dann in einen Integer umwandeln können.
# Ein einfacher Weg ist, hash() zu verwenden und den Absolutwert zu nehmen, um eine positive Integer-ID zu erhalten.

def generate_anki_id(text_seed):
    # Generiert eine positive Integer-ID aus einem String.
    # Wichtig: Für Konsistenz bei wiederholten Läufen sollte die Seed stabil sein.
    # genanki.guid_for liefert einen konsistenten String-Hash für denselben Input.
    # Wir nehmen den Hash des Strings, stellen sicher, dass er positiv ist, und begrenzen ihn auf 30 Bit.
    return abs(hash(text_seed)) % (1 << 30) # Anki IDs sind 30-Bit Integer (ungefähr 1 Milliarde)


# Modell für 'einzeln' (wenn Fragen aufgeteilt werden sollen)
my_single_note_model_id = generate_anki_id('Mathematik-Einzelkarte-Vorlage')
my_single_note_model = genanki.Model(
    my_single_note_model_id,
    'Mathematik-Einzelkarte-Vorlage',
    fields=[
        {'name': 'Einleitung'},
        {'name': 'Frage'},
        {'name': 'Antwort'}
    ],
    templates=[
        {
            'name': 'Einzelkarte',
            'qfmt': '{{Einleitung}}<br><br>{{Frage}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Antwort}}',
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

# Modell für 'gruppiert' (alles auf einer Karte)
my_grouped_note_model_id = generate_anki_id('Mathematik-Gruppenkarte-Vorlage')
my_grouped_note_model = genanki.Model(
    my_grouped_note_model_id,
    'Mathematik-Gruppenkarte-Vorlage',
    fields=[
        {'name': 'Einleitung'},
        {'name': 'Vorderseite_Fragen'},
        {'name': 'Rückseite_Antworten'}
    ],
    templates=[
        {
            'name': 'Gruppenkarte',
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

# --- Hilfsfunktion zum Parsen der Antwort-Strings ---
def parse_antwort_string(antwort_str):
    def ersetze_numerical(match):
        value = match.group(1).replace(',', '.')
        return f"\\({value}\\)"

    antwort_str = re.sub(r'{1:NUMERICAL:=(.*?):(.*?)}', ersetze_numerical, antwort_str)

    def ersetze_mc(match):
        korrekt = match.group(1)
        return korrekt

    antwort_str = re.sub(r'{1:MC:.*?~=(.*?)(?:~|})', ersetze_mc, antwort_str)
    return antwort_str

# --- 4. Anki-Decks erstellen und Notizen hinzufügen ---
# Eine Liste, um alle zu erstellenden Anki-Decks zu sammeln
all_anki_decks = []

# Durchlaufe die ausgewählten Zeilen für den Lernbereich
for index, row in selected_rows.iterrows():
    sammlung_value = row['Sammlung']
    nummer_value = row['Nummer']
    ankityp_value = row['Ankityp']

    # Die Werte für Gebiet und Lernbereich aus der aktuellen Zeile holen
    # Fallback für den Fall, dass die Spalten fehlen oder NaN sind
    gebiet_value_for_anki = str(row['Gebiet']) if 'Gebiet' in row and pd.notna(row['Gebiet']) else "Unbekanntes Gebiet"
    lernbereich_value_for_anki = str(row['Lernbereich']) if 'Lernbereich' in row and pd.notna(row['Lernbereich']) else "Unbekannter Lernbereich"

    # Erstelle den vollständigen Anki-Decknamen für dieses spezifische Unterdeck
    # Die "Nummer" wird jetzt Teil des Decknamens, da du für jede Nummer ein eigenes Deck/Unterdeck möchtest.
    current_anki_deck_name = f"{deck_name_prefix}::{gebiet_value_for_anki}::{lernbereich_value_for_anki}::Check{nummer_value}"
    
    # Generiere eine eindeutige ID für dieses spezifische Unterdeck
    current_deck_id = generate_anki_id(current_anki_deck_name)
    
    # Erstelle das Anki-Deck für diese spezifische "Nummer"
    current_deck = genanki.Deck(
        current_deck_id,
        current_anki_deck_name # Anki Subdeck-Struktur
    )

    json_file_name = f"{sammlung_value}.json"
    json_file_path = os.path.join(base_json_dir, json_file_name)

    print(f"Verarbeite: Nummer={nummer_value}, Sammlung='{sammlung_value}', Ankityp='{ankityp_value}'")

    # Daten aus der JSON-Datei laden
    try:
        with open(json_file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Warnung: JSON-Datei '{json_file_path}' wurde nicht gefunden und übersprungen.")
        continue
    except json.JSONDecodeError:
        print(f"Fehler: JSON-Datei '{json_file_path}' enthält ungültiges JSON und wird übersprungen.")
        continue

    # Jede Aufgabe (item) aus der JSON-Datei als Geschwisterkarte behandeln
    for task_index, item in enumerate(data): # 'data' ist eine Liste von Aufgaben
        einleitung_feld_inhalt = item.get('einleitung', '')
        fragen_list = item.get('fragen', [])
        antworten_list = item.get('antworten', [])

        if ankityp_value == 'einzeln':
            # Einzelne Karten für jede Frage generieren
            for q_idx, frage in enumerate(fragen_list):
                if q_idx < len(antworten_list): # Sicherstellen, dass eine Antwort existiert
                    antwort = antworten_list[q_idx]
                    aufbereitete_antwort = parse_antwort_string(antwort)

                    # Den Gruppennamen für Geschwisterkarten verwenden
                    card_guid = genanki.guid_for(f"{json_file_path}-{task_index}-{q_idx}") # GUID für Notiz anpassen, um einzigartig zu sein
                    
                    my_note = genanki.Note(
                        model=my_single_note_model,
                        fields=[einleitung_feld_inhalt, frage, aufbereitete_antwort],
                        guid=card_guid # Gleiche GUID für Geschwisterkarten
                    )
                    current_deck.add_note(my_note) # Füge Notiz zum aktuellen Unterdeck hinzu
                else:
                    print(f"Warnung: Frage {q_idx + 1} in Aufgabe {task_index + 1} aus '{json_file_name}' hat keine entsprechende Antwort.")

        elif ankityp_value == 'gruppiert':
            # Alle Fragen und Antworten auf einer Karte
            fragen_html = "<ol>"
            for frage in fragen_list:
                fragen_html += f"<li>{frage}</li>"
            fragen_html += "</ol>"

            antworten_html = "<ol>"
            for antwort in antworten_list:
                aufbereitete_antwort = parse_antwort_string(antwort)
                antworten_html += f"<li>{aufbereitete_antwort}</li>"
            antworten_html += "</ol>"

            card_guid = genanki.guid_for(f"{json_file_path}-{task_index}") # GUID für Gruppenkarten
            
            my_note = genanki.Note(
                model=my_grouped_note_model,
                fields=[einleitung_feld_inhalt, fragen_html, antworten_html],
                guid=card_guid # Eine GUID pro Aufgabenblock
            )
            current_deck.add_note(my_note) # Füge Notiz zum aktuellen Unterdeck hinzu
        else:
            print(f"Warnung: Unbekannter 'Ankityp' '{ankityp_value}' für Nummer {nummer_value} aus '{json_file_name}'. Überspringe.")
    
    # Füge das fertig befüllte Deck der Liste aller Decks hinzu
    if len(current_deck.notes) > 0: # Füge das Deck nur hinzu, wenn es Notizen enthält
        all_anki_decks.append(current_deck)


# --- 5. Anki-Paket speichern ---
# Die benötigten Werte für Gebiet und Lernbereich aus der ersten ausgewählten Zeile holen
# Diese werden für den Dateisystem-Pfad verwendet
# Fallback für den Fall, dass die Spalten fehlen oder NaN sind
gebiet_value_for_path = str(selected_rows['Gebiet'].iloc[0]) if 'Gebiet' in selected_rows.columns and not selected_rows.empty and pd.notna(selected_rows['Gebiet'].iloc[0]) else "unbekanntes-gebiet"
lernbereich_value_for_path = str(selected_rows['Lernbereich'].iloc[0]) if 'Lernbereich' in selected_rows.columns and not selected_rows.empty and pd.notna(selected_rows['Lernbereich'].iloc[0]) else "unbekannter-lernbereich"

# Ordnernamen Dateisystem-freundlich machen
def make_filename_safe(name):
    # Ersetzt alle Nicht-alphanumerischen Zeichen (außer Bindestrichen und Leerzeichen) durch Leerzeichen
    name = re.sub(r'[^\w\s-]', ' ', name).strip().lower()
    # Ersetzt alle Leerzeichen und Unterstriche durch einzelne Bindestriche
    name = re.sub(r'[\s_]+', '-', name)
    return name

gebiet_dir = make_filename_safe(gebiet_value_for_path)
lernbereich_dir = make_filename_safe(lernbereich_value_for_path)

# Konstruiere den vollständigen Pfad zum Unterverzeichnis
output_subdir = os.path.join(output_base_dir, gebiet_dir, lernbereich_dir)

# Erstelle die Verzeichnisse rekursiv
os.makedirs(output_subdir, exist_ok=True)

# Konstruiere den Dateinamen für die Anki-Datei
# Der Dateiname soll den ursprünglichen selected_sammlung_name verwenden,
# aber Unterstriche durch Bindestriche ersetzen und den "Check_" Präfix haben.
output_anki_file = os.path.join(output_subdir, f"Check_{selected_sammlung_name.replace('_', '-')}.apkg")

try:
    # genanki.Package kann mehrere Decks enthalten
    if all_anki_decks: # Nur speichern, wenn Decks erstellt wurden
        genanki.Package(all_anki_decks).write_to_file(output_anki_file)
        print(f"\nAnki-Paket erfolgreich erstellt: {output_anki_file}")
    else:
        print("\nKeine Notizen für den ausgewählten Lernbereich gefunden. Kein Anki-Paket erstellt.")
except Exception as e:
    print(f"Fehler beim Speichern des Anki-Pakets: {e}")