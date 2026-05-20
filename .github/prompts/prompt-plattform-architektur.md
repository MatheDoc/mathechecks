---
description: Architektur-Workflow für Datenbank, Benutzerverwaltung, Session-State, Rollen, Fortschritt und Aktionsfeed in MatheChecks.
---

# Plattform-Architektur klären

Lese vor Beginn `.github/glossary.md`, `.github/datenmodell.md` und bei Systemfragen zusätzlich `.github/rechner-architektur.md`.

## Eingaben

- Ziel oder Problemstellung
- betroffene Domänenobjekte, zum Beispiel Benutzer, Session, Feed, Rollen oder Fortschritt
- harte Randbedingungen, zum Beispiel Hosting, Datenschutz, bestehende Jekyll-Struktur oder Migrationsdruck
- offene Fragen oder bereits favorisierte Optionen

## Arbeitsauftrag

1. Scope explizit begrenzen.
2. Domänenobjekte, Zustände und Source of Truth pro Objekt benennen.
3. Schreibfälle, Lesefälle und Berechtigungen skizzieren.
4. Höchstens 2 bis 3 realistische Architekturvarianten vergleichen.
5. Eine inkrementelle Startvariante mit Migrationspfad empfehlen.
6. Verifikationspunkte, Risiken und offene Fragen benennen.

## Ausgabeformat

- Zielbild
- Datenmodell
- API-, Event- oder Synchronisationsflüsse
- Sicherheits- und Datenschutzpunkte
- Migrationsplan
- nächste 3 Schritte