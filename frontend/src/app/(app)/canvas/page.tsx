"use client";

import { Suspense, useEffect, useCallback, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useCanvasStore } from "@/stores/canvas-store";
import { useJourneyStore } from "@/stores/journey-store";
import { LeftRail } from "@/components/canvas/left-rail";
import { PerspectiveHeader } from "@/components/canvas/perspective-header";
import { AgentGrid } from "@/components/canvas/agent-grid";
import { ActionBar } from "@/components/canvas/action-bar";
import { BoomerangPanel } from "@/components/canvas/boomerang-panel";

function CanvasContent() {
  const searchParams = useSearchParams();
  const journeyId = searchParams.get("journey");

  const {
    activeJourneyId,
    setActiveJourneyId,
    activePerspective,
    startBoomerang,
  } = useCanvasStore();
  const { perspectives, fetchPerspectives, activeJourney, setActiveJourney } =
    useJourneyStore();

  const [boomerangOpen, setBoomerangOpen] = useState(false);

  // Sync journey from URL param
  useEffect(() => {
    if (journeyId && journeyId !== activeJourneyId) {
      setActiveJourneyId(journeyId);
      setActiveJourney(journeyId);
      fetchPerspectives(journeyId);
    }
  }, [journeyId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Get the perspective ID for boomerang
  const currentPerspectiveId =
    activePerspective
      ? perspectives.find(
          (p) =>
            p.dimension === activePerspective.dimension &&
            p.phase === activePerspective.phase,
        )?.id ?? null
      : null;

  const handleBoomerang = useCallback(() => {
    if (!currentPerspectiveId) return;
    startBoomerang();
    setBoomerangOpen(true);
  }, [currentPerspectiveId, startBoomerang]);

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <div className="flex flex-1 overflow-hidden">
        {/* Left rail navigation */}
        <LeftRail />

        {/* Main content area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-auto p-6">
            <PerspectiveHeader />
            {activePerspective ? (
              <AgentGrid />
            ) : (
              <div className="flex h-64 items-center justify-center">
                <p className="text-muted-foreground">
                  {activeJourney
                    ? "Select a perspective from the left rail to view agent insights"
                    : "Open a journey from the dashboard to start exploring"}
                </p>
              </div>
            )}
          </div>

          {/* Bottom action bar */}
          <ActionBar onBoomerang={handleBoomerang} />
        </div>
      </div>

      {/* Boomerang execution panel */}
      <BoomerangPanel
        open={boomerangOpen}
        onOpenChange={setBoomerangOpen}
        perspectiveId={currentPerspectiveId}
      />
    </div>
  );
}

export default function CanvasPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-[calc(100vh-3.5rem)] items-center justify-center">
          <p className="text-muted-foreground">Loading canvas...</p>
        </div>
      }
    >
      <CanvasContent />
    </Suspense>
  );
}
