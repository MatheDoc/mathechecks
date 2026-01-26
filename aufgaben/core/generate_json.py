import json
from analysis import LineareNullstelle

aufgaben = []
nummer = 1

for _ in range(20):
    aufgabe = LineareNullstelle(nummer)
    aufgaben.append(aufgabe.to_json())
    nummer += 1

with open("aufgaben-erstellung/core/aufgaben.json", "w", encoding="utf-8") as f:
    json.dump(aufgaben, f, ensure_ascii=False, indent=2)