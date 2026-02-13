"use client";

import { useState, useEffect, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Loader2, Vault, RotateCcw, AlertTriangle } from "lucide-react";
import { apiPost } from "@/lib/api";
import type { BankInstance } from "@/types";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useCanvasStore } from "@/stores/canvas-store";

interface SynopsisResponse {
  synopsis: string;
  input_tokens: number;
  output_tokens: number;
}

interface BankDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  perspectiveId: string | null;
}

export function BankDialog({
  open,
  onOpenChange,
  perspectiveId,
}: BankDialogProps) {
  const queryClient = useQueryClient();
  const [synopsis, setSynopsis] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

  const generateSynopsis = useCallback(async () => {
    if (!perspectiveId) return;
    setIsGenerating(true);
    setGenerationError(null);
    try {
      const res = await apiPost<SynopsisResponse>(
        `/api/perspectives/${perspectiveId}/synopsis`,
      );
      setSynopsis(res.synopsis);
    } catch (err) {
      setGenerationError(
        err instanceof Error ? err.message : "Failed to generate synopsis",
      );
    } finally {
      setIsGenerating(false);
    }
  }, [perspectiveId]);

  // Auto-generate synopsis on dialog open
  useEffect(() => {
    if (open && perspectiveId) {
      setSynopsis("");
      setGenerationError(null);
      generateSynopsis();
    }
    if (!open) {
      setSynopsis("");
      setIsGenerating(false);
      setGenerationError(null);
    }
  }, [open, perspectiveId, generateSynopsis]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!synopsis.trim() || !perspectiveId) return;

    setIsSubmitting(true);
    try {
      // Extract agent_assessments and decision_audit from store
      const { agentOutputs, timelineEvents } = useCanvasStore.getState();

      const agentAssessments: Record<
        string,
        { summary: string; confidence: number; key_findings: string[] }
      > = {};
      for (const [name, output] of Object.entries(agentOutputs)) {
        if (output.status === "complete" && output.content) {
          agentAssessments[name] = {
            summary: output.content.slice(0, 300),
            confidence: output.content.length > 500 ? 0.8 : 0.5,
            key_findings: [],
          };
        }
      }

      const decisionAudit: {
        challenge: string;
        resolution: string;
        evidence: string;
        agents: string[];
        timestamp: string;
      }[] = [];
      for (const event of timelineEvents) {
        if (event.type === "axiom_verdict") {
          decisionAudit.push({
            challenge: "",
            resolution: event.resolution,
            evidence: event.resolutionText,
            agents: [],
            timestamp: new Date(event.timestamp).toISOString(),
          });
        }
      }

      await apiPost<BankInstance>(
        `/api/perspectives/${perspectiveId}/bank`,
        {
          synopsis: synopsis.trim(),
          agent_assessments:
            Object.keys(agentAssessments).length > 0
              ? agentAssessments
              : undefined,
          decision_audit:
            decisionAudit.length > 0 ? decisionAudit : undefined,
        },
      );
      toast.success("Perspective banked successfully");
      queryClient.invalidateQueries({ queryKey: ["bank-timeline"] });
      setSynopsis("");
      onOpenChange(false);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to bank perspective",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Vault className="h-5 w-5" />
              Bank Perspective
            </DialogTitle>
            <DialogDescription>
              Auto-generated from agent analysis. Review and edit before banking.
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="bank-synopsis">Synopsis</Label>
              {isGenerating ? (
                <div className="flex min-h-[120px] w-full items-center justify-center rounded-md border border-input bg-muted/50">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating synopsis...
                  </div>
                </div>
              ) : (
                <textarea
                  id="bank-synopsis"
                  className="border-input bg-background placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 flex min-h-[120px] w-full rounded-md border px-3 py-2 text-sm shadow-xs focus-visible:ring-[3px] focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="Summarize the key findings and outcomes from this perspective..."
                  value={synopsis}
                  onChange={(e) => setSynopsis(e.target.value)}
                  disabled={isSubmitting}
                  required
                  autoFocus
                />
              )}
              {generationError && (
                <div className="flex items-center gap-1.5 text-xs text-[var(--color-error)]">
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                  {generationError}
                </div>
              )}
              {!isGenerating && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={generateSynopsis}
                  disabled={isSubmitting}
                  className="flex items-center gap-1.5"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  Regenerate
                </Button>
              )}
            </div>
          </div>
          <DialogFooter className="mt-6">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting || isGenerating || !synopsis.trim()}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Banking...
                </>
              ) : (
                <>
                  <Vault className="mr-2 h-4 w-4" />
                  Bank
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
