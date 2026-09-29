# Design

## Context

Le digest est composé par Claude à partir des outils MCP de `server.py`, et n'existe aujourd'hui que dans la conversation. Claude Code dispose d'un outil intégré de lecture de page web (WebFetch) et d'un outil de sous-agent (Agent). Une skill est invocable par `/<nom>`, et son corps sert d'instructions cachées. Voir proposal.md pour la motivation.

## Goals / Non-Goals

**Goals :**
- Un décryptage fidèle à la source, lisible par une non-spécialiste, sans consigne à retaper.
- Garder le contexte de la conversation principale propre : les pages brutes restent dans le sous-agent.

**Non-Goals :**
- Tester automatiquement la qualité d'un décryptage (non mockable, comme le tri HN) : on vérifie sur de vrais lancements.
- Un outil MCP de lecture de page, un historique consultable des décryptages ou une recherche plein texte dans les anciens digests.
- Le briefing automatique de 9h : un change séparé, qui s'appuiera sur `digests/`.

## Decisions

**1. Une skill, pas un prompt MCP ni une ressource MCP.**
- Un prompt MCP (`@mcp.prompt()`) apparaîtrait sous un nom long, `/mcp__fomo-ia__decrypte`, et ne peut pas orchestrer un sous-agent ni la recherche dans `digests/`.
- Une ressource MCP sert à exposer des données, ce qui n'est pas le besoin : un fichier markdown sur disque suffit, et Claude le lit directement.
- La skill suit le même modèle que `daily-ai-fomo-briefing`. Elle est découverte par Claude Code via un lien symbolique dans `.claude/skills/`.

**2. Lecture par WebFetch, pas par un nouvel outil dans `server.py`.**
- WebFetch est déjà disponible, gère le HTML et les redirections, et ne demande aucune dépendance.
- Alternative écartée : un outil `fetch_article` avec `requests` et un nettoyage HTML maison. Il faudrait un parseur HTML (une dépendance en plus, ou du fragile avec `re`), pour un gain nul dans Claude Code.
- Compromis : dans un client MCP sans WebFetch (Claude Desktop), `/decrypte` ne fonctionnerait pas. C'est accepté, puisque l'usage visé est Claude Code.

**3. Un sous-agent dédié, `lecteur-article`, lancé une fois par décryptage, qui renvoie des notes et non le texte final.**
- Défini dans `agents/lecteur-article.md` (lien dans `.claude/agents/`), au format d'agent de Claude Code : frontmatter `name`, `description`, `tools: WebFetch, Read`, `model: sonnet`, puis ses consignes de lecture.
- `tools` limite ce qu'il peut faire : il lit, il ne peut ni écrire ni exécuter. `model: sonnet` suffit pour une tâche d'extraction et coûte moins cher que le modèle principal.
- Alternative écartée : un sous-agent généraliste lancé avec une consigne dans la skill. Il serait anonyme dans l'interface, aurait accès à tous les outils (y compris l'écriture), et ses consignes de lecture seraient mêlées à celles de rédaction.
- Source hors de `.claude/` avec un lien symbolique, comme les skills, pour que l'agent survive si `.claude/` est retiré du dépôt (voir le commentaire du `.gitignore`).
- Le sous-agent lit : 1 page pour un article, jusqu'à 3 pour un thème. S'il s'agit d'un post Bluesky qui pointe vers un article, il lit aussi cet article.
- Il renvoie des notes structurées, 400 mots environ : faits, chiffres, citations courtes, auteurs, date, limites, et page illisible ou non.
- La rédaction pédagogique reste dans la skill principale, pour que le format et le ton soient toujours les mêmes quel que soit le sous-agent.
- Alternative écartée : pas de sous-agent. Plusieurs milliers de mots de page brute arriveraient dans la conversation et gonfleraient chaque échange suivant.
- Alternative écartée : un sous-agent par source pour les thèmes. C'est plus cher, pour 3 pages courtes.

**4. Où trouver la cible, par ordre de priorité :** l'URL donnée en argument, puis le digest présent dans la conversation, puis le fichier le plus récent de `digests/`, trié par nom (`AAAA-MM-JJ`, donc dans l'ordre chronologique). Pour un item HN, la source est l'URL externe, ou la page HN si l'URL est absente (Ask HN). Pour un repo, la page GitHub. Pour arXiv, la page `abs`.

**5. Digest enregistré par la skill FOMO, avec l'outil d'écriture de fichier de Claude,** dans `digests/` à la racine du projet ouvert. Pas de mémoire à gérer côté serveur, et le futur briefing planifié pourra lire ou envoyer ce fichier.

**6. `digests/` ignoré par Git :** c'est du contenu généré et personnel, qui changerait tous les jours.

## Risks / Trade-offs

- [WebFetch peut renvoyer une page tronquée ou résumée pour les pages très longues] → le sous-agent le signale, et le décryptage cite ses limites.
- [Hallucination lors de la rédaction] → règle explicite « ne rien affirmer d'absent des notes », et partie « limites » obligatoire.
- [Coût d'un sous-agent à chaque décryptage] → uniquement sur demande.
- [Skill copiée dans `~/.claude/skills/` et utilisée depuis un autre dossier] → `digests/` serait cherché dans ce dossier-là. Le README le documente.
- [Écriture du fichier refusée (permissions)] → le digest reste affiché, avec une mention.
