// InCube Platform — TypeScript type definitions

// Enums matching backend
export type UserRole = "admin" | "editor" | "viewer";
export type GoalType = "predefined" | "custom";
export type JourneyStatus = "active" | "completed" | "archived";
export type DimensionType = "architecture" | "design" | "engineering";
export type PhaseType = "generate" | "review" | "validate" | "summarize";
export type PerspectiveStatus = "locked" | "pending" | "in_progress" | "completed";
export type ChallengeSeverity = "high" | "medium" | "low";
export type ChallengeResolution = "resolved" | "accepted_risk" | "action_required";
export type BankType = "bankable" | "film" | "film_reel" | "published";

// Agent names
export type AgentName =
  | "lyra"
  | "mira"
  | "dex"
  | "rex"
  | "vela"
  | "koda"
  | "halo"
  | "nova"
  | "axiom";

// Core entities
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  organization_id: string;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface Journey {
  id: string;
  title: string;
  status: JourneyStatus;
  goal_id: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export interface Goal {
  id: string;
  type: GoalType;
  title: string;
  description: string;
  organization_id: string;
  created_at: string;
}

export interface Perspective {
  id: string;
  journey_id: string;
  dimension: DimensionType;
  phase: PhaseType;
  status: PerspectiveStatus;
  created_at: string;
  updated_at: string;
}

export interface AgentSession {
  id: string;
  perspective_id: string;
  agent_name: AgentName;
  model_used: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  started_at: string;
  completed_at: string | null;
}

export interface AgentAssessment {
  summary: string;
  confidence: number;
  key_findings: string[];
}

export interface DecisionAuditEntry {
  challenge: string;
  resolution: ChallengeResolution | string;
  evidence: string;
  agents: string[];
  timestamp: string;
}

export interface BankInstance {
  id: string;
  perspective_id: string;
  type: BankType;
  synopsis: string;
  decision_audit: DecisionAuditEntry[];
  agent_assessments: Record<string, AgentAssessment>;
  documents_count: number;
  vibes_count: number;
  created_at: string;
}

export interface BankTimelineResponse {
  bank_instances: BankInstance[];
}

export interface Document {
  id: string;
  journey_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  storage_key: string;
  created_at: string;
}

// VDBA entities
export interface Vdba {
  id: string;
  title: string;
  description: string;
  journey_id: string;
  bank_instance_id: string;
  published_at: string;
  export_url: string | null;
  export_format: "pdf" | "docx" | "json";
  version: number;
}

export interface JourneyAnalytics {
  journey_id: string;
  perspectives_completed: number;
  perspectives_total: number;
  progress_pct: number;
  total_cost_cents: number;
  agent_sessions_count: number;
}

export interface DashboardStats {
  total_journeys: number;
  active_journeys: number;
  completed_journeys: number;
  total_vdbas: number;
  total_cost_cents: number;
  total_vibes: number;
  total_emails: number;
  recent_vdbas: Vdba[];
}

// API responses
export interface HealthResponse {
  status: "healthy" | "degraded";
  version: string;
  services: Record<string, ServiceCheck>;
}

export interface ServiceCheck {
  status: "up" | "down";
  latency_ms: number;
}

export interface Notification {
  id: string;
  title: string;
  body: string;
  link: string | null;
  read_at: string | null;
  created_at: string;
}

export interface NotificationCount {
  unread: number;
}
