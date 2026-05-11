"""
WSGI entry module — WHY: `flask --app app run` and Render keep importing `app` from this path.

All logic lives under `resume_polisher/`; this file stays tiny on purpose.
"""

from resume_polisher.config import LOCAL_DEBUG_ENABLED, LOCAL_DEV_HOST, LOCAL_DEV_PORT
from resume_polisher.factory import create_app

# WHY: Flask CLI / gunicorn convention expects `app` at module scope.
app = create_app()


def run_local_dev_server() -> None:
    """Start Flask's built-in server — WHY: `python app.py` stays beginner-friendly."""

    # TODO: understand this — dev server is not production-safe.
    app.run(host=LOCAL_DEV_HOST, port=LOCAL_DEV_PORT, debug=LOCAL_DEBUG_ENABLED)


if __name__ == "__main__":
    run_local_dev_server()
