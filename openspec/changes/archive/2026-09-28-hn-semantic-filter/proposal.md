# Proposal

## Why

Le tri des articles Hacker News se fait aujourd'hui avec une liste de mots-clés, et cette liste rate beaucoup de choses. Les pluriels ne passent pas (« Why LLMs fail », « Coding agents »), et un article IA sans mot de la liste non plus (« Nvidia », « DeepSeek », « Cursor »). À l'inverse, des titres hors sujet passent (« FBI agent arrested »). Or Claude lit déjà tous les résultats pour écrire le digest et, lui, comprend le sens d'un titre. Autant lui confier le tri plutôt que de rallonger sans fin une liste de mots.

## What Changes

- **BREAKING** : l'outil MCP `get_hackernews_ai_buzz` est remplacé par `get_hackernews_top_stories`. Le nouvel outil ne filtre plus rien : il renvoie les top stories du moment (titre, score, liens), triées par score décroissant.
- Suppression de la liste de mots-clés `AI_KEYWORDS`.
- La skill `daily-ai-fomo-briefing` récupère un lot plus large de stories. Claude y choisit lui-même celles qui parlent vraiment d'IA/LLM/agents/vibe coding (sens du titre, pas mots exacts), dans la limite de 6.
- Si aucune story n'est liée à l'IA, la section HN du digest le dit en une ligne au lieu d'être vide.
- Moins de requêtes HTTP vers Hacker News : on récupère le lot demandé (60 par défaut dans la skill) au lieu de 120 stories systématiquement.

## Capabilities

### New Capabilities
_Aucune._

### Modified Capabilities
- `fomo-briefing` : l'exigence « Buzz Hacker News filtré IA » est retirée au profit de « Top stories Hacker News » (sans filtre), et l'exigence « Digest quotidien composé par la skill » inclut désormais la sélection des stories IA par Claude.

## Impact

- `server.py` : outil HN renommé et simplifié, regex supprimée. Les outils GitHub et arXiv ne changent pas.
- `skills/daily-ai-fomo-briefing/SKILL.md` : nouvel appel et consigne de sélection.
- `test_server.py` : les tests du filtre sont remplacés par des tests sur le tri, la limite et la gestion d'erreur.
- `spec/fomo_briefing.feature`, `README.md`, docstring de `server.py` : à aligner.
- Tout client MCP qui appelait `get_hackernews_ai_buzz` doit passer au nouveau nom. Dans ce projet, c'est seulement la skill.
- Prérequis OpenSpec : `add-daily-fomo-briefing` doit être archivé avant, pour que la spec `fomo-briefing` existe dans `openspec/specs/`.
