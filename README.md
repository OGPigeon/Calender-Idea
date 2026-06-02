# Calendar App

A personal calendar application with a React frontend and a Python/Flask backend. Events are stored locally in a JSON file.

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

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Frontend | React 19, Vite, date-fns, Axios     |
| Backend  | Python 3, Flask, Flask-CORS         |
| Storage  | `Data/events.json` (flat JSON file) |

## Project Structure

```
.
├── Data/
│   └── events.json          # Event storage
├── Src/
│   ├── Event.py             # Event model — CRUD operations on the JSON file
│   ├── System.py            # Business logic — solid/overlap checks
│   ├── api.py               # Flask REST API
│   └── Main.py              # CLI entry point
├── frontend/
│   └── src/
│       ├── App.jsx           # Root component, state, routing between views
│       ├── api.js            # Axios calls to the Flask API
│       └── components/       # DayView, WeekView, MonthView, YearView, EventModal, …
└── Tests/
    └── test_system_event.py  # Pytest test suite
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend

```bash
pip install flask flask-cors
python Src/api.py
```

The API runs on `http://localhost:5001`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies API calls to port 5001.

## API Reference

| Method | Endpoint                  | Description                              |
|--------|---------------------------|------------------------------------------|
| GET    | `/api/events`             | Return all events, sorted by date/time   |
| POST   | `/api/events`             | Create a new event                       |
| PUT    | `/api/events/<idx>`       | Update an event by its sorted index      |
| DELETE | `/api/events/<idx>`       | Delete an event by its sorted index      |
| GET    | `/api/check-solid?date=`  | Check if a locked event exists on a date |
| GET    | `/api/check-overlap?date=&stime=` | Check for a time conflict       |

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
