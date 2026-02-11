#!/bin/bash

# PRP AT Build Validate Stop Hook
# Prevents session exit when a PRD validation loop is active
# Feeds the validation prompt back for the next iteration

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# State file location
STATE_FILE=".claude/at-build-validate.state.md"

# Check if PRD validation loop is active
if [[ ! -f "$STATE_FILE" ]]; then
  # No active loop - allow exit
  exit 0
fi

# Parse YAML frontmatter from state file
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")

# Extract values
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
PRD_PATH=$(echo "$FRONTMATTER" | grep '^working_prd_path:' | sed 's/working_prd_path: *//' | sed 's/^"\(.*\)"$/\1/')
INPUT_TYPE=$(echo "$FRONTMATTER" | grep '^input_type:' | sed 's/input_type: *//' | sed 's/^"\(.*\)"$/\1/')
PACKAGE_PATH=$(echo "$FRONTMATTER" | grep '^package_path:' | sed 's/package_path: *//' | sed 's/^"\(.*\)"$/\1/')

# Validate numeric fields
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  echo "Warning: AT Build Validate state file corrupted (invalid iteration)" >&2
  rm "$STATE_FILE"
  exit 0
fi

if [[ ! "$MAX_ITERATIONS" =~ ^[0-9]+$ ]]; then
  echo "Warning: AT Build Validate state file corrupted (invalid max_iterations)" >&2
  rm "$STATE_FILE"
  exit 0
fi

# Check if max iterations reached
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "AT Build Validate: Max iterations ($MAX_ITERATIONS) reached."
  echo "  Check .claude/at-build-validate.state.md for progress log."
  rm "$STATE_FILE"
  exit 0
fi

# Get transcript path from hook input
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "Warning: AT Build Validate transcript not found" >&2
  rm "$STATE_FILE"
  exit 0
fi

# Check for completion promise in last assistant message
if grep -q '"role":"assistant"' "$TRANSCRIPT_PATH"; then
  LAST_OUTPUT=$(grep '"role":"assistant"' "$TRANSCRIPT_PATH" | tail -1 | jq -r '
    .message.content |
    map(select(.type == "text")) |
    map(.text) |
    join("\n")
  ' 2>/dev/null || echo "")

  # Check for PRD completion promise
  if echo "$LAST_OUTPUT" | grep -q '<promise>PRD_COMPLETE</promise>'; then
    echo "AT Build Validate: All checks passed! PRD is complete."
    rm "$STATE_FILE"
    exit 0
  fi
fi

# Not complete - continue loop
NEXT_ITERATION=$((ITERATION + 1))

# Update iteration in state file
TEMP_FILE="${STATE_FILE}.tmp.$$"
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" "$STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$STATE_FILE"

# Build the prompt to feed back based on input type
if [[ "$INPUT_TYPE" == "package" ]] && [[ -n "$PACKAGE_PATH" ]]; then
  # Package mode prompt
  PROMPT="# PRD Validation Loop (Package Mode) - Iteration $NEXT_ITERATION

## Your Task

Continue validating and fixing the doc-core package until ALL checks pass.

**Package path**: \`$PACKAGE_PATH\`
**State file**: \`.claude/at-build-validate.state.md\`

## Instructions

1. **Read the state file** - check the Progress Log for what was fixed/failed last iteration
2. **Re-read the mapped doc-core documents** for each category being checked:
   - \`01-prd.md\` → Structure, Business Logic, Notifications, AI flows
   - \`02-system-architecture.md\` → External Integrations, Scaffolding, Concurrency
   - \`03-data-model.md\` → Database & ORM, Concurrency
   - \`04-api-specification.md\` → API Spec, Auth, External Integrations
   - \`05-user-flows.md\` → UI/UX, E2E Journeys
   - \`06-sequence-diagrams.md\` → Business Logic, Notifications
   - \`07-ux-specification.md\` → UI/UX, Performance
   - \`08-test-strategy.md\` → Testing & Validation
   - \`09-deployment-architecture.md\` → Logging, Scaffolding, Deployment
   - \`10-security-assessment.md\` → Auth & Authorization
   - \`business/\` subfolder → Business Features (if exists)
3. **Re-run ALL checks** - not just previously failing ones (fixes can introduce new issues)
4. **Fix failing checks** - edit the appropriate document file within the package
5. **Update the validation report** - record new PASS/FAIL status for each check
6. **Update state file** - append iteration results to Progress Log

## Package Mode Check Adaptations

Remember these adapted PASS conditions for package mode:
- 2.1: Entity definition tables (not CREATE TABLE statements)
- 2.3: ERD cardinality + Relationships section (not REFERENCES clauses)
- 2.7: Seed Data section (not INSERT statements)
- 3.1: User flow API Call columns matching endpoints (not wireframe buttons)
- 5.1: Screen specifications in ux-spec (not ASCII wireframes)
- 5.2: Interactive elements tables (not direct DB field mappings)
- 6.2: Precise logic descriptions/formulas (not code)
- 14.1: Tech stack + deployment topology (not folder tree)
- 19.x: Check business/ subfolder first, fall back to 01-prd.md

## Validation Categories (19 total)

1. Structure & Completeness (6 checks)
2. Database & ORM (8 checks)
3. API Specification (7 checks)
4. Authentication & Authorization (5 checks)
5. UI/UX & Wireframes (7 checks)
6. Business Logic & Rules (7 checks)
7. Cross-Reference Consistency (6 checks)
8. External Integrations (6 checks)
9. Logging & Observability (5 checks)
10. Notifications & Communication (4 checks)
11. Testing & Validation (4 checks)
12. Performance & Accessibility (3 checks)
13. AI/Conversation Flows (5 checks - conditional)
14. Project Scaffolding & Configuration (7 checks)
15. End-to-End User Journeys (4 checks)
16. Concurrency & Data Integrity (4 checks)
17. Deployment & Infrastructure (5 checks)
18. Worked Examples & Gotchas (4 checks)
19. Business Features & Stakeholder Summary (6 checks)

## Completion

When ALL applicable checks pass:
1. Write validation report to \`$PACKAGE_PATH/prp-validation-report.md\`
2. Output: \`<promise>PRD_COMPLETE</promise>\`

If checks are still failing:
- Fix what you can (edit the appropriate document file in the package)
- Mark checks needing user input as NEEDS_INPUT
- End your response normally
- The loop will continue

**Do NOT output the completion promise if ANY check is failing (excluding NEEDS_INPUT checks).**"

  SYSTEM_MSG="PRD Validation iteration $NEXT_ITERATION of $MAX_ITERATIONS | Package: $PACKAGE_PATH"
else
  # PRD mode prompt (existing behavior)
  PROMPT="# PRD Validation Loop - Iteration $NEXT_ITERATION

## Your Task

Continue validating and fixing the PRD until ALL checks pass.

**PRD file**: \`$PRD_PATH\`
**State file**: \`.claude/at-build-validate.state.md\`

## Instructions

1. **Read the state file** - check the Progress Log for what was fixed/failed last iteration
2. **Read the PRD** - understand current state after previous fixes
3. **Re-run ALL checks** - not just previously failing ones (fixes can introduce new issues)
4. **Fix failing checks** - edit the PRD directly to address gaps
5. **Update the validation report** - record new PASS/FAIL status for each check
6. **Update state file** - append iteration results to Progress Log

## Validation Categories (19 total)

1. Structure & Completeness (6 checks)
2. Database & ORM (8 checks)
3. API Specification (7 checks)
4. Authentication & Authorization (5 checks)
5. UI/UX & Wireframes (7 checks)
6. Business Logic & Rules (7 checks)
7. Cross-Reference Consistency (6 checks)
8. External Integrations (6 checks)
9. Logging & Observability (5 checks)
10. Notifications & Communication (4 checks)
11. Testing & Validation (4 checks)
12. Performance & Accessibility (3 checks)
13. AI/Conversation Flows (5 checks - conditional)
14. Project Scaffolding & Configuration (7 checks)
15. End-to-End User Journeys (4 checks)
16. Concurrency & Data Integrity (4 checks)
17. Deployment & Infrastructure (5 checks)
18. Worked Examples & Gotchas (4 checks)
19. Business Features & Stakeholder Summary (6 checks)

## Completion

When ALL applicable checks pass:
1. Write final validation report
2. Output: \`<promise>PRD_COMPLETE</promise>\`

If checks are still failing:
- Fix what you can
- Mark checks needing user input as NEEDS_INPUT
- End your response normally
- The loop will continue

**Do NOT output the completion promise if ANY check is failing (excluding NEEDS_INPUT checks).**"

  SYSTEM_MSG="PRD Validation iteration $NEXT_ITERATION of $MAX_ITERATIONS | PRD: $PRD_PATH"
fi

# Output JSON to block exit and feed prompt back
jq -n \
  --arg prompt "$PROMPT" \
  --arg msg "$SYSTEM_MSG" \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'

exit 0
