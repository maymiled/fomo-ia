# Design

## Context

Voir proposal.md pour la motivation. Constats faits le 28/09/2026 sur l'API publique Bluesky (`https://public.api.bsky.app/xrpc/`), sans clé :
- `app.bsky.feed.searchPosts` (recherche plein texte) : **403** pour les anonymes.
- `app.bsky.feed.getAuthorFeed?actor=…&filter=posts_no_replies&limit=100` : **200**. Chaque élément contient `post` (auteur, `record.text`, `likeCount`, `repostCount`, `indexedAt`, `uri`, `embed`) et, pour un repost, `reason` de type `app.bsky.feed.defs#reasonRepost` (avec son propre `indexedAt`). Une citation apparaît dans `post.embed` en `app.bsky.embed.record#view` (auteur dans `embed.record.author`) ou en `app.bsky.embed.recordWithMedia#view` (auteur dans `embed.record.record.author`).
- Pour un compte prolifique (Simon Willison), 30 éléments couvrent environ 4 semaines. 100 éléments suffisent donc largement pour 7 jours.

## Goals / Non-Goals

**Goals :**
- Le serveur reste générique : la liste de comptes est un paramètre, pas une constante.
- La règle du nouveau visage est calculée par le serveur (compte exact, testable), et Claude n'a plus qu'à juger de la pertinence.

**Non-Goals :**
- La recherche par mot-clé dans tout Bluesky (fermée sans compte).
- Les sujets tendance Bluesky (`getTrends`) : testés, mais dominés par la politique et le sport, et les comptes associés sont surtout des commentateurs. On pourra y revenir.
- L'ajout automatique des nouveaux visages à la liste (décision de l'utilisatrice).
- La mémoire d'un jour à l'autre : un même nouveau visage peut réapparaître plusieurs jours de suite tant qu'il reste au-dessus du seuil. C'est accepté pour cette version.

## Decisions

**1. Un seul outil qui renvoie posts et comptes émergents, plutôt que deux outils.** Les deux calculs lisent les mêmes fils d'actualité. Deux outils feraient deux fois les 13 requêtes.

**2. Retour sous forme d'objet :** `{"posts": [...], "rising": [...], "unavailable": [...]}`. En cas d'échec total : `{"error": "..."}`.
- Écart assumé avec les autres outils, qui renvoient une liste : ici le résultat a deux parties de nature différente. La convention « erreur renvoyée comme donnée, jamais d'exception » est respectée, et la skill détecte déjà une erreur par la présence du champ `error`.

**3. Liste de comptes dans `skills/daily-ai-fomo-briefing/references/bluesky-accounts.md`,** passée en paramètre `handles` par la skill.
- Alternative écartée : une constante Python dans `server.py`. L'utilisatrice devrait modifier du code pour changer ses comptes, et le serveur ne serait plus réutilisable.
- Alternative écartée : un fichier JSON lu par le serveur. Ça fait un chemin de fichier à gérer côté serveur, et c'est moins lisible pour l'utilisatrice qu'une liste markdown avec une ligne « pourquoi ».

**4. Une requête `getAuthorFeed` (`limit=100`, `filter=posts_no_replies`) par compte,** en parallèle (`ThreadPoolExecutor`, comme pour HN). Le même résultat sert :
- **aux posts** : `reason` absent, auteur égal au compte suivi, `indexedAt` dans les `hours` dernières heures ;
- **à l'émergence** : sur 7 jours (date du `reason` pour un repost, du post pour une citation), on retient l'ensemble des auteurs repartagés ou cités par chaque expert. On compte ensuite, pour chaque auteur extérieur à la liste, le nombre d'**experts distincts**. Plusieurs reposts du même expert comptent pour 1.

**5. Seuils en constantes nommées :** `BLUESKY_RISING_MIN_EXPERTS = 3`, `BLUESKY_RISING_DAYS = 7`, `BLUESKY_MAX_HANDLES = 30`. Sortie limitée à 40 posts et 5 comptes émergents, pour borner le texte que Claude doit lire.

**6. `hours=48` par défaut, pas 24.** Sur l'échantillon réel, un expert publie en moyenne moins d'un post par jour, donc avec 24 h la section serait souvent vide. Claude ne garde de toute façon que 5 posts.

**7. Texte des posts tronqué à 300 caractères,** lien construit sous la forme `https://bsky.app/profile/{handle}/post/{rkey}`, où `rkey` est le dernier segment de l'`uri`.

## Risks / Trade-offs

- [Un compte « institutionnel » (média, gros compte) peut dépasser le seuil sans être un nouveau visage] → Claude juge la pertinence : IA, personne ou projet émergent. Il en affiche au plus 2.
- [Le même nouveau visage revient plusieurs jours de suite] → accepté (voir Non-Goals). Il disparaît dès que l'utilisatrice l'ajoute à sa liste.
- [L'API publique Bluesky change ou se ferme davantage] → l'échec est renvoyé comme donnée, et le digest continue avec les 3 autres sources.
- [Des experts qui cessent de poster] → la liste est datée dans le fichier de référence, et l'outil signale les comptes indisponibles.
- [Temps de réponse] → 13 requêtes en parallèle, environ 1 à 2 s. Rien de comparable avec HN (61 requêtes).
