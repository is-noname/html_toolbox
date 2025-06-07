#!/usr/bin/env python3
# sources/__init__.py - Package-Definition für API-Quellen

"""
WED API Sources Package

Modulare API-Quellen für das World Economy Dashboard:
- Basis-Klasse für einheitliche Schnittstelle
- Konkrete Implementierungen für verschiedene Datenquellen
- Standardisierte Datenformate
- Rate-Limiting und Fehlerbehandlung

Verfügbare Quellen:
- FREDSource: Federal Reserve Economic Data
- (weitere Quellen werden schrittweise hinzugefügt)
"""

from .base_source import BaseAPISource
from .fred_source import FREDSource, create_fred_source

__all__ = [
    'BaseAPISource',
    'FREDSource', 
    'create_fred_source'
]

__version__ = '1.0.0'
__author__ = 'WED Team'
