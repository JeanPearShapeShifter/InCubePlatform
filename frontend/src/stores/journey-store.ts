"use client";

import { create } from "zustand";
import { apiGet, apiPost, apiPatch } from "@/lib/api";
import type { Journey, Perspective } from "@/types";

interface JourneyDetailResponse extends Journey {
  perspectives: Perspective[];
  bank_instances: unknown[];
}

interface JourneyState {
  journeys: Journey[];
  activeJourney: Journey | null;
  perspectives: Perspective[];
  isLoading: boolean;
}

interface JourneyActions {
  fetchJourneys: () => Promise<void>;
  createJourney: (goalId: string) => Promise<Journey>;
  setActiveJourney: (id: string) => void;
  fetchAndSetActiveJourney: (id: string) => Promise<void>;
  fetchPerspectives: (journeyId: string) => Promise<void>;
  updatePerspectiveStatus: (perspectiveId: string, status: string) => Promise<void>;
}

export const useJourneyStore = create<JourneyState & JourneyActions>(
  (set, get) => ({
    journeys: [],
    activeJourney: null,
    perspectives: [],
    isLoading: false,

    fetchJourneys: async () => {
      set({ isLoading: true });
      try {
        const res = await apiGet<{ journeys: Journey[]; pagination: unknown }>("/api/journeys");
        set({ journeys: res.journeys, isLoading: false });
      } catch {
        set({ isLoading: false });
      }
    },

    createJourney: async (goalId: string) => {
      const journey = await apiPost<Journey>("/api/journeys", {
        goal_id: goalId,
      });
      set((state) => ({ journeys: [journey, ...state.journeys] }));
      return journey;
    },

    setActiveJourney: (id: string) => {
      const journey =
        get().journeys.find((j) => j.id === id) ?? null;
      set({ activeJourney: journey });
    },

    fetchAndSetActiveJourney: async (id: string) => {
      // Try local store first
      const existing = get().journeys.find((j) => j.id === id) ?? null;
      if (existing) {
        set({ activeJourney: existing });
        return;
      }
      // Fetch from API
      set({ isLoading: true });
      try {
        const detail = await apiGet<JourneyDetailResponse>(`/api/journeys/${id}`);
        set({
          activeJourney: detail,
          journeys: [...get().journeys, detail],
          perspectives: detail.perspectives,
          isLoading: false,
        });
      } catch {
        set({ isLoading: false });
      }
    },

    fetchPerspectives: async (journeyId: string) => {
      const perspectives = await apiGet<Perspective[]>(
        `/api/journeys/${journeyId}/perspectives`,
      );
      set({ perspectives });
    },

    updatePerspectiveStatus: async (perspectiveId: string, status: string) => {
      try {
        await apiPatch<Perspective>(`/api/perspectives/${perspectiveId}/status`, { status });
      } catch {
        // Silently ignore — status update is best-effort
      }
    },
  }),
);
