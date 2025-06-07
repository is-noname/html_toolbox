#!/usr/bin/env python3
# quick_start_example.py - Sofort loslegen mit dem neuen API-System

"""
QUICK START: Neues WED API-System

Dieses Skript zeigt, wie das neue modulare API-System sofort verwendet werden kann.
Führe es aus, um zu sehen, ob alles funktioniert!
"""

import os
import json
import sys
from datetime import datetime

def create_example_config():
    """Erstellt Beispiel-Konfiguration falls nicht vorhanden"""
    config = {
        "api_keys": {
            "fred": "bbc4b13f812a3a505523ab2a982e4a66"  # Dein API-Key
        },
        "sources": {
            "fred": {
                "name": "Federal Reserve Economic Data",
                "base_url": "https://api.stlouisfed.org/fred",
                "rate_limit": 1.0,
                "timeout": 30,
                "retries": 3,
                "datasets": {
                    "gdp": "GDP",
                    "inflation": "CPIAUCSL",
                    "unemployment": "UNRATE",
                    "interest_rate_fed": "FEDFUNDS"
                }
            }
        }
    }
    
    with open('api_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ api_config.json erstellt")

def test_fred_source():
    """Testet die FRED-Quelle direkt"""
    try:
        # Prüfen ob sources-Package verfügbar ist
        sys.path.append('.')  # Aktuelles Verzeichnis zu Python-Path hinzufügen
        
        from sources.fred_source import create_fred_source
        
        # FRED-Konfiguration
        config = {
            "base_url": "https://api.stlouisfed.org/fred",
            "rate_limit": 1.0,
            "datasets": {
                "gdp": "GDP",
                "unemployment": "UNRATE"
            }
        }
        
        # FRED-Quelle erstellen
        fred = create_fred_source(config, "bbc4b13f812a3a505523ab2a982e4a66")
        
        print("🔍 Teste FRED-Verbindung...")
        
        # Einzelnen Datensatz abrufen
        gdp_data = fred.fetch_dataset("gdp", {"limit": 5})  # Nur 5 neueste Werte
        
        if 'error' not in gdp_data:
            latest = gdp_data['data']['latest']
            print(f"✅ GDP-Daten erfolgreich abgerufen:")
            print(f"   Neuester Wert: {latest['value']} Billionen USD ({latest['date']})")
            print(f"   Historische Werte: {len(gdp_data['data']['historical'])}")
        else:
            print(f"❌ Fehler beim GDP-Abruf: {gdp_data['error']}")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("   Stelle sicher, dass alle Dateien im sources/ Verzeichnis sind")
        return False
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

def test_full_updater():
    """Testet den kompletten Data-Updater"""
    try:
        from data_updater import WEDDataUpdater
        
        print("🚀 Teste vollständigen Data-Updater...")
        
        updater = WEDDataUpdater()
        
        # Nur einen Datensatz für den Test
        result = updater.update_single_dataset('fred', 'unemployment')
        
        if 'error' not in result:
            print("✅ Data-Updater funktioniert!")
            
            # Prüfen ob economic_data.json erstellt wurde
            if os.path.exists('api/economic_data.json'):
                with open('api/economic_data.json', 'r') as f:
                    data = json.load(f)
                
                unemployment = data.get('datasets', {}).get('unemployment', {})
                if unemployment:
                    latest = unemployment.get('data', {}).get('latest', {})
                    print(f"   Arbeitslosenquote: {latest.get('value')}% ({latest.get('date')})")
                
                print(f"   Datei economic_data.json wurde aktualisiert")
            
            return True
        else:
            print(f"❌ Data-Updater Fehler: {result['error']}")
            return False
            
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Updater-Fehler: {e}")
        return False

def verify_output():
    """Prüft die generierte economic_data.json"""
    if not os.path.exists('api/economic_data.json'):
        print("❌ economic_data.json wurde nicht erstellt")
        return False
    
    try:
        with open('api/economic_data.json', 'r') as f:
            data = json.load(f)
        
        print("📊 Output-Validierung:")
        print(f"   Letzte Aktualisierung: {data.get('meta', {}).get('last_updated', 'Unknown')}")
        
        datasets = data.get('datasets', {})
        print(f"   Anzahl Datensätze: {len(datasets)}")
        
        for dataset_id, dataset in datasets.items():
            latest = dataset.get('data', {}).get('latest', {})
            if latest.get('value') is not None:
                print(f"   ✅ {dataset_id}: {latest['value']} ({latest['date']})")
            else:
                print(f"   ⚠️  {dataset_id}: Keine aktuellen Daten")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ economic_data.json enthält ungültiges JSON")
        return False
    except Exception as e:
        print(f"❌ Validierungs-Fehler: {e}")
        return False

def main():
    """Hauptfunktion: Kompletter Test des neuen API-Systems"""
    print("🎯 WED API-System Quick Start")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # 1. Konfiguration erstellen
    print("\n1️⃣ Konfiguration prüfen/erstellen...")
    if not os.path.exists('api_config.json'):
        create_example_config()
    else:
        print("✅ api_config.json bereits vorhanden")
    success_count += 1
    
    # 2. FRED-Quelle testen
    print("\n2️⃣ FRED-Quelle testen...")
    if test_fred_source():
        success_count += 1
    
    # 3. Data-Updater testen
    print("\n3️⃣ Data-Updater testen...")
    if test_full_updater():
        success_count += 1
    
    # 4. Output validieren
    print("\n4️⃣ Output validieren...")
    if verify_output():
        success_count += 1
    
    # Ergebnis
    print("\n" + "=" * 50)
    print(f"🎯 Test-Ergebnis: {success_count}/{total_tests} erfolgreich")
    
    if success_count == total_tests:
        print("🎉 ALLES FUNKTIONIERT! Das neue API-System ist einsatzbereit.")
        print("\nNächste Schritte:")
        print("   - Führe 'python data_updater.py' für vollständige Updates aus")
        print("   - Dashboard sollte die neuen Daten automatisch laden")
        print("   - Erweitere um weitere API-Quellen in sources/")
    else:
        print("⚠️  Einige Tests fehlgeschlagen. Prüfe die Fehlermeldungen oben.")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
