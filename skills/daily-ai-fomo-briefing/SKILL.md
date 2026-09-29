---
name: daily-ai-fomo-briefing
description: Use this skill when the user asks for their daily AI news briefing, a "veille IA" / "FOMO check", or wants a quick digest of what's new in AI, LLMs, agents or vibe coding today.
---

# Daily AI FOMO briefing

Tu es en train de produire une veille quotidienne courte et dense sur l'actualité IA/LLM/agentique/vibe coding, à partir des outils MCP du serveur `fomo-ia` (voir `server.py` dans ce même projet) :

- `get_hackernews_top_stories` — top stories Hacker News du moment, tous sujets confondus (c'est toi qui tries)
- `get_trending_ai_repos` — repos GitHub qui montent sur un topic IA
- `get_recent_arxiv_papers` — derniers papiers de recherche
- `get_bluesky_buzz` — posts récents d'experts IA sur Bluesky, et comptes qui émergent autour d'eux

## Étapes

1. Appelle `get_hackernews_top_stories(limit=60)`, puis choisis toi-même les stories qui parlent vraiment d'IA :
   - Juge le **sujet** d'après le sens du titre, pas la présence d'un mot précis. Compte comme IA : LLM et modèles, agents, outils de dev IA et vibe coding, recherche, entreprises IA (OpenAI, Anthropic, Mistral…), matériel IA (GPU, puces), régulation et débats sur l'IA.
   - Écarte les homonymes hors sujet (« FBI agent », « real estate agents », « AI » comme initiales d'autre chose).
   - En cas de doute sur un titre tech qui touche peut-être à l'IA, garde-le.
   - Garde-en **au plus 6**, par score décroissant.
   - Si aucune ne convient, écris sous le titre de section une seule ligne : « Rien d'IA qui buzze sur HN aujourd'hui. »
2. Lis la liste des comptes suivis dans `references/bluesky-accounts.md` (dans le dossier de cette skill), puis appelle `get_bluesky_buzz(handles=[...tous les handles de la liste...])`. Dans le résultat :
   - `posts` : garde **au plus 5** posts qui parlent vraiment d'IA (mêmes critères qu'à l'étape 1 : les experts postent aussi sur d'autres sujets), par likes décroissants. Résume chaque post en une phrase, en français. Si aucun ne convient : « Rien de marquant côté experts aujourd'hui. »
   - `rising` : ce sont des comptes hors liste repartagés par au moins 3 experts cette semaine. Il est souvent vide, et dans ce cas tu n'écris **aucune** ligne « Nouveau visage ». Sinon, garde-en **au plus 2** dont l'activité relève de l'IA (une personne ou un projet qui perce, pas un média généraliste), avec la raison en une phrase, tirée de `sample_post`.
   - Ne modifie **jamais** `references/bluesky-accounts.md` de toi-même : un nouveau visage est une suggestion. L'utilisatrice dira « ajoute-le » si elle veut le suivre.
3. Appelle `get_trending_ai_repos(topic="llm", days=7, limit=5)`. Si l'utilisateur mentionne un sujet précis (agents, vibe coding, RAG...), relance l'appel avec ce topic à la place de `"llm"`.
4. Appelle `get_recent_arxiv_papers(category="cs.AI", limit=3)`.
5. Si un des quatre outils renvoie une erreur (champ `error` dans la réponse), ne bloque pas le reste du briefing : mentionne juste que cette source n'a pas répondu, et continue avec les autres. Si `unavailable` n'est pas vide, n'en parle pas dans le digest.
6. Compose un digest markdown, dans cet ordre, avec ce format exact :

```markdown
# FOMO IA — {date du jour}

## 🔥 Ça buzz sur HN
- **{titre}** ({score} pts) — {url ou lien HN}
...

## 🦋 Ça parle sur Bluesky
- **{nom de l'expert}** — {idée du post en une phrase} ({likes} ❤️) — {url}
...

👀 **Nouveau visage** : **{display_name}** (@{handle}) — repartagé par {expert_count} de tes experts cette semaine ({prénoms des experts}) — {pourquoi, en une phrase}. Dis « ajoute-le » pour le suivre.

## 📦 Repos qui montent
- **{owner/repo}** ({stars}⭐) — {description}
...

## 📄 Recherche fraîche
- **{titre}** — {auteurs, format "A. Nom et al."} — {résumé en une phrase} — {url}
...
```

7. Garde chaque item à une ligne, pas de paragraphe. L'objectif est un scan en moins de 60 secondes, pas un rapport détaillé.
8. Termine toujours par une ligne "TL;DR" d'une phrase qui résume la tendance du jour (ex: "Aujourd'hui : tout le monde parle de loop engineering et de specs versionnées, pas grand chose de neuf côté recherche.").

La ligne « 👀 Nouveau visage » n'apparaît que si l'étape 2 en a retenu un. Sinon, pas de ligne du tout.

9. Une fois le digest affiché, enregistre-le tel quel (liens compris) dans `digests/AAAA-MM-JJ.md` à la racine du projet ouvert, avec la date du jour (ex. `digests/2026-09-29.md`). Crée le dossier s'il n'existe pas, et remplace le fichier s'il existe déjà (on ne garde que le dernier digest du jour). C'est ce fichier que `/decrypte` relira dans une autre conversation. Si l'écriture échoue, ajoute juste une ligne sous le digest : « (Digest non enregistré : {raison}) ».

## Ce que cette skill ne fait pas

Elle ne filtre pas les doublons entre les quatre sources, ne vérifie pas la fiabilité des titres HN (souvent putaclic), et ne fait pas de suivi dans le temps (pas de mémoire d'un jour à l'autre) — volontairement simple pour rester un vrai exemple de skill personnelle, pas un produit.
