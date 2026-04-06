# Design Spec: The Intelligence — AI Newsletter Platform

**Date:** 2026-04-06  
**Status:** Approved  
**Project root:** `D:\the-intelligence`  
**Stack:** Python + GitHub Actions + GitHub Pages  
**Delivery:** Daily at 9:00 AM IST — 24/7 online via GitHub Pages (no local machine needed)

---

## 1. What We're Building

A personalised daily digest web page that aggregates AI news, India tourism news, and Dubai job listings from RSS feeds (YouTube channels + newsletters/websites), deduplicates stories, and serves a static HTML page at 9:00 AM IST every day via GitHub Actions + GitHub Pages.

**Key guarantee:** The page is permanently online 24/7. GitHub Pages serves it even when your computer is off. Every past digest is archived at `/digests/YYYY-MM-DD.html` — if you miss Monday, you can still read Monday's digest on Tuesday.

**Name:** The Intelligence  
**Owner:** Raj Thacker  
**Target:** Personal use — career tracking, business awareness, job hunting

---

## 2. Three Categories (V1)

| Category | Purpose | Sources |
|---|---|---|
| **AI News** | Stay current for Dubai AI career | Nick Saraev (YouTube), Julian Goldie (YouTube), The Decoder, Import AI, HuggingFace Blog, TechCrunch AI |
| **Tourism India** | Monitor market for Rajal Tourism | Economic Times Travel, Travel Trends India, Times of India Travel — filtered to Gujarat-relevant stories by default |
| **Dubai Jobs** | Track roles for April 2027 target | Bayt.com RSS, Gulf News Jobs RSS, Khaleej Times Jobs RSS — filtered by keywords (AI, Risk, Finance, Data Analyst) |

---

## 3. Architecture

```
GitHub Actions (cron: 9:00 AM IST daily — runs on GitHub's servers, not your PC)
    │
    ▼
Python script (fetch.py)
    ├── Fetch RSS feeds for all 3 categories
    ├── Deduplicate by URL + title similarity
    ├── Score Dubai jobs against Raj's profile
    ├── Flag "NEW" items (published < 3 hours ago)
    ├── Extract topic tags from titles/content
    └── Generate today.html + index.html (archive)
    │
    ▼
GitHub Pages (static hosting, free, 24/7 online)
    └── Serves the-intelligence.github.io
```

**No paid APIs. No database. No server. No computer needs to be on.**  
Past digests are static HTML files committed to the repo (`/docs/digests/YYYY-MM-DD.html`).

---

## 4. Adding Sources (sources.json)

Any newsletter or YouTube creator can be added by editing `sources.json` — no code changes needed.

```json
[
  {
    "name": "Nick Saraev",
    "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxx",
    "category": "ai",
    "type": "youtube"
  },
  {
    "name": "The Decoder",
    "url": "https://the-decoder.com/feed/",
    "category": "ai",
    "type": "newsletter"
  },
  {
    "name": "Matt Wolfe",
    "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCyyyy",
    "category": "ai",
    "type": "youtube"
  }
]
```

**To add a new creator:** paste their YouTube channel RSS URL or newsletter RSS URL and set the category. The script picks it up on the next run. Any number of sources supported.

---

## 5. Python Script Responsibilities (`fetch.py`)

### 5.1 RSS Fetching
- Use `feedparser` library to pull all RSS feeds
- Each feed has a category tag (ai / tourism / jobs) and source type (youtube / newsletter / jobpost)
- YouTube channel RSS: `https://www.youtube.com/feeds/videos.xml?channel_id=<ID>`
- Run in parallel using `concurrent.futures.ThreadPoolExecutor`

### 5.2 Deduplication
- Primary: exact URL match — skip if already seen today
- Secondary: title similarity using `difflib.SequenceMatcher` — skip if ratio > 0.75 (same story from two sources)
- Keep the first fetched (source priority order defined in sources.json), discard the duplicate

### 5.3 Job Match Scoring
- Simple keyword scoring against Raj's profile:
  - Keywords: `MSc`, `Risk`, `Finance`, `Python`, `AI`, `Data Analyst`, `Streamlit`, `Machine Learning`, `Dubai`, `DIFC`
  - Each keyword match = +10 points, capped at 100%
  - Score shown as badge: ≥80% = green "94% match", 50–79% = orange "78% match"

### 5.4 Gujarat Filter
- Tourism stories tagged `gujarat` if title/summary contains: Kutch, Gandhidham, Bhuj, Rann, Gujarat, Ahmedabad, Surat, Rajkot, Vadodara
- Default view shows Gujarat-tagged only; "All India" toggle shows everything

### 5.5 NEW Badge Logic
- Story `published` timestamp within 3 hours of script run time → mark as `new: true`
- Rendered as pulsing fuchsia dot + "NEW" chip on the card

### 5.6 Topic Tag Extraction
- Simple keyword → hashtag map (no AI needed):
  - "gemini" → `#Gemini`, "openai" → `#OpenAI`, "agent" → `#Agents`, etc.
- Top 5 matching tags shown per card

### 5.7 Reading Time Estimation
- YouTube: extract video duration from RSS `<yt:duration>` field → "18 min video"
- Articles: count words in RSS `<description>` → divide by 200 → "4 min read"

### 5.8 TL;DR Generation
- Top 5 stories (1 per category minimum, ranked by recency + match score for jobs)
- Summary pulled from RSS `<description>` field, truncated to 1 sentence
- Personalised suffix per category:
  - AI → career relevance note
  - Tourism → Rajal Tourism business note
  - Jobs → action prompt ("apply today")

---

## 6. HTML Output Structure

### 6.1 Pages Generated Per Run
- `docs/index.html` — today's digest (overwritten daily)
- `docs/digests/YYYY-MM-DD.html` — permanent archive copy
- `docs/digests/index.html` — archive listing (all past dates)

### 6.2 Page Sections (top to bottom)
1. **Ticker bar** — dark, scrolling breaking headlines, "LIVE" fuchsia tag
2. **Sticky header** — logo, search input, date
3. **Category tabs** — All / AI News / Tourism India / Dubai Jobs with counts
4. **TL;DR box** — fuchsia left border, 5 bullets, collapsible
5. **Archive strip** — last 7 days + "N more" link
6. **AI News section** — hero card (top story) + standard cards
7. **Tourism India section** — Gujarat/All India toggle + cards
8. **Dubai Jobs section** — salary filter buttons + cards
9. **Sidebar** — Today's stats, Trending Today (top 5), Your Intelligence block

### 6.3 Card Anatomy
- Source pill (YouTube / Newsletter / Job Post)
- Category pill (AI / Tourism / Dubai)
- Creator name · NEW badge (if < 3 hrs) · Match score (jobs only) · Reading time · Timestamp
- Headline (Space Grotesk, bold)
- 2-line summary
- Topic tags (#Gemini #Agents etc.)
- Footer: source name + "Read →" link + bookmark icon

---

## 7. Design System

| Token | Value |
|---|---|
| Background | `#FFFFFF` |
| Secondary bg | `#F4F4F5` |
| Header | `#09090B` |
| Accent (fuchsia) | `#D946EF` |
| Text primary | `#09090B` |
| Text secondary | `#71717A` |
| AI blue | `#2563EB` |
| Tourism green | `#16A34A` |
| Jobs orange | `#EA580C` |
| Border radius | `4px` (sharp, editorial) |
| Heading font | Space Grotesk (Google Fonts) |
| Body font | Inter (Google Fonts) |

---

## 8. Search

- Client-side JavaScript only (no backend)
- On keypress: hide cards whose title + summary don't match the query
- Highlight matching keywords in yellow across all visible cards
- Search works within the loaded digest page (today or any archive date)

---

## 9. Scheduling

- **GitHub Actions** cron: `30 3 * * *` (UTC) = 9:00 AM IST
- Runs on GitHub's servers — your PC does not need to be on
- Script generates HTML, commits to `docs/` folder, GitHub Pages serves it instantly
- Total runtime: < 60 seconds

---

## 10. Free Tier Constraints & Limits

| Resource | Limit | Our usage |
|---|---|---|
| GitHub Actions minutes | 2,000/month free | ~30 min/month (1 min/day × 30) |
| GitHub Pages bandwidth | 100 GB/month | Negligible for static HTML |
| RSS feeds | Free, no API key | All sources support RSS |
| YouTube RSS | Free, no API key | `youtube.com/feeds/videos.xml` |
| Bayt.com / Gulf News Jobs | RSS available | Public job search RSS, no API key needed |

**Zero paid APIs. Zero ongoing cost.**

---

## 11. File Structure

```
the-intelligence/
├── fetch.py                  # Main script: fetch → dedupe → generate HTML
├── sources.json              # RSS feed list — add new sources here, no code changes needed
├── profile.json              # Raj's profile for job scoring + personalisation
├── templates/
│   ├── page.html             # Jinja2 template for daily digest
│   └── archive.html          # Archive index template
├── docs/                     # GitHub Pages root
│   ├── index.html            # Today's digest (overwritten daily)
│   └── digests/
│       ├── index.html        # Archive listing
│       └── YYYY-MM-DD.html   # Past digests (permanent)
├── .github/
│   └── workflows/
│       └── daily.yml         # GitHub Actions cron job
└── requirements.txt          # feedparser, jinja2, python-dateutil
```

---

## 12. Out of Scope (V1)

- Dark mode toggle
- Email delivery
- User accounts / login
- Mobile app
- Push notifications
- AI-generated summaries (V1 uses RSS descriptions as-is)
- Multi-country job search
- Auto job application

---

## 13. V2 — Smart Job Application Engine

A dedicated section built on top of V1's job feed. Designed for multi-country job hunting with automated cover letters and one-click apply.

### 13.1 What It Does
- **Multi-country search:** Configure target countries (e.g. Dubai, Singapore, Netherlands) — each with its own job RSS feeds and country-specific job boards
- **Resume-based matching:** Full CV and experience stored in `profile.json` — every job scored against it
- **Auto cover letter:** Each job opening gets a unique cover letter generated using Claude API, tailored to the job title, company, and required skills
- **One-click apply:** "Apply" button on each card opens the application with the cover letter pre-filled
- **Auto-apply conditions (V2.1):** Set rules (title must contain X, salary > Y AED, location = DIFC) — matching jobs get applied to automatically without any clicks

### 13.2 Profile Data (profile.json — extended)
```json
{
  "name": "Raj Thacker",
  "target_salary_min": 18000,
  "target_countries": ["Dubai", "Singapore", "Netherlands"],
  "education": "MSc Risk & Finance with Distinction, University of Southampton (2025)",
  "skills": ["Python", "pandas", "scikit-learn", "Streamlit", "Risk Modelling", "Financial Analysis"],
  "experience": [...],
  "cv_text": "full CV text for cover letter generation"
}
```

### 13.3 Cover Letter Generation
- Uses Claude API (`claude-haiku-4-5` for cost efficiency — ~$0.001 per letter)
- Prompt: job title + company + required skills + Raj's CV → 3-paragraph personalised cover letter
- Stored locally so the same job doesn't regenerate a letter on next run

### 13.4 Auto-Apply Conditions (V2.1)
```json
{
  "auto_apply_rules": [
    { "title_contains": ["AI", "Risk", "Finance", "Data"], "salary_min_aed": 18000, "location_contains": ["Dubai", "DIFC"] }
  ]
}
```
Jobs matching all conditions are applied to automatically on the daily run. A log entry is added to an `applied.json` file.

### 13.5 New Job Sources for V2
| Country | Source |
|---|---|
| Dubai | Bayt.com, Gulf News Jobs, Khaleej Times, LinkedIn (if RSS restored), GulfTalent |
| Singapore | JobStreet, MyCareersFuture (government RSS), Indeed Singapore |
| Netherlands | Indeed NL, LinkedIn NL, Nationale Vacaturebank |
