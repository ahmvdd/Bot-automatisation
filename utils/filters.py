from config import KEYWORDS, IDF_ZONES, MONTPELLIER_ZONES

# Postes dev acceptés — tech pur uniquement
TECH_WHITELIST = [
    # Développement web / logiciel
    "développeur", "developer", "dev web", "dev mobile", "développement logiciel",
    "software engineer", "software developer",
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust",
    "react", "angular", "vue", "node", "backend", "frontend", "fullstack",
    "full stack", "full-stack",
    # Infrastructure / Cloud / DevOps
    "devops", "cloud", "aws", "azure", "gcp", "sre", "site reliability",
    "sysadmin", "linux",
    # Sécurité
    "cybersécurité", "cyber", "sécurité informatique", "pentesting",
    # Data / IA (côté ingénierie)
    "machine learning", "deep learning", "mlops", "data engineer",
    "data scientist", "ai engineer", "intelligence artificielle",
    # Mobile
    "android", "ios", "flutter", "kotlin", "swift",
    # Embarqué / IoT
    "embarqué", "firmware", "iot", "robotique",
]

# Postes à exclure — non-tech
TECH_BLACKLIST = [
    "communication", "marketing", "commercial", "vente", "chargé de projet rh",
    "ressources humaines", "recrutement", "comptabilité", "comptable",
    "finance", "juriste", "droit", "juridique", "audit", "achat", "achats",
    "supply chain", "logistique", "qualité", "hse", "sécurité qualité",
    "community manager", "graphiste", "designer ux", "designer ui",
    "chef de projet marketing", "responsable marketing", "brand",
    "journaliste", "rédacteur", "content", "relations publiques",
    "assistant de direction", "office manager", "secrétaire",
]


def is_tech(title: str, description: str = "") -> bool:
    """Vérifie si l'offre est un poste dev/tech pur."""
    title_lower = title.lower()

    # Blacklist — vérifiée sur le titre en priorité
    if any(kw in title_lower for kw in TECH_BLACKLIST):
        return False

    # Whitelist — titre OU description
    text = (title + " " + description).lower()
    return any(kw in text for kw in TECH_WHITELIST)


def is_alternance(title: str, description: str = "") -> bool:
    """Vérifie si l'offre est bien une alternance."""
    text = (title + " " + description).lower()
    return any(kw in text for kw in KEYWORDS)


def is_idf(location: str) -> bool:
    """Vérifie si l'offre est en Île-de-France."""
    location_lower = location.lower()
    return any(zone in location_lower for zone in IDF_ZONES)


def is_montpellier(location: str) -> bool:
    """Vérifie si l'offre est à Montpellier."""
    location_lower = location.lower()
    return any(zone in location_lower for zone in MONTPELLIER_ZONES)


def is_target_location(location: str) -> bool:
    """Vérifie si l'offre est dans une ville cible (IDF ou Montpellier)."""
    return is_idf(location) or is_montpellier(location)


def score_offer(title: str, location: str, description: str = "") -> int:
    """Score de pertinence 0-100 pour prioriser les offres."""
    score = 0
    text = (title + " " + description).lower()

    # Bonus alternance
    if "alternance" in text:
        score += 30
    if "apprentissage" in text:
        score += 20

    # Bonus localisation
    if "paris" in location.lower():
        score += 20
    elif is_idf(location):
        score += 10
    elif is_montpellier(location):
        score += 15

    # Bonus tech (plus le titre est précis, plus le score est élevé)
    priority_tech = ["python", "développeur", "developer", "cloud",
                     "machine learning", "devops", "cybersécurité", "data engineer"]
    for kw in priority_tech:
        if kw in text:
            score += 5

    return min(score, 100)
