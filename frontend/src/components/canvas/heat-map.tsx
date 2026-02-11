"use client";

import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";
import { useCanvasStore, DIMENSIONS, PHASES, INTERSECTION_LABELS } from "@/stores/canvas-store";
import { useJourneyStore } from "@/stores/journey-store";
import type { PerspectiveStatus, DimensionType, PhaseType } from "@/types";

const statusOpacity: Record<PerspectiveStatus, string> = {
  locked: "opacity-15",
  pending: "opacity-30",
  in_progress: "opacity-70 animate-pulse",
  completed: "opacity-100",
};

interface HeatMapProps {
  compact?: boolean;
}

export function HeatMap({ compact }: HeatMapProps) {
  const { activePerspective, setActivePerspective } = useCanvasStore();
  const perspectives = useJourneyStore((s) => s.perspectives);

  const getStatus = (
    dimension: DimensionType,
    phase: PhaseType,
  ): PerspectiveStatus => {
    const p = perspectives.find(
      (p) => p.dimension === dimension && p.phase === phase,
    );
    return p?.status ?? "locked";
  };

  return (
    <TooltipProvider delayDuration={150}>
      <div className="space-y-1">
        {/* Column headers */}
        {!compact && (
          <div className="grid grid-cols-[auto_repeat(4,1fr)] gap-1">
            <div />
            {PHASES.map((phase) => (
              <div
                key={phase.type}
                className="text-center text-[10px] font-medium text-muted-foreground"
              >
                {phase.label.slice(0, 3)}
              </div>
            ))}
          </div>
        )}

        {DIMENSIONS.map((dim) => (
          <div
            key={dim.type}
            className={cn(
              "grid gap-1",
              compact
                ? "grid-cols-4"
                : "grid-cols-[auto_repeat(4,1fr)]",
            )}
          >
            {!compact && (
              <div className="flex items-center text-[10px] font-medium text-muted-foreground pr-1">
                {dim.label.slice(0, 4)}
              </div>
            )}
            {PHASES.map((phase) => {
              const status = getStatus(dim.type, phase.type);
              const isActive =
                activePerspective?.dimension === dim.type &&
                activePerspective?.phase === phase.type;
              const label = INTERSECTION_LABELS[dim.type][phase.type];

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
                        "rounded-sm transition-all",
                        compact ? "h-5 w-full" : "h-7 w-full",
                        statusOpacity[status],
                        isActive && "ring-2 ring-primary ring-offset-1 ring-offset-background",
                        status === "locked" && "cursor-not-allowed",
                      )}
                      style={{ backgroundColor: dim.colorVar }}
                    />
                  </TooltipTrigger>
                  <TooltipContent className="text-xs">
                    <p className="font-semibold">{label}</p>
                    <p className="text-muted-foreground">
                      {dim.label} x {phase.label}
                    </p>
                    <p className="capitalize">{status.replace("_", " ")}</p>
                  </TooltipContent>
                </Tooltip>
              );
            })}
          </div>
        ))}
      </div>
    </TooltipProvider>
  );
}
