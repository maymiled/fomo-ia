---
name: enquete
description: Use this skill when the user types /enquete or asks to verify, fact-check or investigate an AI-related claim or question, often from their FOMO IA digest (e.g. "enquête : Sonnet 5.5 est-il vraiment meilleur en code ?", "est-ce que c'est vrai que…", "vérifie cette annonce").
---

# Enquête : vérifier une affirmation sur l'IA

L'utilisatrice veut savoir si une affirmation tient la route, en croisant plusieurs sources. Contrairement à `/decrypte`, qui explique **une** source, tu mènes une **boucle** : à chaque étape, tu choisis la suite **en fonction de ce que tu viens de découvrir**, jusqu'à pouvoir trancher ou jusqu'à épuiser ton budget.

## 0. Préparer

1. **Trouver le point de départ.** Si l'argument renvoie à un élément du digest, retrouve son lien comme le fait `decrypte` : le digest de cette conversation, sinon le fichier le plus récent de `digests/`. Sinon, tu pars d'une recherche.
2. **Reformuler en question vérifiable**, en une phrase, et l'afficher :
   > 🎯 **Question** : Les performances en code annoncées pour Sonnet 5.5 sont-elles confirmées par des sources indépendantes d'Anthropic ?
3. **Trop vague ?** Si l'argument ne permet pas de formuler une question vérifiable (ex. « IA », « Opus »), **ne lance aucune recherche** : demande quelle affirmation vérifier, en proposant 2 ou 3 formulations possibles.

## 1. La boucle

À chaque étape :
- **Réfléchis** : quelle information te manque pour trancher ?
- **Agis** avec **une seule** des deux actions :
  - `CHERCHER` : une recherche avec l'outil WebSearch. Formule-la pour combler le manque, et ne relance jamais une recherche déjà faite, même reformulée.
  - `LIRE` : fais lire **une** page par l'agent `lecteur-article` (outil Agent, `subagent_type: "lecteur-article"`), en lui donnant l'URL et la question. Ne lis **jamais** une page toi-même avec WebFetch.
    - **Économie** : si cette page a **déjà** été lue par `lecteur-article` dans cette conversation (par exemple lors d'un `/decrypte`), réutilise ses notes au lieu de relancer une lecture. L'étape compte dans les 8 étapes, mais **pas** dans les 5 lectures, puisque rien n'a été relu. Indique-le dans l'annonce : « Je lis {page} (notes déjà en main) ».
- **Observe** : qu'est-ce que ça confirme, contredit ou laisse ouvert ? Qui parle : l'auteur de l'affirmation, une source indépendante, ou la communauté ?

**Annonce chaque étape au moment où tu la fais**, sur une ligne, avant de passer à la suivante :

`**Étape {n}/8** — Il me manque : {besoin} → Je {cherche « requête » | lis {titre ou domaine}} → J'observe : {apport en une phrase}`

Stratégie habituelle, à adapter selon ce que tu trouves :
1. la source de départ ;
2. une source indépendante sur le point clé ;
3. les avis contraires ou les critiques ;
4. creuser ce qui reste flou.

Si une étape révèle quelque chose d'inattendu (chiffre contesté, source qui se contredit…), suis cette piste.

## 2. Quand s'arrêter

Vérifie après chaque observation. Arrête-toi **dès que** l'un de ces cas est vrai :

| Arrêt | Condition |
|---|---|
| ✅ Éléments suffisants | Au moins **une source indépendante** a été lue **et** une recherche d'éléments contraires a été faite |
| 🔁 Plus rien de nouveau | **Deux étapes de suite** n'ont rien appris de nouveau |
| ⏱️ Budget atteint | **8 étapes** faites. Et jamais plus de **5 `LIRE`** au total : une fois les 5 lectures faites, seules des recherches restent possibles |

## 3. Classer les sources

- 🏢 **intéressée** : l'auteur de l'affirmation, ses partenaires, ses clients cités dans sa propre communication ;
- 🔍 **indépendante** : média, chercheur, testeur ou benchmark sans lien avec l'auteur ;
- 💬 **communauté** : HN, Bluesky, Reddit, forums. Utile pour repérer des doutes, mais **ne suffit pas à confirmer**.

## 4. Le verdict

- ✅ **Confirmé** : plusieurs sources indépendantes vont dans le même sens, sans contradiction sérieuse.
- 👍 **Plutôt confirmé** : au moins une source indépendante va dans le sens de l'affirmation, avec des nuances.
- ⚠️ **Contesté** : des sources indépendantes ou des éléments solides contredisent l'affirmation.
- ❓ **Pas assez d'éléments** : pas de source indépendante, ou des sources trop faibles pour trancher. C'est un résultat normal pour une actualité très fraîche, pas un échec.

**Règle absolue** : sans source 🔍 indépendante lue, le verdict ne peut **jamais** être « Confirmé » ni « Plutôt confirmé ».

## 5. Le résultat

En français, clair et pédagogique, comme pour `/decrypte`. Format exact :

```markdown
# 🕵️ Enquête — {question}

**Verdict : {emoji} {verdict}** — {une phrase qui justifie}

**Ce qui soutient** : {2-4 phrases, avec qui le dit}

**Ce qui contredit** : {2-4 phrases, ou « Rien trouvé de contraire, malgré la recherche. »}

**Ce qu'on ne sait pas** : {1-3 phrases}

**Sources**
- 🏢/🔍/💬 {titre} — {url}
- …

**Journal de l'enquête**
1. {besoin} → {action} → {observation}
2. …

**Arrêt** : {✅ éléments suffisants | 🔁 plus rien de nouveau | ⏱️ budget atteint} après {n} étapes ({k} lectures, dont {r} notes réutilisées).

📖 **Les mots compliqués**
- *{terme}* : {définition en une phrase simple}
```

## Règles

- **N'invente rien** : chaque fait du résultat vient d'une note du lecteur ou d'un extrait de recherche cité dans les sources.
- Distingue ce qui est **annoncé** de ce qui est **démontré**, et dis **qui** l'affirme.
- Chaque terme technique est en *italique* et défini dans le lexique. Si aucun ne le mérite : « Rien de compliqué ici. »
- Ton neutre : tu n'as pas d'opinion à défendre, tu rapportes ce que les sources permettent de dire.
