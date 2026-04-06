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
