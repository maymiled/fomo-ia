Feature: Enquêter sur une affirmation IA
  En tant qu'utilisatrice qui lit beaucoup d'annonces enthousiastes,
  je veux vérifier si une affirmation tient la route en croisant plusieurs sources,
  afin de distinguer ce qui est annoncé de ce qui est démontré.

  # Même comportement que openspec/specs/enquete/spec.md, en Given/When/Then.

  Background:
    Given la skill "enquete" et l'agent "lecteur-article" sont disponibles dans Claude Code

  Scenario: Enquête sur une annonce du digest
    Given le digest du jour cite l'annonce de "Sonnet 5.5"
    When je tape "/enquete Sonnet 5.5 est-il vraiment meilleur en code ?"
    Then la question reformulée m'est affichée avant la première étape
    And chaque étape est annoncée sur une ligne au moment où elle se déroule
    And chaque lecture de page est faite par l'agent "lecteur-article"
    And je reçois un verdict avec les sources classées "intéressée", "indépendante" ou "communauté"

  Scenario: L'étape suivante dépend de la précédente
    Given la source de départ ne donne que les chiffres de l'entreprise concernée
    When l'enquête continue
    Then l'étape suivante cherche une source indépendante sur ces chiffres

  Scenario: Réutiliser une lecture déjà faite
    Given l'agent "lecteur-article" a déjà lu l'annonce de Sonnet 5.5 pendant un "/decrypte" dans la conversation
    When l'enquête a besoin de cette page
    Then elle réutilise ses notes sans relancer de lecture
    And cette étape n'est pas comptée dans les 5 lectures

  Scenario: Pas de confirmation sans source indépendante
    Given toutes les sources trouvées viennent de l'entreprise qui fait l'annonce
    When l'enquête se termine
    Then le verdict est "Pas assez d'éléments"
    And le résultat explique qu'aucune source indépendante n'a été trouvée

  Scenario Outline: L'enquête s'arrête toute seule
    Given <situation>
    When l'enquête vérifie ses conditions d'arrêt
    Then elle s'arrête avec la mention "<raison>"

    Examples:
      | situation                                                                 | raison                  |
      | une source indépendante a été lue et les avis contraires ont été cherchés | éléments suffisants     |
      | deux étapes de suite n'ont rien appris de nouveau                         | plus rien de nouveau    |
      | 8 étapes ont été faites                                                   | budget atteint          |

  Scenario: Question trop vague
    When je tape "/enquete IA"
    Then on me demande quelle affirmation vérifier
    And aucune recherche n'est lancée
