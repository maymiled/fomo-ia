# fomo-briefing Specification

## Purpose
Fournir une veille quotidienne condensée sur l'actualité IA/LLM/agentique/vibe coding, agrégée depuis Hacker News, Bluesky, GitHub et arXiv, sans configuration ni clé API.

## Requirements

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
La skill `daily-ai-fomo-briefing` DOIT (MUST) composer un digest markdown unique à partir des quatre outils, et DOIT continuer avec les sources disponibles si une source échoue. Pour la section Hacker News, la skill DOIT sélectionner elle-même, parmi les top stories reçues, celles dont le sujet relève de l'IA (LLM, agents, modèles, outils de dev IA, vibe coding, recherche, entreprises ou matériel IA), d'après le sens du titre et non la présence d'un mot précis. Elle en garde au plus 6, par score décroissant. Pour la section Bluesky, la skill DOIT lire la liste de comptes dans son fichier de référence, la transmettre à l'outil, puis garder au plus 5 posts qui relèvent de l'IA, par likes décroissants. Elle NE DOIT afficher une ligne « Nouveau visage » que si l'outil renvoie un compte émergent dont l'activité relève de l'IA, et au plus 2. La skill NE DOIT PAS modifier le fichier de référence d'elle-même.

#### Scenario: Toutes les sources répondent
- **WHEN** les quatre outils MCP renvoient des résultats valides
- **THEN** la skill produit un digest markdown avec les quatre sections (HN, Bluesky, repos, recherche) et une ligne TL;DR finale

#### Scenario: Une source échoue
- **WHEN** un des quatre outils renvoie une erreur
- **THEN** la skill mentionne que cette source n'a pas répondu et compose quand même le digest avec les autres sources

#### Scenario: Une story IA sans mot-clé évident
- **WHEN** les top stories contiennent « Why LLMs fail at math » et « Nvidia unveils its next datacenter GPU »
- **THEN** les deux figurent dans la section HN du digest

#### Scenario: Une story hors sujet avec un mot ambigu
- **WHEN** les top stories contiennent « FBI agent arrested for leaking documents »
- **THEN** cette story ne figure pas dans la section HN du digest

#### Scenario: Aucune story liée à l'IA
- **WHEN** aucune des top stories reçues ne relève de l'IA
- **THEN** la section HN indique en une ligne qu'aucun sujet IA ne buzze aujourd'hui, et le reste du digest est généré normalement

#### Scenario: Un jour sans nouveau visage
- **WHEN** l'outil Bluesky ne renvoie aucun compte émergent
- **THEN** le digest ne contient aucune ligne « Nouveau visage »

#### Scenario: Un nouveau visage perce
- **WHEN** l'outil Bluesky renvoie un compte émergent qui publie sur l'IA
- **THEN** le digest affiche une ligne « Nouveau visage » avec son nom, son handle et les experts qui l'ont partagé, et le fichier de référence reste inchangé

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

### Requirement: Posts Bluesky d'une liste d'experts
Le système DOIT (MUST) récupérer, pour une liste de comptes Bluesky fournie à l'appel, les posts publiés par ces comptes sur les `hours` dernières heures (48 par défaut), sans filtrage thématique. Chaque post DOIT comporter l'auteur, le texte, le nombre de likes, le nombre de reposts, la date et un lien bsky.app. Les posts DOIVENT être triés par likes décroissants. Les simples reposts d'un expert ne sont pas des posts de cet expert. Le système NE DOIT PAS demander de clé API. La liste de comptes est plafonnée à 30.

#### Scenario: Des experts ont posté récemment
- **WHEN** l'outil `get_bluesky_buzz` est appelé avec deux comptes, qui ont publié chacun un post il y a moins de 48 h et un post il y a 5 jours
- **THEN** le résultat contient seulement les deux posts récents, triés par likes décroissants, chacun avec son lien bsky.app

#### Scenario: Un compte suivi est indisponible
- **WHEN** la récupération des posts d'un des comptes échoue (compte supprimé, erreur réseau)
- **THEN** les posts des autres comptes sont renvoyés normalement et ce compte est signalé comme indisponible

#### Scenario: Bluesky ne répond pour aucun compte
- **WHEN** la récupération échoue pour tous les comptes, ou la liste de comptes est vide
- **THEN** l'outil renvoie un objet `error` explicite plutôt que de lever une exception

### Requirement: Comptes Bluesky émergents
Le système DOIT (MUST) signaler comme « émergent » tout compte qui n'est pas dans la liste fournie et qui a été repartagé ou cité par au moins 3 comptes différents de la liste sur les 7 derniers jours. Pour chaque compte émergent, il DOIT indiquer le handle, le nom affiché, le nombre d'experts distincts et leurs handles, ainsi qu'un exemple de post partagé. Si aucun compte n'atteint ce seuil, la liste des comptes émergents DOIT être vide.

#### Scenario: Un compte perce
- **WHEN** trois experts différents de la liste ont repartagé ou cité des posts d'un même compte extérieur au cours des 7 derniers jours
- **THEN** ce compte figure parmi les comptes émergents, avec 3 experts et leurs handles

#### Scenario: Pas assez d'experts
- **WHEN** un compte extérieur n'a été repartagé que par deux experts, même plusieurs fois chacun
- **THEN** ce compte ne figure pas parmi les comptes émergents

#### Scenario: Les experts se repartagent entre eux
- **WHEN** des experts de la liste repartagent des posts d'un autre expert de la liste
- **THEN** cet expert n'est jamais signalé comme émergent

### Requirement: Enregistrement du digest
Une fois le digest composé et affiché, la skill `daily-ai-fomo-briefing` DOIT (MUST) l'enregistrer tel quel, liens compris, dans `digests/AAAA-MM-JJ.md` à la racine du projet, en créant le dossier si besoin. Un nouveau digest le même jour DOIT remplacer le fichier de ce jour. Si l'écriture échoue, le digest DOIT quand même être affiché, avec une mention de l'échec. Chaque élément des sections HN, Bluesky et Recherche DOIT comporter le lien de sa source. Pour les repos, le nom `owner/repo` suffit à reconstituer le lien GitHub.

#### Scenario: Premier digest du jour
- **WHEN** l'utilisatrice demande son FOMO le 29/09/2026
- **THEN** le fichier `digests/2026-09-29.md` contient le digest affiché, avec tous ses liens

#### Scenario: Un papier de recherche est retrouvable
- **WHEN** le digest enregistré contient un papier dans « Recherche fraîche »
- **THEN** la ligne de ce papier contient son lien arXiv, pour que `/decrypte` puisse le lire depuis une autre conversation

#### Scenario: Deuxième digest le même jour
- **WHEN** l'utilisatrice redemande son FOMO plus tard le même jour
- **THEN** `digests/2026-09-29.md` contient uniquement le digest le plus récent
