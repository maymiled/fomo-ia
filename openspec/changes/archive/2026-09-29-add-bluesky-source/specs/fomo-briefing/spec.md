# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
