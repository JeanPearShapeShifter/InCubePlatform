---
description: Implement a fix from investigation artifact - code changes, PR, and self-review
argument-hint: <issue-number|artifact-path>
---

# Implement Issue

**Input**: $ARGUMENTS

---

## Your Mission

Execute the implementation plan from `/prp-issue-investigate`:

1. Load and validate the artifact
2. Ensure git state is correct
3. Implement the changes exactly as specified
4. Run validation
5. Create PR linked to issue
6. Run self-review and post findings
7. Archive the artifact

---

## Phase 1: LOAD - Get the Artifact

Load from `.claude/PRPs/issues/issue-{number}.md`.

## Phase 2: VALIDATE - Sanity Check

Verify artifact matches current codebase state.

## Phase 3: GIT-CHECK - Ensure Correct State

Create branch `fix/issue-{number}-{slug}` if needed.

## Phase 4: IMPLEMENT - Make Changes

Follow artifact steps exactly. Validate after each change.

## Phase 5: VERIFY - Run Validation

```bash
cd backend && source .venv/bin/activate && ruff check . && pytest
cd frontend && npm run lint && npm run build
```

## Phase 6: COMMIT

## Phase 7: PR - Create Pull Request

## Phase 8: REVIEW - Self Code Review

## Phase 9: ARCHIVE

Move artifact to `.claude/PRPs/issues/completed/`.

## Phase 10: REPORT

---

## Success Criteria

- **PLAN_EXECUTED**: All artifact steps completed
- **VALIDATION_PASSED**: All checks green
- **PR_CREATED**: PR exists and linked to issue
- **REVIEW_POSTED**: Self-review comment on PR
- **ARTIFACT_ARCHIVED**: Moved to completed folder
