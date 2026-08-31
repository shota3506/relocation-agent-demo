import uuid
from typing import Any

from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field


class UpfrontCostItemizedBreakdown(BaseModel):
    deposit_yen: int = Field(description="Security deposit in JPY (敷金)")
    key_money_yen: int = Field(description="Key money in JPY (礼金)")
    agency_commission_yen: int = Field(
        description="Brokerage agency fee with 10% tax in JPY (仲介手数料)"
    )
    advance_first_month_rent_yen: int = Field(
        description="Advance first month rent + management fee in JPY (前家賃)"
    )
    guarantor_company_fee_yen: int = Field(
        description="Guarantor company guarantee fee in JPY (保証会社利用料)"
    )
    fire_insurance_yen: int = Field(
        description="Fire / renters insurance in JPY (火災保険料)"
    )
    key_exchange_yen: int = Field(description="Key replacement fee in JPY (鍵交換費用)")


class UpfrontCostResponse(BaseModel):
    status: str = Field(description="'success' or 'error'")
    mode: str = Field(
        description="'Exact Property Simulation' or 'General Market Benchmark'"
    )
    is_benchmark: bool = Field(
        description="True if calculated from market benchmark rather than specific listing"
    )
    monthly_rent_yen: int = Field(
        description="Monthly rent amount in JPY used for calculation"
    )
    management_fee_yen: int = Field(
        description="Monthly building maintenance fee in JPY"
    )
    total_upfront_yen: int = Field(
        description="Total upfront moving cost estimate in JPY"
    )
    rent_multiplier: float = Field(
        description="Total cost expressed as a multiple of monthly rent (e.g. 4.5x)"
    )
    breakdown: UpfrontCostItemizedBreakdown = Field(
        description="Itemized breakdown of all move-in expenses"
    )
    cost_saving_tips: list[str] = Field(
        description="Actionable strategies to negotiate and reduce upfront expenses"
    )
    a2ui_card: dict[str, Any] = Field(description="Interactive A2UI UI card payload")
    error_code: str | None = Field(
        default=None, description="Error code if calculation failed"
    )
    recovery_guidance: str | None = Field(
        default=None, description="Actionable recovery guidance for the LLM"
    )


def estimate_upfront_costs(
    monthly_rent_yen: int | None = None,
    management_fee_yen: int = 10000,
    has_pet: bool = False,
    deposit_months: float | None = None,
    key_money_months: float | None = None,
) -> dict[str, Any]:
    """Calculates an itemized upfront moving cost breakdown in JPY with strict JSON schema and guided error recovery.

    Supports two modes:
    - Exact mode: When specific property terms (rent/deposit/key money) are provided.
    - General benchmark mode: When rent is not yet specified, simulates typical market costs (~4.5x rent).

    Args:
        monthly_rent_yen: Monthly rent in JPY (must be positive if specified). Defaults to 150,000 JPY benchmark.
        management_fee_yen: Monthly building management fee in JPY (default: 10,000 JPY).
        has_pet: Whether the tenant will keep pets (adds +1 month deposit).
        deposit_months: Security deposit in months of rent (default: 1.0 month, or 2.0 with pets).
        key_money_months: Key money (reikin) in months of rent (default: 1.0 month).

    Returns:
        Structured Pydantic-validated dict breakdown of all move-in expenses or guided recovery instructions on error.
    """
    # Guided Error Recovery: Validate positive inputs
    if monthly_rent_yen is not None and monthly_rent_yen <= 0:
        return {
            "status": "error",
            "error_code": "INVALID_RENT_AMOUNT",
            "message": f"Monthly rent must be a positive integer, received: {monthly_rent_yen}",
            "recovery_guidance": (
                "The monthly rent amount provided is invalid. Please ask the user for a valid positive monthly budget "
                "(e.g. 150,000 JPY), or call `estimate_upfront_costs()` without `monthly_rent_yen` to calculate using standard market benchmark."
            ),
        }

    if management_fee_yen < 0:
        return {
            "status": "error",
            "error_code": "INVALID_MANAGEMENT_FEE",
            "message": f"Management fee cannot be negative, received: {management_fee_yen}",
            "recovery_guidance": "Please provide a non-negative management fee (typically between 5,000 and 15,000 JPY), or omit it to use the default 10,000 JPY.",
        }

    is_benchmark = monthly_rent_yen is None
    rent = monthly_rent_yen if monthly_rent_yen is not None else 150000

    dep_months = (
        deposit_months if deposit_months is not None else (2.0 if has_pet else 1.0)
    )
    key_months = key_money_months if key_money_months is not None else 1.0

    deposit_yen = int(rent * dep_months)
    key_money_yen = int(rent * key_months)
    agency_fee_yen = int(rent * 1.10)
    advance_rent_yen = rent + management_fee_yen
    guarantor_company_yen = int((rent + management_fee_yen) * 0.50)
    fire_insurance_yen = 20000
    key_exchange_yen = 22000

    total_upfront_yen = (
        deposit_yen
        + key_money_yen
        + agency_fee_yen
        + advance_rent_yen
        + guarantor_company_yen
        + fire_insurance_yen
        + key_exchange_yen
    )

    rent_multiplier = round(total_upfront_yen / rent, 1)

    tips = [
        "Key Money Negotiation: Properties vacant for >1 month often accept 0 key money (saves ~1.0x rent).",
        "Agency Commission: Inquire about commission discounts or 0.5-month broker fees.",
        "Free Rent: Inquire about a 0.5 to 1.0 month free rent promotion to offset advance rent.",
        "Guarantor Guarantee Renewal: Check if the annual renewal fee is fixed or percentage-based.",
    ]
    if has_pet:
        tips.append(
            "Pet Deposit Note: Pet-friendly properties often require 1 month non-refundable deduction fee."
        )

    response_data = UpfrontCostResponse(
        status="success",
        mode="General Market Benchmark"
        if is_benchmark
        else "Exact Property Simulation",
        is_benchmark=is_benchmark,
        monthly_rent_yen=rent,
        management_fee_yen=management_fee_yen,
        total_upfront_yen=total_upfront_yen,
        rent_multiplier=rent_multiplier,
        breakdown=UpfrontCostItemizedBreakdown(
            deposit_yen=deposit_yen,
            key_money_yen=key_money_yen,
            agency_commission_yen=agency_fee_yen,
            advance_first_month_rent_yen=advance_rent_yen,
            guarantor_company_fee_yen=guarantor_company_yen,
            fire_insurance_yen=fire_insurance_yen,
            key_exchange_yen=key_exchange_yen,
        ),
        cost_saving_tips=tips,
        a2ui_card={
            "type": "UpfrontCostCard",
            "title": f"Upfront Moving Cost Estimate (¥{total_upfront_yen:,})",
            "multiplier_text": f"~{rent_multiplier}x monthly rent",
            "total": total_upfront_yen,
        },
    )
    return response_data.model_dump()


class BookingInstructions(BaseModel):
    meeting_place: str = Field(description="Where to meet the agent or broker")
    checklist: list[str] = Field(description="Items and preparations for the viewing")
    cancellation_policy: str = Field(
        description="Notice period and rules for cancellation"
    )


class BookingViewingResponse(BaseModel):
    status: str = Field(description="'confirmed' or 'error'")
    booking_id: str | None = Field(
        default=None, description="Unique booking identifier"
    )
    property_id: str = Field(description="Target property ID or URL")
    preferred_datetime: str = Field(description="Scheduled viewing date and time")
    applicant_name: str = Field(description="Full name of the viewing applicant")
    contact_phone: str = Field(description="Applicant contact number/email")
    instructions: BookingInstructions | None = Field(
        default=None, description="On-site meeting guidelines"
    )
    a2ui_card: dict[str, Any] | None = Field(
        default=None, description="A2UI confirmation card payload"
    )
    message: str = Field(description="Human-readable status or confirmation message")
    error_code: str | None = Field(
        default=None, description="Error code if booking failed"
    )
    recovery_guidance: str | None = Field(
        default=None, description="Actionable recovery guidance for the LLM"
    )


def book_viewing_mock(
    property_id: str,
    preferred_datetime: str,
    applicant_name: str,
    contact_phone: str,
) -> dict[str, Any]:
    """Books an on-site property viewing appointment with strict validation and guided error recovery.

    ★ CRITICAL: This is a state-mutating action requiring explicit human-in-the-loop approval.

    Args:
        property_id: Unique listing identifier or URL.
        preferred_datetime: Preferred date and time (e.g. '2026-08-30 14:00').
        applicant_name: Full name of the applicant viewing the property.
        contact_phone: Contact phone or email for the real estate agent.

    Returns:
        Structured booking confirmation or actionable recovery guidance if required parameters are missing.
    """
    # Guided Error Recovery: Validate required fields
    if not property_id or not property_id.strip():
        return {
            "status": "error",
            "error_code": "MISSING_PROPERTY_ID",
            "message": "Property ID or URL is required to schedule a viewing.",
            "recovery_guidance": "Please specify the property ID or listing URL that the user wishes to inspect before calling this tool.",
        }

    if not applicant_name or not applicant_name.strip():
        return {
            "status": "error",
            "error_code": "MISSING_APPLICANT_NAME",
            "message": "Applicant full name is required for viewing reservation.",
            "recovery_guidance": "Ask the user to provide their name for the viewing reservation before booking.",
        }

    if not contact_phone or not contact_phone.strip():
        return {
            "status": "error",
            "error_code": "MISSING_CONTACT_INFO",
            "message": "Contact phone or email is required for viewing reservation.",
            "recovery_guidance": "Ask the user to provide their contact phone number or email address to finalize the viewing reservation.",
        }

    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"

    resp = BookingViewingResponse(
        status="confirmed",
        booking_id=booking_id,
        property_id=property_id.strip(),
        preferred_datetime=preferred_datetime.strip(),
        applicant_name=applicant_name.strip(),
        contact_phone=contact_phone.strip(),
        instructions=BookingInstructions(
            meeting_place="Directly at the property entrance or agency branch office.",
            checklist=[
                "Bring a valid photo ID.",
                "Bring a measuring tape for room and furniture dimensions.",
                "Take photos/notes of natural lighting and noise levels.",
            ],
            cancellation_policy="Free cancellation up to 2 hours before the scheduled appointment.",
        ),
        a2ui_card={
            "type": "BookingConfirmationCard",
            "title": "Viewing Reserved",
            "booking_id": booking_id,
            "datetime": preferred_datetime,
            "applicant": applicant_name,
        },
        message=f"Viewing appointment successfully reserved for {applicant_name} on {preferred_datetime}.",
    )
    return resp.model_dump()


book_viewing_tool = FunctionTool(
    func=book_viewing_mock,
    require_confirmation=True,
)
