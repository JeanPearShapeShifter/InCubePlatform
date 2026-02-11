---
description: Execute an implementation plan with rigorous validation loops
argument-hint: <path/to/plan.md>
---

# Implement Plan

**Plan**: $ARGUMENTS

---

## Your Mission

Execute the plan end-to-end with rigorous self-validation. You are autonomous.

**Core Philosophy**: Validation loops catch mistakes early. Run checks after every change. Fix issues immediately. The goal is a working implementation, not just code that exists.

**Golden Rule**: If a validation fails, fix it before moving on. Never accumulate broken state.

---

## Phase 0: DETECT - Project Environment

### 0.1 Identify Package Manager / Toolchain

Check for these files to determine the project's toolchain:

| File Found | Tool | Runner |
|------------|------|--------|
| `backend/pyproject.toml` | Python/uv | `cd backend && source .venv/bin/activate` |
| `frontend/package.json` | Node/npm | `cd frontend && npm run` |

### 0.2 Identify Validation Scripts

**Use the plan's "Validation Commands" section** - it should specify exact commands for this project.

---

## Phase 1: LOAD - Read the Plan

### 1.1 Load Plan File

Read the plan at `$ARGUMENTS`.

### 1.2 Extract Key Sections

Locate and understand:

- **Summary** - What we're building
- **Patterns to Mirror** - Code to copy from
- **Files to Change** - CREATE/UPDATE list
- **Step-by-Step Tasks** - Implementation order
- **Validation Commands** - How to verify (USE THESE, not hardcoded commands)
- **Acceptance Criteria** - Definition of done

### 1.3 Validate Plan Exists

**If plan not found:**

```
Error: Plan not found at $ARGUMENTS

Create a plan first: /prp-plan "feature description"
```

**PHASE_1_CHECKPOINT:**

- [ ] Plan file loaded
- [ ] Key sections identified
- [ ] Tasks list extracted

---

## Phase 2: PREPARE - Git State

### 2.1 Check Current State

```bash
git branch --show-current
git status --porcelain
```

### 2.2 Branch Decision

| Current State     | Action                                               |
| ----------------- | ---------------------------------------------------- |
| On main, clean    | Create branch: `git checkout -b feature/{plan-slug}` |
| On main, dirty    | STOP: "Stash or commit changes first"                |
| On feature branch | Use it (log: "Using existing branch")                |

### 2.3 Sync with Remote

```bash
git fetch origin
git pull --rebase origin main 2>/dev/null || true
```

---

## Phase 3: EXECUTE - Implement Tasks

**For each task in the plan's Step-by-Step Tasks section:**

### 3.1 Read Context

1. Read the **MIRROR** file reference from the task
2. Understand the pattern to follow
3. Read any **IMPORTS** specified

### 3.2 Implement

1. Make the change exactly as specified
2. Follow the pattern from MIRROR reference
3. Handle any **GOTCHA** warnings

### 3.3 Validate Immediately

**After EVERY file change, run the appropriate validation command from the plan.**

Backend: `cd backend && source .venv/bin/activate && ruff check .`
Frontend: `cd frontend && npm run lint`

**If validation fails:** Fix → Re-run → Only proceed when passing.

### 3.4 Track Progress

Log each task as you complete it.

**Deviation Handling:** If you must deviate from the plan, note WHAT and WHY.

---

## Phase 4: VALIDATE - Full Verification

### 4.1 Static Analysis

Run the type-check and lint commands from the plan's Validation Commands section.

**Must pass with zero errors.**

### 4.2 Unit Tests

**You MUST write or update tests for new code.** This is not optional.

### 4.3 Build Check

Run the build command from the plan's Validation Commands section.

### 4.4 Browser Validation (UI Phases Only)

**Skip if the phase does NOT involve frontend/UI changes.**

```bash
cd frontend && npm run dev &
DEV_PID=$!
sleep 5
# Verify routes load, no console errors
kill $DEV_PID 2>/dev/null
```

**PHASE_4_CHECKPOINT:**

- [ ] Type-check/lint passes
- [ ] Tests pass (all green)
- [ ] Build succeeds
- [ ] Browser validation passes (if UI phase)

---

## Phase 5: REPORT - Create Implementation Report

### 5.1 Determine Project & Create Report Directory

Determine `{project}` from the plan file path:
- If path contains `/backend/` → `{project}` = `backend`
- If path contains `/frontend/` → `{project}` = `frontend`

```bash
mkdir -p .claude/PRPs/reports/{project}
```

### 5.2 Generate Report

**Path**: `.claude/PRPs/reports/{project}/{plan-name}-report.md`

### 5.3 Update Source PRD (if applicable)

If plan was generated from a PRD, update the phase status to `complete`.

### 5.4 Archive Plan

```bash
mkdir -p .claude/PRPs/plans/{project}/completed
mv $ARGUMENTS .claude/PRPs/plans/{project}/completed/
```

---

## Phase 6: OUTPUT - Report to User

Report implementation status, validation results, files changed, and next steps.

---

## Success Criteria

- **TASKS_COMPLETE**: All plan tasks executed
- **TYPES_PASS**: Type-check/lint command exits 0
- **TESTS_PASS**: Test command all green
- **BUILD_PASS**: Build command succeeds
- **REPORT_CREATED**: Implementation report exists
- **PLAN_ARCHIVED**: Original plan moved to completed
