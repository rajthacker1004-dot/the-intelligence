import pytest
from unittest.mock import patch, MagicMock
from feeds import fetch_all_feeds

SAMPLE_SOURCE = {
    "name": "Test Feed",
    "url": "https://example.com/feed.xml",
    "category": "ai",
    "type": "newsletter"
}

MOCK_FEED = MagicMock()
MOCK_FEED.entries = [
    MagicMock(
        title="Test AI Story",
        link="https://example.com/story-1",
        summary="A test summary about AI.",
        published_parsed=(2026, 4, 6, 7, 0, 0, 0, 0, 0),
        get=lambda k, d=None: d
    )
]
MOCK_FEED.bozo = False


def test_fetch_returns_list():
    with patch("feeds.feedparser.parse", return_value=MOCK_FEED):
        results = fetch_all_feeds([SAMPLE_SOURCE])
    assert isinstance(results, list)


def test_fetch_injects_source_metadata():
    with patch("feeds.feedparser.parse", return_value=MOCK_FEED):
        results = fetch_all_feeds([SAMPLE_SOURCE])
    assert len(results) > 0
    assert results[0]["_source_name"] == "Test Feed"
    assert results[0]["_category"] == "ai"
    assert results[0]["_source_type"] == "newsletter"


def test_fetch_handles_failed_feed():
    bad = MagicMock()
    bad.entries = []
    bad.bozo = True
    bad.bozo_exception = Exception("Connection failed")
    with patch("feeds.feedparser.parse", return_value=bad):
        results = fetch_all_feeds([SAMPLE_SOURCE])
    assert results == []
