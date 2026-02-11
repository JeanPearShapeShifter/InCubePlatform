"use client";

import { useCanvasStore, AGENTS } from "@/stores/canvas-store";
import { AgentCard } from "./agent-card";

export function AgentGrid() {
  const agentOutputs = useCanvasStore((s) => s.agentOutputs);

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {AGENTS.map((agent) => (
        <AgentCard
          key={agent.name}
          agentName={agent.name}
          output={agentOutputs[agent.name]}
        />
      ))}
    </div>
  );
}
