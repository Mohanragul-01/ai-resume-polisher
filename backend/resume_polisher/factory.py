# factory.py
# This file is responsible for creating and configuring the Flask app.
# Using a factory function (instead of creating `app` at the top of a file) makes
# it easier to test the app and configure it differently for different environments.
import os
from flask import Flask
from flask_cors import CORS
from resume_polisher.routes import register_analyze_route


# These are the default origins allowed during local development.
# CORS (Cross-Origin Resource Sharing) controls which websites can call our backend.
DEFAULT_CORS_ORIGINS = ["http://127.0.0.1:5173", "http://localhost:5173"]


def read_cors_origins() -> list[str]:
    """
    Read the list of allowed frontend URLs from the environment variable CORS_ORIGINS.

    If the environment variable is not set, fall back to the local dev defaults.
    Multiple origins can be separated by commas in the environment variable.
    Example: CORS_ORIGINS=https://myapp.com,https://www.myapp.com
    """

    # Get the CORS_ORIGINS environment variable, or use an empty string if not set.
    raw = os.environ.get("CORS_ORIGINS", "").strip()

    # If nothing was set, use the local development defaults.
    if raw == "":
        return DEFAULT_CORS_ORIGINS

    # Split by comma, strip whitespace from each part, and remove any empty entries.
    origins = [origin.strip() for origin in raw.split(",") if origin.strip() != ""]
    return origins


def create_app() -> Flask:
    """
    Build and return the configured Flask application.

    Steps:
    1. Create a Flask instance.
    2. Enable CORS so the frontend can make requests to this backend.
    3. Register the /analyze route.
    """
    app = Flask(__name__)

    # Allow the frontend to call this backend from the configured origins.
    CORS(app, origins=read_cors_origins())

    # Attach the /analyze route to the app.
    register_analyze_route(app)

    return app
