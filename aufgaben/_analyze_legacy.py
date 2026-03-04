"""Einmal-Skript: Legacy-JSONs analysieren."""
import json, os

base = "json"
files = {
    "Check1": "Stochastik_Allgemein_Methoden der Wahrscheinlichkeitsrechnung_BaumdiagrammErstellen_Var1KeineInfoUnabh.json",
    "Check2": "Stochastik_Allgemein_Methoden der Wahrscheinlichkeitsrechnung_BaumdiagrammErstellen_Var2KeineInfoUnabh.json",
    "Check3": "Stochastik_Allgemein_Methoden der Wahrscheinlichkeitsrechnung_BaumdiagrammErstellen_Var3KeineInfoUnabh.json",
    "Check4": "Stochastik_Allgemein_Methoden der Wahrscheinlichkeitsrechnung_BaumdiagrammFolgern_OhneBedingt.json",
}

for label, fn in files.items():
    fp = os.path.join(base, fn)
    if not os.path.exists(fp):
        print(f"NICHT GEFUNDEN: {fn}")
        continue
    data = json.load(open(fp, encoding="utf-8-sig"))
    print(f"\n{'='*60}")
    print(f"{label}  ({len(data)} Aufgaben)")
    print(f"{'='*60}")

    # Analyse der ersten 4 Aufgaben
    for i, task in enumerate(data[:4]):
        antw = task.get("antworten", [])
        dashes = [j+1 for j,a in enumerate(antw) if a == "---"]
        nums = [j+1 for j,a in enumerate(antw) if a != "---"]
        fragen = task.get("fragen", [])
        print(f"\n  Aufg {i+1}: dashes@{dashes}  numerical@{nums}")
        print(f"    #fragen={len(fragen)}  #antw={len(antw)}")
        # Fragen-Texte (gekürzt)
        for fi, f in enumerate(fragen):
            txt = f.replace("\n", " ")[:120]
            print(f"    F{fi+1}: {txt}")
        # Antworten
        for ai, a in enumerate(antw):
            print(f"    A{ai+1}: {a}")

    # Muster-Statistik über alle Aufgaben
    print(f"\n  --- Muster-Statistik (alle {len(data)} Aufgaben) ---")
    from collections import Counter
    patterns = Counter()
    for task in data:
        antw = task.get("antworten", [])
        dashes = tuple(j+1 for j,a in enumerate(antw) if a == "---")
        patterns[dashes] += 1
    for pat, cnt in patterns.most_common():
        print(f"    dashes@{list(pat)} : {cnt}x")
