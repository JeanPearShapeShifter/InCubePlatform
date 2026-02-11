---
description: Create a PR from current branch with unpushed commits
argument-hint: [base-branch] (default: main)
---

# Create Pull Request

**Base branch**: $ARGUMENTS (default: main)

---

## Your Mission

Create a well-formatted pull request from the current branch, using repository PR templates if available, with a clear summary of changes.

---

## Phase 1: VALIDATE - Check Prerequisites

### 1.1 Verify Git State

```bash
git branch --show-current
git status --short
git log origin/main..HEAD --oneline
```

| State | Action |
|-------|--------|
| On main/master | STOP: "Cannot create PR from main." |
| Uncommitted changes | WARN: "Uncommitted changes exist." |
| No commits ahead | STOP: "No commits to create PR from." |
| Has commits, clean | PROCEED |

### 1.2 Check for Existing PR

```bash
gh pr list --head $(git branch --show-current) --json number,url
```

---

## Phase 2: DISCOVER - Gather Context

### 2.1 Check for PR Template

```bash
ls -la .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
```

### 2.2 Analyze Commits

```bash
git log origin/main..HEAD --pretty=format:"- %s"
git diff --stat origin/main..HEAD
```

---

## Phase 3: PUSH

```bash
git push -u origin HEAD
```

---

## Phase 4: CREATE PR

```bash
gh pr create \
  --title "{title}" \
  --base "{base-branch}" \
  --body "$(cat <<'EOF'
## Summary

{description}

## Changes

{commit summaries}

## Testing

- [ ] Type check passes
- [ ] Tests pass
- [ ] Manually verified
EOF
)"
```

---

## Phase 5: OUTPUT

```markdown
## Pull Request Created

**PR**: #{number}
**URL**: {url}
**Title**: {title}
**Base**: {base-branch} <- {current-branch}
```

---

## Success Criteria

- **BRANCH_PUSHED**: Current branch exists on origin
- **PR_CREATED**: PR successfully created via gh
- **URL_RETURNED**: User has the PR URL
