import { createContext, useContext, useEffect, useState } from "react";
import { getStoredToken, logoutRequest, setStoredToken } from "../api/fetchWithAuth";

const AuthContext = createContext();
const AUTH_TOKEN_EVENT = "auth-token-changed";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getStoredToken());

  const login = (newToken) => {
    setStoredToken(newToken);
    setToken(newToken);
  };

  const logout = async () => {
    await logoutRequest();
    setToken(null);
  };

  useEffect(() => {
    const syncToken = () => {
      setToken(getStoredToken());
    };

    window.addEventListener(AUTH_TOKEN_EVENT, syncToken);
    window.addEventListener("storage", syncToken);

    return () => {
      window.removeEventListener(AUTH_TOKEN_EVENT, syncToken);
      window.removeEventListener("storage", syncToken);
    };
  }, []);

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// hook personalizado 
export function useAuth() {
  return useContext(AuthContext);
}
