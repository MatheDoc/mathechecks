import os
import base64
from tkinter import filedialog, Tk
from PIL import Image
from io import BytesIO

def png_to_base64_compressed(pfad):
    """Liest ein PNG ein, komprimiert es und gibt einen Base64-String zurück."""
    img = Image.open(pfad)
    buffer = BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    return base64.b64encode(buffer.getvalue()).decode()

# Dateiauswahl über Dialog
root = Tk()
root.withdraw()
dateipfad = filedialog.askopenfilename(filetypes=[("PNG-Bilder", "*.png")])
root.destroy()

if dateipfad:
    base64_string = png_to_base64_compressed(dateipfad)
    print("Base64-String erzeugt.")

    # HTML-Tag mit eingebettetem Base64
    html_img_tag = f"<img src='data:image/png;base64,{base64_string}'>"

    # Zielpfad im selben Ordner, gleicher Name, .txt-Endung
    basisname = os.path.splitext(os.path.basename(dateipfad))[0]
    ordner = os.path.dirname(dateipfad)
    txt_pfad = os.path.join(ordner, basisname + ".txt")

    # HTML-Tag in Textdatei speichern
    with open(txt_pfad, "w", encoding="utf-8") as datei:
        datei.write(html_img_tag)

    print(f"HTML-<img>-Tag wurde in '{txt_pfad}' gespeichert.")
else:
    print("Keine Datei ausgewählt.")
