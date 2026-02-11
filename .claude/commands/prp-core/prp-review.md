---
description: Comprehensive PR code review - checks diff, patterns, runs validation, comments on PR
argument-hint: <pr-number|pr-url> [--approve|--request-changes]
---

# PR Code Review

**Input**: $ARGUMENTS

---

## Your Mission

Perform a thorough, senior-engineer-level code review:

1. **Understand** what the PR is trying to accomplish
2. **Check** the code against project patterns and constraints
3. **Run** all validation (lint, tests, build)
4. **Identify** issues by severity
5. **Report** findings as PR comment AND local file

---

## Phase 1: FETCH - Get PR Context

### 1.1 Parse Input

| Input Format | Action |
|--------------|--------|
| Number (`123`, `#123`) | Use as PR number |
| URL | Extract PR number |
| Branch name | Find associated PR |

### 1.2 Get PR Metadata

```bash
gh pr view {NUMBER} --json number,title,body,author,headRefName,baseRefName,state,additions,deletions,changedFiles,files,reviews,comments
gh pr diff {NUMBER}
```

### 1.3 Checkout PR Branch

```bash
gh pr checkout {NUMBER}
```

---

## Phase 2: CONTEXT - Understand the Change

Read CLAUDE.md, check for implementation reports, understand PR intent.

---

## Phase 3: REVIEW - Analyze the Code

Review checklist: Correctness, Type Safety, Pattern Compliance, Security, Performance, Completeness, Maintainability.

Categorize issues by severity: Critical, High, Medium, Low.

---

## Phase 4: VALIDATE - Run Automated Checks

```bash
cd backend && source .venv/bin/activate && ruff check . && pytest
cd frontend && npm run lint && npm run build
```

---

## Phase 5: DECIDE - Form Recommendation

APPROVE / REQUEST CHANGES / BLOCK based on findings.

---

## Phase 6: REPORT

Create `.claude/PRPs/reviews/pr-{NUMBER}-review.md` and post to GitHub.

---

## Success Criteria

- **CODE_REVIEWED**: All changed files analyzed
- **VALIDATION_RUN**: All automated checks executed
- **ISSUES_CATEGORIZED**: Findings organized by severity
- **PR_UPDATED**: Review posted to GitHub
- **RECOMMENDATION_CLEAR**: Approve/request-changes/block with rationale
