# validation.py
# This file checks and cleans the JSON response from Gemini before sending it to the frontend.
# We never trust AI output blindly — we validate every field.
import json
from resume_polisher.config import JSON_PRETTY_INDENT, REQUIRED_ANALYSIS_KEYS, TAILORED_RESUME_MAX_CHARS


def parse_json_object_safely(raw_json_text: str) -> tuple[str | None, dict]:
    """
    Parse a JSON string into a Python dictionary.

    Returns (error_message, result_dict):
        - On success: (None, {"match_score": ..., "tailored_resume": ...})
        - On failure: ("reason it failed", {})
    """

    stripped = raw_json_text.strip()

    # Reject empty responses.
    if stripped == "":
        return ("empty Gemini JSON body", {})

    # Try to parse the JSON string.
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        return (f"JSONDecodeError: {exc}", {})

    # The root value must be a dictionary (JSON object), not a list or plain string.
    if not isinstance(parsed, dict):
        return ("JSON root must be an object with keys match_score and tailored_resume", {})

    return (None, parsed)


def validate_required_keys_present(payload: dict) -> str | None:
    """
    Check that all required keys exist in the parsed JSON dictionary.

    Returns an error message if any keys are missing, or None if everything is fine.
    """

    missing_keys = [key for key in REQUIRED_ANALYSIS_KEYS if key not in payload]

    if missing_keys:
        return f"missing required keys: {missing_keys}"

    return None  # All required keys are present.


def bounded_match_score_or_error(value: int) -> tuple[str | None, int]:
    """
    Check that the match score is between 0 and 100.

    Returns (error_message, score):
        - On success: (None, valid_score)
        - On failure: ("error reason", 0)
    """

    if 0 <= value <= 100:
        return (None, value)

    return (f"match_score out of range (0-100): {value}", 0)


def coerce_match_score_from_string(token: str) -> tuple[str | None, int]:
    """
    Handle the case where Gemini returned the score as a string like "85" instead of 85.

    Returns (error_message, score).
    """

    if token == "":
        return ("match_score string was empty", 0)

    # Try to convert the string to a number.
    try:
        numeric = float(token)
    except ValueError:
        return ("match_score must be a number 0-100", 0)

    # Round to the nearest integer and check the range.
    return bounded_match_score_or_error(int(round(numeric)))


def coerce_match_score_to_int(raw_value) -> tuple[str | None, int]:
    """
    Normalize the match_score to an integer regardless of what type Gemini returned.

    Handles: int, float, str, and rejects bool and anything else.

    Returns (error_message, score).
    """

    # Booleans are technically ints in Python, so we check for them first.
    if isinstance(raw_value, bool):
        return ("match_score must be a number, not a boolean", 0)

    if isinstance(raw_value, int):
        return bounded_match_score_or_error(raw_value)

    if isinstance(raw_value, float):
        return bounded_match_score_or_error(int(round(raw_value)))

    if isinstance(raw_value, str):
        return coerce_match_score_from_string(raw_value.strip())

    # Any other type (list, dict, None, etc.) is rejected.
    return ("match_score must be a number 0-100", 0)


def sanitize_tailored_resume_text(raw_value) -> tuple[str | None, str]:
    """
    Clean up the tailored_resume field from the AI response.

    Steps:
    1. Confirm it's a string.
    2. Remove null characters (they can break some browsers/UIs).
    3. Normalize line endings to Unix-style (\n).
    4. Trim to TAILORED_RESUME_MAX_CHARS if it's too long.

    Returns (error_message, cleaned_text).
    """

    if not isinstance(raw_value, str):
        return ("tailored_resume must be a string", "")

    # Remove null bytes (\x00) which can cause display issues.
    without_nulls = raw_value.replace("\x00", "")

    # Normalize Windows-style (\r\n) and old Mac-style (\r) line endings to \n.
    normalized = without_nulls.replace("\r\n", "\n").replace("\r", "\n").strip()

    # If the text is too long, trim it to the allowed maximum.
    if len(normalized) > TAILORED_RESUME_MAX_CHARS:
        return (None, normalized[:TAILORED_RESUME_MAX_CHARS])

    return (None, normalized)


def build_safe_analysis_json_body(match_score: int, tailored_resume: str) -> str:
    """
    Build the final JSON string we send back to the frontend.

    We only include the fields we expect — this prevents any extra/unexpected
    fields from Gemini leaking through to the client.
    """

    safe_payload = {
        "match_score": match_score,
        "tailored_resume": tailored_resume,
    }

    return json.dumps(safe_payload, ensure_ascii=False, indent=JSON_PRETTY_INDENT)


def validate_analysis_payload_fields(payload: dict) -> tuple[str | None, int, str]:
    """
    Validate and clean all fields in the parsed JSON dictionary.

    Returns (error_message, match_score, tailored_resume_text):
        - On success: (None, <valid score>, <cleaned resume text>)
        - On failure: ("<reason>", 0, "")
    """

    # Step 1: Check that required keys exist.
    missing_error = validate_required_keys_present(payload)
    if missing_error is not None:
        return (missing_error, 0, "")

    # Step 2: Validate and normalize the match_score field.
    score_error, score = coerce_match_score_to_int(payload["match_score"])
    if score_error is not None:
        return (score_error, 0, "")

    # Step 3: Validate and clean the tailored_resume field.
    text_error, resume_text = sanitize_tailored_resume_text(payload["tailored_resume"])
    if text_error is not None:
        return (text_error, 0, "")

    # Step 4: Reject a resume that is blank after cleaning.
    if resume_text == "":
        return ("tailored_resume is empty after sanitization", 0, "")

    return (None, score, resume_text)


def validate_and_clean_analysis_json(raw_json_text: str) -> tuple[str | None, str]:
    """
    Full validation pipeline: parse → validate fields → return safe JSON.

    This is the main function called from outside this file.

    Returns (error_message, safe_json_string):
        - On success: (None, "<valid JSON string>")
        - On failure: ("<error reason>", "")
    """

    # Step 1: Parse the raw JSON string into a dictionary.
    parse_error, payload = parse_json_object_safely(raw_json_text)
    if parse_error is not None:
        return (parse_error, "")

    # Step 2: Validate and clean each field in the dictionary.
    field_error, score, resume_text = validate_analysis_payload_fields(payload)
    if field_error is not None:
        return (field_error, "")

    # Step 3: Build and return the safe JSON string.
    return (None, build_safe_analysis_json_body(score, resume_text))
