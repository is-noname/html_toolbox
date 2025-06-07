# Weltwirtschafts-Dashboard: Projektzusammenfassung

## 1. Projektziel

Das Weltwirtschafts-Dashboard ist ein interaktives Tool zur Visualisierung von aktuellen makroökonomischen Daten. Es dient als zentrales Informationsinstrument, um wichtige wirtschaftliche Trends und Indikatoren auf einen Blick zu erfassen und zu verstehen.

**Hauptzweck:**
- Echtzeitdaten zur globalen Wirtschaftslage zugänglich und verständlich darstellen
- Komplexe Wirtschaftsdaten in leicht verständliche visuelle Formate umwandeln
- Eine datenbasierte Grundlage für wirtschaftliche Entscheidungen bieten

## 2. Aktueller Projektstand

### 2.1 Frontend
- Funktionierendes Dashboard mit responsivem Design
- 6 Hauptkarten mit verschiedenen Wirtschaftsindikatoren:
  - BIP der Top-5-Volkswirtschaften
  - OECD Composite Leading Indicator (CLI)
  - Unternehmensumfragen (IfW Kiel Index)
  - Inflationsdynamik
  - Leitzinsen (Fed und EZB)
  - Internationale Handelsströme
- Interaktive Charts mit Chart.js
- Erklärungstexte zur Interpretation der Daten

### 2.2 Datenintegration
- Erfolgreiche Anbindung an die FRED API (Federal Reserve Economic Data)
- Python-Script zum Abrufen und Aufbereiten der Daten in eine JSON-Datei
- Folgende Datensätze werden aktuell abgedeckt:
  - US-BIP (GDP)
  - Inflationsrate (CPIAUCSL)
  - Arbeitslosenquote (UNRATE)
  - Fed-Leitzins (FEDFUNDS)
  - EZB-Leitzins (INTDSREZQ193N)
  - Handelsströme (teilweise)

### 2.3 Datenaktualisierung
- Manuelle Ausführung des Python-Scripts
- Aktualisierungsdatum wird im Dashboard angezeigt
- Daten werden im Format JSON gespeichert und vom Frontend geladen

## 3. Technologie-Stack

- **Frontend:** HTML5, CSS3, JavaScript
- **Visualisierung:** Chart.js (v3.9.1)
- **Icons/Styling:** Font Awesome, Custom CSS
- **Datenquellen:** FRED API
- **Datenabruf:** Python mit requests-Bibliothek

## 4. Projektstruktur

```
/world_economy_dashboard/
├── world_economy_dashboard.html     # Hauptdashboard
├── economic_data.json               # Aktuelle Wirtschaftsdaten
├── fred_data_fetcher.py             # Python-Script zum Datenabruf
├── api/
│   ├── fred.js                      # JavaScript-Interface zur FRED API
│   └── api_keys.js                  # API-Schlüssel (nicht im Repository)
└── 0_data_sources.md                # Dokumentation der Datenquellen
```

## 5. Nächste Schritte

### 5.1 Kurzfristig
- Automatisierung der Datenaktualisierung (z.B. durch Cron-Jobs)
- Vervollständigung fehlender Datensätze (Baltic Dry Index, Welthandelsvolumen)
- Implementierung eines Datums-Sliders für historische Ansichten

### 5.2 Mittelfristig
- Integration weiterer Datenquellen (Weltbank, OECD, Eurostat)
- Erweiterung um regionale Dashboards (Europa, Asien, etc.)
- Hinzufügen von Prognosedaten und -modellen

### 5.3 Langfristig
- Entwicklung eines Backend-Systems für komplexere Datenverarbeitung
- Benutzeranpassbare Dashboards
- Alerting-Funktionen für signifikante wirtschaftliche Veränderungen

## 6. Erste Schritte für neue Teammitglieder

1. Repository klonen und Abhängigkeiten installieren
2. Eigenen FRED API-Key beantragen (https://fred.stlouisfed.org/docs/api/api_key.html)
3. Python-Skript ausführen, um aktuelle Daten zu erhalten
4. Dashboard lokal starten und mit den Funktionen vertraut werden

## 7. Ansprechpartner

Bei Fragen wende dich bitte an das Projektteam:
- Datenintegration & Backend: [Name]
- Frontend & Visualisierung: [Name]
- Wirtschaftliche Interpretation: [Name]

---

*Dokument erstellt: Juni 2025*