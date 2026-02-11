"""Tests for enhanced banking with assessments and audit."""

from app.schemas.bank import (
    AgentAssessment,
    BankCreate,
    BankInstanceDetail,
    DecisionAuditEntry,
)
from app.services.bank import _determine_bank_type

# --- Bank type determination ---


def test_determine_bank_type_generate():
    assert _determine_bank_type("architecture", "generate") == "bankable"


def test_determine_bank_type_review():
    assert _determine_bank_type("design", "review") == "bankable"


def test_determine_bank_type_validate():
    assert _determine_bank_type("engineering", "validate") == "bankable"


def test_determine_bank_type_summarize_architecture():
    assert _determine_bank_type("architecture", "summarize") == "film"


def test_determine_bank_type_summarize_design():
    assert _determine_bank_type("design", "summarize") == "film"


def test_determine_bank_type_summarize_engineering():
    assert _determine_bank_type("engineering", "summarize") == "film_reel"


# --- Schema validation ---


def test_agent_assessment_schema():
    assessment = AgentAssessment(
        summary="Goal analysis complete",
        confidence=0.85,
        key_findings=["Finding 1", "Finding 2"],
    )
    assert assessment.confidence == 0.85
    assert len(assessment.key_findings) == 2


def test_agent_assessment_confidence_bounds():
    """Test that confidence is bounded between 0 and 1."""
    assessment = AgentAssessment(summary="test", confidence=0.0)
    assert assessment.confidence == 0.0

    assessment = AgentAssessment(summary="test", confidence=1.0)
    assert assessment.confidence == 1.0

    import pytest

    with pytest.raises(Exception):
        AgentAssessment(summary="test", confidence=1.5)

    with pytest.raises(Exception):
        AgentAssessment(summary="test", confidence=-0.1)


def test_decision_audit_entry_schema():
    entry = DecisionAuditEntry(
        challenge="No evidence for claim",
        resolution="resolved",
        evidence="Agent provided quantitative analysis",
        agents=["lyra", "vela"],
        timestamp="2026-01-01T00:00:00Z",
    )
    assert entry.resolution == "resolved"
    assert "lyra" in entry.agents


def test_decision_audit_entry_defaults():
    entry = DecisionAuditEntry(challenge="test", resolution="action_required")
    assert entry.evidence == ""
    assert entry.agents == []
    assert entry.timestamp == ""


def test_bank_create_with_assessments():
    data = BankCreate(
        synopsis="Banking the architecture generate perspective",
        agent_assessments={
            "lyra": AgentAssessment(summary="Goal analysis", confidence=0.9, key_findings=["a", "b"]),
        },
        decision_audit=[
            DecisionAuditEntry(
                challenge="Weak evidence",
                resolution="resolved",
                evidence="Corrected",
                agents=["lyra"],
            ),
        ],
    )
    assert data.agent_assessments is not None
    assert "lyra" in data.agent_assessments
    assert len(data.decision_audit) == 1


def test_bank_create_minimal():
    data = BankCreate(synopsis="Simple bank")
    assert data.agent_assessments is None
    assert data.decision_audit is None


def test_bank_instance_detail_schema():
    detail = BankInstanceDetail(
        id="00000000-0000-0000-0000-000000000001",
        perspective_id="00000000-0000-0000-0000-000000000002",
        type="bankable",
        synopsis="Test synopsis",
        decision_audit=[
            DecisionAuditEntry(challenge="ch1", resolution="resolved", evidence="ev1", agents=["lyra"]),
        ],
        agent_assessments={
            "lyra": AgentAssessment(summary="summary", confidence=0.8, key_findings=["f1"]),
        },
        documents_count=3,
        vibes_count=1,
        emails_sent=0,
        feedback_received=0,
        created_at="2026-01-01T00:00:00Z",
    )
    assert detail.type == "bankable"
    assert detail.documents_count == 3
    assert "lyra" in detail.agent_assessments
    assert len(detail.decision_audit) == 1
