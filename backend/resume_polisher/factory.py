"""Application factory."""

import os
from flask import Flask
from flask_cors import CORS
from resume_polisher.routes import register_analyze_route


DEFAULT_CORS_ORIGINS = ["http://127.0.0.1:5173", "http://localhost:5173"]


def read_cors_origins() -> list[str]:
    """Read allowed origins from env, or return local dev defaults."""

    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if raw == "":
        return DEFAULT_CORS_ORIGINS
    return [part.strip() for part in raw.split(",") if part.strip() != ""]


def create_app() -> Flask:
    """Build the Flask app."""

    app = Flask(__name__)
    # Allows the frontend domain to call the backend.
    CORS(app, origins=read_cors_origins())
    register_analyze_route(app)
    return app
