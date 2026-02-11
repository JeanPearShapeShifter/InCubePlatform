"use client";

import { FolderOpen, Mic, Mail, Rocket, Loader2, Vault } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";
import { useCanvasStore } from "@/stores/canvas-store";

interface ActionBarProps {
  onBoomerang: () => void;
  onDocuments?: () => void;
  onVibe?: () => void;
  onEmail?: () => void;
  onBank?: () => void;
}

export function ActionBar({
  onBoomerang,
  onDocuments,
  onVibe,
  onEmail,
  onBank,
}: ActionBarProps) {
  const isBoomerangRunning = useCanvasStore((s) => s.isBoomerangRunning);
  const activePerspective = useCanvasStore((s) => s.activePerspective);
  const agentOutputs = useCanvasStore((s) => s.agentOutputs);

  // Bank is enabled when there are completed agent outputs and boomerang is not running
  const hasCompletedOutputs =
    Object.values(agentOutputs).some((o) => o.status === "complete") &&
    !isBoomerangRunning;

  const actions = [
    {
      label: "Documents",
      icon: FolderOpen,
      onClick: onDocuments,
      disabled: false,
    },
    {
      label: "Vibe",
      icon: Mic,
      onClick: onVibe,
      disabled: false,
    },
    {
      label: "Email",
      icon: Mail,
      onClick: onEmail,
      disabled: false,
    },
  ];

  return (
    <TooltipProvider delayDuration={200}>
      <div className="flex items-center justify-center gap-2 border-t border-border bg-card px-4 py-3">
        {actions.map((action) => (
          <Tooltip key={action.label}>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                onClick={action.onClick}
                disabled={action.disabled}
                className="gap-2"
              >
                <action.icon className="h-4 w-4" />
                <span className="hidden sm:inline">{action.label}</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>{action.label}</TooltipContent>
          </Tooltip>
        ))}

        <div className="mx-2 h-6 w-px bg-border" />

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={onBoomerang}
              disabled={isBoomerangRunning || !activePerspective}
              className="gap-2"
              size="sm"
            >
              {isBoomerangRunning ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Rocket className="h-4 w-4" />
              )}
              <span>Boomerang</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {activePerspective
              ? "Launch all 9 agents"
              : "Select a perspective first"}
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              onClick={onBank}
              disabled={!hasCompletedOutputs}
              className="gap-2"
              size="sm"
            >
              <Vault className="h-4 w-4" />
              <span className="hidden sm:inline">Bank</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {hasCompletedOutputs
              ? "Bank this perspective's results"
              : "Complete a boomerang first"}
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
}
