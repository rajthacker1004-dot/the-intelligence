# The Intelligence — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python script that fetches AI news, India tourism news, and Dubai jobs from RSS feeds, deduplicates and processes them, and generates a permanent static HTML digest page hosted free on GitHub Pages, delivered daily at 9am IST via GitHub Actions with no local machine required.

**Architecture:** Four focused Python modules (`feeds.py`, `process.py`, `render.py`) orchestrated by `fetch.py`. GitHub Actions runs the pipeline daily, commits generated HTML to `docs/`, and GitHub Pages serves it 24/7. No database, no server, no paid APIs.

**Tech Stack:** Python 3.x, feedparser, Jinja2, python-dateutil, GitHub Actions, GitHub Pages

---

## File Map

| File | Responsibility |
|---|---|
| `fetch.py` | Entry point — loads config, calls modules in order |
| `feeds.py` | Parallel RSS fetching via feedparser + ThreadPoolExecutor |
| `process.py` | Dedup, job scoring, Gujarat tagging, NEW badge, reading time, topic tags, hero selection, TL;DR |
| `render.py` | Jinja2 rendering — writes docs/index.html, docs/digests/YYYY-MM-DD.html, docs/digests/index.html |
| `sources.json` | RSS feed config — user edits this to add/remove sources, no code changes |
| `profile.json` | Raj's profile: scoring keywords, Gujarat cities, TL;DR suffixes |
| `templates/page.html` | Full HTML digest template with all CSS + JS inline, Jinja2 loops |
| `templates/archive.html` | Archive listing page template |
| `tests/test_process.py` | Unit tests for all process.py functions |
| `tests/test_render.py` | Unit tests for render.py output |
| `.github/workflows/daily.yml` | Cron job: runs at 9am IST, commits HTML output |
| `requirements.txt` | feedparser, Jinja2, python-dateutil |
| `.gitignore` | Exclude __pycache__, .env, .DS_Store |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `sources.json`
- Create: `profile.json`
- Create dirs: `docs/digests/`, `templates/`, `tests/`, `.github/workflows/`

- [ ] **Step 1: Create directory structure**

```bash
cd D:\the-intelligence
mkdir -p docs/digests templates tests .github/workflows
```

- [ ] **Step 2: Create requirements.txt**

```
feedparser==6.0.11
Jinja2==3.1.4
python-dateutil==2.9.0
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.env
.DS_Store
```

- [ ] **Step 4: Create sources.json**

```json
[
  {
    "name": "Nick Saraev",
    "url": "https://www.youtube.com/feeds/videos.xml?channel_id=REPLACE_WITH_CHANNEL_ID",
    "category": "ai",
    "type": "youtube",
    "note": "Find ID: go to youtube.com/@nicksaraev, view page source, search channelId"
  },
  {
    "name": "Julian Goldie",
    "url": "https://www.youtube.com/feeds/videos.xml?channel_id=REPLACE_WITH_CHANNEL_ID",
    "category": "ai",
    "type": "youtube",
    "note": "Find ID: go to youtube.com/@JulianGoldieSEO, view page source, search channelId"
  },
  {
    "name": "The Decoder",
    "url": "https://the-decoder.com/feed/",
    "category": "ai",
    "type": "newsletter"
  },
  {
    "name": "Import AI",
    "url": "https://importai.substack.com/feed",
    "category": "ai",
    "type": "newsletter"
  },
  {
    "name": "HuggingFace Blog",
    "url": "https://huggingface.co/blog/feed.xml",
    "category": "ai",
    "type": "newsletter"
  },
  {
    "name": "TechCrunch AI",
    "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "category": "ai",
    "type": "newsletter"
  },
  {
    "name": "Economic Times Travel",
    "url": "https://economictimes.indiatimes.com/travel/rssfeeds/2647163.cms",
    "category": "tourism",
    "type": "newsletter"
  },
  {
    "name": "Times of India Travel",
    "url": "https://timesofindia.indiatimes.com/rssfeeds/-2128938712.cms",
    "category": "tourism",
    "type": "newsletter"
  },
  {
    "name": "Bayt.com Dubai Jobs",
    "url": "https://www.bayt.com/en/uae/jobs/rss/?q=AI+risk+finance+data+analyst",
    "category": "jobs",
    "type": "jobpost"
  },
  {
    "name": "Gulf News Jobs",
    "url": "https://jobs.gulfnews.com/rss/jobs.xml",
    "category": "jobs",
    "type": "jobpost"
  }
]
```

- [ ] **Step 5: Create profile.json**

```json
{
  "name": "Raj Thacker",
  "target_salary_min_aed": 18000,
  "job_keywords": ["MSc", "Risk", "Finance", "Python", "AI", "Data Analyst", "Streamlit", "Machine Learning", "Dubai", "DIFC", "analytics", "quantitative"],
  "gujarat_cities": ["Kutch", "Gandhidham", "Bhuj", "Rann", "Gujarat", "Ahmedabad", "Surat", "Rajkot", "Vadodara", "Morbi", "Anand"],
  "tldr_suffixes": {
    "ai": "Relevant for your Dubai AI career.",
    "tourism": "Watch this for Rajal Tourism opportunities.",
    "jobs": "Apply today — your MSc Risk & Finance is a strong match."
  },
  "sidebar_target": "18,000+ AED/month · Dubai · April 2027"
}
```

- [ ] **Step 6: Initialise git repo**

```bash
cd D:\the-intelligence
git init
git add requirements.txt .gitignore sources.json profile.json
git commit -m "chore: project scaffolding"
```

---

## Task 2: RSS Fetching (feeds.py)

**Files:**
- Create: `feeds.py`
- Create: `tests/test_feeds.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_feeds.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:\the-intelligence
python -m pytest tests/test_feeds.py -v
```

Expected: `ImportError: No module named 'feeds'`

- [ ] **Step 3: Create feeds.py**

```python
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed


def _fetch_one(source: dict) -> list:
    """Fetch a single RSS feed. Returns list of entry dicts with source metadata injected."""
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo and not feed.entries:
            print(f"  [WARN] {source['name']}: {getattr(feed, 'bozo_exception', 'unknown')}")
            return []
        entries = []
        for entry in feed.entries:
            raw = {k: v for k, v in entry.items()}
            raw["_source_name"] = source["name"]
            raw["_source_type"] = source.get("type", "newsletter")
            raw["_category"] = source["category"]
            entries.append(raw)
        print(f"  [OK] {source['name']}: {len(entries)} entries")
        return entries
    except Exception as exc:
        print(f"  [ERROR] {source['name']}: {exc}")
        return []


def fetch_all_feeds(sources: list) -> list:
    """
    Fetch all RSS feeds in parallel.
    Returns flat list of entry dicts, each with _source_name/_source_type/_category.
    Source priority order preserved (first source wins dedup).
    """
    results_by_source = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {executor.submit(_fetch_one, src): src for src in sources}
        for future in as_completed(future_map):
            src = future_map[future]
            results_by_source[src["name"]] = future.result()

    # Return in sources.json order for dedup priority
    all_entries = []
    for src in sources:
        all_entries.extend(results_by_source.get(src["name"], []))
    return all_entries
```

- [ ] **Step 4: Install dependencies then run tests**

```bash
pip install feedparser jinja2 python-dateutil
python -m pytest tests/test_feeds.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add feeds.py tests/test_feeds.py requirements.txt
git commit -m "feat: parallel RSS fetching"
```

---

## Task 3: Processing Pipeline (process.py)

**Files:**
- Create: `process.py`
- Create: `tests/test_process.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_process.py`:

```python
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
    assert score >= 80

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
         "title": "AI Story One", "link": "https://a.com/1", "summary": "Summary one.",
         "published_parsed": (2026, 4, 6, 5, 0, 0, 0, 96, 0), "media_content": []},
        {"_source_name": "B", "_source_type": "newsletter", "_category": "ai",
         "title": "AI Story Two", "link": "https://b.com/2", "summary": "Summary two.",
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
```

- [ ] **Step 2: Run to verify they fail**

```bash
python -m pytest tests/test_process.py -v
```

Expected: `ImportError: No module named 'process'`

- [ ] **Step 3: Create process.py**

```python
import re
import difflib
from datetime import datetime, timezone, timedelta
from dateutil import parser as dateutil_parser

TOPIC_TAGS = {
    "gemini": "#Gemini", "openai": "#OpenAI", "chatgpt": "#ChatGPT",
    "gpt-5": "#GPT5", "gpt": "#GPT", "claude": "#Claude", "llama": "#Llama",
    "mistral": "#Mistral", "anthropic": "#Anthropic", "deepmind": "#DeepMind",
    "hugging face": "#HuggingFace", "google ai": "#GoogleAI",
    "agent": "#Agents", "automation": "#Automation", "n8n": "#n8n",
    "langchain": "#LangChain", "rag": "#RAG", "fine-tun": "#FineTuning",
    "benchmark": "#Benchmarks", "safety": "#AISafety", "open source": "#OpenSource",
    "seo": "#SEO", "python": "#Python", "streamlit": "#Streamlit",
    "gujarat": "#Gujarat", "kutch": "#Kutch", "gandhidham": "#Gandhidham",
    "tourism": "#Tourism", "travel": "#Travel",
    "difc": "#DIFC", "dubai": "#Dubai", "risk": "#Risk", "finance": "#Finance",
}


def clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def is_duplicate(url: str, title: str, seen_urls: set, seen_stories: list) -> bool:
    if url in seen_urls:
        return True
    for story in seen_stories:
        ratio = difflib.SequenceMatcher(None, title.lower(), story["title"].lower()).ratio()
        if ratio > 0.75:
            return True
    return False


def score_job(title: str, summary: str, keywords: list) -> int:
    combined = (title + " " + summary).lower()
    matches = sum(1 for kw in keywords if kw.lower() in combined)
    return min(100, matches * 10)


def tag_gujarat(title: str, summary: str, gujarat_cities: list) -> bool:
    combined = (title + " " + summary).lower()
    return any(city.lower() in combined for city in gujarat_cities)


def is_new(published: datetime, run_time: datetime) -> bool:
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    if run_time.tzinfo is None:
        run_time = run_time.replace(tzinfo=timezone.utc)
    return (run_time - published) <= timedelta(hours=3)


def extract_tags(title: str, summary: str) -> list:
    combined = (title + " " + summary).lower()
    found = []
    for keyword, tag in TOPIC_TAGS.items():
        if keyword in combined and tag not in found:
            found.append(tag)
        if len(found) == 5:
            break
    return found


def estimate_reading_time(source_type: str, duration_seconds, summary: str) -> str:
    if source_type == "youtube":
        if duration_seconds:
            mins = max(1, int(duration_seconds) // 60)
            return f"{mins} min video"
        return "Video"
    words = len(clean_html(summary).split())
    return f"{max(1, words // 200)} min read"


def _parse_published(entry: dict) -> datetime:
    parsed = entry.get("published_parsed")
    if parsed:
        try:
            import time
            return datetime.fromtimestamp(time.mktime(parsed), tz=timezone.utc)
        except Exception:
            pass
    raw = entry.get("published", "")
    if raw:
        try:
            dt = dateutil_parser.parse(raw)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return datetime.now(tz=timezone.utc)


def _format_published(dt: datetime) -> str:
    # Windows-safe: no %-d
    day = str(dt.day)
    return dt.strftime(f"{day} %b · %I:%M %p").replace(" 0", " ").strip()


def _get_duration_seconds(entry: dict):
    for media in entry.get("media_content", []):
        duration = media.get("duration")
        if duration:
            try:
                return int(duration)
            except (ValueError, TypeError):
                pass
    return None


def process_entries(raw_entries: list, profile: dict, run_time: datetime) -> list:
    seen_urls = set()
    stories = []
    first_ai_done = False

    for entry in raw_entries:
        url = entry.get("link", "")
        title = (entry.get("title") or "").strip()
        if not title or not url:
            continue
        if is_duplicate(url, title, seen_urls, stories):
            continue
        seen_urls.add(url)

        category = entry["_category"]
        source_type = entry["_source_type"]
        source_name = entry["_source_name"]
        summary_raw = entry.get("summary") or entry.get("description") or ""
        summary = clean_html(summary_raw)[:300]
        published = _parse_published(entry)
        duration_seconds = _get_duration_seconds(entry)

        match_score = match_score_str = match_level = None
        if category == "jobs":
            match_score = score_job(title, summary, profile["job_keywords"])
            match_score_str = f"{match_score}%"
            match_level = "high" if match_score >= 80 else ("mid" if match_score >= 50 else None)

        gujarat = tag_gujarat(title, summary, profile["gujarat_cities"]) if category == "tourism" else False

        is_hero = False
        if category == "ai" and not first_ai_done:
            is_hero = True
            first_ai_done = True

        stories.append({
            "title": title,
            "url": url,
            "summary": summary,
            "source_name": source_name,
            "source_type": source_type,
            "category": category,
            "creator": source_name,
            "published": published,
            "published_str": _format_published(published),
            "reading_time": estimate_reading_time(source_type, duration_seconds, summary_raw),
            "is_new": is_new(published, run_time),
            "tags": extract_tags(title, summary),
            "is_hero": is_hero,
            "match_score": match_score,
            "match_score_str": match_score_str,
            "match_level": match_level,
            "gujarat": gujarat,
            "salary_min": 0,  # placeholder — jobs RSS rarely includes salary
        })

    return stories


def build_tldr(stories: list, profile: dict) -> list:
    suffixes = profile.get("tldr_suffixes", {})
    tldr = []
    used = set()

    for cat in ["ai", "tourism", "jobs"]:
        for i, s in enumerate(stories):
            if s["category"] == cat and i not in used:
                text = s["summary"].split(".")[0] + "."
                tldr.append({"text": text, "category": cat,
                              "suffix": suffixes.get(cat, ""), "title": s["title"]})
                used.add(i)
                break

    for i, s in enumerate(stories):
        if len(tldr) >= 5:
            break
        if i not in used:
            text = s["summary"].split(".")[0] + "."
            tldr.append({"text": text, "category": s["category"],
                          "suffix": suffixes.get(s["category"], ""), "title": s["title"]})
            used.add(i)

    return tldr[:5]
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_process.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add process.py tests/test_process.py
git commit -m "feat: processing pipeline - dedup, scoring, tagging, TL;DR"
```

---

## Task 4: HTML Template (templates/page.html)

**Files:**
- Create: `templates/page.html`

Note: The search highlight uses safe DOM manipulation (createElement + createTextNode) — no innerHTML with untrusted content.

- [ ] **Step 1: Create templates/page.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Intelligence - {{ date_display }}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#FFFFFF;--bg-alt:#F4F4F5;--header:#09090B;--accent:#D946EF;--accent-soft:#FAE8FF;--text:#09090B;--text2:#71717A;--text3:#A1A1AA;--border:#E4E4E7;--border2:#D4D4D8;--ai:#2563EB;--ai-bg:#EFF6FF;--tour:#16A34A;--tour-bg:#F0FDF4;--job:#EA580C;--job-bg:#FFF7ED;--r:4px;--rm:8px}
body{font-family:'Inter',sans-serif;background:var(--bg-alt);color:var(--text);font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
.ticker-bar{background:var(--header);color:#71717A;font-size:11px;padding:7px 0;overflow:hidden;white-space:nowrap;border-bottom:1px solid #27272A}
.ticker-inner{display:inline-flex;animation:ticker 40s linear infinite}
.ticker-item{display:inline-flex;align-items:center;gap:12px;padding:0 28px}
.ticker-dot{width:4px;height:4px;border-radius:50%;background:#3F3F46}
.ticker-live{color:var(--accent);font-weight:700;font-size:9px;background:rgba(217,70,239,.12);padding:1px 6px;border-radius:3px;text-transform:uppercase;letter-spacing:.1em}
@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.header{background:var(--header);padding:0 24px;border-bottom:1px solid #27272A;position:sticky;top:0;z-index:100}
.header-inner{max-width:1140px;margin:0 auto;display:flex;align-items:center;gap:24px;height:58px}
.logo{font-family:'Space Grotesk',sans-serif;font-size:19px;font-weight:800;color:#FFF;letter-spacing:-.03em}
.logo span{color:var(--accent)}
.hdr-search{flex:1;max-width:360px;position:relative}
.hdr-search input{width:100%;background:#18181B;border:1px solid #3F3F46;color:#E4E4E7;border-radius:var(--r);padding:7px 12px 7px 34px;font-size:13px;font-family:'Inter',sans-serif;outline:none;transition:border-color .15s}
.hdr-search input:focus{border-color:var(--accent)}
.hdr-search input::placeholder{color:#52525B}
.s-ico{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:#52525B}
.hdr-date{font-size:12px;color:#52525B;font-weight:500;white-space:nowrap;margin-left:auto}
.page-body{max-width:1140px;margin:0 auto;padding:24px 24px 60px;display:grid;grid-template-columns:1fr 296px;gap:24px;align-items:start}
.cat-tabs{display:flex;gap:3px;margin-bottom:20px;background:var(--bg);border:1px solid var(--border);border-radius:var(--rm);padding:4px}
.cat-tab{flex:1;padding:8px 6px;border-radius:var(--r);font-size:12px;font-weight:600;font-family:'Inter',sans-serif;cursor:pointer;text-align:center;border:none;background:transparent;color:var(--text3);display:flex;align-items:center;justify-content:center;gap:5px;transition:all .15s}
.cat-tab:hover{color:var(--text2);background:var(--bg-alt)}
.active-all{background:var(--header);color:#FFF}
.active-ai{background:var(--ai-bg);color:var(--ai);border:1px solid #BFDBFE}
.active-tour{background:var(--tour-bg);color:var(--tour);border:1px solid #BBF7D0}
.active-job{background:var(--job-bg);color:var(--job);border:1px solid #FED7AA}
.tab-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.dot-ai{background:var(--ai)}.dot-t{background:var(--tour)}.dot-j{background:var(--job)}
.tab-count{font-size:10px;font-weight:700;padding:1px 5px;border-radius:10px;background:rgba(0,0,0,.06)}
.tldr-box{background:var(--bg);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:var(--rm);padding:16px 18px;margin-bottom:20px}
.tldr-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;cursor:pointer;user-select:none}
.tldr-title{font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);display:flex;align-items:center;gap:8px}
.tldr-badge{background:var(--accent);color:#fff;font-size:9px;font-weight:800;padding:2px 7px;border-radius:3px}
.tldr-toggle{font-size:11px;color:var(--text3);font-weight:500}
.tldr-list{list-style:none;display:flex;flex-direction:column;gap:8px}
.tldr-item{display:flex;align-items:flex-start;gap:10px;font-size:13px;color:var(--text);line-height:1.55}
.tldr-num{font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:800;color:var(--accent);min-width:18px;line-height:1.7}
.tldr-tag{font-size:10px;font-weight:700;padding:1px 6px;border-radius:3px;margin-left:6px;flex-shrink:0}
.ttag-ai{background:var(--ai-bg);color:var(--ai)}.ttag-tourism{background:var(--tour-bg);color:var(--tour)}.ttag-jobs{background:var(--job-bg);color:var(--job)}
.arch-strip{background:var(--bg);border:1px solid var(--border);border-radius:var(--rm);padding:10px 14px;margin-bottom:20px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.arch-label{font-size:10px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em}
.arch-pill{font-size:11px;font-weight:600;padding:4px 10px;border-radius:var(--r);background:var(--bg-alt);border:1px solid var(--border);color:var(--text2);cursor:pointer;transition:all .12s;text-decoration:none;display:inline-block}
.arch-pill:hover,.arch-pill.active{background:var(--header);color:#fff;border-color:var(--header)}
.sec-block{margin-bottom:28px}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;padding-bottom:10px;border-bottom:2px solid var(--text)}
.sec-head-left{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.sec-title{font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--text)}
.sec-badge{font-size:10px;font-weight:700;padding:2px 8px;border-radius:3px;text-transform:uppercase;letter-spacing:.04em}
.badge-ai{background:var(--ai-bg);color:var(--ai);border-left:3px solid var(--ai)}
.badge-tour{background:var(--tour-bg);color:var(--tour);border-left:3px solid var(--tour)}
.badge-job{background:var(--job-bg);color:var(--job);border-left:3px solid var(--job)}
.show-all{font-size:11px;font-weight:600;color:var(--text2);background:none;border:1px solid var(--border2);border-radius:var(--r);padding:5px 11px;cursor:pointer;font-family:'Inter',sans-serif;transition:all .15s}
.show-all:hover{background:var(--bg-alt);color:var(--text);border-color:var(--text)}
.filt{display:flex;gap:4px}
.fbtn{font-size:10px;font-weight:700;padding:4px 8px;border-radius:var(--r);border:1px solid var(--border);background:var(--bg);color:var(--text3);cursor:pointer;font-family:'Inter',sans-serif;transition:all .12s;white-space:nowrap}
.fbtn.fa{background:var(--ai-bg);color:var(--ai);border-color:var(--ai)}
.fbtn.ft{background:var(--tour-bg);color:var(--tour);border-color:var(--tour)}
.fbtn.fj{background:var(--job-bg);color:var(--job);border-color:var(--job)}
.cards{display:flex;flex-direction:column;gap:10px}
.card{background:var(--bg);border:1px solid var(--border);border-radius:var(--rm);padding:15px 18px;cursor:pointer;transition:all .15s;border-left:3px solid transparent}
.card:hover{border-color:var(--border2);box-shadow:0 2px 14px rgba(0,0,0,.07);transform:translateY(-1px)}
.card.cai{border-left-color:var(--ai)}.card.ct{border-left-color:var(--tour)}.card.cj{border-left-color:var(--job)}
.card.hero{background:linear-gradient(135deg,#EFF6FF,#F0F9FF);border:1px solid #BFDBFE;border-left:4px solid var(--ai);padding:20px 22px}
.card.hero h3{font-size:18px;font-weight:700}
.hero-lbl{display:inline-flex;align-items:center;gap:5px;font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:var(--ai);background:var(--ai-bg);border:1px solid #BFDBFE;padding:3px 8px;border-radius:3px;margin-bottom:10px}
.card.hidden{display:none}
.cmeta{display:flex;align-items:center;gap:7px;margin-bottom:8px;flex-wrap:wrap}
.spill{font-size:10px;font-weight:700;padding:2px 7px;border-radius:3px;text-transform:uppercase;letter-spacing:.05em}
.syt{background:#FEE2E2;color:#DC2626}.snl{background:var(--bg-alt);color:var(--text2);border:1px solid var(--border)}.sjob{background:var(--job-bg);color:var(--job);border:1px solid #FED7AA}
.cpill{font-size:10px;font-weight:700;padding:2px 7px;border-radius:3px;text-transform:uppercase;letter-spacing:.04em}
.cpai{background:var(--ai-bg);color:var(--ai)}.cpt{background:var(--tour-bg);color:var(--tour)}.cpj{background:var(--job-bg);color:var(--job)}
.nbadge{display:inline-flex;align-items:center;gap:4px;font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:var(--accent);background:var(--accent-soft);border:1px solid #F0ABFC;padding:2px 7px;border-radius:3px}
.ndot{width:5px;height:5px;border-radius:50%;background:var(--accent);animation:pulse 1.5s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.mbadge{display:inline-flex;align-items:center;gap:3px;font-size:10px;font-weight:700;padding:2px 7px;border-radius:3px}
.mh{background:#F0FDF4;color:#16A34A;border:1px solid #BBF7D0}.mm{background:var(--job-bg);color:var(--job);border:1px solid #FED7AA}
.rtime{font-size:11px;color:var(--text3);font-weight:500;display:flex;align-items:center;gap:3px}
.ctime{font-size:11px;color:var(--text3);font-variant-numeric:tabular-nums;margin-left:auto}
.card h3{font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:600;color:var(--text);line-height:1.42;margin-bottom:6px;letter-spacing:-.01em}
.card p{font-size:13px;color:var(--text2);line-height:1.6;margin-bottom:10px}
.ttags{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:10px}
.ttag{font-size:10px;font-weight:600;color:var(--text3);background:var(--bg-alt);border:1px solid var(--border);padding:2px 7px;border-radius:3px;cursor:pointer;transition:all .12s}
.ttag:hover{color:var(--ai);border-color:#BFDBFE;background:var(--ai-bg)}
.cfoot{display:flex;align-items:center;justify-content:space-between}
.cfoot-l{display:flex;align-items:center;gap:10px}
.csrc{font-size:12px;color:var(--accent);font-weight:600}
.cread{font-size:12px;color:var(--text3);font-weight:500;display:flex;align-items:center;gap:4px;text-decoration:none}
.bmark{background:none;border:none;cursor:pointer;padding:4px;color:var(--text3);transition:color .15s;display:flex;align-items:center}
.bmark:hover{color:var(--accent)}
.bmark.saved{color:var(--accent)}
.sidebar{display:flex;flex-direction:column;gap:18px}
.sb{background:var(--bg);border:1px solid var(--border);border-radius:var(--rm);overflow:hidden}
.sbh{padding:12px 16px;background:var(--header);display:flex;align-items:center;justify-content:space-between}
.sbt{font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#71717A}
.sblive{font-size:9px;font-weight:700;text-transform:uppercase;color:var(--accent);background:rgba(217,70,239,.12);padding:2px 6px;border-radius:3px}
.sg{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--border)}
.si{padding:14px 10px;text-align:center;background:var(--bg)}
.sn{font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;letter-spacing:-.03em;line-height:1;margin-bottom:3px}
.cn{color:var(--ai)}.ctn{color:var(--tour)}.cjn{color:var(--job)}
.sl{font-size:9px;color:var(--text3);font-weight:700;text-transform:uppercase;letter-spacing:.07em}
.tlist{list-style:none}
.ti{display:flex;align-items:flex-start;gap:10px;padding:11px 16px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .12s}
.ti:last-child{border-bottom:none}
.ti:hover{background:var(--bg-alt)}
.tn{font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:800;color:var(--border2);line-height:1.3;min-width:22px}
.tt{font-size:12px;font-weight:600;color:var(--text);line-height:1.45}
.tm{font-size:10px;color:var(--text3);margin-top:3px}
.ab{padding:15px 16px}
.ab p{font-size:12px;color:var(--text2);line-height:1.65;margin-bottom:10px}
.fbtn2{display:block;width:100%;padding:9px 16px;background:var(--accent);color:#fff;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;border:none;border-radius:var(--r);cursor:pointer;font-family:'Inter',sans-serif;text-align:center;transition:opacity .15s}
.fbtn2:hover{opacity:.87}
mark.hl{background:#FEF08A;color:inherit;border-radius:2px;padding:0 1px}
@media(max-width:768px){.page-body{grid-template-columns:1fr}.sidebar{display:none}.hdr-date{display:none}}
</style>
</head>
<body>

<div class="ticker-bar"><div class="ticker-inner">
{% for s in stories[:8] %}<span class="ticker-item">{% if loop.first %}<span class="ticker-live">Live</span>{% endif %}{{ s.title }}<span class="ticker-dot"></span></span>{% endfor %}
{% for s in stories[:8] %}<span class="ticker-item">{% if loop.first %}<span class="ticker-live">Live</span>{% endif %}{{ s.title }}<span class="ticker-dot"></span></span>{% endfor %}
</div></div>

<header class="header"><div class="header-inner">
  <div class="logo">The <span>Intelligence</span></div>
  <div class="hdr-search">
    <svg class="s-ico" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    <input id="srch" type="text" placeholder="Search this digest..." autocomplete="off">
  </div>
  <div class="hdr-date">{{ date_display }}</div>
</div></header>

<div class="page-body">
<main>
  <div class="cat-tabs">
    <button class="cat-tab active-all" data-cat="all">All <span class="tab-count">{{ stats.total }}</span></button>
    <button class="cat-tab" data-cat="ai"><span class="tab-dot dot-ai"></span> AI News <span class="tab-count">{{ stats.ai }}</span></button>
    <button class="cat-tab" data-cat="tourism"><span class="tab-dot dot-t"></span> Tourism India <span class="tab-count">{{ stats.tourism }}</span></button>
    <button class="cat-tab" data-cat="jobs"><span class="tab-dot dot-j"></span> Dubai Jobs <span class="tab-count">{{ stats.jobs }}</span></button>
  </div>

  <div class="tldr-box">
    <div class="tldr-hdr" onclick="toggleTldr()">
      <div class="tldr-title"><span class="tldr-badge">TL;DR</span> Today's 5 — 2-minute briefing</div>
      <span class="tldr-toggle" id="ttog">Collapse ↑</span>
    </div>
    <ul class="tldr-list" id="tlist">
      {% for item in tldr %}
      <li class="tldr-item">
        <span class="tldr-num">0{{ loop.index }}</span>
        <span>{{ item.text }} {{ item.suffix }} <span class="tldr-tag ttag-{{ item.category }}">{{ item.category|title }}</span></span>
      </li>
      {% endfor %}
    </ul>
  </div>

  <div class="arch-strip">
    <span class="arch-label">Archive</span>
    {% for d in archive_dates[:7] %}<a href="{{ d.url }}" class="arch-pill {% if loop.first %}active{% endif %}">{{ d.label }}</a>{% endfor %}
    {% if archive_count > 7 %}<a href="digests/index.html" class="arch-pill">+ {{ archive_count - 7 }} more →</a>{% endif %}
  </div>

  {% set ai_stories = stories | selectattr("category","equalto","ai") | list %}
  <div class="sec-block" data-category="ai">
    <div class="sec-head">
      <div class="sec-head-left">
        <span class="sec-title">AI News</span>
        <span class="sec-badge badge-ai">{{ ai_stories|length }} stories</span>
      </div>
      {% if ai_stories|length > 4 %}<button class="show-all" data-sec="ai">Show All {{ ai_stories|length }} →</button>{% endif %}
    </div>
    <div class="cards" id="cards-ai">
      {% for s in ai_stories %}
      <div class="card cai {% if s.is_hero %}hero{% endif %} {% if loop.index > 4 %}hidden{% endif %}"
           data-category="ai" data-title="{{ s.title }}" data-summary="{{ s.summary }}">
        {% if s.is_hero %}<div class="hero-lbl"><svg width="9" height="9" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg> Top Story</div>{% endif %}
        <div class="cmeta">
          <span class="spill {% if s.source_type=='youtube' %}syt{% else %}snl{% endif %}">{{ 'YouTube' if s.source_type=='youtube' else 'Newsletter' }}</span>
          <span class="cpill cpai">AI</span>
          <span style="font-size:12px;color:var(--text2)">{{ s.creator }}</span>
          {% if s.is_new %}<span class="nbadge"><span class="ndot"></span>New</span>{% endif %}
          <span class="rtime"><svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> {{ s.reading_time }}</span>
          <span class="ctime">{{ s.published_str }}</span>
        </div>
        <h3>{{ s.title }}</h3>
        <p>{{ s.summary }}</p>
        {% if s.tags %}<div class="ttags">{% for t in s.tags %}<span class="ttag">{{ t }}</span>{% endfor %}</div>{% endif %}
        <div class="cfoot">
          <div class="cfoot-l">
            <span class="csrc">{{ s.source_name }}</span>
            <a href="{{ s.url }}" target="_blank" rel="noopener noreferrer" class="cread">{{ 'Watch video' if s.source_type=='youtube' else 'Read article' }} <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg></a>
          </div>
          <button class="bmark" title="Save for later" onclick="toggleBookmark(this)"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg></button>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  {% set tour_stories = stories | selectattr("category","equalto","tourism") | list %}
  <div class="sec-block" data-category="tourism">
    <div class="sec-head">
      <div class="sec-head-left">
        <span class="sec-title">Tourism India</span>
        <span class="sec-badge badge-tour">{{ tour_stories|length }} updates</span>
        <div class="filt">
          <button class="fbtn ft" data-reg="gujarat" onclick="filterRegion(this)">Gujarat Only</button>
          <button class="fbtn" data-reg="all" onclick="filterRegion(this)">All India</button>
        </div>
      </div>
      {% if tour_stories|length > 4 %}<button class="show-all" data-sec="tourism">Show All {{ tour_stories|length }} →</button>{% endif %}
    </div>
    <div class="cards" id="cards-tourism">
      {% for s in tour_stories %}
      <div class="card ct {% if loop.index > 4 %}hidden{% endif %}"
           data-category="tourism" data-gujarat="{{ 'true' if s.gujarat else 'false' }}"
           data-title="{{ s.title }}" data-summary="{{ s.summary }}">
        <div class="cmeta">
          <span class="spill snl">Newsletter</span><span class="cpill cpt">Tourism</span>
          <span style="font-size:12px;color:var(--text2)">{{ s.creator }}</span>
          {% if s.is_new %}<span class="nbadge"><span class="ndot"></span>New</span>{% endif %}
          <span class="rtime"><svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> {{ s.reading_time }}</span>
          <span class="ctime">{{ s.published_str }}</span>
        </div>
        <h3>{{ s.title }}</h3><p>{{ s.summary }}</p>
        {% if s.tags %}<div class="ttags">{% for t in s.tags %}<span class="ttag">{{ t }}</span>{% endfor %}</div>{% endif %}
        <div class="cfoot">
          <div class="cfoot-l"><span class="csrc">{{ s.source_name }}</span><a href="{{ s.url }}" target="_blank" rel="noopener noreferrer" class="cread">Read article <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg></a></div>
          <button class="bmark" title="Save" onclick="toggleBookmark(this)"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg></button>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  {% set job_stories = stories | selectattr("category","equalto","jobs") | list %}
  <div class="sec-block" data-category="jobs">
    <div class="sec-head">
      <div class="sec-head-left">
        <span class="sec-title">Dubai Jobs</span>
        <span class="sec-badge badge-job">{{ job_stories|length }} new today</span>
        <div class="filt">
          <button class="fbtn" data-min="0" onclick="filterSalary(this)">Any</button>
          <button class="fbtn fj" data-min="15000" onclick="filterSalary(this)">&gt;15K AED</button>
          <button class="fbtn" data-min="20000" onclick="filterSalary(this)">&gt;20K AED</button>
          <button class="fbtn" data-min="25000" onclick="filterSalary(this)">&gt;25K AED</button>
        </div>
      </div>
      {% if job_stories|length > 4 %}<button class="show-all" data-sec="jobs">Show All {{ job_stories|length }} →</button>{% endif %}
    </div>
    <div class="cards" id="cards-jobs">
      {% for s in job_stories %}
      <div class="card cj {% if loop.index > 4 %}hidden{% endif %}"
           data-category="jobs" data-salary="{{ s.salary_min }}"
           data-title="{{ s.title }}" data-summary="{{ s.summary }}">
        <div class="cmeta">
          <span class="spill sjob">Job Post</span><span class="cpill cpj">Dubai</span>
          <span style="font-size:12px;color:var(--text2)">{{ s.creator }}</span>
          {% if s.is_new %}<span class="nbadge"><span class="ndot"></span>New</span>{% endif %}
          {% if s.match_level %}<span class="mbadge m{{ s.match_level[0] }}"><span style="font-size:12px;font-weight:800">{{ s.match_score_str }}</span> match</span>{% endif %}
          <span class="ctime">{{ s.published_str }}</span>
        </div>
        <h3>{{ s.title }}</h3><p>{{ s.summary }}</p>
        {% if s.tags %}<div class="ttags">{% for t in s.tags %}<span class="ttag">{{ t }}</span>{% endfor %}</div>{% endif %}
        <div class="cfoot">
          <div class="cfoot-l"><span class="csrc">{{ s.source_name }}</span><a href="{{ s.url }}" target="_blank" rel="noopener noreferrer" class="cread">View job <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg></a></div>
          <button class="bmark" title="Save" onclick="toggleBookmark(this)"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg></button>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</main>

<aside class="sidebar">
  <div class="sb"><div class="sbh"><span class="sbt">Today's Digest</span><span class="sblive">Live</span></div>
    <div class="sg">
      <div class="si"><div class="sn cn">{{ stats.ai }}</div><div class="sl">AI</div></div>
      <div class="si"><div class="sn ctn">{{ stats.tourism }}</div><div class="sl">Tourism</div></div>
      <div class="si"><div class="sn cjn">{{ stats.jobs }}</div><div class="sl">Jobs</div></div>
    </div>
  </div>
  <div class="sb"><div class="sbh"><span class="sbt">Trending Today</span></div>
    <ul class="tlist">
      {% for s in trending %}
      <li class="ti" onclick="window.open('{{ s.url }}','_blank')">
        <span class="tn">0{{ loop.index }}</span>
        <div><div class="tt">{{ s.title[:60] }}{% if s.title|length > 60 %}…{% endif %}</div>
        <div class="tm">{{ s.source_name }} · {{ s.category|title }}</div></div>
      </li>
      {% endfor %}
    </ul>
  </div>
  <div class="sb"><div class="sbh"><span class="sbt">Your Intelligence</span></div>
    <div class="ab">
      <p>Personalised for <strong>{{ profile.name }}</strong> — MSc Risk &amp; Finance. Updated daily at 9:00 AM IST.</p>
      <p style="margin-bottom:8px">Target: <strong style="color:var(--job)">{{ profile.sidebar_target }}</strong></p>
      <button class="fbtn2" onclick="window.location.href='sources.json'">View Sources (sources.json)</button>
    </div>
  </div>
</aside>
</div>

<script>
// Category tabs
document.querySelectorAll('.cat-tab').forEach(function(tab) {
  tab.addEventListener('click', function() {
    document.querySelectorAll('.cat-tab').forEach(function(t) {
      t.className = 'cat-tab';
    });
    var cat = this.dataset.cat;
    this.classList.add('active-' + (cat === 'tourism' ? 'tour' : cat === 'jobs' ? 'job' : cat));
    document.querySelectorAll('.sec-block').forEach(function(s) {
      s.style.display = (cat === 'all' || s.dataset.category === cat) ? '' : 'none';
    });
  });
});

// Show All per section
document.querySelectorAll('.show-all').forEach(function(btn) {
  btn.addEventListener('click', function() {
    var sec = this.dataset.sec;
    document.querySelectorAll('#cards-' + sec + ' .hidden').forEach(function(c) {
      c.classList.remove('hidden');
      c.style.display = '';
    });
    this.style.display = 'none';
  });
});

// Gujarat filter (safe DOM — no untrusted innerHTML)
function filterRegion(btn) {
  document.querySelectorAll('.filt .fbtn[data-reg]').forEach(function(b) { b.classList.remove('ft'); });
  btn.classList.add('ft');
  var gujaratOnly = btn.dataset.reg === 'gujarat';
  document.querySelectorAll('#cards-tourism .card').forEach(function(card) {
    card.style.display = (!gujaratOnly || card.dataset.gujarat === 'true') ? '' : 'none';
  });
}

// Salary filter
function filterSalary(btn) {
  document.querySelectorAll('.filt .fbtn[data-min]').forEach(function(b) { b.classList.remove('fj'); });
  btn.classList.add('fj');
  var min = parseInt(btn.dataset.min) || 0;
  document.querySelectorAll('#cards-jobs .card').forEach(function(card) {
    card.style.display = (parseInt(card.dataset.salary) || 0) >= min ? '' : 'none';
  });
}

// TL;DR collapse
function toggleTldr() {
  var list = document.getElementById('tlist');
  var tog = document.getElementById('ttog');
  var hidden = list.style.display === 'none';
  list.style.display = hidden ? '' : 'none';
  tog.textContent = hidden ? 'Collapse \u2191' : 'Expand \u2193';
}

// Search — safe DOM manipulation, no innerHTML with untrusted data
function clearHighlights() {
  document.querySelectorAll('mark.hl').forEach(function(m) {
    var text = document.createTextNode(m.textContent);
    m.parentNode.replaceChild(text, m);
  });
}

function highlightInElement(el, query) {
  if (!el) return;
  var text = el.textContent;
  var lower = text.toLowerCase();
  var qLower = query.toLowerCase();
  var idx = lower.indexOf(qLower);
  if (idx === -1) return;
  // Build new content with highlights using safe DOM nodes
  var frag = document.createDocumentFragment();
  var last = 0;
  while (idx !== -1) {
    frag.appendChild(document.createTextNode(text.slice(last, idx)));
    var mark = document.createElement('mark');
    mark.className = 'hl';
    mark.textContent = text.slice(idx, idx + query.length);
    frag.appendChild(mark);
    last = idx + query.length;
    idx = lower.indexOf(qLower, last);
  }
  frag.appendChild(document.createTextNode(text.slice(last)));
  while (el.firstChild) el.removeChild(el.firstChild);
  el.appendChild(frag);
}

document.getElementById('srch').addEventListener('input', function() {
  var q = this.value.trim();
  clearHighlights();
  if (!q) {
    document.querySelectorAll('.card').forEach(function(c) { c.style.display = ''; });
    return;
  }
  var qLower = q.toLowerCase();
  document.querySelectorAll('.card').forEach(function(card) {
    var title = (card.dataset.title || '').toLowerCase();
    var summary = (card.dataset.summary || '').toLowerCase();
    if (title.includes(qLower) || summary.includes(qLower)) {
      card.style.display = '';
      highlightInElement(card.querySelector('h3'), q);
      highlightInElement(card.querySelector('p'), q);
    } else {
      card.style.display = 'none';
    }
  });
});

// Bookmark toggle
function toggleBookmark(btn) {
  btn.classList.toggle('saved');
}
</script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add templates/page.html
git commit -m "feat: full Jinja2 HTML template with safe DOM search"
```

---

## Task 5: Archive Template (templates/archive.html)

**Files:**
- Create: `templates/archive.html`

- [ ] **Step 1: Create templates/archive.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Intelligence — Archive</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#F4F4F5;color:#09090B;-webkit-font-smoothing:antialiased}
.hdr{background:#09090B;padding:0 24px;border-bottom:1px solid #27272A}
.hdr-in{max-width:860px;margin:0 auto;display:flex;align-items:center;gap:16px;height:58px}
.logo{font-family:'Space Grotesk',sans-serif;font-size:19px;font-weight:800;color:#FFF;letter-spacing:-.03em}
.logo span{color:#D946EF}
.back{font-size:12px;color:#52525B;text-decoration:none;margin-left:auto}
.back:hover{color:#D946EF}
.content{max-width:860px;margin:0 auto;padding:32px 24px}
.pg-title{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800;letter-spacing:-.02em;margin-bottom:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.dc{background:#fff;border:1px solid #E4E4E7;border-radius:8px;padding:16px;text-decoration:none;color:inherit;transition:all .15s;display:block}
.dc:hover{border-color:#D946EF;box-shadow:0 2px 12px rgba(0,0,0,.07);transform:translateY(-1px)}
.dd{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;color:#09090B;margin-bottom:4px}
.dm{font-size:11px;color:#71717A}
.dm span{font-weight:600}
</style>
</head>
<body>
<div class="hdr"><div class="hdr-in">
  <div class="logo">The <span>Intelligence</span></div>
  <a href="../index.html" class="back">← Today's digest</a>
</div></div>
<div class="content">
  <h1 class="pg-title">Archive — {{ digests|length }} digests</h1>
  <div class="grid">
    {% for d in digests %}
    <a href="{{ d.filename }}" class="dc">
      <div class="dd">{{ d.label }}</div>
      <div class="dm"><span>{{ d.ai }}</span> AI · <span>{{ d.tourism }}</span> Tourism · <span>{{ d.jobs }}</span> Jobs</div>
    </a>
    {% endfor %}
  </div>
</div>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add templates/archive.html
git commit -m "feat: archive listing template"
```

---

## Task 6: Renderer (render.py)

**Files:**
- Create: `render.py`
- Create: `tests/test_render.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_render.py`:

```python
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
```

- [ ] **Step 2: Run to verify they fail**

```bash
python -m pytest tests/test_render.py -v
```

Expected: `ImportError: No module named 'render'`

- [ ] **Step 3: Create render.py**

```python
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"
DEFAULT_DOCS_DIR = Path(__file__).parent / "docs"


def _load_manifest(docs_dir: Path) -> list:
    p = docs_dir / "digests" / "manifest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def _save_manifest(manifest: list, docs_dir: Path) -> None:
    p = docs_dir / "digests" / "manifest.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")


def get_archive_dates(manifest: list) -> list:
    dates = []
    for entry in sorted(manifest, key=lambda x: x["date"], reverse=True):
        dt = datetime.strptime(entry["date"], "%Y-%m-%d")
        day = str(dt.day)
        label = dt.strftime(f"{day} %b")
        dates.append({
            "date": entry["date"],
            "label": label,
            "url": f"digests/{entry['date']}.html",
            "filename": f"{entry['date']}.html",
            "ai": entry.get("ai", 0),
            "tourism": entry.get("tourism", 0),
            "jobs": entry.get("jobs", 0),
        })
    return dates


def render_digest(stories: list, profile: dict, run_time: datetime,
                  archive_dates: list, docs_dir: str = None) -> None:
    docs_path = Path(docs_dir) if docs_dir else DEFAULT_DOCS_DIR
    docs_path.mkdir(parents=True, exist_ok=True)
    (docs_path / "digests").mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    page_tmpl = env.get_template("page.html")
    archive_tmpl = env.get_template("archive.html")

    date_str = run_time.strftime("%Y-%m-%d")
    day = str(run_time.day)
    date_display = run_time.strftime(f"{day} %B %Y · 9:00 AM IST")

    stats = {
        "ai": sum(1 for s in stories if s["category"] == "ai"),
        "tourism": sum(1 for s in stories if s["category"] == "tourism"),
        "jobs": sum(1 for s in stories if s["category"] == "jobs"),
        "total": len(stories),
    }

    from process import build_tldr
    tldr = build_tldr(stories, profile)
    trending = sorted(stories, key=lambda s: s["published"], reverse=True)[:5]

    ctx = {
        "date_display": date_display,
        "stories": stories,
        "tldr": tldr,
        "stats": stats,
        "archive_dates": archive_dates,
        "archive_count": len(archive_dates),
        "trending": trending,
        "profile": profile,
    }

    html = page_tmpl.render(**ctx)
    (docs_path / "index.html").write_text(html, encoding="utf-8")
    print(f"  [OK] docs/index.html")
    (docs_path / "digests" / f"{date_str}.html").write_text(html, encoding="utf-8")
    print(f"  [OK] docs/digests/{date_str}.html")

    manifest = _load_manifest(docs_path)
    manifest = [m for m in manifest if m["date"] != date_str]
    manifest.append({"date": date_str, "ai": stats["ai"],
                     "tourism": stats["tourism"], "jobs": stats["jobs"]})
    manifest.sort(key=lambda x: x["date"], reverse=True)
    _save_manifest(manifest, docs_path)

    all_dates = get_archive_dates(manifest)
    archive_html = archive_tmpl.render(digests=all_dates)
    (docs_path / "digests" / "index.html").write_text(archive_html, encoding="utf-8")
    print(f"  [OK] docs/digests/index.html ({len(manifest)} total)")
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_render.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add render.py tests/test_render.py
git commit -m "feat: renderer - writes digest HTML and archive manifest"
```

---

## Task 7: Main Orchestrator (fetch.py)

**Files:**
- Create: `fetch.py`

- [ ] **Step 1: Create fetch.py**

```python
#!/usr/bin/env python3
"""
The Intelligence — Daily digest generator.
Usage: python fetch.py
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from feeds import fetch_all_feeds
from process import process_entries
from render import render_digest, get_archive_dates, _load_manifest

ROOT = Path(__file__).parent


def main():
    print("=" * 50)
    print("The Intelligence — Daily Digest Generator")
    print("=" * 50)

    run_time = datetime.now(tz=timezone.utc)
    print(f"\nRun time (UTC): {run_time.strftime('%Y-%m-%d %H:%M')}")

    print("\n[1/4] Loading config...")
    with open(ROOT / "sources.json", encoding="utf-8") as f:
        sources = json.load(f)
    with open(ROOT / "profile.json", encoding="utf-8") as f:
        profile = json.load(f)
    print(f"  {len(sources)} sources in sources.json")

    print("\n[2/4] Fetching RSS feeds...")
    raw = fetch_all_feeds(sources)
    print(f"  {len(raw)} raw entries fetched")

    print("\n[3/4] Processing...")
    stories = process_entries(raw, profile, run_time)
    ai = sum(1 for s in stories if s["category"] == "ai")
    tour = sum(1 for s in stories if s["category"] == "tourism")
    jobs = sum(1 for s in stories if s["category"] == "jobs")
    print(f"  {len(stories)} stories after dedup  (AI:{ai}  Tourism:{tour}  Jobs:{jobs})")

    docs_dir = ROOT / "docs"
    manifest = _load_manifest(docs_dir)
    archive_dates = get_archive_dates(manifest)

    print("\n[4/4] Rendering HTML...")
    render_digest(stories, profile, run_time, archive_dates)

    print("\nDone. Open docs/index.html to preview.")
    print("=" * 50)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run locally**

```bash
cd D:\the-intelligence
python fetch.py
```

Expected: runs without errors, creates `docs/index.html`. Open it in your browser to verify it looks correct.

- [ ] **Step 3: Commit generated files**

```bash
git add fetch.py docs/
git commit -m "feat: main orchestrator + first generated digest"
```

---

## Task 8: GitHub Repository + Pages Setup

- [ ] **Step 1: Create GitHub repo**

Go to https://github.com/new:
- Name: `the-intelligence`
- Visibility: **Public** (required for free GitHub Pages)
- Do NOT initialise with README (you already have commits locally)

- [ ] **Step 2: Push to GitHub**

```bash
cd D:\the-intelligence
git remote add origin https://github.com/YOUR_USERNAME/the-intelligence.git
git branch -M main
git push -u origin main
```

- [ ] **Step 3: Enable GitHub Pages**

1. Go to repo → **Settings** → **Pages**
2. Source: Deploy from a branch
3. Branch: `main` / Folder: `/docs`
4. Save

Site will be live at `https://YOUR_USERNAME.github.io/the-intelligence/`

---

## Task 9: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/daily.yml`

- [ ] **Step 1: Create daily.yml**

```yaml
name: Daily Digest

on:
  schedule:
    - cron: '30 3 * * *'   # 9:00 AM IST (UTC+5:30 = UTC 03:30)
  workflow_dispatch:         # manual trigger from GitHub UI

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate digest
        run: python fetch.py

      - name: Commit and push
        run: |
          git config user.name "Intelligence Bot"
          git config user.email "bot@github.com"
          git add docs/
          git diff --staged --quiet || git commit -m "digest: $(date -u +'%Y-%m-%d')"
          git push
```

- [ ] **Step 2: Push workflow**

```bash
git add .github/workflows/daily.yml
git commit -m "ci: daily cron at 9am IST via GitHub Actions"
git push
```

- [ ] **Step 3: Trigger a manual test run**

1. Go to your repo → **Actions** tab
2. Select **Daily Digest**
3. Click **Run workflow** → **Run workflow**
4. Watch logs — should complete in < 60 seconds
5. Verify a new commit appears with `digest: YYYY-MM-DD`
6. Open `https://YOUR_USERNAME.github.io/the-intelligence/` in your browser

- [ ] **Step 4: Add real YouTube channel IDs**

For each YouTube creator in `sources.json`:
1. Open their channel page (e.g. `youtube.com/@nicksaraev`)
2. View page source (Ctrl+U in browser)
3. Search for `"channelId"` — copy the UC... value (~24 chars)
4. Update sources.json, replacing `REPLACE_WITH_CHANNEL_ID`

```bash
git add sources.json
git commit -m "config: real YouTube channel IDs"
git push
```

---

## Spec Coverage Check

| Spec requirement | Task |
|---|---|
| Parallel RSS fetching | Task 2 |
| Dedup by URL + title similarity | Task 3 |
| Job match scoring | Task 3 |
| Gujarat filter | Task 3 |
| NEW badge (< 3 hrs) | Task 3 |
| Topic tag extraction | Task 3 |
| Reading time | Task 3 |
| TL;DR (5 items, 1/category) | Task 3 |
| Full design system + HTML | Task 4 |
| Category tabs + JS filtering | Task 4 |
| Gujarat toggle | Task 4 |
| Salary filter | Task 4 |
| Safe search + highlight | Task 4 |
| Show All per section | Task 4 |
| Bookmark | Task 4 |
| Archive listing page | Task 5 |
| Renderer + manifest | Task 6 |
| Main entry point | Task 7 |
| GitHub Pages (24/7 online) | Task 8 |
| GitHub Actions 9am IST | Task 9 |
| sources.json easy add/remove | Task 1 |
| profile.json personalisation | Task 1 |
