# analyze_handlers.py
# This file handles the POST /analyze request end-to-end.
# It reads uploaded files, extracts their text, calls the AI, and returns the result.
from flask import Request, Response
from werkzeug.datastructures import FileStorage
from resume_polisher.config import (
    HTTP_STATUS_BAD_GATEWAY,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_OK,
    HTTP_STATUS_UNSUPPORTED_MEDIA,
    EMPTY_FILENAME_MESSAGE,
    JOB_FORM_FIELD,
    JSON_MIMETYPE,
    MISSING_GEMINI_API_KEY_MESSAGE,
    MISSING_JOB_FILE_MESSAGE,
    MISSING_RESUME_FILE_MESSAGE,
    RESUME_FORM_FIELD,
    TEXT_MIMETYPE,
    UNSUPPORTED_FILE_MESSAGE,
)
from resume_polisher.documents import extract_text_for_kind, extension_kind
from resume_polisher.gemini_service import fetch_analysis_json_safely, read_gemini_api_key
from resume_polisher.validation import validate_and_clean_analysis_json


# ── Logging Helpers ───────────────────────────────────────────────────────────
# These functions print useful debug info to the server console during development.

def log_extracted_text_to_console(document_role: str, original_name: str, text: str) -> None:
    """Print the extracted text from an uploaded file to the console."""
    print(f"--- extracted {document_role} from upload: {original_name!r} ---")
    print(text)
    print("--- end extracted text ---")


def log_gemini_validated_json_to_console(json_text: str) -> None:
    """Print the final validated JSON we are sending back to the client."""
    print("--- Gemini validated JSON ---")
    print(json_text)
    print("--- end Gemini validated JSON ---")


def log_gemini_failure_to_console(message: str) -> None:
    """Print a failure message when the Gemini pipeline goes wrong."""
    print("--- Gemini pipeline failed ---")
    print(message)
    print("--- end Gemini failure ---")


# ── HTTP Error Response Helpers ───────────────────────────────────────────────
# Each function below creates a specific HTTP error response.

def respond_missing_gemini_api_key() -> Response:
    """Return HTTP 500 when the Gemini API key is not configured in the environment."""
    return Response(
        MISSING_GEMINI_API_KEY_MESSAGE,
        status=HTTP_STATUS_INTERNAL_SERVER_ERROR,
        mimetype=TEXT_MIMETYPE,
    )


def bad_empty_filename_response() -> Response:
    """Return HTTP 400 when the uploaded file has no filename."""
    return Response(EMPTY_FILENAME_MESSAGE, status=HTTP_STATUS_BAD_REQUEST, mimetype=TEXT_MIMETYPE)


def bad_file_kind_response() -> Response:
    """Return HTTP 415 when the uploaded file is not a PDF or DOCX."""
    return Response(UNSUPPORTED_FILE_MESSAGE, status=HTTP_STATUS_UNSUPPORTED_MEDIA, mimetype=TEXT_MIMETYPE)


def gateway_text_response(message: str) -> Response:
    """Return HTTP 502 when the AI service (Gemini) fails."""
    return Response(message, status=HTTP_STATUS_BAD_GATEWAY, mimetype=TEXT_MIMETYPE)


# ── File Processing ───────────────────────────────────────────────────────────

def extract_uploaded_text_safely(file_storage: FileStorage) -> tuple[Response | None, str, str]:
    """
    Read one uploaded file and extract its plain text.

    Steps:
    1. Check the filename is not blank.
    2. Check the file type is supported (PDF or DOCX).
    3. Read the file bytes and extract text.

    Returns a tuple of (error_response, filename, extracted_text):
        - On success: (None, "resume.pdf", "John Doe\nSoftware Engineer...")
        - On failure: (Response with error, "", "")
    """

    original_name = file_storage.filename or ""

    # Reject files with no name.
    if original_name.strip() == "":
        return (bad_empty_filename_response(), "", "")

    # Check if we support this file type.
    kind = extension_kind(original_name)
    if kind is None:
        return (bad_file_kind_response(), original_name, "")

    # Read the file content and extract its text.
    raw_bytes = file_storage.read()
    text = extract_text_for_kind(kind, raw_bytes)

    return (None, original_name, text)


def extract_resume_and_job_texts(
    resume_file: FileStorage,
    job_file: FileStorage,
) -> tuple[Response | None, str, str, str, str]:
    """
    Extract text from both the resume file and the job description file.

    Returns a tuple of (error_response, resume_name, resume_text, job_name, job_text):
        - On success: (None, "resume.pdf", "...", "job.pdf", "...")
        - On failure: (Response with error, "", "", "", "")
    """

    # Extract text from the resume file first.
    resume_error, resume_name, resume_text = extract_uploaded_text_safely(resume_file)
    if resume_error is not None:
        return (resume_error, "", "", "", "")

    # Extract text from the job description file.
    job_error, job_name, job_text = extract_uploaded_text_safely(job_file)
    if job_error is not None:
        return (job_error, resume_name, resume_text, "", "")

    return (None, resume_name, resume_text, job_name, job_text)


# ── AI Response Handling ──────────────────────────────────────────────────────

def build_response_from_validated_json(raw_json: str) -> Response:
    """
    Validate the raw JSON from Gemini and return the appropriate HTTP response.

    If validation passes → return HTTP 200 with the cleaned JSON.
    If validation fails  → return HTTP 502 with an error message.
    """

    validate_error, safe_json = validate_and_clean_analysis_json(raw_json)

    if validate_error is not None:
        log_gemini_failure_to_console(f"{validate_error}\nRAW:\n{raw_json}")
        return gateway_text_response(validate_error)

    log_gemini_validated_json_to_console(safe_json)
    return Response(safe_json, status=HTTP_STATUS_OK, mimetype=JSON_MIMETYPE)


def build_ai_analysis_response(api_key: str, resume_text: str, job_text: str) -> Response:
    """
    Send texts to Gemini, get a JSON response, validate it, and return the HTTP response.
    """

    # Call Gemini and get back either an error or a JSON string.
    gemini_error, raw_json = fetch_analysis_json_safely(api_key, resume_text, job_text)

    if gemini_error is not None:
        log_gemini_failure_to_console(gemini_error)
        return gateway_text_response(gemini_error)

    if raw_json is None:
        log_gemini_failure_to_console("Gemini returned no JSON body")
        return gateway_text_response("Gemini returned no JSON body")

    # Validate and clean the JSON before sending it to the client.
    return build_response_from_validated_json(raw_json)


def analyze_resume_and_job(
    resume_name: str,
    resume_text: str,
    job_name: str,
    job_text: str,
) -> Response:
    """
    Log the extracted texts, check for the API key, and run the AI analysis.

    This is called after we've successfully extracted text from both uploaded files.
    """

    # Log both texts to the console so developers can see what was extracted.
    log_extracted_text_to_console("resume", resume_name, resume_text)
    log_extracted_text_to_console("job", job_name, job_text)

    # Make sure the Gemini API key is available before calling the AI.
    api_key = read_gemini_api_key()
    if api_key is None:
        return respond_missing_gemini_api_key()

    return build_ai_analysis_response(api_key, resume_text, job_text)


# ── Main Request Handler ──────────────────────────────────────────────────────

def analyze_http_response(http_request: Request) -> Response:
    """
    Handle the POST /analyze HTTP request from start to finish.

    Steps:
    1. Check that both 'resume' and 'job' files were uploaded.
    2. Extract text from both files.
    3. Send the texts to Gemini and return the AI analysis.
    """

    # Step 1: Make sure the resume file was included in the request.
    if RESUME_FORM_FIELD not in http_request.files:
        return Response(MISSING_RESUME_FILE_MESSAGE, status=HTTP_STATUS_BAD_REQUEST, mimetype=TEXT_MIMETYPE)

    # Step 1b: Make sure the job description file was included in the request.
    if JOB_FORM_FIELD not in http_request.files:
        return Response(MISSING_JOB_FILE_MESSAGE, status=HTTP_STATUS_BAD_REQUEST, mimetype=TEXT_MIMETYPE)

    # Step 2: Get the uploaded file objects from the request.
    resume_file = http_request.files[RESUME_FORM_FIELD]
    job_file = http_request.files[JOB_FORM_FIELD]

    # Step 2b: Extract text from both files.
    error_response, resume_name, resume_text, job_name, job_text = extract_resume_and_job_texts(
        resume_file,
        job_file,
    )

    # If either file had a problem, return the error response immediately.
    if error_response is not None:
        return error_response

    # Step 3: Run the AI analysis and return the result.
    return analyze_resume_and_job(resume_name, resume_text, job_name, job_text)
