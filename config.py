import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DB_PATH = os.getenv("DB_PATH", "data/offers.db")

# Mots-clés pour filtrer les offres d'alternance
KEYWORDS = [
    "alternance", "apprentissage", "contrat d'apprentissage",
    "contrat de professionnalisation", "alternant"
]

# Zones géographiques ciblées
IDF_ZONES = [
    "paris", "île-de-france", "idf", "92", "93", "94", "95", "77", "78", "91",
    "hauts-de-seine", "seine-saint-denis", "val-de-marne", "val-d'oise",
    "seine-et-marne", "yvelines", "essonne", "neuilly", "boulogne",
    "vincennes", "créteil", "versailles", "nanterre", "montreuil"
]

MONTPELLIER_ZONES = [
    "montpellier", "hérault", "34", "montpelier",
]

TARGET_ZONES = IDF_ZONES + MONTPELLIER_ZONES

# Heure d'envoi du récap quotidien (format HH:MM)
DAILY_RECAP_TIME = "08:00"
