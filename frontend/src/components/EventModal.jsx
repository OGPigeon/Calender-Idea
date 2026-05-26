import { useState, useEffect } from "react";
import { format } from "date-fns";

const COLORS = [
  { id: "red", hex: "#ff3b30" },
  { id: "orange", hex: "#ff9500" },
  { id: "yellow", hex: "#ffcc00" },
  { id: "green", hex: "#34c759" },
  { id: "teal", hex: "#5ac8fa" },
  { id: "blue", hex: "#007aff" },
  { id: "purple", hex: "#5856d6" },
  { id: "pink", hex: "#ff2d55" },
  { id: "brown", hex: "#a2845e" },
];

function Toggle({ on, onChange, label }) {
  return (
    <label className="modal-toggle" onClick={() => onChange(!on)}>
      <div className={`toggle-switch${on ? " on" : ""}`}>
        <div className="toggle-knob" />
      </div>
      {label}
    </label>
  );
}

export default function EventModal({ initial, onSave, onDelete, onClose }) {
  const isEdit = !!initial;
  const [form, setForm] = useState({
    date: initial?.date ?? "",
    stime: initial?.stime ?? "",
    etime: initial?.etime ?? "",
    event: initial?.event ?? "",
    solid: initial?.solid ?? false,
    color: initial?.color ?? "blue",
  });
  const [error, setError] = useState("");

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSave = () => {
    if (!form.date || !form.event.trim()) {
      setError("Date and event name are required.");
      return;
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(form.date)) {
      setError("Date must be YYYY-MM-DD.");
      return;
    }
    if (form.stime && !/^\d{2}:\d{2}$/.test(form.stime)) {
      setError("Start time must be HH:MM.");
      return;
    }
    if (form.etime && !/^\d{2}:\d{2}$/.test(form.etime)) {
      setError("End time must be HH:MM.");
      return;
    }
    onSave(form);
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <span className="modal-title">{isEdit ? "Edit Event" : "New Event"}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {error && <div style={{ color: "#ff3b30", fontSize: 13 }}>{error}</div>}

          <div className="modal-field">
            <label className="modal-label">Event Name</label>
            <input
              className="modal-input"
              value={form.event}
              onChange={e => set("event", e.target.value)}
              placeholder="Add title"
              autoFocus
              onKeyDown={e => e.key === "Enter" && handleSave()}
            />
          </div>

          <div className="modal-field">
            <label className="modal-label">Date</label>
            <input
              className="modal-input"
              type="date"
              value={form.date}
              onChange={e => set("date", e.target.value)}
            />
          </div>

          <div className="modal-row">
            <div className="modal-field">
              <label className="modal-label">Start Time</label>
              <input
                className="modal-input"
                type="time"
                value={form.stime}
                onChange={e => set("stime", e.target.value)}
              />
            </div>
            <div className="modal-field">
              <label className="modal-label">End Time</label>
              <input
                className="modal-input"
                type="time"
                value={form.etime}
                onChange={e => set("etime", e.target.value)}
              />
            </div>
          </div>

          <div className="modal-field">
            <label className="modal-label">Color</label>
            <div className="modal-color-row">
              {COLORS.map(c => (
                <div
                  key={c.id}
                  className={`color-dot${form.color === c.id ? " selected" : ""}`}
                  style={{ background: c.hex }}
                  onClick={() => set("color", c.id)}
                />
              ))}
            </div>
          </div>

          <Toggle on={form.solid} onChange={v => set("solid", v)} label="Locked (prevent other events)" />
        </div>

        <div className="modal-footer">
          {isEdit && (
            <button className="btn btn-delete" onClick={onDelete}>Delete</button>
          )}
          <div className="spacer" />
          <button className="btn btn-cancel" onClick={onClose}>Cancel</button>
          <button className="btn btn-save" onClick={handleSave}>
            {isEdit ? "Save" : "Add"}
          </button>
        </div>
      </div>
    </div>
  );
}
