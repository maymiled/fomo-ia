# Spec Delta

## ADDED Requirements

### Requirement: Top stories Hacker News
Le système DOIT (MUST) récupérer les top stories Hacker News du moment, sans filtrage thématique, et les renvoyer triées par score décroissant, chacune avec son titre, son score, son lien Hacker News et son lien externe. Le nombre de stories renvoyées NE DOIT PAS dépasser `limit`, lui-même plafonné à 100. En cas d'échec de l'API, l'outil DOIT renvoyer une erreur lisible plutôt que de lever une exception.

#### Scenario: L'API Hacker News répond normalement
- **WHEN** l'outil `get_hackernews_top_stories` est appelé avec `limit=3` et que le top Hacker News contient plus de 3 stories
- **THEN** le résultat contient exactement 3 stories, triées par score décroissant, qu'elles parlent d'IA ou non

#### Scenario: Une story individuelle est illisible
- **WHEN** la récupération d'une story du lot échoue ou renvoie une story sans titre
- **THEN** cette story est ignorée et les autres sont renvoyées normalement

#### Scenario: L'API Hacker News ne répond pas
- **WHEN** l'appel à la liste des top stories échoue
- **THEN** l'outil renvoie une liste contenant un objet `error` explicite

## MODIFIED Requirements

### Requirement: Digest quotidien composé par la skill
La skill `daily-ai-fomo-briefing` DOIT (MUST) composer un digest markdown unique à partir des trois outils, et DOIT continuer avec les sources disponibles si une source échoue. Pour la section Hacker News, la skill DOIT sélectionner elle-même, parmi les top stories reçues, celles dont le sujet relève de l'IA (LLM, agents, modèles, outils de dev IA, vibe coding, recherche, entreprises ou matériel IA), d'après le sens du titre et non la présence d'un mot précis. Elle en garde au plus 6, par score décroissant.

#### Scenario: Toutes les sources répondent
- **WHEN** les trois outils MCP renvoient des résultats valides
- **THEN** la skill produit un digest markdown avec les trois sections (HN, repos, recherche) et une ligne TL;DR finale

#### Scenario: Une source échoue
- **WHEN** un des trois outils renvoie une erreur
- **THEN** la skill mentionne que cette source n'a pas répondu et compose quand même le digest avec les deux autres sources

#### Scenario: Une story IA sans mot-clé évident
- **WHEN** les top stories contiennent « Why LLMs fail at math » et « Nvidia unveils its next datacenter GPU »
- **THEN** les deux figurent dans la section HN du digest

#### Scenario: Une story hors sujet avec un mot ambigu
- **WHEN** les top stories contiennent « FBI agent arrested for leaking documents »
- **THEN** cette story ne figure pas dans la section HN du digest

#### Scenario: Aucune story liée à l'IA
- **WHEN** aucune des top stories reçues ne relève de l'IA
- **THEN** la section HN indique en une ligne qu'aucun sujet IA ne buzze aujourd'hui, et le reste du digest est généré normalement

## REMOVED Requirements

### Requirement: Buzz Hacker News filtré IA
**Reason** : le filtre par liste de mots-clés rate les pluriels et les sujets IA sans mot-clé, et laisse passer des faux positifs. Le tri est confié à Claude dans la skill, qui juge le sens du titre.
**Migration** : appeler `get_hackernews_top_stories` à la place de `get_hackernews_ai_buzz`, et laisser la skill (voir « Digest quotidien composé par la skill ») sélectionner les stories IA.
