# Proposal

## Why

`/decrypte` explique fidèlement ce que dit **une** source, et signale ce qui est « annoncé mais pas démontré ». Il ne va pas plus loin : quand Anthropic annonce 70 % sur un benchmark, ou quand un post affirme qu'un outil « change tout », rien ne vérifie si c'est confirmé ailleurs. L'utilisatrice veut pouvoir vérifier une affirmation du digest en croisant plusieurs sources. C'est aussi l'occasion d'ajouter au projet une vraie **boucle agentique** : la suite des étapes n'est pas écrite à l'avance, elle dépend de ce que l'agent découvre à chaque étape. Toutes les skills actuelles, elles, suivent une recette fixe.

## What Changes

- Nouvelle skill **`enquete`**, invocable par `/enquete <affirmation ou question>` (ex. `/enquete Sonnet 5.5 est-il vraiment meilleur en code ?`). Elle peut partir d'un élément du digest ou d'une question libre.
- La skill mène une **boucle réfléchir → agir → observer** :
  - **réfléchir** : quelle information manque pour trancher ;
  - **agir** : chercher sur le web, ou faire lire une page par le sous-agent `lecteur-article` ;
  - **observer** : ce que cette étape confirme, contredit ou laisse ouvert ;
  - puis choisir l'étape suivante.
- **Garde-fous** :
  - budget maximal de **8 étapes**, dont **5 lectures** au plus ;
  - arrêt anticipé quand les éléments suffisent (au moins une source indépendante de celui qui affirme, et les arguments des deux côtés cherchés) ;
  - arrêt aussi quand deux étapes de suite n'apportent rien de nouveau.
- **Chaque étape est annoncée en direct** dans la conversation, en une ligne, pour que l'utilisatrice voie la boucle travailler.
- **Résultat** :
  - un verdict (Confirmé / Plutôt confirmé / Contesté / Pas assez d'éléments) ;
  - ce qui soutient, ce qui contredit, ce qu'on ne sait pas ;
  - les sources classées selon leur indépendance ;
  - le journal des étapes ;
  - le lexique des mots compliqués, comme `/decrypte`.

## Capabilities

### New Capabilities
- `enquete` : vérification d'une affirmation liée à l'IA par une boucle agentique de recherche et de lecture croisée, bornée par un budget.

### Modified Capabilities
_Aucune._ Le sous-agent `lecteur-article` est réutilisé tel quel.

## Impact

- Nouveaux fichiers : `skills/enquete/SKILL.md` et le lien `.claude/skills/enquete`.
- Aucun changement de `server.py`, du sous-agent `lecteur-article` ni des autres skills. La recherche passe par l'outil WebSearch intégré à Claude Code.
- `README.md` (nouvelle brique « boucle agentique », mise à jour de la piste), `CLAUDE.md` et `spec/` (Gherkin) : à aligner.
- Coût : une enquête consomme plus qu'un décryptage (jusqu'à 5 lectures par sous-agent, plus des recherches), mais uniquement à la demande. Le budget de 8 étapes en borne le coût maximal.
