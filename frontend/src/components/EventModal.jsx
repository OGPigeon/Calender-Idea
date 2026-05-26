import { useState } from "react";
import { format, addMonths, subMonths, isSameDay, isSameMonth, isToday, parseISO } from "date-fns";
import { getMonthGrid, DAY_NAMES } from "../utils/dateUtils";

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

function DatePicker({ value, onChange }) {
  const tryParse = (v) => { try { return v ? parseISO(v) : new Date(); } catch { return new Date(); } };
  const [viewMonth, setViewMonth] = useState(() => tryParse(value));
  const selected = tryParse(value);
  const grid = getMonthGrid(viewMonth);

  return (
    <div className="date-picker">
      <div className="date-picker-header">
        <button type="button" onClick={() => setViewMonth(m => subMonths(m, 1))}>‹</button>
        <span>{format(viewMonth, "MMMM yyyy")}</span>
        <button type="button" onClick={() => setViewMonth(m => addMonths(m, 1))}>›</button>
      </div>
      <div className="date-picker-grid">
        {DAY_NAMES.map(d => (
          <div key={d} className="date-picker-dayname">{d[0]}</div>
        ))}
        {grid.map((day, i) => {
          const other = !isSameMonth(day, viewMonth);
          const today = isToday(day);
          const sel = value && isSameDay(day, selected);
          let cls = "date-picker-day";
          if (other) cls += " other-month";
          if (today && !sel) cls += " today";
          if (sel) cls += " selected";
          return (
            <div key={i} className={cls} onClick={() => onChange(format(day, "yyyy-MM-dd"))}>
              {format(day, "d")}
            </div>
          );
        })}
      </div>
    </div>
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
    allday: initial?.allday ?? (initial?.stime ? false : true),
    color: initial?.color ?? "blue",
  });
  const [error, setError] = useState("");

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSave = () => {
    if (!form.date || !form.event.trim()) {
      setError("Date and event name are required.");
      return;
    }
    if (!form.allday) {
      if (form.stime && !/^\d{2}:\d{2}$/.test(form.stime)) {
        setError("Start time must be HH:MM.");
        return;
      }
      if (form.etime && !/^\d{2}:\d{2}$/.test(form.etime)) {
        setError("End time must be HH:MM.");
        return;
      }
    }
    const data = { ...form };
    if (form.allday) { data.stime = ""; data.etime = ""; }
    onSave(data);
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
            <DatePicker value={form.date} onChange={v => set("date", v)} />
          </div>

          <Toggle on={form.allday} onChange={v => set("allday", v)} label="All day" />

          {!form.allday && (
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
          )}

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
