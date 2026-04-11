"use client";

import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import { api } from "@/lib/api";
import { Profile } from "@/types";

type AppContextType = {
  token: string | null;
  profile: Profile | null;
  setToken: (token: string | null) => void;
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("interview-coach-token");
    if (stored) setTokenState(stored);
  }, []);

  useEffect(() => {
    if (!token) {
      setProfile(null);
      return;
    }
    api.profile(token).then(setProfile).catch(() => setProfile(null));
  }, [token]);

  function setToken(nextToken: string | null) {
    setTokenState(nextToken);
    if (nextToken) {
      window.localStorage.setItem("interview-coach-token", nextToken);
    } else {
      window.localStorage.removeItem("interview-coach-token");
    }
  }

  return <AppContext.Provider value={{ token, profile, setToken }}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) throw new Error("useAppContext must be used inside AppProvider");
  return context;
}
