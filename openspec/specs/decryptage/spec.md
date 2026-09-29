# decryptage Specification

## Purpose
Permettre d'approfondir en un geste un article ou un sujet cité dans un digest FOMO, avec une explication en français claire, pédagogique et fidèle à la source.

## Requirements

### Requirement: Retrouver la cible du décryptage
La skill `decrypte` DOIT (MUST) accepter comme argument un fragment de titre, un rang dans une section (ex. « le 3ᵉ HN »), un lien direct ou un thème. Elle DOIT d'abord chercher la cible dans le digest présent dans la conversation, puis à défaut dans le digest enregistré le plus récent sous `digests/`. Si plusieurs éléments correspondent, elle DOIT demander lequel en listant les candidats, plutôt que de choisir au hasard. Si rien ne correspond et qu'aucun lien n'est fourni, elle DOIT le dire et proposer les titres du dernier digest.

#### Scenario: Fragment de titre présent dans le digest de la conversation
- **WHEN** l'utilisatrice tape `/decrypte Ember-1` après un FOMO qui contient « Ember-1 »
- **THEN** la skill décrypte l'article lié à cette ligne, sans redemander le lien

#### Scenario: Nouvelle conversation
- **WHEN** l'utilisatrice tape `/decrypte Ember-1` dans une conversation sans digest, et que `digests/` contient un digest mentionnant « Ember-1 »
- **THEN** la skill retrouve le lien dans ce fichier et décrypte l'article

#### Scenario: Cible ambiguë
- **WHEN** l'argument correspond à plusieurs lignes du digest (ex. « Opus » apparaît dans trois items)
- **THEN** la skill liste les candidats et demande lequel décrypter, ou propose de les couvrir comme un thème

#### Scenario: Lien direct
- **WHEN** l'argument est une URL
- **THEN** la skill décrypte cette page, même si elle n'apparaît dans aucun digest

### Requirement: Lecture complète confiée à un sous-agent
La skill DOIT (MUST) confier la lecture de la ou des pages sources à un sous-agent dédié, limité aux outils de lecture : il NE DOIT PAS pouvoir modifier de fichier ni lancer de commande. Ce sous-agent renvoie des notes factuelles (faits, chiffres, affirmations, auteurs, date, nouveautés, limites mentionnées) et non un texte final. Pour un thème, au plus 3 sources du digest sont lues. Si une page est illisible (paywall, erreur), le sous-agent DOIT le signaler, et le décryptage DOIT le dire explicitement au lieu de combler avec des suppositions.

#### Scenario: Page lisible
- **WHEN** la page source se charge normalement
- **THEN** le décryptage s'appuie uniquement sur les notes du sous-agent et sur le digest

#### Scenario: Le sous-agent est en lecture seule
- **WHEN** le sous-agent de lecture est lancé
- **THEN** il ne dispose que d'outils de lecture (page web, fichier), et aucun fichier du projet ne peut être modifié par lui

#### Scenario: Page inaccessible
- **WHEN** la page source est derrière un paywall ou ne répond pas
- **THEN** le décryptage indique en tête que l'article n'a pas pu être lu en entier et précise sur quoi il s'appuie (titre, extrait, discussion)

### Requirement: Format pédagogique du décryptage
Le décryptage DOIT (MUST) être rédigé en français, dans cet ordre : titre « 🔍 Décryptage — {sujet} », « En une phrase », « Le contexte », « Ce qui est nouveau », « Pourquoi ça compte », « Les limites et l'avis critique », « À retenir » (exactement 3 points), « 📖 Les mots compliqués », puis le ou les liens sources. Tout terme technique utilisé DOIT être écrit en italique dans le texte et défini en une phrase simple dans « Les mots compliqués ». Si aucun terme ne le justifie, cette section l'indique en une ligne. Le décryptage NE DOIT PAS affirmer de fait absent des sources.

#### Scenario: Article technique
- **WHEN** l'article emploie des termes comme « inférence » ou « open-weight »
- **THEN** ces termes apparaissent en italique dans le décryptage et chacun est défini dans « Les mots compliqués »

#### Scenario: Structure complète
- **WHEN** un décryptage est produit
- **THEN** il contient les huit parties dans l'ordre, avec exactement 3 points dans « À retenir » et au moins un lien source
