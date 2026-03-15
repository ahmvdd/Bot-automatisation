"""
Scraper Welcome to the Jungle via leur API Algolia interne.
Les clés sont publiques (visibles dans le HTML de la page).
"""
import requests
from scrapers.base_scraper import BaseScraper
from utils.logger import get_logger

logger = get_logger("wtj_scraper")

ALGOLIA_APP_ID = "CSEKHVMS53"
ALGOLIA_API_KEY = "4bd8f6215d0cc52b26430765769e65a0"
ALGOLIA_INDEX = "wttj_jobs_production_fr"
ALGOLIA_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"

IDF_QUERY = "Île-de-France"


class WelcomeToJungleScraper(BaseScraper):
    SOURCE_NAME = "welcome_to_jungle"

    def scrape(self) -> list:
        offers = []
        page = 0

        while True:
            batch = self._fetch_page(page)
            if not batch:
                break
            offers.extend(batch)
            # Max 3 pages (90 offres) pour ne pas surcharger
            if page >= 2:
                break
            page += 1

        logger.info(f"[WTJ] {len(offers)} offres trouvées")
        return offers

    def _fetch_page(self, page: int) -> list:
        headers = {
            "X-Algolia-Application-Id": ALGOLIA_APP_ID,
            "X-Algolia-API-Key": ALGOLIA_API_KEY,
            "Content-Type": "application/json",
            "Referer": "https://www.welcometothejungle.com/",
            "Origin": "https://www.welcometothejungle.com",
        }
        payload = {
            "query": "alternance",
            "hitsPerPage": 30,
            "page": page,
            "facetFilters": [
                ["contract_type:alternance", "contract_type:apprenticeship"]
            ],
            "aroundLatLng": "48.8566,2.3522",
            "aroundRadius": 50000,
            "attributesToRetrieve": [
                "name", "organization", "offices", "slug",
                "contract_type", "published_at", "organization_slug"
            ],
        }

        try:
            resp = requests.post(ALGOLIA_URL, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
            return self._parse_hits(resp.json().get("hits", []))
        except Exception as e:
            logger.warning(f"[WTJ] Erreur page {page} : {e}")
            return []

    def _build_url(self, job: dict, org: dict) -> str:
        org_slug = org.get("slug", "") or job.get("organization_slug", "")
        slug = job.get("slug", "")
        if not (org_slug and slug):
            return ""
        return f"https://www.welcometothejungle.com/fr/companies/{org_slug}/jobs/{slug}"

    def _build_location(self, offices: list) -> str:
        if not offices:
            return ""
        city = offices[0].get("city", "")
        country = offices[0].get("country_code", "")
        return f"{city}, {country}" if country else city

    def _parse_hits(self, hits: list) -> list:
        offers = []
        for job in hits:
            org = job.get("organization", {}) or {}
            url = self._build_url(job, org)
            if not url:
                continue
            offers.append({
                "title": job.get("name", ""),
                "company": org.get("name", ""),
                "location": self._build_location(job.get("offices", [])),
                "url": url,
                "posted_at": job.get("published_at", ""),
            })
        return offers
