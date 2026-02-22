---
name: commit
description: Full InCube Portal commit pipeline — stage, commit, push, create PR, merge to main. Handles GitHub account switching between antikythera-agent-zero and antikythera-technologies.
argument-hint: [commit message]
allowed-tools: Bash(git *), Bash(gh *)
---


# Commit Command

Full pipeline: commit -> push -> create PR -> merge to main. No stopping to ask questions — run it all the way through.

## Usage

```
/commit
```

Or with a message:
```
/commit feat: add agent orchestration service
```

## GitHub Account Configuration

| Repository | Required Account | Remote URL |
|------------|------------------|------------|
| incube-portal (this repo) | `antikythera-agent-zero` | github.com/antikythera-agent-zero/incube-portal |

**Important**: You (Wian) have two GitHub accounts:
- `antikythera-agent-zero` - For Claude Code (this agent) to push code
- `antikythera-technologies` - For ClaudeBot PRs that you review

You often switch accounts in the browser to review ClaudeBot's PRs and forget to switch back. This command catches that.

## What It Does (ALL steps, NO stopping)

1. **Account Verification** - Checks active GitHub account, auto-switches if wrong
2. **Stage All Changes** - Stages all modified and untracked files
3. **Commit** - Creates commit with conventional commit message
4. **Push** - Pushes branch to remote
5. **Create PR** - Creates a pull request against main
6. **Merge PR** - Merges the PR to main immediately

**CRITICAL: Do NOT stop between steps to ask questions. Do NOT make the PR or merge "optional". Run the ENTIRE pipeline automatically. The only reason to stop is if the wrong GitHub account is active and auto-switch fails.**

## Instructions for Claude

Execute ALL steps in order without pausing. The entire flow should complete in one go.

### Step 1: GitHub Account Verification

Check and auto-fix the active account:

```bash
# Get active account
ACTIVE_ACCOUNT=$(gh api user -q '.login' 2>/dev/null)

echo "Active account: $ACTIVE_ACCOUNT"

if [[ "$ACTIVE_ACCOUNT" != "antikythera-agent-zero" ]]; then
    echo "Wrong account, switching..."
    gh auth switch --user antikythera-agent-zero
    echo "Switched to antikythera-agent-zero"
fi
```

**If auto-switch fails, STOP and ask the user to fix it manually. Otherwise continue.**

### Step 2: Stage All Changes

```bash
git add -A
git status --short
```

**If there are no changes to commit, inform the user and stop.**

### Step 3: Create Commit

Generate a conventional commit message based on the changes. If the user provided a message with `/commit <message>`, use that instead.

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

```bash
git commit -m "$(cat <<'EOF'
<type>: <description>

<optional body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### Step 4: Push to Remote

```bash
BRANCH=$(git branch --show-current)
git push -u origin $BRANCH
```

### Step 5: Create Pull Request

**Do NOT ask the user if they want a PR. Always create one.**

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<bullet points summarizing the changes>

## Test plan
<checklist of verification steps>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Step 6: Merge PR to Main

**Do NOT ask the user if they want to merge. Always merge immediately.**

```bash
# Get the PR number from the create output, then merge
gh pr merge --merge
```

### Step 7: Confirm Completion

```bash
echo "=== Complete ==="
git log --oneline -1 origin/main
```

Report to the user: commit hash, PR number/URL, and confirmation that it's merged to main.

## Edge Cases

### Already on main
If working directly on main (no feature branch), create a feature branch first:
```bash
git checkout -b feat/<descriptive-name>
```
Then continue with the normal flow.

### No changes
If `git status` shows nothing to commit, tell the user and stop.

### Account switch fails
If `gh auth switch` fails, stop and ask the user to run `gh auth switch --user antikythera-agent-zero` manually.

## Troubleshooting

### "Remote repository not found"
```bash
git remote set-url origin https://github.com/antikythera-agent-zero/incube-portal.git
```

### "Permission denied"
```bash
gh auth switch --user antikythera-agent-zero
```
