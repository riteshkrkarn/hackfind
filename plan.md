# Hackathon agent - plan

## Overview

A personal agent that discovers new hackathons on a schedule, filters them against your saved preferences, notifies you across your chosen channels, and lets you track deadlines for hackathons you've joined or bookmarked - all manageable through a web dashboard.

---

## Core goals

- Automatically discover new hackathons from multiple platforms
- Apply saved filters so only relevant ones reach you
- Never notify you twice about the same hackathon
- Track deadlines for hackathons you're interested in or have joined
- Send reminders at configurable thresholds (7 days, 1 day, day-of)
- Provide a dashboard to browse, manage, and configure everything
- Be extensible - new sources, channels, and filter types should require minimal changes

---

## Architecture

### Layer 1 - Data sources

External platforms, each wrapped in its own adapter class.

- Devpost
- Devfolio
- MLH
- HackerEarth
- Custom feeds (pluggable)

Each adapter implements a common interface and returns a normalized `Hackathon` object. The rest of the system never knows which platform data came from.

---

### Layer 2 - Core agent

Runs on a configurable cron schedule. Orchestrates all logic.

**Scheduler**
- Triggers the agent run at set intervals
- Hosted on Railway (persistent process) or GitHub Actions (zero-infra cron)

**Scraper / fetcher**
- Calls each platform adapter
- Uses `requests` + `BeautifulSoup` for static HTML pages
- Uses `Playwright` for JS-heavy pages
- Normalizes output into the shared `Hackathon` schema

**Filter engine**
- Loads the user's saved filter profile from the DB
- Scores and filters incoming hackathons against it
- Filter types: tech stack, remote/in-person, prize range, team size, domain (AI, Web3, HealthTech, etc.)
- Pluggable rule system - new filter types don't require rewriting core logic

**Deduplication service**
- Maintains a hash-set of every seen hackathon ID in the DB
- Only new hackathons pass through to notifications
- Prevents re-alerting on the same event across runs

**Deadline tracker**
- Watches the user's joined/interested list
- Emits reminder events at configured thresholds (e.g. 7 days, 1 day, day-of)
- Runs as part of every agent cycle

**Internal event bus**
- Decouples agent logic from notification dispatch
- Can be a simple in-process event emitter (Python `EventEmitter`) to start
- Upgrade path: BullMQ or Redis pub/sub if needed later

---

### Layer 3a - Storage

Single source of truth for all state.

**Hackathons DB**
- All discovered hackathons
- Seen hash-set for deduplication
- Status per hackathon (new, interested, joined, ignored)

**User state DB**
- Saved filter profiles
- Bookmarks and deadline entries
- Notification channel config and credentials

**Strategy:**
- SQLite for local development (zero setup, single file)
- Supabase / Postgres for production (remote access, dashboard reads)

---

### Layer 3b - Notification layer

Pluggable delivery channels. Each is a separate adapter that the event bus dispatches to.

| Channel | Implementation |
|---|---|
| Email | SendGrid or AWS SES |
| Telegram | Telegram Bot API |
| Slack | Incoming webhook |
| Custom | Drop in a new adapter class |

Channel credentials and reminder thresholds are configured via the REST API (not hardcoded in env files), so they can be updated from the dashboard.

---

### Layer 4 - REST API

The single controlled gateway between the dashboard (and any future client) and the storage + notification layers.

- Framework: **FastAPI** (Python - shares models and DB access with the agent)
- Auth: JWT from day one, even for personal use
- Exposes:
  - `GET /hackathons` - paginated, filterable list
  - `POST /hackathons/:id/status` - mark as interested / joined / ignored
  - `CRUD /filters` - manage filter profiles
  - `CRUD /notifications` - manage channel config
  - `POST /agent/run` - manual trigger endpoint
  - `GET /deadlines` - upcoming deadlines with countdown

The core agent and REST API both write to the same DB but independently - the agent handles discovery writes, the API handles user-driven writes.

---

### Layer 5 - UI dashboard

A web frontend that talks exclusively to the REST API.

- Framework: **Next.js** (App Router) + **Tailwind CSS**
- Hosted on **Vercel**

**Four main views:**

| View | Purpose |
|---|---|
| Discover | Browse matched hackathons, apply/adjust filters, mark interest |
| My list | Joined and interested hackathons with deadline countdowns |
| Filters | Create, edit, and toggle saved filter profiles |
| Settings | Configure notification channels and agent schedule |

---

## Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Agent language | Python 3.11+ | Shares models with the API |
| Scraping (static) | `requests` + `BeautifulSoup4` | Most platforms |
| Scraping (dynamic) | `Playwright` | JS-heavy pages |
| Scheduling | `APScheduler` or Railway cron | Persistent process preferred |
| REST API | FastAPI | Auto-generates OpenAPI docs |
| ORM / DB access | SQLModel or SQLAlchemy | Works with both SQLite and Postgres |
| Database (dev) | SQLite | Zero setup |
| Database (prod) | Supabase / Postgres | Remote, dashboard-accessible |
| UI framework | Next.js (App Router) | |
| UI styling | Tailwind CSS | |
| UI hosting | Vercel | |
| Agent + API hosting | Railway | Single service, persistent |
| Email notifications | SendGrid | Free tier sufficient to start |
| Telegram notifications | Telegram Bot API | Snappiest channel |
| Slack notifications | Incoming webhooks | |
| Auth | JWT (PyJWT) | API-level, not per-user |

---

## Key architectural principles

- **Adapter pattern** for all data sources and notification channels - extend without touching core logic
- **Event-driven core** - agent emits events, notification layer listens - fully decoupled and testable
- **Schema-first** - one normalized `Hackathon` type flows through every layer
- **Config-driven filters** - update preferences via API/dashboard, no code changes needed
- **Single API gateway** - dashboard, CLI, and any future client all hit the same REST API; no direct DB access from the frontend
- **Independent writers** - agent writes discovery data, API writes user state; same DB, no conflicts

---

## Upgrade paths (future)

- Add a mobile app - it's just another REST API client
- Add AI-based relevance scoring - slot it into the filter engine as a new rule
- Add more platforms - implement the adapter interface and register it
- Add team features - multi-user auth layer on top of the API
- Scale the event bus - swap in-process emitter for Redis pub/sub if volume grows