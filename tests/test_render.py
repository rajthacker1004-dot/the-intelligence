import json
from datetime import datetime, timezone
from pathlib import Path
import pytest
from render import render_digest, get_archive_dates

PROFILE = {
    "name": "Raj Thacker",
    "sidebar_target": "18,000+ AED/month",
    "tldr_suffixes": {"ai": ".", "tourism": ".", "jobs": "."}
}

STORIES = [
    {
        "title": "Gemini beats benchmarks", "url": "https://x.com/1",
        "summary": "Google model wins.", "source_name": "Nick Saraev",
        "source_type": "youtube", "category": "ai", "creator": "Nick Saraev",
        "published": datetime(2026, 4, 6, 7, 0, tzinfo=timezone.utc),
        "published_str": "6 Apr 7:00 AM", "reading_time": "18 min video",
        "is_new": True, "tags": ["#Gemini"], "is_hero": True,
        "match_score": None, "match_score_str": None, "match_level": None,
        "gujarat": False, "salary_min": 0,
    },
]

RUN_TIME = datetime(2026, 4, 6, 3, 30, tzinfo=timezone.utc)


def test_creates_index_html(tmp_path):
    render_digest(STORIES, PROFILE, RUN_TIME, [], docs_dir=str(tmp_path))
    assert (tmp_path / "index.html").exists()

def test_creates_digest_archive(tmp_path):
    render_digest(STORIES, PROFILE, RUN_TIME, [], docs_dir=str(tmp_path))
    assert (tmp_path / "digests" / "2026-04-06.html").exists()

def test_index_contains_title(tmp_path):
    render_digest(STORIES, PROFILE, RUN_TIME, [], docs_dir=str(tmp_path))
    content = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "Gemini beats benchmarks" in content

def test_saves_manifest(tmp_path):
    render_digest(STORIES, PROFILE, RUN_TIME, [], docs_dir=str(tmp_path))
    manifest = json.loads((tmp_path / "digests" / "manifest.json").read_text())
    assert any(d["date"] == "2026-04-06" for d in manifest)
