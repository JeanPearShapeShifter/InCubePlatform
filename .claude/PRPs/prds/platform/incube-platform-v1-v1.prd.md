# InCube Platform — Product Requirements Document v1

## 1. Problem Statement

Business transformation professionals, consultants, and enterprise architects lack a structured, repeatable framework for converting strategic goals into validated, traceable digital business assets. Current approaches rely on scattered documents, manual coordination between stakeholders, and subjective validation — resulting in inconsistent quality, lost knowledge, and decisions that can't be defended.

**InCube** solves this by providing an AI-powered platform where 9 specialized cognitive agents guide users through a systematic 3x4 matrix (3 Dimensions x 4 Phases = 12 Perspectives), producing a Validated Digital Business Asset (VDBA) with full decision audit trails.

## 2. Target Users

| Persona | Description |
|---------|-------------|
| **Consultant / Consulting House** | Wants to digitize, systematize, and monetize intellectual property into reusable frameworks |
| **CEO / Business Owner** | Needs structured transformation guidance without deep methodology knowledge |
| **Enterprise Innovation Team** | Requires repeatable, auditable processes for large-scale business transformation |

## 3. Hypothesis

If we replace manual stakeholder coordination with specialized AI agents and provide a structured matrix-based workflow, business transformation professionals can produce validated digital business assets 10x faster with full decision traceability.

## 4. Core Framework

### 4.1 The Cube — 3 Dimensions x 4 Phases

**Dimensions** (What we're working on):
| Dimension | Focus | Color |
|-----------|-------|-------|
| **Architecture** | Structure — what something is, how parts relate, what rules govern boundaries | Cyan |
| **Design** | Experience — how something feels, flows, and is understood | Purple |
| **Engineering** | Implementation — how something is made real, sustained, and scaled | Amber |

**Phases** (How we progress):
| Phase | Focus | Color |
|-------|-------|-------|
| **Generate** | Unbounded creation of possibilities without constraints | Green |
| **Review** | Critical refinement and tightening of options | Orange |
| **Validate** | Proof of correctness and feasibility with real testing | Blue |
| **Summarize** | Distillation into a bankable artifact for permanent record | Purple |

**12 Perspectives** (Intersections):
| | Generate | Review | Validate | Summarize |
|---|----------|--------|----------|-----------|
| **Architecture** | Imagining | Critiquing | Proving | Distilling |
| **Design** | Exploring | Shaping | Testing | Crystallizing |
| **Engineering** | Inventing | Optimizing | Verifying | Synthesizing |

### 4.2 Nine Cognitive Agents

All agents powered by Claude API via Agent SDK, using Haiku by default (Sonnet upgrade available per agent in settings).

| # | Name | Role | Specialty | Color |
|---|------|------|-----------|-------|
| 1 | **Lyra** | Goal | Strategic alignment — ensures every element aligns with measurable outcomes | Purple |
| 2 | **Mira** | Stakeholder | Stakeholder analysis — brings the right voices into every decision | Pink |
| 3 | **Dex** | Requirement | Requirements engineering — transforms needs into testable criteria | Blue |
| 4 | **Rex** | Capability | Capability assessment — grounds decisions in actual possibilities | Cyan |
| 5 | **Vela** | Value | Value & ROI analysis — focuses on delivering real business value | Gold |
| 6 | **Koda** | Value-Stream | Process optimization — optimizes end-to-end flow of work | Green |
| 7 | **Halo** | Value-Chain | Systems integration — maintains coherence across the value chain | Orange |
| 8 | **Nova** | Implementation | Execution planning — bridges blueprint to operational reality | Red |
| 9 | **Axiom** | Challenger | Adversarial review — questions all agent outputs to ensure defensible decisions | Silver |

### 4.3 Axiom — The Challenger Agent

Axiom is fundamentally different from the other 8 agents. While the specialists are constructive (they build, assess, and validate), Axiom is adversarial. Its purpose:

1. **Challenge assumptions** — "Why did Lyra conclude this goal is aligned? What evidence supports that?"
2. **Find blind spots** — "Koda optimized the value stream, but nobody addressed the regulatory constraint"
3. **Demand evidence** — "Vela claims high ROI, but Rex's capability assessment contradicts this"
4. **Document rationale** — Every resolved challenge becomes a decision record

**Bounded Debate Protocol (Single-Pass):**
```
8 Specialist Agents produce assessments (parallel)
     ↓
Axiom receives ALL 8 outputs
     ↓
Axiom produces structured challenges:
  - Challenge description
  - Targeted agents
  - Severity (HIGH/MEDIUM/LOW)
  - Evidence needed
     ↓
Targeted agents respond to challenges (parallel)
     ↓
Axiom evaluates responses → Verdict per challenge:
  - RESOLVED — satisfactory justification (→ decision record)
  - ACCEPTED RISK — disagreement logged with both perspectives
  - ACTION REQUIRED — genuine gap, added to actionable items
```

**Maximum 3 LLM calls per challenge** (challenge → response → verdict). No infinite loops.

**Selective Activation** (iMAD pattern):
- Disagreement between specialists triggers Axiom
- Low confidence scores from any specialist trigger Axiom
- High-stakes intersections (Summarize phase) always trigger Axiom
- User can manually request "challenge this"

### 4.4 Banking System — Artefact Lifecycle

| Type | Created When | Description |
|------|-------------|-------------|
| **Bankable** | Non-Summarize phase boomerang accepted | Standard intersection artefact |
| **Film** | Architecture or Design Summarize accepted | Captures a dimension's complete journey |
| **Film Reel** | Engineering Summarize accepted | Captures the cross-dimension journey |
| **Published (VDBA)** | Final publication | Validated Digital Business Asset with full audit trail |

### 4.5 Post-Vibe Agent Analysis

After every vibe (voice) session, all 9 agents analyze the transcript + existing documents:

**Pipeline:**
```
User finishes Vibe session
     ↓
Whisper transcribes audio → structured transcript
     ↓
System gathers context:
  - Transcript text
  - All documents in current intersection
  - Current bank state
  - Current goal + dimension + phase
     ↓
All 9 agents analyze in parallel
     ↓
Output: Vibe Analysis Report
```

**Per-Agent Extraction:**
| Agent | Extracts |
|-------|----------|
| Lyra | Goal-relevant insights |
| Mira | Stakeholder signals |
| Dex | Implicit requirements |
| Rex | Capability gaps |
| Vela | Value indicators |
| Koda | Process observations |
| Halo | Integration points |
| Nova | Implementation hints |
| Axiom | Contradictions & risks |

**Structured Output:**
- Key Insights (per agent, with source attribution)
- Actionable Items (with owner agent and priority)
- Contradictions Found (between transcript and existing documents)
- Document Updates Suggested (proposed edits to existing artefacts)

## 5. Technical Architecture

### 5.1 Tech Stack

| Layer | Technology | Alternatives Considered | Rationale for Choice |
|-------|-----------|------------------------|---------------------|
| **Frontend** | Next.js 15 + React 19 + Tailwind CSS 4 | Remix, SvelteKit | SSR + API routes in one framework. Largest ecosystem. React 19 concurrent features for SSE streaming |
| **UI Components** | shadcn/ui + Radix | MUI, Chakra UI | Fully customizable (copy-paste, not library dependency). Accessible primitives from Radix. No style lock-in |
| **State Management** | Zustand (client) + React Query (server) | Redux Toolkit, Jotai | Zustand: 1KB, minimal boilerplate, sufficient for <10 stores. React Query: server cache + revalidation built-in |
| **Backend** | FastAPI (Python 3.12+) | Django REST, Express.js | Async-native (critical for parallel agent calls). Auto-generates OpenAPI docs. Python required for Claude Agent SDK |
| **ORM** | SQLAlchemy 2.0 + asyncpg | Django ORM, Prisma | True async support with asyncpg driver. Alembic migrations. Mature, well-documented |
| **Database** | PostgreSQL 16 (Docker) | MySQL, SQLite | JSONB support for flexible agent payloads. Array types for targeted_agents. Best ecosystem for complex queries |
| **File Storage** | MinIO (Docker) | AWS S3 (direct), local filesystem | S3-compatible API — zero code changes to migrate to AWS S3 in production. Self-hosted for dev parity |
| **Cache/Queue** | Redis 7 (Docker) | RabbitMQ, Celery+Redis | Simple key-value cache + lightweight job queue (arq). RabbitMQ overkill for this scale |
| **AI Agents** | Claude Agent SDK + Haiku (default) | OpenAI API, LangChain | First-party SDK for Claude. Direct API access without LangChain abstraction overhead. Haiku cost-effective for 9 parallel agents |
| **Voice** | Web Audio API + Whisper API | Deepgram, AssemblyAI | Whisper: proven accuracy, simple API. Web Audio: browser-native, no dependencies. Provider configurable in settings |
| **Email** | Resend | SendGrid, Postmark | Developer-friendly API, React Email templates, generous free tier. Simple integration |
| **Auth** | Custom JWT (bcrypt + httpOnly cookies) | NextAuth.js, Auth0 | Full control over auth flow. No external dependency for core security. Simple for email/password (social login not in v1) |
| **Real-time** | Server-Sent Events (SSE) | WebSocket, Socket.io | Server→client only (agent responses). Simpler than WebSocket. Works with HTTP/2. No bidirectional needed |
| **Background Jobs** | arq (Redis-backed) | Celery, Dramatiq | Lightweight, async-native, Redis-based. Celery too heavy for <10 job types |
| **Document Editor** | TipTap (ProseMirror) | Slate.js, Quill | Structured editing, good plugin ecosystem, collaborative editing ready. Slate API still unstable |

### 5.2 Docker Compose (Development)

```yaml
services:
  db:
    image: postgres:16-alpine
    ports: ["5434:5432"]
    environment:
      POSTGRES_DB: incube_dev
      POSTGRES_USER: incube
      POSTGRES_PASSWORD: incube_dev
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  minio:
    image: minio/minio
    ports: ["9000:9000", "9001:9001"]
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: incube
      MINIO_ROOT_PASSWORD: incube_dev
    volumes: [minio_data:/data]

volumes:
  pgdata:
  minio_data:
```

### 5.3 Database Schema

#### 5.3.1 Enum Definitions

```sql
-- User roles within an organization
-- admin: full org control (billing, members, settings)
-- editor: create/edit goals, journeys, run agents, bank artefacts
-- viewer: read-only access to journeys, bank, VDBAs
CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer');

-- Goal origin type
-- predefined: from InCube's built-in goal library (e.g., "Digital Transformation Readiness")
-- custom: user-defined free-text goal
CREATE TYPE goal_type AS ENUM ('predefined', 'custom');

-- Journey lifecycle
-- active: in progress, perspectives being worked on
-- completed: all 12 perspectives done, ready for VDBA publication
-- archived: soft-archived by user, hidden from dashboard but preserved
CREATE TYPE journey_status AS ENUM ('active', 'completed', 'archived');

-- The 3 dimensions of the Cube framework
CREATE TYPE dimension_type AS ENUM ('architecture', 'design', 'engineering');

-- The 4 phases of the Cube framework
CREATE TYPE phase_type AS ENUM ('generate', 'review', 'validate', 'summarize');

-- Perspective work status
-- locked: prerequisites not met (prior phase incomplete)
-- pending: available to start but not yet begun
-- in_progress: user actively working on this intersection
-- completed: all work done, ready to bank
CREATE TYPE perspective_status AS ENUM ('locked', 'pending', 'in_progress', 'completed');

-- Axiom challenge severity levels
-- high: fundamental contradiction or missing evidence that could invalidate conclusions
-- medium: notable gap that should be addressed but doesn't block progress
-- low: minor observation or suggestion for improvement
CREATE TYPE challenge_severity AS ENUM ('high', 'medium', 'low');

-- Axiom challenge resolution outcomes
-- resolved: satisfactory justification provided, becomes a decision record
-- accepted_risk: disagreement logged with both perspectives preserved
-- action_required: genuine gap identified, added to actionable items
CREATE TYPE challenge_resolution AS ENUM ('resolved', 'accepted_risk', 'action_required');

-- Bank artefact types (lifecycle progression)
-- bankable: standard intersection artefact from non-Summarize phase
-- film: dimension summary from Architecture or Design Summarize phase
-- film_reel: cross-dimension summary from Engineering Summarize phase
-- published: final VDBA with full audit trail
CREATE TYPE bank_type AS ENUM ('bankable', 'film', 'film_reel', 'published');

-- External service identifiers for cost tracking
CREATE TYPE api_service AS ENUM ('claude', 'whisper', 'resend');

-- Email template types
-- stakeholder_invite: request for stakeholder input on a perspective
-- vibe_summary: post-vibe analysis summary sent to participants
-- journey_complete: notification that a journey has finished all 12 perspectives
-- vdba_published: notification that a VDBA has been published and is ready to export
-- budget_alert: warning that API usage is approaching the monthly cap
CREATE TYPE email_template AS ENUM ('stakeholder_invite', 'vibe_summary', 'journey_complete', 'vdba_published', 'budget_alert');

-- Notification delivery channel
CREATE TYPE notification_channel AS ENUM ('in_app', 'email', 'both');
```

#### 5.3.2 Core Tables

```sql
-- Tenant organization. All data is scoped to an organization.
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,                          -- Display name
    slug VARCHAR(100) NOT NULL UNIQUE,                   -- URL-safe identifier (e.g., "acme-consulting")
    logo_url VARCHAR(500),                               -- MinIO key for org logo
    monthly_budget_cents INTEGER DEFAULT 0,              -- Monthly API spend cap in cents (0 = unlimited)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_organizations_slug ON organizations (slug);

-- Authenticated user. Belongs to one organization.
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(320) NOT NULL UNIQUE,                  -- RFC 5321 max email length
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,                 -- bcrypt hash, 12 rounds
    role user_role NOT NULL DEFAULT 'editor',
    avatar_url VARCHAR(500),                             -- MinIO key or external URL
    email_verified_at TIMESTAMPTZ,                       -- NULL = unverified
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_organization ON users (organization_id);
CREATE INDEX idx_users_email ON users (email);

-- Email verification and password reset tokens
CREATE TABLE auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,             -- SHA-256 hash of token sent to user
    token_type VARCHAR(20) NOT NULL CHECK (token_type IN ('email_verify', 'password_reset')),
    expires_at TIMESTAMPTZ NOT NULL,                     -- 24h for email verify, 1h for password reset
    used_at TIMESTAMPTZ,                                 -- Set when token is consumed
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_auth_tokens_hash ON auth_tokens (token_hash) WHERE used_at IS NULL;

-- Transformation goal. Top-level container for a journey.
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,                         -- e.g., "Digital Transformation Readiness Assessment"
    description TEXT NOT NULL DEFAULT '',                 -- Detailed goal context
    type goal_type NOT NULL DEFAULT 'custom',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_goals_organization ON goals (organization_id);

-- A journey through the 12-perspective Cube framework for a specific goal.
CREATE TABLE journeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    status journey_status NOT NULL DEFAULT 'active',
    perspectives_completed INTEGER NOT NULL DEFAULT 0 CHECK (perspectives_completed BETWEEN 0 AND 12),
    total_cost_cents INTEGER NOT NULL DEFAULT 0,         -- Running cost aggregated from agent_sessions
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,                            -- Set when status → completed
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_journeys_organization ON journeys (organization_id);
CREATE INDEX idx_journeys_status ON journeys (organization_id, status);

-- One of the 12 intersections (3 dimensions x 4 phases) within a journey.
CREATE TABLE perspectives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES journeys(id) ON DELETE CASCADE,
    dimension dimension_type NOT NULL,
    phase phase_type NOT NULL,
    status perspective_status NOT NULL DEFAULT 'locked',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (journey_id, dimension, phase)                -- One perspective per intersection per journey
);

CREATE INDEX idx_perspectives_journey ON perspectives (journey_id);
CREATE INDEX idx_perspectives_status ON perspectives (journey_id, status);
```

#### 5.3.3 AI Agent Tables

```sql
-- Record of a single AI agent invocation. Every LLM call is tracked here.
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perspective_id UUID NOT NULL REFERENCES perspectives(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL CHECK (agent_name IN ('lyra','mira','dex','rex','vela','koda','halo','nova','axiom')),
    model_used VARCHAR(50) NOT NULL DEFAULT 'claude-haiku-4-5-20251001', -- Claude model ID
    system_prompt_version VARCHAR(20) NOT NULL DEFAULT 'v1',
    input_tokens INTEGER NOT NULL DEFAULT 0 CHECK (input_tokens >= 0),
    output_tokens INTEGER NOT NULL DEFAULT 0 CHECK (output_tokens >= 0),
    cost_cents NUMERIC(10,4) NOT NULL DEFAULT 0,         -- Calculated: (input_tokens * input_price + output_tokens * output_price)
    request_payload JSONB NOT NULL DEFAULT '{}',         -- System prompt + user context sent
    response_payload JSONB NOT NULL DEFAULT '{}',        -- Agent's structured response
    duration_ms INTEGER,                                  -- Wall-clock time for the LLM call
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agent_sessions_perspective ON agent_sessions (perspective_id);
CREATE INDEX idx_agent_sessions_agent ON agent_sessions (agent_name, created_at);
CREATE INDEX idx_agent_sessions_cost ON agent_sessions (created_at, cost_cents); -- For usage dashboard queries

-- Axiom challenger agent challenges against specialist outputs.
CREATE TABLE axiom_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perspective_id UUID NOT NULL REFERENCES perspectives(id) ON DELETE CASCADE,
    challenge_text TEXT NOT NULL,                         -- What Axiom is challenging
    severity challenge_severity NOT NULL,
    targeted_agents TEXT[] NOT NULL DEFAULT '{}',         -- Which specialist agents are challenged
    evidence_needed TEXT NOT NULL DEFAULT '',             -- What evidence would resolve this
    resolution challenge_resolution,                      -- NULL while unresolved
    resolution_text TEXT,                                 -- Agent responses + Axiom verdict
    agent_session_id UUID REFERENCES agent_sessions(id), -- The session that generated this challenge
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_axiom_challenges_perspective ON axiom_challenges (perspective_id);
CREATE INDEX idx_axiom_challenges_unresolved ON axiom_challenges (perspective_id) WHERE resolution IS NULL;
```

#### 5.3.4 Document & Vibe Tables

```sql
-- File uploaded to a perspective workspace.
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perspective_id UUID NOT NULL REFERENCES perspectives(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    filename VARCHAR(500) NOT NULL,                      -- Original filename
    file_type VARCHAR(50) NOT NULL,                      -- MIME type (e.g., "application/pdf")
    minio_key VARCHAR(1000) NOT NULL UNIQUE,             -- MinIO object key
    file_size INTEGER NOT NULL CHECK (file_size > 0),    -- Bytes
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_documents_perspective ON documents (perspective_id);

-- Voice recording session with transcription.
CREATE TABLE vibe_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perspective_id UUID NOT NULL REFERENCES perspectives(id) ON DELETE CASCADE,
    conducted_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
    audio_minio_key VARCHAR(1000) NOT NULL UNIQUE,       -- MinIO key for audio file
    transcript_text TEXT,                                  -- Plain text transcription
    transcript_minio_key VARCHAR(1000),                  -- MinIO key for structured transcript
    transcription_cost_cents NUMERIC(10,4) DEFAULT 0,    -- Whisper API cost
    status VARCHAR(20) NOT NULL DEFAULT 'transcribing' CHECK (status IN ('transcribing', 'analyzing', 'complete', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_vibe_sessions_perspective ON vibe_sessions (perspective_id);

-- Per-agent analysis of a vibe session transcript.
CREATE TABLE vibe_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vibe_session_id UUID NOT NULL REFERENCES vibe_sessions(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL CHECK (agent_name IN ('lyra','mira','dex','rex','vela','koda','halo','nova','axiom')),
    analysis_type VARCHAR(50) NOT NULL DEFAULT 'post_vibe', -- Extensible for future analysis types
    content JSONB NOT NULL DEFAULT '{}',                 -- Structured: {insights:[], actionItems:[], contradictions:[], suggestedEdits:[]}
    agent_session_id UUID REFERENCES agent_sessions(id), -- Links to the LLM call that produced this
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (vibe_session_id, agent_name, analysis_type)
);

CREATE INDEX idx_vibe_analyses_session ON vibe_analyses (vibe_session_id);
```

#### 5.3.5 Banking & VDBA Tables

```sql
-- A banked artefact from a perspective (or aggregation of perspectives).
CREATE TABLE bank_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perspective_id UUID NOT NULL REFERENCES perspectives(id) ON DELETE CASCADE,
    type bank_type NOT NULL,
    synopsis TEXT NOT NULL DEFAULT '',                    -- Human-readable summary of what was banked
    decision_audit JSONB NOT NULL DEFAULT '[]',          -- Array of {challenge, resolution, evidence, agents, timestamp}
    documents_count INTEGER NOT NULL DEFAULT 0 CHECK (documents_count >= 0),
    vibes_count INTEGER NOT NULL DEFAULT 0 CHECK (vibes_count >= 0),
    emails_sent INTEGER NOT NULL DEFAULT 0 CHECK (emails_sent >= 0),
    feedback_received INTEGER NOT NULL DEFAULT 0 CHECK (feedback_received >= 0),
    agent_assessments JSONB NOT NULL DEFAULT '{}',       -- {agentName: {summary, confidence, keyFindings[]}}
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_bank_instances_perspective ON bank_instances (perspective_id);
CREATE INDEX idx_bank_instances_type ON bank_instances (type);

-- Published Validated Digital Business Asset.
CREATE TABLE vdbas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES journeys(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    bank_instance_id UUID NOT NULL REFERENCES bank_instances(id), -- The film_reel that was published
    published_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    export_url VARCHAR(1000),                            -- MinIO key for generated export file
    export_format VARCHAR(10) DEFAULT 'pdf' CHECK (export_format IN ('pdf', 'docx', 'json')),
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_vdbas_organization ON vdbas (organization_id);
CREATE INDEX idx_vdbas_journey ON vdbas (journey_id);
```

#### 5.3.6 Communication & Tracking Tables

```sql
-- Log of outbound emails sent from perspectives.
CREATE TABLE email_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perspective_id UUID NOT NULL REFERENCES perspectives(id) ON DELETE CASCADE,
    sent_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    recipient_email VARCHAR(320) NOT NULL,
    recipient_type VARCHAR(50) NOT NULL DEFAULT 'stakeholder', -- stakeholder, team_member, external
    template_type email_template NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body_preview TEXT,                                    -- First 200 chars of email body
    resend_message_id VARCHAR(100),                      -- Resend API message ID for delivery tracking
    delivery_status VARCHAR(20) NOT NULL DEFAULT 'sent' CHECK (delivery_status IN ('sent', 'delivered', 'bounced', 'failed')),
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_email_log_perspective ON email_log (perspective_id);

-- API usage tracking for cost dashboard. One row per API call to external services.
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    service api_service NOT NULL,
    model VARCHAR(50),                                   -- e.g., "claude-haiku-4-5-20251001", "whisper-1"
    tokens_in INTEGER NOT NULL DEFAULT 0,
    tokens_out INTEGER NOT NULL DEFAULT 0,
    cost_cents NUMERIC(10,4) NOT NULL DEFAULT 0,
    endpoint VARCHAR(200),                               -- Which API endpoint was called
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_api_usage_org_date ON api_usage (organization_id, created_at);
CREATE INDEX idx_api_usage_service ON api_usage (service, created_at);

-- Key-value settings store per organization.
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,                           -- e.g., "voice_provider", "default_model", "theme"
    value JSONB NOT NULL DEFAULT '{}',                   -- Typed value (provider config, model selection, etc.)
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, key)
);

CREATE INDEX idx_settings_org_key ON settings (organization_id, key);

-- In-app notifications for users.
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    link VARCHAR(500),                                   -- In-app route to navigate to (e.g., "/canvas?journey=abc")
    read_at TIMESTAMPTZ,                                 -- NULL = unread
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_user_unread ON notifications (user_id, created_at) WHERE read_at IS NULL;
```

#### 5.3.7 Indexes Summary

All query-critical paths have indexes:
- **Dashboard queries**: `idx_journeys_organization`, `idx_journeys_status` — filter journeys by org + status
- **Canvas navigation**: `idx_perspectives_journey`, `idx_perspectives_status` — load all 12 perspectives for a journey
- **Agent history**: `idx_agent_sessions_perspective` — load session history for a perspective
- **Cost dashboard**: `idx_api_usage_org_date`, `idx_agent_sessions_cost` — aggregate costs by date range
- **Unread notifications**: `idx_notifications_user_unread` — partial index, only unread rows
- **Unresolved challenges**: `idx_axiom_challenges_unresolved` — partial index for active challenges

#### 5.3.8 Seed Data

```sql
-- Default settings for new organizations
INSERT INTO settings (organization_id, key, value) VALUES
    -- Applied per-org on registration:
    -- ('org_id', 'default_model', '"claude-haiku-4-5-20251001"'),
    -- ('org_id', 'voice_provider', '{"provider": "whisper", "language": "en", "auto_detect": true}'),
    -- ('org_id', 'theme', '"space"'),
    -- ('org_id', 'export_format', '"pdf"'),
    -- ('org_id', 'monthly_budget_cents', '0'),
    -- ('org_id', 'budget_alert_thresholds', '[80, 90, 100]');

-- Predefined goals (inserted once, shared across orgs)
-- These are referenced by goals.type = 'predefined'
-- Actual INSERT runs in seed script with real UUIDs:
--   "Digital Transformation Readiness Assessment"
--   "New Product Innovation Framework"
--   "Operational Excellence Optimization"
--   "Customer Experience Redesign"
--   "Technology Modernization Strategy"
```

#### 5.3.9 Entity-Relationship Summary

| Relationship | Type | ON DELETE |
|-------------|------|-----------|
| organizations → users | 1:N | CASCADE |
| organizations → goals | 1:N | CASCADE |
| organizations → journeys | 1:N | CASCADE |
| goals → journeys | 1:N | CASCADE |
| journeys → perspectives | 1:12 | CASCADE |
| perspectives → agent_sessions | 1:N | CASCADE |
| perspectives → axiom_challenges | 1:N | CASCADE |
| perspectives → documents | 1:N | CASCADE |
| perspectives → vibe_sessions | 1:N | CASCADE |
| vibe_sessions → vibe_analyses | 1:9 | CASCADE |
| perspectives → bank_instances | 1:N | CASCADE |
| perspectives → email_log | 1:N | CASCADE |
| journeys → vdbas | 1:N | CASCADE |
| bank_instances → vdbas | 1:1 | (no cascade) |
| users → auth_tokens | 1:N | CASCADE |
| users → notifications | 1:N | CASCADE |

### 5.4 API Specification

#### 5.4.1 Standard Response Envelope

All API responses use a consistent envelope format:

```json
// Success
{
  "status": "success",
  "data": { /* resource or array */ },
  "meta": { "request_id": "uuid", "timestamp": "ISO 8601" }
}

// Error
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [ { "field": "email", "message": "Must be valid email" } ]
  },
  "meta": { "request_id": "uuid", "timestamp": "ISO 8601" }
}
```

**Standard Error Codes:**

| HTTP | Code | When |
|------|------|------|
| 400 | `VALIDATION_ERROR` | Invalid request body, missing required fields |
| 401 | `UNAUTHORIZED` | Missing or expired auth token |
| 403 | `FORBIDDEN` | Insufficient role/permissions |
| 404 | `NOT_FOUND` | Resource doesn't exist or not in user's org |
| 409 | `CONFLICT` | Duplicate (e.g., email already registered) |
| 413 | `PAYLOAD_TOO_LARGE` | File upload exceeds limit (50MB) |
| 422 | `UNPROCESSABLE` | Valid syntax but business rule violation |
| 429 | `RATE_LIMITED` | Too many requests (60/min per user) |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | External dependency down (Claude API, Whisper) |

#### 5.4.2 Authentication Endpoints

**`POST /api/auth/register`** — Create new account + organization
- Auth: Public
- Request:
  ```json
  {
    "email": "string, required, valid email, max 320 chars",
    "password": "string, required, min 8 chars, must contain uppercase + number",
    "name": "string, required, max 255 chars",
    "organization_name": "string, required, max 255 chars"
  }
  ```
- Response (201): `{ user: { id, email, name, role }, organization: { id, name, slug } }`
- Errors: 409 email already exists, 400 validation errors
- Side effects: Creates org, creates admin user, sends verification email, inserts default settings

**`POST /api/auth/login`** — Authenticate user
- Auth: Public
- Request: `{ "email": "string, required", "password": "string, required" }`
- Response (200): `{ user: { id, email, name, role, organization_id }, token: "JWT string" }`
- Errors: 401 invalid credentials (generic message, don't reveal which field is wrong)
- Rate limit: 5 failed attempts per email per 15 minutes, then 429

**`POST /api/auth/logout`** — Invalidate session
- Auth: Authenticated
- Response (200): `{ message: "Logged out" }`

**`GET /api/auth/me`** — Get current user profile
- Auth: Authenticated
- Response (200): `{ user: { id, email, name, role, avatar_url, organization: { id, name, slug, logo_url } } }`

**`POST /api/auth/verify-email`** — Verify email address
- Auth: Public
- Request: `{ "token": "string, required" }`
- Response (200): `{ message: "Email verified" }`
- Errors: 400 invalid/expired token

**`POST /api/auth/forgot-password`** — Request password reset
- Auth: Public
- Request: `{ "email": "string, required" }`
- Response (200): `{ message: "If email exists, reset link sent" }` (always 200, never reveal existence)

**`POST /api/auth/reset-password`** — Reset password with token
- Auth: Public
- Request: `{ "token": "string, required", "password": "string, required, min 8 chars" }`
- Response (200): `{ message: "Password reset" }`

**`POST /api/auth/refresh`** — Refresh JWT token
- Auth: Authenticated (accepts expired token within 7-day window)
- Response (200): `{ token: "new JWT string" }`

#### 5.4.3 Organization Endpoints

**`GET /api/organizations/:id`** — Get organization details
- Auth: Authenticated, own org only
- Response (200): `{ organization: { id, name, slug, logo_url, monthly_budget_cents, created_at } }`

**`PUT /api/organizations/:id`** — Update organization
- Auth: Admin only
- Request: `{ "name": "string, optional", "logo_url": "string, optional", "monthly_budget_cents": "integer, optional, >= 0" }`
- Response (200): Updated organization object

#### 5.4.4 Goal Endpoints

**`POST /api/goals`** — Create a new goal
- Auth: Editor+
- Request: `{ "title": "string, required, max 500", "description": "string, optional", "type": "predefined|custom" }`
- Response (201): `{ goal: { id, title, description, type, created_by, created_at } }`

**`GET /api/goals`** — List goals for current organization
- Auth: Viewer+
- Query: `?page=1&per_page=20&type=predefined|custom`
- Response (200): `{ goals: [...], pagination: { page, per_page, total, total_pages } }`

**`GET /api/goals/:id`** — Get single goal
- Auth: Viewer+
- Response (200): `{ goal: { id, title, description, type, created_by, journeys_count, created_at } }`

#### 5.4.5 Journey Endpoints

**`POST /api/journeys`** — Start a new journey from a goal
- Auth: Editor+
- Request: `{ "goal_id": "uuid, required" }`
- Response (201): `{ journey: { id, goal_id, status, perspectives: [12 perspective objects], created_at } }`
- Side effects: Creates all 12 perspective records (Generate phase unlocked, others locked)

**`GET /api/journeys`** — List journeys for current organization
- Auth: Viewer+
- Query: `?status=active|completed|archived&page=1&per_page=20`
- Response (200): `{ journeys: [{ id, goal: { id, title }, status, perspectives_completed, total_cost_cents, created_at }], pagination }`

**`GET /api/journeys/:id`** — Get journey with all perspectives
- Auth: Viewer+
- Response (200): `{ journey: { id, goal, status, perspectives: [12 items with status], total_cost_cents, bank_instances: [...] } }`

**`PATCH /api/journeys/:id/status`** — Update journey status
- Auth: Editor+
- Request: `{ "status": "completed|archived" }`
- Validation: Can only complete if all 12 perspectives are completed; can archive from any state

#### 5.4.6 Perspective Endpoints

**`GET /api/journeys/:id/perspectives`** — Get all 12 perspectives for a journey
- Auth: Viewer+
- Response (200): `{ perspectives: [{ id, dimension, phase, status, started_at, completed_at, documents_count, vibes_count }] }`

**`GET /api/perspectives/:id`** — Get perspective detail
- Auth: Viewer+
- Response (200): `{ perspective: { id, dimension, phase, status, journey_id, documents: [...], vibe_sessions: [...], agent_sessions: [...], bank_instances: [...] } }`

**`PATCH /api/perspectives/:id/status`** — Update perspective status
- Auth: Editor+
- Request: `{ "status": "in_progress|completed" }`
- Validation: Can only move to `in_progress` from `pending`; can only move to `completed` from `in_progress`

#### 5.4.7 Agent Endpoints

**`POST /api/perspectives/:id/agents/:name/chat`** — Chat with a specific agent (SSE)
- Auth: Editor+
- Request: `{ "message": "string, required, max 10000 chars", "context": { "include_documents": true, "include_vibes": true } }`
- Response: Server-Sent Events stream
  ```
  event: token
  data: {"content": "partial response text"}

  event: done
  data: {"session_id": "uuid", "input_tokens": 150, "output_tokens": 420, "cost_cents": 0.0012}
  ```
- Validation: `:name` must be one of: lyra, mira, dex, rex, vela, koda, halo, nova, axiom

**`POST /api/perspectives/:id/boomerang`** — Run all 9 agents in parallel (SSE)
- Auth: Editor+
- Request: `{ "prompt": "string, optional, max 10000 chars" }`
- Response: SSE stream with per-agent events
  ```
  event: agent_start
  data: {"agent": "lyra"}

  event: agent_token
  data: {"agent": "lyra", "content": "partial text"}

  event: agent_complete
  data: {"agent": "lyra", "session_id": "uuid", "summary": "...", "cost_cents": 0.0012}

  event: axiom_challenge
  data: {"challenge_id": "uuid", "text": "...", "severity": "high", "targeted_agents": ["lyra","vela"]}

  event: boomerang_complete
  data: {"total_cost_cents": 0.0108, "challenges_count": 2}
  ```

**`GET /api/perspectives/:id/agent-sessions`** — List agent sessions for a perspective
- Auth: Viewer+
- Query: `?agent=lyra&page=1&per_page=50`
- Response (200): `{ sessions: [{ id, agent_name, model_used, input_tokens, output_tokens, cost_cents, created_at }] }`

#### 5.4.8 Axiom Challenge Endpoints

**`POST /api/perspectives/:id/axiom/challenge`** — Manually trigger Axiom challenge (SSE)
- Auth: Editor+
- Request: `{ "target": "string, optional, specific agent name or 'all'" }`
- Response: SSE stream (same format as boomerang axiom events)

**`GET /api/perspectives/:id/axiom/challenges`** — List challenges for a perspective
- Auth: Viewer+
- Response (200): `{ challenges: [{ id, challenge_text, severity, targeted_agents, resolution, resolution_text, created_at, resolved_at }] }`

#### 5.4.9 Document Endpoints

**`POST /api/perspectives/:id/documents`** — Upload document (multipart)
- Auth: Editor+
- Request: multipart/form-data with `file` field
- Validation: Max 50MB, allowed types: pdf, docx, xlsx, pptx, txt, md, csv, png, jpg
- Response (201): `{ document: { id, filename, file_type, file_size, created_at } }`

**`GET /api/perspectives/:id/documents`** — List documents
- Auth: Viewer+
- Response (200): `{ documents: [{ id, filename, file_type, file_size, uploaded_by: { id, name }, created_at }] }`

**`GET /api/documents/:id/download`** — Download document
- Auth: Viewer+
- Response: Binary file with Content-Disposition header

**`DELETE /api/documents/:id`** — Delete document
- Auth: Editor+
- Response (200): `{ message: "Document deleted" }`
- Side effects: Removes from MinIO

#### 5.4.10 Vibe Session Endpoints

**`POST /api/perspectives/:id/vibes`** — Upload voice recording (multipart)
- Auth: Editor+
- Request: multipart/form-data with `audio` field (webm/wav/mp3, max 100MB)
- Response (201): `{ vibe_session: { id, duration_seconds, status: "transcribing", created_at } }`
- Side effects: Queues Whisper transcription → then auto-triggers 9-agent analysis

**`GET /api/perspectives/:id/vibes`** — List vibe sessions
- Auth: Viewer+
- Response (200): `{ vibe_sessions: [{ id, duration_seconds, status, has_transcript, analyses_count, created_at }] }`

**`GET /api/vibes/:id`** — Get vibe session detail
- Auth: Viewer+
- Response (200): `{ vibe_session: { id, duration_seconds, transcript_text, status, analyses: [{ agent_name, content }], created_at } }`

**`POST /api/vibes/:id/analyze`** — Manually re-trigger agent analysis
- Auth: Editor+
- Response (202): `{ message: "Analysis queued" }`

#### 5.4.11 Bank Endpoints

**`POST /api/perspectives/:id/bank`** — Bank an artefact from a perspective
- Auth: Editor+
- Request: `{ "synopsis": "string, required, max 5000 chars" }`
- Validation: Perspective must be completed; type auto-determined from dimension + phase
- Response (201): `{ bank_instance: { id, type, synopsis, decision_audit, agent_assessments, created_at } }`

**`GET /api/journeys/:id/bank`** — Get bank timeline for a journey
- Auth: Viewer+
- Response (200): `{ bank_instances: [{ id, type, synopsis, perspective: { dimension, phase }, documents_count, vibes_count, created_at }] }`

**`GET /api/bank/:id`** — Get bank instance detail
- Auth: Viewer+
- Response (200): `{ bank_instance: { id, type, synopsis, decision_audit, agent_assessments, perspective, documents, vibe_sessions } }`

#### 5.4.12 VDBA Endpoints

**`POST /api/journeys/:id/publish`** — Publish journey as VDBA
- Auth: Editor+
- Request: `{ "title": "string, required, max 500", "description": "string, optional", "export_format": "pdf|docx|json" }`
- Validation: Journey must be completed (all 12 perspectives)
- Response (201): `{ vdba: { id, title, description, export_format, published_at } }`
- Side effects: Generates export file, stores in MinIO

**`GET /api/vdbas`** — List published VDBAs
- Auth: Viewer+
- Query: `?page=1&per_page=20`
- Response (200): `{ vdbas: [{ id, title, journey: { id, goal: { title } }, published_at, export_format }] }`

**`GET /api/vdbas/:id`** — Get VDBA detail
- Auth: Viewer+
- Response (200): `{ vdba: { id, title, description, journey, bank_instances: [...], export_url, published_at } }`

**`GET /api/vdbas/:id/export`** — Download VDBA export
- Auth: Viewer+
- Response: Binary file (PDF/DOCX/JSON)

#### 5.4.13 Email Endpoints

**`POST /api/perspectives/:id/email`** — Send stakeholder email
- Auth: Editor+
- Request: `{ "recipient_email": "string, required, valid email", "template_type": "stakeholder_invite|vibe_summary", "custom_message": "string, optional, max 5000" }`
- Response (201): `{ email: { id, recipient_email, template_type, delivery_status, sent_at } }`

**`GET /api/perspectives/:id/emails`** — List sent emails
- Auth: Viewer+
- Response (200): `{ emails: [{ id, recipient_email, template_type, delivery_status, sent_at }] }`

#### 5.4.14 Settings Endpoints

**`GET /api/settings`** — Get all settings for current organization
- Auth: Viewer+
- Response (200): `{ settings: { default_model, voice_provider, theme, export_format, monthly_budget_cents, budget_alert_thresholds } }`

**`PUT /api/settings`** — Update settings
- Auth: Admin only
- Request: `{ "key": "string", "value": "any JSON value" }`
- Validation: Key must be one of allowed keys; value validated per key type
- Response (200): Updated settings object

**`GET /api/settings/usage`** — Get API usage summary
- Auth: Viewer+
- Query: `?period=day|week|month&start=ISO8601&end=ISO8601`
- Response (200): `{ usage: { total_cost_cents, total_tokens_in, total_tokens_out, by_date: [{ date, cost_cents }] } }`

**`GET /api/settings/usage/breakdown`** — Get usage breakdown
- Auth: Viewer+
- Query: `?period=month&group_by=agent|service|journey`
- Response (200): `{ breakdown: [{ name, cost_cents, tokens_in, tokens_out, call_count }] }`

#### 5.4.15 Health Endpoint

**`GET /api/health`** — System health check
- Auth: Public
- Response (200):
  ```json
  {
    "status": "healthy",
    "checks": {
      "database": { "status": "up", "latency_ms": 2 },
      "redis": { "status": "up", "latency_ms": 1 },
      "minio": { "status": "up", "latency_ms": 5 }
    },
    "version": "1.0.0",
    "uptime_seconds": 86400
  }
  ```

#### 5.4.16 SSE Event Catalog

| Event | Direction | Payload | Trigger |
|-------|-----------|---------|---------|
| `token` | server→client | `{content: string}` | Each LLM output token chunk |
| `done` | server→client | `{session_id, input_tokens, output_tokens, cost_cents}` | LLM call completes |
| `error` | server→client | `{code, message}` | LLM call fails |
| `agent_start` | server→client | `{agent: string}` | Boomerang starts an agent |
| `agent_token` | server→client | `{agent, content}` | Per-agent token during boomerang |
| `agent_complete` | server→client | `{agent, session_id, summary, cost_cents}` | Agent finishes in boomerang |
| `axiom_challenge` | server→client | `{challenge_id, text, severity, targeted_agents}` | Axiom identifies a challenge |
| `axiom_verdict` | server→client | `{challenge_id, resolution, resolution_text}` | Axiom resolves a challenge |
| `boomerang_complete` | server→client | `{total_cost_cents, challenges_count}` | All 9 agents + Axiom done |

### 5.5 Authentication & Authorization

#### 5.5.1 Authentication Flows

**Registration Flow:**
1. User submits email + password + name + org name
2. Server validates input, checks email uniqueness
3. Server creates organization → creates user (admin role) → inserts default settings
4. Server generates email verification token (random 32 bytes → SHA-256 stored)
5. Server sends verification email via Resend with link: `/auth/verify?token={raw_token}`
6. User clicks link → `POST /api/auth/verify-email` → sets `email_verified_at`
7. Server issues JWT → user is logged in

**Login Flow:**
1. User submits email + password
2. Server verifies bcrypt hash (constant-time comparison)
3. Server checks email_verified_at (if null, return 403 with "verify email first")
4. Server issues JWT, updates `last_login_at`
5. Client stores JWT in httpOnly secure cookie (not localStorage)

**Password Reset Flow:**
1. User submits email to `/api/auth/forgot-password`
2. Server always returns 200 (don't reveal email existence)
3. If email exists: generate token (32 bytes → SHA-256 stored), expires in 1 hour
4. Send reset email via Resend with link: `/auth/reset-password?token={raw_token}`
5. User submits new password + token → server validates token, updates password_hash
6. Server invalidates all existing tokens for this user

**Token Refresh Flow:**
1. JWT includes `exp` claim (15 minutes) and `refresh_exp` claim (7 days)
2. Client sends expired JWT to `/api/auth/refresh`
3. Server validates signature + checks `refresh_exp` hasn't passed
4. Server issues new JWT with fresh `exp`

**Session Expiry:**
- JWT access token: 15 minutes
- Refresh window: 7 days from original login
- After 7 days: full re-authentication required
- On password change: all refresh tokens invalidated

#### 5.5.2 Token Specification

| Property | Value |
|----------|-------|
| Type | JWT (HS256) |
| Payload | `{ sub: user_id, org: organization_id, role: user_role, exp, refresh_exp, iat }` |
| Access TTL | 15 minutes |
| Refresh TTL | 7 days |
| Storage | httpOnly, Secure, SameSite=Lax cookie |
| Secret | `JWT_SECRET` env var, min 256-bit |

#### 5.5.3 Permission Matrix

| Resource | Action | Admin | Editor | Viewer |
|----------|--------|-------|--------|--------|
| Organization | View | Yes | Yes | Yes |
| Organization | Update | Yes | No | No |
| Users | Invite/Remove | Yes | No | No |
| Goals | Create | Yes | Yes | No |
| Goals | View | Yes | Yes | Yes |
| Journeys | Create | Yes | Yes | No |
| Journeys | View | Yes | Yes | Yes |
| Journeys | Archive | Yes | Yes | No |
| Perspectives | Work on | Yes | Yes | No |
| Perspectives | View | Yes | Yes | Yes |
| Agents | Chat | Yes | Yes | No |
| Agents | View sessions | Yes | Yes | Yes |
| Boomerang | Trigger | Yes | Yes | No |
| Documents | Upload/Delete | Yes | Yes | No |
| Documents | View/Download | Yes | Yes | Yes |
| Vibes | Record/Upload | Yes | Yes | No |
| Vibes | View | Yes | Yes | Yes |
| Bank | Create instance | Yes | Yes | No |
| Bank | View | Yes | Yes | Yes |
| VDBA | Publish | Yes | Yes | No |
| VDBA | View/Export | Yes | Yes | Yes |
| Email | Send | Yes | Yes | No |
| Email | View log | Yes | Yes | Yes |
| Settings | View | Yes | Yes | Yes |
| Settings | Update | Yes | No | No |

#### 5.5.4 Security Measures

| Measure | Implementation |
|---------|---------------|
| Password hashing | bcrypt, 12 rounds |
| Password requirements | Min 8 chars, at least 1 uppercase, 1 number |
| Brute-force protection | 5 failed login attempts per email per 15 minutes → 429 for 15 min |
| Rate limiting | 60 requests/min per authenticated user (global), 10/min for auth endpoints |
| CORS | Whitelist: `localhost:3001` (dev), production frontend domain |
| CSRF | SameSite=Lax cookie + Origin header check |
| Input sanitization | All string inputs stripped of control characters; HTML escaped on output |
| SQL injection | Parameterized queries only (SQLAlchemy ORM) |
| File upload | MIME type validation, max 50MB, filename sanitized |
| Secrets storage | Environment variables only, never in code or database |

## 6. Settings & Admin

### 6.1 API Usage & Costs Dashboard

- Real-time token counter: input tokens, output tokens, total cost per session
- Per-agent breakdown: which agents consume the most tokens
- Per-journey breakdown: cost of a complete VDBA creation
- Monthly/daily charts (Recharts line graphs)
- Budget alerts: set monthly cap, warnings at 80%/90%/100%
- Model selector: default Haiku, option to upgrade specific agents to Sonnet

### 6.2 Voice Provider Settings

- Provider selector: OpenAI Whisper API (default), Deepgram, AssemblyAI
- Language settings: default language, auto-detect toggle
- Quality/speed tradeoff slider
- Cost tracking: per-minute pricing, monthly usage
- Test button: record 5-second clip, transcribe, show result + latency + cost

### 6.3 Email Settings (Resend)

- API key configuration
- From address / domain verification status
- Template customization
- Send log with delivery status

### 6.4 General Settings

- Organization profile (name, logo)
- User management (invite, roles: Admin/Editor/Viewer)
- Default theme preference
- VDBA export format (PDF, DOCX, JSON)

## 7. UI/UX Design

### 7.1 Layout — Progressive Disclosure

```
┌─────────────────────────────────────────────────────────┐
│  InCube Logo  |  Journey: [Goal Name]  |  ⚙️ Settings   │
├────────┬────────────────────────────────────────────────┤
│        │                                                │
│  Left  │              Main Canvas Area                  │
│  Rail  │                                                │
│        │  Agent insights appear as inline cards         │
│ [Arch] │  (click to expand full assessment)             │
│ [Dsgn] │                                                │
│ [Engr] │  Decision Audit Trail visible when Axiom       │
│        │  challenges are present                        │
│ ────── │                                                │
│  Mini  │                                                │
│  Heat  │  ┌─────┬─────┬─────┬────────────┐             │
│  Map   │  │ Docs│Vibe │Email│ Boomerang  │             │
│        │  └─────┴─────┴─────┴────────────┘             │
├────────┴────────────────────────────────────────────────┤
│  Progress: ████████░░░░  Block 5/12  │  Cost: $0.42    │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Key Layout Changes from Prototype

1. **Left rail navigation** — compact vertical nav showing dimension/phase position + mini heat map
2. **Agent insights inline** — not a separate chat panel; cards within canvas area
3. **Persistent bottom action bar** — Docs, Vibe, Email, Boomerang always visible
4. **Progress + cost footer** — journey completion (X/12) + running API cost
5. **Subtle gradient backgrounds** — dimension/phase color tinting instead of animated canvas backgrounds (animations reserved for landing page)
6. **Persistent vibe recording bar** — like a music player, active while working
7. **Timeline bank view** — chronological journey instead of flat data table
8. **VDBA dashboard** — real data with completion %, cost, export options

### 7.3 Themes

Three visual themes (subtle gradient variations, not full animated backgrounds):
- **Space** (default) — Blue-based dark theme
- **Forest** — Green-based dark theme
- **Black Hole** — Amber-based dark theme

### 7.4 Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Landing | Hero with animated cube, CTA |
| `/dashboard` | Dashboard | Active journeys, recent VDBAs, usage stats |
| `/canvas` | Canvas | Main workspace — the core application |
| `/bank` | Bank | Timeline view of all banked artefacts |
| `/vdbas` | VDBAs | Published assets dashboard with export |
| `/fundamentals` | Fundamentals | Methodology documentation |
| `/settings` | Settings | API usage, voice, email, org config |
| `/auth/login` | Login | Authentication |
| `/auth/register` | Register | New account creation |

## 8. Implementation Phases

| # | Phase | Scope | Dependencies | Parallel | Status |
|---|-------|-------|--------------|----------|--------|
| 1 | **Foundation** | Project scaffolding, Docker Compose, DB schema, Alembic migrations, FastAPI skeleton | None | No | Complete |
| 2 | **Auth & Users** | JWT auth, user/org models, protected routes, password flows | Phase 1 | Yes (with 3, 4) | Pending |
| 3 | **Core Data Models** | Goals, Journeys, Perspectives, Documents, Bank Instances — CRUD API | Phase 1 | Yes (with 2, 4) | Pending |
| 4 | **AI Agent System** | Claude Agent SDK integration, 9 agent definitions, system prompts, SSE streaming | Phase 1 | Yes (with 2, 3) | Pending |
| 5 | **Frontend Foundation** | Next.js app shell, Tailwind design system, layout components, routing | Phase 2 | No | Pending |
| 6 | **Canvas UI** | Left rail, main canvas, agent cards, dimension/phase navigation | Phase 5 | No | Pending |
| 7 | **Document System** | MinIO upload/download, document editors (TipTap), viewer components | Phase 3 | Yes (with 8, 10) | Pending |
| 8 | **Vibe System** | Web Audio recording, Whisper transcription, post-vibe agent analysis | Phase 4 | Yes (with 7, 10) | Pending |
| 9 | **Boomerang & Bank** | Multi-agent orchestration, Axiom challenges, banking workflow | Phase 4, 6 | No | Pending |
| 10 | **Email Integration** | Resend setup, notification templates, send log | Phase 3 | Yes (with 7, 8) | Pending |
| 11 | **Settings & Admin** | API usage dashboard, voice provider config, org management | Phase 2, 4 | No | Pending |
| 12 | **VDBA & Export** | Publication workflow, PDF/DOCX export, sharing | Phase 9 | Yes (with 13) | Pending |
| 13 | **Heat Map & Analytics** | Real progress visualization, journey analytics | Phase 9 | Yes (with 12) | Pending |
| 14 | **Polish & Testing** | E2E tests, accessibility audit, performance optimization | All | No | Pending |

### 8.1 Phase Validation Criteria

| Phase | Pass Criteria |
|-------|--------------|
| 1 | `docker compose up` succeeds; `alembic upgrade head` runs clean; `GET /api/health` returns 200 with all checks passing; `pytest` passes with ≥1 test |
| 2 | Register → login → access protected route works; JWT refresh works; password reset flow end-to-end; roles enforced (viewer can't create) |
| 3 | CRUD for goals, journeys, perspectives via API; 12 perspectives auto-created on journey creation; status transitions enforced |
| 4 | Single agent chat returns SSE stream; boomerang runs all 9 agents; agent_sessions records created with token counts |
| 5 | All routes render; layout matches wireframes; theme switching works; responsive at 3 breakpoints |
| 6 | Left rail navigates dimensions/phases; agent cards display; heat map reflects perspective status; action bar functional |
| 7 | File upload to MinIO succeeds; file list renders; download works; delete removes from MinIO |
| 8 | Audio recording in browser works; upload + transcription succeeds; 9-agent analysis runs; results display |
| 9 | Boomerang → Axiom challenges → resolution flow; banking creates correct type per dimension/phase; decision audit populated |
| 10 | Email sends via Resend; delivery status tracked; email log displays |
| 11 | API usage charts render with real data; model selector saves; budget alert fires at threshold |
| 12 | VDBA publishes from completed journey; PDF export generates; download works |
| 13 | Heat map shows real completion status; cost per journey accurate; journey analytics display |
| 14 | Lighthouse score ≥ 90 performance; WCAG AA compliance; zero console errors; E2E tests pass |

## 9. Success Criteria

- [ ] User can create a goal and complete all 12 perspectives with AI agent guidance
- [ ] All 9 agents (including Axiom) produce contextual, intersection-aware responses
- [ ] Axiom produces defensible decision audit trails
- [ ] Post-vibe analysis extracts actionable items from voice sessions
- [ ] Documents persist in MinIO and survive page refresh
- [ ] Bank instances capture the full journey with audit trail
- [ ] VDBA can be published and exported as PDF
- [ ] Settings dashboard shows real-time API cost tracking
- [ ] Voice provider is configurable (Whisper default, pluggable)
- [ ] Email notifications send via Resend
- [ ] Full authentication with org-level multi-tenancy

## 10. UI/UX Detailed Specifications

### 10.1 Design Tokens

#### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#0A0E1A` | Main background (Space theme) |
| `--bg-secondary` | `#111827` | Card/panel backgrounds |
| `--bg-elevated` | `#1F2937` | Modals, dropdowns |
| `--text-primary` | `#F9FAFB` | Primary text |
| `--text-secondary` | `#9CA3AF` | Secondary/muted text |
| `--text-tertiary` | `#6B7280` | Placeholder, disabled text |
| `--border` | `#374151` | Default borders |
| `--accent-cyan` | `#06B6D4` | Architecture dimension |
| `--accent-purple` | `#A855F7` | Design dimension |
| `--accent-amber` | `#F59E0B` | Engineering dimension |
| `--phase-green` | `#22C55E` | Generate phase |
| `--phase-orange` | `#F97316` | Review phase |
| `--phase-blue` | `#3B82F6` | Validate phase |
| `--phase-purple` | `#8B5CF6` | Summarize phase |
| `--agent-lyra` | `#A855F7` | Lyra (Goal) |
| `--agent-mira` | `#EC4899` | Mira (Stakeholder) |
| `--agent-dex` | `#3B82F6` | Dex (Requirement) |
| `--agent-rex` | `#06B6D4` | Rex (Capability) |
| `--agent-vela` | `#EAB308` | Vela (Value) |
| `--agent-koda` | `#22C55E` | Koda (Value-Stream) |
| `--agent-halo` | `#F97316` | Halo (Value-Chain) |
| `--agent-nova` | `#EF4444` | Nova (Implementation) |
| `--agent-axiom` | `#94A3B8` | Axiom (Challenger) |
| `--success` | `#22C55E` | Success states |
| `--warning` | `#F59E0B` | Warning states |
| `--error` | `#EF4444` | Error states |

#### Typography

| Token | Font | Weight | Size | Line Height |
|-------|------|--------|------|-------------|
| `heading-1` | Inter | 700 | 32px | 40px |
| `heading-2` | Inter | 600 | 24px | 32px |
| `heading-3` | Inter | 600 | 20px | 28px |
| `body` | Inter | 400 | 16px | 24px |
| `body-small` | Inter | 400 | 14px | 20px |
| `caption` | Inter | 500 | 12px | 16px |
| `code` | JetBrains Mono | 400 | 14px | 20px |

#### Effects

| Token | Value | Usage |
|-------|-------|-------|
| `glass` | `backdrop-blur-xl bg-white/5 border border-white/10` | Glass morphism panels |
| `shadow-card` | `0 4px 24px rgba(0,0,0,0.3)` | Card elevation |
| `shadow-modal` | `0 8px 40px rgba(0,0,0,0.5)` | Modal elevation |
| `transition-default` | `150ms ease-out` | All interactive state changes |
| `transition-slow` | `300ms ease-in-out` | Page transitions, panel reveals |

### 10.2 Screen Wireframes

#### Dashboard (`/dashboard`)

```
┌─────────────────────────────────────────────────────────┐
│  InCube Logo          Welcome, Sarah    ⚙️  [Avatar]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Active Journeys (2)                    [+ New Journey] │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ Digital Trans │  │ Customer Exp │                     │
│  │ ████████░░░░  │  │ ██░░░░░░░░  │                     │
│  │ 8/12 · $1.24  │  │ 2/12 · $0.18 │                     │
│  │ [Continue →]  │  │ [Continue →]  │                     │
│  └──────────────┘  └──────────────┘                     │
│                                                         │
│  Recent VDBAs (1)                                       │
│  ┌──────────────────────────────────┐                   │
│  │ 📄 Ops Excellence Report  ↓ PDF  │                   │
│  │    Published Jan 15, 2026        │                   │
│  └──────────────────────────────────┘                   │
│                                                         │
│  This Month's Usage                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │ $4.82/20   │ │ 12 vibes   │ │ 8 emails   │          │
│  │ API cost   │ │ recorded   │ │ sent       │          │
│  └────────────┘ └────────────┘ └────────────┘          │
└─────────────────────────────────────────────────────────┘
```

**Data mappings:**
- Journey cards → `journeys.status = 'active'`, progress = `journeys.perspectives_completed / 12`, cost = `journeys.total_cost_cents`
- VDBA list → `vdbas` ordered by `published_at DESC`
- Usage stats → `api_usage` aggregated by current month

**States:**
- Empty: "Start your first journey" CTA with animated cube illustration
- Loading: Skeleton placeholders for journey cards and stats
- Error: "Couldn't load dashboard. [Retry]" banner

**Navigation:** Header links to all pages. Journey card → `/canvas?journey={id}`. VDBA row → `/vdbas/{id}`.

#### Canvas (`/canvas`)

```
┌─────────────────────────────────────────────────────────┐
│  InCube  |  Journey: Digital Transformation  |  ⚙️      │
├────────┬────────────────────────────────────────────────┤
│        │                                                │
│  ARCH  │  Architecture × Generate — Imagining           │
│  ○ Gen │                                                │
│  ○ Rev │  ┌─ Lyra (Goal) ──────────────────────┐       │
│  ○ Val │  │ "The strategic alignment looks strong│       │
│  ○ Sum │  │  for digital readiness. Key gap:     │       │
│        │  │  no stakeholder mapping yet."         │       │
│  DSGN  │  └──────────────────────────────────────┘       │
│  ○ Gen │                                                │
│  ○ Rev │  ┌─ Mira (Stakeholder) ───────────────┐       │
│  ○ Val │  │ "3 key stakeholder groups identified:│       │
│  ○ Sum │  │  CTO office, ops team, external..."  │       │
│        │  └──────────────────────────────────────┘       │
│  ENGR  │                                                │
│  ○ Gen │  [+ Show all 8 agent assessments]              │
│  ○ Rev │                                                │
│  ○ Val │  ┌─ Axiom Challenge ──────────────────┐       │
│  ○ Sum │  │ ⚠️ HIGH: Lyra and Mira disagree on  │       │
│        │  │ priority of regulatory stakeholders  │       │
│ ────── │  │ [View Resolution]                    │       │
│  HEAT  │  └──────────────────────────────────────┘       │
│ ┌────┐ │                                                │
│ │████│ │  ┌─────┬─────┬─────┬────────────┐             │
│ │░░░░│ │  │ 📄  │ 🎤  │ ✉️  │ 🔄 Boomerang│             │
│ │░░░░│ │  │Docs │Vibe │Email│             │             │
│ └────┘ │  └─────┴─────┴─────┴────────────┘             │
├────────┴────────────────────────────────────────────────┤
│  Block 5/12 ████████░░░░  │  Cost: $1.24  │ [Bank ✓]   │
└─────────────────────────────────────────────────────────┘
```

**Data mappings:**
- Left rail dimension indicators → `perspectives.status` for each dimension/phase combination
- Heat map → grid of `perspectives.status` (locked=dark, pending=dim, in_progress=active, completed=bright)
- Agent cards → `agent_sessions.response_payload` for latest session per agent in this perspective
- Axiom challenges → `axiom_challenges` where `resolution IS NULL`
- Progress bar → `journeys.perspectives_completed / 12`
- Cost → `journeys.total_cost_cents`
- Bank button → enabled only when `perspective.status = 'completed'`

**States:**
- Empty perspective: "Start by chatting with an agent or running a Boomerang" prompt
- Loading agent: Pulsing agent card with streaming text
- Axiom active: Challenge cards with amber border, resolution UI inline
- Perspective completed: Green checkmark, Bank button active

#### Bank (`/bank`)

```
┌─────────────────────────────────────────────────────────┐
│  InCube  |  Bank — Digital Transformation  |  ⚙️        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Timeline                                    [Filter ▾] │
│                                                         │
│  ──── Jan 20 ────────────────────────────────────────── │
│  │                                                      │
│  ├─ 🏦 Bankable: Architecture × Generate               │
│  │  "Initial strategic vision and stakeholder map..."   │
│  │  📄 3 docs  🎤 2 vibes  ✉️ 1 email                  │
│  │  [View Details →]                                    │
│  │                                                      │
│  ├─ 🏦 Bankable: Architecture × Review                 │
│  │  "Refined architecture with Axiom-validated..."      │
│  │  📄 5 docs  🎤 1 vibe  ✉️ 2 emails                  │
│  │  [View Details →]                                    │
│  │                                                      │
│  ──── Jan 22 ────────────────────────────────────────── │
│  │                                                      │
│  ├─ 🎬 Film: Architecture × Summarize                  │
│  │  "Complete Architecture dimension distilled..."      │
│  │  Includes 4 bankables + 2 Axiom decisions           │
│  │  [View Details →]                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Data mappings:**
- Timeline entries → `bank_instances` ordered by `created_at`, grouped by date
- Type badge → `bank_instances.type` (bankable/film/film_reel/published)
- Synopsis → `bank_instances.synopsis`
- Counts → `bank_instances.documents_count`, `vibes_count`, `emails_sent`

**States:**
- Empty: "Complete a perspective and bank it to start your timeline"
- Filter options: by dimension, by phase, by type

#### Login (`/auth/login`)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                     InCube Logo                         │
│                                                         │
│              ┌─────────────────────┐                    │
│              │  Sign In             │                    │
│              │                     │                    │
│              │  Email               │                    │
│              │  ┌─────────────────┐│                    │
│              │  │                 ││                    │
│              │  └─────────────────┘│                    │
│              │                     │                    │
│              │  Password            │                    │
│              │  ┌─────────────────┐│                    │
│              │  │            [👁️] ││                    │
│              │  └─────────────────┘│                    │
│              │                     │                    │
│              │  [Forgot password?]  │                    │
│              │                     │                    │
│              │  [    Sign In     ]  │                    │
│              │                     │                    │
│              │  No account?         │                    │
│              │  [Create one →]      │                    │
│              └─────────────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**States:**
- Default: Empty form, Sign In button disabled until both fields filled
- Loading: Button shows spinner, inputs disabled
- Error: Red border on invalid field, error message below field
- Rate limited: "Too many attempts. Try again in X minutes"

#### Settings (`/settings`)

```
┌─────────────────────────────────────────────────────────┐
│  InCube  |  Settings                        |  ⚙️       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [API Usage] [Voice] [Email] [Organization] [Account]   │
│                                                         │
│  ─── API Usage & Costs ─────────────────────────────── │
│                                                         │
│  This Month: $4.82 / $20.00 budget                     │
│  ┌─────────────────────────────────────────────┐       │
│  │  📊 Daily cost line chart (Recharts)         │       │
│  │  $                                           │       │
│  │  2.0─        ╱╲                              │       │
│  │  1.0─   ╱╲╱╱   ╲╱                           │       │
│  │  0.0─╱╱                                      │       │
│  │     Jan 1  Jan 8  Jan 15  Jan 22             │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  Per-Agent Breakdown:                                   │
│  Axiom ████████████ $1.82 (38%)                        │
│  Lyra  ██████       $0.92 (19%)                        │
│  Nova  █████        $0.78 (16%)                        │
│  ...                                                   │
│                                                         │
│  Model Settings:         Budget:                       │
│  Default: [Haiku ▾]      Monthly cap: [$20.00]         │
│  Axiom:   [Sonnet ▾]     Alerts at: 80%, 90%, 100%    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 10.3 Navigation Map

| From | To | Trigger |
|------|----|---------|
| Landing `/` | Login `/auth/login` | Click "Sign In" |
| Landing `/` | Register `/auth/register` | Click "Get Started" |
| Login | Dashboard `/dashboard` | Successful login |
| Register | Dashboard `/dashboard` | Successful registration |
| Dashboard | Canvas `/canvas?journey={id}` | Click journey card |
| Dashboard | VDBAs `/vdbas` | Click "View all VDBAs" |
| Any page | Settings `/settings` | Click settings icon |
| Canvas | Bank `/bank?journey={id}` | Click "Bank" after completing perspective |
| Canvas | Canvas (different perspective) | Click dimension/phase in left rail |
| Bank | Canvas `/canvas?perspective={id}` | Click "View Details" on bank instance |
| VDBAs | VDBA detail `/vdbas/{id}` | Click VDBA row |
| Any page | Dashboard `/dashboard` | Click InCube logo |

**Back/Cancel behavior:** Browser back button navigates history stack. All modal dialogs have "Cancel" that returns to previous state without saving. Unsaved changes trigger "Discard changes?" confirmation.

### 10.4 Responsive Breakpoints

| Viewport | Width | Layout Changes |
|----------|-------|---------------|
| Desktop | ≥1280px | Full layout as wireframed. Left rail + main canvas side by side |
| Tablet | 768–1279px | Left rail collapses to icon-only (expandable). Heat map moves to bottom sheet |
| Mobile | <768px | Single column. Left rail becomes top tabs. Action bar fixed bottom. Agent cards stack vertically |

### 10.5 Theme Variants

| Theme | `--bg-primary` | `--bg-secondary` | Accent gradient |
|-------|---------------|-------------------|----------------|
| Space (default) | `#0A0E1A` | `#111827` | Blue-purple radial |
| Forest | `#0A1A0E` | `#11271A` | Green-teal radial |
| Black Hole | `#1A0E0A` | `#271811` | Amber-red radial |

## 11. Business Logic & State Machines

### 11.1 Journey Lifecycle State Machine

```
                    create journey
                         │
                         ▼
                    ┌─────────┐
                    │  active  │
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          │
    ┌──────────────┐  ┌──────────┐ │
    │  archived    │  │completed │ │
    └──────────────┘  └──────────┘ │
              ▲                    │
              └────────────────────┘
```

| Transition | Trigger | Guard Condition |
|-----------|---------|-----------------|
| → active | Journey created | Goal exists |
| active → completed | `PATCH /journeys/:id/status` | All 12 perspectives `completed` |
| active → archived | `PATCH /journeys/:id/status` | User confirms (any state) |
| completed → archived | `PATCH /journeys/:id/status` | User confirms |

### 11.2 Perspective Status State Machine

```
    journey created
         │
         ▼
    ┌─────────┐     user starts      ┌─────────────┐     user banks      ┌───────────┐
    │  locked  │ ──────────────────→  │ in_progress  │ ──────────────────→ │ completed │
    └─────────┘                       └─────────────┘                      └───────────┘
         │
    prior phase completed
         │
         ▼
    ┌─────────┐
    │ pending  │
    └─────────┘
```

| Transition | Trigger | Guard Condition |
|-----------|---------|-----------------|
| → locked | Journey created (all except Generate row) | Default state for non-Generate |
| → pending | Journey created (Generate row only) | First phase starts unlocked |
| locked → pending | Prior phase in same dimension completed | `perspectives.status = 'completed'` for prior phase |
| pending → in_progress | User starts working (first agent chat, doc upload, or vibe) | Perspective is `pending` |
| in_progress → completed | User clicks "Complete" or banks the perspective | At least 1 agent session exists |

**Unlock order per dimension:** Generate → Review → Validate → Summarize (sequential within dimension). All three dimensions' Generate perspectives are available immediately.

### 11.3 Banking Type Determination

```python
def determine_bank_type(dimension: str, phase: str) -> str:
    """
    DO THIS: Use dimension + phase to determine bank type
    NOT THAT: Don't let the user pick the type manually
    """
    if phase != "summarize":
        return "bankable"
    elif dimension in ("architecture", "design"):
        return "film"
    elif dimension == "engineering":
        return "film_reel"
    # "published" is set only via the VDBA publication endpoint
```

### 11.4 Cost Calculation

```python
# Model pricing (per million tokens, as of 2026-01)
MODEL_PRICING = {
    "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},    # $1/$5 per M tokens
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},  # $3/$15 per M tokens
}

def calculate_cost_cents(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Example 1 (normal): Haiku, 500 input, 1200 output
      input_cost  = (500 / 1_000_000) * 1.00 = $0.0005
      output_cost = (1200 / 1_000_000) * 5.00 = $0.006
      total = $0.0065 = 0.65 cents

    Example 2 (edge - zero output): Haiku, 300 input, 0 output (timeout/error)
      total = (300 / 1_000_000) * 1.00 = $0.0003 = 0.03 cents
    """
    pricing = MODEL_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round((input_cost + output_cost) * 100, 4)  # Convert to cents, 4 decimal places
```

### 11.5 Budget Alert Logic

```python
def check_budget_alert(org_id: str) -> Optional[str]:
    """
    Check monthly spend against budget and return alert level.
    Alerts fire at 80%, 90%, and 100% thresholds.

    Example: Budget = $20.00 (2000 cents), current spend = $16.50 (1650 cents)
      percentage = 1650 / 2000 = 82.5%
      → Returns "warning_80" (first threshold crossed)

    Edge case: Budget = 0 (unlimited) → never alert
    """
    budget = get_org_budget(org_id)  # monthly_budget_cents
    if budget == 0:
        return None
    spent = get_monthly_spend(org_id)  # SUM(api_usage.cost_cents) WHERE month = current
    percentage = (spent / budget) * 100
    if percentage >= 100:
        return "critical_100"  # Send email, show red banner, block non-admin API calls
    elif percentage >= 90:
        return "warning_90"   # Send email, show amber banner
    elif percentage >= 80:
        return "warning_80"   # Show amber banner (no email)
    return None
```

### 11.6 Boomerang Orchestration Flow

```python
async def run_boomerang(perspective_id: str, prompt: str) -> AsyncGenerator:
    """
    1. Run 8 specialist agents in parallel
    2. Collect all outputs
    3. Run Axiom on the collected outputs
    4. If Axiom challenges: route to targeted agents → collect responses → Axiom verdict
    5. Yield SSE events throughout

    CRITICAL: Axiom bounded to max 3 LLM calls per challenge:
      Call 1: Axiom produces challenge
      Call 2: Targeted agents respond (parallel, but counts as 1 "round")
      Call 3: Axiom evaluates and produces verdict
    DO NOT allow unbounded back-and-forth. If verdict is ACTION_REQUIRED after 3 calls, log it and move on.
    """
    # Step 1: 8 specialists in parallel
    specialist_results = await asyncio.gather(*[
        run_agent(perspective_id, agent, prompt)
        for agent in SPECIALISTS  # All except Axiom
    ])

    # Step 2: Axiom challenge
    axiom_input = format_specialist_outputs(specialist_results)
    challenges = await run_axiom_challenge(perspective_id, axiom_input)

    # Step 3: For each challenge, single round of response + verdict
    for challenge in challenges:
        responses = await asyncio.gather(*[
            get_agent_response_to_challenge(perspective_id, agent, challenge)
            for agent in challenge.targeted_agents
        ])
        verdict = await run_axiom_verdict(perspective_id, challenge, responses)
        # verdict is one of: RESOLVED, ACCEPTED_RISK, ACTION_REQUIRED
```

### 11.7 Input Validation Rules

| Field | Type | Min | Max | Format | Error Message |
|-------|------|-----|-----|--------|--------------|
| email | string | 5 | 320 | RFC 5322 | "Enter a valid email address" |
| password | string | 8 | 128 | ≥1 upper + ≥1 digit | "Password must be at least 8 characters with 1 uppercase and 1 number" |
| name | string | 1 | 255 | - | "Name is required" |
| organization_name | string | 1 | 255 | - | "Organization name is required" |
| goal.title | string | 1 | 500 | - | "Goal title is required" |
| goal.description | string | 0 | 10000 | - | - |
| agent chat message | string | 1 | 10000 | - | "Message cannot be empty" |
| bank synopsis | string | 1 | 5000 | - | "Synopsis is required to bank" |
| vdba.title | string | 1 | 500 | - | "VDBA title is required" |
| file upload | binary | 1B | 50MB | pdf,docx,xlsx,pptx,txt,md,csv,png,jpg | "File type not allowed" or "File too large (max 50MB)" |
| audio upload | binary | 1B | 100MB | webm,wav,mp3 | "Audio format not supported" or "File too large (max 100MB)" |

## 12. External Integrations

### 12.1 Claude API (Anthropic)

| Property | Value |
|----------|-------|
| Base URL | `https://api.anthropic.com` |
| API Version | `2024-01-01` (via `anthropic-version` header) |
| Auth | API key in `ANTHROPIC_API_KEY` env var |
| SDK | `anthropic` Python SDK (Claude Agent SDK wrapper) |
| Rate limits | Tier-dependent (default: 60 RPM, 100K tokens/min) |
| Models used | `claude-haiku-4-5-20251001` (default), `claude-sonnet-4-5-20250929` (configurable per agent) |

**Error handling:**
- Timeout (30s): Retry once with exponential backoff (2s), then return 503 to client
- 429 Rate limited: Queue request, retry after `retry-after` header value
- 500/503: Retry once after 5s, then return 503 with "AI service temporarily unavailable"
- 401 Auth failure: Log critical error, alert admin, return 503

**Data mapping:**
| Claude API field | Internal field |
|-----------------|----------------|
| `usage.input_tokens` | `agent_sessions.input_tokens` |
| `usage.output_tokens` | `agent_sessions.output_tokens` |
| `content[0].text` | `agent_sessions.response_payload.text` |
| `model` | `agent_sessions.model_used` |

### 12.2 Whisper API (OpenAI)

| Property | Value |
|----------|-------|
| Base URL | `https://api.openai.com/v1` |
| Endpoint | `/audio/transcriptions` |
| Auth | API key in `OPENAI_API_KEY` env var |
| Model | `whisper-1` |
| Max file size | 25MB (split longer recordings) |
| Rate limits | 50 RPM |

**Error handling:**
- Timeout (120s for long audio): Retry once, then mark vibe session as `failed`
- 400 Invalid audio: Mark session `failed`, notify user "Audio format not recognized"
- 429: Queue, retry after delay

**Data mapping:**
| Whisper field | Internal field |
|--------------|----------------|
| `text` | `vibe_sessions.transcript_text` |

### 12.3 Resend (Email)

| Property | Value |
|----------|-------|
| Base URL | `https://api.resend.com` |
| Auth | API key in `RESEND_API_KEY` env var |
| From address | Configurable in settings, default `noreply@incube.ai` |
| Rate limits | 10 emails/second |

**Error handling:**
- 422 Invalid recipient: Mark `email_log.delivery_status = 'failed'`, show error to user
- 429: Queue with 1s delay
- 500: Retry once after 5s, mark as `failed` if still failing

### 12.4 MinIO (File Storage)

| Property | Value |
|----------|-------|
| Endpoint | `localhost:9000` (dev), internal Docker network (prod) |
| Auth | Access key + secret key in env vars `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` |
| Bucket | `incube-documents` (auto-created on startup) |

**Key format:** `{org_id}/{journey_id}/{perspective_id}/{type}/{uuid}.{ext}`
- type: `documents`, `audio`, `transcripts`, `exports`

**Error handling:**
- Connection refused: Health check fails, return 503
- Upload timeout (60s): Retry once, then return 500

### 12.5 Credential Management

| Credential | Storage | Rotation | Environment Scoping |
|-----------|---------|----------|-------------------|
| `ANTHROPIC_API_KEY` | Env var | Manual, no expiry | Different key per env |
| `OPENAI_API_KEY` | Env var | Manual, no expiry | Different key per env |
| `RESEND_API_KEY` | Env var | Manual, no expiry | Different key per env |
| `MINIO_ACCESS_KEY` | Env var | Manual | Same in dev, different in prod |
| `MINIO_SECRET_KEY` | Env var | Manual | Same in dev, different in prod |
| `JWT_SECRET` | Env var | Manual, rotate quarterly | Different per env, min 256-bit |
| `DATABASE_URL` | Env var | N/A | `localhost:5434/incube_dev` (dev), Docker internal (prod) |
| `REDIS_URL` | Env var | N/A | `localhost:6379` (dev), Docker internal (prod) |

All credentials accessed via Python `pydantic-settings` BaseSettings class. Never stored in database, never logged, never returned in API responses.

## 13. Logging & Observability

### 13.1 Structured Log Format

```json
{
  "timestamp": "2026-01-15T14:30:00.123Z",
  "level": "INFO",
  "log_type": "HTTP_REQUEST",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-uuid",
  "org_id": "org-uuid",
  "message": "POST /api/perspectives/abc/agents/lyra/chat 200 1.2s",
  "data": {
    "method": "POST",
    "path": "/api/perspectives/abc/agents/lyra/chat",
    "status": 200,
    "duration_ms": 1200,
    "agent": "lyra",
    "tokens_in": 500,
    "tokens_out": 1200
  }
}
```

### 13.2 Log Types

| Log Type | When | Key Fields |
|----------|------|-----------|
| `HTTP_REQUEST` | Every API request | method, path, status, duration_ms, user_id |
| `HTTP_RESPONSE` | Every API response | status, content_length, response_time |
| `EXTERNAL_API` | Claude/Whisper/Resend calls | service, endpoint, status, duration_ms, tokens |
| `DB_QUERY` | Slow queries (>100ms) | query (parameterized), duration_ms, rows_affected |
| `AI_TOOL_CALL` | Agent tool invocations | agent, tool_name, parameters, result_summary |
| `AUTH` | Login/logout/register/password reset | event, email (masked), success, ip_address |
| `BUSINESS_EVENT` | Journey/perspective state changes, banking, publication | event, entity_id, old_state, new_state |
| `ERROR` | Unhandled exceptions, business rule violations | error_type, stack_trace, context |
| `SYSTEM` | Startup, shutdown, health checks, migrations | event, version, uptime |

### 13.3 Example Logs

**Agent Chat:**
```json
{"timestamp": "2026-01-15T14:30:01Z", "level": "INFO", "log_type": "EXTERNAL_API", "request_id": "req-123", "message": "Claude API call completed", "data": {"service": "claude", "model": "claude-haiku-4-5-20251001", "agent": "lyra", "tokens_in": 500, "tokens_out": 1200, "cost_cents": 0.65, "duration_ms": 1200}}
```

**Auth Event:**
```json
{"timestamp": "2026-01-15T14:25:00Z", "level": "INFO", "log_type": "AUTH", "request_id": "req-456", "message": "Login successful", "data": {"event": "login", "email": "s***h@acme.com", "ip": "192.168.1.100"}}
```

**Business Event:**
```json
{"timestamp": "2026-01-15T14:35:00Z", "level": "INFO", "log_type": "BUSINESS_EVENT", "request_id": "req-789", "message": "Perspective completed", "data": {"event": "perspective_completed", "perspective_id": "persp-abc", "dimension": "architecture", "phase": "generate", "journey_id": "journey-xyz"}}
```

### 13.4 Correlation / Request Tracing

- `request_id` (UUID v4) generated in FastAPI middleware for every incoming request
- Propagated via `X-Request-ID` header to external API calls
- Included in all log entries for the request lifecycle
- Returned in API response `meta.request_id` field
- For async jobs (vibe analysis, email): parent `request_id` stored, new `job_id` generated

### 13.5 Logging Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | Minimum log level: DEBUG, INFO, WARNING, ERROR |
| `LOG_FORMAT` | string | `json` | Output format: `json` (production) or `text` (development) |
| `LOG_FILE` | string | `stdout` | Log destination: `stdout` or file path |
| `LOG_INCLUDE_SENSITIVE` | bool | `false` | Include request bodies in logs (dev only, never in prod) |
| `SLOW_QUERY_THRESHOLD_MS` | int | `100` | Log DB queries slower than this |

## 14. Notifications & Communication

### 14.1 Notification Trigger Matrix

| Event | In-App | Email | Timing |
|-------|--------|-------|--------|
| Journey completed (all 12 perspectives) | Yes | Yes | Immediate |
| Axiom HIGH severity challenge | Yes | No | Immediate |
| Budget alert at 80% | Yes | No | Immediate |
| Budget alert at 90% | Yes | Yes | Immediate |
| Budget alert at 100% | Yes | Yes | Immediate |
| VDBA published | Yes | Yes | Immediate |
| Vibe analysis complete | Yes | No | Immediate |
| Stakeholder email bounced | Yes | No | Immediate |
| User invited to organization | N/A | Yes | Immediate |
| Password reset requested | N/A | Yes | Immediate |
| Email verification | N/A | Yes | Immediate |

### 14.2 Email Templates

**Stakeholder Invite:**
- Subject: `"[InCube] {{user_name}} is requesting your input on {{journey_title}}"`
- Body: Greeting, context about the perspective, custom message from user, link to provide feedback
- Recipient: Custom email entered by user

**Journey Complete:**
- Subject: `"[InCube] Journey Complete: {{journey_title}}"`
- Body: Summary of completed journey, perspective count, total cost, link to publish as VDBA
- Recipient: Journey creator + org admins

**VDBA Published:**
- Subject: `"[InCube] VDBA Published: {{vdba_title}}"`
- Body: Publication summary, export format, download link
- Recipient: All org members

**Budget Alert (90%/100%):**
- Subject: `"[InCube] Budget Alert: {{percentage}}% of monthly limit reached"`
- Body: Current spend, budget limit, breakdown by top 3 agents, link to settings
- Recipient: Org admins only

### 14.3 Notification Preferences

Stored in `settings` table per organization:

```json
{
  "notification_preferences": {
    "journey_complete": { "in_app": true, "email": true },
    "axiom_high": { "in_app": true, "email": false },
    "budget_80": { "in_app": true, "email": false },
    "budget_90": { "in_app": true, "email": true },
    "budget_100": { "in_app": true, "email": true },
    "vdba_published": { "in_app": true, "email": true },
    "vibe_complete": { "in_app": true, "email": false }
  }
}
```

Users cannot disable security-critical emails (password reset, email verification, budget 100%).

## 15. AI Agent Specifications

### 15.1 Agent Personas

| Agent | Tone | Personality | Error Recovery |
|-------|------|-------------|----------------|
| **Lyra** | Authoritative, focused | Strategic thinker, outcome-oriented. Uses metrics and KPIs. | "I need more context about your strategic goals. Could you describe what success looks like?" |
| **Mira** | Warm, inclusive | People-first, empathetic. Asks about who is affected. | "I'd like to understand the stakeholders better. Who are the key people involved?" |
| **Dex** | Precise, methodical | Detail-oriented, structured. Produces testable criteria. | "That requirement is ambiguous. Let me ask a few clarifying questions..." |
| **Rex** | Pragmatic, grounded | Reality-checker, capability assessor. Identifies feasibility. | "Before we proceed, let's verify what resources and capabilities are actually available." |
| **Vela** | Analytical, business-focused | ROI-driven, value quantifier. Puts numbers on everything. | "I need more data points to assess value. What's the current cost of this process?" |
| **Koda** | Systematic, flow-oriented | Process optimizer, waste identifier. Thinks in value streams. | "Let me map out the current process flow. Where does work typically get stuck?" |
| **Halo** | Holistic, integrative | Systems thinker, connection spotter. Sees cross-cutting concerns. | "This connects to something we discussed in another dimension. Let me pull that context..." |
| **Nova** | Action-oriented, practical | Builder, execution planner. Turns plans into steps. | "Let me break this down into concrete, actionable steps we can start on immediately." |
| **Axiom** | Direct, challenging | Devil's advocate, evidence demander. Respectfully confrontational. | "I'm not convinced by this reasoning. Here's specifically what concerns me..." |

### 15.2 System Prompt Requirements

All agent system prompts MUST include:
1. Agent identity (name, role, specialty)
2. Current context (goal title, dimension, phase, perspective name)
3. Existing documents summary (if any)
4. Previous agent sessions in this perspective (conversation continuity)
5. Bank state (what has been banked so far in this journey)
6. Instructions to produce structured output with confidence score (0-100)
7. Axiom-specific: instruction to limit to max 3 LLM calls per challenge
8. Instruction to never fabricate facts or make up data
9. Instruction to flag when more information is needed rather than guessing

### 15.3 Conversation Example — Happy Path

**Context:** Architecture × Generate, goal = "Digital Transformation Readiness"

```
User: "We need to assess our organization's readiness for digital transformation.
       We're a mid-size manufacturing company with 500 employees."

Lyra: "Based on your context, I'll frame this around three strategic readiness pillars:
       1. Technology Infrastructure Maturity
       2. Organizational Change Capacity
       3. Digital Skills Gap Analysis

       Each maps to measurable outcomes:
       - Pillar 1: Current system integration score (baseline → target)
       - Pillar 2: Change readiness survey results
       - Pillar 3: Skills inventory vs. required capabilities

       Confidence: 75/100 — I'd like to know more about your current tech stack
       and any previous transformation attempts."

User: "We tried an ERP migration 2 years ago that failed halfway through."

Lyra: "That's critical context. The failed ERP migration tells me:
       - Change management was likely insufficient (Pillar 2 risk: HIGH)
       - There may be organizational resistance to technology change
       - Previous investment was lost, so ROI justification needs to be stronger

       Updated confidence: 85/100.
       I recommend Mira do a stakeholder analysis focusing on who was
       involved in the ERP failure and what lessons were captured."
```

### 15.4 Conversation Example — Error Recovery

```
User: "Just analyze everything and give me the answer."

Lyra: "I appreciate wanting to move quickly, but I need specific context to give you
       actionable strategic guidance. Let me start with three focused questions:

       1. What is your organization's primary business objective for the next 12 months?
       2. What triggered the need for transformation now?
       3. Do you have a rough budget range in mind?

       Even brief answers will help me produce something meaningful rather than generic."
```

### 15.5 AI Interface States

| State | Trigger | Visual | Transition |
|-------|---------|--------|------------|
| Idle | No active agent call | Agent card collapsed, just name + icon | → Streaming (on user message or boomerang) |
| Streaming | LLM call in progress | Card expanded, text appears word-by-word, pulsing border in agent color | → Complete (stream ends) or → Error (stream fails) |
| Complete | Stream `done` event | Full text visible, cost badge shown, fade pulse to solid border | → Idle (after 2s) |
| Error | Stream `error` event or timeout | Red border, error message, "Retry" button | → Streaming (on retry) or → Idle (on dismiss) |
| Challenging | Axiom challenge active | Amber border, challenge text, "View" button | → Resolved (verdict received) |
| Resolved | Axiom verdict received | Green (resolved) or amber (accepted risk) or red (action required) badge | → Idle (after 3s) |

## 16. Project Scaffolding & Configuration

### 16.1 Folder Structure

```
incube-portal/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app creation, middleware, startup events
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py            # Dependency injection (get_db, get_current_user)
│   │   │   └── routes/
│   │   │       ├── auth.py        # /api/auth/*
│   │   │       ├── goals.py       # /api/goals/*
│   │   │       ├── journeys.py    # /api/journeys/*
│   │   │       ├── perspectives.py
│   │   │       ├── agents.py      # /api/perspectives/:id/agents/*
│   │   │       ├── documents.py
│   │   │       ├── vibes.py
│   │   │       ├── bank.py
│   │   │       ├── vdbas.py
│   │   │       ├── email.py
│   │   │       ├── settings.py
│   │   │       └── health.py
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic BaseSettings config class
│   │   │   ├── security.py        # JWT encode/decode, password hashing
│   │   │   └── middleware.py      # Request ID, CORS, rate limiting, logging
│   │   ├── db/
│   │   │   ├── session.py         # AsyncSession factory
│   │   │   ├── base.py            # Base model with id, created_at, updated_at
│   │   │   └── seed.py            # Seed data script
│   │   ├── models/                # SQLAlchemy models (one file per table)
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── agent_service.py   # Claude Agent SDK wrapper, all 9 agents
│   │   │   ├── axiom_service.py   # Bounded debate protocol
│   │   │   ├── vibe_service.py    # Audio upload, Whisper transcription, analysis
│   │   │   ├── bank_service.py    # Banking logic, type determination
│   │   │   ├── email_service.py   # Resend integration
│   │   │   ├── export_service.py  # PDF/DOCX generation
│   │   │   └── storage_service.py # MinIO operations
│   │   └── workers/
│   │       └── tasks.py           # Background job definitions (Redis queue)
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py            # Fixtures: test DB, test client, auth helpers
│   │   ├── test_auth.py
│   │   ├── test_journeys.py
│   │   └── ...
│   ├── pyproject.toml
│   ├── alembic.ini
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                   # Next.js App Router
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   ├── (app)/             # Protected routes (require auth)
│   │   │   │   ├── layout.tsx     # App shell with header + sidebar
│   │   │   │   ├── dashboard/page.tsx
│   │   │   │   ├── canvas/page.tsx
│   │   │   │   ├── bank/page.tsx
│   │   │   │   ├── vdbas/page.tsx
│   │   │   │   ├── fundamentals/page.tsx
│   │   │   │   └── settings/page.tsx
│   │   │   ├── globals.css
│   │   │   └── layout.tsx         # Root layout (theme provider, query client)
│   │   ├── components/
│   │   │   ├── ui/                # shadcn/ui components
│   │   │   ├── layout/            # Header, Sidebar, Navigation
│   │   │   ├── canvas/            # LeftRail, HeatMap, ActionBar, ProgressFooter
│   │   │   ├── agents/            # AgentCard, AgentStream, AxiomChallenge
│   │   │   ├── editors/           # DocumentEditor (TipTap), SpreadsheetViewer
│   │   │   ├── vibe/              # VoiceRecorder, Waveform, TranscriptViewer
│   │   │   └── bank/              # Timeline, BankCard, Synopsis
│   │   ├── hooks/
│   │   │   ├── use-auth.ts        # Auth state + token refresh
│   │   │   ├── use-sse.ts         # SSE connection management
│   │   │   ├── use-agent.ts       # Agent chat + streaming
│   │   │   └── use-vibe.ts        # Audio recording + upload
│   │   ├── stores/
│   │   │   ├── journey-store.ts   # Active journey state
│   │   │   ├── canvas-store.ts    # Current perspective, agent states
│   │   │   └── settings-store.ts  # User preferences
│   │   ├── lib/
│   │   │   ├── api.ts             # Fetch wrapper with auth headers
│   │   │   └── utils.ts           # Date formatting, cost formatting
│   │   └── types/
│   │       └── index.ts           # TypeScript type definitions matching API schemas
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── tsconfig.json
├── docker-compose.dev.yml
├── docker-compose.yml             # Production
└── CLAUDE.md
```

### 16.2 Entry Points

| Entry Point | Command | Description |
|-------------|---------|-------------|
| Backend API | `uvicorn app.main:app --reload --port 8000` | FastAPI development server |
| Frontend | `npm run dev` (port 3001) | Next.js development server |
| Database migrations | `alembic upgrade head` | Run pending migrations |
| Database seed | `python -m app.db.seed` | Insert seed data |
| Background worker | `arq app.workers.tasks.WorkerSettings` | Redis-backed job processor |

### 16.3 Environment Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `DATABASE_URL` | string | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | string | Yes | `redis://localhost:6379` | Redis connection string |
| `JWT_SECRET` | string | Yes | - | JWT signing secret (min 256-bit) |
| `JWT_ACCESS_MINUTES` | int | No | `15` | Access token TTL |
| `JWT_REFRESH_DAYS` | int | No | `7` | Refresh window TTL |
| `ANTHROPIC_API_KEY` | string | Yes | - | Claude API key |
| `OPENAI_API_KEY` | string | Yes | - | Whisper API key |
| `RESEND_API_KEY` | string | Yes | - | Resend email API key |
| `RESEND_FROM_EMAIL` | string | No | `noreply@incube.ai` | Default from address |
| `MINIO_ENDPOINT` | string | No | `localhost:9000` | MinIO server URL |
| `MINIO_ACCESS_KEY` | string | Yes | - | MinIO access key |
| `MINIO_SECRET_KEY` | string | Yes | - | MinIO secret key |
| `MINIO_BUCKET` | string | No | `incube-documents` | Default bucket name |
| `LOG_LEVEL` | string | No | `INFO` | Minimum log level |
| `LOG_FORMAT` | string | No | `json` | Log output format |
| `CORS_ORIGINS` | string | No | `http://localhost:3001` | Comma-separated allowed origins |
| `DEFAULT_MODEL` | string | No | `claude-haiku-4-5-20251001` | Default Claude model |

### 16.4 Configuration Loading

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Config loads in priority order:
    1. Environment variables (highest)
    2. .env file
    3. Default values (lowest)

    Validated on startup — app fails fast if required vars are missing.
    """
    database_url: str
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str
    jwt_access_minutes: int = 15
    jwt_refresh_days: int = 7
    anthropic_api_key: str
    openai_api_key: str
    resend_api_key: str
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "incube-documents"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3001"
    default_model: str = "claude-haiku-4-5-20251001"

    class Config:
        env_file = ".env"
```

### 16.5 Base Patterns

**Base Model (SQLAlchemy):**
```python
class BaseModel(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())
```

**Base Service (Dependency Injection):**
```python
class BaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

# Usage in routes:
async def get_journey_service(db: AsyncSession = Depends(get_db)) -> JourneyService:
    return JourneyService(db)
```

**Error Hierarchy:**
```python
class AppError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"

class ValidationError(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"

class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"

class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
```

### 16.6 Background Jobs

| Job | Trigger | Schedule | Description | Retry |
|-----|---------|----------|-------------|-------|
| `transcribe_audio` | Vibe upload | Event-driven | Send audio to Whisper, store transcript | 2 retries, 30s backoff |
| `analyze_vibe` | Transcription complete | Event-driven | Run 9 agents on transcript | 1 retry, 60s backoff |
| `generate_export` | VDBA publish | Event-driven | Generate PDF/DOCX from bank data | 2 retries, 30s backoff |
| `check_budgets` | Cron | Every hour | Check all org budgets, send alerts | Idempotent (safe to re-run) |
| `cleanup_expired_tokens` | Cron | Daily at 3 AM | Delete expired auth_tokens | Idempotent |

All jobs are idempotent — safe to retry without side effects. Each job checks its preconditions before executing (e.g., `transcribe_audio` checks if transcript already exists).

## 17. End-to-End User Journey

### 17.1 Primary Journey — Creating a VDBA

**Persona:** Sarah, a business transformation consultant at Acme Consulting

**Goal:** Create a "Digital Transformation Readiness Assessment" for her client, a mid-size manufacturer

**Step-by-step:**

1. **Sarah registers** → `POST /api/auth/register` with email "sarah@acme.com", org "Acme Consulting"
   - DB: Creates `organizations` row, `users` row (admin), 5 default `settings` rows
   - UI: Redirected to `/dashboard` (empty state: "Start your first journey")

2. **Sarah creates a goal** → clicks "+ New Journey" → selects predefined goal "Digital Transformation Readiness Assessment"
   - `POST /api/goals` → `POST /api/journeys`
   - DB: Creates `goals` row, `journeys` row (active), 12 `perspectives` rows (Generate unlocked, rest locked)
   - UI: Redirected to `/canvas?journey={id}` showing Architecture × Generate

3. **Sarah chats with Lyra** → types "We're a 500-person manufacturer exploring digital transformation"
   - `POST /api/perspectives/{id}/agents/lyra/chat`
   - SSE stream: Lyra responds about strategic readiness pillars
   - DB: `agent_sessions` row (input_tokens=320, output_tokens=890, cost_cents=0.48)
   - UI: Agent card expands with streaming text

4. **Sarah records a vibe** → clicks microphone, speaks for 3 minutes about her client's failed ERP migration
   - Clicks stop → `POST /api/perspectives/{id}/vibes` with audio file
   - Background job: Whisper transcription (cost: $0.036 for 3 min at $0.006/min)
   - Background job: All 9 agents analyze transcript
   - DB: `vibe_sessions` row, 9 `vibe_analyses` rows, 9 `agent_sessions` rows
   - UI: Notification "Vibe analysis complete" → shows analysis report

5. **Sarah runs a Boomerang** → clicks "Boomerang" button
   - `POST /api/perspectives/{id}/boomerang`
   - SSE stream: 8 specialists run in parallel, then Axiom challenges
   - Axiom finds HIGH severity challenge: "Lyra and Vela disagree on ROI timeline"
   - Targeted agents respond → Axiom verdict: RESOLVED (evidence provided)
   - DB: 9 `agent_sessions` rows, 1 `axiom_challenges` row (resolved)
   - UI: All 9 agent cards populate, Axiom challenge shown and resolved

6. **Sarah completes the perspective** → clicks "Complete" then "Bank"
   - `PATCH /api/perspectives/{id}/status` (→ completed)
   - `POST /api/perspectives/{id}/bank` with synopsis
   - DB: `bank_instances` row (type=bankable), `perspectives.status = 'completed'`
   - Side effect: Architecture × Review unlocked (status → pending)
   - UI: Green checkmark on Architecture × Generate in left rail, Review now clickable

7. **Sarah repeats steps 3-6** for all 12 perspectives (days/weeks of work)

8. **Sarah publishes the VDBA** → navigates to Bank, clicks "Publish"
   - `POST /api/journeys/{id}/publish` with title "Acme Digital Readiness Assessment"
   - Background job: Generates PDF export
   - DB: `vdbas` row, journey status → completed
   - UI: Redirected to `/vdbas/{id}` with download button

### 17.2 Alternate Path — Budget Exceeded

During step 5, if Sarah's organization hits the 100% budget threshold:
1. `check_budgets` job detects 100% → creates notification + sends email to admins
2. Next API call from non-admin returns 422: "Monthly budget exceeded. Contact your admin."
3. Admin can increase budget in Settings → immediately unblocks API calls
4. Sarah retries the Boomerang → succeeds

### 17.3 Alternate Path — Vibe Transcription Fails

During step 4, if Whisper returns an error:
1. `transcribe_audio` job fails → retries twice (30s backoff each)
2. If still failing: `vibe_sessions.status = 'failed'`
3. UI shows: "Transcription failed. [Retry] or [Upload again]"
4. Sarah clicks Retry → re-queues the job
5. Data preserved: original audio still in MinIO, no data loss

## 18. Concurrency & Data Integrity

### 18.1 Concurrent Access Strategy

| Resource | Strategy | Implementation |
|----------|----------|---------------|
| Perspective status | Optimistic locking | `updated_at` column checked in WHERE clause on status updates. If row was modified since read, return 409 Conflict |
| Journey cost aggregation | Eventual consistency | `total_cost_cents` updated after each agent session via DB trigger or service-level SUM |
| Settings updates | Last-write-wins | Acceptable for settings — admin-only, low contention |
| Bank instances | Single-writer | Only one bank per perspective per type — UNIQUE constraint prevents duplicates |
| File uploads | Idempotent | MinIO key includes UUID — no collisions possible |

### 18.2 Transaction Boundaries

| Operation | Scope | Rollback Behavior |
|-----------|-------|-------------------|
| Register (org + user + settings) | Single transaction | All or nothing — no orphan org without admin user |
| Create journey + 12 perspectives | Single transaction | No journey without its 12 perspectives |
| Complete perspective + unlock next | Single transaction | Perspective and next perspective status updated atomically |
| Bank + update perspective status | Single transaction | Can't bank without completing, can't complete without banking |
| Publish VDBA + complete journey | Single transaction | Journey marked complete only if VDBA record created |

### 18.3 Idempotency

| Operation | Strategy |
|-----------|----------|
| Vibe transcription job | Check `vibe_sessions.transcript_text IS NOT NULL` before processing |
| Vibe analysis job | Check `vibe_analyses` count for session — skip if 9 exist |
| Export generation | Check `vdbas.export_url IS NOT NULL` before regenerating |
| Budget alert emails | Track last alert level sent in settings — don't re-send same level |
| Webhook retries (Resend) | `resend_message_id` used to deduplicate delivery status updates |

### 18.4 Known Race Conditions

| Scenario | Mitigation |
|----------|-----------|
| Two users start same perspective simultaneously | First `PATCH` to `in_progress` wins; second gets 409 with "Perspective already in progress" |
| Boomerang running while user chats with individual agent | Both allowed — separate agent_sessions. Boomerang results don't overwrite chat results |
| Budget check runs during active API call | Budget checked pre-call (soft limit). If exceeded during call, the call completes but next call blocked |

## 19. Deployment & Infrastructure

### 19.1 Deployment Method

| Component | Method | Port |
|-----------|--------|------|
| Frontend | Docker container (Node.js 20 alpine, `next start`) | 3001 |
| Backend | Docker container (Python 3.12 slim, `uvicorn`) | 8000 |
| PostgreSQL | Docker container (postgres:16-alpine) | 5432 (internal), 5434 (dev exposed) |
| Redis | Docker container (redis:7-alpine) | 6379 |
| MinIO | Docker container (minio/minio) | 9000 (API), 9001 (console) |
| Reverse proxy | Nginx (Docker or host) | 80/443 |

### 19.2 Health Check Specification

**Endpoint:** `GET /api/health`

**Checks performed:**
1. Database: `SELECT 1` query, must respond in <5s
2. Redis: `PING` command, must respond in <2s
3. MinIO: `list_buckets()` call, must respond in <5s

**Response format:** See section 5.4.15

**Failure behavior:** Returns 503 with failed check details. Load balancer removes instance from rotation.

### 19.3 Startup Order

```
1. PostgreSQL  (must be ready before backend)
2. Redis       (must be ready before backend)
3. MinIO       (must be ready before backend)
4. Backend     (waits for DB/Redis/MinIO health, runs migrations on startup)
5. Worker      (waits for Redis + DB)
6. Frontend    (waits for backend health endpoint)
```

Docker Compose `depends_on` with `condition: service_healthy` enforces this order.

### 19.4 Migration Strategy

- **Tool:** Alembic
- **File naming:** Auto-generated: `{revision_hash}_{description}.py`
- **Up/Down:** All migrations have both `upgrade()` and `downgrade()` functions
- **Rollback:** `alembic downgrade -1` to rollback one step
- **Dev seed data:** `python -m app.db.seed` — safe to re-run (uses upserts)
- **Production:** Never seed production. Migrations only create schema, not data.
- **Auto-run:** Backend startup event runs `alembic upgrade head` before accepting requests

### 19.5 Database Environment Separation

| Property | Development | Production |
|----------|------------|------------|
| Database name | `incube_dev` | `incube` |
| Host | `localhost:5434` (exposed Docker port) | Docker internal network |
| Docker Compose file | `docker-compose.dev.yml` | `docker-compose.yml` |
| Seed data | Yes (predefined goals, test org) | No |
| Credentials | Hardcoded in compose file | Environment variables / secrets manager |
| Backups | None | Daily automated (pg_dump to S3) |

**Rule:** Dev DATABASE_URL must never point to production. Enforced by different port (5434 vs 5432) and different database name.

## 20. Worked Examples & Gotchas

### 20.1 Cost Calculation Examples

**Example 1 — Normal agent chat (Haiku):**
- Input: 500 tokens, Output: 1200 tokens
- Cost = (500/1M × $1.00) + (1200/1M × $5.00) = $0.0005 + $0.006 = $0.0065 = **0.65 cents**

**Example 2 — Full boomerang (9 agents, Haiku):**
- Average per agent: 400 input, 800 output
- Per agent cost = (400/1M × $1.00) + (800/1M × $5.00) = $0.0044 = 0.44 cents
- 9 agents = 9 × 0.44 = **3.96 cents**

**Example 3 — Axiom challenge round (Sonnet for Axiom, Haiku for respondents):**
- Axiom challenge: 2000 input, 600 output on Sonnet
  - (2000/1M × $3.00) + (600/1M × $15.00) = $0.006 + $0.009 = **1.50 cents**
- 2 respondent agents (Haiku): 500 input, 400 output each = 0.25 cents each = 0.50 cents
- Axiom verdict: 1500 input, 300 output on Sonnet = 0.90 cents
- Total challenge: 1.50 + 0.50 + 0.90 = **2.90 cents**

**Edge case — Zero output (timeout):**
- 300 input tokens, 0 output (agent timed out)
- Cost = (300/1M × $1.00) + 0 = **0.03 cents** (still billed for input)

### 20.2 Gotcha List

| # | Gotcha | DO THIS | NOT THAT |
|---|--------|---------|----------|
| 1 | Axiom call limit | Cap at exactly 3 LLM calls per challenge (challenge → response → verdict). If still unresolved, log as ACTION_REQUIRED and move on | Don't allow iterative back-and-forth. No "let me ask one more time" |
| 2 | Banking type | Auto-determine from dimension + phase using `determine_bank_type()` | Don't let users pick bank type. The type is structural, not a preference |
| 3 | Perspective unlock order | Generate unlocks immediately; Review unlocks only after Generate completes in same dimension | Don't unlock all phases at once. The sequential order IS the methodology |
| 4 | JWT storage | Store in httpOnly Secure cookie | Don't use localStorage (XSS vulnerable) |
| 5 | Budget enforcement | Check budget BEFORE making Claude API call. Soft limit — if exceeded mid-call, let it finish | Don't kill mid-stream API calls. Don't charge for calls that fail |
| 6 | Cost tracking precision | Use NUMERIC(10,4) and round at display time | Don't use INTEGER for cost_cents — sub-cent precision matters at scale |
| 7 | SSE connection | One SSE connection per chat/boomerang. Client reconnects on drop | Don't keep persistent SSE connections. Each agent interaction is a new stream |
| 8 | Whisper file size | Split audio >25MB into chunks before sending to Whisper | Don't send >25MB files — Whisper rejects them |
| 9 | Password timing | Use constant-time comparison (bcrypt handles this) | Don't use `==` for password comparison (timing attack) |
| 10 | Error messages (auth) | Return generic "Invalid credentials" for both wrong email and wrong password | Don't reveal whether the email exists. "Email not found" is an information leak |

### 20.3 Decision Log

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| SSE vs WebSocket | WebSocket (bidirectional), SSE (server-push only) | SSE | Agent responses are server→client only. SSE is simpler, works with HTTP/2, no connection upgrade needed. WebSocket overkill |
| Zustand vs Redux | Redux (industry standard), Zustand (minimal), Jotai (atomic) | Zustand | Small app, few stores needed. Redux boilerplate excessive. Zustand is 1KB, works with React 19 |
| FastAPI vs Django | Django (batteries included), FastAPI (async native) | FastAPI | Async critical for parallel agent calls. OpenAPI auto-docs. Django's ORM is sync |
| JWT vs Session | Server-side sessions (Redis), JWT (stateless) | JWT (with httpOnly cookie) | Simpler deployment, no session store needed. Short TTL (15min) mitigates revocation concern. Refresh token provides 7-day window |
| MinIO vs S3 | AWS S3 (managed), MinIO (self-hosted, S3-compatible) | MinIO | Self-hosted for dev parity. Production can swap to S3 with zero code changes (same API) |
| TipTap vs Slate | ProseMirror/TipTap (structured), Slate (flexible) | TipTap | Better docs, more plugins, collaborative editing built-in. Slate API still unstable |

### 20.4 Real Data Example

A complete dataset for "Digital Transformation Readiness Assessment" journey:

**Organization:** Acme Consulting (slug: "acme-consulting")
**User:** Sarah Chen, sarah@acmeconsulting.com, Admin
**Goal:** "Digital Transformation Readiness Assessment for ManuCo"
**Journey:** Started Jan 10, 2026

| Perspective | Status | Docs | Vibes | Cost | Banked |
|------------|--------|------|-------|------|--------|
| Arch × Generate | Completed | 2 | 1 (3:24) | $0.18 | Yes — "Initial strategic vision: 3 readiness pillars identified" |
| Arch × Review | Completed | 3 | 0 | $0.24 | Yes — "Refined pillars with stakeholder input from CTO office" |
| Arch × Validate | Completed | 1 | 1 (5:10) | $0.31 | Yes — "Validated feasibility against ManuCo's current infra" |
| Arch × Summarize | Completed | 0 | 0 | $0.42 | Yes (Film) — "Architecture dimension complete: 3 pillars, 12 requirements" |
| Design × Generate | Completed | 1 | 2 (4:15, 2:30) | $0.22 | Yes |
| Design × Review | In Progress | 2 | 0 | $0.15 | No |
| ... | ... | ... | ... | ... | ... |

**Total journey cost so far:** $4.82
**Total vibes recorded:** 12 sessions, 47 minutes
**Total Axiom challenges:** 5 (3 resolved, 1 accepted risk, 1 action required)

## 21. Testing & Browser Validation

### 21.1 Test Strategy by Phase

| Phase | Test Types | Tools |
|-------|-----------|-------|
| 1 Foundation | Unit: DB models, config loading. Integration: Docker compose up, health endpoint | pytest, docker compose |
| 2 Auth | Unit: JWT encode/decode, password hash. Integration: Full auth flows | pytest, httpx |
| 3 Core Models | Unit: CRUD services. Integration: API endpoint tests with test DB | pytest, httpx |
| 4 AI Agents | Unit: Prompt construction, cost calculation. Integration: Mock Claude API | pytest, respx (mock) |
| 5 Frontend | Component: Layout, navigation. E2E: Route rendering | Vitest, Playwright |
| 6 Canvas | Component: LeftRail, HeatMap, AgentCard. E2E: Dimension/phase navigation | Vitest, Playwright |
| 7-13 | Feature-specific tests per phase | pytest, Vitest, Playwright |
| 14 Polish | E2E: Full journey flow. Performance: Lighthouse. Accessibility: axe-core | Playwright, Lighthouse, axe |

### 21.2 Browser Validation

| Check | Viewports | Method |
|-------|-----------|--------|
| All routes render without error | 1280px, 768px, 375px | Playwright: navigate each route, check `console.error` count = 0 |
| Screenshots match | 1280px | Playwright: screenshot each page, visual regression against baseline |
| Keyboard navigation | 1280px | Playwright: Tab through all interactive elements, verify focus visible |
| No layout overflow | All 3 | Playwright: check `document.documentElement.scrollWidth <= window.innerWidth` |

### 21.3 Test Failure Procedure

1. Capture: error message, stack trace, screenshot (if browser test)
2. Log: write failure to `test-results/` directory with timestamp
3. Block: PR cannot merge with failing tests (GitHub Actions check)
4. Retry: flaky tests retried once automatically (Playwright `retries: 1`)

### 21.4 Business Rule Test Cases

```python
# Cost calculation
assert calculate_cost_cents("claude-haiku-4-5-20251001", 500, 1200) == 0.65
assert calculate_cost_cents("claude-haiku-4-5-20251001", 0, 0) == 0.0
assert calculate_cost_cents("claude-sonnet-4-5-20250929", 2000, 600) == 1.50

# Bank type determination
assert determine_bank_type("architecture", "generate") == "bankable"
assert determine_bank_type("architecture", "summarize") == "film"
assert determine_bank_type("design", "summarize") == "film"
assert determine_bank_type("engineering", "summarize") == "film_reel"

# Perspective unlock
assert can_unlock("architecture", "review") == False  # Generate not complete
complete_perspective("architecture", "generate")
assert can_unlock("architecture", "review") == True

# Budget alert
assert check_budget_alert(budget=2000, spent=1500) == None       # 75% — no alert
assert check_budget_alert(budget=2000, spent=1600) == "warning_80"  # 80%
assert check_budget_alert(budget=2000, spent=1800) == "warning_90"  # 90%
assert check_budget_alert(budget=2000, spent=2100) == "critical_100"  # 105%
assert check_budget_alert(budget=0, spent=99999) == None          # Unlimited
```

## 22. Performance & Accessibility

### 22.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint (FCP) | < 1.5s | Lighthouse |
| Time to Interactive (TTI) | < 3.0s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| API response time (CRUD) | < 200ms | Server-side timing middleware |
| API response time (agent chat first token) | < 2s | SSE first `token` event |
| Full boomerang (9 agents) | < 30s | SSE `boomerang_complete` event |

### 22.2 Optimization Strategies

| Area | Strategy |
|------|----------|
| Agent responses | SSE streaming — user sees text immediately, no wait for full response |
| Dashboard data | React Query with 30s stale time — cache journey list, refresh in background |
| Document list | Paginated (20/page), lazy load thumbnails |
| Bank timeline | Virtualized list (react-window) for journeys with many bank instances |
| Static assets | Next.js automatic code splitting, image optimization |
| Database | Connection pooling (asyncpg, 10 connections), prepared statements |
| API | Response compression (gzip), pagination on all list endpoints |

### 22.3 Accessibility (WCAG 2.1 AA)

| Requirement | Implementation |
|-------------|---------------|
| Color contrast | All text meets 4.5:1 ratio (verified against dark theme backgrounds) |
| Keyboard navigation | All interactive elements focusable via Tab. Focus ring visible (2px solid white, offset 2px) |
| Screen reader | All agent cards have `aria-label="Agent name assessment"`. Live regions for streaming text (`aria-live="polite"`) |
| ARIA landmarks | `<main>`, `<nav>`, `<aside>` for canvas layout. Role="status" for progress bar |
| Reduced motion | `prefers-reduced-motion: reduce` disables: gradient animations, streaming text animation, card transitions. Static alternatives provided |
| Focus management | After modal close: focus returns to trigger element. After route change: focus moves to main heading |

## 23. Business Features & Stakeholder Summary

### 23.1 Feature Catalog

1. **Journey Builder** — Create a structured business transformation journey with a clear goal
2. **AI Agent Guidance** — 9 specialized AI agents that each bring a different perspective to your problem
3. **Voice Sessions (Vibes)** — Record voice conversations and get automatic AI analysis of everything discussed
4. **Smart Challenge System (Axiom)** — An AI devil's advocate that questions all conclusions to make sure they hold up
5. **Document Management** — Upload, organize, and reference documents within each step of your journey
6. **Banking System** — Lock in validated work as you go, building a permanent record of decisions and evidence
7. **VDBA Publication** — Turn your completed journey into a polished, exportable business asset (PDF or Word)
8. **Stakeholder Communication** — Send emails to stakeholders directly from the platform to gather input
9. **Cost Tracking** — See exactly how much AI processing costs, set budgets, and get alerts
10. **Multi-user Organizations** — Invite team members with different access levels (Admin, Editor, Viewer)
11. **Interactive Heat Map** — Visual progress tracker showing which parts of the journey are complete
12. **Theme Customization** — Three visual themes (Space, Forest, Black Hole) for different work preferences

### 23.2 User Capabilities by Role

**Admin — You can:**
- Everything an Editor can do, plus:
- Invite and remove team members
- Change team member roles
- Update organization name and logo
- Set and modify the monthly AI budget
- Configure voice provider, email settings, and default AI model
- View all API usage and cost breakdowns

**Editor — You can:**
- Create new goals and start journeys
- Navigate through all 12 perspectives in a journey
- Chat with any of the 9 AI agents
- Run Boomerangs (all agents analyze at once)
- Record voice sessions and see AI analysis
- Upload and delete documents
- Bank completed work
- Publish finished journeys as VDBAs
- Send stakeholder emails
- Export VDBAs as PDF or Word
- View cost tracking and usage stats

**Viewer — You can:**
- See all journeys, goals, and VDBAs
- Read agent conversation history
- View documents and voice transcripts
- Browse the bank timeline
- Download VDBA exports
- View cost and usage statistics
- You cannot create, edit, or delete anything

### 23.3 End-to-End Workflow (Business Terms)

**Creating a Digital Transformation Assessment:**

1. Sarah logs into InCube and clicks "New Journey"
2. She picks "Digital Transformation Readiness" from the goal menu
3. The system creates a structured path with 12 steps arranged in a 3x4 grid
4. Sarah starts at the first step (Architecture × Generate) — this is the "big picture brainstorming" phase
5. She types her thoughts and the AI agents respond with structured analysis
6. She records a 5-minute voice note describing her client's situation — all 9 agents automatically listen and extract relevant insights
7. She clicks "Boomerang" to have all agents weigh in at once — the Challenger agent (Axiom) checks if anything was missed or if agents disagree
8. When she's satisfied with this step, she clicks "Bank" to lock it in as a permanent record
9. The next step unlocks — she moves through all 12 steps over several days
10. After completing all steps, she clicks "Publish" to create a Validated Digital Business Asset
11. She downloads a professional PDF to share with her client

### 23.4 Screen-by-Screen Walkthrough

**Dashboard — Your Home Base:**
You see your active journeys as cards with progress bars (like "8 of 12 steps complete, $1.24 spent"). Below that, any published VDBAs with download buttons. At the bottom, this month's usage stats. Click a journey card to jump into work.

**Canvas — Your Workspace:**
The left side shows a slim rail with three sections (Architecture, Design, Engineering), each with four dots (Generate, Review, Validate, Summarize). Click any dot to navigate to that step. The main area shows AI agent responses as cards — each agent has a colored border matching its specialty. At the bottom, four action buttons: upload documents, record voice, send email, or run all agents at once.

**Bank — Your Record:**
A timeline view showing everything you've banked, ordered by date. Each entry shows the step it came from, a summary, and counts of documents and voice sessions included. Think of it as a scrapbook of validated decisions.

**Settings — Control Panel:**
Tabs for API usage (charts showing daily costs and per-agent breakdown), voice settings, email configuration, and organization management. The budget section lets admins set a monthly cap with automatic warnings.

### 23.5 Feature Value Statements

| Feature | Business Value |
|---------|---------------|
| AI Agent Guidance | Instead of hiring 8 specialist consultants for different perspectives, get structured analysis from 9 AI agents at a fraction of the cost ($0.04 per full analysis) |
| Voice Sessions | Capture insights from stakeholder conversations without manual note-taking. AI extracts actionable items automatically — no more "I think someone mentioned..." |
| Axiom (Challenger) | Every conclusion is stress-tested. When you present to a board, you can say "this was challenged and defended" rather than "the consultant said so" |
| Banking System | No more lost work or forgotten decisions. Every validated step is locked in with a full audit trail. If someone asks "why did you decide X?", the answer is always available |
| VDBA Export | Turn weeks of collaborative analysis into a polished, shareable document in one click. Previously, assembling a transformation report took days of manual formatting |
| Cost Tracking | Complete transparency on AI usage costs. No surprise bills — set a monthly budget and get alerts at 80%, 90%, and 100% |

### 23.6 Limitations and Exclusions

The InCube Platform v1 does NOT:
- **Replace human judgment** — AI agents provide analysis and structured perspectives, but all decisions require human review and banking
- **Provide industry-specific regulatory compliance** — The framework is methodology-agnostic; industry regulations must be known by the user
- **Support real-time collaboration** — One person works on a perspective at a time (multi-user viewing is supported, but not simultaneous editing)
- **Integrate with project management tools** — No Jira, Asana, or Monday.com integration. Outputs are standalone documents
- **Provide offline capability** — Requires internet connection for AI agents, voice transcription, and file storage
- **Support languages other than English** — AI agents and voice transcription are English-only in v1 (voice language configurable in settings for transcription, but agent prompts are English)
- **Include mobile native apps** — Web-only, responsive design supports mobile browsers but no iOS/Android app
- **Handle payment or billing** — No Stripe integration, no subscription management. Cost tracking is informational only
