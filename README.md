# Calendar App

**Live site:** https://calender-idea-jrljktnbh-ogpigeons-projects.vercel.app/

A personal calendar application with a React frontend and a Python/Flask backend. Supports two methods for keeping data in sync across devices: a PostgreSQL database (cloud) or a GitHub-backed JSON file (local).

## Features

- **Four calendar views:** Day, Week, Month, and Year
- **Event management:** Create, edit, and delete events via a modal form
- **Color-coded events:** Assign a color to each event
- **All-day events:** Mark events as all-day or give them a start/end time
- **Locked events:** Mark an event as "solid" to prevent other events from being created on the same date
- **Overlap detection:** Warns when a new event's start time conflicts with an existing one
- **Event search:** Filter events by keyword from the toolbar
- **Mini calendar sidebar:** Click any date to jump directly to it
- **Dark mode:** Toggle with the moon/sun icon; preference is saved across sessions
- **Keyboard shortcuts:** `←` / `→` to navigate, `T` to jump to today
- **GitHub sync:** Push and pull `Data/events.json` to/from a GitHub repo so your data is always up to date across devices

## Deployment

| Layer    | Platform                                            |
|----------|-----------------------------------------------------|
| Frontend | [Vercel](https://calender-idea-git-main-ogpigeons-projects.vercel.app)         |
| Backend  | [Render](https://render.com) (see `render.yaml`)    |

## Tech Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | React 19, Vite, date-fns, Axios                 |
| Backend  | Python 3, Flask, Flask-CORS                     |
| Storage  | PostgreSQL (cloud) or `Data/events.json` (local)|

## Project Structure

```
.
├── Data/
│   └── events.json          # Event storage (synced via GitHub)
├── Src/
│   ├── Event.py             # Event model — CRUD, auto-switches between DB and JSON
│   ├── System.py            # Business logic — solid/overlap checks
│   ├── db.py                # PostgreSQL backend (used when DATABASE_URL is set)
│   ├── sync.py              # Git pull/push logic for JSON-file sync
│   ├── api.py               # Flask REST API
│   └── Main.py              # CLI entry point
├── frontend/
│   └── src/
│       ├── App.jsx           # Root component, state, routing between views
│       ├── api.js            # Axios calls to the Flask API
│       └── components/       # DayView, WeekView, MonthView, YearView, EventModal, …
├── Tests/
│   └── test_system_event.py  # Pytest test suite
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- git (required for cross-device sync)

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the backend

```bash
python Src/api.py
```

The API runs on `http://localhost:5001`.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies API calls to port 5001.

## Data Sync

The app supports two storage backends. It automatically picks the right one based on whether `DATABASE_URL` is set.

### Method 1 — PostgreSQL (cloud / recommended for hosted use)

When the `DATABASE_URL` environment variable is present (set automatically by Render), `db.py` takes over as the storage layer. Events are stored in a Postgres table and are instantly consistent — no manual sync required.

**Setup on Render:** add a Postgres database to your Render service and the `DATABASE_URL` env var is set for you.

### Method 2 — GitHub file sync (local / self-hosted)

Without `DATABASE_URL`, events live in `Data/events.json` and can be synced to a private GitHub repository via `sync.py`.

**First-time setup:**

```bash
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

**Syncing:** use the `↓` and `↑` buttons in the toolbar:

| Button | Action |
|--------|--------|
| `↓` | **Pull** — fetches the latest `events.json` from GitHub and refreshes the calendar |
| `↑` | **Push** — commits the current `events.json` with a timestamp and pushes to GitHub |

On a new device, clone the repo, run the app, and hit `↓` to get the latest data.

> **Note:** Requires git credentials (SSH key or stored HTTPS token). If push fails, verify your remote is set up and you have write access.

## API Reference

| Method | Endpoint                          | Description                              |
|--------|-----------------------------------|------------------------------------------|
| GET    | `/api/events`                     | Return all events, sorted by date/time   |
| POST   | `/api/events`                     | Create a new event                       |
| PUT    | `/api/events/<idx>`               | Update an event by its sorted index      |
| DELETE | `/api/events/<idx>`               | Delete an event by its sorted index      |
| GET    | `/api/check-solid?date=`          | Check if a locked event exists on a date |
| GET    | `/api/check-overlap?date=&stime=` | Check for a time conflict                |
| POST   | `/api/sync/pull`                  | Pull latest events from GitHub           |
| POST   | `/api/sync/push`                  | Commit and push events to GitHub         |

### Event schema

```json
{
  "date":   "2026-06-15",
  "stime":  "09:00",
  "etime":  "10:00",
  "event":  "Team standup",
  "solid":  false,
  "color":  "blue",
  "allday": false
}
```

`solid: true` locks the date — no other events can be added to it.

## Running Tests

```bash
pytest Tests/
```
