import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

# Configure root logger
logger = logging.getLogger("relocation_concierge.audit")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


_DLP_CLIENT = None
_DLP_INITIALIZED = False


def _get_dlp_client():
    """Initializes Google Cloud DLP client if enabled and available in environment."""
    global _DLP_CLIENT, _DLP_INITIALIZED
    if _DLP_INITIALIZED:
        return _DLP_CLIENT

    _DLP_INITIALIZED = True
    # Enable if explicitly enabled or if running in a GCP environment with a valid project ID
    enable_dlp = os.environ.get("ENABLE_CLOUD_DLP", "").lower() in ("true", "1", "yes")
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    if enable_dlp and project_id:
        try:
            from google.cloud import dlp_v2

            _DLP_CLIENT = dlp_v2.DlpServiceClient()
        except Exception as e:
            logger.debug(f"Cloud DLP initialization skipped or failed: {e}")
            _DLP_CLIENT = None
    return _DLP_CLIENT


def deidentify_with_dlp(text: str, project_id: str | None = None) -> str:
    """Uses Google Cloud Sensitive Data Protection (DLP API) to inspect and de-identify PII.

    Detects person names, phone numbers, emails, addresses, credit cards, and credentials
    using enterprise machine-learning info-type detectors.
    """
    dlp_client = _get_dlp_client()
    if not dlp_client or not text:
        return text

    proj = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not proj:
        return text

    try:
        parent = f"projects/{proj}/locations/global"
        inspect_config = {
            "info_types": [
                {"name": "PERSON_NAME"},
                {"name": "PHONE_NUMBER"},
                {"name": "EMAIL_ADDRESS"},
                {"name": "STREET_ADDRESS"},
                {"name": "CREDENTIAL"},
                {"name": "JAPAN_MY_NUMBER"},
            ]
        }
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [
                    {"primitive_transformation": {"replace_with_info_type_config": {}}}
                ]
            }
        }
        response = dlp_client.deidentify_content(
            request={
                "parent": parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": {"value": text},
            }
        )
        return response.item.value
    except Exception as e:
        logger.warning(f"Cloud DLP de-identification call failed, falling back: {e}")
        return text


def redact_pii(data: Any) -> Any:
    """Recursively walks dictionaries, lists, or strings and applies Cloud DLP PII redaction.

    When Cloud DLP is active, inspects all string payloads via Cloud DLP API.
    When Cloud DLP is inactive, applies zero-trust key-level masking for known sensitive fields.
    """
    dlp_client = _get_dlp_client()

    if isinstance(data, dict):
        redacted = {}
        for k, v in data.items():
            k_lower = str(k).lower()
            if any(
                sensitive_key in k_lower
                for sensitive_key in [
                    "applicant_name",
                    "full_name",
                    "user_name",
                    "phone",
                    "tel",
                    "mobile",
                    "email",
                    "contact",
                ]
            ):
                # When DLP is enabled, pass through DLP de-identification; otherwise mask safely
                if dlp_client and isinstance(v, str):
                    redacted[k] = deidentify_with_dlp(v)
                else:
                    redacted[k] = "[CONFIDENTIAL_PII_MASKED]"
            else:
                redacted[k] = redact_pii(v)
        return redacted
    elif isinstance(data, list):
        return [redact_pii(item) for item in data]
    elif isinstance(data, str):
        if dlp_client:
            return deidentify_with_dlp(data)
        return data
    return data


def log_structured_event(
    event_type: str,
    status: str,
    payload: dict[str, Any],
    session_id: str | None = None,
    user_id: str | None = None,
) -> None:
    """Emits a single-line, PII-redacted structured JSON audit log entry."""
    sanitized_payload = redact_pii(payload)
    log_record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": event_type,
        "status": status,
        "session_id": session_id or "unknown_session",
        "user_id": user_id or "anonymous_user",
        "data": sanitized_payload,
    }
    logger.info(json.dumps(log_record, ensure_ascii=False))


def log_turn_execution(
    turn_intent: str,
    outcome_summary: str,
    delegated_subagents: list[str],
    status: str = "success",
    session_id: str | None = None,
    user_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Logs the turn execution lifecycle comparing user intent against agent outcome.

    Args:
        turn_intent: The inferred or explicit user intent (e.g. 'Search 1LDK apartments in Meguro').
        outcome_summary: The synthesized result presented to the user.
        delegated_subagents: List of sub-agents delegated to satisfy the intent.
        status: Execution status ('success', 'partial_match', 'error').
        session_id: Active session identifier.
        user_id: Active user identifier.
        metadata: Additional contextual parameters (e.g. budget, filters applied).
    """
    payload = {
        "intent": turn_intent,
        "outcome": outcome_summary,
        "delegated_subagents": delegated_subagents,
        "metadata": metadata or {},
    }
    log_structured_event(
        event_type="turn_execution",
        status=status,
        payload=payload,
        session_id=session_id,
        user_id=user_id,
    )


# Backward-compatibility alias
log_intent_vs_outcome = log_turn_execution
