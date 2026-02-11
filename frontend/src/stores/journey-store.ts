"use client";

import { create } from "zustand";
import { apiGet, apiPost } from "@/lib/api";
import type { Journey, Perspective } from "@/types";

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
  fetchPerspectives: (journeyId: string) => Promise<void>;
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
        const journeys = await apiGet<Journey[]>("/api/journeys");
        set({ journeys, isLoading: false });
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

    fetchPerspectives: async (journeyId: string) => {
      const perspectives = await apiGet<Perspective[]>(
        `/api/journeys/${journeyId}/perspectives`,
      );
      set({ perspectives });
    },
  }),
);
