"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiGet } from "@/lib/api";

interface DailyUsage {
  date: string;
  cost_cents: number;
  tokens_in: number;
  tokens_out: number;
}

interface UsageSummary {
  total_cost_cents: number;
  total_tokens_in: number;
  total_tokens_out: number;
  total_calls: number;
  by_date: DailyUsage[];
}

interface UsageEntry {
  name: string;
  cost_cents: number;
  tokens_in: number;
  tokens_out: number;
  call_count: number;
}

interface UsageBreakdown {
  breakdown: UsageEntry[];
}

function formatCost(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

function formatTokens(count: number): string {
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M`;
  if (count >= 1_000) return `${(count / 1_000).toFixed(1)}K`;
  return count.toString();
}

export function UsageTab() {
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  const [breakdown, setBreakdown] = useState<UsageBreakdown | null>(null);
  const [groupBy, setGroupBy] = useState("service");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [summaryRes, breakdownRes] = await Promise.all([
          apiGet<{ data: UsageSummary }>("/api/settings/usage"),
          apiGet<{ data: UsageBreakdown }>(`/api/settings/usage/breakdown?group_by=${groupBy}`),
        ]);
        setSummary(summaryRes.data);
        setBreakdown(breakdownRes.data);
      } catch {
        // API not available yet, show empty state
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [groupBy]);

  const chartData = summary?.by_date.map((d) => ({
    date: d.date,
    cost: d.cost_cents / 100,
  })) ?? [];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Cost</CardDescription>
            <CardTitle className="text-2xl">
              {loading ? "..." : formatCost(summary?.total_cost_cents ?? 0)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>API Calls</CardDescription>
            <CardTitle className="text-2xl">
              {loading ? "..." : (summary?.total_calls ?? 0).toLocaleString()}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Tokens In</CardDescription>
            <CardTitle className="text-2xl">
              {loading ? "..." : formatTokens(summary?.total_tokens_in ?? 0)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Input tokens consumed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Tokens Out</CardDescription>
            <CardTitle className="text-2xl">
              {loading ? "..." : formatTokens(summary?.total_tokens_out ?? 0)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Output tokens generated</p>
          </CardContent>
        </Card>
      </div>

      {/* Daily Cost Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Daily Cost</CardTitle>
          <CardDescription>API costs over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis
                  dataKey="date"
                  className="text-xs"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                />
                <YAxis
                  className="text-xs"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                  tickFormatter={(v) => `$${v}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                  labelStyle={{ color: "hsl(var(--foreground))" }}
                  formatter={(value: number | undefined) => [`$${(value ?? 0).toFixed(2)}`, "Cost"]}
                />
                <Line
                  type="monotone"
                  dataKey="cost"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-[300px] items-center justify-center text-muted-foreground">
              {loading ? "Loading..." : "No usage data available"}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Breakdown Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Usage Breakdown</CardTitle>
              <CardDescription>Detailed usage by category</CardDescription>
            </div>
            <Select value={groupBy} onValueChange={setGroupBy}>
              <SelectTrigger className="w-[160px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="service">By Service</SelectItem>
                <SelectItem value="model">By Model</SelectItem>
                <SelectItem value="endpoint">By Endpoint</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {breakdown && breakdown.breakdown.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-2 font-medium">Name</th>
                    <th className="pb-2 font-medium text-right">Calls</th>
                    <th className="pb-2 font-medium text-right">Tokens In</th>
                    <th className="pb-2 font-medium text-right">Tokens Out</th>
                    <th className="pb-2 font-medium text-right">Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {breakdown.breakdown.map((entry) => (
                    <tr key={entry.name} className="border-b last:border-0">
                      <td className="py-2">
                        <Badge variant="secondary" className="capitalize">
                          {entry.name}
                        </Badge>
                      </td>
                      <td className="py-2 text-right">{entry.call_count.toLocaleString()}</td>
                      <td className="py-2 text-right">{formatTokens(entry.tokens_in)}</td>
                      <td className="py-2 text-right">{formatTokens(entry.tokens_out)}</td>
                      <td className="py-2 text-right font-medium">{formatCost(entry.cost_cents)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-8 text-center text-muted-foreground">
              {loading ? "Loading..." : "No usage data available"}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
