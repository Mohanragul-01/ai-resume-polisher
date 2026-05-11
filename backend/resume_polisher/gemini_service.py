"""Gemini API calls."""

import os
from google import genai
from google.genai import types
from resume_polisher.config import (
    ANALYSIS_SYSTEM_INSTRUCTION,
    GEMINI_API_KEY_ENV_NAME,
    GEMINI_FLASH_MODEL_ID,
    GEMINI_JSON_TEMPERATURE,
    JOB_TEXT_CHAR_LIMIT,
    JOB_SECTION_HEADER,
    RESUME_SECTION_HEADER,
    RESUME_TEXT_CHAR_LIMIT,
)
from resume_polisher.schemas import TailoredAnalysisJson


def read_gemini_api_key() -> str | None:
    """Load the Gemini API key from the environment."""

    # Stripping avoids issues like trailing newline characters.
    raw_key = os.environ.get(GEMINI_API_KEY_ENV_NAME)
    if raw_key is None:
        return None
    stripped = raw_key.strip()
    if stripped == "":
        return None
    return stripped


def build_analysis_prompt(resume_text: str, job_text: str) -> str:
    """Combine clipped resume + job text into the user message Gemini sees."""

    clipped_resume = resume_text[:RESUME_TEXT_CHAR_LIMIT]
    clipped_job = job_text[:JOB_TEXT_CHAR_LIMIT]
    return RESUME_SECTION_HEADER + clipped_resume + JOB_SECTION_HEADER + clipped_job


def generate_gemini_structured_json(api_key: str, user_prompt: str) -> str:
    """Call Gemini Flash with JSON mime + schema so output matches `TailoredAnalysisJson`."""

    # TODO: understand this — creating a client per request is simple for now.
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=TailoredAnalysisJson,
        system_instruction=ANALYSIS_SYSTEM_INSTRUCTION,
        temperature=GEMINI_JSON_TEMPERATURE,
    )
    response = client.models.generate_content(
        model=GEMINI_FLASH_MODEL_ID,
        contents=user_prompt,
        config=config,
    )
    # TODO: understand this — `.text` can raise on blocked/safety responses; caller catches it.
    return response.text


def fetch_analysis_json_safely(
    api_key: str,
    resume_text: str,
    job_text: str,
) -> tuple[str | None, str | None]:
    """Return `(error_or_none, json_text_or_none)` and never raise exceptions."""

    try:
        user_prompt = build_analysis_prompt(resume_text, job_text)
        json_text = generate_gemini_structured_json(api_key, user_prompt)
        return (None, json_text)
    except Exception as exc:
        return (f"{type(exc).__name__}: {exc}", None)
