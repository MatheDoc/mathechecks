import json
import numpy as np

# --- Hilfsfunktionen für Regressionen ---
def lineare_regression(x, y):
    """Führt eine lineare Regression durch und gibt die Koeffizienten zurück."""
    coeffs = np.polyfit(x, y, 1)
    return coeffs

def quadratische_regression(x, y):
    """Führt eine quadratische Regression durch und gibt die Koeffizienten zurück."""
    coeffs = np.polyfit(x, y, 2)
    return coeffs

def kubische_regression(x, y):
    """Führt eine kubische Regression durch und gibt die Koeffizienten zurück."""
    coeffs = np.polyfit(x, y, 3)
    return coeffs

def exponentielle_regression(x, y):
    """
    Führt eine exponentielle Regression durch, indem das Modell
    ln(y) = ln(a) + b*x linearisiert wird.
    """
    # y-Werte müssen positiv sein für den Logarithmus
    y = np.where(y <= 0, 1e-8, y)
    log_y = np.log(y)
    # Linearer Fit: ln(y) = ln(a) + b*x
    b, log_a = np.polyfit(x, log_y, 1)
    a = np.exp(log_a)
    return a, b

# --- R² berechnen ---
def berechne_r2(y_actual, y_predicted):
    """
    Berechnet das Bestimmtheitsmaß R^2.
    y_actual: Tatsächliche y-Werte
    y_predicted: Vorhergesagte y-Werte
    """
    ss_res = np.sum((y_actual - y_predicted) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
    if ss_tot == 0:
        return 0
    return 1 - ss_res / ss_tot

# --- HTML-Tabelle ---
def make_table(x_vals, y_vals):
    """Erstellt eine HTML-Tabelle aus x- und y-Werten."""
    header = "    <tr><td>\\( x \\)</td>" + "".join(f"<td>\\( {xi:.2f} \\)</td>" for xi in x_vals) + "</tr>"
    row = "    <tr><td>\\( y \\)</td>" + "".join(f"<td>\\( {yi:.2f} \\)</td>" for yi in y_vals) + "</tr>"
    return f"<table class=\"TabelleEinleitung\">\n{header}\n{row}\n</table>"

# --- Antwortformat ---
def format_answer(coeffs, typ, r2):
    """
    Formatiert die Antwort-Zeichenkette mit Platzhaltern
    für ein automatisches Bewertungssystem.
    """
    if typ == "linear":
        eq = f"\\( y = \\){{1:NUMERICAL:={coeffs[0]:.2f}:0.01}}\\( x + \\){{1:NUMERICAL:={coeffs[1]:.2f}:0.01}}"
    elif typ == "quadratisch":
        eq = (f"\\( y = \\){{1:NUMERICAL:={coeffs[0]:.2f}:0.01}}\\( x^2 + \\)"
              f"{{1:NUMERICAL:={coeffs[1]:.2f}:0.01}}\\( x + \\)"
              f"{{1:NUMERICAL:={coeffs[2]:.2f}:0.01}}")
    elif typ == "kubisch":
        eq = (f"\\( y = \\){{1:NUMERICAL:={coeffs[0]:.2f}:0.01}}\\( x^3 + \\)"
              f"{{1:NUMERICAL:={coeffs[1]:.2f}:0.01}}\\( x^2 + \\)"
              f"{{1:NUMERICAL:={coeffs[2]:.2f}:0.01}}\\( x + \\)"
              f"{{1:NUMERICAL:={coeffs[3]:.2f}:0.01}}")
    elif typ == "exponentiell":
        eq = (f"\\( y = \\){{1:NUMERICAL:={coeffs[0]:.2f}:0.01}}"
              f"\\( \\cdot exp( \\){{1:NUMERICAL:={coeffs[1]:.2f}:0.01}}\\( x) \\)")
    else:
        eq = ""
    r2_part = f"</p> <p>\\( R^2 = \\){{1:NUMERICAL:={r2:.3f}:0.001}}"
    return eq + r2_part

# --- Hauptskript ---
arten = ["linear", "quadratisch", "kubisch", "exponentiell"]
aufgaben = []
aufgaben_nummer = 1

for art in arten:
    for i in range(5):  # je 5 Aufgaben pro Typ
        # x-Werte zufällig aufsteigend
        x_vals = np.sort(np.random.choice(np.arange(1, 21), size=5, replace=False))
        
        # y-Werte und R²-Berechnung basierend auf dem Regressionstyp
        if art == "linear":
            y_vals = 2 * x_vals + 3 + np.random.normal(0, 3, size=5)
            coeffs = lineare_regression(x_vals, y_vals)
            y_predicted = np.polyval(coeffs, x_vals)
            r2 = berechne_r2(y_vals, y_predicted)
        elif art == "quadratisch":
            y_vals = 1 * x_vals**2 - 2 * x_vals + 5 + np.random.normal(0, 5, size=5)
            coeffs = quadratische_regression(x_vals, y_vals)
            y_predicted = np.polyval(coeffs, x_vals)
            r2 = berechne_r2(y_vals, y_predicted)
        elif art == "kubisch":
            y_vals = -0.5 * x_vals**3 + 2 * x_vals**2 - x_vals + 4 + np.random.normal(0, 7, size=5)
            coeffs = kubische_regression(x_vals, y_vals)
            y_predicted = np.polyval(coeffs, x_vals)
            r2 = berechne_r2(y_vals, y_predicted)
        else:  # exponentiell
            # Generieren der linearen Koeffizienten zuerst
            b = np.random.uniform(0.05, 0.4)
            log_a = np.random.uniform(0.5, 2)
            
            # y-Werte basierend auf den Koeffizienten mit Rauschen erzeugen
            # ln(y) = log_a + b*x + Rauschen
            log_y = log_a + b * x_vals + np.random.normal(0, 0.2, size=5)
            y_vals = np.exp(log_y)
            
            # Rückwärtsrechnung, um die Koeffizienten zu finden (sollte sehr genau sein)
            b_reg, log_a_reg = np.polyfit(x_vals, log_y, 1)
            coeffs = np.exp(log_a_reg), b_reg
            
            # R² auf dem linearisierten Modell (ln(y) vs. x) berechnen
            y_predicted_log = log_a_reg + b_reg * x_vals
            r2 = berechne_r2(log_y, y_predicted_log)

        # Antwort
        antwort = format_answer(coeffs, art, r2)

        # HTML-Tabelle
        tabelle = make_table(x_vals, y_vals)

        # JSON-Eintrag
        aufgabe = {
            "titel": f"Aufgabe {aufgaben_nummer}",
            "einleitung": f"Gegeben sind die folgenden Wertepaare:{tabelle}",
            "fragen": [
                f"Bestimmen Sie die {art}e Regressionsfunktion und das Bestimmtheitsmaß \\( R^2 \\)."
            ],
            "antworten": [
                antwort
            ]
        }
        aufgaben.append(aufgabe)
        aufgaben_nummer += 1

# JSON speichern
with open("json/analysis_regression.json", "w", encoding="utf-8") as f:
    json.dump(aufgaben, f, ensure_ascii=False, indent=2)

print("Datei 'analysis_regression.json' erstellt.")