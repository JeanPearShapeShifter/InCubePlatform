"use client";

import { BankCard } from "@/components/bank/bank-card";
import type { BankInstance } from "@/types";

interface TimelineProps {
  instances: BankInstance[];
}

export function BankTimeline({ instances }: TimelineProps) {
  if (instances.length === 0) {
    return null;
  }

  return (
    <div className="relative">
      {/* Vertical timeline line */}
      <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />

      <div className="space-y-6">
        {instances.map((instance) => (
          <div key={instance.id} className="relative pl-10">
            {/* Timeline dot */}
            <div className="absolute left-2.5 top-6 h-3 w-3 rounded-full border-2 border-primary bg-background" />

            {/* Date label */}
            <time className="mb-2 block text-xs text-muted-foreground">
              {new Date(instance.created_at).toLocaleDateString(undefined, {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </time>

            <BankCard instance={instance} />
          </div>
        ))}
      </div>
    </div>
  );
}
