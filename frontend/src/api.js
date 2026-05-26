import axios from "axios";

const BASE = "/api";

export const fetchEvents = () => axios.get(`${BASE}/events`).then(r => r.data);

export const createEvent = (data) => axios.post(`${BASE}/events`, data).then(r => r.data);

export const updateEvent = (idx, data) => axios.put(`${BASE}/events/${idx}`, data).then(r => r.data);

export const deleteEvent = (idx) => axios.delete(`${BASE}/events/${idx}`).then(r => r.data);
