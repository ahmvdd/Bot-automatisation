# 🤖 Bot de Veille Alternances

Un bot Python qui scrape automatiquement les offres d'alternance tech en **Île-de-France** et à **Montpellier**, filtre les résultats pertinents et envoie un récap quotidien sur **Telegram**.

---

## ✨ Fonctionnalités

- 🔍 **Scraping automatique** toutes les 6 heures sur Welcome to the Jungle et France Travail
- 🧠 **Filtrage intelligent** — alternance uniquement, secteur tech, zones géographiques ciblées
- 📊 **Scoring des offres** selon la pertinence (titre, localisation, description)
- 📩 **Récap Telegram quotidien** à 08h00 avec les nouvelles offres
- 🗄️ **Base de données SQLite** pour éviter les doublons
- ☁️ **Déploiement cloud** sur Fly.io via GitHub Actions

---

## 🏗️ Architecture

```
├── main.py                  # Point d'entrée principal
├── config.py                # Configuration (zones, mots-clés, horaires)
├── scrapers/
│   ├── welcome_to_jungle.py # Scraper WTJ
│   └── france_travail.py    # Scraper France Travail (API)
├── notifications/
│   └── telegram_bot.py      # Envoi des messages Telegram
├── database/
│   ├── models.py            # Schéma base de données
│   └── repository.py        # Requêtes SQLite
├── utils/
│   ├── filters.py           # Filtres alternance / tech / localisation
│   └── logger.py            # Logger
├── Dockerfile               # Image Docker pour le déploiement
├── fly.toml                 # Config Fly.io
└── .github/workflows/
    └── fly.yml              # CI/CD GitHub Actions → Fly.io
```

---

## 🚀 Déploiement

Le bot est déployé sur **Fly.io** et se redéploie automatiquement à chaque `git push` via **GitHub Actions**.

```
git push origin main
       ↓
GitHub Actions déclenche le workflow
       ↓
Fly.io rebuild et relance le bot
       ↓
Bot tourne 24/7 ☁️
```

---

## ⚙️ Installation locale

### Prérequis
- Python 3.11+
- Un bot Telegram (via [@BotFather](https://t.me/BotFather))

### Setup

```bash
# Cloner le repo
git clone https://github.com/ahmvdd/Bot-automatisation.git
cd Bot-automatisation

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Remplir TELEGRAM_TOKEN et TELEGRAM_CHAT_ID dans .env
```

### Lancer le bot

```bash
# Mode continu (scraping toutes les 6h + récap à 08h00)
python3 main.py

# Un seul cycle de scraping (test)
python3 main.py --once

# Envoyer le récap Telegram immédiatement (test)
python3 main.py --recap
```

---

## 🔐 Variables d'environnement

| Variable | Description |
|----------|-------------|
| `TELEGRAM_TOKEN` | Token du bot Telegram (via BotFather) |
| `TELEGRAM_CHAT_ID` | ID du chat Telegram où envoyer les récaps |
| `DB_PATH` | Chemin vers la base de données SQLite (défaut: `data/offers.db`) |

---

## 🛠️ Stack technique

| Technologie | Usage |
|-------------|-------|
| Python 3.11 | Langage principal |
| BeautifulSoup4 | Scraping HTML |
| python-telegram-bot | Envoi des notifications |
| SQLite | Stockage des offres |
| Docker | Conteneurisation |
| Fly.io | Hébergement cloud |
| GitHub Actions | CI/CD automatisé |

---

## 📍 Zones ciblées

- **Île-de-France** — Paris, 92, 93, 94, 95, 77, 78, 91 et grandes villes (Neuilly, Boulogne, Versailles...)
- **Montpellier** — Hérault (34)

---

*Projet réalisé dans le cadre d'une recherche d'alternance en tech.*
