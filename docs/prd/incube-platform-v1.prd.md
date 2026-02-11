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

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js 15 + React 19 + Tailwind CSS 4 | SSR, API routes, modern React |
| **UI Components** | shadcn/ui + Radix | Accessible, customizable primitives |
| **State Management** | Zustand (client) + React Query (server) | Simple, performant |
| **Backend** | FastAPI (Python 3.12+) | Async native, OpenAPI auto-docs |
| **ORM** | SQLAlchemy 2.0 + asyncpg | Async PostgreSQL, Alembic migrations |
| **Database** | PostgreSQL 16 (Docker) | Containerized, matches TourHub pattern |
| **File Storage** | MinIO (Docker) | S3-compatible, containerized |
| **Cache/Queue** | Redis 7 (Docker) | Sessions, background job queue |
| **AI Agents** | Claude Agent SDK + Haiku (default) | 9 specialized agents, parallel execution |
| **Voice** | Web Audio API + Whisper API | Browser recording, server-side transcription |
| **Email** | Resend | Transactional notifications |
| **Auth** | NextAuth.js (Auth.js) | Social + email login, sessions |
| **Real-time** | Server-Sent Events (SSE) | AI agent streaming responses |

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

### 5.3 Database Schema (Key Tables)

```
organizations
  - id, name, slug, logo_url, created_at

users
  - id, organization_id, email, name, role, avatar_url, created_at

goals
  - id, organization_id, created_by, title, description, type (predefined|custom), created_at

journeys
  - id, goal_id, organization_id, status (active|completed|archived), created_at, completed_at

perspectives
  - id, journey_id, dimension (architecture|design|engineering), phase (generate|review|validate|summarize)
  - status (pending|in_progress|completed), started_at, completed_at

agent_sessions
  - id, perspective_id, agent_name, system_prompt_version
  - input_tokens, output_tokens, model_used, cost_cents
  - request_payload (jsonb), response_payload (jsonb), created_at

axiom_challenges
  - id, perspective_id, challenge_text, severity (high|medium|low)
  - targeted_agents (text[]), evidence_needed
  - resolution (resolved|accepted_risk|action_required), resolution_text
  - created_at, resolved_at

documents
  - id, perspective_id, uploaded_by, filename, file_type, minio_key, file_size
  - created_at

vibe_sessions
  - id, perspective_id, conducted_by, duration_seconds
  - audio_minio_key, transcript_text, transcript_minio_key
  - created_at

vibe_analyses
  - id, vibe_session_id, agent_name, analysis_type
  - content (jsonb), created_at

bank_instances
  - id, perspective_id, type (bankable|film|filmReel|published)
  - synopsis (text), decision_audit (jsonb)
  - documents_count, vibes_count, emails_sent, feedback_received
  - agent_assessments (jsonb), created_at

vdbas
  - id, journey_id, organization_id, title, description
  - bank_instance_id, published_at, export_url

email_log
  - id, perspective_id, sent_by, recipient_type, recipient_count
  - template_type, sent_at

api_usage
  - id, organization_id, user_id, service (claude|whisper|resend)
  - model, tokens_in, tokens_out, cost_cents
  - endpoint, created_at

settings
  - id, organization_id, key, value (jsonb)
```

### 5.4 API Routes

```
# Auth
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

# Organizations
GET    /api/organizations/:id
PUT    /api/organizations/:id

# Goals
POST   /api/goals
GET    /api/goals
GET    /api/goals/:id

# Journeys
POST   /api/journeys
GET    /api/journeys
GET    /api/journeys/:id
PATCH  /api/journeys/:id/status

# Perspectives
GET    /api/journeys/:id/perspectives
GET    /api/perspectives/:id
PATCH  /api/perspectives/:id/status

# Agents
POST   /api/perspectives/:id/agents/:name/chat    (SSE)
POST   /api/perspectives/:id/boomerang             (SSE - all 9 agents)
GET    /api/perspectives/:id/agent-sessions

# Axiom
POST   /api/perspectives/:id/axiom/challenge       (SSE)
GET    /api/perspectives/:id/axiom/challenges

# Documents
POST   /api/perspectives/:id/documents              (multipart upload)
GET    /api/perspectives/:id/documents
GET    /api/documents/:id/download
DELETE /api/documents/:id

# Vibe Sessions
POST   /api/perspectives/:id/vibes                   (multipart audio upload)
GET    /api/perspectives/:id/vibes
GET    /api/vibes/:id
POST   /api/vibes/:id/analyze                        (trigger agent analysis)

# Bank
POST   /api/perspectives/:id/bank
GET    /api/journeys/:id/bank
GET    /api/bank/:id

# VDBA
POST   /api/journeys/:id/publish
GET    /api/vdbas
GET    /api/vdbas/:id
GET    /api/vdbas/:id/export

# Email
POST   /api/perspectives/:id/email
GET    /api/perspectives/:id/emails

# Settings
GET    /api/settings
PUT    /api/settings
GET    /api/settings/usage                           (API cost dashboard data)
GET    /api/settings/usage/breakdown                 (per-agent, per-service)

# Health
GET    /api/health
```

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

| # | Phase | Scope | Dependencies | Status |
|---|-------|-------|--------------|--------|
| 1 | **Foundation** | Project scaffolding, Docker Compose, DB schema, Alembic migrations, FastAPI skeleton | None | Pending |
| 2 | **Auth & Users** | NextAuth.js, user/org models, JWT, protected routes | Phase 1 | Pending |
| 3 | **Core Data Models** | Goals, Journeys, Perspectives, Documents, Bank Instances — CRUD API | Phase 1 | Pending |
| 4 | **AI Agent System** | Claude Agent SDK integration, 9 agent definitions, system prompts, SSE streaming | Phase 1 | Pending |
| 5 | **Frontend Foundation** | Next.js app shell, Tailwind design system, layout components, routing | Phase 2 | Pending |
| 6 | **Canvas UI** | Left rail, main canvas, agent cards, dimension/phase navigation | Phase 5 | Pending |
| 7 | **Document System** | MinIO upload/download, document editors (TipTap), viewer components | Phase 3 | Pending |
| 8 | **Vibe System** | Web Audio recording, Whisper transcription, post-vibe agent analysis | Phase 4 | Pending |
| 9 | **Boomerang & Bank** | Multi-agent orchestration, Axiom challenges, banking workflow | Phase 4, 6 | Pending |
| 10 | **Email Integration** | Resend setup, notification templates, send log | Phase 3 | Pending |
| 11 | **Settings & Admin** | API usage dashboard, voice provider config, org management | Phase 2, 4 | Pending |
| 12 | **VDBA & Export** | Publication workflow, PDF/DOCX export, sharing | Phase 9 | Pending |
| 13 | **Heat Map & Analytics** | Real progress visualization, journey analytics | Phase 9 | Pending |
| 14 | **Polish & Testing** | E2E tests, accessibility audit, performance optimization | All | Pending |

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
