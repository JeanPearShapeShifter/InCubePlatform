"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  ChevronDown,
  ChevronRight,
  FileText,
  Mic,
  Layers,
  Film,
  BookOpen,
  Globe,
} from "lucide-react";
import { DecisionAudit } from "@/components/bank/decision-audit";
import type { BankInstance, DimensionType } from "@/types";

const typeConfig: Record<string, { label: string; icon: typeof FileText; className: string }> = {
  bankable: {
    label: "Bankable",
    icon: Layers,
    className: "bg-green-500/10 text-green-500 border-green-500/20",
  },
  film: {
    label: "Film",
    icon: Film,
    className: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  },
  film_reel: {
    label: "Film Reel",
    icon: BookOpen,
    className: "bg-amber-500/10 text-amber-500 border-amber-500/20",
  },
  published: {
    label: "Published VDBA",
    icon: Globe,
    className: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  },
};

const dimensionColors: Record<DimensionType, string> = {
  architecture: "border-l-[var(--color-dim-architecture)]",
  design: "border-l-[var(--color-dim-design)]",
  engineering: "border-l-[var(--color-dim-engineering)]",
};

interface BankCardProps {
  instance: BankInstance;
  dimension?: DimensionType;
  phase?: string;
}

export function BankCard({ instance, dimension, phase }: BankCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const config = typeConfig[instance.type] ?? typeConfig.bankable;
  const TypeIcon = config.icon;

  const agentNames = Object.keys(instance.agent_assessments);
  const hasAudit = instance.decision_audit.length > 0;
  const hasAssessments = agentNames.length > 0;
  const borderClass = dimension ? dimensionColors[dimension] : "";

  return (
    <Card className={`border-l-4 ${borderClass}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <TypeIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
            <CardTitle className="text-sm font-medium leading-snug">
              {instance.synopsis.length > 120
                ? `${instance.synopsis.slice(0, 120)}...`
                : instance.synopsis}
            </CardTitle>
          </div>
          <Badge variant="outline" className={config.className}>
            {config.label}
          </Badge>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
          {dimension && phase && (
            <span className="capitalize">
              {dimension} / {phase}
            </span>
          )}
          <span>{new Date(instance.created_at).toLocaleDateString()}</span>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Stats row */}
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <FileText className="h-3 w-3" />
            {instance.documents_count} doc{instance.documents_count !== 1 ? "s" : ""}
          </span>
          <span className="flex items-center gap-1">
            <Mic className="h-3 w-3" />
            {instance.vibes_count} vibe{instance.vibes_count !== 1 ? "s" : ""}
          </span>
        </div>

        {/* Agent assessment chips */}
        {hasAssessments && (
          <div className="flex flex-wrap gap-1.5">
            {agentNames.map((name) => {
              const assessment = instance.agent_assessments[name];
              return (
                <Badge key={name} variant="secondary" className="text-xs capitalize">
                  {name}
                  <span className="ml-1 opacity-60">
                    {Math.round(assessment.confidence * 100)}%
                  </span>
                </Badge>
              );
            })}
          </div>
        )}

        {/* Expandable section */}
        {(hasAudit || hasAssessments) && (
          <>
            <Separator />
            <button
              type="button"
              className="flex w-full items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronDown className="h-3.5 w-3.5" />
              ) : (
                <ChevronRight className="h-3.5 w-3.5" />
              )}
              {hasAudit
                ? `${instance.decision_audit.length} decision audit entr${instance.decision_audit.length === 1 ? "y" : "ies"}`
                : "Agent assessments"}
            </button>

            {isExpanded && (
              <div className="space-y-4 pt-1">
                {hasAudit && (
                  <div>
                    <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Decision Audit
                    </h4>
                    <DecisionAudit entries={instance.decision_audit} />
                  </div>
                )}

                {hasAssessments && (
                  <div>
                    <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Agent Assessments
                    </h4>
                    <div className="space-y-2">
                      {agentNames.map((name) => {
                        const assessment = instance.agent_assessments[name];
                        return (
                          <div key={name} className="rounded-lg border bg-card p-3">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium capitalize">{name}</span>
                              <span className="text-xs text-muted-foreground">
                                {Math.round(assessment.confidence * 100)}% confidence
                              </span>
                            </div>
                            <p className="mt-1 text-xs text-muted-foreground">
                              {assessment.summary}
                            </p>
                            {assessment.key_findings.length > 0 && (
                              <ul className="mt-2 space-y-0.5">
                                {assessment.key_findings.map((finding, i) => (
                                  <li key={i} className="text-xs text-muted-foreground">
                                    - {finding}
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
