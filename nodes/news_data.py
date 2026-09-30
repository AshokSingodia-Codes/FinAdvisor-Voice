"""
nodes/news_data.py -- Current-Events / Live News Node
======================================================
Fetches fresh financial news from Indian RSS feeds (no API key required).
Called when the router classifies a query as 'current_events'.

Feeds (all verified live 2026-09-28):
  LiveMint Economy  : https://www.livemint.com/rss/economy
  LiveMint Markets  : https://www.livemint.com/rss/markets
  LiveMint Industry : https://www.livemint.com/rss/industry

Returns retrieved_context for evidence_builder with source+date citations.
Bypasses Neo4j/vector retrieval -- static corpus cannot contain today's news.
"""

from __future__ import annotations

import re
import time
import requests
from typing import Any, Dict, List, Tuple
from graph.state import AgentState

# ---------------------------------------------------------------------------
# Feed catalogue
# ---------------------------------------------------------------------------

_FEEDS: List[Tuple[str, str]] = [
    ("LiveMint Economy",  "https://www.livemint.com/rss/economy"),
    ("LiveMint Markets",  "https://www.livemint.com/rss/markets"),
    ("LiveMint Industry", "https://www.livemint.com/rss/industry"),
]

_FETCH_TIMEOUT    = 8
_MAX_PER_FEED     = 35
_TOP_N            = 5
_CACHE_TTL        = 900  # 15 minutes

# In-process feed cache: url -> (fetched_ts, [items])
_FEED_CACHE: Dict[str, Tuple[float, List[Dict[str, str]]]] = {}

# ---------------------------------------------------------------------------
# Finance relevance vocabulary
# ---------------------------------------------------------------------------

_FINANCE_TERMS = {
    "rbi", "sebi", "repo", "inflation", "gdp", "budget", "tax",
    "nifty", "sensex", "ipo", "mutual fund", "nav", "stock", "share",
    "market", "rate", "bank", "interest", "bond", "rupee", "forex",
    "equity", "debt", "sip", "dividend", "profit", "revenue", "quarter",
    "economy", "finance", "fiscal", "monetary", "policy", "reform",
    "regulation", "amendment", "circular", "notification", "fdi", "crude",
}

_STOP = {
    "what", "how", "when", "where", "who", "is", "are", "was",
    "the", "a", "an", "in", "on", "of", "to", "for", "with",
    "about", "today", "latest", "new", "recent", "update",
    "give", "tell", "me", "please", "any",
}

# ---------------------------------------------------------------------------
# Parsing helpers (regex -- tolerates malformed XML from Indian news sites)
# ---------------------------------------------------------------------------

_CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)
_TAG_RE   = re.compile(r"<[^>]+>")
_WS_RE    = re.compile(r"\s+")
_ITEM_RE  = re.compile(r"<item>(.*?)</item>", re.DOTALL)

def _mk_field(tag: str):
    return re.compile(
        rf"<{tag}>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</{tag}>",
        re.DOTALL)

_TITLE_RE = _mk_field("title")
_LINK_RE  = _mk_field("link")
_DATE_RE  = _mk_field("pubDate")
_DESC_RE  = _mk_field("description")


def _unwrap(text: str) -> str:
    m = _CDATA_RE.match(text)
    return m.group(1).strip() if m else text.strip()


def _plain(html: str) -> str:
    return _WS_RE.sub(" ", _TAG_RE.sub(" ", html)).strip()


def _parse_items(xml: str, src: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for raw in _ITEM_RE.findall(xml):
        tm = _TITLE_RE.search(raw)
        lm = _LINK_RE.search(raw)
        dm = _DATE_RE.search(raw)
        sm = _DESC_RE.search(raw)

        title   = _unwrap(tm.group(1)) if tm else ""
        link    = _unwrap(lm.group(1)) if lm else ""
        pub     = _unwrap(dm.group(1))[:30] if dm else ""
        snippet = _plain(_unwrap(sm.group(1)))[:250] if sm else ""

        if title:
            out.append({"title": title, "link": link,
                        "pub": pub, "snippet": snippet, "source": src})
    return out


# ---------------------------------------------------------------------------
# Per-feed fetch with caching
# ---------------------------------------------------------------------------

def _fetch(name: str, url: str) -> List[Dict[str, str]]:
    now = time.time()
    cached = _FEED_CACHE.get(url)
    if cached and now - cached[0] < _CACHE_TTL:
        return cached[1]
    try:
        r = requests.get(url, timeout=_FETCH_TIMEOUT,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; FinAdvisor-X/2.0)"})
        if r.status_code != 200:
            print(f"  [news] {name}: HTTP {r.status_code}")
            return []
        items = _parse_items(r.text, name)
        _FEED_CACHE[url] = (now, items)
        return items
    except requests.RequestException as exc:
        print(f"  [news] {name}: {exc}")
        return []


# ---------------------------------------------------------------------------
# Relevance scoring
# ---------------------------------------------------------------------------

def _score(item: Dict[str, str], tokens: List[str]) -> int:
    hay = (item["title"] + " " + item["snippet"]).lower()
    s  = sum(3 for t in tokens if len(t) >= 3 and t in hay)
    s += sum(1 for term in _FINANCE_TERMS if term in hay)
    return s


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------

def fetch_current_events(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: 'current_events'
    Fetches live Indian financial news via RSS; returns top-N items with
    source + date citations for evidence_builder. Never fabricates -- returns
    a clear "no current information" when nothing relevant is found.
    """
    print("---NODE: CURRENT EVENTS (RSS)---")

    question = (state.get("resolved_query")
                or state.get("current_question")
                or state.get("original_question", ""))

    tokens = [t for t in re.sub(r"[^a-z0-9 ]", " ", question.lower()).split()
              if t not in _STOP and len(t) >= 3]

    # Collect from all feeds
    all_items: List[Dict[str, str]] = []
    for name, url in _FEEDS:
        all_items.extend(_fetch(name, url)[:_MAX_PER_FEED])

    if not all_items:
        return {"retrieved_context": [
            "**No current information available**: financial news feeds are "
            "temporarily unreachable. Please visit livemint.com or rbi.org.in."
        ]}

    top = sorted(all_items, key=lambda i: _score(i, tokens), reverse=True)[:_TOP_N]
    best = _score(top[0], tokens) if top else 0

    generic = any(tok in question.lower()
                  for tok in ["news", "latest", "update", "today",
                               "this week", "what happened"])
    if best == 0 and not generic:
        return {"retrieved_context": [
            "**No current information available** for this specific query. "
            "The static knowledge base does not contain today's events and no "
            "closely relevant recent news was found in the live feeds. "
            "Please check livemint.com or rbi.org.in for the latest updates."
        ]}

    ts  = time.strftime("%d %b %Y %H:%M IST")
    src = ", ".join(sorted({i["source"] for i in top}))
    lines = [
        f"### Recent Indian Financial News (as of {ts})\n"
        f"*(Live from {src})*\n"
    ]
    for idx, it in enumerate(top, 1):
        lines.append(
            f"**{idx}. {it['title']}**\n"
            f"   - **Source:** {it['source']}  |  **Published:** {it['pub']}\n"
            f"   - {it['snippet']}\n"
            f"   - {it['link']}\n"
        )
    return {"retrieved_context": ["\n".join(lines)]}
