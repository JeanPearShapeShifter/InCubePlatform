#!/bin/bash

# AT Doc Validate Stop Hook
# Prevents session exit when a doc validation loop is active
# Feeds the validation prompt back for the next iteration

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# State file location
STATE_FILE=".claude/at-doc-validate.state.md"

# Check if doc validation loop is active
if [[ ! -f "$STATE_FILE" ]]; then
  # No active loop - allow exit
  exit 0
fi

# Parse YAML frontmatter from state file
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")

# Extract values
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
PACKAGE_PATH=$(echo "$FRONTMATTER" | grep '^package_path:' | sed 's/package_path: *//' | sed 's/^"\(.*\)"$/\1/')

# Validate numeric fields
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  echo "Warning: AT Doc Validate state file corrupted (invalid iteration)" >&2
  rm "$STATE_FILE"
  exit 0
fi

if [[ ! "$MAX_ITERATIONS" =~ ^[0-9]+$ ]]; then
  echo "Warning: AT Doc Validate state file corrupted (invalid max_iterations)" >&2
  rm "$STATE_FILE"
  exit 0
fi

# Check if max iterations reached
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "AT Doc Validate: Max iterations ($MAX_ITERATIONS) reached."
  echo "  Check .claude/at-doc-validate.state.md for progress log."
  rm "$STATE_FILE"
  exit 0
fi

# Get transcript path from hook input
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "Warning: AT Doc Validate transcript not found" >&2
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

  # Check for DOC_COMPLETE promise
  if echo "$LAST_OUTPUT" | grep -q '<promise>DOC_COMPLETE</promise>'; then
    echo "AT Doc Validate: All checks passed! Documentation package is complete."
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
PROMPT="# Doc Validation Loop - Iteration $NEXT_ITERATION

## Your Task

Continue validating and fixing the documentation package until ALL checks pass.

**Package path**: \`$PACKAGE_PATH\`
**State file**: \`.claude/at-doc-validate.state.md\`

## Instructions

1. **Read the state file** - check the Progress Log for what was fixed/failed last iteration
2. **Read ALL 10 documents** - understand current state after previous fixes
3. **Re-run ALL 80 checks** - not just previously failing ones (fixes can introduce new issues)
4. **Fix failing checks** - edit documents directly to address gaps
5. **Write the validation report** - record new PASS/FAIL/NEEDS_INPUT status for each check
6. **Update state file** - append iteration results to Progress Log

## Validation Categories (10 total, 80 checks)

1. PRD Completeness (10 checks)
2. System Architecture (8 checks)
3. Data Model (8 checks)
4. API Specification (9 checks)
5. User Flows (7 checks)
6. Sequence Diagrams (6 checks)
7. UX Specification (8 checks)
8. Test Strategy (8 checks)
9. Deployment Architecture (8 checks)
10. Security Assessment (8 checks)

## Completion

When ALL checks are PASS or NEEDS_INPUT (no remaining FAIL):
1. Write final validation report
2. Delete the state file
3. Output: \`<promise>DOC_COMPLETE</promise>\`

If checks are still FAIL and you made progress (fixed something):
- End your response normally
- The loop will continue

If checks are still FAIL but no progress was made:
- Write validation report showing stuck checks
- Delete the state file
- Output: \`<promise>DOC_COMPLETE</promise>\` (with NEEDS_INPUT items noted)

**Do NOT output the completion promise if FAIL checks remain AND you made progress this iteration.**"

SYSTEM_MSG="Doc Validation iteration $NEXT_ITERATION of $MAX_ITERATIONS | Package: $PACKAGE_PATH"

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
