# Tipps in checks.json

## Allgemeines

Tipps sind kurze Hinweise, die den Lernenden beim Bearbeiten und Verständnis eines Checks unterstützen. Sie können inhaltlicher oder prozessualer Natur sein. Inhaltliche Tipps geben Hinweise auf mathematische Zusammenhänge, Formeln oder Regeln. Prozessuale Tipps geben Hinweise auf den Lösungsweg.

## Technischer Aufbau

Jeder Check aus `checks.json` muss die Felder `Tipps` und `tippOrder` enthalten. Ein Tipp muss die Felder `cue` und `response` enthalten. `tippOrder` hat den Wert `shuffle` oder `fixed`.

- Die Anzahl der Tipps pro Check liegt typischerweise bei 2–4, ist aber keine harte Bedingung.
- `cue` und `response` dürfen nicht leer sein.

## Inhaltlicher Aufbau

Typische Formen einzelner Tipps mit Beispielen:

### Formeln

`cue`: Bezeichnung der Formel, `response`: konkrete Formel

```json
{
  "cue": "pq-Formel",
  "response": "$x_{1{,}2} = -\\frac{p}{2} \\pm \\sqrt{\\left(\\frac{p}{2}\\right)^2 - q}$"
}
```

### Erklärung

`cue`: mathematische Symbolik, `response`: Erklärung der Symbolik

```json
{
  "cue": "\\(P(X=k)\\)",
  "response": "Wahrscheinlichkeit für genau \\(k\\) Treffer"
}
```

### Bedingung

`cue`: Folgerung, `response`: Bedingung

```json
{
  "cue": "Graph von $f$ ist streng monoton wachsend, falls",
  "response": "$f'(x)>0$"
}
```

### Merkregel

`cue`: "Merkregel", `response`: Ausprägung der Merkregel

```json
{
  "cue": "Merkregel",
  "response": "Produkt der Hauptdiagonale minus Produkt der Nebendiagonale"
}
```

### Beachte

`cue`: "Beachte", `response`: das, was beachtet werden muss

```json
{
  "cue": "Beachte",
  "response": "Matrizenmultiplikation ist nicht kommutativ: $AB \\neq BA$"
}
```

## Prozess-Tipps

Prozess-Tipps sind Schritt-für-Schritt-Anleitungen, die den Lösungsweg für einen Check beschreiben. Sie sind in einer bestimmten Reihenfolge zu bearbeiten und haben daher zwingend `tippOrder = fixed`.

`cue`: Schrittbeschreibung, `response`: konkrete Anweisung

```json
[
  {
    "cue": "1. Ansatz",
    "response": "Allgemeine Form $K(x)=ax^3+bx^2+cx+d$ aufstellen, evtl. weitere"
  },
  {
    "cue": "2. Bedingungen",
    "response": "Informationen in Gleichung überführen"
  },
  {
    "cue": "3. Gleichungssystem",
    "response": "Lineares Gleichungssystem mit 4 Gleichungen und 4 Unbekannten aufstellen"
  },
  {
    "cue": "4. Lösung",
    "response": "Lineares Gleichungssystem mit Taschenrechner oder Gauß-Algorithmus lösen"
  }
]
```

## Funktion im System

- Im Skript werden die Tipps in einer Liste mit Einträgen "`cue`: `response`" angezeigt.
- Bei den Aufgaben und der Feynman-Aktivität dienen die Tipps als Kontext für KI-Agenten, den der User kopieren kann.
- Im Recall werden die Tipps zunächst vollständig angezeigt, und zwar immer in der Reihenfolge wie in checks.json (unabhängig von `tippOrder`). Danach werden die `responses` verdeckt, und der User muss die `responses` per Text- oder Spracheingabe in ein Input-Feld eingeben. In dieser Abfragephase richtet sich die Reihenfolge der Tipps nach `tippOrder`: bei `shuffle` werden sie zufällig angeordnet, bei `fixed` bleibt die Reihenfolge aus checks.json erhalten. Im Anschluss prüft eine KI, ob die User-Eingabe inhaltlich zum hinterlegten Systemwert passt.

## Allgemeine Hinweise zur Darstellung

- Konsistente Schreibweise der `cues` und `responses`: keine Abkürzungen, keine Umgangssprache, keine vollständigen Sätze, sondern stichwortartig; einheitliche Konventionen bei Groß- und Kleinschreibung
- Nicht zu lang
- Keine allgemeinen Phrasen – die Tipps müssen einen Mehrwert für den User haben