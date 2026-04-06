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
