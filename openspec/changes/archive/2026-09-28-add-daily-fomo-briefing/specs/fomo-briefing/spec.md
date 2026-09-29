# Spec Delta

## Purpose

Fournir une veille quotidienne condensée sur l'actualité IA/LLM/agentique/vibe coding, agrégée depuis Hacker News, GitHub et arXiv, sans configuration ni clé API.

## ADDED Requirements

### Requirement: Buzz Hacker News filtré IA
Le système DOIT récupérer les top stories Hacker News du moment et ne conserver que celles dont le titre correspond à un vocabulaire lié à l'IA (IA, LLM, agent, vibe coding, noms de modèles/éditeurs).

#### Scenario: Une story IA est présente dans le top HN
- **WHEN** l'outil `get_hackernews_ai_buzz` est appelé et qu'au moins une story du top Hacker News contient un mot-clé IA dans son titre
- **THEN** cette story apparaît dans le résultat, avec son titre, son score et son lien

#### Scenario: Aucune story IA dans le pool observé
- **WHEN** aucune des stories observées ne contient de mot-clé IA
- **THEN** l'outil renvoie une liste vide plutôt qu'une erreur

### Requirement: Repos GitHub tendance sur un topic IA
Le système DOIT récupérer les repos GitHub les plus étoilés sur un topic donné, mis à jour dans une fenêtre de fraîcheur récente, et DOIT dégrader proprement en cas d'échec de l'API.

#### Scenario: L'API GitHub répond normalement
- **WHEN** l'outil `get_trending_ai_repos` est appelé avec un topic valide et que l'API GitHub répond 200
- **THEN** le résultat contient jusqu'à `limit` repos triés par nombre d'étoiles décroissant, chacun avec son nom complet, ses étoiles, sa description et son URL

#### Scenario: L'API GitHub est rate-limitée
- **WHEN** l'API GitHub répond avec un code d'erreur (ex: 403 pour rate limit)
- **THEN** l'outil renvoie une liste contenant un objet `error` explicite plutôt que de lever une exception

### Requirement: Derniers papiers arXiv d'une catégorie
Le système DOIT récupérer et parser les entrées les plus récentes du flux Atom arXiv pour une catégorie donnée.

#### Scenario: Le flux arXiv contient des entrées valides
- **WHEN** l'outil `get_recent_arxiv_papers` est appelé avec une catégorie valide (ex: `cs.AI`)
- **THEN** le résultat contient jusqu'à `limit` papiers, chacun avec titre nettoyé (espaces normalisés), auteurs, résumé tronqué et lien arXiv

### Requirement: Digest quotidien composé par la skill
La skill `daily-ai-fomo-briefing` DOIT composer un digest markdown unique à partir des trois outils, et DOIT continuer avec les sources disponibles si une source échoue.

#### Scenario: Toutes les sources répondent
- **WHEN** les trois outils MCP renvoient des résultats valides
- **THEN** la skill produit un digest markdown avec les trois sections (HN, repos, recherche) et une ligne TL;DR finale

#### Scenario: Une source échoue
- **WHEN** un des trois outils renvoie une erreur
- **THEN** la skill mentionne que cette source n'a pas répondu et compose quand même le digest avec les deux autres sources
