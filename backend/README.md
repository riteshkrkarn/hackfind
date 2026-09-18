# Hackfind Backend

Python FastAPI service: discovery agent, scrapers, filters, deadlines, and notifications.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --port 8002
```

Open docs at http://localhost:8002/docs

## Sources (pluggable)

You do **not** need a new Python file for every platform.

| Kind | When to use |
|---|---|
| Built-in adapters | Devpost, Devfolio, MLH, HackerEarth (tuned scrapers) |
| `html` | Any listing page — pass URL + CSS selectors |
| `json` | Any JSON API — map title/url fields |
| `tavily` | Web search discovery via [Tavily](https://tavily.com) (set `TAVILY_API_KEY`) |

### Add a platform via API

```http
POST /sources
{
  "name": "unstop",
  "kind": "html",
  "enabled": true,
  "config": {
    "list_url": "https://unstop.com/hackathons",
    "link_selector": "a[href*='hackathon']",
    "base_url": "https://unstop.com",
    "max_items": 30
  }
}
```

Or via Tavily:

```http
POST /sources
{
  "name": "tavily-india-hacks",
  "kind": "tavily",
  "enabled": true,
  "config": {
    "query": "upcoming hackathons India students apply",
    "max_results": 15,
    "include_domains": ["unstop.com", "devfolio.co", "devpost.com"]
  }
}
```

File-based option: copy `sources.example.json` → `sources.json` (path from `SOURCES_FILE`).

Built-ins are toggled with `ENABLED_BUILTIN_SOURCES`. Global Tavily (default query) turns on when `TAVILY_API_KEY` is set and `TAVILY_ENABLED=true`.

## Agent

- Cycle: fetch → dedupe → filter → upsert → notify → deadline reminders
- Scheduler: `AGENT_CRON_MINUTES` (default 60). Runs **once on startup**, then on that interval.
- Manual: `POST /agent/run`
- Status: `GET /agent/status` (next/last run, errors)

## API (no auth yet)

| Method | Path | Purpose |
|---|---|---|
| GET | `/hackathons` | List / filter hackathons |
| POST | `/hackathons/{id}/status` | Mark interested / joined / ignored |
| CRUD | `/filters` | Filter profiles |
| CRUD | `/notifications` | Channel config |
| CRUD | `/sources` | Generic / Tavily sources |
| POST | `/agent/run` | Trigger one agent cycle |
| GET | `/deadlines` | Upcoming deadlines |

Set `USE_SEED_SOURCE=true` for offline sample events.
