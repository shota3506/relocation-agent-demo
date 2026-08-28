import uuid
from typing import Any

from google.adk.tools import FunctionTool


def estimate_upfront_costs(
    monthly_rent_yen: int | None = None,
    management_fee_yen: int = 10000,
    has_pet: bool = False,
    deposit_months: float | None = None,
    key_money_months: float | None = None,
) -> dict[str, Any]:
    """Calculates an itemized upfront moving cost breakdown in JPY.

    Supports two modes:
    - Exact mode: When specific property terms (rent/deposit/key money) are provided.
    - General benchmark mode: When rent is not yet specified, simulates typical market costs (~4.5x rent).

    Args:
        monthly_rent_yen: Monthly rent in JPY. If omitted/None, defaults to 150,000 JPY benchmark.
        management_fee_yen: Monthly building management/maintenance fee in JPY (default: 10,000 JPY).
        has_pet: Whether the tenant will keep pets (typically adds +1 month deposit).
        deposit_months: Security deposit in months of rent (default: 1.0 month, or 2.0 with pets).
        key_money_months: Key money (reikin) in months of rent (default: 1.0 month).

    Returns:
        Structured breakdown of all move-in expenses, total estimated cost, rent multiplier, and negotiation tips.
    """
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

    return {
        "status": "success",
        "is_benchmark": is_benchmark,
        "mode": "General Market Benchmark"
        if is_benchmark
        else "Exact Property Simulation",
        "monthly_rent_yen": rent,
        "management_fee_yen": management_fee_yen,
        "total_upfront_yen": total_upfront_yen,
        "rent_multiplier": rent_multiplier,
        "breakdown": {
            "deposit_yen": deposit_yen,
            "key_money_yen": key_money_yen,
            "agency_commission_yen": agency_fee_yen,
            "advance_first_month_rent_yen": advance_rent_yen,
            "guarantor_company_fee_yen": guarantor_company_yen,
            "fire_insurance_yen": fire_insurance_yen,
            "key_exchange_yen": key_exchange_yen,
        },
        "cost_saving_tips": tips,
        "a2ui_card": {
            "type": "UpfrontCostCard",
            "title": f"Upfront Moving Cost Estimate (¥{total_upfront_yen:,})",
            "multiplier_text": f"~{rent_multiplier}x monthly rent",
            "total": total_upfront_yen,
        },
    }


def book_viewing_mock(
    property_id: str,
    preferred_datetime: str,
    applicant_name: str,
    contact_phone: str,
) -> dict[str, Any]:
    """Books an on-site property viewing appointment with the listing management agency.

    ★ CRITICAL: This is a state-mutating action requiring explicit human-in-the-loop approval.

    Args:
        property_id: Unique listing identifier or URL.
        preferred_datetime: Preferred date and time (e.g. '2026-08-30 14:00').
        applicant_name: Full name of the applicant viewing the property.
        contact_phone: Contact phone or email for the real estate agent.

    Returns:
        Booking confirmation details including booking ID, meeting instructions, and preparation checklist.
    """
    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"

    return {
        "status": "confirmed",
        "booking_id": booking_id,
        "property_id": property_id,
        "preferred_datetime": preferred_datetime,
        "applicant_name": applicant_name,
        "contact_phone": contact_phone,
        "instructions": {
            "meeting_place": "Directly at the property entrance or agency branch office.",
            "checklist": [
                "Bring a valid photo ID.",
                "Bring a measuring tape for room and furniture dimensions.",
                "Take photos/notes of natural lighting and noise levels.",
            ],
            "cancellation_policy": "Free cancellation up to 2 hours before the scheduled appointment.",
        },
        "a2ui_card": {
            "type": "BookingConfirmationCard",
            "title": "Viewing Reserved",
            "booking_id": booking_id,
            "datetime": preferred_datetime,
            "applicant": applicant_name,
        },
        "message": f"Viewing appointment successfully reserved for {applicant_name} on {preferred_datetime}.",
    }


book_viewing_tool = FunctionTool(
    func=book_viewing_mock,
    require_confirmation=True,
)
