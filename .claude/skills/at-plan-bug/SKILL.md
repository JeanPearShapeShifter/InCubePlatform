---
name: at-plan-bug
description: Create a targeted plan for fixing an InCube Portal bug. Root cause analysis, execution path tracing, minimal fix scope.
argument-hint: <bug description or error message>
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(gh issue*)
---


Create a targeted plan for fixing a specific bug. Focused on root cause analysis and minimal fix.

## Variables

- `$ARGUMENTS` — Bug description, error message, GitHub issue number, or reproduction steps

## Instructions

1. **Research the bug**:
   - Read `CLAUDE.md` for project context
   - If GitHub issue: `gh issue view $NUMBER`
   - Search codebase for relevant error messages or affected code
   - Check recent git log for changes that might have introduced the bug
   - Identify which component is affected: api-backend, frontend, ai-agents, database
2. **Root cause analysis**:
   - Trace the execution path that triggers the bug
   - Identify the specific file(s) and line(s) where the bug originates
   - Distinguish between the symptom and the root cause
3. **Write the plan** to `.claude/PRPs/plans/bug-{slug}.plan.md`:

```markdown
# Bug Fix: {Title}

## Component
{api-backend | frontend | ai-agents | database}

## Symptom
{What the user sees / the error that occurs}

## Root Cause
{Why it happens — the actual code issue}

## Affected Files
- {path}: {what's wrong here}

## Fix Tasks

### 1. {Fix Description}
- **File**: {path}
- **Change**: {specific change needed}
- **Acceptance**: {how to verify the fix}

## Regression Risk
- {What could break if this fix is wrong}
- {Related functionality to test}

## Testing
- [ ] Reproduce the bug before fixing
- [ ] Unit test for the fix
- [ ] Verify no regressions in: {list}
```

## Input

$ARGUMENTS
