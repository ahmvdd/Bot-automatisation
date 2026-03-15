import time
import random
import requests
from abc import ABC, abstractmethod
from typing import Optional
from fake_useragent import UserAgent
from utils.logger import get_logger

logger = get_logger("base_scraper")
ua = UserAgent()


class BaseScraper(ABC):
    """Classe de base commune à tous les scrapers."""

    SOURCE_NAME = "unknown"

    def __init__(self):
        self.session = requests.Session()

    def _get(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """GET avec headers rotatifs, délai humain et retry automatique."""
        headers = {
            "User-Agent": ua.random,
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
        }
        for attempt in range(retries):
            try:
                time.sleep(random.uniform(2.0, 5.0))  # délai humain
                response = self.session.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"[{self.SOURCE_NAME}] Tentative {attempt+1}/{retries} échouée : {e}")
                time.sleep(random.uniform(5.0, 10.0))
        logger.error(f"[{self.SOURCE_NAME}] Impossible de récupérer {url}")
        return None

    @abstractmethod
    def scrape(self) -> list[dict]:
        """
        Retourne une liste de dicts avec les clés :
        title, company, location, url, posted_at
        """
        pass
