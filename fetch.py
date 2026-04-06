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
