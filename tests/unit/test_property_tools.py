from app.property_tools import (
    book_viewing_mock,
    book_viewing_tool,
    estimate_upfront_costs,
)


def test_estimate_upfront_costs_benchmark():
    """Verify default market benchmark calculation when rent is not specified."""
    result = estimate_upfront_costs()
    assert result["status"] == "success"
    assert result["is_benchmark"] is True
    assert result["monthly_rent_yen"] == 150000
    assert result["rent_multiplier"] >= 4.0
    assert "breakdown" in result
    assert result["breakdown"]["deposit_yen"] == 150000
    assert result["breakdown"]["agency_commission_yen"] == 165000


def test_estimate_upfront_costs_exact_with_pet():
    """Verify exact property cost calculation with pet deposit addition."""
    result = estimate_upfront_costs(
        monthly_rent_yen=200000,
        management_fee_yen=15000,
        has_pet=True,
    )
    assert result["status"] == "success"
    assert result["is_benchmark"] is False
    assert result["monthly_rent_yen"] == 200000
    # Pet adds +1 month deposit -> deposit = 2 months = 400,000 yen
    assert result["breakdown"]["deposit_yen"] == 400000
    assert len(result["cost_saving_tips"]) >= 4


def test_estimate_upfront_costs_invalid_input_guided_recovery():
    """Verify guided error handling when invalid negative rent is supplied."""
    result = estimate_upfront_costs(monthly_rent_yen=-50000)
    assert result["status"] == "error"
    assert result["error_code"] == "INVALID_RENT_AMOUNT"
    assert "recovery_guidance" in result
    assert "positive" in result["recovery_guidance"].lower()


def test_book_viewing_mock_and_hitl_configuration():
    """Verify viewing booking mock logic and human approval gate."""
    res = book_viewing_mock(
        property_id="prop-bk-201",
        preferred_datetime="2026-08-30 14:00",
        applicant_name="Alex Smith",
        contact_phone="+1-555-0199",
    )
    assert res["status"] == "confirmed"
    assert "BK-" in res["booking_id"]
    assert res["applicant_name"] == "Alex Smith"
    assert "a2ui_card" in res

    # Test HITL FunctionTool configuration (require_confirmation)
    assert getattr(book_viewing_tool, "_require_confirmation", False) is True


def test_book_viewing_mock_invalid_input_guided_recovery():
    """Verify guided recovery advice when booking without applicant name or contact."""
    res = book_viewing_mock(
        property_id="prop-bk-201",
        preferred_datetime="2026-08-30 14:00",
        applicant_name="",
        contact_phone="",
    )
    assert res["status"] == "error"
    assert res["error_code"] == "MISSING_APPLICANT_NAME"
    assert "recovery_guidance" in res
