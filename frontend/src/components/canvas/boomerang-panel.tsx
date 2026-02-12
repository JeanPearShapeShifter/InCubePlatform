"use client";

import { useEffect, useRef } from "react";
import { Loader2, CheckCircle2, AlertCircle, Circle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useCanvasStore, AGENTS } from "@/stores/canvas-store";
import type { AgentOutput } from "@/stores/canvas-store";
import { useJourneyStore } from "@/stores/journey-store";
import { connectSSE } from "@/lib/sse";
import type { AgentName } from "@/types";

const StatusIcon = ({ status }: { status: AgentOutput["status"] }) => {
  switch (status) {
    case "pending":
      return <Circle className="h-4 w-4 text-muted-foreground" />;
    case "running":
      return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
    case "complete":
      return <CheckCircle2 className="h-4 w-4 text-[var(--color-success)]" />;
    case "error":
      return <AlertCircle className="h-4 w-4 text-[var(--color-error)]" />;
  }
};

interface BoomerangPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  perspectiveId: string | null;
}

export function BoomerangPanel({
  open,
  onOpenChange,
  perspectiveId,
}: BoomerangPanelProps) {
  const {
    agentOutputs,
    isBoomerangRunning,
    stopBoomerang,
    setAgentOutput,
  } = useCanvasStore();
  const { updatePerspectiveStatus, fetchPerspectives, activeJourney } =
    useJourneyStore();
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!open || !perspectiveId || !isBoomerangRunning) return;

    const controller = connectSSE(
      `/api/perspectives/${perspectiveId}/boomerang`,
      {
        method: "POST",
        body: { prompt: "" },
        onEvent: (event) => {
          try {
            const data = JSON.parse(event.data);
            const agentName = data.agent_name as AgentName;

            switch (event.event) {
              case "agent_start":
                setAgentOutput(agentName, { status: "running" });
                break;
              case "agent_chunk":
                setAgentOutput(agentName, {
                  content:
                    (agentOutputs[agentName]?.content ?? "") +
                    (data.chunk ?? ""),
                });
                break;
              case "agent_complete":
                setAgentOutput(agentName, {
                  status: "complete",
                  content: data.content ?? agentOutputs[agentName]?.content,
                  inputTokens: data.input_tokens ?? 0,
                  outputTokens: data.output_tokens ?? 0,
                  costUsd: data.cost_usd ?? 0,
                });
                break;
              case "agent_error":
                setAgentOutput(agentName, {
                  status: "error",
                  content: data.error ?? "Agent failed",
                });
                break;
              case "boomerang_complete":
                stopBoomerang();
                if (perspectiveId) {
                  updatePerspectiveStatus(perspectiveId, "completed").then(() => {
                    if (activeJourney) {
                      fetchPerspectives(activeJourney.id);
                    }
                  });
                }
                break;
            }
          } catch {
            // Skip unparseable events
          }
        },
        onError: () => {
          stopBoomerang();
        },
        onClose: () => {
          stopBoomerang();
        },
      },
    );

    abortRef.current = controller;
    return () => controller.abort();
  }, [open, perspectiveId, isBoomerangRunning]); // eslint-disable-line react-hooks/exhaustive-deps

  const agents = AGENTS;
  const completedCount = Object.values(agentOutputs).filter(
    (o) => o.status === "complete",
  ).length;
  const totalAgents = agents.length;
  const progressPercent =
    totalAgents > 0 ? (completedCount / totalAgents) * 100 : 0;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-[400px] sm:w-[480px]">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            Boomerang
            {isBoomerangRunning && (
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
            )}
          </SheetTitle>
        </SheetHeader>

        <div className="mt-4 space-y-4">
          <div className="space-y-1" role="status" aria-label="Boomerang progress">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">
                {completedCount} / {totalAgents}
              </span>
            </div>
            <Progress value={progressPercent} className="h-2" />
          </div>

          <ScrollArea className="h-[calc(100vh-200px)]">
            <div className="space-y-2 pr-4" aria-live="polite">
              {agents.map((agent) => {
                const output = agentOutputs[agent.name];
                const status = output?.status ?? "pending";

                return (
                  <div
                    key={agent.name}
                    className={cn(
                      "rounded-lg border border-border p-3 transition-colors",
                      status === "running" && "border-primary/50 bg-primary/5",
                      status === "complete" && "bg-muted/50",
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="h-2.5 w-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: agent.colorVar }}
                      />
                      <span className="text-sm font-medium flex-1">
                        {agent.label}
                      </span>
                      <span className="text-xs text-muted-foreground mr-1">
                        {agent.role}
                      </span>
                      <StatusIcon status={status} />
                    </div>
                    {output?.content && (
                      <p className="mt-2 text-xs text-muted-foreground line-clamp-3">
                        {output.content}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </div>
      </SheetContent>
    </Sheet>
  );
}
