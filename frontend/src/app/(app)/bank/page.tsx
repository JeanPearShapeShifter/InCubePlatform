"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { BankTimelineResponse, BankType, Journey } from "@/types";
import { BankTimeline } from "@/components/bank/timeline";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Vault, Filter } from "lucide-react";

const typeFilters: { value: BankType | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "bankable", label: "Bankable" },
  { value: "film", label: "Film" },
  { value: "film_reel", label: "Film Reel" },
  { value: "published", label: "Published" },
];

export default function BankPage() {
  const [selectedJourneyId, setSelectedJourneyId] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<BankType | "all">("all");

  const { data: journeys, isLoading: journeysLoading } = useQuery({
    queryKey: ["journeys"],
    queryFn: () => apiGet<Journey[]>("/api/journeys"),
  });

  // Auto-select the first journey if none selected
  const activeJourneyId = selectedJourneyId ?? journeys?.[0]?.id ?? null;

  const { data: bankData, isLoading: bankLoading } = useQuery({
    queryKey: ["bank-timeline", activeJourneyId],
    queryFn: () =>
      apiGet<BankTimelineResponse>(`/api/journeys/${activeJourneyId}/bank`),
    enabled: !!activeJourneyId,
  });

  const filteredInstances = bankData?.bank_instances.filter(
    (instance) => typeFilter === "all" || instance.type === typeFilter,
  ) ?? [];

  const isLoading = journeysLoading || bankLoading;

  return (
    <div className="p-6 lg:p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Bank</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Timeline of banked artefacts from your transformation journeys
        </p>
      </div>

      {/* Journey selector */}
      {journeys && journeys.length > 1 && (
        <div className="mb-6">
          <label htmlFor="journey-select" className="mb-1.5 block text-sm font-medium">
            Journey
          </label>
          <select
            id="journey-select"
            value={activeJourneyId ?? ""}
            onChange={(e) => setSelectedJourneyId(e.target.value)}
            className="rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          >
            {journeys.map((journey) => (
              <option key={journey.id} value={journey.id}>
                {journey.title}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Type filter */}
      <div className="mb-6 flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <div className="flex flex-wrap gap-1.5">
          {typeFilters.map((filter) => (
            <button
              key={filter.value}
              type="button"
              onClick={() => setTypeFilter(filter.value)}
              className="focus:outline-none"
            >
              <Badge
                variant={typeFilter === filter.value ? "default" : "outline"}
                className="cursor-pointer transition-colors"
              >
                {filter.label}
              </Badge>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="py-6">
                <div className="h-4 w-3/4 rounded bg-muted" />
                <div className="mt-3 h-3 w-1/2 rounded bg-muted" />
                <div className="mt-3 h-3 w-1/3 rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredInstances.length > 0 ? (
        <BankTimeline instances={filteredInstances} />
      ) : (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Vault className="mb-4 h-12 w-12 text-muted-foreground/50" />
            <h3 className="text-lg font-semibold">No banked artefacts</h3>
            <p className="mt-1 text-center text-sm text-muted-foreground">
              {typeFilter !== "all"
                ? `No ${typeFilter.replace("_", " ")} artefacts found. Try changing the filter.`
                : "Complete perspectives and bank them to see artefacts here."}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
