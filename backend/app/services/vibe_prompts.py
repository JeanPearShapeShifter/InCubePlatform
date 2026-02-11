"""Post-vibe analysis prompts for each of the 9 InCube agents."""

VIBE_ANALYSIS_SYSTEM = (
    "You are analyzing a voice session transcript from an InCube business transformation session. "
    "Extract structured insights from the transcript using your specialist perspective. "
    "Respond ONLY with a valid JSON object — no markdown, no explanation, no preamble."
)

VIBE_ANALYSIS_SCHEMA = """\
Respond with a JSON object containing exactly these keys:
{
    "insights": [{"text": "...", "source": "quote or context from transcript"}],
    "actionItems": [{"text": "...", "priority": "high|medium|low", "owner_agent": "agent_name"}],
    "contradictions": [{"text": "...", "between": "what vs what"}],
    "suggestedEdits": [{"document": "...", "suggestion": "..."}]
}

Each array may be empty if nothing relevant was found, but all four keys must be present."""

VIBE_ANALYSIS_PROMPTS: dict[str, str] = {
    "lyra": (
        "Analyze this voice session transcript as Lyra, the Goal Alignment specialist. Extract:\n"
        "1) Goal-relevant insights — statements that clarify, redefine, or conflict with stated objectives\n"
        "2) Strategic alignment observations — how the discussion maps to measurable outcomes\n"
        "3) Actionable items for goal tracking and success measurement\n"
        "4) Contradictions between stated goals and discussed actions\n"
        "5) Suggested edits to goal-related documents based on what was discussed\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
    "mira": (
        "Analyze this voice session transcript as Mira, the Stakeholder Analysis specialist. Extract:\n"
        "1) Stakeholder signals and concerns — explicit or implicit needs expressed\n"
        "2) Missing voices — stakeholders not represented or mentioned who should be\n"
        "3) Relationship dynamics — power structures, influence patterns, conflicts\n"
        "4) Contradictions in stakeholder expectations vs. project direction\n"
        "5) Suggested edits to stakeholder mapping or analysis documents\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
    "dex": (
        "Analyze this voice session transcript as Dex, the Requirements Engineering specialist. Extract:\n"
        "1) Implicit requirements mentioned — needs stated conversationally that should be formalized\n"
        "2) Testable criteria — statements that can be converted into acceptance criteria\n"
        "3) Gaps in requirement coverage — areas discussed but not yet documented\n"
        "4) Contradictions between stated requirements and discussed constraints\n"
        "5) Suggested edits to requirements or specification documents\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
    "rex": (
        "Analyze this voice session transcript as Rex, the Capability Assessment specialist. Extract:\n"
        "1) Capability gaps identified — skills, tools, or resources mentioned as lacking\n"
        "2) Resource constraints — budget, timeline, or personnel limitations discussed\n"
        "3) Technical feasibility signals — what is possible vs. aspirational\n"
        "4) Contradictions between ambitions and available capabilities\n"
        "5) Suggested edits to capability assessment or resource planning documents\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
    "vela": (
        "Analyze this voice session transcript as Vela, the Value and ROI Analysis specialist. Extract:\n"
        "1) Value indicators — statements about expected benefits, returns, or impact\n"
        "2) ROI signals — quantitative or qualitative measures of value discussed\n"
        "3) Cost-benefit observations — trade-offs mentioned or implied\n"
        "4) Contradictions between stated value propositions and discussed costs\n"
        "5) Suggested edits to business case or value analysis documents\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
    "koda": (
        "Analyze this voice session transcript as Koda, the Process Optimization specialist. Extract:\n"
        "1) Process observations — workflow steps, handoffs, or sequences described\n"
        "2) Workflow bottlenecks — delays, friction, or inefficiencies mentioned\n"
        "3) Optimization opportunities — improvements suggested or implied\n"
        "4) Contradictions between ideal process and actual practice discussed\n"
        "5) Suggested edits to process maps or workflow documents\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
    "halo": (
        "Analyze this voice session transcript as Halo, the Systems Integration specialist. Extract:\n"
        "1) Integration points — systems, tools, or data flows mentioned\n"
        "2) Cross-system dependencies — connections between components discussed\n"
        "3) Coherence gaps — where things don't fit together or conflict\n"
        "4) Contradictions between integration expectations and system realities\n"
        "5) Suggested edits to architecture or integration documents\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
    "nova": (
        "Analyze this voice session transcript as Nova, the Execution Planning specialist. Extract:\n"
        "1) Implementation hints — concrete steps, approaches, or techniques discussed\n"
        "2) Execution risks — threats to delivery mentioned or implied\n"
        "3) Timeline signals — deadlines, milestones, or sequencing discussed\n"
        "4) Contradictions between planned execution and discussed constraints\n"
        "5) Suggested edits to implementation plans or delivery roadmaps\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
    "axiom": (
        "Analyze this voice session transcript as Axiom, the Adversarial Reviewer. Extract:\n"
        "1) Contradictions in the discussion — conflicting statements or goals\n"
        "2) Unsubstantiated claims — assertions made without evidence or data\n"
        "3) Risks not addressed — threats or failure modes overlooked in the conversation\n"
        "4) Logical gaps — reasoning that doesn't hold up to scrutiny\n"
        "5) Suggested edits to strengthen documents against the identified weaknesses\n\n"
        + VIBE_ANALYSIS_SCHEMA
    ),
}


def build_vibe_analysis_prompt(agent_name: str, transcript: str, dimension: str | None = None,
                               phase: str | None = None) -> str:
    """Build the full user prompt for a post-vibe analysis by a specific agent."""
    agent_prompt = VIBE_ANALYSIS_PROMPTS[agent_name]

    parts = [agent_prompt, "\n## Voice Session Transcript\n", transcript]

    if dimension and phase:
        parts.insert(1, f"\n## Context\nDimension: {dimension.title()}, Phase: {phase.title()}\n")

    return "\n".join(parts)
