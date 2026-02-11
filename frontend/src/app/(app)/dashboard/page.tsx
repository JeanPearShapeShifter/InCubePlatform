"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Journey } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, Rocket } from "lucide-react";
import Link from "next/link";

const statusColors: Record<string, string> = {
  active: "bg-green-500/10 text-green-500 border-green-500/20",
  completed: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  archived: "bg-muted text-muted-foreground border-border",
};

export default function DashboardPage() {
  const { data: journeys, isLoading } = useQuery({
    queryKey: ["journeys"],
    queryFn: () => apiGet<Journey[]>("/api/journeys"),
  });

  return (
    <div className="p-6 lg:p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Your active journeys and transformation progress
          </p>
        </div>
        <Button asChild>
          <Link href="/canvas">
            <Plus className="mr-2 h-4 w-4" />
            New Journey
          </Link>
        </Button>
      </div>

      <section>
        <h2 className="mb-4 text-lg font-semibold">Active Journeys</h2>
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-5 w-3/4 rounded bg-muted" />
                  <div className="h-4 w-1/2 rounded bg-muted" />
                </CardHeader>
                <CardContent>
                  <div className="h-2 w-full rounded bg-muted" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : journeys && journeys.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {journeys.map((journey) => (
              <Link key={journey.id} href={`/canvas?journey=${journey.id}`}>
                <Card className="transition-colors hover:border-primary/50">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-base">
                        {journey.title}
                      </CardTitle>
                      <Badge
                        variant="outline"
                        className={statusColors[journey.status] ?? ""}
                      >
                        {journey.status}
                      </Badge>
                    </div>
                    <CardDescription>
                      Created{" "}
                      {new Date(journey.created_at).toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{ width: "0%" }}
                      />
                    </div>
                    <p className="mt-2 text-xs text-muted-foreground">
                      0 / 12 perspectives completed
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Rocket className="mb-4 h-12 w-12 text-muted-foreground/50" />
              <h3 className="text-lg font-semibold">No journeys yet</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Start your first business transformation journey
              </p>
              <Button className="mt-4" asChild>
                <Link href="/canvas">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Journey
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  );
}
