"""
Scraper France Travail (ex Pôle Emploi) — API officielle et gratuite.
Inscription : https://francetravail.io/data/api/offres-emploi
"""
import requests
from typing import Optional
from scrapers.base_scraper import BaseScraper
from utils.logger import get_logger
import os

logger = get_logger("france_travail_scraper")

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
OFFERS_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"


class FranceTravailScraper(BaseScraper):
    SOURCE_NAME = "france_travail"

    def __init__(self):
        super().__init__()
        self.client_id = os.getenv("FT_CLIENT_ID")
        self.client_secret = os.getenv("FT_CLIENT_SECRET")
        self._token = None

    def _get_token(self) -> Optional[str]:
        """Récupère un token OAuth2 (valide 1499 secondes)."""
        if not self.client_id or not self.client_secret:
            logger.warning("[FT] FT_CLIENT_ID / FT_CLIENT_SECRET non définis dans .env")
            return None
        try:
            resp = requests.post(TOKEN_URL, data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "api_offresdemploiv2 o2dsoffre",
            }, params={"realm": "/partenaire"}, timeout=10)
            resp.raise_for_status()
            return resp.json().get("access_token")
        except Exception as e:
            logger.error(f"[FT] Erreur token : {e}")
            return None

    def scrape(self) -> list[dict]:
        token = self._get_token()
        if not token:
            return []

        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "motsCles": "alternance",
            "typeContrat": "CA,CC",   # CA=Contrat Apprentissage, CC=Contrat Professionnalisation
            "departement": "75,92,93,94,95,77,78,91",  # Tous les départements IDF
            "range": "0-49",
        }

        try:
            resp = requests.get(OFFERS_URL, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"[FT] Erreur appel API : {e}")
            return []

        offers = []
        for job in data.get("resultats", []):
            lieu = job.get("lieuTravail", {})
            offers.append({
                "title": job.get("intitule", ""),
                "company": job.get("entreprise", {}).get("nom", "Entreprise confidentielle"),
                "location": f"{lieu.get('libelle', '')} ({lieu.get('codePostal', '')})",
                "url": job.get("origineOffre", {}).get("urlOrigine", ""),
                "posted_at": job.get("dateCreation", ""),
            })

        logger.info(f"[France Travail] {len(offers)} offres trouvées")
        return offers
