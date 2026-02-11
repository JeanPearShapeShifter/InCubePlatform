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
import { useThemeStore, type Theme } from "@/stores/theme-store";

const THEMES: { value: Theme; label: string; description: string }[] = [
  { value: "space", label: "Space", description: "Deep blue cosmic theme" },
  { value: "forest", label: "Forest", description: "Natural green tones" },
  { value: "blackhole", label: "Black Hole", description: "Warm amber accents" },
];

const EXPORT_FORMATS = [
  { value: "pdf", label: "PDF" },
  { value: "docx", label: "DOCX" },
  { value: "json", label: "JSON" },
];

interface GeneralTabProps {
  settings: {
    theme: string;
    export_format: string;
  };
  onUpdate: (key: string, value: string) => void;
}

export function GeneralTab({ settings, onUpdate }: GeneralTabProps) {
  const { setTheme } = useThemeStore();

  const handleThemeChange = (value: string) => {
    setTheme(value as Theme);
    onUpdate("theme", value);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize the visual theme of the platform</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Theme</Label>
            <Select value={settings.theme} onValueChange={handleThemeChange}>
              <SelectTrigger className="w-[240px]">
                <SelectValue placeholder="Select theme" />
              </SelectTrigger>
              <SelectContent>
                {THEMES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    <div>
                      <div>{t.label}</div>
                      <div className="text-xs text-muted-foreground">{t.description}</div>
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
          <CardTitle>Export</CardTitle>
          <CardDescription>Default format for VDBA and document exports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label>Export Format</Label>
            <Select value={settings.export_format} onValueChange={(v) => onUpdate("export_format", v)}>
              <SelectTrigger className="w-[240px]">
                <SelectValue placeholder="Select format" />
              </SelectTrigger>
              <SelectContent>
                {EXPORT_FORMATS.map((f) => (
                  <SelectItem key={f.value} value={f.value}>
                    {f.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
