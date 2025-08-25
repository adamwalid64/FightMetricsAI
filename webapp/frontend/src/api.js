// Simple API helper to centralize backend base URL
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export function apiUrl(path) {
  if (!path.startsWith('/')) path = `/${path}`;
  if (!API_BASE_URL) return path; // fallback to relative during dev proxy, if configured
  return `${API_BASE_URL}${path}`;
}

export async function apiFetch(path, options = {}) {
  const url = apiUrl(path);
  return fetch(url, options);
}


