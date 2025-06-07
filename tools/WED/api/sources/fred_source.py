#!/usr/bin/env python3
# sources/fred_source.py - FRED API-Integration für das WED-Dashboard

from typing import Dict, List, Optional
import logging
from .base_source import BaseAPISource

logger = logging.getLogger(__name__)

class FREDSource(BaseAPISource):
    """Federal Reserve Economic Data (FRED) API-Implementierung
    
    Spezialisierte Klasse für FRED-API:
    - Unterstützt alle Standard-FRED-Parameter
    - Automatische Datenkonvertierung für Wirtschaftsindikatoren
    - Robuste Fehlerbehandlung für FRED-spezifische Probleme
    """
    
    # Mindestintervall zwischen API-Calls (für api_manager)
    MIN_INTERVAL = 1.0
    
    def fetch_dataset(self, dataset_id: str, params: Dict = None) -> Dict:
        """Ruft FRED-Datensatz ab und konvertiert in Standard-Format
        
        Args:
            dataset_id: Logische Dataset-ID (z.B. "gdp", "inflation")
            params: Zusätzliche FRED-Parameter (limit, sort_order, etc.)
            
        Returns:
            Standardisierte Datenstruktur für Dashboard
        """
        # FRED-spezifische Dataset-ID aus Config holen
        fred_series_id = self.get_dataset_config(dataset_id)
        if not fred_series_id:
            raise ValueError(f"Dataset '{dataset_id}' not configured for FRED")
        
        # Standard-Parameter für FRED setzen
        request_params = {
            'series_id': fred_series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'sort_order': 'desc',  # Neueste Daten zuerst
            'limit': 60  # Letzten 5 Jahre (ca. 12 Quartale * 5)
        }
        
        # Benutzer-Parameter hinzufügen/überschreiben
        if params:
            request_params.update(params)
        
        try:
            # FRED API-Call
            url = f"{self.base_url}/series/observations"
            response_data = self._make_request(url, request_params)
            
            # FRED-Response validieren
            if 'observations' not in response_data:
                raise Exception("Invalid FRED response: missing 'observations'")
            
            observations = response_data['observations']
            
            # Dataset-Info für Konvertierung
            dataset_info = {
                'id': dataset_id,
                'fred_series': fred_series_id,
                'source': 'FRED'
            }
            
            # Daten in Standard-Format konvertieren
            standardized_data = self._standardize_data_format(observations, dataset_info)
            
            logger.info(f"Successfully fetched {len(observations)} observations for {dataset_id}")
            return standardized_data
            
        except Exception as e:
            logger.error(f"FRED fetch failed for {dataset_id}: {str(e)}")
            raise
    
    def get_available_datasets(self) -> List[Dict]:
        """Gibt alle konfigurierten FRED-Datensätze zurück
        
        Returns:
            Liste mit Dataset-Informationen
        """
        datasets = []
        for logical_id, fred_series_id in self.datasets.items():
            
            # Zusätzliche Metadaten aus FRED Series-Info holen (optional)
            try:
                series_info = self._get_series_info(fred_series_id)
                title = series_info.get('title', logical_id.title())
                units = series_info.get('units', 'Unknown')
            except:
                title = logical_id.title()
                units = 'Unknown'
            
            datasets.append({
                'id': logical_id,
                'title': title,
                'source': 'FRED',
                'series_id': fred_series_id,
                'units': units
            })
        
        return datasets
    
    def _get_series_info(self, fred_series_id: str) -> Dict:
        """Holt Metadaten für eine FRED-Serie
        
        Args:
            fred_series_id: FRED Series-ID (z.B. "GDP")
            
        Returns:
            Serie-Metadaten
        """
        params = {
            'series_id': fred_series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        
        url = f"{self.base_url}/series"
        response = self._make_request(url, params)
        
        if 'seriess' in response and len(response['seriess']) > 0:
            return response['seriess'][0]
        
        return {}
    
    def fetch_latest_value(self, dataset_id: str) -> Dict:
        """Schneller Abruf nur des neuesten Wertes (für Real-time Updates)
        
        Args:
            dataset_id: Logische Dataset-ID
            
        Returns:
            Nur der neueste Wert mit Timestamp
        """
        params = {'limit': 1}  # Nur neuester Wert
        data = self.fetch_dataset(dataset_id, params)
        
        return {
            'dataset': dataset_id,
            'latest': data['data']['latest'],
            'timestamp': data['meta']['last_updated']
        }
    
    def fetch_historical_range(self, dataset_id: str, start_date: str, end_date: str) -> Dict:
        """Ruft Daten für einen spezifischen Zeitraum ab
        
        Args:
            dataset_id: Logische Dataset-ID
            start_date: Start-Datum (YYYY-MM-DD)
            end_date: End-Datum (YYYY-MM-DD)
            
        Returns:
            Daten für den angegebenen Zeitraum
        """
        params = {
            'observation_start': start_date,
            'observation_end': end_date,
            'limit': 1000  # Mehr Datenpunkte für längere Zeiträume
        }
        
        return self.fetch_dataset(dataset_id, params)
    
    def _convert_value(self, raw_value: str, dataset_info: Dict) -> float:
        """FRED-spezifische Wert-Konvertierung
        
        Überschreibt die Basis-Methode für FRED-spezifische Besonderheiten:
        - GDP in Billionen umrechnen
        - Prozentsätze normalisieren
        - Fehlende Werte (".") behandeln
        """
        if raw_value is None or raw_value == "." or raw_value == "":
            return None
        
        try:
            value = float(raw_value)
            
            # FRED-spezifische Konvertierungen
            dataset_id = dataset_info.get('id', '')
            
            if dataset_id == 'gdp':
                # GDP von Milliarden in Billionen USD
                value = value / 1000
            elif dataset_id in ['unemployment', 'interest_rate_fed', 'interest_rate_ecb']:
                # Prozentsätze bleiben unverändert
                pass
            elif dataset_id == 'inflation':
                # CPI bleibt als Index-Wert
                pass
            
            return value
            
        except (ValueError, TypeError):
            logger.warning(f"Could not convert value '{raw_value}' for dataset {dataset_info.get('id')}")
            return None

# Factory-Funktion für api_manager
def create_fred_source(config: Dict, api_key: str) -> FREDSource:
    """Erstellt FRED-Source-Instanz
    
    Args:
        config: FRED-Konfiguration aus api_config.json
        api_key: FRED API-Schlüssel
        
    Returns:
        Konfigurierte FRED-Source-Instanz
    """
    return FREDSource(config, api_key)
