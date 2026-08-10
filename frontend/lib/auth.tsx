"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import type { ReactNode } from "react";
import type { AuthResponse, User } from "@/types";
import { API_URL, clearAuth, getStoredUser, getToken, setAuth } from "./api";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoggedIn: boolean;
  isAdmin: boolean;
  hydrated: boolean;
  saveAuth: (data: AuthResponse) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setUser(getStoredUser());
    setToken(getToken());

    // Refresh the user identity against the backend.
    (async () => {
      const t = getToken();
      if (!t) return;
      try {
        const res = await fetch(`${API_URL}/api/me`, {
          headers: { Authorization: `Bearer ${t}` },
        });
        if (res.ok) {
          const freshUser = (await res.json()) as User;
          setUser(freshUser);
          localStorage.setItem("animehub_user", JSON.stringify(freshUser));
        } else {
          // Token expired or invalid -> drop it
          clearAuth();
          setUser(null);
          setToken(null);
        }
      } catch {
        // Backend offline right now; keep cached session
      }
    })();

    setHydrated(true);
  }, []);

  const saveAuth = useCallback((data: AuthResponse) => {
    setAuth(data);
    setUser(data.user);
    setToken(data.access_token);
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoggedIn: !!user && !!token,
        isAdmin: !!user && user.is_admin === 1,
        hydrated,
        saveAuth,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}