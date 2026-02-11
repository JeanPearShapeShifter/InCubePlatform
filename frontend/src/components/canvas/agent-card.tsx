"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { AgentOutput } from "@/stores/canvas-store";
import { AGENTS } from "@/stores/canvas-store";
import type { AgentName } from "@/types";

interface AgentCardProps {
  agentName: AgentName;
  output?: AgentOutput;
}

export function AgentCard({ agentName, output }: AgentCardProps) {
  const [expanded, setExpanded] = useState(false);
  const meta = AGENTS.find((a) => a.name === agentName);
  if (!meta) return null;

  const isAxiom = agentName === "axiom";
  const status = output?.status ?? "pending";

  return (
    <Card
      role="article"
      aria-label={`Agent ${meta.label} — ${meta.role}`}
      className={cn(
        "flex flex-col overflow-hidden transition-all",
        isAxiom && "border-[var(--color-agent-axiom)]",
        expanded && "row-span-2",
      )}
    >
      <CardHeader className="flex flex-row items-center gap-2 space-y-0 p-3 pb-2">
        <div
          className="h-3 w-3 rounded-full shrink-0"
          style={{ backgroundColor: meta.colorVar }}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm">{meta.label}</span>
            {isAxiom && (
              <Badge variant="outline" className="text-[10px] h-4 border-[var(--color-agent-axiom)] text-[var(--color-agent-axiom)]">
                Challenger
              </Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground">{meta.role}</p>
        </div>
        {status === "running" && (
          <Loader2 className="h-4 w-4 animate-spin text-primary" />
        )}
        {status === "complete" && (
          <Badge variant="secondary" className="text-[10px] h-4">
            Done
          </Badge>
        )}
      </CardHeader>

      <CardContent className="flex-1 px-3 py-0">
        {output?.content ? (
          expanded ? (
            <ScrollArea className="h-40">
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {output.content}
              </p>
            </ScrollArea>
          ) : (
            <p className="text-sm text-muted-foreground line-clamp-3">
              {output.content}
            </p>
          )
        ) : (
          <p className="text-xs text-muted-foreground italic">
            {status === "running"
              ? "Analyzing..."
              : "No output yet"}
          </p>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between p-3 pt-2">
        {output && output.status === "complete" ? (
          <span className="text-[10px] text-muted-foreground">
            {output.inputTokens + output.outputTokens} tokens
            {" / "}${output.costUsd.toFixed(4)}
          </span>
        ) : (
          <span />
        )}
        {output?.content && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2 text-xs"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? (
              <>
                <ChevronUp className="mr-1 h-3 w-3" /> Less
              </>
            ) : (
              <>
                <ChevronDown className="mr-1 h-3 w-3" /> More
              </>
            )}
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
