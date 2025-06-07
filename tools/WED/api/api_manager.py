#!/usr/bin/env python3
# api_manager.py - Zentrale Komponente für API-Verwaltung im WED-Projekt

import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Callable

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_manager.log'
)
logger = logging.getLogger('api_manager')

class APIManager:
    """Zentrale Verwaltung für alle Datenquellen-APIs im WED-Projekt"""
    
    def __init__(self, config_file: str = "api_config.json"):
        """Initialisiert den API-Manager mit Konfigurationsdaten
        
        Args:
            config_file: Pfad zur Konfigurationsdatei mit API-Schlüsseln etc.
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.sources = {}  # API-Quellen-Module
        self.rate_limits = {}  # Speichert Zeitstempel für Rate-Limiting
        self.data_cache = {}  # Cache für API-Antworten
        
        logger.info("API Manager initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Lädt Konfigurationen und API-Schlüssel aus der Konfigurationsdatei"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file {self.config_file} not found. Using empty config.")
                return {}
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def register_source(self, name: str, source_module) -> None:
        """Registriert eine neue API-Quelle
        
        Args:
            name: Eindeutiger Name für die Datenquelle
            source_module: Python-Modul mit API-Funktionen
        """
        if name in self.sources:
            logger.warning(f"Source {name} already registered. Overwriting.")
        
        self.sources[name] = source_module
        self.rate_limits[name] = {
            'last_call': 0,
            'min_interval': source_module.MIN_INTERVAL if hasattr(source_module, 'MIN_INTERVAL') else 1
        }
        logger.info(f"Registered source: {name}")
    
    def get_api_key(self, source_name: str) -> str:
        """Gibt den API-Schlüssel für eine bestimmte Quelle zurück
        
        Args:
            source_name: Name der Datenquelle
            
        Returns:
            API-Schlüssel als String
        """
        if source_name in self.config.get('api_keys', {}):
            return self.config['api_keys'][source_name]
        else:
            logger.warning(f"No API key found for {source_name}")
            return ""
    
    def fetch_data(self, source_name: str, dataset_id: str, params: Dict = None) -> Dict:
        """Ruft Daten von einer API-Quelle ab mit Rate-Limiting und Fehlerbehandlung
        
        Args:
            source_name: Name der registrierten Datenquelle
            dataset_id: ID des Datensatzes in der Datenquelle
            params: Zusätzliche Parameter für den API-Aufruf
            
        Returns:
            Abgerufene Daten als Dictionary
        """
        if source_name not in self.sources:
            error_msg = f"Source {source_name} not registered"
            logger.error(error_msg)
            return {'error': error_msg}
        
        # Rate-Limiting prüfen und einhalten
        self._respect_rate_limit(source_name)
        
        # Caching-Schlüssel erstellen
        cache_key = f"{source_name}_{dataset_id}_{str(params)}"
        
        # Versuchen, aus dem Cache zu laden
        if cache_key in self.data_cache:
            cache_entry = self.data_cache[cache_key]
            # Wenn Cache noch frisch ist (weniger als 1 Stunde alt)
            if time.time() - cache_entry['timestamp'] < 3600:  
                logger.info(f"Using cached data for {cache_key}")
                return cache_entry['data']
        
        try:
            source_module = self.sources[source_name]
            
            # API-Schlüssel bereitstellen, wenn verfügbar
            api_key = self.get_api_key(source_name)
            
            # Startzeit für Protokollierung und Rate-Limiting
            start_time = time.time()
            
            # API-Aufruf mit dem spezifischen Modul
            result = source_module.fetch_dataset(dataset_id, params)
            
            # Rate-Limit aktualisieren
            self.rate_limits[source_name]['last_call'] = start_time
            
            # Ergebnis im Cache speichern
            self.data_cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            
            logger.info(f"Successfully fetched data from {source_name} for {dataset_id}")
            return result
            
        except Exception as e:
            error_msg = f"Error fetching data from {source_name}: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}
    
    def _respect_rate_limit(self, source_name: str) -> None:
        """Stellt sicher, dass Rate-Limits eingehalten werden"""
        if source_name in self.rate_limits:
            last_call = self.rate_limits[source_name]['last_call']
            min_interval = self.rate_limits[source_name]['min_interval']
            
            # Zeit seit dem letzten Aufruf berechnen
            time_since_last = time.time() - last_call
            
            # Wenn nötig, warten bis zum nächsten erlaubten Aufruf
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                logger.info(f"Rate limit: Waiting {wait_time:.2f}s before calling {source_name}")
                time.sleep(wait_time)
    
    def get_available_datasets(self, source_name: str) -> List[Dict]:
        """Gibt verfügbare Datensätze für eine Quelle zurück
        
        Args:
            source_name: Name der Datenquelle
            
        Returns:
            Liste von Datensatz-Informationen
        """
        if source_name not in self.sources:
            logger.error(f"Source {source_name} not registered")
            return []
        
        try:
            source_module = self.sources[source_name]
            if hasattr(source_module, 'get_available_datasets'):
                return source_module.get_available_datasets(self.get_api_key(source_name))
            else:
                logger.warning(f"Source {source_name} does not support dataset listing")
                return []
        except Exception as e:
            logger.error(f"Error getting datasets from {source_name}: {str(e)}")
            return []
    
    def clear_cache(self, source_name: str = None) -> None:
        """Leert den Daten-Cache für eine oder alle Quellen
        
        Args:
            source_name: Optional, Name der zu löschenden Quelle. 
                         Wenn None, wird der gesamte Cache geleert.
        """
        if source_name:
            # Nur Einträge für die angegebene Quelle löschen
            keys_to_delete = [k for k in self.data_cache if k.startswith(f"{source_name}_")]
            for key in keys_to_delete:
                del self.data_cache[key]
            logger.info(f"Cleared cache for source {source_name}")
        else:
            # Gesamten Cache leeren
            self.data_cache = {}
            logger.info("Cleared entire cache")

# Singleton-Instanz erstellen
api_manager = APIManager()

# Hilfsfunktion zum einfachen Abrufen von Daten
def get_data(source: str, dataset: str, params: Dict = None) -> Dict:
    """Vereinfachte Funktion zum Abrufen von Daten
    
    Args:
        source: Name der Datenquelle
        dataset: ID des Datensatzes
        params: Zusätzliche Parameter
        
    Returns:
        Abgerufene Daten
    """
    return api_manager.fetch_data(source, dataset, params)