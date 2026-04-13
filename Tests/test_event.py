import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Src"))
from Event import Events


def make_json(tmp_dir, data):
    path = os.path.join(tmp_dir, "events.json")
    with open(path, "w") as f:
        json.dump(data, f)
    return path


class TestEventsInit(unittest.TestCase):
    def test_valid_init(self):
        e = Events("2026-04-13", "09:00", "10:00", "Meeting", True)
        self.assertEqual(e.date, "2026-04-13")
        self.assertEqual(e.event, "Meeting")
        self.assertTrue(e.solid)
        self.assertEqual(e.stime.hour, 9)
        self.assertEqual(e.etime.hour, 10)

    def test_none_times(self):
        e = Events("2026-04-13", None, None, "All day", False)
        self.assertIsNone(e.stime)
        self.assertIsNone(e.etime)

    def test_none_date(self):
        e = Events(None, "09:00", "10:00", "No date", False)
        self.assertIsNone(e.date)

    def test_invalid_date_format(self):
        with self.assertRaises(ValueError):
            Events("13-04-2026", "09:00", "10:00", "Bad date", False)

    def test_invalid_time_format(self):
        with self.assertRaises(ValueError):
            Events("2026-04-13", "9am", "10am", "Bad time", False)


class TestLoadEvents(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["DATA_FOLDER"] = self.tmp
        self.loader = Events(None, None, None, "", False)

    def tearDown(self):
        del os.environ["DATA_FOLDER"]

    def test_load_list_of_events(self):
        make_json(self.tmp, [
            {"date": "2026-01-01", "time": "", "event": "New Year", "solid": True},
            {"date": "2026-06-15", "time": "", "event": "Meeting", "solid": False},
        ])
        events = self.loader._load_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "New Year")
        self.assertEqual(events[1]["date"], "2026-06-15")

    def test_load_single_dict_wrapped_in_list(self):
        make_json(self.tmp, {"date": "2026-02-14", "time": "", "event": "Valentine's", "solid": False})
        events = self.loader._load_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "Valentine's")

    def test_load_missing_fields_default(self):
        make_json(self.tmp, [{"event": "No date or solid"}])
        events = self.loader._load_events()
        self.assertEqual(events[0]["date"], "")
        self.assertFalse(events[0]["solid"])

    def test_load_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.loader._load_events()

    def test_load_stress(self):
        """Many duplicate entries should not crash load."""
        entry = {"date": "2026-04-13", "time": "", "event": "Stress", "solid": True}
        make_json(self.tmp, [entry] * 500)
        events = self.loader._load_events()
        self.assertEqual(len(events), 500)


class TestGetEvent(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["DATA_FOLDER"] = self.tmp
        make_json(self.tmp, [
            {"date": "2026-04-13", "time": "", "event": "Phoebe time", "solid": True},
            {"date": "2026-01-27", "time": "None-None", "event": "Hi", "solid": False},
        ])
        self.loader = Events(None, None, None, "", False)

    def tearDown(self):
        del os.environ["DATA_FOLDER"]

    def test_get_existing_event(self):
        result = self.loader.get_event("2026-04-13")
        self.assertEqual(result["event"], "Phoebe time")
        self.assertTrue(result["solid"])

    def test_get_unlocked_event(self):
        result = self.loader.get_event("2026-01-27")
        self.assertEqual(result["event"], "Hi")
        self.assertFalse(result["solid"])

    def test_get_missing_date_raises(self):
        with self.assertRaises(ValueError):
            self.loader.get_event("1999-01-01")


class TestCreateEvent(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["DATA_FOLDER"] = self.tmp

    def tearDown(self):
        del os.environ["DATA_FOLDER"]

    def test_create_new_file(self):
        e = Events("2026-05-01", "10:00", "11:00", "Dentist", False)
        e._create_event()
        path = os.path.join(self.tmp, "events.json")
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["event"], "Dentist")

    def test_append_to_existing_list(self):
        make_json(self.tmp, [{"date": "2026-01-01", "time": "", "event": "Existing", "solid": True}])
        e = Events("2026-05-01", "10:00", "11:00", "New Event", False)
        e._create_event()
        path = os.path.join(self.tmp, "events.json")
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]["event"], "New Event")

    def test_create_wraps_single_dict(self):
        make_json(self.tmp, {"date": "2026-01-01", "time": "", "event": "Solo", "solid": True})
        e = Events("2026-05-01", "10:00", "11:00", "Second", False)
        e._create_event()
        path = os.path.join(self.tmp, "events.json")
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)

    def test_stress_create_many(self):
        """Adding many events should not crash."""
        for i in range(200):
            e = Events(f"2026-01-{(i % 28) + 1:02d}", "08:00", "09:00", f"Event {i}", False)
            e._create_event()
        path = os.path.join(self.tmp, "events.json")
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(len(data), 200)


if __name__ == "__main__":
    unittest.main()
