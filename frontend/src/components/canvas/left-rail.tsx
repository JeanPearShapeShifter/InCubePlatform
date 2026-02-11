"use client";

import { Lock, Circle, Loader2, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useCanvasStore, DIMENSIONS, PHASES, INTERSECTION_LABELS } from "@/stores/canvas-store";
import { useJourneyStore } from "@/stores/journey-store";
import type { PerspectiveStatus } from "@/types";
import { HeatMap } from "./heat-map";

const StatusIcon = ({ status }: { status: PerspectiveStatus }) => {
  switch (status) {
    case "locked":
      return <Lock className="h-3 w-3 opacity-50" />;
    case "pending":
      return <Circle className="h-3 w-3" />;
    case "in_progress":
      return <Loader2 className="h-3 w-3 animate-spin" />;
    case "completed":
      return <CheckCircle2 className="h-3 w-3" />;
  }
};

export function LeftRail() {
  const { activePerspective, setActivePerspective } = useCanvasStore();
  const perspectives = useJourneyStore((s) => s.perspectives);

  const getStatus = (
    dimension: string,
    phase: string,
  ): PerspectiveStatus => {
    const p = perspectives.find(
      (p) => p.dimension === dimension && p.phase === phase,
    );
    return p?.status ?? "locked";
  };

  return (
    <TooltipProvider delayDuration={200}>
      <div className="flex h-full w-56 flex-col border-r border-border bg-card">
        <div className="border-b border-border p-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Perspectives
          </h3>
        </div>
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-3">
            {DIMENSIONS.map((dim) => (
              <div key={dim.type}>
                <div className="flex items-center gap-2 px-2 py-1">
                  <div
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: dim.colorVar }}
                  />
                  <span className="text-xs font-semibold uppercase tracking-wider">
                    {dim.label}
                  </span>
                </div>
                <div className="mt-1 space-y-0.5">
                  {PHASES.map((phase) => {
                    const status = getStatus(dim.type, phase.type);
                    const isActive =
                      activePerspective?.dimension === dim.type &&
                      activePerspective?.phase === phase.type;
                    const intersectionLabel =
                      INTERSECTION_LABELS[dim.type][phase.type];

                    return (
                      <Tooltip key={phase.type}>
                        <TooltipTrigger asChild>
                          <button
                            onClick={() =>
                              setActivePerspective({
                                dimension: dim.type,
                                phase: phase.type,
                              })
                            }
                            disabled={status === "locked"}
                            className={cn(
                              "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm transition-colors",
                              isActive
                                ? "bg-primary/10 text-primary font-medium"
                                : "hover:bg-muted text-foreground",
                              status === "locked" &&
                                "cursor-not-allowed opacity-40",
                            )}
                          >
                            <StatusIcon status={status} />
                            <span className="flex-1 truncate">
                              {phase.label}
                            </span>
                            <span
                              className="h-1.5 w-1.5 rounded-full"
                              style={{ backgroundColor: phase.colorVar }}
                            />
                          </button>
                        </TooltipTrigger>
                        <TooltipContent side="right" className="text-xs">
                          {dim.label} x {phase.label} = {intersectionLabel}
                        </TooltipContent>
                      </Tooltip>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
          <div className="p-3 pt-1">
            <div className="border-t border-border pt-3">
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Heat Map
              </h4>
              <HeatMap compact />
            </div>
          </div>
        </ScrollArea>
      </div>
    </TooltipProvider>
  );
}
