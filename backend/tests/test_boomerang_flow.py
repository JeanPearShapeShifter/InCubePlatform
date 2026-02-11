"""Tests for the enhanced boomerang service."""

from app.services.boomerang import AgentAssessment, BoomerangResult, DecisionAuditEntry, _build_assessment


def test_build_assessment_short_content():
    assessment = _build_assessment("lyra", "Short response")
    assert isinstance(assessment, AgentAssessment)
    assert assessment.summary == "Short response"
    assert assessment.confidence > 0
    assert assessment.confidence <= 1.0


def test_build_assessment_long_content():
    content = "A very detailed analysis.\n" * 100
    assessment = _build_assessment("dex", content)
    assert assessment.confidence == 1.0
    assert len(assessment.summary) <= 300


def test_build_assessment_with_bullet_points():
    content = (
        "Overview of the analysis\n"
        "- First key finding about architecture\n"
        "- Second key finding about scalability\n"
        "- Third finding about performance metrics\n"
        "Some concluding thoughts"
    )
    assessment = _build_assessment("rex", content)
    assert len(assessment.key_findings) >= 2
    assert any("architecture" in f for f in assessment.key_findings)


def test_build_assessment_numbered_list():
    content = (
        "Summary paragraph\n"
        "1. First important point here\n"
        "2. Second important point here\n"
        "3. Third important point here\n"
    )
    assessment = _build_assessment("vela", content)
    assert len(assessment.key_findings) >= 2


def test_build_assessment_empty_content():
    assessment = _build_assessment("lyra", "")
    assert assessment.summary == "No output"
    assert assessment.confidence == 0.3


def test_build_assessment_no_bullets_uses_lines():
    content = (
        "Main overview of the topic\n"
        "Additional context and details about the analysis\n"
        "More supporting information follows here\n"
        "Final thoughts and recommendations"
    )
    assessment = _build_assessment("mira", content)
    assert len(assessment.key_findings) >= 1


def test_boomerang_result_structure():
    result = BoomerangResult(
        agent_assessments={
            "lyra": {"summary": "Goal analysis", "confidence": 0.8, "key_findings": ["finding 1"]},
        },
        decision_audit=[
            {"challenge": "test challenge", "resolution": "resolved", "evidence": "evidence", "agents": ["lyra"]},
        ],
        agents_completed=["lyra"],
    )
    assert "lyra" in result.agent_assessments
    assert len(result.decision_audit) == 1
    assert result.agents_completed == ["lyra"]


def test_decision_audit_entry_dataclass():
    entry = DecisionAuditEntry(
        challenge="No ROI evidence",
        resolution="resolved",
        evidence="Quantitative analysis provided",
        agents=["vela", "lyra"],
        timestamp="2026-01-01T00:00:00",
    )
    assert entry.challenge == "No ROI evidence"
    assert entry.resolution == "resolved"
    assert len(entry.agents) == 2
