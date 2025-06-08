# WED Dateninfrastruktur

## Überblick
Diese Komponente verwaltet die Datenerfassung und -aktualisierung für das World Economy Dashboard (WED). Sie arbeitet unabhängig vom Frontend und sorgt für aktuelle Wirtschaftsdaten.

## Architektur

```
/api/
  api_manager.py       # Zentrale API-Verwaltung
  data_updater.py      # Regelmäßige Datenaktualisierung
  /sources/
    fred.py            # Federal Reserve Economic Data (FRED)
    eurostat.py        # EU-Wirtschaftsdaten
    tradingeconomics.py # Marktdaten & Indizes
/data/
  economic_data.json   # Zentrale Datenablage
```

## Funktionsweise
1. `data_updater.py` läuft täglich als geplanter Task (Cron/Scheduler)
2. Der Updater nutzt `api_manager.py` um Daten von verschiedenen Quellen zu holen
3. Quellenspezifische Module in `/sources/` kapseln Details der jeweiligen APIs
4. Aktualisierte Daten werden in `economic_data.json` geschrieben
5. Das Frontend liest diese Datei und muss keine API-Calls selbst durchführen

## Vorteile
- **Entkopplung**: Frontend entwickelt sich unabhängig von Datenquellen
- **Zuverlässigkeit**: Fehlerhafte APIs blockieren nicht die Anwendung
- **Kosten-Optimierung**: Effizientes Caching reduziert API-Anfragen
- **Skalierbarkeit**: Neue Datenquellen erfordern nur neue Quell-Module

## Status
- [x] Grundlegende FRED-Integration (fred_data_fetcher.py)
- [x] Modularer API-Manager
- [ ] Automatisierte Aktualisierungslogik
- [ ] Fehlerbehandlung und Logging
- [ ] Erweiterung um weitere Datenquellen

**Anmerkung**: Diese Komponente läuft parallel zur Frontend-Entwicklung und wird schrittweise ausgebaut.