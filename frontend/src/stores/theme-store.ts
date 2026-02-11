"use client";

import { create } from "zustand";

export type Theme = "space" | "forest" | "blackhole";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  theme: "space",
  setTheme: (theme: Theme) => {
    const root = document.documentElement;
    // Always keep "dark", toggle theme modifiers
    root.classList.remove("forest", "blackhole");
    if (theme !== "space") {
      root.classList.add(theme);
    }
    set({ theme });
  },
}));
