"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  Circle,
  XCircle,
  RotateCcw,
  Clock,
  Coins,
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
  SheetDescription,
} from "@/components/ui/sheet";
import { useCanvasStore, AGENTS } from "@/stores/canvas-store";
import type { AgentOutput } from "@/stores/canvas-store";
import { useJourneyStore } from "@/stores/journey-store";
import { connectSSE } from "@/lib/sse";
import type { AgentName } from "@/types";

const STALL_TIMEOUT_MS = 90_000;

const FATAL_ERROR_MESSAGES: Record<string, string> = {
  credit_balance:
    "API credit balance exhausted. Add credits in Settings > API Key to continue.",
  auth: "Invalid API key. Check your API key in Settings.",
};

function getFatalErrorMessage(errorType: string, fallback: string): string {
  return FATAL_ERROR_MESSAGES[errorType] ?? fallback;
}

function formatElapsed(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function formatCost(usd: number): string {
  if (usd <= 0) return "";
  if (usd < 0.01) return `$${usd.toFixed(4)}`;
  return `$${usd.toFixed(2)}`;
}

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
  const [isComplete, setIsComplete] = useState(false);
  const [fatalError, setFatalError] = useState<{ message: string; errorType: string } | null>(null);
  const stallTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Elapsed timer
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

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
    if (timerRef.current) clearInterval(timerRef.current);
  }, [stopBoomerang]);

  // Start/stop elapsed timer based on boomerang state
  useEffect(() => {
    if (isBoomerangRunning && open) {
      setElapsedSeconds(0);
      setIsComplete(false);
      timerRef.current = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isBoomerangRunning, open]);

  useEffect(() => {
    if (!open || !perspectiveId || !isBoomerangRunning) return;

    setPhaseMessage("Connecting...");
    setIsStalled(false);
    setIsComplete(false);
    setFatalError(null);

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
              case "boomerang_error": {
                const errorType = (data.error_type as string) ?? "unknown";
                const errorMsg = getFatalErrorMessage(
                  errorType,
                  (data.error as string) ?? "An error occurred",
                );
                setFatalError({ message: errorMsg, errorType });
                setPhaseMessage("");
                stopBoomerang();
                setIsStalled(false);
                if (stallTimerRef.current)
                  clearTimeout(stallTimerRef.current);
                if (timerRef.current) clearInterval(timerRef.current);
                break;
              }
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
                setIsComplete(true);
                setPhaseMessage("");
                if (stallTimerRef.current)
                  clearTimeout(stallTimerRef.current);
                if (timerRef.current) clearInterval(timerRef.current);
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
          if (timerRef.current) clearInterval(timerRef.current);
        },
        onClose: () => {
          stopBoomerang();
          if (stallTimerRef.current) clearTimeout(stallTimerRef.current);
          if (timerRef.current) clearInterval(timerRef.current);
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

  // Calculate totals
  const totalTokens = Object.values(agentOutputs).reduce(
    (sum, o) => sum + (o.inputTokens ?? 0) + (o.outputTokens ?? 0),
    0,
  );
  const totalCost = Object.values(agentOutputs).reduce(
    (sum, o) => sum + (o.costUsd ?? 0),
    0,
  );

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
          <SheetDescription>
            {isBoomerangRunning
              ? "8 specialist agents analyze this perspective in parallel, then Axiom challenges their findings to strengthen the analysis."
              : isComplete
                ? "Analysis complete. Bank this perspective to save your findings."
                : "Run all 9 agents to get a comprehensive analysis of this perspective."}
          </SheetDescription>
        </SheetHeader>

        <div className="mt-4 space-y-3">
          {/* Progress + Timer row */}
          <div className="space-y-1" role="status" aria-label="Boomerang progress">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <div className="flex items-center gap-3">
                {(isBoomerangRunning || elapsedSeconds > 0) && (
                  <span className="flex items-center gap-1 text-muted-foreground">
                    <Clock className="h-3.5 w-3.5" />
                    {formatElapsed(elapsedSeconds)}
                  </span>
                )}
                <span className="font-medium">
                  {completedCount} / {totalAgents}
                  {errorCount > 0 && (
                    <span className="text-[var(--color-error)] ml-1">
                      ({errorCount} failed)
                    </span>
                  )}
                </span>
              </div>
            </div>
            <Progress value={progressPercent} className="h-2" />
          </div>

          {/* Token/cost summary */}
          {totalTokens > 0 && (
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Coins className="h-3 w-3" />
                {totalTokens.toLocaleString()} tokens
              </span>
              {totalCost > 0 && (
                <span>{formatCost(totalCost)}</span>
              )}
            </div>
          )}

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

          {/* Fatal error banner */}
          {fatalError && (
            <div className="rounded-md border border-[var(--color-error)]/30 bg-[var(--color-error)]/5 px-3 py-2 text-xs text-[var(--color-error)]">
              <div className="flex items-center gap-1.5 font-medium">
                <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                {fatalError.errorType === "credit_balance"
                  ? "API Credits Exhausted"
                  : fatalError.errorType === "auth"
                    ? "Authentication Error"
                    : "Fatal Error"}
              </div>
              <p className="mt-1">{fatalError.message}</p>
            </div>
          )}

          {/* Completion message */}
          {isComplete && !fatalError && (
            <div className="rounded-md border border-[var(--color-success)]/30 bg-[var(--color-success)]/5 px-3 py-2 text-xs text-[var(--color-success)]">
              Analysis complete in {formatElapsed(elapsedSeconds)}. Bank this perspective to save your findings.
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
                  }}
                  className="flex items-center gap-1.5"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  Stop &amp; Retry
                </Button>
              )}
            </div>
          )}

          <ScrollArea className="h-[calc(100vh-340px)]">
            <div className="space-y-2 pr-4" aria-live="polite">
              {/* Collapsed error banner when all errors share the same message */}
              {(() => {
                const errorOutputs = agents
                  .map((a) => agentOutputs[a.name])
                  .filter((o) => o?.status === "error" && o.content);
                if (errorOutputs.length >= 3) {
                  const firstError = errorOutputs[0]?.content ?? "";
                  const allSame = errorOutputs.every(
                    (o) => o?.content === firstError,
                  );
                  if (allSame) {
                    return (
                      <div className="rounded-md border border-[var(--color-error)]/30 bg-[var(--color-error)]/5 px-3 py-2 text-xs text-[var(--color-error)]">
                        <div className="flex items-center gap-1.5 font-medium">
                          <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                          {errorOutputs.length} agents failed with the same
                          error
                        </div>
                        <p className="mt-1">{firstError}</p>
                      </div>
                    );
                  }
                }
                return null;
              })()}

              {agents.map((agent) => {
                const output = agentOutputs[agent.name];
                const status = output?.status ?? "pending";
                const tokens = (output?.inputTokens ?? 0) + (output?.outputTokens ?? 0);
                const cost = output?.costUsd ?? 0;

                // When there's a fatal error banner, hide individual error content
                // to avoid showing 8 identical error messages
                const errorOutputs = agents
                  .map((a) => agentOutputs[a.name])
                  .filter((o) => o?.status === "error" && o.content);
                const allSameError =
                  errorOutputs.length >= 3 &&
                  errorOutputs.every(
                    (o) => o?.content === errorOutputs[0]?.content,
                  );
                const hideErrorContent =
                  status === "error" && (fatalError != null || allSameError);

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
                    {/* Token + cost info */}
                    {status === "complete" && tokens > 0 && (
                      <div className="mt-1 flex items-center gap-2 text-[10px] text-muted-foreground">
                        <span>{tokens.toLocaleString()} tokens</span>
                        {cost > 0 && <span>{formatCost(cost)}</span>}
                      </div>
                    )}
                    {output?.content && !hideErrorContent && (
                      <p
                        className={cn(
                          "mt-1.5 text-xs line-clamp-3",
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
