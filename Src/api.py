"""Flask REST API wrapping the existing Events/System logic."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
from flask_cors import CORS
from Event import Events
from System import System
import sync

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
    """Create a new event from the request body and save it."""
    body = request.json
    date = body.get("date", "").strip()
    stime = body.get("stime", "").strip()
    etime = body.get("etime", "").strip()
    event = body.get("event", "").strip()
    solid = bool(body.get("solid", False))
    color = body.get("color", "blue")
    allday = bool(body.get("allday", False))

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

    new_event._create_event(color=color, allday=allday)

    all_events = _sorted(_load())
    created = next((e for e in all_events if e["date"] == date and e["event"] == event), None)
    return jsonify({"overlap": overlap, "event": created}), 201


@app.route("/api/events/<int:idx>", methods=["PUT"])
def update_event(idx):
    """Update an existing event by its sorted index."""
    body = request.json
    events = _sorted(_load())
    if idx < 0 or idx >= len(events):
        return jsonify({"error": "index out of range"}), 404

    loader = Events("", "", "", "", False)
    loader._edit_event(
        idx,
        ndate=body.get("date") or None,
        nstime=body["stime"] if "stime" in body else None,
        netime=body["etime"] if "etime" in body else None,
        nevent=body.get("event") or None,
        nsolid=bool(body["solid"]) if "solid" in body else None,
        ncolor=body["color"] if "color" in body else None,
        nallday=bool(body["allday"]) if "allday" in body else None,
    )

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


@app.route("/api/sync/pull", methods=["POST"])
def sync_pull():
    """Pull the latest events.json from the remote GitHub repository."""
    try:
        msg = sync.pull()
        return jsonify({"message": msg})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sync/push", methods=["POST"])
def sync_push():
    """Commit and push the current events.json to the remote GitHub repository."""
    try:
        msg = sync.push()
        return jsonify({"message": msg})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001, debug=True)
