"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { ChevronDown, ChevronRight, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import type { DecisionAuditEntry } from "@/types";

const resolutionConfig: Record<string, { label: string; className: string; icon: typeof CheckCircle }> = {
  resolved: {
    label: "Resolved",
    className: "bg-green-500/10 text-green-500 border-green-500/20",
    icon: CheckCircle,
  },
  accepted_risk: {
    label: "Accepted Risk",
    className: "bg-amber-500/10 text-amber-500 border-amber-500/20",
    icon: AlertTriangle,
  },
  action_required: {
    label: "Action Required",
    className: "bg-red-500/10 text-red-500 border-red-500/20",
    icon: Clock,
  },
};

interface DecisionAuditProps {
  entries: DecisionAuditEntry[];
}

export function DecisionAudit({ entries }: DecisionAuditProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (entries.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No decision audit entries recorded.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {entries.map((entry, index) => {
        const isExpanded = expandedIndex === index;
        const resolution = resolutionConfig[entry.resolution] ?? resolutionConfig.action_required;
        const ResolutionIcon = resolution.icon;

        return (
          <div
            key={index}
            className="rounded-lg border bg-card"
          >
            <button
              type="button"
              className="flex w-full items-start gap-3 p-3 text-left"
              onClick={() => setExpandedIndex(isExpanded ? null : index)}
            >
              <span className="mt-0.5 shrink-0 text-muted-foreground">
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium leading-snug">
                  {entry.challenge}
                </p>
                <div className="mt-1.5 flex flex-wrap items-center gap-2">
                  <Badge variant="outline" className={resolution.className}>
                    <ResolutionIcon className="h-3 w-3" />
                    {resolution.label}
                  </Badge>
                  {entry.agents.length > 0 && (
                    <span className="text-xs text-muted-foreground">
                      {entry.agents.join(", ")}
                    </span>
                  )}
                </div>
              </div>
            </button>

            {isExpanded && entry.evidence && (
              <div className="border-t px-3 pb-3 pt-2">
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {entry.evidence}
                </p>
                {entry.timestamp && (
                  <p className="mt-2 text-xs text-muted-foreground/70">
                    {new Date(entry.timestamp).toLocaleString()}
                  </p>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
