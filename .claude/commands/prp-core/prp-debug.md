---
description: Deep root cause analysis - finds the actual cause, not just symptoms
argument-hint: <issue|error|stacktrace> [--quick]
---

# Root Cause Analysis

**Input**: $ARGUMENTS

---

## Your Mission

Find the **actual root cause** - the specific code, config, or logic that, if changed, would prevent this issue. Not symptoms. Not intermediate failures. The origin.

**The Test**: "If I changed THIS, would the issue be prevented?" If the answer is "maybe" or "partially", you haven't found the root cause yet.

---

## Phase 1: CLASSIFY - Parse Input

Determine input type (raw symptom vs pre-diagnosed) and mode (--quick vs deep).

## Phase 2: HYPOTHESIZE - Form Theories

Generate 2-4 hypotheses ranked by likelihood.

## Phase 3: INVESTIGATE - The 5 Whys

Execute the 5 Whys protocol with concrete evidence at each step.

## Phase 4: VALIDATE - Confirm Root Cause

Three tests: Causation, Necessity, Sufficiency. Check git history.

## Phase 5: REPORT

Create `.claude/PRPs/debug/rca-{issue-slug}.md` with evidence chain and fix specification.

---

## Success Criteria

- **ROOT_CAUSE_FOUND**: Specific file:line identified
- **EVIDENCE_CHAIN_COMPLETE**: Every step has proof
- **FIX_ACTIONABLE**: Someone could implement from the report
- **VERIFICATION_CLEAR**: How to confirm fix works
