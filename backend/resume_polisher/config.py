# config.py
# This file stores all the settings and fixed values used across the backend.
# Instead of writing the same value in many places, we define it once here.


# ── URL Routes ────────────────────────────────────────────────────────────────
# The URL path the frontend sends requests to.
ANALYZE_ROUTE_PATH = "/analyze"


# ── Form Field Names ──────────────────────────────────────────────────────────
# These are the names the frontend uses when uploading files.
RESUME_FORM_FIELD = "resume"
JOB_FORM_FIELD = "job"


# ── Supported File Types ──────────────────────────────────────────────────────
# We only accept PDF and DOCX files.
PDF_EXTENSION = ".pdf"
DOCX_EXTENSION = ".docx"


# ── HTTP Status Codes ─────────────────────────────────────────────────────────
# These are standard web response codes.
# 200 = success, 400 = bad request, 415 = wrong file type,
# 500 = server error, 502 = bad gateway (upstream service failed)
HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNSUPPORTED_MEDIA = 415
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500
HTTP_STATUS_BAD_GATEWAY = 502


# ── Gemini AI Settings ────────────────────────────────────────────────────────
# The name of the environment variable where the Gemini API key is stored.
GEMINI_API_KEY_ENV_NAME = "GEMINI_API_KEY"

# The specific Gemini model we use for analysis.
GEMINI_FLASH_MODEL_ID = "gemini-2.5-flash"

# Maximum number of characters we send to Gemini.
# This limits token usage and keeps costs low.
RESUME_TEXT_CHAR_LIMIT = 10_000
JOB_TEXT_CHAR_LIMIT = 8_000

# Lower temperature = more predictable/consistent output from the AI.
# Range is 0.0 (very predictable) to 1.0 (very creative).
GEMINI_JSON_TEMPERATURE = 0.2

# The instructions we give the AI before every request.
ANALYSIS_SYSTEM_INSTRUCTION = (
    "You are an expert resume coach.\n"
    "Compare the resume to the job description.\n"
    "Set match_score to an integer 0-100 for overall fit (100 = perfect alignment).\n"
    "Write tailored_resume as plain text you would hand to a recruiter (headings/bullets ok).\n"
    "Do not invent employers, degrees, or dates that are not implied by the resume text.\n"
    "Output MUST match the response JSON schema exactly (no markdown fences, no commentary outside JSON)."
)

# Labels added before each section in the prompt we send to Gemini.
RESUME_SECTION_HEADER = "RESUME_TEXT\n"
JOB_SECTION_HEADER = "\n\nJOB_DESCRIPTION_TEXT\n"


# ── Local Development Server Settings ────────────────────────────────────────
LOCAL_DEV_HOST = "127.0.0.1"   # Localhost — only accessible on your own machine
LOCAL_DEV_PORT = 5000           # The port Flask will listen on
LOCAL_DEBUG_ENABLED = True      # Auto-reloads server when you edit code


# ── Response Types ────────────────────────────────────────────────────────────
TEXT_MIMETYPE = "text/plain"        # Plain text response
JSON_MIMETYPE = "application/json"  # JSON response


# ── Error Messages Sent to the Client ────────────────────────────────────────
MISSING_RESUME_FILE_MESSAGE = "missing multipart form field 'resume' (send a PDF or DOCX resume)"
MISSING_JOB_FILE_MESSAGE = "missing multipart form field 'job' (send a PDF or DOCX job description)"
EMPTY_FILENAME_MESSAGE = "empty filename"
UNSUPPORTED_FILE_MESSAGE = f"only {PDF_EXTENSION} and {DOCX_EXTENSION} uploads are supported."


# ── JSON Formatting ───────────────────────────────────────────────────────────
# Number of spaces used when formatting JSON output (makes it readable).
JSON_PRETTY_INDENT = 2


# ── Safety Limits on AI Output ────────────────────────────────────────────────
# Max characters allowed in the tailored resume returned to the browser.
TAILORED_RESUME_MAX_CHARS = 50_000

# The exact keys we expect in the AI's JSON response.
REQUIRED_ANALYSIS_KEYS = ("match_score", "tailored_resume")

# Error shown when the Gemini API key is not set up.
MISSING_GEMINI_API_KEY_MESSAGE = (
    "missing GEMINI_API_KEY - set it in your environment before calling /analyze (see plan.md)"
)
