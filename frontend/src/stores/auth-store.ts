"use client";

import { create } from "zustand";
import { api } from "@/lib/api";

interface User {
  id: string;
  email: string;
  name: string | null;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  sendMagicLink: (email: string) => Promise<void>;
  verifyToken: (token: string) => Promise<void>;
  refreshSession: () => Promise<void>;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  sendMagicLink: async (email: string) => {
    await api.post("/auth/magic-link", { email });
  },

  verifyToken: async (token: string) => {
    const data = await api.post<{ access_token: string; user: User }>(
      "/auth/verify",
      { token }
    );
    api.setToken(data.access_token);
    set({ user: data.user, isAuthenticated: true, isLoading: false });
  },

  refreshSession: async () => {
    try {
      const data = await api.post<{ access_token: string; user: User }>(
        "/auth/refresh"
      );
      api.setToken(data.access_token);
      set({ user: data.user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  logout: () => {
    api.setToken(null);
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  initialize: () => {
    const token = api.getToken();
    if (token) {
      useAuthStore.getState().refreshSession();
    } else {
      set({ isLoading: false });
    }
  },
}));
