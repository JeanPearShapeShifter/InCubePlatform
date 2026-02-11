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
import { Slider } from "@/components/ui/slider";

const VOICE_PROVIDERS = [
  { value: "whisper", label: "OpenAI Whisper", description: "High accuracy, moderate speed" },
  { value: "deepgram", label: "Deepgram", description: "Fast processing, real-time capable" },
  { value: "assemblyai", label: "AssemblyAI", description: "Best-in-class accuracy" },
];

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "es", label: "Spanish" },
  { value: "fr", label: "French" },
  { value: "de", label: "German" },
  { value: "pt", label: "Portuguese" },
  { value: "ja", label: "Japanese" },
  { value: "zh", label: "Chinese" },
];

interface VoiceTabProps {
  settings: {
    voice_provider: string;
    voice_language: string;
  };
  onUpdate: (key: string, value: string) => void;
}

export function VoiceTab({ settings, onUpdate }: VoiceTabProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Voice Provider</CardTitle>
          <CardDescription>Speech-to-text service for vibe sessions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Provider</Label>
            <Select value={settings.voice_provider} onValueChange={(v) => onUpdate("voice_provider", v)}>
              <SelectTrigger className="w-[280px]">
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent>
                {VOICE_PROVIDERS.map((p) => (
                  <SelectItem key={p.value} value={p.value}>
                    <div>
                      <div>{p.label}</div>
                      <div className="text-xs text-muted-foreground">{p.description}</div>
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
          <CardTitle>Language</CardTitle>
          <CardDescription>Primary language for voice recognition</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label>Language</Label>
            <Select value={settings.voice_language} onValueChange={(v) => onUpdate("voice_language", v)}>
              <SelectTrigger className="w-[240px]">
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((l) => (
                  <SelectItem key={l.value} value={l.value}>
                    {l.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Quality / Speed Tradeoff</CardTitle>
          <CardDescription>
            Balance between transcription accuracy and processing speed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>Faster</span>
              <span>More Accurate</span>
            </div>
            <Slider defaultValue={[75]} max={100} step={5} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
