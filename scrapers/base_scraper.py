from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseScraper(ABC):
    """Abstrakte Basis-Klasse für alle Scraper."""

    @abstractmethod
    def analyze_structure(self, url: str) -> Dict[str, Any]:
        """Einmalige Analyse, um DOM-Struktur zu erkennen."""
        pass

    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Lädt HTML asynchron."""
        pass

    @abstractmethod
    def parse(self, html: str) -> Dict[str, Any]:
        """Extrahiert Spiel-Daten robust und redundant."""
        pass

    @abstractmethod
    async def batch_download(self, seasons: List[str]) -> List[Dict[str, Any]]:
        """Lädt alle Spiele einer Saison per Spieltag."""
        pass
