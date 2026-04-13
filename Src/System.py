from Event import Events
from datetime import datetime
from typing import Dict

class System:
    """A collection of events, loaded from a JSON file."""

    def __init__(self, events: list):
        self.events = events

    def get_event(self, date: str) -> Dict[str, bool]:
        """Return the event and solid status for the given date."""
        for event in self.events:
            if event["date"] == date:
                return {"event": event["event"], "solid": event["solid"]}
        raise ValueError(f"No event found for date: {date}")

    def is_solid(self, date: datetime, stime: datetime) -> bool:
        """check if the that date + time has a solid event or not"""
        for evt in self.events:
            if evt["date"] == date and evt["stime"] == stime and evt["solid"]:
                return True
        return False

    def is_overlapped(self, stime: str) -> bool:
        """check if the given start time conflicts with an existing event's time"""
        if not stime:
            return False
        try:
            normalized = datetime.strptime(stime, "%H:%M").strftime("%H:%M")
        except ValueError:
            return False
        for evt in self.events:
            if evt.get("stime") == normalized or evt.get("etime") == normalized:
                return True
        return False
