"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Loader2, Vault } from "lucide-react";
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
  const [synopsis, setSynopsis] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!synopsis.trim() || !perspectiveId) return;

    setIsSubmitting(true);
    try {
      await apiPost<BankInstance>(
        `/api/perspectives/${perspectiveId}/bank`,
        { synopsis: synopsis.trim() },
      );
      toast.success("Perspective banked successfully");
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
              Save this perspective&apos;s findings to the bank. Write a brief
              synopsis summarizing the key outcomes.
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="bank-synopsis">Synopsis</Label>
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
            <Button type="submit" disabled={isSubmitting || !synopsis.trim()}>
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
