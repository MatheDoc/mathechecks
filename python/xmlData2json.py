import os
import json

# Pfad zu deinem xml-Ordner
xml_ordner = "xml"
dateien = [f for f in os.listdir(xml_ordner) if f.endswith(".xml")]

# JSON speichern
with open(os.path.join(xml_ordner, "xml-liste.json"), "w", encoding="utf-8") as f:
    json.dump(dateien, f, indent=2, ensure_ascii=False)

print("xml-liste.json wurde erstellt.")
