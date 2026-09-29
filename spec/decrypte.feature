Feature: Décrypter un élément du FOMO
  En tant qu'utilisatrice qui veut comprendre un sujet qui l'intrigue dans son digest,
  je veux une explication claire et pédagogique de l'article, sans devoir le lire en anglais,
  afin de saisir l'essentiel et le vocabulaire en quelques minutes.

  # Même comportement que openspec/specs/decryptage/spec.md, en Given/When/Then.

  Background:
    Given la skill "decrypte" et l'agent "lecteur-article" sont disponibles dans Claude Code

  Scenario: Décrypter un article cité dans le digest de la conversation
    Given un FOMO du jour contenant "Ember-1" a été affiché dans la conversation
    When je tape "/decrypte Ember-1"
    Then l'agent "lecteur-article" lit l'article lié à cette ligne
    And je reçois un décryptage avec "En une phrase", "Le contexte", "Ce qui est nouveau", "Pourquoi ça compte", "Les limites et l'avis critique", "À retenir" et "Les mots compliqués"
    And le lien source est indiqué à la fin

  Scenario: Décrypter depuis une nouvelle conversation
    Given aucune conversation n'affiche de digest
    And le dossier "digests" contient un digest mentionnant "Ember-1"
    When je tape "/decrypte Ember-1"
    Then la skill retrouve le lien dans ce fichier et décrypte l'article

  Scenario: Plusieurs articles correspondent
    Given le digest contient trois lignes qui parlent d'"Opus"
    When je tape "/decrypte Opus"
    Then la skill me liste les trois candidats et me demande lequel décrypter

  Scenario: Les mots techniques sont expliqués
    Given l'article emploie les termes "inférence" et "open-weight"
    When je le décrypte
    Then ces termes sont en italique dans le texte
    And chacun est défini simplement dans "Les mots compliqués"

  Scenario: L'article est payant ou illisible
    Given la page de l'article est derrière un paywall
    When je le décrypte
    Then le décryptage indique en tête que l'article n'a pas pu être lu en entier
    And il ne présente aucune information inventée comme un fait

  Scenario: Le lecteur ne peut rien modifier
    When l'agent "lecteur-article" est lancé
    Then il ne dispose que d'outils de lecture de page web et de fichier
