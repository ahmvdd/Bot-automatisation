from datetime import datetime
from typing import Optional, List
from database.models import get_connection


def save_offer(title: str, company: str, location: str, url: str,
               source: str, score: int = 0, posted_at: str = None) -> bool:
    """
    Insère une offre. Retourne True si nouvelle, False si déjà connue.
    La contrainte UNIQUE sur url gère la déduplication automatiquement.
    """
    try:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO offers (title, company, location, url, source, score, posted_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, company, location, url, source, score, posted_at)
            )
            conn.commit()
        return True
    except Exception:
        return False  # URL déjà présente → doublon ignoré


def get_new_offers(limit: int = 50):
    """Récupère les offres non encore notifiées, triées par score décroissant."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM offers
               WHERE notified = 0
               ORDER BY score DESC, scraped_at DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def mark_as_notified(offer_ids: List[int]):
    """Marque les offres comme envoyées sur Telegram."""
    if not offer_ids:
        return
    placeholders = ",".join("?" * len(offer_ids))
    with get_connection() as conn:
        conn.execute(
            f"UPDATE offers SET notified = 1 WHERE id IN ({placeholders})",
            offer_ids
        )
        conn.commit()


def get_stats() -> dict:
    """Stats pour le message récap Telegram."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM offers").fetchone()[0]
        today = conn.execute(
            "SELECT COUNT(*) FROM offers WHERE DATE(scraped_at) = DATE('now')"
        ).fetchone()[0]
        new_unseen = conn.execute(
            "SELECT COUNT(*) FROM offers WHERE notified = 0"
        ).fetchone()[0]
    return {"total": total, "today": today, "new_unseen": new_unseen}


def update_status(offer_id: int, status: str):
    """Met à jour le statut d'une offre (seen / applied / rejected)."""
    with get_connection() as conn:
        conn.execute("UPDATE offers SET status = ? WHERE id = ?", (status, offer_id))
        conn.commit()
