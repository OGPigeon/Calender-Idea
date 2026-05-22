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


def write_events(path, events):
    path.write_text(json.dumps(events))


def read_events(path):
    return json.loads(path.read_text())


# ===========================================================================
# Events — __init__ / __str__
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

    def test_solid_flag_true(self):
        e = Events("2026-04-13", "09:00", "10:00", "Locked", True)
        assert e.solid is True

    def test_solid_flag_false(self):
        e = Events("2026-04-13", "09:00", "10:00", "Free", False)
        assert e.solid is False

    def test_event_name_stored(self):
        e = Events("2026-04-13", "09:00", "10:00", "Standup", False)
        assert e.event == "Standup"

    def test_midnight_time(self):
        e = Events("2026-04-13", "00:00", "01:00", "Overnight", False)
        assert e.stime.hour == 0
        assert e.etime.hour == 1

    def test_end_of_day_time(self):
        e = Events("2026-04-13", "23:00", "23:59", "Late", False)
        assert e.stime.hour == 23
        assert e.etime.minute == 59


class TestEventsStr:
    def test_str_contains_event_name(self):
        e = Events("2026-04-13", "09:00", "10:00", "Standup", False)
        assert "Standup" in str(e)

    def test_str_shows_locked_when_solid(self):
        e = Events("2026-04-13", "09:00", "10:00", "Sprint", True)
        assert "[LOCKED]" in str(e)

    def test_str_no_locked_when_not_solid(self):
        e = Events("2026-04-13", "09:00", "10:00", "Lunch", False)
        assert "[LOCKED]" not in str(e)

    def test_str_contains_date(self):
        e = Events("2026-04-13", "09:00", "10:00", "Demo", False)
        assert "2026-04-13" in str(e)


# ===========================================================================
# Events — _load_events
# ===========================================================================

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
        raw = make_event_dict()
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", self._make_json(raw)):
            with patch("os.path.exists", return_value=True):
                result = e._load_events()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_load_defaults_missing_keys(self):
        raw = [{"date": "2026-04-13"}]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", self._make_json(raw)):
            result = e._load_events()
        assert result[0]["solid"] is False
        assert result[0]["event"] == ""
        assert result[0]["stime"] is None
        assert result[0]["etime"] is None

    def test_load_multiple_events(self):
        raw = [make_event_dict(event="A"), make_event_dict(event="B")]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", self._make_json(raw)):
            result = e._load_events()
        assert len(result) == 2
        assert {r["event"] for r in result} == {"A", "B"}

    def test_load_preserves_solid_true(self):
        raw = [make_event_dict(solid=True)]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", self._make_json(raw)):
            result = e._load_events()
        assert result[0]["solid"] is True


# ===========================================================================
# Events — get_event
# ===========================================================================

class TestEventsGetEvent:
    def test_returns_matching_event(self):
        raw = [make_event_dict(date="2026-04-13", stime="09:00", etime="10:00", event="Sync")]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", mock_open(read_data=json.dumps(raw))):
            result = e.get_event("2026-04-13", "09:00", "10:00")
        assert result["event"] == "Sync"

    def test_returns_solid_status(self):
        raw = [make_event_dict(date="2026-04-13", stime="09:00", etime="10:00", solid=True)]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", mock_open(read_data=json.dumps(raw))):
            result = e.get_event("2026-04-13", "09:00", "10:00")
        assert result["solid"] is True

    def test_raises_value_error_when_not_found(self):
        raw = [make_event_dict(date="2026-04-13", stime="09:00", etime="10:00")]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", mock_open(read_data=json.dumps(raw))):
            with pytest.raises(ValueError):
                e.get_event("2026-04-14", "09:00", "10:00")

    def test_raises_value_error_wrong_time(self):
        raw = [make_event_dict(date="2026-04-13", stime="09:00", etime="10:00")]
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        with patch("builtins.open", mock_open(read_data=json.dumps(raw))):
            with pytest.raises(ValueError):
                e.get_event("2026-04-13", "11:00", "12:00")

    def test_matches_correct_event_among_multiple(self):
        raw = [
            make_event_dict(date="2026-04-13", stime="09:00", etime="10:00", event="Morning"),
            make_event_dict(date="2026-04-13", stime="14:00", etime="15:00", event="Afternoon"),
        ]
        e = Events("2026-04-13", "14:00", "15:00", "x", False)
        with patch("builtins.open", mock_open(read_data=json.dumps(raw))):
            result = e.get_event("2026-04-13", "14:00", "15:00")
        assert result["event"] == "Afternoon"


# ===========================================================================
# Events — _create_event
# ===========================================================================

class TestEventsCreateEvent:
    def test_creates_file_with_new_event(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        e = Events("2026-04-13", "09:00", "10:00", "NewEvent", False)
        e._create_event()
        file_path = tmp_path / "events.json"
        assert file_path.exists()
        data = read_events(file_path)
        assert data[0]["event"] == "NewEvent"
        del os.environ["DATA_FOLDER"]

    def test_appends_to_existing_file(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        file_path = tmp_path / "events.json"
        write_events(file_path, [make_event_dict(event="Existing")])

        e = Events("2026-04-14", "11:00", "12:00", "Second", False)
        e._create_event()

        data = read_events(file_path)
        assert len(data) == 2
        assert data[1]["event"] == "Second"
        del os.environ["DATA_FOLDER"]

    def test_created_event_has_correct_fields(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        e = Events("2026-04-13", "09:00", "10:00", "Standup", True)
        e._create_event()
        data = read_events(tmp_path / "events.json")
        evt = data[0]
        assert evt["date"] == "2026-04-13"
        assert evt["stime"] == "09:00"
        assert evt["etime"] == "10:00"
        assert evt["event"] == "Standup"
        assert evt["solid"] is True
        del os.environ["DATA_FOLDER"]

    def test_all_day_event_has_none_times(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        e = Events("2026-04-13", "", "", "Holiday", False)
        e._create_event()
        data = read_events(tmp_path / "events.json")
        assert data[0]["stime"] is None
        assert data[0]["etime"] is None
        del os.environ["DATA_FOLDER"]

    def test_multiple_creates_accumulate(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        for i in range(3):
            stime = f"{9 + i:02d}:00"
            etime = f"{10 + i:02d}:00"
            Events("2026-04-13", stime, etime, f"Event{i}", False)._create_event()
        data = read_events(tmp_path / "events.json")
        assert len(data) == 3
        del os.environ["DATA_FOLDER"]


# ===========================================================================
# Events — _delete_event
# ===========================================================================

class TestEventsDeleteEvent:
    def test_deletes_event_by_index(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        events = [
            make_event_dict(date="2026-04-13", event="Alpha"),
            make_event_dict(date="2026-04-14", event="Beta"),
        ]
        write_events(tmp_path / "events.json", events)
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._delete_event(0)
        data = read_events(tmp_path / "events.json")
        assert len(data) == 1
        assert data[0]["event"] == "Beta"
        del os.environ["DATA_FOLDER"]

    def test_deletes_second_event(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        events = [
            make_event_dict(date="2026-04-13", event="Alpha"),
            make_event_dict(date="2026-04-14", event="Beta"),
        ]
        write_events(tmp_path / "events.json", events)
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._delete_event(1)
        data = read_events(tmp_path / "events.json")
        assert len(data) == 1
        assert data[0]["event"] == "Alpha"
        del os.environ["DATA_FOLDER"]

    def test_deletes_from_single_item_list(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        write_events(tmp_path / "events.json", [make_event_dict(event="Solo")])
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._delete_event(0)
        data = read_events(tmp_path / "events.json")
        assert data == []
        del os.environ["DATA_FOLDER"]

    def test_delete_uses_sorted_order(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        # Store in reverse order; index 0 in sorted = earliest date
        events = [
            make_event_dict(date="2026-04-15", event="Later"),
            make_event_dict(date="2026-04-13", event="Earlier"),
        ]
        write_events(tmp_path / "events.json", events)
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._delete_event(0)  # sorted index 0 = "Earlier"
        data = read_events(tmp_path / "events.json")
        assert len(data) == 1
        assert data[0]["event"] == "Later"
        del os.environ["DATA_FOLDER"]


# ===========================================================================
# Events — _edit_event
# ===========================================================================

class TestEventsEditEvent:
    def test_edit_event_name(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        write_events(tmp_path / "events.json", [make_event_dict(event="Old")])
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._edit_event(0, nevent="New")
        data = read_events(tmp_path / "events.json")
        assert data[0]["event"] == "New"
        del os.environ["DATA_FOLDER"]

    def test_edit_date(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        write_events(tmp_path / "events.json", [make_event_dict(date="2026-04-13")])
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._edit_event(0, ndate="2026-05-01")
        data = read_events(tmp_path / "events.json")
        assert data[0]["date"] == "2026-05-01"
        del os.environ["DATA_FOLDER"]

    def test_edit_solid_flag(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        write_events(tmp_path / "events.json", [make_event_dict(solid=False)])
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._edit_event(0, nsolid=True)
        data = read_events(tmp_path / "events.json")
        assert data[0]["solid"] is True
        del os.environ["DATA_FOLDER"]

    def test_edit_times(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        write_events(tmp_path / "events.json", [make_event_dict(stime="09:00", etime="10:00")])
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._edit_event(0, nstime="13:00", netime="14:00")
        data = read_events(tmp_path / "events.json")
        assert data[0]["stime"] == "13:00"
        assert data[0]["etime"] == "14:00"
        del os.environ["DATA_FOLDER"]

    def test_edit_only_changes_target(self, tmp_path):
        os.environ["DATA_FOLDER"] = str(tmp_path)
        events = [
            make_event_dict(date="2026-04-13", event="Alpha"),
            make_event_dict(date="2026-04-14", event="Beta"),
        ]
        write_events(tmp_path / "events.json", events)
        e = Events("2026-04-13", "09:00", "10:00", "x", False)
        e._edit_event(0, nevent="AlphaEdited")
        data = read_events(tmp_path / "events.json")
        names = {d["event"] for d in data}
        assert "AlphaEdited" in names
        assert "Beta" in names
        del os.environ["DATA_FOLDER"]


# ===========================================================================
# System — get_event
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

    def test_returns_solid_true_event(self):
        events = [make_event_dict(date="2026-04-13", event="Locked", solid=True)]
        sys_ = System(events)
        assert sys_.get_event("2026-04-13")["solid"] is True

    def test_empty_events_raises(self):
        sys_ = System([])
        with pytest.raises(ValueError):
            sys_.get_event("2026-04-13")


# ===========================================================================
# System — is_solid
# ===========================================================================

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

    def test_returns_false_on_empty_list(self):
        assert System([]).is_solid("2026-04-13") is False

    def test_all_solid_events_on_date(self):
        events = [
            make_event_dict(date="2026-04-13", stime="09:00", event="A", solid=True),
            make_event_dict(date="2026-04-13", stime="11:00", event="B", solid=True),
        ]
        assert System(events).is_solid("2026-04-13") is True

    def test_mixed_solid_non_solid_same_date(self):
        events = [
            make_event_dict(date="2026-04-13", stime="09:00", event="Free", solid=False),
            make_event_dict(date="2026-04-13", stime="11:00", event="Lock", solid=True),
        ]
        assert System(events).is_solid("2026-04-13") is True


# ===========================================================================
# System — is_overlapped
# ===========================================================================

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
        sys_ = System(SAMPLE_EVENTS)
        assert sys_.is_overlapped("2026-04-13", "9:00") is True

    def test_no_overlap_on_empty_list(self):
        assert System([]).is_overlapped("2026-04-13", "09:00") is False

    def test_overlap_on_etime_boundary(self):
        events = [make_event_dict(date="2026-04-13", stime="09:00", etime="10:00")]
        assert System(events).is_overlapped("2026-04-13", "10:00") is True

    def test_no_overlap_just_outside_range(self):
        events = [make_event_dict(date="2026-04-13", stime="09:00", etime="10:00")]
        assert System(events).is_overlapped("2026-04-13", "10:01") is False

    def test_overlap_with_multiple_events_on_date(self):
        events = [
            make_event_dict(date="2026-04-13", stime="09:00", etime="10:00"),
            make_event_dict(date="2026-04-13", stime="13:00", etime="14:00"),
        ]
        assert System(events).is_overlapped("2026-04-13", "13:00") is True
