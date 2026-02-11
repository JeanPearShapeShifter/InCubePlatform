# Antikythera Loop Hooks

This directory contains stop hooks for Antikythera autonomous loop systems.

## Setup

All hooks are configured in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/wkoch/github-repos/incube-portal/.claude/hooks/at-build-ralph-stop.sh"
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/wkoch/github-repos/incube-portal/.claude/hooks/at-build-validate-stop.sh"
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/wkoch/github-repos/incube-portal/.claude/hooks/at-doc-validate-stop.sh"
          }
        ]
      }
    ]
  }
}
```

## How It Works

### Ralph Loop (`at-build-ralph-stop.sh`)

1. When you run `/at-build:ralph <plan>`, it creates `.claude/at-build-ralph.state.md`
2. The stop hook checks for this state file on every exit attempt
3. If the state file exists and completion promise not found:
   - Increments iteration counter
   - Feeds the execution prompt back to Claude
   - Loop continues
4. If completion promise (`<promise>COMPLETE</promise>`) detected:
   - State file is removed
   - Session exits normally
5. If max iterations reached:
   - State file is removed
   - Session exits normally

### Build Validate Loop (`at-build-validate-stop.sh`)

1. When you run `/at-build:validate <prd>`, it creates `.claude/at-build-validate.state.md`
2. The stop hook checks for this state file on every exit attempt
3. If the state file exists and completion promise not found:
   - Increments iteration counter
   - Feeds the validation prompt back to Claude
   - Loop continues
4. If completion promise (`<promise>PRD_COMPLETE</promise>`) detected:
   - State file is removed
   - Session exits normally
5. If max iterations reached:
   - State file is removed
   - Session exits normally

### Doc Validate Loop (`at-doc-validate-stop.sh`)

1. When you run `/at-doc:validate <package>`, it creates `.claude/at-doc-validate.state.md`
2. The stop hook checks for this state file on every exit attempt
3. If the state file exists and completion promise not found:
   - Increments iteration counter
   - Feeds the validation prompt back to Claude
   - Loop continues
4. If completion promise (`<promise>DOC_COMPLETE</promise>`) detected:
   - State file is removed
   - Session exits normally
5. If max iterations reached:
   - State file is removed
   - Session exits normally

## Files

- `at-build-ralph-stop.sh` - Ralph implementation loop hook
- `at-build-validate-stop.sh` - PRD/package validation loop hook
- `at-doc-validate-stop.sh` - Documentation validation loop hook
- `README.md` - This file

## Troubleshooting

### Hook not triggering

1. Verify hook is configured in settings:
   ```bash
   cat .claude/settings.local.json | jq '.hooks'
   ```

2. Check hook script is executable:
   ```bash
   ls -la .claude/hooks/at-build-ralph-stop.sh
   ```

3. Test hook manually:
   ```bash
   echo '{"transcript_path": "/tmp/test.jsonl"}' | .claude/hooks/at-build-ralph-stop.sh
   ```

### Loop not stopping

1. Verify completion promise is exact: `<promise>COMPLETE</promise>`
2. Check state file exists: `cat .claude/at-build-ralph.state.md`
3. Check iteration count hasn't reached max

### Manual cancellation

Run `/at-build:ralph-cancel` or:
```bash
rm .claude/at-build-ralph.state.md
```
