#!/bin/bash

# AT Build Ralph Stop Hook
# Prevents session exit when a Ralph loop is active
# Feeds the PRP plan execution prompt back for the next iteration

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# State file location
STATE_FILE=".claude/at-build-ralph.state.md"

# Check if Ralph loop is active
if [[ ! -f "$STATE_FILE" ]]; then
  # No active loop - allow exit
  exit 0
fi

# Parse YAML frontmatter from state file
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")

# Extract values
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
PLAN_PATH=$(echo "$FRONTMATTER" | grep '^plan_path:' | sed 's/plan_path: *//' | sed 's/^"\(.*\)"$/\1/')
INPUT_TYPE=$(echo "$FRONTMATTER" | grep '^input_type:' | sed 's/input_type: *//' | sed 's/^"\(.*\)"$/\1/')
PACKAGE_PATH=$(echo "$FRONTMATTER" | grep '^package_path:' | sed 's/package_path: *//' | sed 's/^"\(.*\)"$/\1/')

# Validate numeric fields
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  echo "Warning: AT Build Ralph state file corrupted (invalid iteration)" >&2
  rm "$STATE_FILE"
  exit 0
fi

if [[ ! "$MAX_ITERATIONS" =~ ^[0-9]+$ ]]; then
  echo "Warning: AT Build Ralph state file corrupted (invalid max_iterations)" >&2
  rm "$STATE_FILE"
  exit 0
fi

# Check if max iterations reached
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "AT Build Ralph: Max iterations ($MAX_ITERATIONS) reached."
  echo "   Check .claude/at-build-ralph.state.md for progress log."
  rm "$STATE_FILE"
  exit 0
fi

# Get transcript path from hook input
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "Warning: AT Build Ralph transcript not found" >&2
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

  # Check for completion promise
  if echo "$LAST_OUTPUT" | grep -q '<promise>COMPLETE</promise>'; then
    echo "AT Build Ralph: All validations passed! Loop complete."
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
  PROMPT="# AT Build Ralph Loop (Package Mode) - Iteration $NEXT_ITERATION

## Your Task

Continue executing the implementation from doc-core package until ALL validations pass.

**Package path**: \`$PACKAGE_PATH\`
**Plan file**: \`$PLAN_PATH\`
**State file**: \`.claude/at-build-ralph.state.md\`

## Instructions

1. **Re-read the package documents** for full context:
   - \`$PACKAGE_PATH/01-prd.md\` → Requirements and acceptance criteria
   - \`$PACKAGE_PATH/02-system-architecture.md\` → Architecture and tech stack
   - \`$PACKAGE_PATH/03-data-model.md\` → Database schema
   - \`$PACKAGE_PATH/04-api-specification.md\` → API endpoint contracts
   - \`$PACKAGE_PATH/05-user-flows.md\` → User journey validation
   - \`$PACKAGE_PATH/07-ux-specification.md\` → UI component specs
   - \`$PACKAGE_PATH/08-test-strategy.md\` → Test requirements
   - \`$PACKAGE_PATH/09-deployment-architecture.md\` → Infrastructure
   - \`$PACKAGE_PATH/10-security-assessment.md\` → Security requirements
2. **Read the plan file** - understand all tasks and validation requirements
3. **Check your previous work** - review files, git status, test outputs
4. **Identify what's incomplete** - which tasks/validations are still failing?
5. **Fix and implement** - address failures, complete remaining tasks
   - DB models/migrations → follow \`03-data-model.md\`
   - API routes → follow \`04-api-specification.md\`
   - Frontend components → follow \`07-ux-specification.md\`
   - Tests → follow \`08-test-strategy.md\`
6. **Run ALL validations** - lint, tests, build
7. **Update progress** - mark tasks complete, add learnings to state file

## Validation Requirements

Run these (or equivalent from your plan):
\`\`\`bash
# Backend
cd backend && source .venv/bin/activate && ruff check . && pytest
# Frontend
cd frontend && npm run lint && npm run build
\`\`\`

**Browser validation (if UI phase):**
If the plan involves frontend/UI changes, also verify:
- Start dev server, verify no console errors
- Verify routes load correctly
- Only output COMPLETE when browser validation also passes

## Completion

When ALL validations pass:
1. Generate implementation report
2. Archive the plan
3. Output: \`<promise>COMPLETE</promise>\`

If validations are still failing:
- Fix the issues
- End your response normally
- The loop will continue

**Do NOT output the completion promise if ANY validation is failing.**"

  SYSTEM_MSG="AT Build Ralph iteration $NEXT_ITERATION of $MAX_ITERATIONS | Package: $PACKAGE_PATH | Plan: $PLAN_PATH"
else
  # Plan/PRD mode prompt (existing behavior)
  PROMPT="# AT Build Ralph Loop - Iteration $NEXT_ITERATION

## Your Task

Continue executing the PRP plan until ALL validations pass.

**Plan file**: \`$PLAN_PATH\`
**State file**: \`.claude/at-build-ralph.state.md\`

## Instructions

1. **Read the plan file** - understand all tasks and validation requirements
2. **Check your previous work** - review files, git status, test outputs
3. **Identify what's incomplete** - which tasks/validations are still failing?
4. **Fix and implement** - address failures, complete remaining tasks
5. **Run ALL validations** - lint, tests, build
6. **Update progress** - mark tasks complete, add learnings to state file

## Validation Requirements

Run these (or equivalent from your plan):
\`\`\`bash
# Backend
cd backend && source .venv/bin/activate && ruff check . && pytest
# Frontend
cd frontend && npm run lint && npm run build
\`\`\`

**Browser validation (if UI phase):**
If the plan involves frontend/UI changes, also verify:
- Start dev server, verify no console errors
- Verify routes load correctly
- Only output COMPLETE when browser validation also passes

## Completion

When ALL validations pass:
1. Generate implementation report
2. Archive the plan
3. Output: \`<promise>COMPLETE</promise>\`

If validations are still failing:
- Fix the issues
- End your response normally
- The loop will continue

**Do NOT output the completion promise if ANY validation is failing.**"

  SYSTEM_MSG="AT Build Ralph iteration $NEXT_ITERATION of $MAX_ITERATIONS | Plan: $PLAN_PATH"
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
