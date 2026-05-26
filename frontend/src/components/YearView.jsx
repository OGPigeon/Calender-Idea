import { format, isSameMonth, isSameDay, isToday, parseISO, startOfYear, eachMonthOfInterval, endOfYear } from "date-fns";
import { getMonthGrid, DAY_NAMES } from "../utils/dateUtils";

export default function YearView({ current, events, onDayClick, onMonthClick }) {
  const months = eachMonthOfInterval({ start: startOfYear(current), end: endOfYear(current) });
  const eventDates = events.map(e => { try { return parseISO(e.date); } catch { return null; } }).filter(Boolean);

  return (
    <div className="year-view">
      <div className="year-grid">
        {months.map((month, mi) => {
          const grid = getMonthGrid(month);
          return (
            <div key={mi} className="year-month">
              <div className="year-month-title" onClick={() => onMonthClick(month)}>
                {format(month, "MMMM")}
              </div>
              <div className="year-mini-grid">
                {DAY_NAMES.map(d => (
                  <div key={d} className="year-mini-dayname">{d[0]}</div>
                ))}
                {grid.map((day, di) => {
                  const otherMonth = !isSameMonth(day, month);
                  const today = isToday(day);
                  const hasEvts = eventDates.some(d => isSameDay(d, day));
                  let cls = "year-mini-day";
                  if (otherMonth) cls += " other-month";
                  if (today) cls += " today";
                  if (hasEvts && !otherMonth) cls += " has-events";
                  return (
                    <div
                      key={di}
                      className={cls}
                      onClick={() => !otherMonth && onDayClick(day)}
                    >
                      {!otherMonth ? format(day, "d") : ""}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
