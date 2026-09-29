# Design

## Context

Trois sources publiques, trois formats différents (JSON simple pour HN et GitHub, Atom/XML pour arXiv), aucune ne nécessitant de clé API. La contrainte principale est le rate limit de l'API de recherche GitHub sans authentification (60 requêtes/heure), qui rend l'outil `get_trending_ai_repos` plus fragile que les deux autres.

## Goals / Non-Goals

**Goals:**
- Un digest lisible en moins d'une minute, pas un rapport exhaustif.
- Zéro clé API à configurer pour que le projet reste copiable et utilisable tel quel.
- Chaque source doit pouvoir échouer indépendamment sans faire échouer tout le briefing.

**Non-Goals:**
- Pas de déduplication entre sources.
- Pas de mémoire d'un jour à l'autre (pas de detection de "déjà vu hier").
- Pas de vérification de la fiabilité des titres (HN est volontairement putaclic parfois).

## Decisions

- **Filtrage par mots-clés plutôt que par catégorie HN dédiée** : HN n'a pas de catégorie "AI" native, donc `get_hackernews_ai_buzz` récupère un pool large de top stories (120) et filtre par regex sur le titre. Alternative écartée : scraper un site d'agrégation tiers, moins stable dans le temps qu'une regex sur l'API officielle.
- **GitHub sans authentification** : plus simple à mettre en place (zéro secret dans le repo), au prix d'un rate limit bas. Alternative : un token personnel en variable d'environnement, documentée dans le README comme amélioration possible plutôt qu'implémentée par défaut.
- **arXiv via parsing XML natif (`xml.etree`) plutôt qu'une lib tierce** (`feedparser`) : garde les dépendances du projet à `mcp` + `requests` uniquement.
- **Erreurs renvoyées comme données, pas comme exceptions qui remontent** : `get_trending_ai_repos` renvoie `[{"error": ...}]` plutôt que de lever une exception, pour que la skill qui orchestre les trois outils puisse continuer avec les sources qui répondent.

## Risks / Trade-offs

- Rate limit GitHub (60/h) : acceptable pour un usage personnel quotidien, pas pour un usage partagé par toute une équipe sans token.
- Le filtrage par mots-clés sur HN peut laisser passer du bruit (ex: un titre contenant "agent" sans rapport avec l'IA) — accepté comme compromis simplicité/pertinence pour un projet perso.
