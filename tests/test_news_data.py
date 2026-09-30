"""
tests/test_news_data.py
=======================
Unit tests for nodes/news_data.py.
All HTTP calls are mocked -- no live network required.
"""

import pytest
from unittest.mock import patch, MagicMock


# ---- helpers ----------------------------------------------------------

def _make_state(question: str) -> dict:
    return {
        "original_question": question,
        "current_question": question,
        "resolved_query": question,
    }


def _rss_xml_with(items):
    """Build a minimal RSS XML containing the given items."""
    item_blocks = ""
    for t, l, d, s in items:
        item_blocks += f"""<item>
  <title><![CDATA[{t}]]></title>
  <link><![CDATA[{l}]]></link>
  <pubDate><![CDATA[Sun, 28 Sep 2026 08:00:00 +0530]]></pubDate>
  <description><![CDATA[{s}]]></description>
</item>"""
    return f"""<?xml version="1.0"?><rss version="2.0"><channel>{item_blocks}</channel></rss>"""


_SAMPLE_ITEMS = [
    ("RBI hikes repo rate by 25 bps to 6.75%",
     "https://livemint.com/economy/rbi-hike",
     "Sun, 28 Sep 2026",
     "The RBI monetary policy committee unanimously decided to hike the repo rate."),
    ("SEBI tightens IPO disclosure norms",
     "https://livemint.com/markets/sebi-ipo",
     "Sun, 28 Sep 2026",
     "SEBI has issued a circular mandating stricter disclosures for IPO filings."),
    ("Nifty closes at record 26,000",
     "https://livemint.com/markets/nifty-record",
     "Sun, 28 Sep 2026",
     "The Nifty 50 closed at an all-time high of 26,000 points on heavy FII buying."),
]


def _mock_response(xml_text: str):
    mock = MagicMock()
    mock.status_code = 200
    mock.text = xml_text
    return mock


# ---- tests ------------------------------------------------------------

class TestNewsDataNode:

    def setup_method(self):
        """Clear feed cache between tests so mocks take effect."""
        import nodes.news_data as nd
        nd._FEED_CACHE.clear()

    @patch("nodes.news_data.requests.get")
    def test_returns_relevant_news_for_rbi_query(self, mock_get):
        """Query about RBI should return articles mentioning RBI."""
        xml = _rss_xml_with(_SAMPLE_ITEMS)
        mock_get.return_value = _mock_response(xml)

        from nodes.news_data import fetch_current_events
        result = fetch_current_events(_make_state("What is the latest RBI repo rate decision?"))

        ctx = result["retrieved_context"]
        assert len(ctx) == 1
        text = ctx[0]
        assert "RBI" in text or "rbi" in text.lower()
        # Source and date must be cited
        assert "LiveMint" in text
        assert "2026" in text or "Sep" in text

    @patch("nodes.news_data.requests.get")
    def test_fallback_when_all_feeds_fail(self, mock_get):
        """When every feed returns non-200, node returns a clean no-data message."""
        mock_get.return_value = MagicMock(status_code=503, text="")

        from nodes.news_data import fetch_current_events
        result = fetch_current_events(_make_state("latest RBI news"))

        ctx = result["retrieved_context"]
        assert len(ctx) == 1
        assert "No current information" in ctx[0]
        assert "temporarily unreachable" in ctx[0] or "feeds" in ctx[0].lower()

    @patch("nodes.news_data.requests.get")
    def test_fallback_when_no_relevant_items(self, mock_get):
        """
        Zero-relevance items on a non-generic, non-recency query -> clean fallback,
        not a random article list.
        """
        irrelevant_items = [
            ("Cricket World Cup 2026 schedule", "https://link", "date", "Cricket matches."),
            ("Best tourist spots in Goa", "https://link2", "date", "Tourism in India."),
        ]
        xml = _rss_xml_with(irrelevant_items)
        mock_get.return_value = _mock_response(xml)

        from nodes.news_data import fetch_current_events
        # Specific finance query with NO generic recency trigger words
        # (no 'news', 'latest', 'today', 'update', 'this week', 'what happened')
        result = fetch_current_events(_make_state(
            "Explain the RBI repo rate decision impact on bond yields"))

        ctx = result["retrieved_context"]
        assert len(ctx) == 1
        assert "No current information" in ctx[0]

    @patch("nodes.news_data.requests.get")
    def test_generic_news_request_returns_items_even_at_zero_score(self, mock_get):
        """
        A generic 'give me the latest news' query should get results even
        if the relevance scorer gives low scores (no specific topic tokens).
        """
        xml = _rss_xml_with(_SAMPLE_ITEMS)
        mock_get.return_value = _mock_response(xml)

        from nodes.news_data import fetch_current_events
        result = fetch_current_events(_make_state("What is the latest financial news today?"))

        ctx = result["retrieved_context"]
        assert len(ctx) == 1
        # Should have actual article titles
        assert "**1." in ctx[0] or "1." in ctx[0]

    @patch("nodes.news_data.requests.get")
    def test_citations_include_source_and_date(self, mock_get):
        """Every returned item must carry source and published date."""
        xml = _rss_xml_with(_SAMPLE_ITEMS)
        mock_get.return_value = _mock_response(xml)

        from nodes.news_data import fetch_current_events
        result = fetch_current_events(_make_state("SEBI IPO disclosure rules"))

        ctx = result["retrieved_context"][0]
        assert "Source:" in ctx
        assert "Published:" in ctx
        assert "LiveMint" in ctx

    @patch("nodes.news_data.requests.get")
    def test_feed_cache_prevents_duplicate_fetches(self, mock_get):
        """Second call within TTL should not trigger another HTTP request."""
        xml = _rss_xml_with(_SAMPLE_ITEMS)
        mock_get.return_value = _mock_response(xml)

        from nodes.news_data import fetch_current_events
        fetch_current_events(_make_state("nifty sensex today"))
        fetch_current_events(_make_state("nifty sensex today"))

        # 3 feeds, but should only be called 3 times total (first call only)
        assert mock_get.call_count == 3

    @patch("nodes.news_data.requests.get")
    def test_max_five_results_returned(self, mock_get):
        """Node must never return more than _TOP_N (5) items."""
        many = [
            (f"Finance headline {i}", f"https://link{i}", "date", f"Content about market {i}.")
            for i in range(20)
        ]
        xml = _rss_xml_with(many)
        mock_get.return_value = _mock_response(xml)

        from nodes.news_data import fetch_current_events
        result = fetch_current_events(_make_state("latest market news today"))

        ctx = result["retrieved_context"][0]
        # Count numbered entries
        count = len([l for l in ctx.split("\n") if l.startswith("**") and len(l) > 2 and l[2].isdigit()])
        assert count <= 5
