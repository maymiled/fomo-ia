# FOMO IA

Veille quotidienne IA : un serveur MCP (`server.py`, FastMCP, 4 outils : Hacker News, GitHub, arXiv, Bluesky) orchestré par une Claude Skill (`skills/daily-ai-fomo-briefing/SKILL.md`) qui compose un digest markdown.

## Commandes

```bash
source .venv/bin/activate && pip install -r requirements.txt   # Python >= 3.10
python test_server.py                                          # tests mockés, sans réseau
python -c "import server; print(server.get_recent_arxiv_papers(limit=2))"   # vrai appel réseau
npx -y @fission-ai/openspec@latest validate --all                  # CLI OpenSpec (non installé globalement)
```

Le serveur MCP est déclaré dans `.mcp.json` (chemins relatifs : lancer `claude` depuis la racine, avec le `.venv` installé). Ne pas l'enregistrer en plus via `claude mcp add fomo-ia`, sinon il est déclaré en double.

`python server.py` seul ne fait rien de visible : il attend un client MCP sur stdin (transport stdio).

## Structure

- `server.py` : outils MCP (`@mcp.tool()`). La docstring et les types sont ce que Claude voit de l'outil.
- `test_server.py` : unittest + `patch.object(server.requests, "get", ...)`. Aucun test ne doit faire d'appel réseau réel.
- `skills/daily-ai-fomo-briefing/` : la skill (source). `references/bluesky-accounts.md` = comptes Bluesky suivis, lus par la skill et passés à `get_bluesky_buzz`. `.claude/skills/daily-ai-fomo-briefing` est un lien symbolique vers ce dossier, ne pas le dupliquer. Étape finale : enregistre le digest dans `digests/AAAA-MM-JJ.md` (ignoré par Git).
- `skills/decrypte/` : skill `/decrypte` (explique un élément du digest). Elle délègue la lecture à `agents/lecteur-article.md`, un sous-agent en lecture seule (`tools: WebFetch, Read`). Même principe de liens : `.claude/skills/decrypte`, `.claude/agents/lecteur-article.md`. Il faut relancer Claude Code pour qu'une nouvelle skill ou un nouvel agent soit découvert.
- `openspec/specs/` : specs courantes (WHEN/THEN) : `fomo-briefing`, `decryptage`. `openspec/changes/archive/` : changes terminés (proposal, design, tasks), avec l'historique des décisions.
- `spec/*.feature` : mêmes comportements en Gherkin (documentation, non exécuté).
- `.claude/skills/openspec-*`, `.claude/commands/opsx/` : générés par `openspec init`, ne pas modifier à la main.

## Conventions

- **Erreurs renvoyées comme données** : un outil ne lève jamais d'exception vers le client MCP. En cas d'échec, il renvoie `[{"error": "..."}]` (ou `{"error": "..."}` pour `get_bluesky_buzz`, qui renvoie un objet) pour que la skill continue avec les autres sources.
- Zéro clé API, dépendances limitées à `mcp` + `requests` (parsing XML via `xml.etree`).
- Tout nouveau comportement d'un outil s'accompagne d'un test mocké dans `test_server.py`.
- Un changement de comportement passe d'abord par OpenSpec (`/opsx:propose`), puis la spec et le Gherkin restent alignés avec le code.
- Code, commentaires et docs en français.
