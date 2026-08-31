import logging
from unittest.mock import MagicMock, patch

from app.app_utils.logging import (
    deidentify_with_dlp,
    log_structured_event,
    redact_pii,
)


def test_redact_pii_zero_trust_masking_when_dlp_inactive():
    """Verify zero-trust masking for sensitive keys when Cloud DLP is not initialized."""
    data = {
        "applicant_name": "Taro Yamada",
        "contact_phone": "+81-90-1234-5678",
        "email": "taro.yamada@example.jp",
        "property_id": "prop-123",
        "monthly_rent": 180000,
    }
    redacted = redact_pii(data)
    assert redacted["applicant_name"] == "[CONFIDENTIAL_PII_MASKED]"
    assert redacted["contact_phone"] == "[CONFIDENTIAL_PII_MASKED]"
    assert redacted["email"] == "[CONFIDENTIAL_PII_MASKED]"
    assert redacted["property_id"] == "prop-123"
    assert redacted["monthly_rent"] == 180000


def test_deidentify_with_dlp_mocked():
    """Verify Cloud DLP deidentification logic with mock client."""
    mock_dlp_client = MagicMock()
    mock_response = MagicMock()
    mock_response.item.value = "Applicant [PERSON_NAME] phone [PHONE_NUMBER]"
    mock_dlp_client.deidentify_content.return_value = mock_response

    with patch("app.app_utils.logging._get_dlp_client", return_value=mock_dlp_client):
        result = deidentify_with_dlp(
            "Applicant Alex Smith phone +1-555-0199", project_id="test-proj"
        )
        assert result == "Applicant [PERSON_NAME] phone [PHONE_NUMBER]"
        mock_dlp_client.deidentify_content.assert_called_once()


def test_log_structured_event(caplog):
    """Verify structured JSON log emission via caplog."""
    with caplog.at_level(logging.INFO):
        log_structured_event(
            event_type="test_event",
            status="success",
            payload={"applicant_name": "John Doe", "rent": 150000},
            session_id="sess-001",
        )
    assert '"event_type": "test_event"' in caplog.text
    assert "[CONFIDENTIAL_PII_MASKED]" in caplog.text
    assert '"status": "success"' in caplog.text


def test_log_turn_execution(caplog):
    """Verify turn execution structured log output via caplog."""
    from app.app_utils.logging import log_turn_execution

    with caplog.at_level(logging.INFO):
        log_turn_execution(
            turn_intent="Search 2LDK apartments in Shibuya under 250,000 JPY",
            outcome_summary="Found 3 matching listings with separate bath/toilet",
            delegated_subagents=["property_agent"],
            status="success",
            session_id="sess-002",
            metadata={"budget": 250000},
        )
    assert '"event_type": "turn_execution"' in caplog.text
    assert "Search 2LDK apartments" in caplog.text
    assert "property_agent" in caplog.text
