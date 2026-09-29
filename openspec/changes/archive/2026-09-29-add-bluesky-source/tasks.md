# Tasks

## 1. Outil serveur `get_bluesky_buzz`

- [x] 1.1 Écrire dans `test_server.py` des tests mockés : posts récents gardés, vieux posts et reposts exclus, tri par likes, lien bsky.app ; compte repartagé ou cité par 3 experts marqué émergent avec ses 3 handles ; compte partagé par 2 experts absent ; expert repartagé par d'autres experts jamais émergent ; un compte en échec signalé dans `unavailable` ; échec total ou liste vide donnant `{"error": ...}`. Vérifier qu'ils échouent avant 1.2.
- [x] 1.2 Implémenter `get_bluesky_buzz(handles, hours=48)` dans `server.py`, selon les décisions 2, 4, 5 et 7 du design, et mettre à jour la docstring du module. Vérifier que `python test_server.py` passe entièrement.
- [x] 1.3 Faire un appel réel avec 3 comptes de la liste, et vérifier que des posts reviennent avec des liens bsky.app valides et que `rising` est une liste (vide ou non).

## 2. Skill

- [x] 2.1 Créer `skills/daily-ai-fomo-briefing/references/bluesky-accounts.md` avec les 13 comptes validés (handle, nom, pourquoi), la date de vérification et une note « comment ajouter un compte ». Vérifier que chaque handle répond à un vrai appel.
- [x] 2.2 Mettre à jour `SKILL.md` : lire le fichier de référence, appeler `get_bluesky_buzz`, section « 🦋 Ça parle sur Bluesky » (au plus 5 posts IA, par likes), ligne « 👀 Nouveau visage » conditionnelle (au plus 2, jamais d'ajout automatique), 4 sources dans la gestion d'erreur et dans le format. Vérifier par relecture que chaque scénario du delta spec « Digest quotidien » y est couvert.

## 3. Documentation alignée

- [x] 3.1 Mettre à jour `spec/fomo_briefing.feature` (section Bluesky, nouveau visage présent ou absent, 4 sources), `README.md` (source Bluesky, commande d'exemple, limite « pas de recherche plein texte »), `CLAUDE.md` (4 outils) et le Purpose de `openspec/specs/fomo-briefing/spec.md` (4 sources). Vérifier avec `grep -n "trois\|3 outils"` qu'il ne reste pas de mention obsolète dans ces fichiers.
- [x] 3.2 Lancer `openspec validate add-bluesky-source --strict` et vérifier qu'il ne remonte aucune erreur.

## 4. Vérification réelle

- [x] 4.1 Reconnecter `fomo-ia` via `/mcp`, lancer « fais-moi le FOMO IA du jour », puis vérifier : la section 🦋 est présente et ne contient que des posts IA, la ligne « Nouveau visage » n'apparaît que si `rising` contient un compte pertinent, et `references/bluesky-accounts.md` n'a pas été modifié.
