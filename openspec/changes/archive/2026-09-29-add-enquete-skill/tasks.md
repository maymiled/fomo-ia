# Tasks

## 1. Skill `enquete`

- [x] 1.1 Créer `skills/enquete/SKILL.md` : frontmatter (`name: enquete`, description qui déclenche sur « enquête », « vérifie », « est-ce que c'est vrai que… »), reformulation en question vérifiable (décision 6), boucle `CHERCHER` / `LIRE` avec annonce de chaque étape (décisions 2 et 5), budget et conditions d'arrêt (décision 3), classement des sources et règle du verdict (décision 4), format du résultat. Vérifier par relecture que chaque scénario du delta `enquete` est couvert.
- [x] 1.2 Créer le lien `.claude/skills/enquete` qui pointe vers `../../skills/enquete`, et vérifier avec `ls -la .claude/skills/`.
- [x] 1.3 Ajouter la règle de réutilisation des notes déjà en main (décision 2 bis) dans `SKILL.md`, dans le delta spec et dans le Gherkin (écart repéré au test réel 3.1). Vérifier par relecture.

## 2. Documentation alignée

- [x] 2.1 Mettre à jour `README.md` : nouvelle brique « Boucle agentique » avec ce que c'est, comment c'est fait ici et les leçons ; ajout au schéma et à la structure ; retrait de la piste devenue réalité ; ajout de la piste « version SDK Python ». Mettre à jour `CLAUDE.md` (3 skills) et ajouter `spec/enquete.feature`. Vérifier la cohérence par relecture, et que le README garde sa présentation de projet perso.
- [x] 2.2 Lancer `openspec validate add-enquete-skill --strict` et vérifier qu'il ne remonte aucune erreur.

## 3. Vérification réelle

- [x] 3.1 Lancer `/enquete Sonnet 5.5 est-il vraiment meilleur en code ?`, puis vérifier : question reformulée affichée, chaque étape annoncée au format de la décision 5, lectures faites par `lecteur-article`, au plus 8 étapes et 5 lectures, sources classées, raison de l'arrêt indiquée, verdict cohérent avec la règle « pas de Confirmé sans source indépendante ».
- [x] 3.2 Lancer `/enquete IA` et vérifier qu'une précision est demandée, sans aucune recherche lancée.
