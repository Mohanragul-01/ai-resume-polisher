# routes.py
# This file connects URL paths to the functions that handle them.
# Keeping routing separate from business logic makes the code easier to test and maintain.
from flask import Flask, Response, request
from resume_polisher.config import ANALYZE_ROUTE_PATH
from resume_polisher.analyze_handlers import analyze_http_response


def register_analyze_route(app: Flask) -> None:
    """
    Register the POST /analyze route on the Flask app.

    When the frontend sends a POST request to /analyze,
    Flask will call the analyze() function below.
    """

    @app.post(ANALYZE_ROUTE_PATH)
    def analyze() -> Response:
        # Pass the incoming HTTP request to our handler function.
        # Keeping the logic in analyze_http_response() (not here) means
        # we can test it directly without needing a running Flask server.
        return analyze_http_response(request)
