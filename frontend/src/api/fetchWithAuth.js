console.log("ENV COMPLETO:", import.meta.env);
console.log("VITE_API_URL:", import.meta.env.VITE_API_URL);

const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function fetchWithAuth(endpoint, token, options = {}) {
  const url = `${API_URL}${endpoint}`;

  console.log("API BASE:", API_URL);
  console.log("ENDPOINT:", endpoint);
  console.log("URL FINAL:", url);

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`Error ${res.status}`);
  }

  return res.json();
}