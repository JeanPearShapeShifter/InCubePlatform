"use client";

import { Badge } from "@/components/ui/badge";
import {
  useCanvasStore,
  DIMENSIONS,
  PHASES,
  INTERSECTION_LABELS,
  STATUS_CONFIG,
} from "@/stores/canvas-store";
import { useJourneyStore } from "@/stores/journey-store";
import type { PerspectiveStatus } from "@/types";

export function PerspectiveHeader() {
  const activePerspective = useCanvasStore((s) => s.activePerspective);
  const perspectives = useJourneyStore((s) => s.perspectives);

  if (!activePerspective) {
    return (
      <div className="px-1 py-4">
        <h2 className="text-lg font-semibold text-muted-foreground">
          Select a perspective to begin
        </h2>
      </div>
    );
  }

  const dim = DIMENSIONS.find((d) => d.type === activePerspective.dimension);
  const phase = PHASES.find((p) => p.type === activePerspective.phase);
  const intersectionLabel =
    INTERSECTION_LABELS[activePerspective.dimension][activePerspective.phase];

  const perspective = perspectives.find(
    (p) =>
      p.dimension === activePerspective.dimension &&
      p.phase === activePerspective.phase,
  );
  const status: PerspectiveStatus = perspective?.status ?? "locked";
  const statusConfig = STATUS_CONFIG[status];

  return (
    <div className="flex items-center gap-4 px-1 py-4">
      <div
        className="h-8 w-1 rounded-full"
        style={{ backgroundColor: dim?.colorVar }}
      />
      <div className="flex-1">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold">{intersectionLabel}</h2>
          <Badge variant="outline" className={statusConfig.className}>
            {statusConfig.label}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          {dim?.label} <span className="mx-1 text-muted-foreground/50">x</span>{" "}
          {phase?.label}
        </p>
      </div>
    </div>
  );
}
