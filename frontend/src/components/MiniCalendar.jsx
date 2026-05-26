import { format, addMonths, subMonths, isSameDay, isSameMonth, isToday } from "date-fns";
import { getMonthGrid, DAY_NAMES, parseEventDate } from "../utils/dateUtils";

export default function MiniCalendar({ current, selected, events, onSelect, onMonthChange }) {
  const grid = getMonthGrid(current);
  const eventDates = events.map(e => parseEventDate(e)).filter(Boolean);

  return (
    <div className="mini-cal">
      <div className="mini-cal-header">
        <span className="mini-cal-title">{format(current, "MMMM yyyy")}</span>
        <div className="mini-cal-nav">
          <button onClick={() => onMonthChange(subMonths(current, 1))}>‹</button>
          <button onClick={() => onMonthChange(addMonths(current, 1))}>›</button>
        </div>
      </div>
      <div className="mini-cal-grid">
        {DAY_NAMES.map(d => (
          <div key={d} className="mini-cal-dayname">{d[0]}</div>
        ))}
        {grid.map((day, i) => {
          const otherMonth = !isSameMonth(day, current);
          const today = isToday(day);
          const sel = selected && isSameDay(day, selected);
          const hasEvts = eventDates.some(d => isSameDay(d, day));
          let cls = "mini-cal-day";
          if (otherMonth) cls += " other-month";
          if (today) cls += " today";
          if (sel) cls += " selected";
          if (hasEvts) cls += " has-events";
          return (
            <div key={i} className={cls} onClick={() => onSelect(day)}>
              {format(day, "d")}
            </div>
          );
        })}
      </div>
    </div>
  );
}
