import axios from "axios";

const BASE = (import.meta.env.VITE_API_URL || "") + "/api";

let _getToken = null;

/** Called once from App.jsx after Clerk initialises so every request carries the JWT. */
export const setTokenGetter = (fn) => { _getToken = fn; };

axios.interceptors.request.use(async (config) => {
  if (_getToken) {
    const token = await _getToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const fetchEvents = () => axios.get(`${BASE}/events`).then(r => r.data);

export const createEvent = (data) => axios.post(`${BASE}/events`, data).then(r => r.data);

export const updateEvent = (idx, data) => axios.put(`${BASE}/events/${idx}`, data).then(r => r.data);

export const deleteEvent = (idx) => axios.delete(`${BASE}/events/${idx}`).then(r => r.data);

export const syncPull = () => axios.post(`${BASE}/sync/pull`).then(r => r.data);
export const syncPush = () => axios.post(`${BASE}/sync/push`).then(r => r.data);
