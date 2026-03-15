# Roadmap — Bot de veille alternances

## Fonctionnalités actuelles

- Scraping WelcomeToTheJungle + France Travail
- Filtrage : alternance + localisation (IDF / Montpellier) + tech pur (dev, data, devops, cyber...)
- Score de pertinence par offre
- Notification Telegram (récap quotidien à 08h00)
- BDD SQLite locale pour éviter les doublons

---

## Fonctionnalités prévues

### Microservice auto-candidature *(priorité haute)*

**Objectif :** Pour chaque offre jugée pertinente (score ≥ seuil), déclencher automatiquement une candidature.

**Architecture envisagée :**
- Microservice indépendant, appelé par le bot via HTTP ou une queue (ex. Redis, RabbitMQ)
- Le bot envoie l'offre (titre, URL, entreprise, description) au microservice
- Le microservice :
  1. Génère une lettre de motivation personnalisée (LLM — ex. Claude API)
  2. Remplit et soumet le formulaire de candidature (Playwright / Selenium)
  3. Confirme le statut de la candidature au bot (succès / échec)
- Le bot logue le résultat en BDD et notifie via Telegram

**Points de vigilance :**
- Certains sites bloquent les soumissions automatisées (Cloudflare, captchas) — prévoir un fallback manuel
- Ajouter un champ `auto_applied` dans la table `offers` pour traçabilité
- Exposer un endpoint de contrôle (`/dry-run`) pour tester sans soumettre réellement

**Interface bot Telegram à prévoir :**
- Bouton "Postuler" inline sur chaque offre notifiée (déclenche le microservice à la demande)
- Commande `/candidatures` pour voir l'historique des candidatures envoyées

---

*Document mis à jour le 2026-03-15*
