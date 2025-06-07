#!/usr/bin/env python3
# sources/base_source.py - Basis-Klasse für alle API-Datenquellen

import requests
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAPISource(ABC):
    """Abstrakte Basis-Klasse für alle API-Datenquellen
    
    Definiert einheitliche Schnittstelle und gemeinsame Funktionalität:
    - Rate-Limiting
    - Fehlerbehandlung  
    - Retry-Logik
    - Datenformatierung
    """
    
    def __init__(self, config: Dict[str, Any], api_key: str = ""):
        """Initialisiert die API-Quelle mit Konfiguration
        
        Args:
            config: Konfigurationsdictionary aus api_config.json
            api_key: API-Schlüssel für authentifizierte Requests
        """
        self.config = config
        self.api_key = api_key
        self.name = config.get('name', 'Unknown Source')
        self.base_url = config.get('base_url', '')
        self.rate_limit = config.get('rate_limit', 1.0)  # Sekunden zwischen Requests
        self.timeout = config.get('timeout', 30)
        self.retries = config.get('retries', 3)
        self.datasets = config.get('datasets', {})
        
        self.last_request_time = 0
        
        logger.info(f"Initialized {self.name} source")
    
    def _wait_for_rate_limit(self) -> None:
        """Wartet bis zum nächsten erlaubten Request (Rate-Limiting)"""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.rate_limit:
            wait_time = self.rate_limit - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Führt HTTP-Request mit Retry-Logik und Fehlerbehandlung durch
        
        Args:
            url: Vollständige URL für den Request
            params: Query-Parameter
            
        Returns:
            JSON-Response als Dictionary
        """
        if params is None:
            params = {}
            
        # Rate-Limiting einhalten
        self._wait_for_rate_limit()
        
        for attempt in range(self.retries):
            try:
                self.last_request_time = time.time()
                
                logger.debug(f"Request attempt {attempt + 1}: {url}")
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.retries}): {str(e)}")
                
                if attempt < self.retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed after {self.retries} attempts: {str(e)}")
    
    @abstractmethod
    def fetch_dataset(self, dataset_id: str, params: Dict = None) -> Dict:
        """Ruft einen spezifischen Datensatz ab (muss von Subklassen implementiert werden)
        
        Args:
            dataset_id: ID des Datensatzes (z.B. "gdp", "inflation")
            params: Zusätzliche Parameter
            
        Returns:
            Standardisierte Datenstruktur
        """
        pass
    
    @abstractmethod
    def get_available_datasets(self) -> List[Dict]:
        """Gibt verfügbare Datensätze zurück (muss von Subklassen implementiert werden)
        
        Returns:
            Liste mit Datensatz-Informationen
        """
        pass
    
    def _standardize_data_format(self, raw_data: List[Dict], dataset_info: Dict) -> Dict:
        """Konvertiert rohe API-Daten in einheitliches Format
        
        Args:
            raw_data: Rohdaten von der API
            dataset_info: Metadaten zum Datensatz
            
        Returns:
            Standardisierte Datenstruktur für das Dashboard
        """
        if not raw_data:
            return {
                "meta": {
                    "source": self.name,
                    "dataset": dataset_info.get('id', 'unknown'),
                    "last_updated": datetime.now().isoformat(),
                    "count": 0
                },
                "data": {
                    "latest": {"value": None, "date": None},
                    "historical": []
                }
            }
        
        # Historische Daten sortieren (neueste zuerst für latest, dann umkehren für Charts)
        historical = []
        for entry in raw_data:
            try:
                # Datenkonvertierung je nach Datensatz
                value = self._convert_value(entry.get('value'), dataset_info)
                if value is not None:
                    historical.append({
                        "date": entry.get('date'),
                        "value": value
                    })
            except (ValueError, TypeError):
                continue
        
        # Nach Datum sortieren (neueste zuerst)
        historical.sort(key=lambda x: x['date'], reverse=True)
        
        # Latest value bestimmen
        latest = historical[0] if historical else {"value": None, "date": None}
        
        # Für Charts: älteste zuerst
        historical_for_charts = list(reversed(historical))
        
        return {
            "meta": {
                "source": self.name,
                "dataset": dataset_info.get('id', 'unknown'),
                "last_updated": datetime.now().isoformat(),
                "count": len(historical)
            },
            "data": {
                "latest": latest,
                "historical": historical_for_charts
            }
        }
    
    def _convert_value(self, raw_value: str, dataset_info: Dict) -> float:
        """Konvertiert String-Werte in numerische Werte
        
        Args:
            raw_value: Roher Wert als String
            dataset_info: Metadaten für Konvertierungsregeln
            
        Returns:
            Konvertierter numerischer Wert
        """
        if raw_value is None or raw_value == ".":
            return None
            
        try:
            value = float(raw_value)
            
            # Spezielle Konvertierungen je nach Datensatz
            if dataset_info.get('id') == 'gdp':
                # GDP von Millionen in Billionen konvertieren
                value = value / 1000
            
            return value
            
        except (ValueError, TypeError):
            return None
    
    def get_dataset_config(self, dataset_id: str) -> Optional[str]:
        """Gibt die API-spezifische Dataset-ID zurück
        
        Args:
            dataset_id: Logische Dataset-ID (z.B. "gdp")
            
        Returns:
            API-spezifische Dataset-ID oder None
        """
        return self.datasets.get(dataset_id)
