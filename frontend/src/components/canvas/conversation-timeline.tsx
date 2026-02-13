"use client";

import { Badge } from "@/components/ui/badge";
import { useCanvasStore, AGENTS } from "@/stores/canvas-store";
import type { TimelineEvent } from "@/stores/canvas-store";

function getAgentMeta(name: string) {
  return AGENTS.find((a) => a.name === name);
}

function AgentLabel({ name }: { name: string }) {
  const meta = getAgentMeta(name);
  if (!meta) return <span className="font-medium">{name}</span>;
  return (
    <span className="font-medium" style={{ color: meta.colorVar }}>
      {meta.label}
    </span>
  );
}

function TimelineItem({ event }: { event: TimelineEvent }) {
  switch (event.type) {
    case "agent_start":
      return (
        <div className="text-xs text-muted-foreground py-1">
          <AgentLabel name={event.agent} />
          <span className="ml-1">is analyzing...</span>
        </div>
      );

    case "agent_complete":
      return (
        <div className="py-1.5">
          <div className="text-xs">
            <AgentLabel name={event.agent} />
            <span className="ml-1 text-[var(--color-success)]">completed</span>
          </div>
          {event.snippet && (
            <p className="mt-0.5 text-xs text-muted-foreground line-clamp-2">
              {event.snippet}
            </p>
          )}
        </div>
      );

    case "agent_error":
      return (
        <div className="py-1.5">
          <div className="text-xs">
            <AgentLabel name={event.agent} />
            <span className="ml-1 text-[var(--color-error)]">failed</span>
          </div>
          <p className="mt-0.5 text-xs text-[var(--color-error)]/80">
            {event.error}
          </p>
        </div>
      );

    case "phase":
      return (
        <div className="py-2">
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            {event.message}
          </span>
        </div>
      );

    case "axiom_challenge": {
      const axiomMeta = getAgentMeta("axiom");
      return (
        <div
          className="border-l-2 pl-3 py-1.5 my-1"
          style={{ borderColor: axiomMeta?.colorVar }}
        >
          <div className="flex items-center gap-2 text-xs">
            <AgentLabel name="axiom" />
            <span className="text-muted-foreground">
              challenges{" "}
              {event.agents
                .map(
                  (a) => getAgentMeta(a)?.label ?? a,
                )
                .join(", ")}
            </span>
            <Badge
              variant={
                event.severity === "high"
                  ? "destructive"
                  : event.severity === "low"
                    ? "secondary"
                    : "outline"
              }
              className="text-[10px] px-1.5 py-0"
            >
              {event.severity}
            </Badge>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            {event.challengeText}
          </p>
        </div>
      );
    }

    case "challenge_response":
      return (
        <div className="pl-6 py-1 text-xs">
          <AgentLabel name={event.agent} />
          <span className="ml-1 text-muted-foreground">responds:</span>
          <p className="mt-0.5 text-muted-foreground line-clamp-3">
            {event.response}
          </p>
        </div>
      );

    case "axiom_verdict": {
      const axiomMeta = getAgentMeta("axiom");
      const isResolved = event.resolution === "resolved";
      const isActionRequired = event.resolution === "action_required";
      return (
        <div
          className="border-l-2 pl-3 py-1.5 my-1"
          style={{ borderColor: axiomMeta?.colorVar }}
        >
          <div className="flex items-center gap-2 text-xs">
            <AgentLabel name="axiom" />
            <span className="text-muted-foreground">verdict:</span>
            <Badge
              variant={
                isResolved
                  ? "secondary"
                  : isActionRequired
                    ? "destructive"
                    : "outline"
              }
              className="text-[10px] px-1.5 py-0"
            >
              {event.resolution}
            </Badge>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            {event.resolutionText}
          </p>
        </div>
      );
    }
  }
}

export function ConversationTimeline() {
  const timelineEvents = useCanvasStore((s) => s.timelineEvents);

  if (timelineEvents.length === 0) return null;

  return (
    <div className="space-y-0.5">
      {timelineEvents.map((event, i) => (
        <TimelineItem key={i} event={event} />
      ))}
    </div>
  );
}
