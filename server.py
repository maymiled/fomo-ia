"""
FOMO IA — MCP server
=====================

Serveur MCP (Model Context Protocol) qui expose quatre outils de veille IA,
tous branchés sur des APIs publiques, sans clé nécessaire :

- get_hackernews_top_stories -> top stories Hacker News du moment (le tri IA est fait par la skill)
- get_trending_ai_repos      -> repos GitHub récents/populaires sur un topic IA
- get_recent_arxiv_papers    -> derniers papiers arXiv sur une catégorie donnée
- get_bluesky_buzz           -> posts récents d'experts Bluesky + comptes qui émergent

Construit avec le SDK MCP officiel (FastMCP), pour pouvoir être branché
directement à Claude Code / Claude Desktop comme n'importe quel serveur MCP.

Lancer en local :
    pip install -r requirements.txt
    python server.py

Puis l'ajouter comme serveur MCP dans Claude Code / Claude Desktop (stdio).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("fomo-ia")

HN_BASE = "https://hacker-news.firebaseio.com/v0"
GITHUB_API = "https://api.github.com/search/repositories"
ARXIV_API = "http://export.arxiv.org/api/query"

# Au-delà, l'API HN a 500 top stories : inutile de toutes les télécharger.
HN_MAX_STORIES = 100

# API publique Bluesky : lecture sans clé. La recherche plein texte y est
# fermée aux anonymes, d'où l'approche par liste de comptes suivis.
BLUESKY_FEED_API = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
BLUESKY_MAX_HANDLES = 30
# Un compte hors liste est "émergent" s'il est repartagé ou cité par au moins
# 3 experts différents sur 7 jours : un vrai boom, pas une suggestion quotidienne.
BLUESKY_RISING_MIN_EXPERTS = 3
BLUESKY_RISING_DAYS = 7
BLUESKY_MAX_POSTS = 40
BLUESKY_MAX_RISING = 5

REQUEST_HEADERS = {
    # GitHub refuse les requêtes sans User-Agent.
    "User-Agent": "fomo-ia-mcp-server (personal project, github.com/maymiled)",
    "Accept": "application/vnd.github+json",
}


@mcp.tool()
def get_hackernews_top_stories(limit: int = 30) -> list[dict]:
    """Récupère les top stories Hacker News du moment, tous sujets confondus,
    triées par score décroissant. Aucun filtre thématique : c'est à toi de
    choisir celles qui parlent vraiment d'IA d'après le sens du titre.

    Args:
        limit: nombre de stories à récupérer en haut du classement HN
            (défaut 30, plafonné à 100).
    """
    limit = max(0, min(limit, HN_MAX_STORIES))
    try:
        top_ids_resp = requests.get(f"{HN_BASE}/topstories.json", timeout=10)
        top_ids_resp.raise_for_status()
        candidate_ids = top_ids_resp.json()[:limit]
    except Exception as exc:
        # Cohérent avec get_trending_ai_repos : une source qui échoue renvoie
        # une erreur lisible plutôt que de faire planter tout le briefing.
        return [{"error": f"Hacker News n'a pas répondu : {exc}"}]

    items: list[dict] = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {
            pool.submit(requests.get, f"{HN_BASE}/item/{item_id}.json", timeout=10): item_id
            for item_id in candidate_ids
        }
        for future in as_completed(futures):
            try:
                resp = future.result()
                resp.raise_for_status()
                data = resp.json()
            except Exception:
                continue
            if not data or not data.get("title"):
                continue
            items.append(
                {
                    "title": data["title"],
                    "score": data.get("score", 0),
                    "hn_url": f"https://news.ycombinator.com/item?id={data['id']}",
                    "url": data.get("url"),
                }
            )

    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:limit]


@mcp.tool()
def get_trending_ai_repos(topic: str = "llm", days: int = 7, limit: int = 8) -> list[dict]:
    """Récupère les repos GitHub les plus étoilés sur un topic IA donné, mis à
    jour dans les derniers jours (repos "chauds" plutôt qu'anciens et figés).

    Args:
        topic: topic GitHub à chercher (ex: "llm", "agentic-ai", "vibe-coding").
        days: fenêtre de fraîcheur en jours (défaut 7).
        limit: nombre maximum de repos à retourner (défaut 8).
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {
        "q": f"topic:{topic} pushed:>{since}",
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }
    resp = requests.get(GITHUB_API, params=params, headers=REQUEST_HEADERS, timeout=10)
    if resp.status_code != 200:
        # Pas de clé API -> rate limit bas côté GitHub (60 req/h). On renvoie
        # une erreur lisible plutôt que de planter l'appel de l'agent.
        return [
            {
                "error": f"GitHub API a répondu {resp.status_code}",
                "detail": resp.text[:300],
            }
        ]
    data = resp.json()
    return [
        {
            "name": repo["full_name"],
            "stars": repo["stargazers_count"],
            "description": repo.get("description"),
            "url": repo["html_url"],
            "pushed_at": repo["pushed_at"],
        }
        for repo in data.get("items", [])[:limit]
    ]


@mcp.tool()
def get_recent_arxiv_papers(category: str = "cs.AI", limit: int = 5) -> list[dict]:
    """Récupère les papiers arXiv les plus récents d'une catégorie donnée.

    Args:
        category: catégorie arXiv (ex: "cs.AI", "cs.CL", "cs.LG").
        limit: nombre maximum de papiers à retourner (défaut 5).
    """
    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": limit,
    }
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=10)
        resp.raise_for_status()
        return _parse_arxiv_feed(resp.text, limit)
    except Exception as exc:
        return [{"error": f"arXiv n'a pas répondu : {exc}"}]


def _parse_arxiv_feed(xml_text: str, limit: int) -> list[dict]:
    """Parse le flux Atom renvoyé par l'API arXiv. Séparée de la fonction
    outil pour pouvoir être testée sans appel réseau (voir test_server.py)."""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall("atom:entry", ns)[:limit]:
        title = entry.findtext("atom:title", default="", namespaces=ns).strip()
        title = re.sub(r"\s+", " ", title)
        summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
        summary = re.sub(r"\s+", " ", summary)
        authors = [
            a.findtext("atom:name", default="", namespaces=ns)
            for a in entry.findall("atom:author", ns)
        ]
        papers.append(
            {
                "title": title,
                "authors": authors,
                "summary": summary[:280] + ("…" if len(summary) > 280 else ""),
                "url": entry.findtext("atom:id", default="", namespaces=ns),
                "published": entry.findtext("atom:published", default="", namespaces=ns),
            }
        )
    return papers


@mcp.tool()
def get_bluesky_buzz(handles: list[str], hours: int = 48) -> dict:
    """Récupère ce que publient des experts Bluesky choisis, et repère les
    comptes qui émergent autour d'eux. Aucun filtre thématique : c'est à toi
    de garder les posts qui parlent vraiment d'IA.

    Renvoie {"posts": [...], "rising": [...], "unavailable": [...]} :
    - posts : posts écrits par ces comptes sur les `hours` dernières heures,
      triés par likes décroissants (les simples reposts sont exclus) ;
    - rising : comptes hors liste repartagés ou cités par au moins 3 experts
      différents sur les 7 derniers jours (souvent vide, c'est normal) ;
    - unavailable : comptes dont le fil n'a pas pu être lu.

    Args:
        handles: comptes Bluesky à suivre (ex: "simonwillison.net"), 30 max.
        hours: fenêtre de fraîcheur des posts en heures (défaut 48).
    """
    handles = list(dict.fromkeys(h.strip().lstrip("@") for h in handles if h.strip()))
    handles = handles[:BLUESKY_MAX_HANDLES]
    if not handles:
        return {"error": "Aucun compte Bluesky fourni."}

    now = datetime.now(timezone.utc)
    posts_since = now - timedelta(hours=hours)
    rising_since = now - timedelta(days=BLUESKY_RISING_DAYS)

    feeds: dict[str, list[dict]] = {}
    unavailable: list[str] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_fetch_bluesky_feed, handle): handle for handle in handles}
        for future in as_completed(futures):
            handle = futures[future]
            try:
                feeds[handle] = future.result()
            except Exception:
                unavailable.append(handle)

    if not feeds:
        # Cohérent avec les autres outils : l'échec est une donnée, pas une exception.
        return {"error": "Bluesky n'a répondu pour aucun des comptes suivis."}

    followed = set(handles)
    posts: list[dict] = []
    # Pour chaque auteur hors liste : experts distincts qui l'ont partagé,
    # et le post partagé le plus liké comme exemple.
    shared_by: dict[str, set[str]] = {}
    samples: dict[str, dict] = {}

    for handle, feed in feeds.items():
        for item in feed:
            post = item.get("post") or {}
            author = post.get("author") or {}
            reason = item.get("reason") or {}

            if reason.get("$type") == "app.bsky.feed.defs#reasonRepost":
                if _parse_bsky_date(reason.get("indexedAt")) >= rising_since:
                    _count_share(shared_by, samples, followed, handle, author, post)
                continue

            if author.get("handle") != handle:
                continue
            created = _parse_bsky_date(post.get("indexedAt"))
            if created >= posts_since:
                posts.append(_format_bsky_post(post))
            if created >= rising_since:
                quoted = _quoted_record(post.get("embed") or {})
                if quoted:
                    _count_share(shared_by, samples, followed, handle, quoted.get("author") or {}, quoted)

    posts.sort(key=lambda p: p["likes"], reverse=True)

    rising = [
        {
            "handle": author_handle,
            "display_name": samples[author_handle]["display_name"],
            "expert_count": len(experts),
            "experts": sorted(experts),
            "sample_post": samples[author_handle]["text"],
            "sample_url": samples[author_handle]["url"],
        }
        for author_handle, experts in shared_by.items()
        if len(experts) >= BLUESKY_RISING_MIN_EXPERTS
    ]
    rising.sort(key=lambda r: r["expert_count"], reverse=True)

    return {
        "posts": posts[:BLUESKY_MAX_POSTS],
        "rising": rising[:BLUESKY_MAX_RISING],
        "unavailable": sorted(unavailable),
    }


def _fetch_bluesky_feed(handle: str) -> list[dict]:
    params = {"actor": handle, "limit": 100, "filter": "posts_no_replies"}
    resp = requests.get(BLUESKY_FEED_API, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("feed", [])


def _parse_bsky_date(value: str | None) -> datetime:
    """Les dates Bluesky sont en ISO 8601 ("...Z"). Une date illisible est
    traitée comme très ancienne, donc hors de toutes les fenêtres."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)


def _bsky_url(handle: str, uri: str) -> str:
    return f"https://bsky.app/profile/{handle}/post/{uri.rsplit('/', 1)[-1]}"


def _format_bsky_post(post: dict) -> dict:
    author = post.get("author") or {}
    text = (post.get("record") or {}).get("text", "")
    return {
        "author": author.get("handle"),
        "author_name": author.get("displayName") or author.get("handle"),
        "text": text[:300] + ("…" if len(text) > 300 else ""),
        "likes": post.get("likeCount", 0),
        "reposts": post.get("repostCount", 0),
        "created_at": post.get("indexedAt"),
        "url": _bsky_url(author.get("handle", ""), post.get("uri", "")),
    }


def _quoted_record(embed: dict) -> dict | None:
    """Renvoie le post cité par une citation, ou None si ce n'en est pas une."""
    if embed.get("$type") == "app.bsky.embed.record#view":
        return embed.get("record")
    if embed.get("$type") == "app.bsky.embed.recordWithMedia#view":
        return (embed.get("record") or {}).get("record")
    return None


def _count_share(shared_by, samples, followed, expert, author, shared_post) -> None:
    """Note que `expert` a partagé un post de `author`, si `author` n'est pas
    déjà suivi. Un même expert ne compte qu'une fois par auteur (set)."""
    author_handle = author.get("handle")
    if not author_handle or author_handle in followed:
        return
    shared_by.setdefault(author_handle, set()).add(expert)
    likes = shared_post.get("likeCount", 0)
    if author_handle not in samples or likes > samples[author_handle]["likes"]:
        text = (shared_post.get("record") or shared_post.get("value") or {}).get("text", "")
        samples[author_handle] = {
            "display_name": author.get("displayName") or author_handle,
            "text": text[:200] + ("…" if len(text) > 200 else ""),
            "url": _bsky_url(author_handle, shared_post.get("uri", "")),
            "likes": likes,
        }


if __name__ == "__main__":
    mcp.run()
