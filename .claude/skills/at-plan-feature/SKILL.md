---
name: at-plan-feature
description: Create a detailed implementation plan for a new InCube Portal feature. Researches codebase patterns, identifies affected files, and produces a plan.md ready for implementation.
argument-hint: <feature description>
---


Create a detailed implementation plan for a new feature. The plan IS the prompt — it will be fed to a build or iterate skill.

## Variables

- `$ARGUMENTS` — Feature description or requirement

## Instructions

1. **Research the codebase first** — think hard before writing anything:
   - Read `CLAUDE.md` for project architecture and conventions
   - Search for similar patterns in the codebase
   - Identify which InCube component(s) this feature touches:
     - **backend/** — FastAPI (Python 3.12+, SQLAlchemy, asyncpg, Alembic)
     - **frontend/** — Next.js 15, React 19, Tailwind CSS 4, shadcn/ui, Zustand
     - **AI agents** — Claude Agent SDK, 9 agents (8 specialists + Axiom adversarial reviewer)
     - **Infrastructure** — PostgreSQL, Redis, MinIO
2. **Understand the tech stack**:
   - Backend: FastAPI + SQLAlchemy async + Pydantic v2 + Alembic migrations
   - Frontend: Next.js 15 + React 19 + Tailwind 4 + Zustand + React Query
   - AI: Claude Agent SDK with SSE streaming, token tracking, post-vibe analysis
   - Storage: PostgreSQL (port 5435 dev) + Redis (port 6380 dev) + MinIO (ports 9002/9003 dev)
3. **Replace all placeholders** — no `<placeholder>` should remain in the final plan

## Relevant Files

List the files this feature will touch (discovered during research):
- File paths with descriptions of what changes are needed

## Plan Format

Write the plan to `.claude/PRPs/plans/feature-{slug}.plan.md`:

```markdown
# Feature: {Title}

## Component
{api-backend | frontend | ai-agents | database | cross-cutting}

## Description
{What this feature does and why}

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Architecture Decisions
- Decision 1: {choice} because {reason}
- Decision 2: {choice} because {reason}

## Tasks

### 1. {Task Name}
- **Files**: {paths to create/modify}
- **Description**: {what to do}
- **Acceptance**: {how to verify it's done}

### 2. {Task Name}
...

## Dependencies
- External: {packages to install}
- Internal: {modules this depends on}

## Testing Strategy
- Unit tests for: {what} (pytest for backend, vitest/jest for frontend)
- Integration tests for: {what}
- E2E tests for: {what, if applicable}

## File Patterns
{List of file patterns for conditional docs matching}
```

## Quality Checks

Before finalizing the plan, verify:
- [ ] Every task has clear acceptance criteria
- [ ] File paths are real (verified against codebase)
- [ ] No placeholders remain
- [ ] Dependencies are identified
- [ ] Testing strategy covers the feature
- [ ] Architecture decisions are justified
- [ ] Correct InCube component identified

## Input

$ARGUMENTS
