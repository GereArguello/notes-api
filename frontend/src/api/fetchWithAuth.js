const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");
const TOKEN_STORAGE_KEY = "token";
const AUTH_TOKEN_EVENT = "auth-token-changed";

function notifyTokenChange() {
  window.dispatchEvent(new Event(AUTH_TOKEN_EVENT));
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }

  notifyTokenChange();
}

async function buildErrorMessage(res) {
  try {
    const data = await res.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }
  } catch {
    // Si la respuesta no es JSON, usamos un mensaje genérico.
  }

  return `Error ${res.status}`;
}

async function refreshAccessToken() {
  const res = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });

  if (!res.ok) {
    setStoredToken(null);
    throw new Error("Sesion expirada");
  }

  const data = await res.json();
  setStoredToken(data.access_token);
  return data.access_token;
}

export async function logoutRequest() {
  try {
    await fetch(`${API_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
  } finally {
    setStoredToken(null);
  }
}

export async function fetchWithAuth(endpoint, token, options = {}) {
  const { skipRefresh = false, headers: customHeaders, ...fetchOptions } = options;
  const url = `${API_URL}${endpoint}`;
  const currentToken = token ?? getStoredToken();
  const headers = {
    ...(currentToken ? { Authorization: `Bearer ${currentToken}` } : {}),
    ...(fetchOptions.body && { "Content-Type": "application/json" }),
    ...customHeaders,
  };

  const res = await fetch(url, {
    ...fetchOptions,
    credentials: "include",
    headers,
  });

  const isAuthRefreshCall = endpoint === "/auth/refresh";
  const canTryRefresh = res.status === 401 && currentToken && !skipRefresh && !isAuthRefreshCall;

  if (canTryRefresh) {
    const newToken = await refreshAccessToken();

    return fetchWithAuth(endpoint, newToken, {
      ...options,
      skipRefresh: true,
    });
  }

  if (!res.ok) {
    throw new Error(await buildErrorMessage(res));
  }

  if (res.status === 204) {
    return null;
  }

  return res.json();
}
