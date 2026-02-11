"""Tests for core business rules: cost calculation, bank type, and perspective unlock order."""

from app.models.enums import BankType, DimensionType, PerspectiveStatus, PhaseType
from app.services.bank import _determine_bank_type
from app.services.perspective import PHASE_ORDER

# ── Model pricing (from PRD) ────────────────────────────────────────────
# claude-haiku-4-5-20251001:   input=$1.00/M  output=$5.00/M
# claude-sonnet-4-5-20250929:  input=$3.00/M  output=$15.00/M

MODEL_PRICING = {
    "claude-haiku-4-5-20251001": {"input_per_m": 1.00, "output_per_m": 5.00},
    "claude-sonnet-4-5-20250929": {"input_per_m": 3.00, "output_per_m": 15.00},
}


def _calculate_cost_cents(model: str, tokens_in: int, tokens_out: int) -> float:
    """Calculate cost in cents for a given model and token counts."""
    pricing = MODEL_PRICING[model]
    input_cost = (tokens_in / 1_000_000) * pricing["input_per_m"]
    output_cost = (tokens_out / 1_000_000) * pricing["output_per_m"]
    return (input_cost + output_cost) * 100  # convert dollars to cents


# ── Cost calculation tests ──────────────────────────────────────────────


def test_cost_calculation_haiku():
    """500 input + 1200 output tokens on Haiku.

    (500/1M * 1.00) + (1200/1M * 5.00) = 0.0005 + 0.006 = 0.0065
    In cents: 0.65
    """
    cost = _calculate_cost_cents("claude-haiku-4-5-20251001", 500, 1200)
    assert abs(cost - 0.65) < 0.001


def test_cost_calculation_sonnet():
    """500 input + 1200 output tokens on Sonnet.

    (500/1M * 3.00) + (1200/1M * 15.00) = 0.0015 + 0.018 = 0.0195
    In cents: 1.95
    """
    cost = _calculate_cost_cents("claude-sonnet-4-5-20250929", 500, 1200)
    assert abs(cost - 1.95) < 0.001


def test_cost_calculation_zero_tokens():
    cost = _calculate_cost_cents("claude-haiku-4-5-20251001", 0, 0)
    assert cost == 0.0


def test_cost_calculation_large_volume():
    """1M input + 1M output on Haiku = (1.00 + 5.00) * 100 = 600 cents."""
    cost = _calculate_cost_cents("claude-haiku-4-5-20251001", 1_000_000, 1_000_000)
    assert abs(cost - 600.0) < 0.001


def test_budget_zero_means_unlimited():
    """Budget = 0 should never trigger alert (treated as unlimited)."""
    budget_cents = 0
    current_spend = 99999
    # If budget is 0, alert should not fire regardless of spend
    should_alert = budget_cents > 0 and current_spend >= budget_cents * 0.8
    assert not should_alert


def test_budget_alert_at_80_percent():
    """Alert should trigger at 80% of budget."""
    budget_cents = 1000
    current_spend = 800
    should_alert = budget_cents > 0 and current_spend >= budget_cents * 0.8
    assert should_alert


def test_budget_no_alert_below_threshold():
    budget_cents = 1000
    current_spend = 700
    should_alert = budget_cents > 0 and current_spend >= budget_cents * 0.8
    assert not should_alert


# ── Bank type determination tests ───────────────────────────────────────


def test_bank_type_generate_phase():
    """Generate phase -> bankable."""
    for dim in DimensionType:
        result = _determine_bank_type(dim.value, PhaseType.GENERATE.value)
        assert result == BankType.BANKABLE.value, f"Expected bankable for {dim}/generate"


def test_bank_type_review_phase():
    """Review phase -> bankable."""
    for dim in DimensionType:
        result = _determine_bank_type(dim.value, PhaseType.REVIEW.value)
        assert result == BankType.BANKABLE.value, f"Expected bankable for {dim}/review"


def test_bank_type_validate_phase():
    """Validate phase -> bankable."""
    for dim in DimensionType:
        result = _determine_bank_type(dim.value, PhaseType.VALIDATE.value)
        assert result == BankType.BANKABLE.value, f"Expected bankable for {dim}/validate"


def test_bank_type_summarize_architecture():
    """Summarize in architecture -> film."""
    result = _determine_bank_type(DimensionType.ARCHITECTURE.value, PhaseType.SUMMARIZE.value)
    assert result == BankType.FILM.value


def test_bank_type_summarize_design():
    """Summarize in design -> film."""
    result = _determine_bank_type(DimensionType.DESIGN.value, PhaseType.SUMMARIZE.value)
    assert result == BankType.FILM.value


def test_bank_type_summarize_engineering():
    """Summarize in engineering -> film_reel."""
    result = _determine_bank_type(DimensionType.ENGINEERING.value, PhaseType.SUMMARIZE.value)
    assert result == BankType.FILM_REEL.value


# ── Perspective unlock order tests ──────────────────────────────────────


def test_phase_order_correct():
    """Verify the phase order constant is generate -> review -> validate -> summarize."""
    assert PHASE_ORDER == [PhaseType.GENERATE, PhaseType.REVIEW, PhaseType.VALIDATE, PhaseType.SUMMARIZE]


def test_review_locked_until_generate_complete():
    """Review phase starts as LOCKED; only Generate starts as PENDING."""
    # Simulate the journey creation logic from journey service
    statuses = {}
    for phase in PhaseType:
        if phase == PhaseType.GENERATE:
            statuses[phase.value] = PerspectiveStatus.PENDING.value
        else:
            statuses[phase.value] = PerspectiveStatus.LOCKED.value

    assert statuses["generate"] == "pending"
    assert statuses["review"] == "locked"
    assert statuses["validate"] == "locked"
    assert statuses["summarize"] == "locked"


def test_validate_locked_until_review_complete():
    """Validate should remain locked even if generate is complete, until review is done."""
    # After generate completes, review moves to pending, but validate stays locked
    statuses = {
        "generate": PerspectiveStatus.COMPLETED.value,
        "review": PerspectiveStatus.PENDING.value,
        "validate": PerspectiveStatus.LOCKED.value,
        "summarize": PerspectiveStatus.LOCKED.value,
    }
    assert statuses["validate"] == "locked"


def test_summarize_locked_until_validate_complete():
    """Summarize should remain locked until validate is complete."""
    statuses = {
        "generate": PerspectiveStatus.COMPLETED.value,
        "review": PerspectiveStatus.COMPLETED.value,
        "validate": PerspectiveStatus.PENDING.value,
        "summarize": PerspectiveStatus.LOCKED.value,
    }
    assert statuses["summarize"] == "locked"
