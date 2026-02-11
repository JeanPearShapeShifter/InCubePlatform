"use client";

import { create } from "zustand";
import { apiGet, apiPost } from "@/lib/api";
import type { User, Organization } from "@/types";

interface MeResponse extends User {
  organization: Organization;
}

interface AuthState {
  user: User | null;
  organization: Organization | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    name: string;
    organization_name: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  user: null,
  organization: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      await apiPost("/api/auth/login", { email, password });
      const me = await apiGet<MeResponse>("/api/auth/me");
      set({ user: me, organization: me.organization, isAuthenticated: true, isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : "Login failed",
      });
      throw err;
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await apiPost("/api/auth/register", data);
      const me = await apiGet<MeResponse>("/api/auth/me");
      set({ user: me, organization: me.organization, isAuthenticated: true, isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : "Registration failed",
      });
      throw err;
    }
  },

  logout: async () => {
    try {
      await apiPost("/api/auth/logout");
    } finally {
      set({
        user: null,
        organization: null,
        isAuthenticated: false,
        error: null,
      });
    }
  },

  fetchMe: async () => {
    set({ isLoading: true });
    try {
      const me = await apiGet<MeResponse>("/api/auth/me");
      set({ user: me, organization: me.organization, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, organization: null, isAuthenticated: false, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
