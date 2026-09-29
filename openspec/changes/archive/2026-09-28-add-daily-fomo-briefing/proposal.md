# Proposal

## Why

Suivre l'actualité IA/LLM/agentique/vibe coding au jour le jour demande de checker plusieurs sources différentes (Hacker News, GitHub, arXiv) à la main, chacune avec son propre format et son propre bruit à filtrer. Sur un sujet qui bouge aussi vite, ce temps de veille manuel est le premier réflexe qu'on abandonne dès qu'on est chargé — alors que c'est justement là-dessus qu'on ne veut jamais être largué. Le but : un digest du jour généré en un appel, à partir de sources publiques, sans clé API à gérer.

## What Changes

Ajout d'une capacité "fomo-briefing" : un serveur MCP qui expose trois outils de récupération de données (Hacker News, GitHub trending, arXiv), et une Claude Skill qui les orchestre en un digest markdown lisible en moins d'une minute.

## Capabilities

### New Capabilities
- `fomo-briefing`: récupération et mise en forme d'une veille quotidienne IA/LLM/vibe coding à partir de trois sources publiques (Hacker News, GitHub, arXiv), exposée comme outils MCP et orchestrée par une Claude Skill.

### Modified Capabilities
_Aucune — premier changement du projet._

## Impact

- Nouveau fichier `server.py` (serveur MCP, SDK officiel `mcp`, dépendance `requests`).
- Nouvelle skill `skills/daily-ai-fomo-briefing/SKILL.md`.
- Dépendances externes : API publique Hacker News (Firebase), API de recherche GitHub (non authentifiée, donc limitée à 60 requêtes/heure), API arXiv. Aucune clé secrète à gérer.
