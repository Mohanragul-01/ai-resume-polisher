# gemini_service.py
# This file handles all communication with the Gemini AI API.
# It builds the prompt, sends it to Gemini, and returns the response.
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
    """
    Read the Gemini API key from the environment variable GEMINI_API_KEY.

    Returns:
        The API key as a string, or None if it's missing or empty.
    """

    raw_key = os.environ.get(GEMINI_API_KEY_ENV_NAME)

    # If the environment variable was never set, return None.
    if raw_key is None:
        return None

    # Remove leading/trailing whitespace (e.g. accidental newline when pasting the key).
    cleaned_key = raw_key.strip()

    # If the key is blank after stripping, treat it as missing.
    if cleaned_key == "":
        return None

    return cleaned_key


def build_analysis_prompt(resume_text: str, job_text: str) -> str:
    """
    Combine the resume and job description into a single text prompt for Gemini.

    We clip both texts to their max character limits to avoid sending too many tokens.
    """

    # Clip texts to their limits to save on API costs and avoid huge requests.
    clipped_resume = resume_text[:RESUME_TEXT_CHAR_LIMIT]
    clipped_job = job_text[:JOB_TEXT_CHAR_LIMIT]

    # Build the full prompt by joining the two sections with headers.
    prompt = RESUME_SECTION_HEADER + clipped_resume + JOB_SECTION_HEADER + clipped_job
    return prompt


def generate_gemini_structured_json(api_key: str, user_prompt: str) -> str:
    """
    Send the prompt to Gemini and get back a JSON response.

    We tell Gemini to respond with JSON that matches our TailoredAnalysisJson schema.
    This ensures the output has the exact fields and types we expect.
    """

    # Create a Gemini client using the API key.
    client = genai.Client(api_key=api_key)

    # Configure how Gemini should respond.
    config = types.GenerateContentConfig(
        response_mime_type="application/json",      # Tell Gemini to respond in JSON format.
        response_schema=TailoredAnalysisJson,        # Tell Gemini the exact shape of the JSON.
        system_instruction=ANALYSIS_SYSTEM_INSTRUCTION,  # Our instructions for the AI.
        temperature=GEMINI_JSON_TEMPERATURE,         # Lower = more consistent output.
    )

    # Send the request to Gemini.
    response = client.models.generate_content(
        model=GEMINI_FLASH_MODEL_ID,
        contents=user_prompt,
        config=config,
    )

    # .text gives us the raw response string from Gemini.
    # Note: this can raise an exception if Gemini blocked the response for safety reasons.
    # The caller (fetch_analysis_json_safely) handles that exception.
    return response.text


def fetch_analysis_json_safely(
    api_key: str,
    resume_text: str,
    job_text: str,
) -> tuple[str | None, str | None]:
    """
    Call Gemini and return the result without raising exceptions.

    Returns a tuple of (error_message, json_text):
        - On success: (None, "<json string>")
        - On failure: ("<error description>", None)

    Using a tuple return instead of raising exceptions means the caller
    can handle errors with a simple if-check instead of a try/except.
    """

    try:
        user_prompt = build_analysis_prompt(resume_text, job_text)
        json_text = generate_gemini_structured_json(api_key, user_prompt)
        return (None, json_text)  # No error, return the JSON text.

    except Exception as exc:
        # Capture any error (network issue, safety block, etc.) as a readable string.
        error_message = f"{type(exc).__name__}: {exc}"
        return (error_message, None)  # Return the error, no JSON text.
