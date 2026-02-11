#!/bin/bash

# PRP PRD Validate Stop Hook
# Prevents session exit when a PRD validation loop is active
# Feeds the validation prompt back for the next iteration

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# State file location
STATE_FILE=".claude/prp-prd-validate.state.md"

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

# Validate numeric fields
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  echo "Warning: PRD Validate state file corrupted (invalid iteration)" >&2
  rm "$STATE_FILE"
  exit 0
fi

if [[ ! "$MAX_ITERATIONS" =~ ^[0-9]+$ ]]; then
  echo "Warning: PRD Validate state file corrupted (invalid max_iterations)" >&2
  rm "$STATE_FILE"
  exit 0
fi

# Check if max iterations reached
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "PRD Validate: Max iterations ($MAX_ITERATIONS) reached."
  echo "  Check .claude/prp-prd-validate.state.md for progress log."
  rm "$STATE_FILE"
  exit 0
fi

# Get transcript path from hook input
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "Warning: PRD Validate transcript not found" >&2
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
    echo "PRD Validate: All checks passed! PRD is complete."
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

# Build the prompt to feed back
PROMPT="# PRD Validation Loop - Iteration $NEXT_ITERATION

## Your Task

Continue validating and fixing the PRD until ALL checks pass.

**PRD file**: \`$PRD_PATH\`
**State file**: \`.claude/prp-prd-validate.state.md\`

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
