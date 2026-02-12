"use client";

import { useCallback, useEffect, useState } from "react";
import { Settings, Cpu, Mic, BarChart3, Building2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GeneralTab } from "@/components/settings/general-tab";
import { ModelsTab } from "@/components/settings/models-tab";
import { VoiceTab } from "@/components/settings/voice-tab";
import { UsageTab } from "@/components/settings/usage-tab";
import { OrgTab } from "@/components/settings/org-tab";
import { useAuthStore } from "@/stores/auth-store";
import { apiGet, apiPut } from "@/lib/api";

interface OrgSettings {
  default_model: string;
  anthropic_api_key: string;
  voice_provider: string;
  voice_language: string;
  theme: string;
  export_format: string;
  monthly_budget_cents: number;
  budget_alert_thresholds: number[];
}

const DEFAULT_SETTINGS: OrgSettings = {
  default_model: "claude-haiku-4-5-20251001",
  anthropic_api_key: "",
  voice_provider: "whisper",
  voice_language: "en",
  theme: "space",
  export_format: "pdf",
  monthly_budget_cents: 0,
  budget_alert_thresholds: [50, 80, 100],
};

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [settings, setSettings] = useState<OrgSettings>(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(true);
  const isAdmin = user?.role === "admin";

  useEffect(() => {
    async function fetchSettings() {
      try {
        const res = await apiGet<{ data: OrgSettings }>("/api/settings");
        setSettings(res.data);
      } catch {
        // API not available yet, use defaults
      } finally {
        setLoading(false);
      }
    }
    fetchSettings();
  }, []);

  const handleUpdate = useCallback(async (key: string, value: string | number | number[]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    try {
      await apiPut("/api/settings", { key, value });
    } catch {
      // Revert on failure could be added here
    }
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <p className="text-muted-foreground">Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="mt-1 text-muted-foreground">
          Manage your platform configuration, AI models, and organization
        </p>
      </div>

      <Tabs defaultValue="general" className="w-full">
        <TabsList>
          <TabsTrigger value="general" className="gap-1.5">
            <Settings className="size-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="models" className="gap-1.5">
            <Cpu className="size-4" />
            AI Models
          </TabsTrigger>
          <TabsTrigger value="voice" className="gap-1.5">
            <Mic className="size-4" />
            Voice
          </TabsTrigger>
          <TabsTrigger value="usage" className="gap-1.5">
            <BarChart3 className="size-4" />
            Usage
          </TabsTrigger>
          <TabsTrigger value="org" className="gap-1.5">
            <Building2 className="size-4" />
            Organization
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general">
          <GeneralTab settings={settings} onUpdate={handleUpdate} />
        </TabsContent>

        <TabsContent value="models">
          <ModelsTab settings={settings} onUpdate={handleUpdate} />
        </TabsContent>

        <TabsContent value="voice">
          <VoiceTab settings={settings} onUpdate={handleUpdate} />
        </TabsContent>

        <TabsContent value="usage">
          <UsageTab />
        </TabsContent>

        <TabsContent value="org">
          <OrgTab settings={settings} onUpdate={handleUpdate} isAdmin={isAdmin} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
