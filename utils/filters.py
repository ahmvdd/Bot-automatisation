from config import KEYWORDS, IDF_ZONES


def is_alternance(title: str, description: str = "") -> bool:
    """Vérifie si l'offre est bien une alternance."""
    text = (title + " " + description).lower()
    return any(kw in text for kw in KEYWORDS)


def is_idf(location: str) -> bool:
    """Vérifie si l'offre est en Île-de-France."""
    location_lower = location.lower()
    return any(zone in location_lower for zone in IDF_ZONES)


def score_offer(title: str, location: str, description: str = "") -> int:
    """Score de pertinence 0-100 pour prioriser les offres."""
    score = 0
    text = (title + " " + description).lower()

    # Bonus alternance
    if "alternance" in text:
        score += 40
    if "apprentissage" in text:
        score += 30

    # Bonus localisation Paris intra-muros
    if "paris" in location.lower():
        score += 20
    elif is_idf(location):
        score += 10

    # Bonus secteurs tech/data
    tech_keywords = ["data", "python", "développeur", "developer", "ia", "machine learning", "cloud"]
    for kw in tech_keywords:
        if kw in text:
            score += 5

    return min(score, 100)
