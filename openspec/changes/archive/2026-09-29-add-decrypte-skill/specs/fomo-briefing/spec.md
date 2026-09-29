# Spec Delta

## ADDED Requirements

### Requirement: Enregistrement du digest
Une fois le digest composé et affiché, la skill `daily-ai-fomo-briefing` DOIT (MUST) l'enregistrer tel quel, liens compris, dans `digests/AAAA-MM-JJ.md` à la racine du projet, en créant le dossier si besoin. Un nouveau digest le même jour DOIT remplacer le fichier de ce jour. Si l'écriture échoue, le digest DOIT quand même être affiché, avec une mention de l'échec. Chaque élément des sections HN, Bluesky et Recherche DOIT comporter le lien de sa source. Pour les repos, le nom `owner/repo` suffit à reconstituer le lien GitHub.

#### Scenario: Premier digest du jour
- **WHEN** l'utilisatrice demande son FOMO le 29/09/2026
- **THEN** le fichier `digests/2026-09-29.md` contient le digest affiché, avec tous ses liens

#### Scenario: Un papier de recherche est retrouvable
- **WHEN** le digest enregistré contient un papier dans « Recherche fraîche »
- **THEN** la ligne de ce papier contient son lien arXiv, pour que `/decrypte` puisse le lire depuis une autre conversation

#### Scenario: Deuxième digest le même jour
- **WHEN** l'utilisatrice redemande son FOMO plus tard le même jour
- **THEN** `digests/2026-09-29.md` contient uniquement le digest le plus récent
