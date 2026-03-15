"""
Point d'entrée principal du bot de veille alternances IDF.

Usage :
    python main.py            # Lance le bot en continu (scraping + récap à 08h00)
    python main.py --once     # Un seul cycle de scraping (test)
    python main.py --recap    # Envoie le récap Telegram immédiatement (test)
"""
import sys
import schedule
import time
from datetime import datetime

from database.models import init_db
from database.repository import save_offer, get_new_offers, mark_as_notified, get_stats
from scrapers.welcome_to_jungle import WelcomeToJungleScraper
from scrapers.france_travail import FranceTravailScraper
from notifications.telegram_bot import send_daily_recap, send_startup_message
from utils.filters import is_alternance, is_idf, score_offer
from utils.logger import get_logger
from config import DAILY_RECAP_TIME

logger = get_logger("main")

# Liste des scrapers actifs
SCRAPERS = [
    WelcomeToJungleScraper(),
    FranceTravailScraper(),
]


def run_scraping():
    """Lance tous les scrapers et sauvegarde les nouvelles offres."""
    logger.info("═" * 50)
    logger.info(f"Cycle de scraping démarré — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    new_count = 0
    total_scraped = 0

    for scraper in SCRAPERS:
        try:
            offers = scraper.scrape()
            total_scraped += len(offers)

            for offer in offers:
                # Filtres : alternance + IDF
                if not is_alternance(offer["title"]):
                    continue
                if not is_idf(offer.get("location", "")):
                    continue

                score = score_offer(
                    offer["title"],
                    offer.get("location", ""),
                    offer.get("description", "")
                )

                saved = save_offer(
                    title=offer["title"],
                    company=offer.get("company", ""),
                    location=offer.get("location", ""),
                    url=offer["url"],
                    source=scraper.SOURCE_NAME,
                    score=score,
                    posted_at=offer.get("posted_at"),
                )
                if saved:
                    new_count += 1

        except Exception as e:
            logger.error(f"Erreur scraper {scraper.SOURCE_NAME} : {e}", exc_info=True)

    logger.info(f"Scraping terminé : {total_scraped} offres analysées, {new_count} nouvelles sauvegardées")
    return new_count


def send_recap():
    """Récupère les nouvelles offres et envoie le récap Telegram."""
    logger.info("Envoi du récap Telegram...")
    offers = get_new_offers(limit=50)
    stats = get_stats()

    send_daily_recap(offers, stats)

    # Marquer comme notifiées
    ids = [o["id"] for o in offers]
    mark_as_notified(ids)

    logger.info(f"Récap envoyé : {len(offers)} offres notifiées")


def full_cycle():
    """Scraping + envoi récap (utilisé pour le run --once)."""
    run_scraping()
    send_recap()


def run_continuous():
    """Mode continu : scraping toutes les 6h + récap quotidien à l'heure définie."""
    logger.info("Bot démarré en mode continu")
    send_startup_message()

    # Récap quotidien à l'heure configurée (défaut 08:00)
    schedule.every().day.at(DAILY_RECAP_TIME).do(send_recap)

    # Scraping toutes les 6 heures
    schedule.every(6).hours.do(run_scraping)

    # Premier cycle immédiat au démarrage
    run_scraping()

    logger.info(f"Récap quotidien programmé à {DAILY_RECAP_TIME}")
    logger.info("En attente... (Ctrl+C pour arrêter)")

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Bot arrêté manuellement.")
            break


if __name__ == "__main__":
    # Initialisation BDD
    init_db()
    logger.info("Base de données initialisée")

    args = sys.argv[1:]

    if "--recap" in args:
        # Test : envoie le récap immédiatement
        send_recap()
    elif "--once" in args:
        # Test : un seul cycle complet
        full_cycle()
    else:
        # Mode normal : tourne en continu
        run_continuous()
