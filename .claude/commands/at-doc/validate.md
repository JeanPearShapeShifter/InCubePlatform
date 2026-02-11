# AT Doc: Validate Documentation Package

You are a documentation quality auditor. Your job is to run a comprehensive completeness checklist against a documentation package, fix what you can, and flag what needs user input.

**Input:** `$ARGUMENTS` is the path to a documentation package directory (e.g., `.claude/docs/packages/{project}/{slug}/`).

---

## Phase 0: SETUP

1. Read `$ARGUMENTS` — the package directory path
2. If `$ARGUMENTS` is empty, ask the user for the path. Wait.
3. Read `README.md` from the package directory to get project info
4. Determine the state file path: `.claude/at-doc-validate.state.md`
5. Check if a state file already exists (resuming a previous run):
   - **If exists:** Read it, extract the iteration number, continue from where you left off
   - **If not exists:** Create it with the template below
6. Tell the user: _"Starting validation of **{project}** documentation package (iteration {N})..."_

### State File Template

```markdown
---
project: "{project}"
package_path: "{package-path}"
iteration: 1
max_iterations: 5
started: "{YYYY-MM-DD HH:MM}"
---

# Doc-Validate State: {project}

## Progress Log

### Iteration 1
- Started: {timestamp}
- Checks run: 0
- Passed: 0
- Failed: 0
- Fixed: 0
- Needs input: 0
```

---

## Phase 1: READ ALL DOCUMENTS

Read every document in the package directory:
- `01-prd.md`
- `02-system-architecture.md`
- `03-data-model.md`
- `04-api-specification.md`
- `05-user-flows.md`
- `06-sequence-diagrams.md`
- `07-ux-specification.md`
- `08-test-strategy.md`
- `09-deployment-architecture.md`
- `10-security-assessment.md`
- `review-report.md` (if exists)
- `business/` subfolder (if exists): read all files (`README.md`, `executive-summary.md`, `feature-catalog.md`, `user-walkthroughs.md`, `business-rules.md`, `stakeholder-faq.md`)
- `strategy/` subfolder (if exists): read all files (`README.md`, `market-analysis.md`, `competitive-landscape.md`, `business-model.md`, `go-to-market.md`, `mvp-validation.md`)

---

## Phase 2: RUN VALIDATION CHECKS

Run ALL applicable checks below. For each check, determine:
- **PASS** — Check is satisfied
- **FAIL** — Check is not satisfied, AND you can fix it by editing the document
- **NEEDS_INPUT** — Check is not satisfied, and you need information from the user to fix it

### Category 1: PRD Completeness (01-prd.md) — 10 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 1.1 | Executive summary exists | Non-empty section with 2+ paragraphs |
| 1.2 | Problem statement is specific | No vague language ("various", "etc.", "and more") |
| 1.3 | Target users defined | At least 1 persona with description and goals |
| 1.4 | Success metrics are measurable | Each metric has a numeric target and measurement method |
| 1.5 | Core features listed | At least 3 features with descriptions and acceptance criteria |
| 1.6 | Feature priority matrix present | Table with Priority and Complexity columns |
| 1.7 | Non-functional requirements specified | Performance, scalability, reliability each have numeric targets |
| 1.8 | Out of scope section exists | At least 1 explicit exclusion |
| 1.9 | No placeholder text | Zero instances of "TBD", "TODO", "placeholder", "{...}" |
| 1.10 | Glossary present | At least 3 domain-specific terms defined |

### Category 2: System Architecture (02-system-architecture.md) — 8 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 2.1 | C4 Context diagram present | Mermaid block with C4Context or equivalent |
| 2.2 | C4 Container diagram present | Mermaid block with C4Container or equivalent |
| 2.3 | C4 Component diagram present | Mermaid block with C4Component or equivalent |
| 2.4 | Technology stack table complete | Every layer has technology AND justification |
| 2.5 | At least 1 ADR documented | ADR with Status, Context, Decision, Consequences |
| 2.6 | Communication patterns described | Section exists with specific protocols (REST, gRPC, etc.) |
| 2.7 | Scalability strategy defined | Specific approach (not just "scales horizontally") |
| 2.8 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 3: Data Model (03-data-model.md) — 8 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 3.1 | ERD present | Mermaid erDiagram block exists |
| 3.2 | All entities have column definitions | Every entity has a table with Type, Constraints, Description |
| 3.3 | Primary keys defined | Every entity table has a PK column |
| 3.4 | Relationships have cardinality | ERD shows 1:1, 1:N, M:N for all relationships |
| 3.5 | Indexes specified | At least 1 index per entity with justification |
| 3.6 | Data types are specific | No generic "string" — use VARCHAR(N), TEXT, etc. |
| 3.7 | Foreign keys explicit | Relationship section lists FK columns |
| 3.8 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 4: API Specification (04-api-specification.md) — 9 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 4.1 | Base URL and versioning defined | Section 1 has specific base URL pattern |
| 4.2 | Auth mechanism specified | Section 2 describes specific mechanism (JWT, OAuth2, etc.) |
| 4.3 | Error response format defined | Standard error envelope with code and message fields |
| 4.4 | All endpoints have method + path | Every endpoint starts with `METHOD /path` |
| 4.5 | Request schemas present | Every mutating endpoint (POST, PUT, PATCH) has request body schema |
| 4.6 | Response schemas present | Every endpoint has at least one response schema |
| 4.7 | Error responses per endpoint | Every endpoint has error response table with status codes |
| 4.8 | Auth requirements per endpoint | Every endpoint specifies required role or "public" |
| 4.9 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 5: User Flows (05-user-flows.md) — 7 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 5.1 | At least 3 user flows documented | 3+ flow sections with diagrams |
| 5.2 | Mermaid flowcharts present | Each flow has a Mermaid flowchart block |
| 5.3 | Step-by-step tables present | Each flow has a table with User Action, System Response, API Call columns |
| 5.4 | Error paths documented | Each flow has an Error Paths table |
| 5.5 | Personas linked to flows | Each flow specifies which persona performs it |
| 5.6 | API calls reference real endpoints | API Call column values match endpoints in 04-api-specification.md |
| 5.7 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 6: Sequence Diagrams (06-sequence-diagrams.md) — 6 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 6.1 | At least 3 sequences documented | 3+ sequence sections |
| 6.2 | Mermaid sequenceDiagram blocks present | Each sequence has a Mermaid sequenceDiagram block |
| 6.3 | All actors identified | Each diagram has participant declarations |
| 6.4 | Async operations marked | Async calls use appropriate Mermaid notation (activate/deactivate, notes) |
| 6.5 | Error/alt paths included | At least 1 sequence uses alt/opt fragment for error handling |
| 6.6 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 7: UX Specification (07-ux-specification.md) — 8 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 7.1 | Design tokens defined | Table with at least color-primary and spacing-unit |
| 7.2 | At least 3 screens specified | 3+ screen specification sections |
| 7.3 | State machines present | At least 1 Mermaid stateDiagram-v2 block |
| 7.4 | All screens have 4 states | Each screen defines Empty, Loading, Populated, Error states |
| 7.5 | Interactive elements listed | Each screen has an interactive elements table |
| 7.6 | Navigation structure diagrammed | Mermaid diagram showing screen navigation |
| 7.7 | Responsive breakpoints defined | Table with at least Mobile, Tablet, Desktop |
| 7.8 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 8: Test Strategy (08-test-strategy.md) — 8 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 8.1 | Test pyramid diagram present | Mermaid diagram showing test type distribution |
| 8.2 | Unit test section complete | Framework named, coverage target specified as percentage |
| 8.3 | Integration test scenarios listed | At least 3 specific integration test scenarios |
| 8.4 | E2E critical paths defined | Table with Path, Steps, Expected Outcome columns |
| 8.5 | Performance targets specified | Table with numeric thresholds (p95 response time, throughput) |
| 8.6 | CI/CD pipeline stages defined | Table with Stage, Tests Run, Blocking, Duration columns |
| 8.7 | Quality gates defined | Table with Gate, Criteria, Enforcement columns |
| 8.8 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 9: Deployment Architecture (09-deployment-architecture.md) — 8 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 9.1 | Deployment diagram present | Mermaid diagram showing infrastructure topology |
| 9.2 | Environments table complete | Table with at least Development, Staging, Production rows |
| 9.3 | Infrastructure components listed | Compute, Storage, Networking sections have specific technologies |
| 9.4 | CI/CD pipeline diagrammed | Mermaid flowchart showing build → test → deploy |
| 9.5 | Deployment strategy specified | Named strategy (rolling, blue-green, canary) with justification |
| 9.6 | Health check endpoints defined | Table with Endpoint, Interval, Timeout, Alert Threshold |
| 9.7 | Backup strategy defined | Table with Data, Method, Frequency, Retention columns |
| 9.8 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 10: Security Assessment (10-security-assessment.md) — 8 checks

| # | Check | PASS Condition |
|---|-------|----------------|
| 10.1 | Security architecture diagram present | Mermaid diagram showing trust boundaries |
| 10.2 | Auth mechanism detailed | Specific mechanism with token format and refresh strategy |
| 10.3 | Authorization model defined | Named model (RBAC, ABAC) with role definitions table |
| 10.4 | OWASP Top 10 table complete | All 10 rows have Risk Level and Mitigation filled |
| 10.5 | Encryption at rest specified | Specific algorithm and key management approach |
| 10.6 | Encryption in transit specified | TLS version, certificate management |
| 10.7 | API security measures listed | Rate limiting, input validation, CORS, CSP mentioned |
| 10.8 | No placeholder text | Zero instances of "TBD", "TODO", "{...}" |

### Category 11: Business Documents (business/ subfolder) — 8 conditional checks

**These checks ONLY run if a `business/` subfolder exists in the package directory.** If the subfolder does not exist, skip this category entirely and do not report it as a failure.

| # | Check | PASS Condition |
|---|-------|----------------|
| 11.1 | Executive summary exists and is concise | `business/executive-summary.md` exists and is under ~500 words (1 page) |
| 11.2 | Feature catalog covers all PRD features | Every feature listed in `01-prd.md` Section 4 has a corresponding section in `business/feature-catalog.md` |
| 11.3 | User walkthroughs cover all personas | Every persona from `01-prd.md` Section 2.3 has a walkthrough in `business/user-walkthroughs.md` |
| 11.4 | Business rules are formatted correctly | Every rule in `business/business-rules.md` has When/Then/Example/Applies-to fields |
| 11.5 | FAQ has sufficient coverage | `business/stakeholder-faq.md` has at least 5 category sections with at least 2 questions each |
| 11.6 | No technical jargon violations | Business documents do not use bare technical terms (endpoint, payload, schema, middleware, ORM, container, microservice, JWT, OAuth, gRPC, SDK) without plain-English explanation |
| 11.7 | No placeholder text | Zero instances of "TBD", "TODO", "placeholder", "{...}" in any business document |
| 11.8 | Business README index links are valid | `business/README.md` exists and all linked document filenames match actual files in the `business/` directory |

### Category 12: Strategy Documents (strategy/ subfolder) — 8 conditional checks

**These checks ONLY run if a `strategy/` subfolder exists in the package directory.** If the subfolder does not exist, skip this category entirely and do not report it as a failure.

| # | Check | PASS Condition |
|---|-------|----------------|
| 12.1 | Market analysis covers all factors | `strategy/market-analysis.md` has all 6 PESTLE factors (Political, Economic, Social, Technological, Legal, Environmental) and all 5 Porter's forces (Industry Rivalry, Threat of New Entrants, Threat of Substitutes, Supplier Power, Buyer Power) with specific, non-generic content |
| 12.2 | Venture SWOT has 5 items per quadrant | `strategy/competitive-landscape.md` has exactly 5 Strengths, 5 Weaknesses, 5 Opportunities, and 5 Threats, each with evidence |
| 12.3 | At least 1 named competitor with profile | `strategy/competitive-landscape.md` has at least 1 competitor profile with a real company/product name (not "Competitor A"), including strengths, weaknesses, and differentiation |
| 12.4 | Business model has all 9 canvas blocks | `strategy/business-model.md` has all 9 Business Model Canvas blocks (Value Proposition, Customer Segments, Channels, Customer Relationships, Revenue Streams, Key Resources, Key Activities, Key Partnerships, Cost Structure) populated with specific content |
| 12.5 | Unit economics section present | `strategy/business-model.md` has a Unit Economics section with ARPU, CAC, LTV, LTV:CAC Ratio, and Breakeven — each with a value (or explicit "Assumption:" / "Target:" label) |
| 12.6 | Go-to-market has at least 2 launch phases | `strategy/go-to-market.md` defines at least Phase 1 (MVP Launch) and Phase 2 (Growth) with target segments and KPIs |
| 12.7 | MVP validation has at least 5 testable assumptions | `strategy/mvp-validation.md` has at least 5 assumptions in the Testable Assumptions table, each with Test, Pass Criteria, Fail Action, and Priority columns filled |
| 12.8 | No fabricated metrics | No statistics stated as facts without "Assumption:", "Target:", or "To be validated" label across all strategy documents. No percentages or dollar amounts presented as established data when the product doesn't exist yet |

**Total: 80 checks + 8 conditional (business/) + 8 conditional (strategy/)**

---

## Phase 3: FIX FAILING CHECKS

For each FAIL check (not NEEDS_INPUT):

1. Open the relevant document
2. Edit it to satisfy the check's PASS condition
3. Log what you fixed

### Fix Priorities
1. Missing diagrams (Mermaid blocks) — generate based on document content
2. Placeholder text — replace with specific content derived from other documents in the package
3. Missing sections — add with content extrapolated from existing sections
4. Missing tables — create with appropriate columns and rows

### Cross-Reference After Fixes
After fixing any document, re-check:
- Category 5, check 5.6 (API calls reference real endpoints)
- Any naming consistency across documents you modified

---

## Phase 4: WRITE VALIDATION REPORT

Write `validation-report.md` to the package directory:

```markdown
---
document: "validation-report"
project: "{project}"
generated: "{YYYY-MM-DD}"
iteration: {N}
---

# Validation Report: {Title}

## Summary

| Status | Count |
|--------|-------|
| PASS | {n} |
| FAIL (Fixed) | {n} |
| NEEDS_INPUT | {n} |
| **Total** | **{80 + 8 if business/ + 8 if strategy/}** |

**Completion: {pass_count + fixed_count}/{total} checks satisfied**

## Results by Document

### 01-prd.md ({pass}/{total} checks)
| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1.1 | Executive summary | PASS/FIXED/NEEDS_INPUT | {details} |
...

{Repeat for each document}

## Fixes Applied This Iteration
1. {Document}: {what was fixed}
...

## Items Requiring User Input
1. **Check {N.N}** ({document}): {what information is needed from the user}
...

## Iteration History
{Copy from state file progress log}
```

---

## Phase 5: UPDATE STATE & COMPLETION CHECK

### Update State File
Append to the Progress Log in `.claude/at-doc-validate.state.md`:

```markdown
### Iteration {N}
- Completed: {timestamp}
- Checks run: {80 + 8 if business/ + 8 if strategy/}
- Passed: {n}
- Failed: {n}
- Fixed this iteration: {n}
- Needs input: {n}
```

Update the `iteration` field in frontmatter to `{N + 1}`.

### Completion Check

**If ALL checks are PASS or NEEDS_INPUT (no remaining FAIL):**
1. Write final validation report
2. Clean up: delete state file
3. Tell the user the package is validated
4. Output: `<promise>DOC_COMPLETE</promise>`

**If FAIL checks remain but nothing was fixed this iteration (no progress):**
1. Write validation report showing stuck checks
2. Clean up: delete state file
3. Tell the user which checks are stuck and why
4. Output: `<promise>DOC_COMPLETE</promise>` (with NEEDS_INPUT items noted)

**If FAIL checks remain and fixes were made (progress was made):**
1. Write validation report
2. End your response normally — the stop hook will continue the loop
3. Do NOT output the completion promise

---

## Rules

1. **Read ALL documents before checking.** Don't validate a document in isolation — cross-references matter.
2. **Fix before reporting.** Don't just list failures — fix everything you can first, THEN report.
3. **Be conservative with NEEDS_INPUT.** If you can reasonably extrapolate from existing content, fix it yourself. Only mark NEEDS_INPUT when you genuinely lack information.
4. **Don't invent requirements.** When fixing, derive content from the existing brief and other documents. Don't add features or requirements that aren't implied by the existing package.
5. **Mermaid diagrams must be syntactically valid.** Test mental model of diagram syntax before writing. Use standard Mermaid syntax only.
6. **Preserve existing content.** When fixing, add to documents — don't rewrite sections that are already satisfactory.
7. **The stop hook handles looping.** You don't need to restart yourself. Just end your response and the hook will feed you back in.
8. **Maximum 5 iterations.** If you can't satisfy all checks in 5 passes, stop and report. The state file `max_iterations` enforces this.
