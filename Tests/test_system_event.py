"""Tests for System and Events classes."""
import json
import os
import sys
import pytest
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Src"))

from Event import Events
from System import System


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_event_dict(date="2026-04-13", stime="09:00", etime="10:00",
                    event="Meeting", solid=False):
    return {"date": date, "stime": stime, "etime": etime,
            "event": event, "solid": solid}


# ===========================================================================
# Events tests
# ===========================================================================

class TestEventsInit:
    def test_date_normalized(self):
        e = Events("2026-04-13", "09:00", "10:00", "Meeting", False)
        assert e.date == "2026-04-13"

    def test_stime_parsed(self):
        e = Events("2026-04-13", "09:00", "10:00", "Meeting", False)
        assert e.stime.hour == 9
        assert e.stime.minute == 0

    def test_etime_parsed(self):
        e = Events("2026-04-13", "09:00", "10:00", "Meeting", False)
        assert e.etime.hour == 10

    def test_empty_stime_is_none(self):
        e = Events("2026-04-13", "", "", "All-day", False)
        assert e.stime is None
        assert e.etime is None

    def test_solid_flag(self):
        e = Events("2026-04-13", "09:00", "10:00", "Locked", True)
        assert e.solid is True

    def test_str_contains_event_name(self):
        e = Events("2026-04-13", "09:00", "10:00", "Standup", False)
        assert "Standup" in str(e)

    def test_str_shows_locked_when_solid(self):
        e = Events("2026-04-13", "09:00", "10:00", "Sprint", True)
        assert "[LOCKED]" in str(e)

    def test_str_no_locked_when_not_solid(self):
        e = Events("2026-04-13", "09:00", "10:00", "Lunch", False)
        assert "[LOCKED]" not in str(e)


class TestEventsLoadEvents:
    def _make_json(self, data):
        return mock_open(read_data=json.dumps(data))

    def test_load_list(self):
        raw = [make_event_dict()]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", self._make_json(raw)):
            with patch("os.path.exists", return_value=True):
                result = e._load_events()
        assert len(result) == 1
        assert result[0]["event"] == "Meeting"

    def test_load_single_dict_wrapped_in_list(self):
        raw = make_event_dict()  # single dict, not a list
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", self._make_json(raw)):
            with patch("os.path.exists", return_value=True):
                result = e._load_events()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_load_defaults_missing_keys(self):
        raw = [{"date": "2026-04-13"}]  # missing most keys
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", self._make_json(raw)):
            result = e._load_events()
        assert result[0]["solid"] is False
        assert result[0]["event"] == ""


class TestEventsGetEvent:
    def test_returns_matching_event(self):
        raw = [make_event_dict(date="2026-04-13", stime="09:00", etime="10:00", event="Sync")]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", mock_open(read_data=json.dumps(raw))):
            result = e.get_event("2026-04-13", "09:00", "10:00")
        assert result["event"] == "Sync"

    def test_raises_value_error_when_not_found(self):
        raw = [make_event_dict(date="2026-04-13", stime="09:00", etime="10:00")]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", mock_open(read_data=json.dumps(raw))):
            with pytest.raises(ValueError):
                e.get_event("2026-04-14", "09:00", "10:00")


class TestEventsCreateEvent:
    def test_creates_file_with_new_event(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        e = Events("2026-04-13", "09:00", "10:00", "NewEvent", False)
        e._create_event()
        file_path = tmp_path / "events.json"
        assert file_path.exists()
        data = json.loads(file_path.read_text())
        assert data[0]["event"] == "NewEvent"
        del os.environ["DATA_FOLDER"]

    def test_appends_to_existing_file(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        file_path = tmp_path / "events.json"
        file_path.write_text(json.dumps([make_event_dict(event="Existing")]))

        e = Events("2026-04-14", "11:00", "12:00", "Second", False)
        e._create_event()

        data = json.loads(file_path.read_text())
        assert len(data) == 2
        assert data[1]["event"] == "Second"
        del os.environ["DATA_FOLDER"]


# ===========================================================================
# System tests
# ===========================================================================

SAMPLE_EVENTS = [
    make_event_dict(date="2026-04-13", stime="09:00", etime="10:00", event="Standup", solid=False),
    make_event_dict(date="2026-04-13", stime="14:00", etime="15:00", event="Review",  solid=True),
    make_event_dict(date="2026-04-14", stime="10:00", etime="11:00", event="Retro",   solid=False),
]


class TestSystemGetEvent:
    def test_returns_event_for_known_date(self):
        sys_ = System(SAMPLE_EVENTS)
        result = sys_.get_event("2026-04-14")
        assert result["event"] == "Retro"
        assert result["solid"] is False

    def test_returns_first_match_for_date_with_multiple(self):
        sys_ = System(SAMPLE_EVENTS)
        result = sys_.get_event("2026-04-13")
        assert result["event"] == "Standup"

    def test_raises_value_error_for_unknown_date(self):
        sys_ = System(SAMPLE_EVENTS)
        with pytest.raises(ValueError):
            sys_.get_event("2099-01-01")


class TestSystemIsSolid:
    def test_returns_true_when_solid_event_exists(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_solid("2026-04-13") is True

    def test_returns_false_when_no_solid_event(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_solid("2026-04-14") is False

    def test_returns_false_for_unknown_date(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_solid("2099-01-01") is False


class TestSystemIsOverlapped:
    def test_detects_stime_overlap(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_overlapped("2026-04-13", "09:00") is True

    def test_detects_etime_overlap(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_overlapped("2026-04-13", "10:00") is True

    def test_no_overlap_different_time(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_overlapped("2026-04-13", "11:00") is False

    def test_no_overlap_different_date(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_overlapped("2099-01-01", "09:00") is False

    def test_empty_stime_returns_false(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_overlapped("2026-04-13", "") is False

    def test_invalid_time_format_returns_false(self):
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_overlapped("2026-04-13", "not-a-time") is False

    def test_normalizes_time_before_comparing(self):
        # "9:00" should normalize to "09:00" and still match
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_overlapped("2026-04-13", "9:00") is True
