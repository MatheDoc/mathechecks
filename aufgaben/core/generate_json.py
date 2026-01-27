import json
import importlib

VARIANTEN = 20

with open("config.json") as f:
    config = json.load(f)

for export in config["exports"]:
    # Importpfad aus Config-Struktur zusammenbauen
    import_path = f"aufgaben.{export['gebiet']}.{export['lernbereich']}.{export['module']}"
    module = importlib.import_module(import_path)
    AufgabeClass = getattr(module, export["class"])
    
    # Output-Pfad aus Config-Struktur generieren
    output_path = f"export/json/{export['gebiet']}/{export['lernbereich']}/{export['module']}.json"
    
    aufgaben = []
    for i in range(VARIANTEN):
        aufgabe = AufgabeClass(i + 1)
        aufgaben.append(aufgabe.to_json())
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(aufgaben, f, ensure_ascii=False, indent=2)