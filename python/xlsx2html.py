import pandas as pd
import json

# Pfad zur Excel-Datei
excel_datei = 'kompetenzliste.xlsx'

# Excel-Datei laden (erste Tabelle)
df = pd.read_excel(excel_datei)

# Optional: NaN-Werte durch leere Strings ersetzen
df = df.fillna('')

# In JSON umwandeln
json_struktur = df.to_dict(orient='records')  # Liste von Dictionaries

# JSON-Datei schreiben mit UTF-8-Codierung
with open('kompetenzliste.json', 'w', encoding='utf-8') as file:
    json.dump(json_struktur, file, ensure_ascii=False, indent=2)

print("Die Excel-Tabelle wurde erfolgreich in JSON umgewandelt!")
