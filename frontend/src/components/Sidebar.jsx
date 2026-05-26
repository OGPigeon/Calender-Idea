import MiniCalendar from "./MiniCalendar";

const CALENDARS = [
  { name: "Home", color: "#007aff" },
  { name: "Work", color: "#34c759" },
  { name: "Personal", color: "#ff9500" },
  { name: "Birthdays", color: "#ff3b30" },
  { name: "Holidays", color: "#5856d6" },
];

export default function Sidebar({ miniMonth, setMiniMonth, selectedDate, setSelectedDate, events, setView }) {
  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <MiniCalendar
          current={miniMonth}
          selected={selectedDate}
          events={events}
          onSelect={d => { setSelectedDate(d); setView("day"); }}
          onMonthChange={setMiniMonth}
        />
      </div>
      <div className="sidebar-section">
        <div className="sidebar-label">My Calendars</div>
        <div className="cal-list">
          {CALENDARS.map(c => (
            <div key={c.name} className="cal-list-item">
              <div className="cal-dot" style={{ background: c.color }} />
              {c.name}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
