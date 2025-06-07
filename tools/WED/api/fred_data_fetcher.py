#!/usr/bin/env python3
# fred_data_fetcher.py - Holt Wirtschaftsdaten von FRED API

import requests
import json
from datetime import datetime
import os

def load_api_key():
    """Lädt den API-Key sicher aus der Konfigurationsdatei"""
    try:
        with open('api_config.json', 'r') as config_file:
            config = json.load(config_file)
            return config.get('api_keys', {}).get('fred', '')
    except FileNotFoundError:
        print("⚠️ Warnung: api_config.json nicht gefunden!")
        return ""
    except json.JSONDecodeError:
        print("⚠️ Fehler: api_config.json enthält ungültiges JSON!")

        return ""

# API-Key aus der JS-Datei
API_KEY = load_api_key() # Aus deiner api_config.js
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Die Datensätze, die wir abrufen wollen
datasets = {
    "gdp": {
        "id": "GDP",
        "title": "BIP der USA",
        "unit": "Billionen USD"
    },
    "inflation": {
        "id": "CPIAUCSL",
        "title": "Inflation (USA)",
        "unit": "Index"
    },
    "unemployment": {
        "id": "UNRATE",
        "title": "Arbeitslosenquote (USA)",
        "unit": "%"
    },
    "interest_rate_fed": {
        "id": "FEDFUNDS",
        "title": "Leitzins (Fed)",
        "unit": "%"
    },
    "interest_rate_ecb": {
        "id": "INTDSREZQ193N",
        "title": "Leitzins (EZB)",
        "unit": "%"
    },
    "baltic_dry": {
        "id": "BALTICF",
        "title": "Baltic Dry Index",
        "unit": "Index"
    },
    "world_trade": {
        "id": "WTEXVOL",  # Welthandelsvolumen Index
        "title": "Welthandelsvolumen",
        "unit": "Index 2010=100"
    }
}


# Historische Daten für Charts - letzten 5 Jahre
def get_historical_data(series_id, limit=60):
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['observations']
    else:
        print(f"Fehler beim Abrufen von {series_id}: {response.status_code}")
        return []


# Daten formatieren
def process_dataset(raw_data, dataset_info):
    if not raw_data:
        return {
            "latest": {"value": "N/A", "date": "N/A"},
            "historical": []
        }

    # Für Charts: Historische Daten (neueste zuerst)
    historical = []

    for entry in raw_data:
        # FRED nutzt "." für fehlende Werte
        if entry.get('value') == '.' or entry.get('value') is None:
            continue

        try:
            value = float(entry['value'])
            # Spezielle Formatierung für bestimmte Datensätze
            if dataset_info["id"] == "GDP":
                value = value / 1000  # Umrechnung in Billionen

            # Hier Nachkommastellen kürzen, z.B. auf 1 Stelle:
            value = round(value, 3)

            historical.append({
                "date": entry['date'],
                "value": value
            })
        except (ValueError, TypeError):
            # Ungültige Werte überspringen
            continue

    # Neueste Daten
    latest = {
        "value": historical[0]["value"] if historical else "N/A",
        "date": historical[0]["date"] if historical else "N/A"
    }

    # Liste umkehren für Chart (älteste zuerst)
    historical.reverse()

    return {
        "latest": latest,
        "historical": historical
    }


# Alle Daten sammeln
def collect_all_data():
    output_data = {
        "meta": {
            "last_updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "source": "FRED (Federal Reserve Economic Data)"
        },
        "datasets": {}
    }

    for key, dataset in datasets.items():
        print(f"Fetching {dataset['title']}...")
        raw_data = get_historical_data(dataset['id'])
        output_data["datasets"][key] = {
            "title": dataset['title'],
            "unit": dataset['unit'],
            "data": process_dataset(raw_data, dataset)
        }

    return output_data


# Hauptfunktion
def main():
    print("Starte Datensammlung von FRED API...")
    all_data = collect_all_data()

    # Daten speichern
    with open("economic_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"Fertig! Daten wurden in economic_data.json gespeichert.")
    print(f"Letzte Aktualisierung: {all_data['meta']['last_updated']}")


if __name__ == "__main__":
    main()