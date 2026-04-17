"""
Notifications Telegram — récap quotidien des nouvelles offres d'alternance.
"""
import asyncio
import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils.logger import get_logger

logger = get_logger("telegram")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def _send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Envoie un message Telegram (synchrone, pas de dépendance async)."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID manquant dans .env")
        return False
    try:
        resp = requests.post(
            f"{BASE_URL}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"[Telegram] Erreur envoi : {e}")
        return False


def send_daily_recap(offers: list[dict], stats: dict) -> bool:
    """
    Envoie le récap quotidien avec toutes les nouvelles offres.
    Format : header de stats + liste des offres groupées.
    """
    if not offers:
        message = (
            f"👋 <b>Bonjour !</b>\n"
            f"📅 {datetime.now().strftime('%A %d %B %Y')}\n\n"
            "🤖 Le bot tourne correctement.\n"
            "🔍 Pas de nouvelle offre depuis hier.\n\n"
            f"📊 Total en base : <b>{stats.get('total', 0)}</b> offres\n"
            f"🕐 Prochain scan dans ~6h"
        )
        return _send_message(message)

    # Header
    lines = [
        "🎯 <b>Récap Alternances Île-de-France</b>",
        f"📅 {datetime.now().strftime('%A %d %B %Y')}",
        "",
        f"✨ <b>{len(offers)} nouvelle(s) offre(s)</b> trouvée(s)",
        f"📊 Total en base : {stats.get('total', 0)} | Aujourd'hui : {stats.get('today', 0)}",
        "─" * 32,
        "",
    ]

    # Top offres (max 10 par message pour lisibilité)
    top_offers = sorted(offers, key=lambda x: x.get("score", 0), reverse=True)[:10]

    for i, offer in enumerate(top_offers, 1):
        score = offer.get("score", 0)
        stars = "⭐" * (score // 25) if score > 0 else ""
        lines += [
            f"<b>{i}. {offer['title']}</b>",
            f"🏢 {offer.get('company', 'N/A')}",
            f"📍 {offer.get('location', 'N/A')}",
            f"🔗 <a href='{offer['url']}'>Voir l'offre</a>  {stars}",
            "",
        ]

    if len(offers) > 10:
        lines.append(f"<i>... et {len(offers) - 10} autres offres en base de données.</i>")

    lines += [
        "─" * 32,
        "🤖 <i>Bot Alternances IDF — mise à jour automatique</i>",
    ]

    message = "\n".join(lines)

    # Telegram limite à 4096 caractères par message
    if len(message) > 4000:
        _send_message(message[:4000] + "\n\n<i>[Message tronqué]</i>")
    else:
        _send_message(message)

    # Envoyer le reste des offres si > 10
    if len(offers) > 10:
        _send_remaining_offers(offers[10:])

    return True


def _send_remaining_offers(offers: list[dict]):
    """Envoie les offres au-delà des 10 premières dans un second message."""
    lines = ["📋 <b>Suite des offres :</b>\n"]
    for i, offer in enumerate(offers, 11):
        lines += [
            f"<b>{i}. {offer['title']}</b> — {offer.get('company', 'N/A')}",
            f"📍 {offer.get('location', 'N/A')} | <a href='{offer['url']}'>Lien</a>",
            "",
        ]
    _send_message("\n".join(lines))


def send_alert(offer: dict) -> bool:
    """Alerte instantanée pour une offre à très fort score (optionnel)."""
    message = (
        f"🚨 <b>Offre prioritaire détectée !</b>\n\n"
        f"<b>{offer['title']}</b>\n"
        f"🏢 {offer.get('company', 'N/A')}\n"
        f"📍 {offer.get('location', 'N/A')}\n"
        f"⭐ Score : {offer.get('score', 0)}/100\n\n"
        f"🔗 <a href='{offer['url']}'>Postuler maintenant</a>"
    )
    return _send_message(message)


def send_startup_message() -> bool:
    """Message envoyé au démarrage du bot pour confirmer qu'il tourne."""
    message = (
        "✅ <b>Bot Alternances IDF — démarré</b>\n"
        f"🕐 {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"
        "📡 Scraping actif (toutes les 6h)\n"
        "📬 Récap quotidien à <b>08h00</b>\n"
        "💬 Bonjour envoyé chaque matin même sans offres\n\n"
        "Tout roule. 🤖"
    )
    return _send_message(message)
