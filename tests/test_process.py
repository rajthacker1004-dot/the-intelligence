from datetime import datetime, timezone
import pytest
from process import (
    clean_html, is_duplicate, score_job, tag_gujarat,
    is_new, extract_tags, estimate_reading_time,
    process_entries, build_tldr,
)

PROFILE = {
    "job_keywords": ["Risk", "Finance", "Python", "AI", "DIFC"],
    "gujarat_cities": ["Kutch", "Gandhidham", "Gujarat"],
    "tldr_suffixes": {
        "ai": "For your career.",
        "tourism": "For Rajal Tourism.",
        "jobs": "Apply today."
    }
}
RUN_TIME = datetime(2026, 4, 6, 3, 30, 0, tzinfo=timezone.utc)


def test_clean_html_strips_tags():
    assert clean_html("<p>Hello <b>world</b></p>") == "Hello world"

def test_clean_html_plain_text():
    assert clean_html("plain text") == "plain text"

def test_is_duplicate_exact_url():
    assert is_duplicate("https://x.com/s", "Any title", {"https://x.com/s"}, []) is True

def test_is_duplicate_similar_title():
    existing = [{"title": "GPT-5 delayed by six weeks due to safety issues"}]
    assert is_duplicate("https://new.com/x", "GPT-5 delayed six weeks over safety", set(), existing) is True

def test_not_duplicate_different_story():
    existing = [{"title": "GPT-5 delayed by six weeks"}]
    assert is_duplicate("https://y.com", "Gemini 2.5 Pro beats benchmarks", set(), existing) is False

def test_score_job_high_match():
    score = score_job("AI Risk Analyst Dubai DIFC Python", "Finance role", PROFILE["job_keywords"])
    assert score >= 40

def test_score_job_low_match():
    assert score_job("Chef de Partie", "Restaurant role", PROFILE["job_keywords"]) == 0

def test_tag_gujarat_found():
    assert tag_gujarat("Summer tourism in Kutch rises 22%", "", PROFILE["gujarat_cities"]) is True

def test_tag_gujarat_not_found():
    assert tag_gujarat("Kerala backwaters tourism boom", "", PROFILE["gujarat_cities"]) is False

def test_is_new_recent():
    published = datetime(2026, 4, 6, 1, 0, 0, tzinfo=timezone.utc)
    assert is_new(published, RUN_TIME) is True

def test_is_new_old():
    published = datetime(2026, 4, 5, 0, 0, 0, tzinfo=timezone.utc)
    assert is_new(published, RUN_TIME) is False

def test_extract_tags_finds_keywords():
    tags = extract_tags("Gemini 2.5 Pro beats OpenAI GPT-5", "")
    assert "#Gemini" in tags
    assert "#OpenAI" in tags

def test_extract_tags_max_five():
    tags = extract_tags("Gemini OpenAI GPT agents automation python streamlit RAG", "")
    assert len(tags) <= 5

def test_reading_time_youtube_with_duration():
    assert estimate_reading_time("youtube", 1080, "") == "18 min video"

def test_reading_time_youtube_no_duration():
    assert estimate_reading_time("youtube", None, "") == "Video"

def test_reading_time_article():
    words = " ".join(["word"] * 400)
    assert estimate_reading_time("newsletter", None, words) == "2 min read"

def test_process_entries_returns_stories():
    raw = [{
        "_source_name": "The Decoder", "_source_type": "newsletter", "_category": "ai",
        "title": "OpenAI delays GPT-5",
        "link": "https://the-decoder.com/gpt5",
        "summary": "OpenAI delays GPT-5 by six weeks.",
        "published_parsed": (2026, 4, 6, 5, 30, 0, 0, 96, 0),
        "media_content": [],
    }]
    stories = process_entries(raw, PROFILE, RUN_TIME)
    assert len(stories) == 1
    s = stories[0]
    assert s["title"] == "OpenAI delays GPT-5"
    assert s["category"] == "ai"
    assert isinstance(s["tags"], list)
    assert isinstance(s["is_new"], bool)

def test_process_marks_first_ai_as_hero():
    raw = [
        {"_source_name": "A", "_source_type": "newsletter", "_category": "ai",
         "title": "OpenAI announces GPT-5 with major reasoning upgrades", "link": "https://a.com/1", "summary": "Summary one.",
         "published_parsed": (2026, 4, 6, 5, 0, 0, 0, 96, 0), "media_content": []},
        {"_source_name": "B", "_source_type": "newsletter", "_category": "ai",
         "title": "Google Gemini beats every benchmark in head-to-head test", "link": "https://b.com/2", "summary": "Summary two.",
         "published_parsed": (2026, 4, 6, 4, 0, 0, 0, 96, 0), "media_content": []},
    ]
    stories = process_entries(raw, PROFILE, RUN_TIME)
    ai = [s for s in stories if s["category"] == "ai"]
    assert ai[0]["is_hero"] is True
    assert ai[1]["is_hero"] is False

def test_process_deduplicates():
    raw = [
        {"_source_name": "A", "_source_type": "newsletter", "_category": "ai",
         "title": "GPT-5 delayed six weeks", "link": "https://a.com/gpt5",
         "summary": "OpenAI delays.", "published_parsed": (2026, 4, 6, 5, 0, 0, 0, 96, 0), "media_content": []},
        {"_source_name": "B", "_source_type": "newsletter", "_category": "ai",
         "title": "GPT-5 delayed by six weeks over safety", "link": "https://b.com/gpt5",
         "summary": "OpenAI delays GPT-5.", "published_parsed": (2026, 4, 6, 4, 0, 0, 0, 96, 0), "media_content": []},
    ]
    stories = process_entries(raw, PROFILE, RUN_TIME)
    assert len(stories) == 1

def test_build_tldr_returns_five():
    stories = [
        {"title": f"S{i}", "summary": f"Summary {i}.", "category": c, "is_hero": False}
        for i, c in enumerate(["ai", "ai", "ai", "tourism", "jobs"])
    ]
    assert len(build_tldr(stories, PROFILE)) == 5

def test_build_tldr_one_per_category():
    stories = [
        {"title": "AI s", "summary": "AI.", "category": "ai", "is_hero": False},
        {"title": "Tour s", "summary": "Tour.", "category": "tourism", "is_hero": False},
        {"title": "Job s", "summary": "Job.", "category": "jobs", "is_hero": False},
        {"title": "AI 2", "summary": "AI2.", "category": "ai", "is_hero": False},
        {"title": "AI 3", "summary": "AI3.", "category": "ai", "is_hero": False},
    ]
    tldr = build_tldr(stories, PROFILE)
    cats = [item["category"] for item in tldr]
    assert "ai" in cats and "tourism" in cats and "jobs" in cats
