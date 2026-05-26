"""Flask REST API wrapping the existing Events/System logic."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
from flask_cors import CORS
from Event import Events
from System import System

app = Flask(__name__)
CORS(app)


def _load():
    loader = Events("", "", "", "", False)
    return loader._load_events()


def _sorted(events):
    return sorted(events, key=lambda e: (e["date"], e.get("stime") or ""))


@app.route("/api/events", methods=["GET"])
def get_events():
    return jsonify(_sorted(_load()))


@app.route("/api/events", methods=["POST"])
def create_event():
    body = request.json
    date = body.get("date", "").strip()
    stime = body.get("stime", "").strip()
    etime = body.get("etime", "").strip()
    event = body.get("event", "").strip()
    solid = bool(body.get("solid", False))
    color = body.get("color", "blue")

    if not date or not event:
        return jsonify({"error": "date and event are required"}), 400

    try:
        new_event = Events(date, stime, etime, event, solid)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    events = _load()
    sys_obj = System(events)

    if sys_obj.is_solid(date):
        return jsonify({"error": "A locked event exists on that date"}), 409

    overlap = sys_obj.is_overlapped(date, stime) if stime else False

    new_event._create_event()

    # patch color into the last event
    all_events = _load()
    for evt in all_events:
        if evt["date"] == date and evt["event"] == event and "color" not in evt:
            evt["color"] = color
    import json
    data_path = os.path.join(os.path.dirname(__file__), "..", "Data", "events.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2)

    return jsonify({"overlap": overlap, "event": _load()[-1]}), 201


@app.route("/api/events/<int:idx>", methods=["PUT"])
def update_event(idx):
    body = request.json
    events = _sorted(_load())
    if idx < 0 or idx >= len(events):
        return jsonify({"error": "index out of range"}), 404

    loader = Events("", "", "", "", False)
    loader._edit_event(
        idx,
        ndate=body.get("date") or None,
        nstime=body.get("stime") or None,
        netime=body.get("etime") or None,
        nevent=body.get("event") or None,
        nsolid=body.get("solid", False),
    )

    # update color
    if "color" in body:
        import json
        data_path = os.path.join(os.path.dirname(__file__), "..", "Data", "events.json")
        with open(data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        updated = _sorted(_load())
        target = updated[idx]
        for evt in raw:
            if evt.get("date") == target.get("date") and evt.get("event") == target.get("event"):
                evt["color"] = body["color"]
                break
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2)

    return jsonify(_sorted(_load())[idx])


@app.route("/api/events/<int:idx>", methods=["DELETE"])
def delete_event(idx):
    events = _sorted(_load())
    if idx < 0 or idx >= len(events):
        return jsonify({"error": "index out of range"}), 404
    loader = Events("", "", "", "", False)
    loader._delete_event(idx)
    return jsonify({"deleted": idx})


@app.route("/api/check-solid", methods=["GET"])
def check_solid():
    date = request.args.get("date", "")
    sys_obj = System(_load())
    return jsonify({"solid": sys_obj.is_solid(date)})


@app.route("/api/check-overlap", methods=["GET"])
def check_overlap():
    date = request.args.get("date", "")
    stime = request.args.get("stime", "")
    sys_obj = System(_load())
    return jsonify({"overlap": sys_obj.is_overlapped(date, stime)})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
