"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  Circle,
  XCircle,
  RotateCcw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
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

const STALL_TIMEOUT_MS = 90_000; // 90 seconds without events = stalled

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
  const [phaseMessage, setPhaseMessage] = useState<string>("");
  const [isStalled, setIsStalled] = useState(false);
  const stallTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /** Read the latest axiom content from the store (avoids stale closure). */
  const getAxiomContent = useCallback((): string => {
    return useCanvasStore.getState().agentOutputs["axiom"]?.content ?? "";
  }, []);

  const resetStallTimer = useCallback(() => {
    setIsStalled(false);
    if (stallTimerRef.current) clearTimeout(stallTimerRef.current);
    stallTimerRef.current = setTimeout(() => setIsStalled(true), STALL_TIMEOUT_MS);
  }, []);

  const handleCancel = useCallback(() => {
    abortRef.current?.abort();
    stopBoomerang();
    setPhaseMessage("Cancelled by user");
    setIsStalled(false);
    if (stallTimerRef.current) clearTimeout(stallTimerRef.current);
  }, [stopBoomerang]);

  useEffect(() => {
    if (!open || !perspectiveId || !isBoomerangRunning) return;

    setPhaseMessage("Connecting...");
    setIsStalled(false);

    const controller = connectSSE(
      `/api/perspectives/${perspectiveId}/boomerang`,
      {
        method: "POST",
        body: { prompt: "" },
        onEvent: (event) => {
          resetStallTimer();

          try {
            const data = JSON.parse(event.data);
            const agentName = (data.agent ?? data.agent_name) as AgentName;

            switch (event.event) {
              case "phase":
                setPhaseMessage(data.message ?? "");
                break;
              case "agent_start":
                setAgentOutput(agentName, { status: "running" });
                break;
              case "agent_chunk": {
                const current = useCanvasStore.getState().agentOutputs[agentName];
                setAgentOutput(agentName, {
                  content: (current?.content ?? "") + (data.chunk ?? ""),
                });
                break;
              }
              case "agent_complete":
                setAgentOutput(agentName, {
                  status: "complete",
                  content:
                    data.content ??
                    useCanvasStore.getState().agentOutputs[agentName]?.content,
                  inputTokens: data.input_tokens ?? 0,
                  outputTokens: data.output_tokens ?? 0,
                  costUsd: data.cost_usd ?? 0,
                });
                break;
              case "agent_error":
                setAgentOutput((agentName ?? "axiom") as AgentName, {
                  status: "error",
                  content: data.error ?? "Agent failed",
                });
                break;
              case "axiom_start":
                setAgentOutput("axiom", { status: "running" });
                setPhaseMessage("Axiom is reviewing specialist outputs...");
                break;
              case "axiom_challenge":
                setAgentOutput("axiom", {
                  status: "running",
                  content:
                    getAxiomContent() +
                    `**Challenge** (${data.severity ?? "medium"}): ${data.challenge_text ?? ""}\n\n`,
                });
                setPhaseMessage("Axiom raised a challenge...");
                break;
              case "challenge_response":
                setAgentOutput("axiom", {
                  status: "running",
                  content:
                    getAxiomContent() +
                    `**${data.agent ?? "Agent"} responds**: ${data.response ?? ""}\n\n`,
                });
                setPhaseMessage(
                  `${(data.agent as string)?.charAt(0).toUpperCase()}${(data.agent as string)?.slice(1) ?? "Agent"} responding to challenge...`,
                );
                break;
              case "axiom_verdict":
                setAgentOutput("axiom", {
                  status: "running",
                  content:
                    getAxiomContent() +
                    `**Verdict** (${data.resolution ?? ""}): ${data.resolution_text ?? ""}\n\n`,
                });
                setPhaseMessage("Axiom delivered verdict");
                break;
              case "boomerang_complete": {
                // Mark axiom as complete if it was running
                const axiomState =
                  useCanvasStore.getState().agentOutputs["axiom"];
                if (
                  axiomState?.status === "running" ||
                  axiomState?.status === "pending"
                ) {
                  setAgentOutput("axiom", {
                    status: axiomState.content ? "complete" : "error",
                    content: axiomState.content || "No Axiom output received",
                  });
                }
                stopBoomerang();
                setPhaseMessage("Complete");
                if (stallTimerRef.current)
                  clearTimeout(stallTimerRef.current);
                if (perspectiveId) {
                  updatePerspectiveStatus(
                    perspectiveId,
                    "completed",
                  ).then(() => {
                    if (activeJourney) {
                      fetchPerspectives(activeJourney.id);
                    }
                  });
                }
                break;
              }
            }
          } catch {
            // Skip unparseable events
          }
        },
        onError: () => {
          stopBoomerang();
          setPhaseMessage("Connection error");
          if (stallTimerRef.current) clearTimeout(stallTimerRef.current);
        },
        onClose: () => {
          stopBoomerang();
          if (stallTimerRef.current) clearTimeout(stallTimerRef.current);
        },
      },
    );

    abortRef.current = controller;
    resetStallTimer();

    return () => {
      controller.abort();
      if (stallTimerRef.current) clearTimeout(stallTimerRef.current);
    };
  }, [open, perspectiveId, isBoomerangRunning]); // eslint-disable-line react-hooks/exhaustive-deps

  const agents = AGENTS;
  const completedCount = Object.values(agentOutputs).filter(
    (o) => o.status === "complete",
  ).length;
  const errorCount = Object.values(agentOutputs).filter(
    (o) => o.status === "error",
  ).length;
  const totalAgents = agents.length;
  const doneCount = completedCount + errorCount;
  const progressPercent =
    totalAgents > 0 ? (doneCount / totalAgents) * 100 : 0;

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
          {/* Progress section */}
          <div className="space-y-1" role="status" aria-label="Boomerang progress">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">
                {completedCount} / {totalAgents}
                {errorCount > 0 && (
                  <span className="text-[var(--color-error)] ml-1">
                    ({errorCount} failed)
                  </span>
                )}
              </span>
            </div>
            <Progress value={progressPercent} className="h-2" />
          </div>

          {/* Status message */}
          {(phaseMessage || isStalled) && (
            <div
              className={cn(
                "rounded-md px-3 py-2 text-xs",
                isStalled
                  ? "bg-[var(--color-error)]/10 text-[var(--color-error)]"
                  : "bg-muted text-muted-foreground",
              )}
            >
              {isStalled
                ? "No response received for a while. The process may be stalled."
                : phaseMessage}
            </div>
          )}

          {/* Cancel / Retry controls */}
          {(isBoomerangRunning || isStalled) && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancel}
                className="flex items-center gap-1.5"
              >
                <XCircle className="h-3.5 w-3.5" />
                Cancel
              </Button>
              {isStalled && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    handleCancel();
                    // Allow UI to update, then user can re-trigger
                  }}
                  className="flex items-center gap-1.5"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  Stop &amp; Retry
                </Button>
              )}
            </div>
          )}

          <ScrollArea className="h-[calc(100vh-280px)]">
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
                      status === "error" && "border-[var(--color-error)]/50 bg-[var(--color-error)]/5",
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
                      <p
                        className={cn(
                          "mt-2 text-xs line-clamp-3",
                          status === "error"
                            ? "text-[var(--color-error)]"
                            : "text-muted-foreground",
                        )}
                      >
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
