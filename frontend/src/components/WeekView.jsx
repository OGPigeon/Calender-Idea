import { format, isSameDay, isToday, parseISO } from "date-fns";
import { useRef, useEffect } from "react";
import { getWeekDays, DAY_NAMES, HOURS, timeToMinutes } from "../utils/dateUtils";
import { getColor } from "../utils/colors";

const HOUR_H = 60;

function NowLine() {
  const now = new Date();
  const mins = now.getHours() * 60 + now.getMinutes();
  return <div className="now-line" style={{ top: (mins / 60) * HOUR_H }} />;
}

export default function WeekView({ current, events, onSlotClick, onEventClick, searchQuery }) {
  const days = getWeekDays(current);
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

  const eventsForDay = (day) =>
    filtered.filter(e => {
      try { return isSameDay(parseISO(e.date), day); } catch { return false; }
    });

  const alldayForDay = (day) => eventsForDay(day).filter(e => e.allday || !e.stime);
  const timedForDay = (day) => eventsForDay(day).filter(e => !e.allday && e.stime);

  function eventStyle(evt) {
    const sm = timeToMinutes(evt.stime);
    const em = timeToMinutes(evt.etime);
    if (sm === null) return null;
    const top = (sm / 60) * HOUR_H;
    const height = em !== null && em > sm ? ((em - sm) / 60) * HOUR_H : HOUR_H * 0.5;
    return { top, height: Math.max(height, 18), background: getColor(evt) };
  }

  const hasAnyAllday = days.some(d => alldayForDay(d).length > 0);

  return (
    <div className="week-view">
      <div className="week-header">
        <div className="week-header-gutter" />
        {days.map((day, i) => {
          const today = isToday(day);
          return (
            <div key={i} className="week-header-day" onClick={() => onSlotClick(day, null)}>
              <div className="week-header-dayname">{DAY_NAMES[i]}</div>
              <div className={`week-header-daynum${today ? " today" : ""}`}>
                {format(day, "d")}
              </div>
            </div>
          );
        })}
      </div>

      {hasAnyAllday && (
        <div className="week-allday-row">
          <div className="week-allday-gutter">all-day</div>
          {days.map((day, di) => (
            <div key={di} className="week-allday-cell">
              {alldayForDay(day).map((evt, j) => (
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
          ))}
        </div>
      )}

      <div className="week-body" ref={bodyRef}>
        <div className="week-time-gutter">
          {HOURS.map(h => (
            <div key={h} className="week-hour-label">
              {h === 0 ? "" : format(new Date(2000, 0, 1, h), "h a")}
            </div>
          ))}
        </div>
        <div className="week-cols">
          {days.map((day, di) => {
            const dayEvts = timedForDay(day);
            const today = isToday(day);
            return (
              <div key={di} className="week-col">
                {HOURS.map(h => (
                  <div
                    key={h}
                    className="week-hour-line"
                    onClick={() => onSlotClick(day, `${String(h).padStart(2, "0")}:00`)}
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
                      style={style}
                      onClick={e => { e.stopPropagation(); onEventClick(evt, e); }}
                    >
                      <div className="ev-name">{evt.event}</div>
                      {evt.stime && <div className="ev-time">{evt.stime}{evt.etime ? `–${evt.etime}` : ""}</div>}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
