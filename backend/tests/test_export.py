import json
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

from app.services.export import _build_export_data, _generate_docx, _generate_json, _generate_pdf


def _make_vdba_ns(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "journey_id": uuid.uuid4(),
        "organization_id": uuid.uuid4(),
        "title": "Test VDBA",
        "description": "A test VDBA export",
        "bank_instance_id": uuid.uuid4(),
        "published_at": datetime.now(UTC),
        "export_url": None,
        "export_format": "json",
        "version": 1,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_perspective_ns(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "journey_id": uuid.uuid4(),
        "dimension": "architecture",
        "phase": "generate",
        "status": "completed",
        "started_at": datetime.now(UTC),
        "completed_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_bank_instance_ns(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "type": "bankable",
        "synopsis": "Test synopsis for banking",
        "agent_assessments": {"lyra": {"summary": "Good", "confidence": 0.9}},
        "decision_audit": [{"challenge": "test", "resolution": "resolved"}],
        "documents_count": 2,
        "vibes_count": 1,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_build_export_data():
    """Export data should include VDBA info, perspectives, and bank instances."""
    vdba = _make_vdba_ns()
    perspectives = [
        _make_perspective_ns(dimension="architecture", phase="generate"),
        _make_perspective_ns(dimension="design", phase="review"),
    ]
    bank_instances = [_make_bank_instance_ns()]

    data = _build_export_data(vdba, perspectives, bank_instances)

    assert data["vdba"]["title"] == "Test VDBA"
    assert data["vdba"]["version"] == 1
    assert len(data["perspectives"]) == 2
    assert len(data["bank_instances"]) == 1
    assert data["bank_instances"][0]["synopsis"] == "Test synopsis for banking"


def test_generate_json():
    """JSON export should produce valid JSON bytes."""
    vdba = _make_vdba_ns()
    perspectives = [_make_perspective_ns()]
    bank_instances = [_make_bank_instance_ns()]

    data = _build_export_data(vdba, perspectives, bank_instances)
    file_bytes, content_type, extension = _generate_json(data)

    assert content_type == "application/json"
    assert extension == "json"
    parsed = json.loads(file_bytes.decode("utf-8"))
    assert parsed["vdba"]["title"] == "Test VDBA"
    assert len(parsed["perspectives"]) == 1
    assert len(parsed["bank_instances"]) == 1


def test_generate_json_empty_data():
    """JSON export should handle empty perspectives and bank instances."""
    vdba = _make_vdba_ns()
    data = _build_export_data(vdba, [], [])
    file_bytes, content_type, extension = _generate_json(data)

    parsed = json.loads(file_bytes.decode("utf-8"))
    assert parsed["perspectives"] == []
    assert parsed["bank_instances"] == []


def test_generate_pdf_fallback():
    """PDF export should produce output (either PDF or JSON fallback)."""
    vdba = _make_vdba_ns()
    perspectives = [_make_perspective_ns()]
    bank_instances = [_make_bank_instance_ns()]

    data = _build_export_data(vdba, perspectives, bank_instances)
    file_bytes, content_type, extension = _generate_pdf(data)

    # Should return either real PDF or JSON fallback
    assert len(file_bytes) > 0
    assert content_type in ("application/pdf", "application/json")
    assert extension in ("pdf", "json")

    if content_type == "application/json":
        # Verify JSON fallback is valid
        parsed = json.loads(file_bytes.decode("utf-8"))
        assert parsed["vdba"]["title"] == "Test VDBA"


def test_generate_docx_fallback():
    """DOCX export should produce output (either DOCX or JSON fallback)."""
    vdba = _make_vdba_ns()
    perspectives = [_make_perspective_ns()]
    bank_instances = [_make_bank_instance_ns()]

    data = _build_export_data(vdba, perspectives, bank_instances)
    file_bytes, content_type, extension = _generate_docx(data)

    assert len(file_bytes) > 0
    valid_types = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/json",
    )
    assert content_type in valid_types
    assert extension in ("docx", "json")

    if content_type == "application/json":
        parsed = json.loads(file_bytes.decode("utf-8"))
        assert parsed["vdba"]["title"] == "Test VDBA"


def test_build_export_data_perspective_dates():
    """Export data should correctly serialize perspective dates."""
    now = datetime.now(UTC)
    vdba = _make_vdba_ns()
    perspective = _make_perspective_ns(started_at=now, completed_at=now)
    data = _build_export_data(vdba, [perspective], [])

    assert data["perspectives"][0]["started_at"] == now.isoformat()
    assert data["perspectives"][0]["completed_at"] == now.isoformat()


def test_build_export_data_null_dates():
    """Export data should handle None dates gracefully."""
    vdba = _make_vdba_ns(published_at=None)
    perspective = _make_perspective_ns(started_at=None, completed_at=None)
    data = _build_export_data(vdba, [perspective], [])

    assert data["vdba"]["published_at"] is None
    assert data["perspectives"][0]["started_at"] is None
    assert data["perspectives"][0]["completed_at"] is None
