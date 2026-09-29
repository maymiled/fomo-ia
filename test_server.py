"""
Tests de la logique du serveur FOMO IA, SANS appel réseau réel.

Pourquoi des mocks : les tests doivent tourner partout, vite et sans
dépendre de la disponibilité des APIs (Hacker News, GitHub, arXiv, Bluesky).
Ils vérifient la logique de tri, de parsing et de gestion d'erreur ; ils ne
remplacent pas un vrai appel réseau de temps en temps :

    pip install -r requirements.txt
    python test_server.py        # ces tests mockés
    python -c "import server; print(server.get_recent_arxiv_papers(limit=2))"  # vrai appel réseau
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import server


class FakeResponse:
    def __init__(self, json_data=None, text_data="", status_code=200):
        self._json_data = json_data
        self.text = text_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def make_fake_hn_get(fake_items):
    """Simule l'API HN : topstories.json renvoie les IDs dans l'ordre du dict."""

    def fake_get(url, timeout=10):
        if url.endswith("topstories.json"):
            return FakeResponse(json_data=list(fake_items.keys()))
        item_id = int(url.rsplit("/", 1)[-1].replace(".json", ""))
        return FakeResponse(json_data=fake_items[item_id])

    return fake_get


class TestHackerNewsTopStories(unittest.TestCase):
    def test_returns_all_topics_sorted_by_score(self):
        # Plus de filtre IA côté serveur : c'est la skill (Claude) qui trie.
        fake_items = {
            1: {"id": 1, "title": "New Claude Skills feature ships", "score": 120},
            2: {"id": 2, "title": "A history of French cheese", "score": 500},
            3: {"id": 3, "title": "Why LLMs fail at math", "score": 80},
        }

        with patch.object(server.requests, "get", side_effect=make_fake_hn_get(fake_items)):
            result = server.get_hackernews_top_stories(limit=5)

        self.assertEqual(
            [r["title"] for r in result],
            ["A history of French cheese", "New Claude Skills feature ships", "Why LLMs fail at math"],
        )
        self.assertEqual(result[0]["hn_url"], "https://news.ycombinator.com/item?id=2")

    def test_limit_truncates_results(self):
        fake_items = {i: {"id": i, "title": f"Story {i}", "score": i} for i in range(1, 6)}

        with patch.object(server.requests, "get", side_effect=make_fake_hn_get(fake_items)):
            result = server.get_hackernews_top_stories(limit=3)

        self.assertEqual(len(result), 3)

    def test_skips_items_without_title(self):
        fake_items = {
            1: {"id": 1, "title": "Show HN: my agent framework", "score": 10},
            2: {"id": 2, "score": 99},  # story supprimée ou sans titre
        }

        with patch.object(server.requests, "get", side_effect=make_fake_hn_get(fake_items)):
            result = server.get_hackernews_top_stories(limit=5)

        self.assertEqual([r["title"] for r in result], ["Show HN: my agent framework"])

    def test_returns_error_object_when_topstories_call_fails(self):
        with patch.object(server.requests, "get", side_effect=RuntimeError("boom")):
            result = server.get_hackernews_top_stories(limit=5)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


class TestTrendingRepos(unittest.TestCase):
    def test_parses_github_search_results(self):
        fake_payload = {
            "items": [
                {
                    "full_name": "someorg/agentic-toolkit",
                    "stargazers_count": 4200,
                    "description": "Toolkit for building agent loops",
                    "html_url": "https://github.com/someorg/agentic-toolkit",
                    "pushed_at": "2026-09-20T10:00:00Z",
                }
            ]
        }
        with patch.object(
            server.requests, "get", return_value=FakeResponse(json_data=fake_payload)
        ):
            result = server.get_trending_ai_repos(topic="llm", limit=5)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "someorg/agentic-toolkit")
        self.assertEqual(result[0]["stars"], 4200)

    def test_handles_github_error_gracefully(self):
        with patch.object(
            server.requests,
            "get",
            return_value=FakeResponse(json_data={}, text_data="rate limited", status_code=403),
        ):
            result = server.get_trending_ai_repos()

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


SAMPLE_ARXIV_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2609.00001v1</id>
    <title>  A Study of   Loop Engineering
    for Coding Agents </title>
    <summary>We explore how agentic loops improve over static prompt chains
    in real-world coding tasks and propose a benchmark.</summary>
    <published>2026-09-20T00:00:00Z</published>
    <author><name>A. Researcher</name></author>
    <author><name>B. Researcher</name></author>
  </entry>
</feed>
"""


class TestArxivParsing(unittest.TestCase):
    def test_parses_atom_feed_correctly(self):
        papers = server._parse_arxiv_feed(SAMPLE_ARXIV_ATOM, limit=5)
        self.assertEqual(len(papers), 1)
        paper = papers[0]
        self.assertEqual(paper["title"], "A Study of Loop Engineering for Coding Agents")
        self.assertEqual(paper["authors"], ["A. Researcher", "B. Researcher"])
        self.assertTrue(paper["url"].startswith("http://arxiv.org/abs/"))
        self.assertTrue(paper["summary"].startswith("We explore how agentic loops"))

    def test_returns_error_object_when_arxiv_call_fails(self):
        with patch.object(server.requests, "get", side_effect=RuntimeError("timeout")):
            result = server.get_recent_arxiv_papers()

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


def hours_ago(hours):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def bsky_post(handle, rkey, text, likes, hours, embed=None):
    """Un post tel que renvoyé par app.bsky.feed.getAuthorFeed."""
    post = {
        "uri": f"at://did:plc:{handle}/app.bsky.feed.post/{rkey}",
        "author": {"handle": handle, "displayName": handle.split(".")[0].title()},
        "record": {"text": text, "createdAt": hours_ago(hours)},
        "likeCount": likes,
        "repostCount": 1,
        "indexedAt": hours_ago(hours),
    }
    if embed:
        post["embed"] = embed
    return {"post": post}


def bsky_repost(expert, author, rkey, hours):
    item = bsky_post(author, rkey, f"post de {author}", 10, hours + 1)
    item["reason"] = {
        "$type": "app.bsky.feed.defs#reasonRepost",
        "by": {"handle": expert},
        "indexedAt": hours_ago(hours),
    }
    return item


def bsky_quote(expert, author, rkey, hours):
    embed = {
        "$type": "app.bsky.embed.record#view",
        "record": {
            "uri": f"at://did:plc:{author}/app.bsky.feed.post/q{rkey}",
            "author": {"handle": author, "displayName": author.split(".")[0].title()},
            "value": {"text": f"post cité de {author}"},
        },
    }
    return bsky_post(expert, rkey, "regardez ça", 5, hours, embed=embed)


def make_fake_bsky_get(feeds):
    """Simule getAuthorFeed : `feeds` associe un handle à ses items, ou à une exception."""

    def fake_get(url, params=None, timeout=10):
        feed = feeds[params["actor"]]
        if isinstance(feed, Exception):
            raise feed
        return FakeResponse(json_data={"feed": feed})

    return fake_get


class TestBlueskyBuzz(unittest.TestCase):
    def run_tool(self, feeds, **kwargs):
        with patch.object(server.requests, "get", side_effect=make_fake_bsky_get(feeds)):
            return server.get_bluesky_buzz(handles=list(feeds.keys()), **kwargs)

    def test_returns_recent_own_posts_sorted_by_likes(self):
        feeds = {
            "alice.bsky.social": [
                bsky_post("alice.bsky.social", "a1", "Nouveau modèle testé", 50, hours=3),
                bsky_post("alice.bsky.social", "a2", "Vieux post", 999, hours=24 * 5),
                bsky_repost("alice.bsky.social", "zoe.bsky.social", "z1", hours=2),
            ],
            "bob.bsky.social": [
                bsky_post("bob.bsky.social", "b1", "Mon avis sur les agents", 120, hours=10),
            ],
        }
        result = self.run_tool(feeds)

        self.assertEqual([p["text"] for p in result["posts"]], ["Mon avis sur les agents", "Nouveau modèle testé"])
        self.assertEqual(result["posts"][0]["url"], "https://bsky.app/profile/bob.bsky.social/post/b1")
        self.assertEqual(result["posts"][0]["likes"], 120)
        self.assertEqual(result["unavailable"], [])

    def test_account_shared_by_three_experts_is_rising(self):
        feeds = {
            "e1.bsky.social": [bsky_repost("e1.bsky.social", "newcomer.dev", "n1", hours=20)],
            "e2.bsky.social": [bsky_repost("e2.bsky.social", "newcomer.dev", "n2", hours=50)],
            "e3.bsky.social": [bsky_quote("e3.bsky.social", "newcomer.dev", "e3q", hours=24 * 6)],
        }
        result = self.run_tool(feeds)

        self.assertEqual(len(result["rising"]), 1)
        rising = result["rising"][0]
        self.assertEqual(rising["handle"], "newcomer.dev")
        self.assertEqual(rising["expert_count"], 3)
        self.assertEqual(sorted(rising["experts"]), ["e1.bsky.social", "e2.bsky.social", "e3.bsky.social"])

    def test_two_experts_are_not_enough_even_with_many_reposts(self):
        feeds = {
            "e1.bsky.social": [
                bsky_repost("e1.bsky.social", "almost.dev", f"x{i}", hours=5 + i) for i in range(5)
            ],
            "e2.bsky.social": [bsky_repost("e2.bsky.social", "almost.dev", "y1", hours=5)],
            "e3.bsky.social": [bsky_repost("e3.bsky.social", "almost.dev", "old", hours=24 * 10)],
        }
        result = self.run_tool(feeds)

        self.assertEqual(result["rising"], [])

    def test_experts_reposting_each_other_are_never_rising(self):
        feeds = {
            "e1.bsky.social": [bsky_post("e1.bsky.social", "p1", "post", 10, hours=1)],
            "e2.bsky.social": [bsky_repost("e2.bsky.social", "e1.bsky.social", "p1", hours=1)],
            "e3.bsky.social": [bsky_repost("e3.bsky.social", "e1.bsky.social", "p1", hours=1)],
            "e4.bsky.social": [bsky_repost("e4.bsky.social", "e1.bsky.social", "p1", hours=1)],
        }
        result = self.run_tool(feeds)

        self.assertEqual(result["rising"], [])

    def test_failing_account_is_reported_as_unavailable(self):
        feeds = {
            "ok.bsky.social": [bsky_post("ok.bsky.social", "o1", "Toujours là", 7, hours=1)],
            "gone.bsky.social": RuntimeError("Profile not found"),
        }
        result = self.run_tool(feeds)

        self.assertEqual([p["text"] for p in result["posts"]], ["Toujours là"])
        self.assertEqual(result["unavailable"], ["gone.bsky.social"])

    def test_returns_error_when_every_account_fails(self):
        feeds = {"a.bsky.social": RuntimeError("timeout"), "b.bsky.social": RuntimeError("timeout")}
        result = self.run_tool(feeds)

        self.assertIn("error", result)

    def test_returns_error_when_handles_is_empty(self):
        result = server.get_bluesky_buzz(handles=[])

        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
