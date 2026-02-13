"use client";

import { Suspense, useEffect, useCallback, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useCanvasStore } from "@/stores/canvas-store";
import { useJourneyStore } from "@/stores/journey-store";
import { LeftRail } from "@/components/canvas/left-rail";
import { PerspectiveHeader } from "@/components/canvas/perspective-header";
import { AgentGrid } from "@/components/canvas/agent-grid";
import { ActionBar } from "@/components/canvas/action-bar";
import { BankDialog } from "@/components/canvas/bank-dialog";
import { BoomerangPanel } from "@/components/canvas/boomerang-panel";
import { Button } from "@/components/ui/button";

function CanvasContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const journeyId = searchParams.get("journey");

  const {
    activeJourneyId,
    setActiveJourneyId,
    activePerspective,
    startBoomerang,
  } = useCanvasStore();
  const {
    perspectives,
    fetchPerspectives,
    activeJourney,
    fetchAndSetActiveJourney,
    isLoading,
    updatePerspectiveStatus,
  } = useJourneyStore();

  const [boomerangOpen, setBoomerangOpen] = useState(false);
  const [bankDialogOpen, setBankDialogOpen] = useState(false);

  // Sync journey from URL param, or restore from store
  useEffect(() => {
    if (journeyId && journeyId !== activeJourneyId) {
      setActiveJourneyId(journeyId);
      fetchAndSetActiveJourney(journeyId).then(() => {
        fetchPerspectives(journeyId);
      });
    } else if (!journeyId && activeJourney) {
      // No journey in URL but we have one in store — restore it
      router.replace(`/canvas?journey=${activeJourney.id}`);
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
    // Mark perspective as in_progress
    updatePerspectiveStatus(currentPerspectiveId, "in_progress").then(() => {
      if (journeyId) fetchPerspectives(journeyId);
    });
    startBoomerang();
    setBoomerangOpen(true);
  }, [currentPerspectiveId, startBoomerang, updatePerspectiveStatus, journeyId, fetchPerspectives]);

  // No journey param — show a prompt to go to the dashboard
  if (!journeyId) {
    return (
      <div className="flex h-[calc(100vh-3.5rem)] items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-muted-foreground">
            No journey selected. Open or create a journey from the dashboard to get started.
          </p>
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  // Loading state while fetching journey
  if (isLoading && !activeJourney) {
    return (
      <div className="flex h-[calc(100vh-3.5rem)] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

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
          <ActionBar
            onBoomerang={handleBoomerang}
            onBank={() => setBankDialogOpen(true)}
          />
        </div>
      </div>

      {/* Boomerang execution panel */}
      <BoomerangPanel
        open={boomerangOpen}
        onOpenChange={setBoomerangOpen}
        perspectiveId={currentPerspectiveId}
      />

      {/* Bank dialog */}
      <BankDialog
        open={bankDialogOpen}
        onOpenChange={setBankDialogOpen}
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
