import {
  startOfMonth, endOfMonth, startOfWeek, endOfWeek,
  eachDayOfInterval, format, addMonths, subMonths,
  addWeeks, subWeeks, addDays, subDays, isSameDay,
  isSameMonth, isToday, parseISO, getYear, getMonth,
  startOfYear, eachMonthOfInterval, endOfYear, addYears, subYears,
  getHours, getMinutes, setHours, setMinutes, startOfDay
} from "date-fns";

export {
  startOfMonth, endOfMonth, startOfWeek, endOfWeek,
  eachDayOfInterval, format, addMonths, subMonths,
  addWeeks, subWeeks, addDays, subDays, isSameDay,
  isSameMonth, isToday, parseISO, getYear, getMonth,
  startOfYear, eachMonthOfInterval, endOfYear, addYears, subYears,
  getHours, getMinutes, setHours, setMinutes, startOfDay
};

export function getMonthGrid(date) {
  const start = startOfWeek(startOfMonth(date), { weekStartsOn: 0 });
  const end = endOfWeek(endOfMonth(date), { weekStartsOn: 0 });
  return eachDayOfInterval({ start, end });
}

export function getWeekDays(date) {
  const start = startOfWeek(date, { weekStartsOn: 0 });
  const end = endOfWeek(date, { weekStartsOn: 0 });
  return eachDayOfInterval({ start, end });
}

export function parseEventDate(evt) {
  try { return parseISO(evt.date); } catch { return null; }
}

export function timeToMinutes(t) {
  if (!t) return null;
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}

export function minutesToTime(mins) {
  const h = Math.floor(mins / 60) % 24;
  const m = mins % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export const HOURS = Array.from({ length: 24 }, (_, i) => i);

export const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
export const DAY_NAMES_FULL = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
export const MONTH_NAMES = ["January","February","March","April","May","June","July","August","September","October","November","December"];
