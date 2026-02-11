"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { DashboardStats, Journey } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { StatCard } from "@/components/dashboard/stat-card";
import { Plus, Rocket, Briefcase, Zap, Globe, DollarSign, FileText } from "lucide-react";
import Link from "next/link";

const statusColors: Record<string, string> = {
  active: "bg-green-500/10 text-green-500 border-green-500/20",
  completed: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  archived: "bg-muted text-muted-foreground border-border",
};

const formatColors: Record<string, string> = {
  pdf: "bg-red-500/10 text-red-500 border-red-500/20",
  json: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  docx: "bg-purple-500/10 text-purple-500 border-purple-500/20",
};

export default function DashboardPage() {
  const { data: journeys, isLoading: journeysLoading } = useQuery({
    queryKey: ["journeys"],
    queryFn: () =>
      apiGet<{ journeys: Journey[]; pagination: unknown }>("/api/journeys").then(
        (res) => res.journeys,
      ),
  });

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () =>
      apiGet<{ data: DashboardStats }>("/api/analytics/dashboard").then(
        (res) => res.data,
      ),
  });

  const isLoading = journeysLoading || statsLoading;

  function formatCost(cents: number): string {
    return `$${(cents / 100).toFixed(2)}`;
  }

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

      {/* Stats row */}
      <section className="mb-8">
        {statsLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="py-4">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-muted" />
                    <div>
                      <div className="h-6 w-16 rounded bg-muted" />
                      <div className="mt-1 h-4 w-24 rounded bg-muted" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : stats ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              title="Total Journeys"
              value={stats.total_journeys}
              icon={Briefcase}
            />
            <StatCard
              title="Active Journeys"
              value={stats.active_journeys}
              icon={Zap}
            />
            <StatCard
              title="Published VDBAs"
              value={stats.total_vdbas}
              icon={Globe}
            />
            <StatCard
              title="Total Cost"
              value={formatCost(stats.total_cost_cents)}
              icon={DollarSign}
            />
          </div>
        ) : null}
      </section>

      {/* Active Journeys */}
      <section className="mb-8">
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
            {journeys.map((journey) => {
              const progressPct = (journey.perspectives_completed / 12) * 100;

              return (
                <Link
                  key={journey.id}
                  href={`/canvas?journey=${journey.id}`}
                >
                  <Card className="transition-colors hover:border-primary/50">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-base">
                          Journey
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
                      <Progress value={progressPct} />
                      <p className="mt-2 text-xs text-muted-foreground">
                        {journey.perspectives_completed} / 12 perspectives completed
                      </p>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
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

      {/* Recent VDBAs */}
      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recent VDBAs</h2>
          <Link
            href="/vdbas"
            className="text-sm text-primary hover:underline"
          >
            View all
          </Link>
        </div>
        {statsLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="flex items-center gap-4 py-4">
                  <div className="h-8 w-8 rounded bg-muted" />
                  <div className="flex-1">
                    <div className="h-4 w-1/3 rounded bg-muted" />
                    <div className="mt-2 h-3 w-1/4 rounded bg-muted" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : stats && stats.recent_vdbas.length > 0 ? (
          <div className="space-y-3">
            {stats.recent_vdbas.slice(0, 5).map((vdba) => (
              <Link key={vdba.id} href={`/vdbas/${vdba.id}`}>
                <Card className="transition-colors hover:border-primary/50">
                  <CardContent className="flex items-center gap-4 py-4">
                    <FileText className="h-5 w-5 shrink-0 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{vdba.title}</p>
                      <p className="text-xs text-muted-foreground">
                        Published{" "}
                        {new Date(vdba.published_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge
                      variant="outline"
                      className={formatColors[vdba.export_format] ?? ""}
                    >
                      {vdba.export_format.toUpperCase()}
                    </Badge>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-8">
              <Globe className="mb-3 h-8 w-8 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">
                No published VDBAs yet
              </p>
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  );
}
