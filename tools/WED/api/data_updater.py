#!/usr/bin/env python3
# data_updater.py - Orchestriert regelmäßige Datenaktualisierung für WED

import os
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List
from api_manager import api_manager
from sources.fred_source import create_fred_source

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_updater')

class WEDDataUpdater:
    """Zentraler Updater für alle Wirtschaftsdaten im Dashboard
    
    Funktionen:
    - Lädt Konfiguration für alle Datenquellen
    - Orchestriert Datenabfrage von verschiedenen APIs
    - Konsolidiert Daten in einheitliche JSON-Struktur
    - Behandelt Fehler und Fallbacks
    """
    
    def __init__(self, config_file: str = "api_config.json", output_file: str = "economic_data.json"):
        self.config_file = config_file
        self.output_file = output_file
        self.config = self._load_config()
        self.registered_sources = {}
        
        # API-Manager vorbereiten
        self._setup_api_sources()
        
        logger.info("WED Data Updater initialized")
    
    def _load_config(self) -> Dict:
        """Lädt Konfiguration für Datenquellen und API-Schlüssel"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {self.config_file} not found")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return {}
    
    def _setup_api_sources(self):
        """Registriert alle konfigurierten API-Quellen im API-Manager"""
        
        # FRED-Quelle registrieren
        if 'fred' in self.config.get('sources', {}):
            fred_config = self.config['sources']['fred']
            fred_api_key = self.config.get('api_keys', {}).get('fred', '')
            
            if fred_api_key:
                fred_source = create_fred_source(fred_config, fred_api_key)
                api_manager.register_source('fred', fred_source)
                self.registered_sources['fred'] = fred_config['datasets']
                logger.info("FRED source registered")
            else:
                logger.warning("FRED API key missing - skipping FRED registration")
        
        # Hier können weitere Quellen hinzugefügt werden:
        # self._setup_eurostat()
        # self._setup_tradingeconomics()
    
    def update_all_data(self) -> Dict:
        """Aktualisiert alle konfigurierten Datensätze
        
        Returns:
            Vollständige Datenstruktur für economic_data.json
        """
        logger.info("Starting full data update...")
        
        # Basis-Struktur für Output
        output_data = {
            "meta": {
                "last_updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "source": "Multiple APIs via WED Data Updater",
                "update_summary": {}
            },
            "datasets": {}
        }
        
        total_datasets = 0
        successful_updates = 0
        
        # Alle registrierten Quellen durchgehen
        for source_name, datasets in self.registered_sources.items():
            logger.info(f"Updating data from {source_name}...")
            
            source_summary = {
                "total": len(datasets),
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            # Alle Datensätze der Quelle aktualisieren
            for dataset_id in datasets.keys():
                try:
                    total_datasets += 1
                    
                    # Daten über API-Manager abrufen
                    data = api_manager.fetch_data(source_name, dataset_id)
                    
                    if 'error' not in data:
                        # Erfolgreiche Aktualisierung
                        output_data['datasets'][dataset_id] = self._format_dataset_for_output(data, dataset_id)
                        successful_updates += 1
                        source_summary["successful"] += 1
                        logger.info(f"✅ Updated {dataset_id}")
                    else:
                        # Fehler beim Abrufen
                        source_summary["failed"] += 1
                        source_summary["errors"].append(f"{dataset_id}: {data['error']}")
                        logger.error(f"❌ Failed to update {dataset_id}: {data['error']}")
                        
                        # Fallback: Alte Daten beibehalten wenn möglich
                        old_data = self._load_existing_dataset(dataset_id)
                        if old_data:
                            output_data['datasets'][dataset_id] = old_data
                            logger.info(f"🔄 Using cached data for {dataset_id}")
                
                except Exception as e:
                    source_summary["failed"] += 1
                    error_msg = f"Unexpected error: {str(e)}"
                    source_summary["errors"].append(f"{dataset_id}: {error_msg}")
                    logger.error(f"❌ Exception updating {dataset_id}: {error_msg}")
                    logger.debug(traceback.format_exc())
            
            output_data["meta"]["update_summary"][source_name] = source_summary
        
        # Update-Statistiken
        logger.info(f"Update complete: {successful_updates}/{total_datasets} datasets updated successfully")
        
        # Daten speichern
        self._save_data(output_data)
        
        return output_data
    
    def _format_dataset_for_output(self, raw_data: Dict, dataset_id: str) -> Dict:
        """Formatiert API-Daten für economic_data.json
        
        Args:
            raw_data: Rohdaten vom API-Manager
            dataset_id: ID des Datensatzes
            
        Returns:
            Formatierte Daten für Output-JSON
        """
        # Basis-Struktur aus der API-Antwort übernehmen
        formatted = {
            "title": self._get_dataset_title(dataset_id),
            "unit": self._get_dataset_unit(dataset_id),
            "data": raw_data.get('data', {})
        }
        
        return formatted
    
    def _get_dataset_title(self, dataset_id: str) -> str:
        """Gibt menschenlesbaren Titel für Dataset zurück"""
        titles = {
            'gdp': 'BIP der USA',
            'inflation': 'Inflation (USA)',
            'unemployment': 'Arbeitslosenquote (USA)',
            'interest_rate_fed': 'Leitzins (Fed)',
            'interest_rate_ecb': 'Leitzins (EZB)',
            'baltic_dry': 'Baltic Dry Index',
            'world_trade': 'Welthandelsvolumen'
        }
        return titles.get(dataset_id, dataset_id.title())
    
    def _get_dataset_unit(self, dataset_id: str) -> str:
        """Gibt Einheit für Dataset zurück"""
        units = {
            'gdp': 'Billionen USD',
            'inflation': 'Index',
            'unemployment': '%',
            'interest_rate_fed': '%',
            'interest_rate_ecb': '%',
            'baltic_dry': 'Index',
            'world_trade': 'Index 2010=100'
        }
        return units.get(dataset_id, 'Unknown')
    
    def _load_existing_dataset(self, dataset_id: str) -> Dict:
        """Lädt existierenden Datensatz als Fallback
        
        Args:
            dataset_id: ID des Datensatzes
            
        Returns:
            Bestehende Daten oder None
        """
        try:
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r') as f:
                    existing_data = json.load(f)
                    return existing_data.get('datasets', {}).get(dataset_id)
        except:
            pass
        return None
    
    def _save_data(self, data: Dict):
        """Speichert konsolidierte Daten in JSON-Datei"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to save data: {str(e)}")
            raise
    
    def update_single_dataset(self, source: str, dataset_id: str) -> Dict:
        """Aktualisiert nur einen spezifischen Datensatz
        
        Args:
            source: Name der Datenquelle (z.B. 'fred')
            dataset_id: ID des Datensatzes
            
        Returns:
            Aktualisierte Daten
        """
        logger.info(f"Updating single dataset: {source}.{dataset_id}")
        
        try:
            data = api_manager.fetch_data(source, dataset_id)
            
            if 'error' not in data:
                # Existierende Datei laden und updaten
                try:
                    with open(self.output_file, 'r') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = {"meta": {}, "datasets": {}}
                
                # Einzelnen Datensatz aktualisieren
                existing_data['datasets'][dataset_id] = self._format_dataset_for_output(data, dataset_id)
                existing_data['meta']['last_updated'] = datetime.now().strftime("%d.%m.%Y %H:%M")
                
                # Speichern
                self._save_data(existing_data)
                
                logger.info(f"✅ Successfully updated {dataset_id}")
                return data
            else:
                logger.error(f"❌ Failed to update {dataset_id}: {data['error']}")
                return data
                
        except Exception as e:
            error_msg = f"Exception updating {dataset_id}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

# Hauptfunktionen für externe Verwendung
def update_all():
    """Aktualisiert alle Datensätze - Entry Point für Cron-Jobs"""
    updater = WEDDataUpdater()
    return updater.update_all_data()

def update_dataset(source: str, dataset_id: str):
    """Aktualisiert einzelnen Datensatz - Entry Point für gezielte Updates"""
    updater = WEDDataUpdater()
    return updater.update_single_dataset(source, dataset_id)

if __name__ == "__main__":
    # Vollständige Aktualisierung ausführen
    try:
        result = update_all()
        print("✅ Data update completed successfully")
        print(f"Updated {len(result.get('datasets', {}))} datasets")
    except Exception as e:
        print(f"❌ Data update failed: {str(e)}")
        logger.error(f"Main execution failed: {str(e)}")
        logger.debug(traceback.format_exc())
