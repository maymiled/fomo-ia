# FOMO IA

Ma veille IA quotidienne, dans Claude Code. Hacker News, Bluesky, GitHub et arXiv sont résumés en un digest lisible en moins d'une minute, et chaque sujet peut être approfondi en un geste avec `/decrypte`. Construit pour ne plus jamais être larguée sur ce qui bouge dans le milieu (le nom est assumé).

## Pourquoi ce projet

**Un vrai besoin perso.** Suivre l'IA au jour le jour, c'est checker plusieurs sources à la main, chacune avec son bruit, et c'est la première chose qu'on laisse tomber quand on est chargé. FOMO IA me donne chaque jour l'essentiel, trié et résumé en français.

**Un terrain d'apprentissage de l'écosystème Claude.** Plutôt que de lire la doc de chaque brique séparément, je voulais les manipuler toutes, ensemble, sur un projet qui me sert vraiment : serveur **MCP**, **Skills**, **sous-agents**, fichier **CLAUDE.md**, **spec-driven development** avec OpenSpec, specs **Gherkin**, **tests mockés**, **revue de code par IA** et **vibe coding**. Chaque brique a un rôle réel dans le projet, et chaque choix de conception est documenté (voir [`openspec/`](openspec/)).

## Ce que ça fait

**« fais-moi le FOMO IA du jour »** produit un digest de ce type :

```markdown
# FOMO IA — 29 septembre 2026

## 🔥 Ça buzz sur HN
- **Sonnet 5.5** (753 pts) — https://www.anthropic.com/claude-sonnet-5-5
...
## 🦋 Ça parle sur Bluesky
- **Simon Willison** — Publie ses notes sur tout ce qui s'est passé côté LLM en 2026 (87 ❤️) — https://bsky.app/…
👀 Nouveau visage : … (seulement quand quelqu'un perce vraiment)
## 📦 Repos qui montent
## 📄 Recherche fraîche

**TL;DR** — Aujourd'hui : Sonnet 5.5 sort et domine HN, pendant que Bluesky débat…
```

**`/decrypte Sonnet 5.5`** (ou `/decrypte le 3e HN`, `/decrypte <url>`, `/decrypte Labos d'IA` pour un thème) produit une explication pédagogique en 8 parties : en une phrase, contexte, ce qui est nouveau, pourquoi ça compte, limites et avis critique, 3 points à retenir, un lexique des mots compliqués, et les sources.

## Comment les briques s'articulent

```
  Moi : « fais-moi le FOMO IA du jour »            Moi : « /decrypte Sonnet 5.5 »
            │                                                │
            ▼                                                ▼
  ┌──────────────────────────────┐              ┌──────────────────────────────┐
  │ Skill daily-ai-fomo-briefing │              │ Skill decrypte               │
  │ la recette : quoi appeler,   │              │ trouve l'article, délègue    │
  │ comment trier, quel format   │              │ la lecture, rédige           │
  └──────────────┬───────────────┘              └──────────────┬───────────────┘
                 │ appelle des outils MCP                      │ lance un sous-agent
                 ▼                                             ▼
  ┌──────────────────────────────┐              ┌──────────────────────────────┐
  │ Serveur MCP fomo-ia          │              │ Sous-agent lecteur-article   │
  │ (server.py, 4 outils)        │              │ lecture seule : WebFetch,    │
  │ HN · Bluesky · GitHub · arXiv│              │ Read. Rend des notes         │
  └──────────────┬───────────────┘              └──────────────▲───────────────┘
                 │ données brutes                              │ relit le lien
                 ▼                                             │
     Claude trie par le sens, compose ───► digests/AAAA-MM-JJ.md ─┘
```

Le principe qui guide tout le projet : **le code fait ce qui doit être exact et testable** (récupérer, compter, trier par score, gérer les erreurs). **Le modèle fait ce qui demande du jugement** (dire si un titre parle d'IA, résumer, vulgariser).

## Les briques Claude, une par une

### 1. Serveur MCP — [`server.py`](server.py)

**C'est quoi.** Le *Model Context Protocol* est un standard qui permet d'exposer des « outils » à un modèle. Claude Code lance le serveur, découvre ses outils et les appelle quand il en a besoin. Ici, le serveur est écrit avec le SDK officiel Python (`FastMCP`) et communique en *stdio*, c'est-à-dire par l'entrée et la sortie standard du process.

**Ici.** 4 outils, branchés sur des APIs publiques, **zéro clé API** :

| Outil | Ce qu'il renvoie |
|---|---|
| `get_hackernews_top_stories` | Les top stories du moment, **sans filtre** : le tri IA est fait par Claude |
| `get_bluesky_buzz` | Les posts récents d'une liste d'experts, et les comptes « émergents » (repartagés par ≥ 3 experts sur 7 jours) |
| `get_trending_ai_repos` | Les repos GitHub les plus étoilés sur un topic, poussés récemment |
| `get_recent_arxiv_papers` | Les derniers papiers d'une catégorie arXiv (parsing Atom avec `xml.etree`) |

**Ce que j'en ai retenu.**
- **La docstring et les types sont l'interface** : c'est exactement ce que Claude lit pour décider comment appeler l'outil. Une docstring floue donne des appels flous.
- **Les erreurs sont renvoyées comme des données** (`{"error": "..."}`), jamais levées : une source en panne ne casse pas le digest, et Claude le signale simplement.
- **Déclaration par projet** dans [`.mcp.json`](.mcp.json) : quiconque clone le repo et lance `claude` à la racine récupère le serveur.
- Le SDK MCP est passé en 2.x (FastMCP y a été renommé), d'où la version bornée dans `requirements.txt` (`mcp>=1.20.0,<2`).

### 2. Skills — [`skills/`](skills/)

**C'est quoi.** Une skill est un dossier contenant un `SKILL.md` : un en-tête (`name`, `description`) et des instructions en langage naturel. Claude ne charge le corps que quand la `description` correspond à la demande, et la skill est aussi invocable directement par `/<name>`. C'est un « prompt caché » réutilisable, versionné avec le code.

**Ici.**
- [`daily-ai-fomo-briefing`](skills/daily-ai-fomo-briefing/SKILL.md) : l'orchestration du digest. Elle dit quels outils appeler et avec quels paramètres, comment trier (par le sens du titre, pas par mots-clés), quel format exact produire, et comment réagir à une source en panne. Elle enregistre le digest dans `digests/`.
- [`decrypte`](skills/decrypte/SKILL.md) : `/decrypte`. Elle trouve la cible (dans la conversation ou dans le dernier digest enregistré), demande lequel choisir si c'est ambigu, délègue la lecture au sous-agent, puis rédige en suivant des règles strictes : chaque terme technique en *italique* et défini dans un lexique, rien qui ne soit dans les sources, et « annoncé » bien distingué de « démontré ».
- **Fichier de référence** : [`references/bluesky-accounts.md`](skills/daily-ai-fomo-briefing/references/bluesky-accounts.md) contient les 13 experts Bluesky suivis. Ce sont des données que je modifie à la main, sans toucher au code. La skill les lit et les passe à l'outil.

**Ce que j'en ai retenu.**
- **Skill = savoir-faire, MCP = capacité.** Le serveur ne sait que chercher des données. Toute la « politique » (tri, format, ton) vit dans la skill et se change sans redéployer quoi que ce soit.
- La `description` décide du déclenchement : c'est elle qu'il faut soigner.
- Claude Code découvre les skills dans `.claude/skills/`. Les sources sont dans `skills/`, avec des **liens symboliques**, pour que la skill survive même si `.claude/` était retiré du dépôt.

### 3. Sous-agent — [`agents/lecteur-article.md`](agents/lecteur-article.md)

**C'est quoi.** Un sous-agent est une deuxième instance de Claude, avec son propre contexte, ses propres consignes et **sa propre liste d'outils autorisés**. Il travaille à part et ne rend qu'un résultat.

**Ici.** `/decrypte` confie la lecture complète des pages à `lecteur-article` :

```yaml
name: lecteur-article
tools: WebFetch, Read     # lecture seule : il ne peut ni écrire ni exécuter
model: sonnet             # un modèle plus léger suffit pour extraire des faits
```

Il renvoie des notes factuelles structurées (faits, chiffres, auteurs, limites, lisibilité de la page), et la skill rédige à partir de ces notes.

**Ce que j'en ai retenu.**
- **Isoler le contexte** : une page complète fait des milliers de mots. Lue dans le sous-agent, elle n'encombre pas la conversation principale, qui ne reçoit que les ~400 mots de notes.
- **Séparer les rôles** : lire (fidélité) et rédiger (pédagogie) sont deux prompts différents, dans deux fichiers différents.
- **Le verrou `tools:` est une vraie garantie**, appliquée par Claude Code. En revanche, « le Claude principal ne lit pas lui-même », c'est une consigne de la skill : elle se vérifie dans le terminal, où l'on voit le bloc `lecteur-article` travailler.
- Pas de sous-agent pour le digest quotidien : 4 appels rapides, un sous-agent n'y apporterait que du coût et de la latence.

### 4. CLAUDE.md — [`CLAUDE.md`](CLAUDE.md)

**C'est quoi.** Un fichier d'instructions que Claude Code lit automatiquement à chaque session dans ce dossier : commandes, structure et conventions du projet.

**Ici.** Il fixe les règles que Claude doit respecter en modifiant le code : erreurs renvoyées comme données, zéro clé API, un test mocké pour chaque nouveau comportement, passage par OpenSpec avant tout changement de comportement, et tout en français.

### 5. Spec-driven development avec OpenSpec — [`openspec/`](openspec/)

**C'est quoi.** [OpenSpec](https://openspec.dev/) formalise un cycle : **proposer** un changement (pourquoi, quoi, comment, tâches), l'**appliquer** tâche par tâche, puis l'**archiver**, ce qui fusionne ses exigences dans la spec officielle. Les exigences s'écrivent avec des scénarios `WHEN/THEN`, vérifiés par `openspec validate`.

**Ici.** Chaque évolution du projet est passée par ce cycle. L'historique se lit dans [`openspec/changes/archive/`](openspec/changes/archive/) :

| Change | Ce qui a changé |
|---|---|
| `add-daily-fomo-briefing` | Le serveur MCP et la skill de digest |
| `hn-semantic-filter` | Le filtre HN par mots-clés (qui ratait « LLMs », « Nvidia »…) remplacé par un tri sémantique fait par Claude |
| `add-bluesky-source` | 4ᵉ source, liste d'experts et détection des « nouveaux visages » |
| `add-decrypte-skill` | `/decrypte`, le sous-agent lecteur et l'enregistrement des digests |

Le comportement actuel est dans [`openspec/specs/`](openspec/specs/) (`fomo-briefing`, `decryptage`). Chaque `design.md` archivé garde les alternatives écartées et leurs raisons. Les commandes `/opsx:propose`, `/opsx:apply` et `/opsx:archive` sont fournies par `openspec init` (dans `.claude/`).

**Ce que j'en ai retenu.** Écrire le « pourquoi » avant le code change les décisions. Par exemple, la première idée pour le filtre HN était d'ajouter les pluriels à une regex. En l'écrivant, il est devenu évident que c'était une course sans fin, et que le jugement devait revenir au modèle.

### 6. Gherkin — [`spec/`](spec/)

Les mêmes comportements, écrits en `Given/When/Then` classique, lisibles sans connaître le code. Ils servent de documentation (aucun *step definition*, donc ils ne sont pas exécutés).

### 7. Tests mockés — [`test_server.py`](test_server.py)

15 tests `unittest` qui remplacent les APIs par de fausses réponses (`patch.object(server.requests, "get", ...)`). Ils vérifient le tri, les limites, le parsing et la gestion d'erreur, dont la règle « 3 experts distincts, pas 2, même avec 5 reposts ». Aucun appel réseau : ils tournent partout, en une fraction de seconde. Ce que le modèle décide (tri sémantique, rédaction) n'est pas mockable. C'est vérifié sur de vrais lancements, et noté comme tel dans les tâches OpenSpec.

### 8. Revue de code par IA — [`REVIEW.md`](REVIEW.md)

Le diff initial relu par Claude : une incohérence de gestion d'erreur entre les outils a été trouvée et corrigée, et des tests de non-régression ont été ajoutés. Les limites restantes sont documentées plutôt que cachées.

### 9. Vibe coding

Le projet est construit en conversation avec Claude Code : l'essentiel du code est généré et itéré directement, avec une vérification ciblée là où ça compte (gestion d'erreur, parsing, règles de comptage), des tests écrits avant le code, et un vrai lancement à la fin de chaque change.

## Structure du repo

```
server.py                         serveur MCP (4 outils)
test_server.py                    tests mockés
.mcp.json                         déclaration du serveur pour Claude Code
CLAUDE.md                         instructions projet lues par Claude Code
skills/
  daily-ai-fomo-briefing/         skill du digest
    references/bluesky-accounts.md   experts Bluesky suivis
  decrypte/                       skill /decrypte
agents/lecteur-article.md         sous-agent de lecture (lecture seule)
.claude/                          liens vers skills/ et agents/, plus les outils OpenSpec
openspec/specs/                   comportement actuel (WHEN/THEN)
openspec/changes/archive/         historique des changements et des décisions
spec/*.feature                    mêmes comportements en Gherkin
digests/                          digests générés (local, ignoré par Git)
```

## Installer et lancer

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
claude          # à lancer depuis la racine du repo
```

Claude Code détecte le serveur MCP via `.mcp.json` et demande une validation la première fois (vérifier avec `/mcp`). Les skills et le sous-agent sont découverts automatiquement via `.claude/`. Ensuite :

- *« fais-moi le FOMO IA du jour »* → le digest, aussi enregistré dans `digests/AAAA-MM-JJ.md`
- `/decrypte <titre | rang | url | thème>` → le décryptage d'un élément

`python server.py` seul ne semble rien faire : c'est normal, il attend un client MCP sur l'entrée standard. Pour Claude Desktop, déclarer le serveur dans sa config avec des chemins absolus (`/decrypte` n'y fonctionnera pas, faute de WebFetch).

## Tester

```bash
python test_server.py            # 15 tests mockés, sans réseau
```

Vrais appels réseau (testés sur Mac le 28/09/2026 : les quatre APIs répondent) :

```bash
python -c "import server; print(server.get_hackernews_top_stories(limit=3))"
python -c "import server; print(server.get_bluesky_buzz(['simonwillison.net', 'emollick.bsky.social']))"
python -c "import server; print(server.get_trending_ai_repos(limit=3))"
python -c "import server; print(server.get_recent_arxiv_papers(limit=2))"
```

## Limites connues (assumées)

- Pas de déduplication entre les sources, ni de mémoire d'un jour à l'autre : un « nouveau visage » Bluesky peut réapparaître plusieurs jours de suite.
- Le tri des stories HN et des posts Bluesky est fait par Claude : plus fin qu'une liste de mots-clés, mais pas testable automatiquement et un peu variable d'un lancement à l'autre.
- GitHub Search est appelé sans authentification : le rate limit est bas, suffisant pour un usage perso.
- Bluesky : la recherche plein texte est fermée aux anonymes, d'où la liste d'experts. Un expert très actif peut occuper plusieurs places dans la section.
- `/decrypte` dépend de WebFetch (Claude Code). Un article derrière un paywall est signalé, pas deviné.

## Pistes

- Lancer le digest automatiquement (GitHub Actions, avec une *issue* comme notification), plutôt en déclenchement manuel que tous les jours, pour ne pas consommer inutilement.
- Limiter le nombre de posts par expert dans la section Bluesky.
- Un token GitHub optionnel pour relever le rate limit.
- Un exemple de vraie boucle agentique (reason → act → observe) : c'est l'objet de mon autre projet, [RunCrew Coach IA](https://github.com/maymiled), un agent Claude Haiku avec MCP.
