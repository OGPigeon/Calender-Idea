"""PostgreSQL storage backend. Used when DATABASE_URL env var is set."""
import os
from typing import Any, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor


def _conn():
    """Open a new database connection."""
    return psycopg2.connect(os.environ["DATABASE_URL"])


def init_db() -> None:
    """Create the events table if it doesn't exist."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    date TEXT NOT NULL,
                    stime TEXT,
                    etime TEXT,
                    event TEXT NOT NULL,
                    solid BOOLEAN NOT NULL DEFAULT FALSE,
                    color TEXT DEFAULT 'blue',
                    allday BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)


def _load_with_ids() -> List[Dict[str, Any]]:
    """Load all events including internal database IDs."""
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, date, stime, etime, event, solid, color, allday FROM events")
            return [dict(r) for r in cur.fetchall()]


def load_events() -> List[Dict[str, Any]]:
    """Return all events without exposing database IDs."""
    return [{k: v for k, v in row.items() if k != "id"} for row in _load_with_ids()]


def create_event(date: str, stime: str, etime: str, event: str, solid: bool, color: str, allday: bool) -> None:
    """Insert a new event row."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (date, stime, etime, event, solid, color, allday) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (date, stime or None, etime or None, event, solid, color, allday),
            )


def edit_event(idx: int, ndate=None, nstime=None, netime=None, nevent=None, nsolid=None, ncolor=None, nallday=None) -> None:
    """Update the event at sorted index idx. Only non-None fields are changed."""
    rows = sorted(_load_with_ids(), key=lambda e: (e["date"], e.get("stime") or ""))
    target_id = rows[idx]["id"]

    updates: Dict[str, Any] = {}
    if ndate is not None:
        updates["date"] = ndate
    if nstime is not None:
        updates["stime"] = nstime
    if netime is not None:
        updates["etime"] = netime
    if nevent is not None:
        updates["event"] = nevent
    if nsolid is not None:
        updates["solid"] = nsolid
    if ncolor is not None:
        updates["color"] = ncolor
    if nallday is not None:
        updates["allday"] = nallday

    if not updates:
        return

    set_clause = ", ".join(f"{col} = %s" for col in updates)
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE events SET {set_clause} WHERE id = %s", [*updates.values(), target_id])


def delete_event(idx: int) -> None:
    """Delete the event at sorted index idx."""
    rows = sorted(_load_with_ids(), key=lambda e: (e["date"], e.get("stime") or ""))
    target_id = rows[idx]["id"]
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM events WHERE id = %s", (target_id,))
