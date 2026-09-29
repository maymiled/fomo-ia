# Proposal

## Why

Le digest FOMO se lit en moins d'une minute, mais une ligne par sujet ne suffit pas quand un article intrigue. Aujourd'hui, pour approfondir, il faut ouvrir le lien, lire en anglais et parfois décoder du jargon. L'utilisatrice veut pouvoir dire « décrypte-moi celui-là » et obtenir une explication claire et pédagogique, sans avoir à formuler elle-même une consigne détaillée à chaque fois. Autre besoin : le digest n'existe que dans la conversation où il a été généré, ce qui empêche de s'y référer plus tard. C'est aussi un prérequis pour le futur briefing automatique du matin.

## What Changes

- Nouvelle skill **`decrypte`**, invocable par `/decrypte <sujet>`. Le sujet peut être un fragment de titre (« Ember-1 »), un rang (« le 3ᵉ HN »), un lien direct ou un thème (« Opus 5.5 »).
  - Elle retrouve l'article dans le digest de la conversation, ou à défaut dans le dernier digest enregistré.
  - Elle confie la lecture complète de la page à un **sous-agent dédié, `lecteur-article`**, qui n'a le droit que de lire (pages web et fichiers) et renvoie des notes factuelles.
  - Elle rédige un décryptage en français, au format fixe : En une phrase / Le contexte / Ce qui est nouveau / Pourquoi ça compte / Les limites et l'avis critique / À retenir en 3 points / 📖 Les mots compliqués / Source.
  - Les consignes de rédaction (pédagogie, pas de jargon non expliqué, pas d'invention) forment le « prompt caché » de la skill.
- La skill `daily-ai-fomo-briefing` **enregistre chaque digest** dans `digests/AAAA-MM-JJ.md` à la racine du projet. Un nouveau digest le même jour écrase le précédent.
- `digests/` est ajouté au `.gitignore` : c'est du contenu personnel et généré, pas du code.

Le nom `/resume` a été écarté car c'est déjà une commande intégrée de Claude Code (reprendre une conversation).

## Capabilities

### New Capabilities
- `decryptage` : explication pédagogique et approfondie d'un article ou d'un sujet cité dans un digest FOMO.

### Modified Capabilities
- `fomo-briefing` : ajout de l'exigence « Enregistrement du digest ».

## Impact

- Nouveaux fichiers : `skills/decrypte/SKILL.md` et `agents/lecteur-article.md`, avec les liens symboliques `.claude/skills/decrypte` et `.claude/agents/lecteur-article.md` pour que Claude Code les découvre, comme pour la skill FOMO.
- `skills/daily-ai-fomo-briefing/SKILL.md` : une étape finale d'enregistrement.
- `.gitignore`, `README.md`, `CLAUDE.md`, `spec/` (Gherkin) : à aligner.
- **Aucun changement dans `server.py`** : la lecture des pages passe par l'outil de lecture web intégré à Claude Code (WebFetch). Il n'y a donc pas de nouveau test mocké, et la vérification se fait sur de vrais lancements.
- Coût : un décryptage lance un sous-agent, donc un appel de modèle en plus. Ça n'arrive qu'à la demande, jamais pendant le digest quotidien.
