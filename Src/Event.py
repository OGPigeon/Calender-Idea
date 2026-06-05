"""Utilities to load event data from the top-level `Data/` folder.
Expected JSON: a file containing either a list of event objects or a single
object. Each event will be normalized to a dict with keys:
  - `date` (str)
  - `event` (str)
  - `solid` (bool)  # locked/mandatory event

This module exposes `get_events(data_folder=None)` which returns a list of
normalized event dicts.
"""
from datetime import datetime
from typing import Any, Dict, List
import os
import json

_DATA_FOLDER = os.path.join(os.path.dirname(__file__), "..", "Data")
_db_initialized = False


def _get_data_folder() -> str:
    """Return the data folder path from env or default."""
    return os.environ.get("DATA_FOLDER", _DATA_FOLDER)


def _use_db() -> bool:
    """Return True when DATABASE_URL is set, initialising the table on first call."""
    global _db_initialized
    if os.environ.get("DATABASE_URL"):
        if not _db_initialized:
            import db
            db.init_db()
            _db_initialized = True
        return True
    return False


class Events:
    """A collection of events, loaded from a JSON file or database."""

    def __init__(self, date: str, stime: str, etime: str, event: str, solid: bool, user_id: str = "local"):
        self.stime = datetime.strptime(stime, "%H:%M") if stime else None
        self.etime = datetime.strptime(etime, "%H:%M") if etime else None
        self.date = datetime.strptime(
            date, "%Y-%m-%d").date().isoformat() if date else None
        self.event = event
        self.solid = solid
        self.user_id = user_id

    def __str__(self):
        "returns event details in a readable format"
        return f"{self.date} - from {self.stime} to {self.etime} — {self.event} {'[LOCKED]' if self.solid else ''}"

    def _create_event(self, color: str = "blue", allday: bool = False) -> None:
        """Save this event to the database or JSON file."""
        stime_str = self.stime.strftime("%H:%M") if self.stime else None
        etime_str = self.etime.strftime("%H:%M") if self.etime else None
        if _use_db():
            import db
            db.create_event(self.user_id, self.date, stime_str, etime_str, self.event, self.solid, color, allday)
            return
        file_path = os.path.join(_get_data_folder(), "events.json")
        new_event = {
            "date": self.date,
            "stime": stime_str,
            "etime": etime_str,
            "event": self.event,
            "solid": self.solid,
            "color": color,
            "allday": allday,
        }
        data = self._load_events() if os.path.exists(file_path) else []
        data.append(new_event)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _delete_event(self, index: int) -> None:
        """Delete the event at the given sorted index."""
        if _use_db():
            import db
            db.delete_event(self.user_id, index)
            return
        file_path = os.path.join(_get_data_folder(), "events.json")
        data = self._load_events()
        sorted_data = sorted(data, key=lambda e: (e["date"], e.get("stime") or ""))
        target = sorted_data[index]
        data = [evt for evt in data if evt != target]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_events(self) -> List[Dict[str, Any]]:
        """Load and normalize events from the database or JSON file."""
        if _use_db():
            import db
            return db.load_events(self.user_id)
        file_path = os.path.join(_get_data_folder(), "events.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        return [
            {
                "date": event.get("date", ""),
                "stime": event.get("stime"),
                "etime": event.get("etime"),
                "event": event.get("event", ""),
                "solid": event.get("solid", False),
                "allday": event.get("allday", False),
                "color": event.get("color"),
            }
            for event in data
        ]

    def _edit_event(self, index: int, ndate=None, nstime=None, netime=None, nevent=None, nsolid=None, ncolor=None, nallday=None) -> None:
        """Edit the event at the given sorted index. Only non-None fields are updated."""
        if _use_db():
            import db
            db.edit_event(self.user_id, index, ndate=ndate, nstime=nstime, netime=netime, nevent=nevent, nsolid=nsolid, ncolor=ncolor, nallday=nallday)
            return
        file_path = os.path.join(_get_data_folder(), "events.json")
        data = self._load_events()
        sorted_data = sorted(data, key=lambda e: (e["date"], e.get("stime") or ""))
        target = sorted_data[index]
        for i, evt in enumerate(data):
            if evt == target:
                if ndate is not None:
                    data[i]["date"] = ndate
                if nstime is not None:
                    data[i]["stime"] = nstime
                if netime is not None:
                    data[i]["etime"] = netime
                if nevent is not None:
                    data[i]["event"] = nevent
                if nsolid is not None:
                    data[i]["solid"] = nsolid
                if ncolor is not None:
                    data[i]["color"] = ncolor
                if nallday is not None:
                    data[i]["allday"] = nallday
                break
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_event(self, date: datetime, stime: datetime, etime: datetime) -> Dict[str, Any]:
        """Return event info for the given date, or raise ValueError if not found."""
        events = self._load_events()
        for evt in events:
            if evt["date"] == date and evt["stime"] == stime and evt["etime"] == etime:
                return {"event": evt["event"], "solid": evt["solid"]}
        raise ValueError(f"No event found for date: {date}")
