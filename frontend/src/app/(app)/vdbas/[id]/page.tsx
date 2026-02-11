"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Vdba } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Download, FileText, FileJson, FileType } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

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

export default function VdbaDetailPage() {
  const params = useParams<{ id: string }>();

  const { data: vdba, isLoading } = useQuery({
    queryKey: ["vdba", params.id],
    queryFn: () =>
      apiGet<{ data: Vdba }>(`/api/vdbas/${params.id}`).then((res) => res.data),
    enabled: !!params.id,
  });

  async function handleDownload() {
    if (!vdba) return;
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

  if (isLoading) {
    return (
      <div className="p-6 lg:p-8">
        <div className="mb-6">
          <div className="h-5 w-24 animate-pulse rounded bg-muted" />
        </div>
        <Card className="animate-pulse">
          <CardHeader>
            <div className="h-6 w-3/4 rounded bg-muted" />
            <div className="h-4 w-1/2 rounded bg-muted" />
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="h-4 w-full rounded bg-muted" />
            <div className="h-4 w-2/3 rounded bg-muted" />
            <div className="h-10 w-40 rounded bg-muted" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!vdba) {
    return (
      <div className="p-6 lg:p-8">
        <Link
          href="/vdbas"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to VDBAs
        </Link>
        <p className="text-muted-foreground">VDBA not found.</p>
      </div>
    );
  }

  const FormatIcon = formatIcons[vdba.export_format] ?? FileText;

  return (
    <div className="p-6 lg:p-8">
      <Link
        href="/vdbas"
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to VDBAs
      </Link>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <FormatIcon className="h-5 w-5 text-muted-foreground" />
              <CardTitle className="text-xl">{vdba.title}</CardTitle>
            </div>
            <Badge
              variant="outline"
              className={formatColors[vdba.export_format] ?? ""}
            >
              {vdba.export_format.toUpperCase()}
            </Badge>
          </div>
          <CardDescription>
            Published {new Date(vdba.published_at).toLocaleDateString()}
            {" \u00B7 "}Version {vdba.version}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {vdba.description && (
            <p className="text-sm text-muted-foreground">{vdba.description}</p>
          )}

          <Button size="lg" onClick={handleDownload}>
            <Download className="mr-2 h-4 w-4" />
            Download {vdba.export_format.toUpperCase()}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
