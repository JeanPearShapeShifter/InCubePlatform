"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AgentName } from "@/types";

const MODELS = [
  { value: "claude-haiku-4-5-20251001", label: "Claude Haiku", cost: "$0.25/1M in, $1.25/1M out" },
  { value: "claude-sonnet-4-5-20250929", label: "Claude Sonnet", cost: "$3/1M in, $15/1M out" },
];

const AGENTS: { name: AgentName; label: string; role: string }[] = [
  { name: "lyra", label: "Lyra", role: "Architecture - Generate" },
  { name: "mira", label: "Mira", role: "Architecture - Review" },
  { name: "dex", label: "Dex", role: "Design - Generate" },
  { name: "rex", label: "Rex", role: "Design - Review" },
  { name: "vela", label: "Vela", role: "Engineering - Generate" },
  { name: "koda", label: "Koda", role: "Engineering - Review" },
  { name: "halo", label: "Halo", role: "Synthesis" },
  { name: "nova", label: "Nova", role: "Validation" },
  { name: "axiom", label: "Axiom", role: "Adversarial Reviewer" },
];

interface ModelsTabProps {
  settings: {
    default_model: string;
  };
  onUpdate: (key: string, value: string) => void;
}

export function ModelsTab({ settings, onUpdate }: ModelsTabProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Default Model</CardTitle>
          <CardDescription>
            The AI model used for all agents unless overridden below
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label>Model</Label>
            <Select value={settings.default_model} onValueChange={(v) => onUpdate("default_model", v)}>
              <SelectTrigger className="w-[320px]">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                {MODELS.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    <div className="flex items-center justify-between gap-4">
                      <span>{m.label}</span>
                      <span className="text-xs text-muted-foreground">{m.cost}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Per-Agent Overrides</CardTitle>
          <CardDescription>
            Override the model for specific agents. Leave as default to use the model selected above.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {AGENTS.map((agent) => (
              <div key={agent.name} className="flex items-center gap-4">
                <div className="w-[200px]">
                  <div className="text-sm font-medium capitalize">{agent.label}</div>
                  <div className="text-xs text-muted-foreground">{agent.role}</div>
                </div>
                <Select defaultValue="default">
                  <SelectTrigger className="w-[240px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Use default</SelectItem>
                    {MODELS.map((m) => (
                      <SelectItem key={m.value} value={m.value}>
                        {m.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
