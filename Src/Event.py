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


def _get_data_folder() -> str:
    return os.environ.get("DATA_FOLDER", _DATA_FOLDER)


class Events:
    """A collection of events, loaded from a JSON file."""

    def __init__(self, date: str, stime: str, etime: str, event: str, solid: bool):
        self.stime = datetime.strptime(stime, "%H:%M") if stime else None
        self.etime = datetime.strptime(etime, "%H:%M") if etime else None
        self.date = datetime.strptime(
            date, "%Y-%m-%d").date().isoformat() if date else None
        self.event = event
        self.solid = solid

    def __str__(self):
        "returns event details in a readable format"
        return f"{self.date} - from {self.stime} to {self.etime} — {self.event} {'[LOCKED]' if self.solid else ''}"

    def _create_event(self) -> None:
        """Create a dict representation of the event."""
        file_path = os.path.join(_get_data_folder(), "events.json")
        new_event = {
            "date": self.date,
            "stime": self.stime.strftime("%H:%M") if self.stime else None,
            "etime": self.etime.strftime("%H:%M") if self.etime else None,
            "event": self.event,
            "solid": self.solid
        }
        if os.path.exists(file_path):
            data = self._load_events()
        else:
            data = []
        data.append(new_event)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _delete_event(self, index: int):
        "Deletes the event at the given index in the sorted events list."
        file_path = os.path.join(_get_data_folder(), "events.json")
        data = self._load_events()
        sorted_data = sorted(data, key=lambda e: e["date"])
        target = sorted_data[index]
        data = [evt for evt in data if evt != target]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_events(self) -> List[Dict[str, Any]]:
        """Load and normalize events from the JSON file."""
        file_path = os.path.join(_get_data_folder(), "events.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Normalize to a list of event dicts
        if isinstance(data, dict):
            data = [data]  # Wrap single object in a list
        normalized_events = []
        for event in data:
            normalized_events.append({
                "date": event.get("date", ""),
                "stime": event.get("stime", None),
                "etime": event.get("etime", None),
                "event": event.get("event", ""),
                "solid": event.get("solid", False)
            })
        return normalized_events

    def _edit_event(self, index: int, ndate: str = "", nstime: str = "", netime: str = "", nevent: str = "", nsolid: bool = False):
        """Edit an event by its index in the sorted events list."""
        file_path = os.path.join(_get_data_folder(), "events.json")
        data = self._load_events()
        sorted_data = sorted(data, key=lambda e: e["date"])
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
