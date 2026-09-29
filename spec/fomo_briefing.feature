Feature: Daily AI FOMO briefing
  En tant qu'utilisatrice qui ne veut rien louper de l'actu IA/vibe coding,
  je veux un digest quotidien condensé plutôt que de checker quatre sources à la main,
  afin de rester à jour en moins d'une minute.

  # Note : format Gherkin classique (Given/When/Then), distinct du format
  # WHEN/THEN natif d'OpenSpec (voir openspec/changes/.../specs/fomo-briefing/spec.md).
  # Les deux décrivent le même comportement, à deux niveaux différents :
  # OpenSpec pour la spec versionnée du projet, Gherkin ici pour des scénarios
  # lisibles par un non-dev.

  Background:
    Given le serveur MCP "fomo-ia" est démarré et connecté à Claude Code

  Scenario: Digest normal, toutes les sources répondent
    Given Hacker News a au moins une story qui parle d'IA
    And l'API GitHub répond avec des repos sur le topic demandé
    And l'API arXiv répond avec des papiers récents
    And des experts de ma liste Bluesky ont posté sur l'IA ces dernières 48 heures
    When j'invoque la skill "daily-ai-fomo-briefing"
    Then je reçois un digest markdown avec une section "Ça buzz sur HN"
    And une section "Ça parle sur Bluesky"
    And une section "Repos qui montent"
    And une section "Recherche fraîche"
    And une ligne "TL;DR" en conclusion

  Scenario: Le digest est enregistré pour plus tard
    When j'invoque la skill "daily-ai-fomo-briefing" le 29 septembre 2026
    Then le fichier "digests/2026-09-29.md" contient le digest affiché, avec ses liens
    And si je relance le FOMO le même jour, le fichier ne contient que le plus récent

  Scenario: Une source est indisponible
    Given l'API GitHub renvoie une erreur de rate limit
    When j'invoque la skill "daily-ai-fomo-briefing"
    Then le digest est quand même généré avec les sources Hacker News, Bluesky et arXiv
    And une mention indique que la source GitHub n'a pas répondu

  Scenario: Claude reconnaît une story IA sans mot-clé évident
    Given les top stories Hacker News contiennent "Why LLMs fail at math"
    And elles contiennent "Nvidia unveils its next datacenter GPU"
    When j'invoque la skill "daily-ai-fomo-briefing"
    Then ces deux stories figurent dans la section "Ça buzz sur HN"

  Scenario: Claude écarte un homonyme hors sujet
    Given les top stories Hacker News contiennent "FBI agent arrested for leaking documents"
    When j'invoque la skill "daily-ai-fomo-briefing"
    Then cette story ne figure pas dans la section "Ça buzz sur HN"

  Scenario: Aucune actualité IA sur Hacker News aujourd'hui
    Given aucune des top stories Hacker News ne parle d'IA
    When j'invoque la skill "daily-ai-fomo-briefing"
    Then la section "Ça buzz sur HN" indique en une ligne qu'aucun sujet IA ne buzze aujourd'hui
    And le digest reste généré avec les deux autres sources

  Scenario: Un nouveau visage perce sur Bluesky
    Given trois experts de ma liste Bluesky ont repartagé cette semaine un compte que je ne suis pas
    And ce compte publie sur l'IA
    When j'invoque la skill "daily-ai-fomo-briefing"
    Then le digest affiche une ligne "Nouveau visage" avec ce compte et les experts qui l'ont partagé
    And ma liste de comptes suivis n'est pas modifiée

  Scenario: Personne ne perce cette semaine
    Given aucun compte hors de ma liste n'a été repartagé par au moins trois experts sur 7 jours
    When j'invoque la skill "daily-ai-fomo-briefing"
    Then le digest ne contient aucune ligne "Nouveau visage"

  Scenario Outline: Filtrage par topic GitHub personnalisé
    Given je précise le topic "<topic>" pour la recherche de repos
    When j'invoque get_trending_ai_repos avec ce topic
    Then les repos renvoyés ont tous le topic "<topic>" dans leurs métadonnées GitHub

    Examples:
      | topic          |
      | llm            |
      | agentic-ai     |
      | vibe-coding    |
