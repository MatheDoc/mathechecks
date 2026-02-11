

import shutil
import os
import json
import xml.etree.ElementTree as ET


# Ordnerpfade
json_dir = 'json'
xml_dir = 'xml'
kompetenzliste_path = 'kompetenzliste.json'

os.makedirs(xml_dir, exist_ok=True)

# Hilfsfunktion zum Erstellen einer Aufgabe-XML
def aufgabe_to_xml(aufgabe):
    html = aufgabe.get('einleitung', '')
    fragen = aufgabe.get('fragen', [])
    antworten = aufgabe.get('antworten', [])
    for i in range(max(len(fragen), len(antworten))):
        if i < len(fragen):
            html += f'<p>{fragen[i]}</p>'
        if i < len(antworten):
            html += f'<p>{antworten[i]}</p>'
    return html

# Lade die Kompetenzliste
with open(kompetenzliste_path, 'r', encoding='utf-8-sig') as f:
    kompetenzen = json.load(f)

for eintrag in kompetenzen:
    if eintrag.get('Typ') == 'statisch':
        continue
    sammlung = eintrag.get('Sammlung')
    gebiet = eintrag.get('Gebiet')
    lernbereich = eintrag.get('Lernbereich')
    nummer = eintrag.get('Nummer')
    if not (sammlung and gebiet and lernbereich and nummer):
        continue
    json_filename = f"{sammlung}.json"
    json_path = os.path.join(json_dir, json_filename)
    if not os.path.isfile(json_path):
        print(f"Warnung: {json_path} nicht gefunden, überspringe.")
        continue

    try:
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            content = f.read().strip()
            if not content:
                print(f"Warnung: {json_filename} ist leer und wird übersprungen.")
                continue

            # MC-Pattern-Check: Überspringe Datei, wenn ein MC-Pattern mit \( oder \) vorkommt
            import re
            mc_patterns = re.findall(r'\{(.*?:MC:.*?)\}', content)
            skip_due_to_mc = False
            for pattern in mc_patterns:
                if '\\(' in pattern or '\\)' in pattern:
                    print(f"Warnung: {json_filename} enthält ein MC-Pattern mit \\( oder \\) und wird übersprungen.")
                    skip_due_to_mc = True
                    break
            if skip_due_to_mc:
                continue

            data = json.loads(content)
    except Exception as e:
        print(f"Warnung: {json_filename} konnte nicht geladen werden: {e}")
        continue

    # Moodle XML Struktur
    quiz = ET.Element('quiz')

    # Kategorie-Frage
    question_cat = ET.SubElement(quiz, 'question', {'type': 'category'})
    category = ET.SubElement(question_cat, 'category')
    cat_text = ET.SubElement(category, 'text')
    cat_text.text = sammlung.replace('_', '/')
    info = ET.SubElement(question_cat, 'info', {'format': 'html'})
    ET.SubElement(info, 'text').text = ''
    ET.SubElement(question_cat, 'idnumber').text = ''

    # Aufgaben als Cloze-Fragen
    for idx, aufgabe in enumerate(data, 1):
        question = ET.SubElement(quiz, 'question', {'type': 'cloze'})
        name = ET.SubElement(question, 'name')
        ET.SubElement(name, 'text').text = f'{idx:02d} '
        questiontext = ET.SubElement(question, 'questiontext', {'format': 'html'})
        ET.SubElement(questiontext, 'text').text = f'__CDATA_PLACEHOLDER_{idx}__'

    # XML generieren
    rough_string = ET.tostring(quiz, encoding='utf-8').decode('utf-8')
    for idx, aufgabe in enumerate(data, 1):
        html = aufgabe_to_xml(aufgabe)
        cdata = f'<![CDATA[{html}]]>'
        rough_string = rough_string.replace(f'__CDATA_PLACEHOLDER_{idx}__', cdata)

    # Zielverzeichnis erzeugen
    zielverzeichnis = os.path.join(xml_dir, gebiet, lernbereich)
    os.makedirs(zielverzeichnis, exist_ok=True)
    xml_filename = f"{nummer}. Check.xml"
    xml_path = os.path.join(zielverzeichnis, xml_filename)
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write(rough_string)
    print(f"Erstellt: {xml_path}")

    # Nach dem Schreiben der XML-Datei: ZIP für den Lernbereich erzeugen
    zip_ziel = os.path.join(xml_dir, gebiet, f"{lernbereich}.zip")
    lernbereich_pfad = os.path.join(xml_dir, gebiet, lernbereich)
    # Nur erzeugen, wenn noch nicht vorhanden oder veraltet
    import time
    def zip_neu_benoetigt(zip_pfad, ordner_pfad):
        if not os.path.exists(zip_pfad):
            return True
        zip_time = os.path.getmtime(zip_pfad)
        for root, dirs, files in os.walk(ordner_pfad):
            for f in files:
                if os.path.getmtime(os.path.join(root, f)) > zip_time:
                    return True
        return False
    if zip_neu_benoetigt(zip_ziel, lernbereich_pfad):
        shutil.make_archive(base_name=zip_ziel[:-4], format='zip', root_dir=lernbereich_pfad)
        print(f"ZIP-Archiv erstellt: {zip_ziel}")
print('Konvertierung abgeschlossen.')
