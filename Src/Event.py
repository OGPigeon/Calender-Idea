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


class Events:
    """A collection of events, loaded from a JSON file."""

    def __init__(self, date: str, stime: str, etime: str, event: str, solid: bool):
        self.stime = datetime.strptime(stime, "%H:%M") if stime else None
        self.etime = datetime.strptime(etime, "%H:%M") if etime else None
        self.date = datetime.strptime(date, "%Y-%m-%d").date().isoformat() if date else None
        self.event = event
        self.solid = solid
        
    def __str__(self):
        "returns event details in a readable format"
        return f"{self.date} - from {self.stime} to {self.etime} — {self.event} {'[LOCKED]' if self.solid else ''}"

    def _create_event(self) -> None:
        """Create a dict representation of the event."""
        data_folder = os.getenv("DATA_FOLDER", "Data")
        file_path = os.path.join(data_folder, "events.json")
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
    
    def _delete_event(self,date: datetime, stime: datetime, etime:datetime):
        "Finds and deletes the event from json"
        data_folder = os.getenv("DATA_FOLDER", "Data")
        file_path = os.path.join(data_folder, "events.json")
        new_data = self._load_events()
        event = self.get_event(date, stime, etime)
        new_data = [evt for evt in new_data if not (
            evt["event"] == event["event"] and
            evt["date"] == date and
            evt["stime"] == stime and
            evt["etime"] == etime
        )]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2)
            
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load and normalize events from the JSON file."""
        data_folder = os.getenv("DATA_FOLDER", "Data")
        file_path = os.path.join(data_folder, "events.json")
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

    def get_event(self, date: datetime, stime: datetime, etime: datetime) -> Dict[str, Any]:
        """Return event info for the given date, or raise ValueError if not found."""
        events = self._load_events()
        for evt in events:
            if evt["date"] == date and evt["stime"] == stime and evt["etime"] == etime:
                return {"event": evt["event"], "solid": evt["solid"]}
        raise ValueError(f"No event found for date: {date}")

