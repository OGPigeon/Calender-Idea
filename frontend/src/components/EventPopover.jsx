import { useEffect, useRef } from "react";
import { EVENT_COLORS } from "../utils/colors";

export default function EventPopover({ event, idx, anchor, onEdit, onDelete, onClose }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    if (anchor) {
      let top = anchor.y + 8;
      let left = anchor.x;
      if (left + r.width > vw - 12) left = vw - r.width - 12;
      if (top + r.height > vh - 12) top = anchor.y - r.height - 8;
      ref.current.style.top = top + "px";
      ref.current.style.left = left + "px";
    }
  }, [anchor]);

  const color = EVENT_COLORS[event.color] || EVENT_COLORS.blue;
  const timeStr = event.stime
    ? `${event.stime}${event.etime ? " – " + event.etime : ""}`
    : "All day";

  return (
    <>
      <div className="popover-overlay" onClick={onClose} />
      <div className="popover" ref={ref} style={{ top: -9999, left: -9999 }}>
        <div className="popover-header">
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: color, flexShrink: 0 }} />
              <span className="popover-title">{event.event}</span>
            </div>
            <div className="popover-meta">
              {event.date} &nbsp;·&nbsp; {timeStr}
            </div>
            {event.solid && <div className="popover-locked">🔒 Locked</div>}
          </div>
          <button className="modal-close" onClick={onClose} style={{ flexShrink: 0 }}>✕</button>
        </div>
        <div className="popover-actions">
          <button className="popover-btn popover-edit" onClick={onEdit}>Edit</button>
          <button className="popover-btn popover-delete" onClick={onDelete}>Delete</button>
        </div>
      </div>
    </>
  );
}
