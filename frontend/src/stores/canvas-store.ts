"use client";

import { create } from "zustand";
import type {
  DimensionType,
  PhaseType,
  AgentName,
  PerspectiveStatus,
  ChallengeSeverity,
  ChallengeResolution,
} from "@/types";

export interface AgentOutput {
  agentName: AgentName;
  status: "pending" | "running" | "complete" | "error";
  content: string;
  inputTokens: number;
  outputTokens: number;
  costUsd: number;
}

export interface ActivePerspective {
  dimension: DimensionType;
  phase: PhaseType;
}

// Timeline event discriminated union
export type TimelineEvent =
  | { type: "agent_start"; timestamp: number; agent: AgentName }
  | { type: "agent_complete"; timestamp: number; agent: AgentName; snippet: string }
  | { type: "agent_error"; timestamp: number; agent: AgentName; error: string }
  | { type: "phase"; timestamp: number; message: string }
  | {
      type: "axiom_challenge";
      timestamp: number;
      agents: string[];
      challengeText: string;
      severity: ChallengeSeverity;
    }
  | {
      type: "challenge_response";
      timestamp: number;
      agent: string;
      response: string;
    }
  | {
      type: "axiom_verdict";
      timestamp: number;
      resolution: ChallengeResolution | string;
      resolutionText: string;
    };

interface CanvasState {
  activeJourneyId: string | null;
  activePerspective: ActivePerspective | null;
  agentOutputs: Record<string, AgentOutput>;
  isBoomerangRunning: boolean;
  timelineEvents: TimelineEvent[];
}

interface CanvasActions {
  setActiveJourneyId: (id: string | null) => void;
  setActivePerspective: (perspective: ActivePerspective | null) => void;
  startBoomerang: () => void;
  stopBoomerang: () => void;
  setAgentOutput: (agentName: AgentName, output: Partial<AgentOutput>) => void;
  addTimelineEvent: (event: TimelineEvent) => void;
  clearOutputs: () => void;
}

export const useCanvasStore = create<CanvasState & CanvasActions>(
  (set, get) => ({
    activeJourneyId: null,
    activePerspective: null,
    agentOutputs: {},
    isBoomerangRunning: false,
    timelineEvents: [],

    setActiveJourneyId: (id) => set({ activeJourneyId: id }),

    setActivePerspective: (perspective) =>
      set({ activePerspective: perspective }),

    startBoomerang: () => {
      const agents: AgentName[] = [
        "lyra",
        "mira",
        "dex",
        "rex",
        "vela",
        "koda",
        "halo",
        "nova",
        "axiom",
      ];
      const initial: Record<string, AgentOutput> = {};
      for (const name of agents) {
        initial[name] = {
          agentName: name,
          status: "pending",
          content: "",
          inputTokens: 0,
          outputTokens: 0,
          costUsd: 0,
        };
      }
      set({ isBoomerangRunning: true, agentOutputs: initial, timelineEvents: [] });
    },

    stopBoomerang: () => set({ isBoomerangRunning: false }),

    setAgentOutput: (agentName, output) => {
      const current = get().agentOutputs[agentName];
      if (!current) return;
      set({
        agentOutputs: {
          ...get().agentOutputs,
          [agentName]: { ...current, ...output },
        },
      });
    },

    addTimelineEvent: (event) =>
      set((state) => ({ timelineEvents: [...state.timelineEvents, event] })),

    clearOutputs: () =>
      set({ agentOutputs: {}, isBoomerangRunning: false, timelineEvents: [] }),
  }),
);

// Static agent metadata
export const AGENTS: {
  name: AgentName;
  label: string;
  role: string;
  colorVar: string;
}[] = [
  { name: "lyra", label: "Lyra", role: "Goal", colorVar: "var(--color-agent-lyra)" },
  { name: "mira", label: "Mira", role: "Stakeholder", colorVar: "var(--color-agent-mira)" },
  { name: "dex", label: "Dex", role: "Requirement", colorVar: "var(--color-agent-dex)" },
  { name: "rex", label: "Rex", role: "Capability", colorVar: "var(--color-agent-rex)" },
  { name: "vela", label: "Vela", role: "Value", colorVar: "var(--color-agent-vela)" },
  { name: "koda", label: "Koda", role: "Value-Stream", colorVar: "var(--color-agent-koda)" },
  { name: "halo", label: "Halo", role: "Value-Chain", colorVar: "var(--color-agent-halo)" },
  { name: "nova", label: "Nova", role: "Implementation", colorVar: "var(--color-agent-nova)" },
  { name: "axiom", label: "Axiom", role: "Challenger", colorVar: "var(--color-agent-axiom)" },
];

// Dimension display info
export const DIMENSIONS: {
  type: DimensionType;
  label: string;
  colorVar: string;
}[] = [
  { type: "architecture", label: "Architecture", colorVar: "var(--color-dim-architecture)" },
  { type: "design", label: "Design", colorVar: "var(--color-dim-design)" },
  { type: "engineering", label: "Engineering", colorVar: "var(--color-dim-engineering)" },
];

// Phase display info
export const PHASES: {
  type: PhaseType;
  label: string;
  colorVar: string;
}[] = [
  { type: "generate", label: "Generate", colorVar: "var(--color-phase-generate)" },
  { type: "review", label: "Review", colorVar: "var(--color-phase-review)" },
  { type: "validate", label: "Validate", colorVar: "var(--color-phase-validate)" },
  { type: "summarize", label: "Summarize", colorVar: "var(--color-phase-summarize)" },
];

// Intersection labels: dimension x phase
export const INTERSECTION_LABELS: Record<DimensionType, Record<PhaseType, string>> = {
  architecture: {
    generate: "Imagining",
    review: "Critiquing",
    validate: "Proving",
    summarize: "Distilling",
  },
  design: {
    generate: "Exploring",
    review: "Shaping",
    validate: "Testing",
    summarize: "Crystallizing",
  },
  engineering: {
    generate: "Inventing",
    review: "Optimizing",
    validate: "Verifying",
    summarize: "Synthesizing",
  },
};

// Status helpers
export const STATUS_CONFIG: Record<
  PerspectiveStatus,
  { label: string; className: string }
> = {
  locked: { label: "Locked", className: "text-muted-foreground opacity-50" },
  pending: { label: "Pending", className: "text-muted-foreground" },
  in_progress: { label: "In Progress", className: "text-primary" },
  completed: { label: "Completed", className: "text-[var(--color-success)]" },
};
