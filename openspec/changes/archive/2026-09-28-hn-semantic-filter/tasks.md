# Tasks

## 1. Prérequis OpenSpec

- [x] 1.1 Archiver `add-daily-fomo-briefing` pour créer `openspec/specs/fomo-briefing/spec.md`, et vérifier que `openspec list --specs` affiche `fomo-briefing`

## 2. Serveur : outil HN sans filtre

- [x] 2.1 Réécrire dans `test_server.py` les tests HN pour `get_hackernews_top_stories` : un titre non-IA est renvoyé, le tri par score est décroissant, `limit=3` sur 5 stories en renvoie 3, une story sans titre est ignorée, et l'échec de `topstories.json` renvoie `[{"error": ...}]`. Vérifier qu'ils échouent avant l'étape 2.2.
- [x] 2.2 Dans `server.py`, remplacer `get_hackernews_ai_buzz` par `get_hackernews_top_stories(limit=30)` (plafond 100, récupère les `limit` premiers IDs), supprimer `AI_KEYWORDS` (et l'import `re` s'il ne sert plus), et mettre à jour la docstring de l'outil et celle du module. Vérifier que `python test_server.py` passe entièrement.

## 3. Skill et documentation

- [x] 3.1 Mettre à jour `skills/daily-ai-fomo-briefing/SKILL.md` : appel `get_hackernews_top_stories(limit=60)`, consigne de sélection par sujet (au plus 6, par score, homonymes écartés), ligne « rien d'IA aujourd'hui » si aucune story ne convient. Vérifier par relecture que chaque scénario de la spec « Digest quotidien » y est couvert.
- [x] 3.2 Aligner `spec/fomo_briefing.feature` : scénarios « story IA sans mot-clé », « homonyme hors sujet » et « aucune story IA » reformulé. Aligner aussi `README.md` : commande d'exemple et description de l'outil HN. Vérifier avec `grep -rn "ai_buzz\|AI_KEYWORDS"` qu'il ne reste aucune référence hors `openspec/changes/archive` et `REVIEW.md` (qui est un historique).
- [x] 3.3 Lancer `openspec validate hn-semantic-filter` et vérifier qu'il ne remonte aucune erreur.

## 4. Vérification réelle

- [x] 4.1 Reconnecter `fomo-ia` via `/mcp`, lancer « fais-moi le FOMO IA du jour » et vérifier : l'outil appelé est le nouveau, la section HN ne contient que des sujets IA, et au moins un article sans mot-clé de l'ancienne liste y figure, si le top du jour en contient un.
