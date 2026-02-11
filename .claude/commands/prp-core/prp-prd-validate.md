# PRP PRD Validate

Autonomous PRD validation loop. Iterates through a PRD document checking against 19 categories of completeness criteria. Fixes issues found, re-validates, and loops until the PRD is 100% complete.

## Usage

```
/prp-prd-validate <prd-file-path> [--max-iterations 15]
```

## Arguments

- `prd-file-path`: Path to the PRD markdown file to validate
- `--max-iterations`: Maximum validation iterations (default: 15)

## Phase 0: SETUP

1. **Parse arguments** from `$ARGUMENTS`:
   - Extract PRD file path (the source/original PRD)
   - Extract max iterations (default 15)

2. **Validate source PRD exists**:
   - Read the source PRD file
   - If it doesn't exist, inform user and stop

3. **Create versioned working copy** (NEVER modify the original):

   a. Determine the project from the source PRD path:
      - If path contains `backend/` or the PRD content is about the API, AI agents, database → `{project}` = `backend`
      - If path contains `frontend/` or the PRD content is about the UI, React, Next.js → `{project}` = `frontend`
      - If unclear, ask the user which project this PRD belongs to

   b. Ensure output directory exists: `.claude/PRPs/prds/{project}/`

   c. Derive the PRD name from the source filename:
      - Strip path and extension: `incube-initial-prd.md` → `incube-initial-prd`
      - This becomes the `{prd-name}` for versioning

   d. Determine next version number:
      - Check `.claude/PRPs/prds/{project}/` for existing files matching `{prd-name}-v*.prd.md`
      - If none exist: version = 1
      - If `{prd-name}-v1.prd.md` exists: version = 2
      - If `{prd-name}-v3.prd.md` is the highest: version = 4
      - Always increment from the highest existing version

   e. Create the working copy:
      - Copy source PRD to: `.claude/PRPs/prds/{project}/{prd-name}-v{N}.prd.md`
      - Example: `.claude/PRPs/prds/backend/incube-initial-prd-v1.prd.md`
      - This is the file that gets edited during validation

   f. Inform the user:
      - "Source PRD: `{source-path}` (will NOT be modified)"
      - "Working copy: `.claude/PRPs/prds/{project}/{prd-name}-v{N}.prd.md`"
      - "Previous versions: {list any existing versions}"

4. **Create state file** at `.claude/prp-prd-validate.state.md`:

```markdown
---
iteration: 1
max_iterations: 15
source_prd_path: "<original-file-path>"
working_prd_path: ".claude/PRPs/prds/{project}/{prd-name}-v{N}.prd.md"
project: "{project}"
version: {N}
started_at: "<ISO 8601 timestamp>"
---

# PRD Validation Loop State

## Version History
- Source: `<original-file-path>`
- Working copy: `.claude/PRPs/prds/{project}/{prd-name}-v{N}.prd.md`
- Previous versions: {list or "none"}

## Discovered Patterns
(Persist any reusable patterns/context across iterations)

## Category Applicability
(After first scan, note which categories apply to this PRD)

## Progress Log
(Append after each iteration)
```

5. **Determine applicable categories**:
   - Read the working copy PRD to understand scope
   - Category 13 (AI/Conversation Flows): Only if PRD involves AI agents
   - All other categories: Always apply
   - Record applicability in state file

**CRITICAL: From this point forward, ALL reads and edits operate on the working copy path, NEVER the source PRD.**

## Phase 1: VALIDATE

Run ALL applicable checks from the checklist below. For each check:
- Read the relevant section(s) of the PRD
- Evaluate the PASS condition
- Record result as PASS or FAIL with specific details

### Category 1: Structure & Completeness

| # | Check | PASS Condition |
|---|-------|---------------|
| 1.1 | No placeholder text | Zero instances of "TBD", "TODO", "[placeholder]", "to be defined", "...", "fill in later", "needs input" |
| 1.2 | All TOC sections populated | Every section heading has substantive content (>3 lines of actual specification) |
| 1.3 | No empty subsections | No heading followed immediately by another heading without content |
| 1.4 | Consistent formatting | All tables have headers, all lists are complete, all code blocks have language tags |
| 1.5 | Implementation phases defined | Phase table exists with: phase number, description, status, dependencies, parallel flag |
| 1.6 | Architecture decisions documented | Each major decision has: choice made, alternatives considered, rationale for choice |

### Category 2: Database & ORM

| # | Check | PASS Condition |
|---|-------|---------------|
| 2.1 | All entities have tables | Every business entity mentioned in business rules/requirements has a CREATE TABLE statement |
| 2.2 | All columns specified | Each table has columns with: data type, constraints (NOT NULL, CHECK, DEFAULT, UNIQUE), and inline comments explaining purpose |
| 2.3 | Relationships mapped | Every FK has: REFERENCES clause with target table, ON DELETE/UPDATE behavior documented, relationship cardinality (1:1, 1:N, M:N) noted |
| 2.4 | Indexes defined | All columns used in WHERE/JOIN/ORDER BY have indexes; partial indexes with WHERE clause where appropriate; composite indexes for multi-column queries |
| 2.5 | No redundant fields | No column duplicates data available via JOIN; any intentional denormalization has explicit justification comment |
| 2.6 | Enums and constraints documented | All CHECK constraints with value lists have documentation explaining what each value means and when it's used |
| 2.7 | Seed/default data specified | All tables requiring initial data have INSERT statements with actual values (e.g., system_settings, default terms, reference data) |
| 2.8 | Sync/source tracking | Tables populated from external systems have: `last_synced_at TIMESTAMPTZ`, `source_system VARCHAR` fields |

### Category 3: API Specification

| # | Check | PASS Condition |
|---|-------|---------------|
| 3.1 | All user actions have endpoints | Every button/action in wireframes maps to a documented API endpoint or tool call |
| 3.2 | Request schemas defined | Every endpoint has typed parameters with: field name, type, required/optional, validation rules, description |
| 3.3 | Response schemas defined | Every endpoint has response structure with: field types, example values, nested object shapes |
| 3.4 | Error responses defined | Every endpoint specifies: HTTP status codes, error message format, recovery suggestions for the client |
| 3.5 | Auth requirements specified | Every endpoint declares access level: public, authenticated, admin-only, or specific role/user_type required |
| 3.6 | Validation rules documented | Every input parameter has validation: type check, range/length limits, format (regex if needed), specific error message on failure |
| 3.7 | Real-time events documented | If the system uses WebSocket/SSE: event catalog with event name, payload schema, direction (client→server / server→client), trigger condition, and room/channel scoping |

### Category 4: Authentication & Authorization

| # | Check | PASS Condition |
|---|-------|---------------|
| 4.1 | Auth flow complete | All flows defined: login, logout, register, email verification, password reset, token refresh, session expiry |
| 4.2 | Token specification | Defined: token type (JWT/session), payload contents, expiry duration, storage location (httpOnly cookie/localStorage), refresh mechanism and timing |
| 4.3 | Permission matrix complete | Table exists showing every user role × every resource/action = explicit access level (allow/deny/conditional) |
| 4.4 | User types distinguished | Each user type has documented: visibility rules (what they can see), service access (what they can do), pricing display rules (what numbers they see) |
| 4.5 | Security measures specified | Defined: password hashing algorithm, bcrypt rounds, session invalidation strategy, brute-force protection, CORS policy, CSRF protection approach |

### Category 5: UI/UX & Wireframes

| # | Check | PASS Condition |
|---|-------|---------------|
| 5.1 | All screens have wireframes | Every user-facing page has an ASCII art diagram OR detailed component-by-component layout description showing arrangement and hierarchy |
| 5.2 | Screen elements have data mappings | Each interactive/display element maps to a specific DB field or API response field (e.g., "Name field → `agents.name`") |
| 5.3 | States defined per screen | Each screen documents: empty state (no data), loading state, populated state, error state (what the user sees in each) |
| 5.4 | Navigation defined | Each screen has: route path, how user arrives (from where), where user can go next, back/cancel behavior |
| 5.5 | Responsive viewports specified | Layout differences documented for: Desktop (1920x1080), Tablet (768x1024), Mobile (375x812) |
| 5.6 | Pricing/sensitive display rules | For screens showing data that varies by user type: explicit examples of what each user type sees |
| 5.7 | Design tokens specified | Defined: color palette with hex values, typography hierarchy (font names + weights + sizes), effects/utilities (glass, shadows, animations) |

### Category 6: Business Logic & Rules

| # | Check | PASS Condition |
|---|-------|---------------|
| 6.1 | All stakeholder rules documented | Every business rule from source requirements/emails is captured and traceable |
| 6.2 | Rules have implementation code | Each complex rule has Python/TypeScript code showing exact logic, not just prose description |
| 6.3 | Calculation formulas explicit | All pricing/margin/quantity formulas defined with: formula notation, operator order, rounding rules |
| 6.4 | Edge cases covered | Each rule has scenarios for: zero values, maximum values, missing/null data, boundary conditions |
| 6.5 | State machines defined | Every entity with lifecycle has: enumerated states, valid transitions, triggers for each transition, guard conditions |
| 6.6 | Validation rules specified | Every user input has: type check, range/length limits, format requirements, specific error message for each failure mode |
| 6.7 | CRITICAL rules flagged | Domain-specific rules that are commonly misunderstood are marked with warnings and "DO THIS / NOT THAT" examples |

### Category 7: Cross-Reference Consistency

| # | Check | PASS Condition |
|---|-------|---------------|
| 7.1 | DB ↔ API alignment | Every field in API response schemas traces to a DB column or a documented computation |
| 7.2 | API ↔ UI alignment | Every data element shown in wireframes has a corresponding API endpoint that provides it |
| 7.3 | Permissions ↔ UI consistency | UI wireframes show/hide elements consistent with the permission matrix (no UI showing data the user can't access) |
| 7.4 | Business rules ↔ DB | Every business rule that stores/reads data references columns that exist in the schema |
| 7.5 | No orphan entities | No DB tables without API access; no API endpoints without UI consumption; no UI screens without supporting APIs |
| 7.6 | Notification triggers ↔ Events | Every notification in the trigger matrix maps to a specific system event that is actually generated in a documented workflow |

### Category 8: External Integrations

| # | Check | PASS Condition |
|---|-------|---------------|
| 8.1 | All integrations specified | Each external system has: base URL, authentication method, API version, rate limits |
| 8.2 | Request/response formats | Each external API call has: exact request structure (XML/JSON), response parsing logic, field-by-field mapping |
| 8.3 | Error handling per integration | Each external system has documented behavior for: timeout, invalid response, auth failure, rate limit hit, service unavailable |
| 8.4 | Sync strategy defined | For data-syncing integrations: schedule (cron expression), dependency chain, staging approach, conflict resolution, retry policy |
| 8.5 | Data mapping documented | Explicit mapping table: external field name → internal DB column, with any transformations noted |
| 8.6 | Credential management | How API keys/passwords are: stored (encrypted columns, env vars), rotated, accessed at runtime, scoped per environment |

### Category 9: Logging & Observability

| # | Check | PASS Condition |
|---|-------|---------------|
| 9.1 | Log format defined | Structured log interface specified with fields: timestamp (ISO 8601), level, log_type, request_id, agent_id, message, data, duration_ms |
| 9.2 | Log types catalogued | All log categories defined: HTTP_REQUEST, HTTP_RESPONSE, EXTERNAL_API, DB_QUERY, AI_TOOL_CALL, WEBSOCKET, AUTH, BUSINESS_EVENT, ERROR, SYSTEM |
| 9.3 | Example logs provided | Each log type has at least one concrete JSON example showing realistic output with real field values |
| 9.4 | Correlation IDs specified | Request tracing strategy documented: how request_id is generated, propagated across async operations, and included in responses |
| 9.5 | Environment config defined | Logging configuration variables listed: LOG_LEVEL, LOG_FORMAT (json/text), LOG_FILE path, LOG_INCLUDE_SENSITIVE (bool) |

### Category 10: Notifications & Communication

| # | Check | PASS Condition |
|---|-------|---------------|
| 10.1 | Trigger matrix complete | Table exists mapping: event name → in-app delivery (yes/no) → email delivery (yes/no) → timing (immediate/delayed/scheduled) |
| 10.2 | Email templates specified | Each outbound email has: subject line template, body template with variable placeholders, recipient determination logic |
| 10.3 | Preferences system defined | User-configurable settings: which notifications can be toggled, quiet hours config, urgency override rules |
| 10.4 | Follow-up automation | Auto-reminder rules defined: trigger condition, delay before sending, max retry count, escalation path if no response |

### Category 11: Testing & Validation

| # | Check | PASS Condition |
|---|-------|---------------|
| 11.1 | Validation criteria per phase | Each implementation phase has specific pass/fail criteria that can be verified programmatically |
| 11.2 | Browser validation defined | For UI phases: routes to test, viewport sizes, screenshot requirements, console error checks, interaction tests |
| 11.3 | Failure procedures documented | What happens when tests fail: error format to capture, screenshot requirements, PR blocking rules, retry procedures |
| 11.4 | Business rule test cases | Each critical calculation has: input values → expected output values, documented as testable assertions |

### Category 12: Performance & Accessibility

| # | Check | PASS Condition |
|---|-------|---------------|
| 12.1 | Performance targets defined | Table with: metric name (FCP, TTI, response time), target value, measurement tool/method |
| 12.2 | Optimization strategies listed | For each performance-sensitive operation: caching approach, lazy loading strategy, pagination/virtualization plan |
| 12.3 | WCAG compliance specified | Documented: required contrast ratios, keyboard navigation requirements, ARIA label strategy, prefers-reduced-motion handling |

### Category 13: AI/Conversation Flows (Conditional)

**Skip this category if the PRD does not involve AI agents or conversational interfaces.**

| # | Check | PASS Condition |
|---|-------|---------------|
| 13.1 | AI persona defined | Personality traits, tone guidelines, error recovery behavior, escalation triggers documented |
| 13.2 | Tool definitions complete | Each AI tool has: name, typed parameter schema, return type schema, error codes, usage examples |
| 13.3 | Conversation examples provided | At least one complete transcript showing: happy path flow, one error recovery flow, one edge case |
| 13.4 | Animation/state catalog | Each AI interface state has: trigger condition, visual behavior description, transition rules to other states |
| 13.5 | System prompt requirements | Complete list of rules/constraints that must be embedded in the AI system prompt |

### Category 14: Project Scaffolding & Configuration

| # | Check | PASS Condition |
|---|-------|---------------|
| 14.1 | Folder structure defined | Complete directory tree showing where each type of file lives (routes, services, models, utils, tests, config) |
| 14.2 | Entry points specified | Documented: main application entry, worker/background processes, scheduler entry, CLI commands, migration runner |
| 14.3 | Environment variables listed | Complete table: variable name, type (string/int/bool), default value, required/optional flag, description |
| 14.4 | Package dependencies specified | Critical libraries listed with version ranges or pinned versions (framework, ORM, HTTP client, test runner, etc.) |
| 14.5 | Configuration pattern defined | How config loads: source priority (env vars > .env > defaults), validation on startup, typed config class structure |
| 14.6 | Base patterns documented | Base class patterns for: models (timestamps, soft-delete), services (dependency injection), errors (error hierarchy), responses (envelope format) |
| 14.7 | Background jobs catalogued | Each scheduled/background job has: name, trigger type (cron/interval/event), description of what it does, dependencies, error/retry behavior, idempotency strategy |

### Category 15: End-to-End User Journeys

| # | Check | PASS Condition |
|---|-------|---------------|
| 15.1 | Primary journey documented | At least one complete happy-path journey showing every step: user action → UI state → API call → DB write → UI response, end to end |
| 15.2 | Journey uses real data | The documented journey uses concrete realistic data values, not generic placeholders (actual names, dates, prices) |
| 15.3 | Feature boundaries explicit | Every handoff between features documents: what triggers the transition, what data is passed, what validations run at the boundary, what can fail |
| 15.4 | Alternate paths documented | At least one error/cancel/back path per major journey showing: how the user gets back on track, what data is preserved, what is discarded |

### Category 16: Concurrency & Data Integrity

| # | Check | PASS Condition |
|---|-------|---------------|
| 16.1 | Concurrent access handled | For every shared mutable resource: strategy defined (optimistic locking, pessimistic locking, last-write-wins, queue) |
| 16.2 | Transaction boundaries defined | Which multi-step operations must be atomic? What rolls back on partial failure? Database transaction scopes documented |
| 16.3 | Idempotency specified | API calls that may be retried (webhooks, async jobs) are marked idempotent with strategy (idempotency keys, upsert logic) |
| 16.4 | Race conditions identified | Known race scenarios listed with mitigation: e.g., "sync runs during quote generation → quote reads from production tables only, not staging" |

### Category 17: Deployment & Infrastructure

| # | Check | PASS Condition |
|---|-------|---------------|
| 17.1 | Deployment method defined | Specified: containerized/bare-metal/serverless, port assignments, reverse proxy config, static asset serving |
| 17.2 | Health checks specified | Health endpoint defined: what it checks (DB connection, external API reachability, memory usage), expected response format, failure behavior |
| 17.3 | Startup order documented | Service dependency chain: which services must be running before others start (DB → API → worker → scheduler → frontend) |
| 17.4 | Migration strategy defined | Documented: migration tool (alembic/knex/prisma), file naming convention, up/down patterns, rollback procedure, seed data approach per environment |
| 17.5 | Database environments separated | Development and production database environments clearly defined: separate connection strings, separate Docker configs (docker-compose.dev.yml vs docker-compose.yml), dev seed data strategy, production backup strategy, environment separation rules (never use prod URL in dev, never seed prod) |

### Category 18: Worked Examples & Gotchas

| # | Check | PASS Condition |
|---|-------|---------------|
| 18.1 | Every formula has worked examples | Each calculation has at least 2 concrete numeric examples: one normal case, one edge case (minimum/maximum/zero) |
| 18.2 | Gotcha list maintained | Known pitfalls explicitly listed with "DO THIS / NOT THAT" format showing correct vs incorrect implementation |
| 18.3 | Decision log for ambiguities | Any "it could go either way" decision is explicitly resolved with reasoning recorded (not left for implementer to guess) |
| 18.4 | Real data examples provided | At least one realistic dataset that flows through the complete system (real names, dates, prices, not lorem ipsum) |

### Category 19: Business Features & Stakeholder Summary

**Purpose:** This section serves as both a validation tool (if you can't explain it in plain language, it's not well-understood) and a shareable document for non-technical business partners to review and sign off on before development begins.

| # | Check | PASS Condition |
|---|-------|---------------|
| 19.1 | Feature catalog exists | A complete numbered list of every feature the application offers, written in plain business language (no technical jargon) |
| 19.2 | User capabilities per role | For each user type (e.g., consultant, admin, external agent): a bulleted list of "You can..." statements describing every action available to them |
| 19.3 | End-to-end workflows in business terms | Each major workflow described as a business process: "The consultant receives an email → opens the system → speaks to the agent → receives 3 quotes → sends to client" (not API calls or DB writes) |
| 19.4 | Screen-by-screen walkthrough | Plain language description of each screen: what the user sees, what they can click/type, what happens when they do (written for someone who has never seen the app) |
| 19.5 | Feature value statements | For each major feature: why it matters to the business (time saved, errors prevented, revenue impact, client experience improvement) |
| 19.6 | Limitations and exclusions | What the system explicitly does NOT do, written clearly so stakeholders don't assume capabilities that aren't being built |

**Format guidance for this section:**

The business features section should be written as if explaining the application to a business partner over coffee. Use:
- Simple language (no "API", "database", "ORM", "webhook")
- Active voice ("You click the button" not "The button is clicked")
- Concrete examples ("You type 'Cape Town, 4 nights, 10 golfers' and the agent finds hotels" not "Natural language processing extracts travel parameters")
- Visual flow descriptions ("The screen shows three quote cards side by side - Budget, Standard, and Premium")
- Before/after comparisons where helpful ("Today you spend 2 hours building a quote manually. With this system, you describe the trip and get 3 quotes in 2 minutes")

---

## Phase 2: REPORT

After running all checks, generate a validation report:

```markdown
# PRD Validation Report - Iteration {N}

## Overall: {PASS_COUNT}/{TOTAL_APPLICABLE} checks passing ({PERCENTAGE}%)

## PASSING CHECKS:
(List all passing checks briefly)

## FAILING CHECKS:

### {Check Number} {Check Name} - FAIL
**Location in PRD:** {section/line reference}
**What's missing:** {specific description of what needs to be added}
**How to fix:** {concrete instruction for what content to write}

(Repeat for each FAIL)

## FIXED THIS ITERATION:
(List what was fixed, with before/after summary)
```

## Phase 3: FIX

For each FAILING check:

1. **Determine if fixable** - Can you add the missing content based on context in the PRD?
   - If the fix requires domain knowledge you don't have → Mark as "NEEDS_INPUT" and describe what question to ask
   - If the fix can be derived from existing PRD content → Fix it

2. **Apply fixes** - Edit the working copy (NEVER the source):
   - All edits go to the versioned working copy at `.claude/PRPs/prds/{project}/{prd-name}-v{N}.prd.md`
   - Add missing sections/content
   - Fill in gaps based on patterns already in the document
   - Ensure fixes are consistent with existing content
   - Don't remove existing content unless it contradicts other sections

3. **Preserve structure** - Maintain the PRD's existing formatting, heading hierarchy, and style

4. **Log fixes** - Record what was fixed in the validation report

## Phase 4: RE-VALIDATE

After applying fixes:
- Re-run ALL checks (not just the ones that failed)
- Fixes in one area can introduce issues in another (cross-reference consistency)
- Update the validation report with new results

## Phase 5: COMPLETION CHECK

### If ALL applicable checks PASS:
1. Write final validation report to `.claude/PRPs/reports/{project}/prd-validation-{prd-name}-v{N}-report.md`
2. Update state file progress log with final summary
3. Inform user of output artifacts:
   - "Source PRD (unchanged): `{source_prd_path}`"
   - "Validated PRD (v{N}): `.claude/PRPs/prds/{project}/{prd-name}-v{N}.prd.md`"
   - "Validation report: `.claude/PRPs/reports/{project}/prd-validation-{prd-name}-v{N}-report.md`"
4. Output: `<promise>PRD_COMPLETE</promise>`

### If checks are still FAILING:
1. Update state file progress log with:
   - Which checks passed/failed
   - What was fixed this iteration
   - What remains and why (needs input? complex cross-reference issue?)
2. End your response normally
3. The stop hook will feed you back for the next iteration

### If checks require user input:
1. List the questions that need answers in the validation report
2. Mark those checks as "NEEDS_INPUT" (not FAIL)
3. Note: NEEDS_INPUT checks do NOT block completion if all other checks pass
4. The user can address these in a follow-up session

## Important Rules

- **Never invent business rules** - If a check fails because business logic is missing, mark it NEEDS_INPUT rather than guessing
- **Maintain existing quality** - Don't simplify or reduce detail in sections that already pass
- **Cross-reference on every iteration** - Category 7 must be re-checked after every fix
- **Be specific in failure reports** - "Section 5.2 is incomplete" is bad. "The Dashboard screen wireframe is missing data mappings for the SLA metrics panel - needs to show which DB fields (leads.sla_due_at, leads.sla_breached) map to which UI elements" is good
- **Don't over-engineer** - If a section is adequate for implementation, don't add unnecessary detail just to be thorough. The goal is implementability, not verbosity
- **Respect conditional categories** - Skip Category 13 if no AI features. Don't add AI sections to a non-AI PRD

## State File Updates

After each iteration, append to the Progress Log section:

```markdown
### Iteration {N} - {timestamp}
- Checks passing: {X}/{Y} ({Z}%)
- Fixed: {list of check numbers fixed}
- Remaining failures: {list of check numbers still failing}
- Needs input: {list of questions for user}
- Key learnings: {any patterns discovered}
```

## Completion Criteria

The loop exits when ONE of:
1. **All applicable checks pass** → Output `<promise>PRD_COMPLETE</promise>`
2. **All fixable checks pass, remainder are NEEDS_INPUT** → Output `<promise>PRD_COMPLETE</promise>` with note about remaining questions
3. **Max iterations reached** → Stop hook handles cleanup
