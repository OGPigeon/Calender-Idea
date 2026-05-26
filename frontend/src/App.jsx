import { useState, useEffect, useCallback } from "react";
import { format, addMonths, subMonths, addWeeks, subWeeks, addDays, subDays, addYears, subYears } from "date-fns";
import { getWeekDays } from "./utils/dateUtils";
import Sidebar from "./components/Sidebar";
import MonthView from "./components/MonthView";
import WeekView from "./components/WeekView";
import DayView from "./components/DayView";
import YearView from "./components/YearView";
import EventModal from "./components/EventModal";
import EventPopover from "./components/EventPopover";
import { fetchEvents, createEvent, updateEvent, deleteEvent } from "./api";

function Toast({ msg, onDone }) {
  useEffect(() => {
    const t = setTimeout(onDone, 2200);
    return () => clearTimeout(t);
  }, [msg]);
  return <div className="toast">{msg}</div>;
}

export default function App() {
  const today = new Date();
  const [view, setView] = useState("month");
  const [current, setCurrent] = useState(today);
  const [miniMonth, setMiniMonth] = useState(today);
  const [selectedDate, setSelectedDate] = useState(today);
  const [events, setEvents] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [modal, setModal] = useState(null);
  const [popover, setPopover] = useState(null);
  const [toast, setToast] = useState(null);

  const load = useCallback(async () => {
    try { setEvents(await fetchEvents()); } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const showToast = (msg) => setToast(msg);

  const goPrev = () => {
    if (view === "month") setCurrent(c => subMonths(c, 1));
    else if (view === "week") setCurrent(c => subWeeks(c, 1));
    else if (view === "day") setCurrent(c => subDays(c, 1));
    else if (view === "year") setCurrent(c => subYears(c, 1));
  };
  const goNext = () => {
    if (view === "month") setCurrent(c => addMonths(c, 1));
    else if (view === "week") setCurrent(c => addWeeks(c, 1));
    else if (view === "day") setCurrent(c => addDays(c, 1));
    else if (view === "year") setCurrent(c => addYears(c, 1));
  };
  const goToday = () => { setCurrent(today); setSelectedDate(today); setMiniMonth(today); };

  const toolbarTitle = () => {
    if (view === "month") return format(current, "MMMM yyyy");
    if (view === "week") {
      const days = getWeekDays(current);
      const s = days[0], e = days[6];
      return format(s, "MMM yyyy") === format(e, "MMM yyyy")
        ? `${format(s, "MMM d")} – ${format(e, "d, yyyy")}`
        : `${format(s, "MMM d")} – ${format(e, "MMM d, yyyy")}`;
    }
    if (view === "day") return format(current, "EEEE, MMMM d, yyyy");
    if (view === "year") return format(current, "yyyy");
    return "";
  };

  const handleDayClick = (day) => {
    setSelectedDate(day);
    setMiniMonth(day);
    if (view === "month") { setCurrent(day); setView("day"); }
  };

  const handleSlotClick = (day, time) => {
    setModal({
      type: "new",
      initial: { date: format(day, "yyyy-MM-dd"), stime: time || "", etime: "", event: "", solid: false, color: "blue" }
    });
  };

  const handleEventClick = (evt, e) => {
    const rect = e?.currentTarget?.getBoundingClientRect();
    const anchor = rect ? { x: rect.left, y: rect.bottom } : { x: e.clientX, y: e.clientY };
    const idx = events.findIndex(ev => ev.date === evt.date && ev.event === evt.event && ev.stime === evt.stime);
    setPopover({ event: evt, idx, anchor });
  };

  const handleSave = async (form) => {
    try {
      if (modal.type === "new") {
        const res = await createEvent(form);
        showToast(res.overlap ? "Added (time overlap warning)" : "Event added");
      } else {
        await updateEvent(modal.idx, form);
        showToast("Event updated");
      }
      setModal(null);
      await load();
    } catch (err) {
      showToast(err?.response?.data?.error || "Failed to save event");
    }
  };

  const handleDelete = async (idx) => {
    try {
      await deleteEvent(idx);
      setModal(null);
      setPopover(null);
      showToast("Event deleted");
      await load();
    } catch { showToast("Failed to delete event"); }
  };

  const openEdit = () => {
    if (!popover) return;
    setModal({ type: "edit", initial: popover.event, idx: popover.idx });
    setPopover(null);
  };

  useEffect(() => {
    const h = (e) => {
      if (modal || popover) return;
      if (e.key === "ArrowLeft") goPrev();
      if (e.key === "ArrowRight") goNext();
      if (e.key === "t" || e.key === "T") goToday();
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [view, modal, popover]);

  return (
    <div className="app">
      <Sidebar
        miniMonth={miniMonth}
        setMiniMonth={setMiniMonth}
        selectedDate={selectedDate}
        setSelectedDate={d => { setSelectedDate(d); setCurrent(d); }}
        events={events}
        setView={setView}
      />

      <div className="main">
        <div className="toolbar">
          <button className="toolbar-today" onClick={goToday}>Today</button>
          <div className="toolbar-nav">
            <button onClick={goPrev}>‹</button>
            <button onClick={goNext}>›</button>
          </div>
          <span className="toolbar-title">{toolbarTitle()}</span>
          <input
            className="toolbar-search"
            placeholder="Search"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
          <div className="view-switcher">
            {["day", "week", "month", "year"].map(v => (
              <button key={v} className={view === v ? "active" : ""} onClick={() => setView(v)}>
                {v[0].toUpperCase() + v.slice(1)}
              </button>
            ))}
          </div>
          <button className="toolbar-add" title="New Event" onClick={() => setModal({
            type: "new",
            initial: { date: format(selectedDate || today, "yyyy-MM-dd"), stime: "", etime: "", event: "", solid: false, color: "blue" }
          })}>+</button>
        </div>

        {view === "month" && (
          <MonthView current={current} selectedDate={selectedDate} events={events}
            onDayClick={handleDayClick} onEventClick={handleEventClick} searchQuery={searchQuery} />
        )}
        {view === "week" && (
          <WeekView current={current} events={events}
            onSlotClick={handleSlotClick} onEventClick={handleEventClick} searchQuery={searchQuery} />
        )}
        {view === "day" && (
          <DayView current={current} events={events}
            onSlotClick={handleSlotClick} onEventClick={handleEventClick} searchQuery={searchQuery} />
        )}
        {view === "year" && (
          <YearView current={current} events={events}
            onDayClick={d => { setSelectedDate(d); setCurrent(d); setView("day"); }}
            onMonthClick={m => { setCurrent(m); setView("month"); }} />
        )}
      </div>

      {modal && (
        <EventModal
          initial={modal.initial}
          onSave={handleSave}
          onDelete={modal.type === "edit" ? () => handleDelete(modal.idx) : undefined}
          onClose={() => setModal(null)}
        />
      )}

      {popover && (
        <EventPopover
          event={popover.event}
          idx={popover.idx}
          anchor={popover.anchor}
          onEdit={openEdit}
          onDelete={() => handleDelete(popover.idx)}
          onClose={() => setPopover(null)}
        />
      )}

      {toast && <Toast msg={toast} onDone={() => setToast(null)} />}
    </div>
  );
}
