"""Validate and clean the AI response before returning it to the client."""

import json
from resume_polisher.config import JSON_PRETTY_INDENT, REQUIRED_ANALYSIS_KEYS, TAILORED_RESUME_MAX_CHARS


def parse_json_object_safely(raw_json_text: str) -> tuple[str | None, dict[str, object]]:
    """Parse body into a dict — reject arrays/strings at root (malformed model output)."""

    stripped = raw_json_text.strip()
    if stripped == "":
        return ("empty Gemini JSON body", {})

    try:
        parsed: object = json.loads(stripped)
    except json.JSONDecodeError as exc:
        return (f"JSONDecodeError: {exc}", {})

    if not isinstance(parsed, dict):
        return ("JSON root must be an object with keys match_score and tailored_resume", {})

    # TODO: understand this — after json.loads, object keys are strings.
    return (None, parsed)


def validate_required_keys_present(payload: dict[str, object]) -> str | None:
    """Fail fast if Gemini omitted a required field."""

    missing = [key for key in REQUIRED_ANALYSIS_KEYS if key not in payload]
    if missing:
        return f"missing required keys: {missing}"
    return None


def bounded_match_score_or_error(value: int) -> tuple[str | None, int]:
    """Enforce MVP rule: score must be 0-100."""

    if 0 <= value <= 100:
        return (None, value)
    return (f"match_score out of range (0-100): {value}", 0)


def coerce_match_score_from_string(token: str) -> tuple[str | None, int]:
    """Accept numeric strings some models emit instead of strict JSON integers."""

    if token == "":
        return ("match_score string was empty", 0)
    try:
        numeric = float(token)
    except ValueError:
        return ("match_score must be a number 0-100", 0)
    return bounded_match_score_or_error(int(round(numeric)))


def coerce_match_score_to_int(raw: object) -> tuple[str | None, int]:
    """Normalize score without trusting JSON types from the model."""

    if isinstance(raw, bool):
        return ("match_score must be a number, not a boolean", 0)
    if isinstance(raw, int):
        return bounded_match_score_or_error(raw)
    if isinstance(raw, float):
        return bounded_match_score_or_error(int(round(raw)))
    if isinstance(raw, str):
        return coerce_match_score_from_string(raw.strip())
    return ("match_score must be a number 0-100", 0)


def sanitize_tailored_resume_text(raw: object) -> tuple[str | None, str]:
    """Strip nulls and normalize newlines so downstream UIs do not choke."""

    if not isinstance(raw, str):
        return ("tailored_resume must be a string", "")

    without_nulls = raw.replace("\x00", "")
    normalized = without_nulls.replace("\r\n", "\n").replace("\r", "\n").strip()

    if len(normalized) > TAILORED_RESUME_MAX_CHARS:
        return (None, normalized[:TAILORED_RESUME_MAX_CHARS])

    return (None, normalized)


def build_safe_analysis_json_body(match_score: int, tailored_resume: str) -> str:
    """Emit only whitelisted keys — stray model fields never reach HTTP."""

    safe_payload = {"match_score": match_score, "tailored_resume": tailored_resume}
    return json.dumps(safe_payload, ensure_ascii=False, indent=JSON_PRETTY_INDENT)


def validate_analysis_payload_fields(payload: dict[str, object]) -> tuple[str | None, int, str]:
    """Apply validation rules to dict fields after JSON parse."""

    missing_error = validate_required_keys_present(payload)
    if missing_error is not None:
        return (missing_error, 0, "")

    score_error, score = coerce_match_score_to_int(payload["match_score"])
    if score_error is not None:
        return (score_error, 0, "")

    text_error, resume_text = sanitize_tailored_resume_text(payload["tailored_resume"])
    if text_error is not None:
        return (text_error, 0, "")

    if resume_text == "":
        return ("tailored_resume is empty after sanitization", 0, "")

    return (None, score, resume_text)


def validate_and_clean_analysis_json(raw_json_text: str) -> tuple[str | None, str]:
    """End-to-end validation — returns safe JSON string or error message for HTTP 502."""

    parse_error, payload = parse_json_object_safely(raw_json_text)
    if parse_error is not None:
        return (parse_error, "")

    field_error, score, resume_text = validate_analysis_payload_fields(payload)
    if field_error is not None:
        return (field_error, "")

    return (None, build_safe_analysis_json_body(score, resume_text))
