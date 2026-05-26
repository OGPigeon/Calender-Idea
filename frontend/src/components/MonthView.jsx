import { format, isSameMonth, isSameDay, isToday, parseISO } from "date-fns";
import { getMonthGrid, DAY_NAMES } from "../utils/dateUtils";
import { getColor } from "../utils/colors";

export default function MonthView({ current, selectedDate, events, onDayClick, onEventClick, searchQuery }) {
  const grid = getMonthGrid(current);
  const filtered = searchQuery
    ? events.filter(e => e.event.toLowerCase().includes(searchQuery.toLowerCase()))
    : events;

  const eventsForDay = (day) =>
    filtered.filter(e => {
      try { return isSameDay(parseISO(e.date), day); } catch { return false; }
    });

  return (
    <div className="month-view">
      <div className="month-day-names">
        {DAY_NAMES.map(d => (
          <div key={d} className="month-day-name">{d}</div>
        ))}
      </div>
      <div className="month-grid">
        {grid.map((day, i) => {
          const otherMonth = !isSameMonth(day, current);
          const today = isToday(day);
          const selected = selectedDate && isSameDay(day, selectedDate);
          const dayEvts = eventsForDay(day);

          let cls = "month-cell";
          if (otherMonth) cls += " other-month";
          if (today) cls += " today";
          if (selected) cls += " selected";

          let numCls = "month-day-num";
          if (today) numCls += " today";
          else if (otherMonth) numCls += " other-month";

          const MAX = 3;
          const visible = dayEvts.slice(0, MAX);
          const hidden = dayEvts.length - MAX;

          return (
            <div key={i} className={cls} onClick={() => onDayClick(day)}>
              <div className={numCls}>{format(day, "d")}</div>
              {visible.map((evt, j) => (
                <div
                  key={j}
                  className={`month-event-pill${evt.solid ? " locked" : ""}`}
                  style={{ background: getColor(evt) }}
                  onClick={e => { e.stopPropagation(); onEventClick(evt, e); }}
                  title={evt.event}
                >
                  {evt.stime ? `${evt.stime} ` : ""}{evt.event}
                </div>
              ))}
              {hidden > 0 && (
                <div className="month-more" onClick={e => { e.stopPropagation(); onDayClick(day); }}>
                  +{hidden} more
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
