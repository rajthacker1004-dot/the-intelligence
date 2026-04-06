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
    return min(100, matches * 20)


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
