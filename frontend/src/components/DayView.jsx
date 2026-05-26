import { format, isSameDay, isToday, parseISO } from "date-fns";
import { useRef, useEffect } from "react";
import { DAY_NAMES_FULL, HOURS, timeToMinutes } from "../utils/dateUtils";
import { getColor } from "../utils/colors";

const HOUR_H = 60;

function NowLine() {
  const now = new Date();
  const mins = now.getHours() * 60 + now.getMinutes();
  return <div className="now-line" style={{ top: (mins / 60) * HOUR_H }} />;
}

export default function DayView({ current, events, onSlotClick, onEventClick, searchQuery }) {
  const bodyRef = useRef(null);
  const filtered = searchQuery
    ? events.filter(e => e.event.toLowerCase().includes(searchQuery.toLowerCase()))
    : events;

  useEffect(() => {
    if (bodyRef.current) {
      const h = new Date().getHours();
      bodyRef.current.scrollTop = Math.max(0, (h - 1) * HOUR_H);
    }
  }, []);

  const allEvts = filtered.filter(e => {
    try { return isSameDay(parseISO(e.date), current); } catch { return false; }
  });
  const alldayEvts = allEvts.filter(e => e.allday || !e.stime);
  const dayEvts = allEvts.filter(e => !e.allday && e.stime);

  const today = isToday(current);
  const dowIdx = current.getDay();

  function eventStyle(evt) {
    const sm = timeToMinutes(evt.stime);
    const em = timeToMinutes(evt.etime);
    if (sm === null) return null;
    const top = (sm / 60) * HOUR_H;
    const height = em !== null && em > sm ? ((em - sm) / 60) * HOUR_H : HOUR_H * 0.5;
    return { top, height: Math.max(height, 18), background: getColor(evt) };
  }

  return (
    <div className="day-view">
      <div className="day-header">
        <span className="day-header-name">{DAY_NAMES_FULL[dowIdx]}</span>
        <div className={`day-header-num${today ? " today" : ""}`}>
          {format(current, "d")}
        </div>
      </div>

      {alldayEvts.length > 0 && (
        <div className="day-allday-row">
          <div className="week-allday-gutter">all-day</div>
          <div className="day-allday-cell">
            {alldayEvts.map((evt, j) => (
              <div
                key={j}
                className="allday-pill"
                style={{ background: getColor(evt) }}
                onClick={e => { e.stopPropagation(); onEventClick(evt, e); }}
                title={evt.event}
              >
                {evt.event}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="day-body" ref={bodyRef}>
        <div className="day-gutter">
          {HOURS.map(h => (
            <div key={h} className="week-hour-label">
              {h === 0 ? "" : format(new Date(2000, 0, 1, h), "h a")}
            </div>
          ))}
        </div>
        <div className="day-col">
          {HOURS.map(h => (
            <div
              key={h}
              className="week-hour-line"
              onClick={() => onSlotClick(current, `${String(h).padStart(2, "0")}:00`)}
            />
          ))}
          {today && <NowLine />}
          {dayEvts.map((evt, j) => {
            const style = eventStyle(evt);
            if (!style) return null;
            return (
              <div
                key={j}
                className="week-event"
                style={{ ...style, left: 4, right: 4 }}
                onClick={e => { e.stopPropagation(); onEventClick(evt, e); }}
              >
                <div className="ev-name">{evt.event}</div>
                {evt.stime && <div className="ev-time">{evt.stime}{evt.etime ? `–${evt.etime}` : ""}</div>}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
