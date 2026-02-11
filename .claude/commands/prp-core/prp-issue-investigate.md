---
description: Investigate a GitHub issue or problem - analyze codebase, create plan, post to GitHub
argument-hint: <issue-number|url|"description">
---

# Investigate Issue

**Input**: $ARGUMENTS

---

## Your Mission

Investigate the issue/problem and produce a comprehensive implementation plan that:

1. Can be executed by `/prp-issue-fix`
2. Is posted as a GitHub comment (if GH issue provided)
3. Captures all context needed for one-pass implementation

---

## Phase 1: PARSE - Understand Input

Determine input type (GH issue number, URL, or free-form). Classify issue type (BUG, ENHANCEMENT, REFACTOR, CHORE, DOCUMENTATION). Assess severity/complexity/confidence.

## Phase 2: EXPLORE - Codebase Intelligence

Use Explore agent to find relevant code, integration points, test patterns.

## Phase 3: ANALYZE - Form Approach

For BUGs: 5 Whys root cause analysis. For ENHANCEMENTs: change rationale and scope.

## Phase 4: GENERATE - Create Artifact

Write to `.claude/PRPs/issues/issue-{number}.md` with problem statement, analysis, implementation plan, patterns to follow, edge cases, and validation commands.

## Phase 5: COMMIT - Save Artifact

## Phase 6: POST - GitHub Comment (if GH issue)

## Phase 7: REPORT - Output to User

---

## Success Criteria

- **ARTIFACT_COMPLETE**: All sections filled with specific, actionable content
- **EVIDENCE_BASED**: Every claim has file:line reference or proof
- **IMPLEMENTABLE**: Another agent can execute without questions
- **GITHUB_POSTED**: Comment visible on issue (if GH issue)
