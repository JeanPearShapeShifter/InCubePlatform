"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Download, FileText, FileJson, FileType } from "lucide-react";
import { useRouter } from "next/navigation";
import type { Vdba } from "@/types";

const formatIcons = {
  pdf: FileText,
  json: FileJson,
  docx: FileType,
} as const;

const formatColors: Record<string, string> = {
  pdf: "bg-red-500/10 text-red-500 border-red-500/20",
  json: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  docx: "bg-purple-500/10 text-purple-500 border-purple-500/20",
};

interface VdbaCardProps {
  vdba: Vdba;
}

export function VdbaCard({ vdba }: VdbaCardProps) {
  const router = useRouter();
  const FormatIcon = formatIcons[vdba.export_format] ?? FileText;

  async function handleDownload(e: React.MouseEvent) {
    e.stopPropagation();
    const res = await fetch(`/api/vdbas/${vdba.id}/export`);
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${vdba.title}.${vdba.export_format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <Card
      className="cursor-pointer transition-colors hover:border-primary/50"
      onClick={() => router.push(`/vdbas/${vdba.id}`)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <FormatIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
            <CardTitle className="text-base">{vdba.title}</CardTitle>
          </div>
          <Badge
            variant="outline"
            className={formatColors[vdba.export_format] ?? ""}
          >
            {vdba.export_format.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            Published {new Date(vdba.published_at).toLocaleDateString()}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownload}
          >
            <Download className="mr-1.5 h-3.5 w-3.5" />
            Download
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
