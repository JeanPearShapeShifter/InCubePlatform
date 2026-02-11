"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/stores/auth-store";

interface OrgTabProps {
  settings: {
    monthly_budget_cents: number;
    budget_alert_thresholds: number[];
  };
  onUpdate: (key: string, value: number) => void;
  isAdmin: boolean;
}

export function OrgTab({ settings, onUpdate, isAdmin }: OrgTabProps) {
  const { user, organization } = useAuthStore();

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Organization</CardTitle>
          <CardDescription>Your organization details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Organization Name</Label>
            <p className="text-sm font-medium">{organization?.name ?? "Not available"}</p>
          </div>
          <div className="space-y-2">
            <Label>Organization ID</Label>
            <p className="font-mono text-xs text-muted-foreground">{organization?.id ?? "N/A"}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Members</CardTitle>
          <CardDescription>People in your organization</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {user && (
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <div className="text-sm font-medium">{user.full_name}</div>
                <div className="text-xs text-muted-foreground">{user.email}</div>
              </div>
              <Badge variant="secondary" className="capitalize">{user.role}</Badge>
            </div>
          )}
          {isAdmin && (
            <Button variant="outline" className="w-full" disabled>
              Invite Member (coming soon)
            </Button>
          )}
        </CardContent>
      </Card>

      {isAdmin && (
        <Card>
          <CardHeader>
            <CardTitle>Budget</CardTitle>
            <CardDescription>Set monthly spending limits for API usage</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Monthly Budget ($)</Label>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  className="w-[180px]"
                  value={settings.monthly_budget_cents / 100}
                  onChange={(e) => {
                    const dollars = parseFloat(e.target.value) || 0;
                    onUpdate("monthly_budget_cents", Math.round(dollars * 100));
                  }}
                  min={0}
                  step={1}
                />
                <span className="text-sm text-muted-foreground">per month</span>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Alert Thresholds</Label>
              <p className="text-sm text-muted-foreground">
                Receive alerts at {settings.budget_alert_thresholds.join("%, ")}% of budget
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
