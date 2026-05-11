"""POST /analyze handler."""

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


def log_extracted_text_to_console(document_role: str, original_name: str, text: str) -> None:
    """Print extracted text to the server console (useful while developing)."""

    print(f"--- extracted {document_role} from upload: {original_name!r} ---")
    print(text)
    print("--- end extracted text ---")


def log_gemini_validated_json_to_console(json_text: str) -> None:
    """Print the final JSON we return to the client."""

    print("--- Gemini validated JSON ---")
    print(json_text)
    print("--- end Gemini validated JSON ---")


def log_gemini_failure_to_console(message: str) -> None:
    """Print errors in a visible place while developing."""

    print("--- Gemini pipeline failed ---")
    print(message)
    print("--- end Gemini failure ---")


def respond_missing_gemini_api_key() -> Response:
    """Return a clear message when the API key is not configured."""

    return Response(
        MISSING_GEMINI_API_KEY_MESSAGE,
        status=HTTP_STATUS_INTERNAL_SERVER_ERROR,
        mimetype=TEXT_MIMETYPE,
    )


def bad_empty_filename_response() -> Response:
    """Return a clear error when the uploaded file has no name."""

    return Response(EMPTY_FILENAME_MESSAGE, status=HTTP_STATUS_BAD_REQUEST, mimetype=TEXT_MIMETYPE)


def bad_file_kind_response() -> Response:
    """Return a clear error for unsupported file types."""

    return Response(UNSUPPORTED_FILE_MESSAGE, status=HTTP_STATUS_UNSUPPORTED_MEDIA, mimetype=TEXT_MIMETYPE)


def gateway_text_response(message: str) -> Response:
    """Return a simple 502 response."""

    return Response(message, status=HTTP_STATUS_BAD_GATEWAY, mimetype=TEXT_MIMETYPE)


def extract_uploaded_text_safely(file_storage: FileStorage) -> tuple[Response | None, str, str]:
    """Parse one multipart file into plain text or return an HTTP error response."""

    original_name = file_storage.filename or ""
    if original_name.strip() == "":
        return (bad_empty_filename_response(), "", "")

    kind = extension_kind(original_name)
    if kind is None:
        return (bad_file_kind_response(), original_name, "")

    raw_bytes = file_storage.read()
    text = extract_text_for_kind(kind, raw_bytes)
    return (None, original_name, text)


def extract_resume_and_job_texts(
    resume_file: FileStorage,
    job_file: FileStorage,
) -> tuple[Response | None, str, str, str, str]:
    """Extract resume text and job text (in that order)."""

    resume_error, resume_name, resume_text = extract_uploaded_text_safely(resume_file)
    if resume_error is not None:
        return (resume_error, "", "", "", "")

    job_error, job_name, job_text = extract_uploaded_text_safely(job_file)
    if job_error is not None:
        return (job_error, resume_name, resume_text, "", "")

    return (None, resume_name, resume_text, job_name, job_text)


def build_response_from_validated_json(raw_json: str) -> Response:
    """Validate JSON and return either a 200 JSON response or a 502 error."""

    validate_error, safe_json = validate_and_clean_analysis_json(raw_json)
    if validate_error is not None:
        log_gemini_failure_to_console(f"{validate_error}\nRAW:\n{raw_json}")
        return gateway_text_response(validate_error)

    log_gemini_validated_json_to_console(safe_json)
    return Response(safe_json, status=HTTP_STATUS_OK, mimetype=JSON_MIMETYPE)


def build_ai_analysis_response(api_key: str, resume_text: str, job_text: str) -> Response:
    """Call the AI service, then validate and clean its JSON."""

    gemini_error, raw_json = fetch_analysis_json_safely(api_key, resume_text, job_text)
    if gemini_error is not None:
        log_gemini_failure_to_console(gemini_error)
        return gateway_text_response(gemini_error)

    if raw_json is None:
        log_gemini_failure_to_console("Gemini returned no JSON body")
        return gateway_text_response("Gemini returned no JSON body")

    return build_response_from_validated_json(raw_json)


def analyze_resume_and_job(
    resume_name: str,
    resume_text: str,
    job_name: str,
    job_text: str,
) -> Response:
    """Log uploads, require API key, run Gemini + validation."""

    log_extracted_text_to_console("resume", resume_name, resume_text)
    log_extracted_text_to_console("job", job_name, job_text)
    api_key = read_gemini_api_key()
    if api_key is None:
        return respond_missing_gemini_api_key()
    return build_ai_analysis_response(api_key, resume_text, job_text)


def analyze_http_response(http_request: Request) -> Response:
    """Handle the /analyze request."""

    if RESUME_FORM_FIELD not in http_request.files:
        return Response(MISSING_RESUME_FILE_MESSAGE, status=HTTP_STATUS_BAD_REQUEST, mimetype=TEXT_MIMETYPE)

    if JOB_FORM_FIELD not in http_request.files:
        return Response(MISSING_JOB_FILE_MESSAGE, status=HTTP_STATUS_BAD_REQUEST, mimetype=TEXT_MIMETYPE)

    resume_file = http_request.files[RESUME_FORM_FIELD]
    job_file = http_request.files[JOB_FORM_FIELD]
    error_response, resume_name, resume_text, job_name, job_text = extract_resume_and_job_texts(
        resume_file,
        job_file,
    )
    if error_response is not None:
        return error_response

    return analyze_resume_and_job(resume_name, resume_text, job_name, job_text)
