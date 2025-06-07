# Migration zum neuen API-System

## 🎯 Ziel
Übergang vom standalone `fred_data_fetcher.py` zum modularen API-Manager-System.

## 📁 Neue Struktur

```
/api/
├── api_config.json         # ✅ Zentrale Konfiguration
├── api_manager.py          # ✅ Bereits vorhanden
├── data_updater.py         # ✅ Neuer Orchestrator
├── /sources/               # ✅ Modulare API-Quellen
│   ├── __init__.py
│   ├── base_source.py      # ✅ Basis-Klasse
│   └── fred_source.py      # ✅ FRED-Modul
└── fred_data_fetcher.py    # 🔄 Legacy (wird ersetzt)
```

## 🚀 Migrations-Schritte

### 1. Neue Dateien erstellen
```bash
# Konfiguration anlegen
touch api_config.json

# Sources-Verzeichnis erstellen
mkdir -p sources
touch sources/__init__.py
```

### 2. Konfiguration migrieren
**Alt:** API-Key direkt im Code
```python
API_KEY = "bbc4b13f812a3a505523ab2a982e4a66"
```

**Neu:** API-Key in `api_config.json`
```json
{
  "api_keys": {
    "fred": "bbc4b13f812a3a505523ab2a982e4a66"
  }
}
```

### 3. Code migrieren

**Alt:** Direkter API-Call
```python
# fred_data_fetcher.py
def get_historical_data(series_id, limit=60):
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit
    }
    response = requests.get(BASE_URL, params=params)
    return response.json()['observations']
```

**Neu:** Über API-Manager
```python
# data_updater.py verwenden
from data_updater import update_all, update_dataset

# Alle Daten aktualisieren
result = update_all()

# Einzelnen Datensatz aktualisieren  
data = update_dataset('fred', 'gdp')
```

### 4. Dashboard-Integration

**Alt:** Dashboard lädt direkt `economic_data.json`
```javascript
// Bleibt unverändert! 
fetch('economic_data.json')
  .then(response => response.json())
  .then(data => updateCharts(data));
```

**Neu:** Identische Schnittstelle, aber bessere Daten
- Gleiche JSON-Struktur
- Robustere Datenaktualisierung
- Bessere Fehlerbehandlung

## ⚡ Sofortiger Nutzen

### Alte Methode ausführen
```bash
python fred_data_fetcher.py
```

### Neue Methode ausführen
```bash
python data_updater.py
```

**Ergebnis:** Identische `economic_data.json`, aber mit:
- ✅ Modularer Struktur
- ✅ Rate-Limiting
- ✅ Fehlerbehandlung
- ✅ Caching
- ✅ Logging
- ✅ Erweiterbar für neue APIs

## 🔧 Testing

### 1. Neue Struktur testen
```python
# Test der FRED-Quelle
from sources.fred_source import create_fred_source

config = {"base_url": "https://api.stlouisfed.org/fred", "datasets": {"gdp": "GDP"}}
fred = create_fred_source(config, "your-api-key")
data = fred.fetch_dataset("gdp")
print(data)
```

### 2. Vollständigen Updater testen
```python
from data_updater import WEDDataUpdater

updater = WEDDataUpdater()
result = updater.update_all_data()
print(f"Updated {len(result['datasets'])} datasets")
```

## 🎯 Nächste Schritte

1. **Sofort:** Neue Dateien erstellen und testen
2. **Diese Woche:** Alte Aufrufe durch neue ersetzen
3. **Nächste Woche:** Weitere API-Quellen hinzufügen
4. **Später:** Automatisierung mit Cron-Jobs

## ❗ Wichtige Hinweise

- **Backward-kompatibel:** Dashboard funktioniert ohne Änderungen
- **Schrittweise Migration:** Beide Systeme können parallel laufen
- **Gleiche Ausgabe:** `economic_data.json` bleibt identisch
- **Bessere Wartung:** Neue Struktur ist einfacher zu erweitern
