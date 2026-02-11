# AT Doc: Generate Strategy Documentation

You are a business strategy analyst. Your job is to read a complete technical documentation package and produce strategic business analysis documents — market analysis, competitive positioning, business model design, go-to-market planning, and MVP validation — for founders, investors, and product managers.

**Input:** `$ARGUMENTS` is the path to a documentation package directory (e.g., `.claude/docs/packages/{project}/{slug}/`).

---

## Phase 0: LOAD PACKAGE

1. Read `$ARGUMENTS` — the package directory path
2. If `$ARGUMENTS` is empty, ask the user for the path. Wait.
3. Read `README.md` from the package directory to get project info
4. Read ALL 10 technical documents from the package directory:
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
5. Also read `review-report.md` and `validation-report.md` if they exist (for additional context)
6. If any of the 10 core documents are missing, warn the user but continue with what's available
7. Create the output directory: `{package-path}/strategy/`
8. Tell the user: _"Loaded **{project}** documentation package ({N}/10 documents). Generating strategy documentation..."_

---

## Phase 1: GENERATE STRATEGY DOCUMENTS

Generate all 5 strategy documents below, writing each to `{package-path}/strategy/`. Read the technical documents thoroughly and produce strategic analysis following the **Writing Rules** at the bottom of this prompt.

### Document S1: Market Analysis

**File:** `market-analysis.md`
**Sources:** `01-prd.md`, `02-system-architecture.md`, `09-deployment-architecture.md`

Combines macro environment (PESTLE) and competitive dynamics (Porter's Five Forces) into one document. No framework tutorials — just the analysis.

```markdown
---
document: "market-analysis"
project: "{project}"
generated: "{YYYY-MM-DD}"
source: "strategy-docs"
---

# Market Analysis: {Title}

## Macro Environment (PESTLE)

| Factor | What's Happening | Impact on This Venture | Implication | Timeframe |
|--------|-----------------|----------------------|-------------|-----------|
| **Political** | {Specific regulatory or policy trends affecting this market/region} | {How it specifically affects this product} | {What the team should do about it} | {Near-term / Medium-term / Long-term} |
| **Economic** | {Economic conditions, funding climate, buyer budgets} | {Impact on pricing, demand, or growth} | {Action to take} | {Timeframe} |
| **Social** | {Demographic shifts, behavioral trends, cultural factors} | {Impact on adoption or user needs} | {Action to take} | {Timeframe} |
| **Technological** | {Tech trends, platform shifts, emerging capabilities} | {Impact on build vs. buy, competitive moat} | {Action to take} | {Timeframe} |
| **Legal** | {Data privacy laws, industry regulations, compliance requirements} | {Impact on product design or operations} | {Action to take} | {Timeframe} |
| **Environmental** | {Sustainability expectations, carbon footprint considerations} | {Impact on infrastructure or positioning} | {Action to take} | {Timeframe} |

## Competitive Dynamics (Porter's Five Forces)

| Force | Assessment | Key Players | Defensive Levers |
|-------|-----------|-------------|-----------------|
| **Industry Rivalry** | {Low / Moderate / High — with specific evidence} | {Named competitors in this space} | {What this venture can do to strengthen its position} |
| **Threat of New Entrants** | {Assessment with evidence — barriers to entry, capital requirements} | {Who could enter this market and why} | {Defensive actions} |
| **Threat of Substitutes** | {Assessment — alternative solutions, manual processes, status quo} | {Named substitutes or alternative approaches} | {How to make switching costly} |
| **Supplier Power** | {Assessment — dependency on cloud providers, API providers, content} | {Named suppliers this venture depends on} | {How to reduce dependency} |
| **Buyer Power** | {Assessment — price sensitivity, switching costs, alternatives} | {Target buyer segments and their leverage} | {How to increase switching costs} |

## Strategic Implications

{3-5 bullet synthesis of what the market analysis means for product and business decisions. Each bullet: one specific, actionable insight — not generic advice.}

- {Implication 1}
- {Implication 2}
- {Implication 3}
```

---

### Document S2: Competitive Landscape

**File:** `competitive-landscape.md`
**Sources:** `01-prd.md`, `02-system-architecture.md`, `07-ux-specification.md`

Venture SWOT, competitor profiles, and positioning statement. Extract competitors from the PRD's "Current Solutions & Gaps" section. If the PRD doesn't name competitors, identify the 2-3 most obvious based on the product category and mark them "Inferred — not in PRD."

```markdown
---
document: "competitive-landscape"
project: "{project}"
generated: "{YYYY-MM-DD}"
source: "strategy-docs"
---

# Competitive Landscape: {Title}

## Venture SWOT

### Internal

| | Factor | Evidence |
|---|--------|----------|
| **S1** | {Strength} | {Why this is true — cite specific capability from PRD or architecture} |
| **S2** | {Strength} | {Evidence} |
| **S3** | {Strength} | {Evidence} |
| **S4** | {Strength} | {Evidence} |
| **S5** | {Strength} | {Evidence} |
| **W1** | {Weakness} | {Why this is a concern} |
| **W2** | {Weakness} | {Evidence} |
| **W3** | {Weakness} | {Evidence} |
| **W4** | {Weakness} | {Evidence} |
| **W5** | {Weakness} | {Evidence} |

### External

| | Factor | Evidence |
|---|--------|----------|
| **O1** | {Opportunity} | {Why this exists — market gap, trend, timing} |
| **O2** | {Opportunity} | {Evidence} |
| **O3** | {Opportunity} | {Evidence} |
| **O4** | {Opportunity} | {Evidence} |
| **O5** | {Opportunity} | {Evidence} |
| **T1** | {Threat} | {Why this is dangerous} |
| **T2** | {Threat} | {Evidence} |
| **T3** | {Threat} | {Evidence} |
| **T4** | {Threat} | {Evidence} |
| **T5** | {Threat} | {Evidence} |

### Strategic Moves (SO/WT Cross-Analysis)

{3-5 actions that exploit strengths against opportunities or defend weaknesses against threats. Each move references specific S/W/O/T items by label.}

1. **{Move name}** — {Description referencing specific items, e.g., "Leverage S1 (technical moat) against O2 (market gap) by..."}
2. **{Move name}** — {Description}
3. **{Move name}** — {Description}

## Competitor Profiles

{For each identified competitor — extract from PRD's "current solutions" or "gaps" section. If none named, infer the 2-3 most obvious and mark "Inferred — not in PRD."}

### {Competitor Name} {if inferred: "(Inferred — not in PRD)"}

- **Who They Are:** {1-2 sentence description — what they do, who they serve}
- **Their Strengths:** {What they do well — be specific}
- **Their Weaknesses:** {Where they fall short — these are our opportunities}
- **Our Differentiation:** {How this venture is specifically better for the target market}

{Repeat for each competitor}

## Positioning Statement

For **{target users}** who **{pain point}**, **{product name}** is a **{category}** that **{key differentiator}**. Unlike **{primary competitor}**, we **{unique advantage}**.
```

---

### Document S3: Business Model

**File:** `business-model.md`
**Sources:** `01-prd.md`, `03-data-model.md`, `04-api-specification.md`, `09-deployment-architecture.md`

Full Business Model Canvas (all 9 blocks) plus unit economics. Where the PRD doesn't specify pricing or financial data, state assumptions explicitly and label them.

```markdown
---
document: "business-model"
project: "{project}"
generated: "{YYYY-MM-DD}"
source: "strategy-docs"
---

# Business Model: {Title}

## Business Model Canvas

### 1. Value Proposition

{What value do we deliver? Which customer problems do we solve? What bundles of products and services do we offer? Derived from PRD problem statement and core features.}

### 2. Customer Segments

{Who are we creating value for? Who are our most important customers? Distinguish between users and buyers if different.}

| Segment | Description | Pain Points | Willingness to Pay |
|---------|-------------|-------------|-------------------|
| {Segment} | {Who they are} | {What they struggle with} | {How much, how — derived from PRD or marked "Assumption"} |

### 3. Channels

| Phase | Channel | Purpose |
|-------|---------|---------|
| Awareness | {How customers discover us} | {Acquisition} |
| Evaluation | {How customers evaluate us} | {Conversion} |
| Purchase | {How customers buy} | {Revenue} |
| Delivery | {How we deliver value} | {Retention} |
| Support | {How we provide post-purchase support} | {Satisfaction} |

### 4. Customer Relationships

{Self-service, personal assistance, automated, community? Derived from UX and feature set.}

- **Primary model:** {e.g., "Self-service with automated onboarding"}
- **Retention mechanism:** {e.g., "Habit-forming daily use + data lock-in"}
- **Upsell path:** {e.g., "Free → Pro when team size exceeds 5"}

### 5. Revenue Streams

| Stream | Model | Price Point | Basis |
|--------|-------|-------------|-------|
| {Stream} | {Subscription / One-time / Freemium / Transaction fee} | {Amount or "Assumption: $X/mo"} | {From PRD or "Assumption — validate before launch"} |

### 6. Key Resources

| Resource | Type | Why Critical |
|----------|------|-------------|
| {Resource} | {Team / Infrastructure / Content / IP / Data} | {Why the business can't function without it} |

### 7. Key Activities

| Activity | Description | Frequency |
|----------|-------------|-----------|
| {Activity} | {What must be done well} | {Daily / Weekly / Ongoing} |

### 8. Key Partnerships

| Partner Type | Examples | What They Provide | Dependency Level |
|-------------|----------|-------------------|-----------------|
| {Type} | {Named partners or categories} | {What we get from them} | {Critical / Important / Nice-to-have} |

### 9. Cost Structure

| Cost Category | Type | Estimated Range | Basis |
|--------------|------|-----------------|-------|
| {Category} | {Fixed / Variable} | {Amount or "To be estimated"} | {From deployment architecture or "Assumption"} |

## Unit Economics

| Metric | Value | Basis |
|--------|-------|-------|
| **ARPU** (Average Revenue Per User) | {Derived from pricing above or "Assumption: $X/mo"} | {Source} |
| **CAC** (Customer Acquisition Cost) | {Estimated from channel strategy or "Target: $X"} | {Source} |
| **LTV** (Lifetime Value) | {ARPU × estimated retention months or "Assumption: $X"} | {Calculation shown} |
| **LTV:CAC Ratio** | {Ratio or "Target: 3:1+"} | {Assessment: healthy / needs improvement / to be validated} |
| **Breakeven** | {Users/subscribers needed to cover fixed costs or "To be calculated"} | {Calculation basis} |
| **Gross Margin** | {Revenue minus variable costs per user or "Target: X%"} | {Source} |

{Where data is unavailable, every estimate is explicitly labeled "Assumption — validate before launch" or "Target — track post-launch."}
```

---

### Document S4: Go-To-Market Plan

**File:** `go-to-market.md`
**Sources:** `01-prd.md`, `05-user-flows.md`, `07-ux-specification.md`

Phased launch strategy, channel strategy, marketing, and retention. Derived from PRD target users, feature priorities, and success metrics.

```markdown
---
document: "go-to-market"
project: "{project}"
generated: "{YYYY-MM-DD}"
source: "strategy-docs"
---

# Go-To-Market Plan: {Title}

## Launch Strategy

### Phase 1: MVP Launch

- **Target Segment:** {Most urgent persona from PRD — who feels the pain most acutely}
- **Launch Channel:** {Primary channel to reach them — where they already are}
- **Core Value Proposition:** {The single sentence that makes them try it}
- **Initial Traction KPIs:**
  | Metric | Target | Timeframe |
  |--------|--------|-----------|
  | {KPI} | {Specific number — or "Target:" prefix} | {e.g., "First 90 days"} |

### Phase 2: Growth

- **Expansion Strategy:** {How to move beyond the initial segment — new personas, geographies, or use cases}
- **New Channels:** {Additional acquisition channels to add}
- **Feature Additions:** {Features from PRD Phase 2 / P1 priorities that unlock growth}
- **Growth KPIs:**
  | Metric | Target | Timeframe |
  |--------|--------|-----------|
  | {KPI} | {Target} | {Timeframe} |

### Phase 3: Scale

- **Market Expansion:** {New markets, verticals, or geographies}
- **Partnership Plays:** {Strategic partnerships that accelerate growth}
- **Platform Potential:** {If applicable — how this becomes a platform others build on}

## Channel Strategy

### Owned Channels

| Channel | Objective | Tactics | Success Metric |
|---------|-----------|---------|---------------|
| {e.g., Website/blog} | {e.g., Awareness + SEO} | {2-3 specific actions} | {How to measure} |
| {e.g., Email list} | {e.g., Nurture + conversion} | {Specific tactics} | {Metric} |
| {e.g., Product itself} | {e.g., Viral/referral loops} | {Specific tactics} | {Metric} |

### Earned Channels

| Channel | Objective | Tactics | Success Metric |
|---------|-----------|---------|---------------|
| {e.g., Industry press} | {e.g., Credibility} | {Specific tactics} | {Metric} |
| {e.g., Community/forums} | {e.g., Word of mouth} | {Specific tactics} | {Metric} |

### Paid Channels

| Channel | Objective | Tactics | Success Metric |
|---------|-----------|---------|---------------|
| {e.g., Search ads} | {e.g., Intent capture} | {Specific tactics} | {Metric} |
| {e.g., Social ads} | {e.g., Awareness} | {Specific tactics} | {Metric} |

## Marketing Strategy

### Core Message

{The single sentence that captures the value proposition — what goes on the homepage hero.}

### Target Audience Messaging

| Audience | Their Pain | Our Message | Proof Point |
|----------|-----------|-------------|-------------|
| {Persona from PRD} | {Their specific frustration} | {Message that speaks to their pain} | {Evidence from PRD success metrics, benchmarks, or "To be validated"} |

### Calls to Action

| Funnel Stage | CTA | Where It Appears |
|-------------|-----|-----------------|
| Awareness | {e.g., "See how it works"} | {e.g., Landing page, ads} |
| Consideration | {e.g., "Start free trial"} | {e.g., Pricing page, product page} |
| Decision | {e.g., "Upgrade to Pro"} | {e.g., In-app, email} |

## Retention Strategy

### Engagement Hooks

{What keeps users coming back — derived from core user flows and feature design.}

- {Hook 1 — e.g., "Daily digest email with actionable insights"}
- {Hook 2}
- {Hook 3}

### Churn Signals

| Signal | Detection Method | Intervention |
|--------|-----------------|-------------|
| {e.g., "No login for 7 days"} | {How we detect it} | {What we do — e.g., "Trigger re-engagement email"} |
| {Signal} | {Detection} | {Intervention} |

### Retention Targets

| Metric | Target | Basis |
|--------|--------|-------|
| Day-30 retention | {Target: X% or "Industry benchmark: X%"} | {Source} |
| Monthly churn rate | {Target: <X%} | {Basis} |
| NPS | {Target: X+} | {Basis} |
```

---

### Document S5: MVP Validation Plan

**File:** `mvp-validation.md`
**Sources:** `01-prd.md`, `08-test-strategy.md`

Testable assumptions with pass/fail criteria, pilot plan, and risk register. Derived from PRD features, success metrics, and constraints.

```markdown
---
document: "mvp-validation"
project: "{project}"
generated: "{YYYY-MM-DD}"
source: "strategy-docs"
---

# MVP Validation Plan: {Title}

## MVP Scope

### Included Features

{From PRD Phase 1 / P0 features — list each with a one-line description of what it does.}

| Feature | Description | Why It's MVP |
|---------|-------------|-------------|
| {Feature} | {One-line description} | {Why this can't be deferred — what breaks without it} |

### Excluded Features (Deferred)

| Feature | Deferred To | Reasoning |
|---------|------------|-----------|
| {Feature} | {Phase 2 / Phase 3 / Backlog} | {Why it can wait — what still works without it} |

### MVP Success Criteria

{What "works" means in measurable terms — not "users like it" but specific thresholds.}

| Criterion | Metric | Threshold |
|-----------|--------|-----------|
| {e.g., "Users complete core flow"} | {e.g., "Task completion rate"} | {e.g., "Target: >80%"} |

## Testable Assumptions

{5-8 assumptions that must be validated. Each one is a belief about users, market, or product that could be wrong.}

| # | Assumption | Test | Pass Criteria | Fail Action | Priority |
|---|-----------|------|---------------|-------------|----------|
| A1 | {What we believe to be true — e.g., "Teachers will use this daily during term time"} | {How we'll validate — e.g., "Track DAU/MAU ratio during pilot"} | {Specific threshold — e.g., "DAU/MAU > 0.4 after 30 days"} | {What we do if wrong — e.g., "Pivot to weekly digest model"} | {Must-validate-before-launch / Validate-during-pilot / Nice-to-know} |
| A2 | {Assumption} | {Test} | {Pass criteria} | {Fail action} | {Priority} |
| A3 | {Assumption} | {Test} | {Pass criteria} | {Fail action} | {Priority} |
| A4 | {Assumption} | {Test} | {Pass criteria} | {Fail action} | {Priority} |
| A5 | {Assumption} | {Test} | {Pass criteria} | {Fail action} | {Priority} |

## Pilot Plan

### Pilot Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Duration** | {Recommended length — e.g., "8 weeks"} | {Why this duration — enough to see patterns, short enough to iterate} |
| **Cohort Size** | {Target participants — e.g., "50-100 users"} | {Why this size — statistical significance vs. recruitment feasibility} |
| **Cohort Composition** | {Mix of user types — e.g., "60% teachers, 40% administrators"} | {Why this mix — reflects target market proportions} |
| **Geography** | {Where the pilot runs — e.g., "3 schools in Gauteng, South Africa"} | {Why here — access, representativeness, logistics} |

### Pilot Metrics

| Metric | Frequency | Target | Red Flag |
|--------|-----------|--------|----------|
| {e.g., "Active users"} | {Weekly} | {Target: X} | {Below Y triggers review} |
| {e.g., "Feature adoption"} | {Weekly} | {Target: X% use core feature} | {Below Y%} |
| {e.g., "NPS score"} | {End of pilot} | {Target: X+} | {Below Y} |
| {e.g., "Support tickets"} | {Weekly} | {Target: <X per user} | {Above Y} |

### Decision Points

| Week | Decision | Go Criteria | No-Go Criteria | Pivot Option |
|------|----------|-------------|----------------|-------------|
| {e.g., "Week 2"} | {e.g., "Continue pilot?"} | {e.g., ">30 active users"} | {e.g., "<10 active users"} | {e.g., "Recruit more aggressively or narrow scope"} |
| {e.g., "Week 6"} | {e.g., "Proceed to launch?"} | {e.g., "All must-validate assumptions pass"} | {e.g., "2+ must-validate assumptions fail"} | {e.g., "Extended pilot with revised features"} |
| {e.g., "Week 8"} | {e.g., "Scale decision"} | {e.g., "Retention >60%, NPS >30"} | {e.g., "Retention <40%"} | {e.g., "Iterate on retention before scaling"} |

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|------|-----------|--------|------------|-------|
| R1 | {What could go wrong — e.g., "Low adoption due to change resistance"} | {Low / Medium / High} | {Low / Medium / High} | {Specific action — e.g., "Champion program: train 3 power users per school"} | {Role responsible — e.g., "Product Manager"} |
| R2 | {Risk} | {Likelihood} | {Impact} | {Mitigation} | {Owner} |
| R3 | {Risk} | {Likelihood} | {Impact} | {Mitigation} | {Owner} |
| R4 | {Risk} | {Likelihood} | {Impact} | {Mitigation} | {Owner} |
| R5 | {Risk} | {Likelihood} | {Impact} | {Mitigation} | {Owner} |
```

---

## Phase 2: GENERATE STRATEGY README

Write `{package-path}/strategy/README.md`:

```markdown
# Strategy Documentation: {Title}

**Project:** {project}
**Generated:** {YYYY-MM-DD}
**Source Package:** {package-path}

## Purpose

These documents provide strategic business analysis derived from the technical documentation package — market positioning, competitive analysis, business model design, go-to-market planning, and MVP validation. They answer "should we build this?" and "how do we take it to market?" for founders, investors, and product managers.

## Documents

| # | Document | What It Answers |
|---|----------|-----------------|
| S1 | [Market Analysis](./market-analysis.md) | What external forces shape this market? How strong is the competitive pressure? |
| S2 | [Competitive Landscape](./competitive-landscape.md) | What are our strengths and weaknesses? Who are the competitors? How do we position? |
| S3 | [Business Model](./business-model.md) | How do we create and capture value? What are the unit economics? |
| S4 | [Go-To-Market Plan](./go-to-market.md) | How do we launch, grow, and retain users? |
| S5 | [MVP Validation Plan](./mvp-validation.md) | What assumptions must be true? How do we test them? What are the risks? |

## How to Use These Documents

- **Founders:** Start with [Market Analysis](./market-analysis.md) and [Competitive Landscape](./competitive-landscape.md) to validate the opportunity
- **Investors:** Read [Business Model](./business-model.md) for unit economics and [MVP Validation Plan](./mvp-validation.md) for risk assessment
- **Product Managers:** Focus on [Go-To-Market Plan](./go-to-market.md) and [MVP Validation Plan](./mvp-validation.md) for launch planning

## Assumptions

Strategy documents contain forward-looking projections. All estimates are explicitly labeled:
- **"Assumption:"** — derived from analysis, needs validation before launch
- **"Target:"** — aspirational metric to track post-launch
- **"Inferred — not in PRD"** — competitor or data point extrapolated from product category

No metric is stated as fact unless sourced directly from the PRD.
```

---

## Phase 3: REPORT TO USER

Tell the user:

1. Output location: `{package-path}/strategy/`
2. Summary of what was generated: 5 strategy documents + README index
3. List of documents with one-line descriptions:
   - **S1: Market Analysis** — PESTLE macro environment + Porter's Five Forces competitive dynamics
   - **S2: Competitive Landscape** — Venture SWOT + competitor profiles + positioning statement
   - **S3: Business Model** — Business Model Canvas (9 blocks) + unit economics
   - **S4: Go-To-Market Plan** — Phased launch strategy + channels + marketing + retention
   - **S5: MVP Validation Plan** — Testable assumptions + pilot plan + risk register
4. Per-document stats: approximate word count for each document
5. Key assumptions called out: list the most significant "Assumption:" labels across all documents
6. Next steps:
   - Review the market analysis first for accuracy of PESTLE factors and named competitors
   - Check the business model for realistic unit economics assumptions
   - Verify MVP validation assumptions match real business hypotheses
   - Run `/at-doc:validate {package-path}` to validate both technical and strategy documents
   - For non-technical stakeholder documents, run `/at-doc:business {package-path}`
7. Reminder: _"These documents are strategic analyses derived from the technical package. If the product scope changes, re-run `/at-doc:strategy {package-path}` to regenerate."_

---

## Writing Rules

These rules are mandatory for ALL strategy documents. Every sentence you write must follow them.

1. **Business terms are fine; engineering terms are not.** Use CAC, LTV, ARPU, NPS, churn, MRR, ARR, TAM, SAM, SOM freely. Do not use endpoint, payload, schema, middleware, container, JWT, OAuth, gRPC, SDK, ORM, REST, CRUD, CI/CD, WebSocket, SSE, Redis, PostgreSQL, microservice.

2. **Every claim needs evidence or an explicit assumption label.** Never state a metric as fact unless it's from the PRD. If projected, prefix with "Assumption:" or "Target:" before the number.

3. **No fabricated metrics.** If data doesn't exist, don't invent it. Say "To be validated during pilot" — never "85% of users recommend the product" when the product doesn't exist yet.

4. **Concrete over generic.** "Google Classroom lacks integrated payment management" not "Competitor platforms have limitations."

5. **Name competitors.** Extract from PRD's "Current Solutions & Gaps" section. If the PRD doesn't name competitors, identify the most obvious 2-3 based on the product category and state "Inferred — not in PRD."

6. **Tables over paragraphs** for structured data (PESTLE factors, SWOT items, unit economics, risk register, channel strategy).

7. **No framework tutorials.** Don't explain what PESTLE analysis is, what Porter's Five Forces are, what a SWOT matrix does, or how a Business Model Canvas works. Just do the analysis.

8. **No repetition.** Each fact appears once, in its most relevant document. Cross-reference between documents instead of copying content. E.g., "See [Competitive Landscape](./competitive-landscape.md) for detailed competitor profiles" instead of re-listing competitors.

9. **Use active voice.** "The venture targets mid-market SaaS buyers" — not "Mid-market SaaS buyers are targeted by the venture."

10. **No placeholder text.** Every field must have real, specific content derived from the technical documentation. If the technical docs don't specify something, write "Not specified in current documentation — recommend {specific suggestion}" — never use "{placeholder}", "TBD", or "TODO".

---

## Rules

1. **Read ALL 10 technical documents before writing anything.** You need full context to produce accurate analysis.
2. **Every PESTLE factor must be specific to this venture's market.** No generic observations that apply to any business. Each factor must reference the specific industry, geography, or user base from the PRD.
3. **The venture SWOT must have exactly 5 items per quadrant** (5 strengths, 5 weaknesses, 5 opportunities, 5 threats) — each with evidence.
4. **All 9 Business Model Canvas blocks must be populated.** Don't skip blocks. If a block requires financial data not in the PRD, label assumptions explicitly.
5. **Unit economics must show calculations.** Don't just state "LTV: $500" — show "ARPU ($25/mo) × estimated retention (20 months) = $500 (Assumption)."
6. **MVP validation needs at least 5 testable assumptions** with specific pass/fail thresholds. "Users like it" is not a testable assumption. "DAU/MAU > 0.4 after 30 days" is.
7. **Risk register needs at least 5 risks** with likelihood, impact, and specific mitigations — not "monitor the situation."
8. **Competitors must be named.** "Competitor A" and "Competitor B" are not acceptable. Use real company/product names.
9. **Cross-reference, don't repeat.** If a fact is in the market analysis, the competitive landscape should reference it, not restate it.
10. **The positioning statement must follow the template exactly:** "For [target users] who [pain point], [product] is a [category] that [key differentiator]. Unlike [primary competitor], we [unique advantage]."
