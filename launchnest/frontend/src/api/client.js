/**
 * LaunchNest — API Client
 * Axios instance for the LaunchNest backend on port 8000.
 * Auto-attaches JWT token from localStorage.
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Request interceptor: attach JWT ───
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('ln_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response interceptor: handle 401 ───
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear and reload
      localStorage.removeItem('ln_token');
      localStorage.removeItem('ln_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ─── API methods ───

export const api = {
  // Auth
  login: (email, password) =>
    client.post('/api/auth/login', { email, password }).then((r) => r.data),

  register: (payload) =>
    client.post('/api/auth/register', payload).then((r) => r.data),

  me: () => client.get('/api/auth/me').then((r) => r.data),

  // Dashboard
  stats: () => client.get('/api/dashboard/stats').then((r) => r.data),

  // Projects
  projects: () => client.get('/api/projects').then((r) => r.data),
  project: (id) => client.get(`/api/projects/${id}`).then((r) => r.data),
  createProject: (payload) =>
    client.post('/api/projects', payload).then((r) => r.data),
  updateProject: (id, payload) =>
    client.put(`/api/projects/${id}`, payload).then((r) => r.data),
  deleteProject: (id) =>
    client.delete(`/api/projects/${id}`).then((r) => r.data),

  // Tasks
  tasks: (params = {}) =>
    client.get('/api/tasks', { params }).then((r) => r.data),
  createTask: (payload) =>
    client.post('/api/tasks', payload).then((r) => r.data),
  updateTask: (id, payload) =>
    client.put(`/api/tasks/${id}`, payload).then((r) => r.data),
  deleteTask: (id) =>
    client.delete(`/api/tasks/${id}`).then((r) => r.data),

  // Team
  team: () => client.get('/api/team').then((r) => r.data),
};

export default client;