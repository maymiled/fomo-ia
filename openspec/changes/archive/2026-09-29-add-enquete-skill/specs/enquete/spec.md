# Spec Delta

## Purpose

Vérifier une affirmation ou répondre à une question sur l'actualité IA en croisant plusieurs sources, par une boucle de recherche dont chaque étape dépend de la précédente, avec un budget borné et un raisonnement visible.

## ADDED Requirements

### Requirement: Question vérifiable
La skill `enquete` DOIT (MUST) partir d'une affirmation ou d'une question fournie en argument, éventuellement liée à un élément du digest (même recherche de cible que `decrypte` : conversation, puis dernier fichier de `digests/`). Avant la première étape, elle DOIT reformuler l'argument en une question vérifiable, en une phrase affichée à l'utilisatrice. Si l'argument est trop vague pour être vérifié (ex. « l'IA »), elle DOIT demander une précision au lieu de lancer la boucle.

#### Scenario: Affirmation liée au digest
- **WHEN** l'utilisatrice tape `/enquete Sonnet 5.5 est-il vraiment meilleur en code ?` après un digest qui cite l'annonce de Sonnet 5.5
- **THEN** la skill affiche la question reformulée et utilise le lien du digest comme point de départ

#### Scenario: Argument trop vague
- **WHEN** l'utilisatrice tape `/enquete IA`
- **THEN** la skill demande quelle affirmation vérifier, et ne lance aucune recherche

### Requirement: Boucle réfléchir-agir-observer
La skill DOIT (MUST) mener une boucle dont chaque étape se compose d'un **besoin** (l'information qui manque), d'une **action** (une recherche web ou une lecture) et d'une **observation** (ce que l'action a apporté). L'action d'une étape DOIT être choisie en fonction des observations précédentes, et non tirée d'une liste fixe. Chaque lecture de page DOIT être confiée au sous-agent `lecteur-article`, sauf si des notes de ce sous-agent sur la même page existent déjà dans la conversation : elles DOIVENT alors être réutilisées plutôt que de relancer une lecture. Chaque étape DOIT être annoncée dans la conversation au moment où elle se déroule, en une ligne.

#### Scenario: L'étape suivante dépend de ce qui a été trouvé
- **WHEN** la lecture de la source de départ révèle que ses chiffres viennent uniquement de l'entreprise concernée
- **THEN** l'étape suivante cherche une source indépendante sur ces chiffres

#### Scenario: Notes déjà en main
- **WHEN** la page de départ a déjà été lue par `lecteur-article` plus tôt dans la conversation (ex. lors d'un `/decrypte`)
- **THEN** l'enquête réutilise ces notes sans relancer de lecture, l'annonce le précise, et le compteur de lectures n'augmente pas

#### Scenario: Lecture déléguée
- **WHEN** une étape consiste à lire une page
- **THEN** cette lecture est faite par l'agent `lecteur-article`, et non directement par la skill

### Requirement: Budget et conditions d'arrêt
La boucle NE DOIT PAS (MUST NOT) dépasser 8 étapes, dont 5 lectures au plus. Une réutilisation de notes compte comme une étape, mais pas comme une lecture. Elle DOIT s'arrêter avant si les deux conditions suivantes sont remplies : au moins une source indépendante de l'auteur de l'affirmation a été lue, et des éléments contraires ont été recherchés. Elle DOIT aussi s'arrêter après deux étapes consécutives sans information nouvelle. La raison de l'arrêt DOIT être indiquée dans le résultat.

#### Scenario: Éléments suffisants
- **WHEN** après 4 étapes, une source indépendante a été lue et une recherche d'avis contraires a été faite
- **THEN** la boucle s'arrête et le résultat indique « arrêt : éléments suffisants »

#### Scenario: Budget épuisé
- **WHEN** 8 étapes ont été faites sans remplir les conditions d'arrêt
- **THEN** la boucle s'arrête, et le verdict est au mieux « Pas assez d'éléments », avec la mention « arrêt : budget atteint »

#### Scenario: Plus rien de nouveau
- **WHEN** deux étapes consécutives n'apportent aucune information nouvelle
- **THEN** la boucle s'arrête avec la mention « arrêt : plus rien de nouveau »

### Requirement: Verdict sourcé et pédagogique
Le résultat DOIT (MUST) être rédigé en français et comporter, dans cet ordre :
- un titre « 🕵️ Enquête — {question} » ;
- un verdict parmi Confirmé, Plutôt confirmé, Contesté ou Pas assez d'éléments, avec une phrase de justification ;
- « Ce qui soutient », « Ce qui contredit », « Ce qu'on ne sait pas » ;
- les sources, chacune classée « intéressée » (l'auteur de l'affirmation ou ses partenaires), « indépendante » ou « communauté » (forums, réseaux) ;
- le journal des étapes, une ligne par étape ;
- la raison de l'arrêt ;
- « 📖 Les mots compliqués », selon les mêmes règles que `decrypte`.

Le verdict NE DOIT PAS être « Confirmé » si aucune source indépendante n'a été lue. Aucun fait absent des sources lues ne DOIT être affirmé.

#### Scenario: Seules des sources intéressées
- **WHEN** toutes les sources lues proviennent de l'entreprise qui fait l'affirmation
- **THEN** le verdict est au mieux « Pas assez d'éléments », et le résultat explique qu'aucune source indépendante n'a été trouvée

#### Scenario: Structure complète
- **WHEN** une enquête se termine
- **THEN** le résultat contient le verdict, les trois rubriques, les sources classées, le journal, la raison de l'arrêt et le lexique
