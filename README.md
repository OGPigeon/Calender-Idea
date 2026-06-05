# Calendar App

**Live site:** https://joseph1209.app

A personal calendar application with a React frontend and a Python/Flask backend. Requires a Clerk account to sign in. Events are stored in PostgreSQL (cloud) or a local JSON file (dev).

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
- **PWA:** Installable on desktop and mobile
- **Authentication:** Clerk sign-in gates the app; each user's events are stored separately

## Deployment

| Layer    | Platform                                        |
|----------|-------------------------------------------------|
| Frontend | Vercel — `joseph1209.app`                       |
| Backend  | Render — `calendar-api-epdq.onrender.com`       |
| Auth     | Clerk — `clerk.joseph1209.app`                  |
| Database | Render PostgreSQL                               |

## Tech Stack

| Layer    | Technology                                              |
|----------|---------------------------------------------------------|
| Frontend | React 19, Vite, Clerk, date-fns, Axios, vite-plugin-pwa |
| Backend  | Python 3, Flask, Flask-CORS, PyJWT                      |
| Storage  | PostgreSQL (cloud) or `Data/events.json` (local dev)    |

## Project Structure

```
.
├── Data/
│   └── events.json           # Fallback event storage (local dev only)
├── Src/
│   ├── api.py                # Flask REST API
│   ├── auth.py               # Clerk JWT verification
│   ├── db.py                 # PostgreSQL backend (used when DATABASE_URL is set)
│   ├── Event.py              # Event model — CRUD, auto-switches between DB and JSON
│   ├── System.py             # Business logic — solid/overlap checks
│   ├── sync.py               # Git pull/push logic for JSON-file sync
│   └── Main.py               # CLI entry point
├── frontend/
│   └── src/
│       ├── App.jsx           # Root component, state, view switching
│       ├── api.js            # Axios calls to the Flask API
│       ├── main.jsx          # ClerkProvider setup
│       └── components/       # DayView, WeekView, MonthView, YearView, EventModal, …
├── Tests/
│   └── test_system_event.py  # Pytest suite
├── render.yaml               # Render deployment config
└── requirements.txt
```

## Getting Started (local dev)

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Clerk](https://clerk.com) account with an application created

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

**Backend** — create `Src/.env` (or set in your shell):

```
# Leave unset to skip auth in local dev (all requests treated as user "local")
CLERK_JWKS_URL=

# Leave unset to use Data/events.json instead of Postgres
DATABASE_URL=
```

**Frontend** — create `frontend/.env.local`:

```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...   # from Clerk dashboard → API Keys
VITE_API_URL=                            # leave empty; Vite proxies /api to localhost:5001
```

### 3. Start the backend

```bash
python Src/api.py
```

The API runs on `http://localhost:5001`.

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies `/api` calls to port 5001.

> **Auth in dev:** if `CLERK_JWKS_URL` is not set, the backend accepts all requests without a token and assigns them to the `"local"` user. You can skip Clerk setup entirely for local development.

## Deploying

### Backend (Render)

The `render.yaml` defines the service. Set these environment variables in the Render dashboard:

| Variable         | Value                                                         |
|------------------|---------------------------------------------------------------|
| `DATABASE_URL`   | Internal URL from your Render PostgreSQL instance             |
| `CLERK_JWKS_URL` | JWKS endpoint from Clerk dashboard (e.g. `https://clerk.yourdomain.com/.well-known/jwks.json`) |
| `ALLOWED_ORIGINS`| Your frontend domain (e.g. `https://yourdomain.com`)         |

### Frontend (Vercel)

Set these environment variables in the Vercel dashboard before deploying:

| Variable                    | Value                                       |
|-----------------------------|---------------------------------------------|
| `VITE_CLERK_PUBLISHABLE_KEY`| `pk_live_...` from Clerk dashboard          |
| `VITE_API_URL`              | `https://your-render-service.onrender.com`  |

Set the **Root Directory** to `frontend` and the **Output Directory** to `dist`.

### Clerk custom domain

To use a custom domain with Clerk, add the following DNS records to your domain:

| Name              | Type  | Value                                 |
|-------------------|-------|---------------------------------------|
| `accounts`        | CNAME | `accounts.clerk.services`             |
| `clerk`           | CNAME | `frontend-api.clerk.services`         |
| `clk._domainkey`  | CNAME | `dkim1.<your-instance>.clerk.services`|
| `clk2._domainkey` | CNAME | `dkim2.<your-instance>.clerk.services`|
| `clkmail`         | CNAME | `mail.<your-instance>.clerk.services` |

The exact values are provided in Clerk dashboard → Domains → DNS Records.

## Storage backends

The backend automatically selects a storage layer based on environment variables.

### PostgreSQL (recommended for production)

When `DATABASE_URL` is set, `db.py` stores all events in a Postgres table. Each user's events are isolated by their Clerk user ID. The table is created automatically on first request.

### JSON file (local dev)

Without `DATABASE_URL`, events are stored in `Data/events.json`. All requests share the same file regardless of user. This is suitable for local development only — Render's filesystem is ephemeral and writes will not survive a redeploy.

The toolbar `↓` / `↑` buttons can pull and push this file to a GitHub repository as a manual sync mechanism.

## API Reference

All endpoints require a valid Clerk JWT in the `Authorization: Bearer <token>` header. If `CLERK_JWKS_URL` is not set (dev mode), the header is optional.

| Method | Endpoint                          | Description                              |
|--------|-----------------------------------|------------------------------------------|
| GET    | `/api/health`                     | Diagnostic info — env vars, DB status    |
| GET    | `/api/events`                     | Return all events for the current user   |
| POST   | `/api/events`                     | Create a new event                       |
| PUT    | `/api/events/<idx>`               | Update an event by its sorted index      |
| DELETE | `/api/events/<idx>`               | Delete an event by its sorted index      |
| GET    | `/api/check-solid?date=`          | Check if a locked event exists on a date |
| GET    | `/api/check-overlap?date=&stime=` | Check for a time conflict                |
| POST   | `/api/sync/pull`                  | Pull latest events.json from GitHub      |
| POST   | `/api/sync/push`                  | Commit and push events.json to GitHub    |

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
