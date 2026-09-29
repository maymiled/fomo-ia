# Design

## Context

Voir proposal.md pour la motivation. Briques existantes réutilisables :
- le sous-agent `lecteur-article` (lecture seule, notes factuelles) ;
- la recherche de cible de `decrypte` (conversation, puis `digests/`) ;
- le format pédagogique avec lexique.

Claude Code fournit WebSearch (résultats de recherche courts : titres, extraits, liens) et l'outil Agent.

## Goals / Non-Goals

**Goals :**
- Une boucle **visible** : l'utilisatrice doit voir chaque décision et comprendre pourquoi l'agent passe à l'étape suivante.
- Un coût **borné** et prévisible.
- Un verdict **honnête** : il ne doit jamais être plus affirmatif que les sources ne le permettent.

**Non-Goals :**
- Enregistrer les enquêtes dans des fichiers. Ça pourra venir plus tard.
- Une version Python de la boucle avec le SDK Agent. C'est une piste séparée, pour comparer « boucle guidée par des consignes » et « boucle écrite en code ».
- Tester automatiquement la qualité d'un verdict : c'est non mockable, et vérifié sur de vrais lancements.

## Decisions

**1. La boucle est menée par la skill, dans la conversation principale, et pas dans un sous-agent « enquêteur ».**
- Raison : la visibilité est un objectif. Dans un sous-agent, les étapes se dérouleraient dans un bloc replié, et seul le résultat final remonterait.
- Coût en contexte acceptable : la conversation ne reçoit que des résultats de recherche courts et des notes de lecture d'environ 400 mots (5 lectures au plus, soit ~2 000 mots).
- Alternative écartée : un sous-agent `enqueteur` avec WebSearch, WebFetch et Read. Le contexte serait plus propre, mais la boucle deviendrait invisible et le raisonnement plus difficile à suivre. Elle reste envisageable si les enquêtes s'allongent.

**2. Deux types d'action seulement : `CHERCHER` et `LIRE`.**
- `CHERCHER` : la skill fait une recherche WebSearch. Les résultats (titres et extraits) sont courts, donc pas besoin de sous-agent.
- `LIRE` : la page est confiée à `lecteur-article`, réutilisé tel quel. Il reste en lecture seule et renvoie des notes structurées.
- Limiter les types d'action rend la boucle lisible et le budget facile à compter.

**2 bis. Réutilisation des notes déjà en main.** Si `lecteur-article` a déjà lu la page dans la conversation (souvent la source de départ, après un `/decrypte`), ses notes sont réutilisées. Relire coûterait un sous-agent pour un résultat identique. La réutilisation compte comme une étape, pour que la boucle reste bornée, mais pas comme une lecture, puisque le plafond de 5 lectures sert à borner le coût. Ce cas a été ajouté après le premier test réel, où l'étape 1 a naturellement réutilisé les notes d'un décryptage.

**3. Budget : 8 étapes, dont 5 lectures au plus. Trois conditions d'arrêt,** vérifiées après chaque observation :
1. **Éléments suffisants** : au moins une source indépendante lue, et une recherche d'éléments contraires faite.
2. **Plus rien de nouveau** : deux étapes de suite sans information nouvelle.
3. **Budget atteint.**

Pourquoi 8 : une enquête typique demande la source de départ, une recherche indépendante, une ou deux lectures, une recherche d'avis contraires et une lecture, soit 5 à 6 étapes. 8 laisse une marge sans laisser tourner indéfiniment.

**4. Classement des sources en trois catégories**, qui conditionne le verdict :
- **intéressée** : l'auteur de l'affirmation, ses partenaires ou ses clients cités ;
- **indépendante** : un média, un chercheur ou un testeur sans lien avec l'auteur ;
- **communauté** : HN, Bluesky, Reddit. Utile pour repérer des doutes, mais ne suffit pas à confirmer.

Règle : sans source indépendante, le verdict ne peut pas être « Confirmé ».

**5. Annonce de chaque étape en une ligne**, au format :

`Étape n/8 — Il me manque : … → Je {cherche « … » | lis …} → J'observe : …`

Le journal final reprend ces lignes. C'est la trace du raisonnement, et ce qui distingue visiblement la boucle d'une recette fixe.

**6. Reformulation préalable en question vérifiable**, affichée avant de commencer. Ça évite une boucle sur une question floue, qui consommerait le budget sans pouvoir conclure.

## Risks / Trade-offs

- [La boucle tourne en rond (mêmes recherches reformulées)] → condition « deux étapes sans nouveauté », et consigne de ne jamais relancer une recherche déjà faite.
- [Le verdict est influencé par l'ordre de découverte] → recherche d'éléments contraires obligatoire avant l'arrêt « éléments suffisants ».
- [WebSearch renvoie des résultats peu fiables ou datés] → la classification des sources et la rubrique « Ce qu'on ne sait pas » rendent l'incertitude visible.
- [Coût plus élevé qu'un décryptage] → le budget de 8 étapes, uniquement à la demande. Le nombre d'étapes est affiché.
- [Actualité très fraîche, sans source indépendante encore publiée] → verdict « Pas assez d'éléments », présenté comme un résultat normal et non comme un échec.
