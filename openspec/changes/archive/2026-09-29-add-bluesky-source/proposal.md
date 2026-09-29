# Proposal

## Why

Les trois sources actuelles (Hacker News, GitHub, arXiv) donnent les articles, les repos et les papiers, mais pas « ce dont parlent les gens du milieu ». C'est le rôle que jouait Twitter/X, dont l'API de lecture est payante. Bluesky, où beaucoup de chercheurs et de devs IA ont migré, se lit gratuitement et sans clé. Autre besoin : repérer les personnes qui percent (le créateur d'un projet qui explose, inconnu la veille) sans avoir à remplir une liste à la main, mais aussi sans suggestion artificielle les jours où rien ne se passe.

## What Changes

- Nouvel outil MCP `get_bluesky_buzz(handles, hours=48)`. Il reçoit une liste de comptes Bluesky à suivre et renvoie deux choses :
  - leurs posts récents (texte, likes, reposts, lien), triés par likes. Rien n'est filtré par thème ;
  - les **comptes émergents** : des comptes hors de la liste, repartagés ou cités par **au moins 3 experts différents** sur les **7 derniers jours**.
- Nouveau fichier de référence de la skill, `references/bluesky-accounts.md`. Il contient la liste de base de 13 comptes vérifiés le 28/09/2026, que l'utilisatrice peut modifier sans toucher au code.
- La skill lit cette liste, appelle l'outil et ajoute une section « 🦋 Ça parle sur Bluesky ». Claude y choisit au plus 5 posts qui parlent vraiment d'IA. Une ligne « 👀 Nouveau visage » apparaît **seulement** si un compte émergent pertinent existe ce jour-là. C'est une suggestion : il n'y a aucun ajout automatique à la liste.
- Le digest passe de 3 à 4 sources, et une source en panne n'empêche toujours pas les autres.

## Capabilities

### New Capabilities
_Aucune._

### Modified Capabilities
- `fomo-briefing` : ajout des exigences « Posts Bluesky d'une liste d'experts » et « Comptes Bluesky émergents ». L'exigence « Digest quotidien composé par la skill » est modifiée pour inclure la section Bluesky et la règle du nouveau visage.

## Impact

- `server.py` : un nouvel outil, sans nouvelle dépendance (`requests` suffit). Il fait 1 requête HTTP par compte suivi, soit 13 aujourd'hui, en parallèle.
- `skills/daily-ai-fomo-briefing/` : `SKILL.md` (nouvelle étape et nouvelle section), nouveau `references/bluesky-accounts.md`.
- `test_server.py` : nouveaux tests mockés.
- `spec/fomo_briefing.feature`, `README.md`, `CLAUDE.md` (qui parle de « 3 outils »), et le « Purpose » de la spec principale (qui cite 3 sources) : à aligner.
- Dépendance externe : l'API publique de Bluesky (`public.api.bsky.app`), en lecture seule et sans clé. La recherche plein texte y est fermée aux anonymes (vérifié : 403), d'où l'approche par liste de comptes.
