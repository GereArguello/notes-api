const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function fetchWithAuth(endpoint, token, options = {}) {
  const url = `${API_URL}${endpoint}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(options.body && { "Content-Type": "application/json" }),
      ...options.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`Error ${res.status}`);
  }

  if (res.status === 204) return null;

  return res.json();
}