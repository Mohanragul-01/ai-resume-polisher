"""Constants shared across the backend."""

# API route used by the frontend.
ANALYZE_ROUTE_PATH = "/analyze"

# Form field names expected by the backend.
RESUME_FORM_FIELD = "resume"
JOB_FORM_FIELD = "job"

# File types we accept in the MVP.
PDF_EXTENSION = ".pdf"
DOCX_EXTENSION = ".docx"

HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNSUPPORTED_MEDIA = 415
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500
HTTP_STATUS_BAD_GATEWAY = 502

# Name of the environment variable that holds the Gemini API key.
GEMINI_API_KEY_ENV_NAME = "GEMINI_API_KEY"

# Gemini model used for analysis.
GEMINI_FLASH_MODEL_ID = "gemini-2.5-flash"

# Simple size limits to reduce token usage.
RESUME_TEXT_CHAR_LIMIT = 10_000
JOB_TEXT_CHAR_LIMIT = 8_000

# Lower temperature = more consistent JSON.
GEMINI_JSON_TEMPERATURE = 0.2

# Instructions for the AI model.
ANALYSIS_SYSTEM_INSTRUCTION = (
    "You are an expert resume coach.\n"
    "Compare the resume to the job description.\n"
    "Set match_score to an integer 0-100 for overall fit (100 = perfect alignment).\n"
    "Write tailored_resume as plain text you would hand to a recruiter (headings/bullets ok).\n"
    "Do not invent employers, degrees, or dates that are not implied by the resume text.\n"
    "Output MUST match the response JSON schema exactly (no markdown fences, no commentary outside JSON)."
)

RESUME_SECTION_HEADER = "RESUME_TEXT\n"
JOB_SECTION_HEADER = "\n\nJOB_DESCRIPTION_TEXT\n"

LOCAL_DEV_HOST = "127.0.0.1"
LOCAL_DEV_PORT = 5000
LOCAL_DEBUG_ENABLED = True

TEXT_MIMETYPE = "text/plain"
JSON_MIMETYPE = "application/json"

MISSING_RESUME_FILE_MESSAGE = "missing multipart form field 'resume' (send a PDF or DOCX resume)"
MISSING_JOB_FILE_MESSAGE = "missing multipart form field 'job' (send a PDF or DOCX job description)"
EMPTY_FILENAME_MESSAGE = "empty filename"
UNSUPPORTED_FILE_MESSAGE = f"only {PDF_EXTENSION} and {DOCX_EXTENSION} uploads are supported."

JSON_PRETTY_INDENT = 2

# Safety limit to avoid sending extremely large text back to the browser.
TAILORED_RESUME_MAX_CHARS = 50_000

# Only these keys are returned to the client.
REQUIRED_ANALYSIS_KEYS = ("match_score", "tailored_resume")

MISSING_GEMINI_API_KEY_MESSAGE = (
    "missing GEMINI_API_KEY - set it in your environment before calling /analyze (see plan.md)"
)
