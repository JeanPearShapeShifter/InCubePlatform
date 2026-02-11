# PRP Loop Hooks

This directory contains stop hooks for PRP autonomous loop systems.

## Setup

Both hooks are configured in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/wkoch/github-repos/incube-portal/.claude/hooks/prp-ralph-stop.sh"
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/wkoch/github-repos/incube-portal/.claude/hooks/prp-prd-validate-stop.sh"
          }
        ]
      }
    ]
  }
}
```

## How It Works

### Ralph Loop (`prp-ralph-stop.sh`)

1. When you run `/prp-ralph <plan>`, it creates `.claude/prp-ralph.state.md`
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

### PRD Validate Loop (`prp-prd-validate-stop.sh`)

1. When you run `/prp-prd-validate <prd>`, it creates `.claude/prp-prd-validate.state.md`
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

## Files

- `prp-ralph-stop.sh` - Ralph implementation loop hook
- `prp-prd-validate-stop.sh` - PRD validation loop hook
- `README.md` - This file

## Troubleshooting

### Hook not triggering

1. Verify hook is configured in settings:
   ```bash
   cat .claude/settings.local.json | jq '.hooks'
   ```

2. Check hook script is executable:
   ```bash
   ls -la .claude/hooks/prp-ralph-stop.sh
   ```

3. Test hook manually:
   ```bash
   echo '{"transcript_path": "/tmp/test.jsonl"}' | .claude/hooks/prp-ralph-stop.sh
   ```

### Loop not stopping

1. Verify completion promise is exact: `<promise>COMPLETE</promise>`
2. Check state file exists: `cat .claude/prp-ralph.state.md`
3. Check iteration count hasn't reached max

### Manual cancellation

Run `/prp-ralph-cancel` or:
```bash
rm .claude/prp-ralph.state.md
```
