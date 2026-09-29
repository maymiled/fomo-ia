# Tasks

## 1. Enregistrement du digest

- [x] 1.1 Ajouter à `skills/daily-ai-fomo-briefing/SKILL.md` une étape finale « enregistrer le digest dans `digests/AAAA-MM-JJ.md` (écraser si le fichier existe, mentionner un éventuel échec) », et ajouter `digests/` au `.gitignore`. Vérifier par relecture que les deux scénarios « Enregistrement du digest » sont couverts.
- [x] 1.2 Ajouter le lien arXiv à la fin de chaque ligne « Recherche fraîche » dans le format de `SKILL.md` : sans lui, `/decrypte` ne peut pas retrouver un papier depuis `digests/` (trou repéré au test réel du 29/09). Vérifier par relecture du format.

## 2. Skill `decrypte`

- [x] 2.1 Créer `agents/lecteur-article.md` (décision 3 : `tools: WebFetch, Read`, `model: sonnet`, consignes de lecture et format des notes, signalement d'une page illisible) et le lien `.claude/agents/lecteur-article.md` qui pointe vers `../../agents/lecteur-article.md`. Vérifier avec `ls -la .claude/agents/`.
- [x] 2.2 Créer `skills/decrypte/SKILL.md` : frontmatter (`name: decrypte`, description qui déclenche sur « décrypte », « explique-moi cet article du FOMO »), recherche de la cible (décision 4), appel de l'agent `lecteur-article` (décision 3), format et règles de rédaction (exigence « Format pédagogique »). Vérifier par relecture que chaque scénario du delta `decryptage` y est couvert.
- [x] 2.3 Créer le lien `.claude/skills/decrypte` qui pointe vers `../../skills/decrypte`, et vérifier avec `ls -la .claude/skills/` qu'il pointe au bon endroit.

## 3. Documentation alignée

- [x] 3.1 Mettre à jour `README.md` (usage de `/decrypte`, dossier `digests/`, limite « nécessite WebFetch, donc Claude Code »), `CLAUDE.md` (structure : 2 skills, l'agent `lecteur-article`, `digests/`) et ajouter à `spec/` un fichier `decrypte.feature` en Gherkin, plus un scénario « digest enregistré » dans `fomo_briefing.feature`. Vérifier par relecture la cohérence avec les deltas.
- [x] 3.2 Lancer `openspec validate add-decrypte-skill --strict` et vérifier qu'il ne remonte aucune erreur.

## 4. Vérification réelle

- [x] 4.1 Après relance de Claude Code (nouvelle skill à découvrir), lancer un FOMO et vérifier que `digests/AAAA-MM-JJ.md` existe avec les liens. Puis lancer `/decrypte Ember-1` et vérifier : les huit parties sont dans l'ordre, les mots en italique sont définis dans le lexique, le lien source est présent et l'agent `lecteur-article` apparaît bien dans le terminal (aucun WebFetch lancé directement par le Claude principal).
- [x] 4.2 Lancer `/decrypte Opus` (ambigu) et vérifier que la skill liste les candidats au lieu d'en choisir un.
