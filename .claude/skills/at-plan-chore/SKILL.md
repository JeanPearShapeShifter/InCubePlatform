---
name: at-plan-chore
description: Create a plan for InCube Portal maintenance, refactoring, dependency updates, or infrastructure tasks. Scoped and low-risk.
argument-hint: <chore description>
---


Create a plan for maintenance, refactoring, dependency updates, or infrastructure tasks.

## Variables

- `$ARGUMENTS` — Chore description

## Instructions

1. **Research**:
   - Read `CLAUDE.md` for project context
   - Understand the current state of what needs to change
   - Identify which component(s): api-backend, frontend, ai-agents, database, infrastructure
2. **Scope strictly** — chores should be contained and low-risk
3. **Write the plan** to `.claude/PRPs/plans/chore-{slug}.plan.md`:

```markdown
# Chore: {Title}

## Component
{api-backend | frontend | ai-agents | database | infrastructure | all}

## Purpose
{Why this maintenance is needed}

## Tasks

### 1. {Task Name}
- **Files**: {paths}
- **Description**: {what to do}
- **Acceptance**: {how to verify}

## Risk Assessment
- Impact: {low/medium/high}
- Rollback: {how to undo if needed}

## Testing
- [ ] Verify no regressions
- [ ] Build succeeds
- [ ] All existing tests pass
```

## Input

$ARGUMENTS
