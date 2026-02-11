"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Vdba } from "@/types";
import { VdbaCard } from "@/components/vdba/vdba-card";
import { Card, CardContent } from "@/components/ui/card";
import { Globe } from "lucide-react";

export default function VdbasPage() {
  const { data: vdbas, isLoading } = useQuery({
    queryKey: ["vdbas"],
    queryFn: () => apiGet<Vdba[]>("/api/vdbas"),
  });

  return (
    <div className="p-6 lg:p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Published VDBAs</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Your validated digital business assets
        </p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="py-6">
                <div className="h-5 w-3/4 rounded bg-muted" />
                <div className="mt-3 h-4 w-1/2 rounded bg-muted" />
                <div className="mt-3 h-8 w-28 rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : vdbas && vdbas.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {vdbas.map((vdba) => (
            <VdbaCard key={vdba.id} vdba={vdba} />
          ))}
        </div>
      ) : (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Globe className="mb-4 h-12 w-12 text-muted-foreground/50" />
            <h3 className="text-lg font-semibold">No published VDBAs yet</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Complete your transformation journey and publish artefacts to see
              them here.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
