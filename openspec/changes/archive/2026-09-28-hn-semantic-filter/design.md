# Design

## Context

Aujourd'hui, `get_hackernews_ai_buzz` (`server.py:53`) récupère les 120 premières top stories, soit 121 requêtes HTTP en parallèle, puis garde celles dont le titre matche la regex `AI_KEYWORDS`. Claude ne voit donc que les « gagnants » de la regex. Voir proposal.md pour les défauts de ce filtre.

Contrainte du projet : zéro clé API. Un classement sémantique côté serveur (embeddings, appel à un LLM) demanderait une dépendance ou une clé en plus. En revanche, Claude est déjà dans la boucle au moment de composer le digest.

## Goals / Non-Goals

**Goals :**
- Le serveur fournit des données brutes, et Claude, via la skill, fait la sélection thématique.
- Garder un serveur simple, déterministe et testable sans réseau.

**Non-Goals :**
- Tester automatiquement la qualité du jugement de Claude : ce n'est pas faisable avec des mocks. On vérifie sur un vrai lancement (tâche 4.1).
- Dédoublonner avec GitHub et arXiv, ou garder une mémoire entre les jours : inchangé.

## Decisions

**1. La sélection se fait dans la skill, pas dans le serveur.**
- Alternative écartée : le serveur appelle lui-même un LLM. Il faudrait une clé API et le serveur ne serait plus testable simplement.
- Alternative écartée : filtre par embeddings en local. Il faudrait une grosse dépendance (modèle, torch), contraire à « dépendances limitées à `mcp` + `requests` ».
- Alternative écartée : garder la regex et l'élargir. C'était la première idée (pluriels). Elle reste une course sans fin après les mots manquants.

**2. Nouveau nom d'outil : `get_hackernews_top_stories`.** L'outil ne filtre plus sur l'IA, donc « ai_buzz » serait trompeur. Or le nom et la docstring sont ce que Claude voit de l'outil. Le changement est cassant, mais le seul appelant est la skill, mise à jour dans le même change.

**3. Taille du lot : `limit` par défaut 30, plafonné à 100 ; la skill demande 60.** Il faut un compromis. Plus de stories, c'est plus de chances d'attraper les sujets IA. Mais c'est aussi plus de requêtes HTTP (1 + `limit`) et plus de texte à lire pour Claude : 60 titres courts, c'est quelques milliers de tokens, acceptable. On passe de 121 requêtes à 61. Le plafond évite qu'un appel demande les 500 stories de l'API.

**4. On récupère les `limit` premières stories du classement HN, puis on les trie par score.** C'est le comportement actuel, sans le filtre. Le tri par score reste cohérent avec l'affichage « (X pts) » du digest.

**5. La consigne de sélection dans la skill est formulée par sujet, pas par mots.** Elle liste les domaines (LLM, agents, modèles, outils de dev IA, vibe coding, recherche, entreprises ou matériel IA). Elle demande d'écarter les homonymes (« FBI agent ») et d'être inclusive en cas de doute sur un titre clairement tech/IA.

## Risks / Trade-offs

- [Le choix de Claude varie un peu d'un lancement à l'autre] → assumé. Le digest est une veille, pas une donnée de référence.
- [Un sujet IA classé au-delà de la 60ᵉ top story est manqué] → même limite qu'avant avec 120. Ajustable via `limit` dans la skill sans toucher au serveur.
- [Plus de contexte consommé par Claude] → environ 60 lignes titre/score/URL, négligeable face au reste du digest.
- [Changement cassant du nom d'outil] → un seul appelant, mis à jour dans le même change. Le serveur est déclaré en local (`.mcp.json`) : il suffit de reconnecter via `/mcp`.
- [Delta MODIFIED/REMOVED sur une spec pas encore archivée] → archiver `add-daily-fomo-briefing` d'abord (tâche 1.1).
