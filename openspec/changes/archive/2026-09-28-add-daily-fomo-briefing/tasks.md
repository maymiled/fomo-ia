# Tasks

## 1. Serveur MCP

- [x] 1.1 Outil `get_hackernews_ai_buzz` (top stories HN filtrées par mots-clés IA)
- [x] 1.2 Outil `get_trending_ai_repos` (recherche GitHub par topic + fraîcheur)
- [x] 1.3 Outil `get_recent_arxiv_papers` (parsing du flux Atom arXiv)
- [x] 1.4 Gestion d'erreur gracieuse sur l'outil GitHub (rate limit sans token)

## 2. Skill d'orchestration

- [x] 2.1 `SKILL.md` `daily-ai-fomo-briefing` qui appelle les trois outils et compose le digest
- [x] 2.2 Format de sortie markdown fixe (sections HN / repos / recherche + TL;DR)

## 3. Vérification

- [x] 3.1 Tests avec mocks pour la logique de filtrage/parsing (`test_server.py`), sans dépendre du réseau
- [x] 3.2 Test en conditions réelles (vrais appels réseau) sur une machine avec accès internet non restreint
- [x] 3.3 Revue de code assistée par IA du diff final (voir `REVIEW.md`) — incohérence de gestion d'erreur trouvée et corrigée
