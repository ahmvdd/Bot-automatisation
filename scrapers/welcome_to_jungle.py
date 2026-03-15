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

# Villes cibles avec coordonnées GPS
TARGET_LOCATIONS = [
    {"name": "idf",          "lat": 48.8566, "lng": 2.3522,  "radius": 50000},
    {"name": "montpellier",  "lat": 43.6119, "lng": 3.8772,  "radius": 30000},
]

# Requêtes tech ciblées
TECH_QUERIES = [
    "développeur alternance",
    "data engineer alternance",
    "devops alternance",
    "cybersécurité alternance",
    "cloud alternance",
    "python alternance",
    "machine learning alternance",
    "software engineer alternance",
]


class WelcomeToJungleScraper(BaseScraper):
    SOURCE_NAME = "welcome_to_jungle"

    def scrape(self) -> list:
        seen_urls = set()
        offers = []

        for location in TARGET_LOCATIONS:
            for query in TECH_QUERIES:
                batch = self._fetch_page(query=query, location=location)
                for o in batch:
                    if o["url"] not in seen_urls:
                        seen_urls.add(o["url"])
                        offers.append(o)

        logger.info(f"[WTJ] {len(offers)} offres trouvées")
        return offers

    def _fetch_page(self, query: str, location: dict, page: int = 0) -> list:
        headers = {
            "X-Algolia-Application-Id": ALGOLIA_APP_ID,
            "X-Algolia-API-Key": ALGOLIA_API_KEY,
            "Content-Type": "application/json",
            "Referer": "https://www.welcometothejungle.com/",
            "Origin": "https://www.welcometothejungle.com",
        }
        payload = {
            "query": query,
            "hitsPerPage": 30,
            "page": page,
            "facetFilters": [
                ["contract_type:alternance", "contract_type:apprenticeship"]
            ],
            "aroundLatLng": f"{location['lat']},{location['lng']}",
            "aroundRadius": location["radius"],
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
            logger.warning(f"[WTJ] Erreur ({location['name']}, {query}) : {e}")
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
