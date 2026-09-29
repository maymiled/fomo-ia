---
name: decrypte
description: Use this skill when the user types /decrypte or asks to explain, "décrypter", summarize or deep-dive an article, repo, paper, Bluesky post or topic from their FOMO IA digest (e.g. "décrypte Ember-1", "explique-moi le 3e article HN", "c'est quoi ce truc d'Opus 5.5 ?").
---

# Décryptage d'un article du FOMO

L'utilisatrice veut comprendre en profondeur un élément de son digest FOMO IA, expliqué clairement, comme par un bon prof qui connaît le sujet. L'argument (ce qui suit `/decrypte`) peut être un fragment de titre, un rang (« le 3ᵉ HN », « le 2ᵉ repo »), une URL ou un thème.

## 1. Trouver la cible

Cherche dans cet ordre, et arrête-toi dès que tu trouves :

1. **L'argument est une URL** : c'est la source, même si elle n'est dans aucun digest.
2. **Le digest affiché dans cette conversation**, s'il y en a un.
3. **Le fichier le plus récent de `digests/`** à la racine du projet (noms `AAAA-MM-JJ.md` : le plus grand est le plus récent).

Ensuite :
- **Plusieurs lignes correspondent** (ex. « Opus » dans trois items) : ne choisis pas au hasard. Liste les candidats, numérotés avec leur section, et demande lequel décrypter, ou propose de les couvrir ensemble comme un thème.
- **Rien ne correspond** et pas d'URL : dis-le, et propose les titres du dernier digest.
- **Quelle URL lire selon la section** : HN → l'URL de l'article (la page HN seulement s'il n'y en a pas, cas des « Ask HN ») ; Bluesky → l'URL du post ; repo → la page GitHub ; arXiv → la page `abs`.
- **Un thème** : prends au plus 3 lignes du digest sur ce thème.

## 2. Faire lire la source par l'agent `lecteur-article`

Ne lis **pas** la page toi-même avec WebFetch. Lance l'agent `lecteur-article` (outil Agent, `subagent_type: "lecteur-article"`) en lui donnant :
- la ou les URL (3 au maximum) ;
- la ligne du digest qui les cite, pour le contexte.

Il te renverra des notes factuelles par source, avec le niveau de lisibilité. Ton décryptage s'appuie **uniquement** sur ces notes et sur le digest.

## 3. Rédiger le décryptage

En français, clair et pédagogique : imagine que tu expliques à quelqu'un de curieux et d'intelligent, qui suit l'IA mais n'est pas chercheur. Des phrases courtes, un exemple concret quand ça aide. Entre 300 et 500 mots, lexique compris.

Format exact :

```markdown
# 🔍 Décryptage — {sujet}

{Seulement si une source n'a pas pu être lue en entier : > ⚠️ Article lu partiellement / non lu ({raison}). Ce décryptage s'appuie sur {ce qui a été lu : titre, extrait, post…}.}

**En une phrase** : {l'idée centrale, compréhensible sans rien connaître}

**Le contexte** : {2-3 phrases : ce qu'il faut savoir avant pour comprendre}

**Ce qui est nouveau** : {3-5 phrases : l'explication pas à pas, avec les chiffres clés des notes}

**Pourquoi ça compte** : {2-3 phrases : les conséquences concrètes pour quelqu'un qui suit l'IA et le vibe coding}

**Les limites et l'avis critique** : {2-3 phrases : ce qui n'est qu'annoncé et pas démontré, ce que la source ne dit pas, les critiques relevées}

**À retenir** :
1. {…}
2. {…}
3. {…}

📖 **Les mots compliqués**
- *{terme}* : {définition en une phrase simple, avec une image si possible}
- …

🔗 Source : {url} (une ligne par source)
```

## Règles du décryptage

- **Chaque terme technique** que tu utilises (anglicismes et jargon compris : *inférence*, *open-weight*, *benchmark*, *agent*…) est écrit en *italique* dans le texte **et** défini dans « Les mots compliqués ». Pas de mot en italique sans définition, pas de définition d'un mot absent du texte. Si aucun mot ne le mérite : « Rien de compliqué ici. »
- **N'invente rien** : aucun fait, chiffre ou citation qui ne figure pas dans les notes du lecteur. En cas de doute, dis « l'article ne le précise pas ».
- Distingue toujours ce qui est **annoncé** de ce qui est **démontré**.
- « À retenir » contient exactement **3** points, d'une ligne chacun.
- Pas de flatterie ni d'emballement : ton neutre, comme un bon article de vulgarisation.
