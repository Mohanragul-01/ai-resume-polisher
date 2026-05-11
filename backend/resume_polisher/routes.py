"""Flask URL registration — WHY: keeps routing separate from business logic."""

from flask import Flask, Response, request

from resume_polisher.analyze_handlers import analyze_http_response
from resume_polisher.config import ANALYZE_ROUTE_PATH


def register_analyze_route(app: Flask) -> None:
    """Attach POST /analyze — WHY: app factory imports only this for wiring."""

    @app.post(ANALYZE_ROUTE_PATH)
    def analyze() -> Response:
        # WHY: Delegate to pure handler so tests can call `analyze_http_response` without the decorator.
        return analyze_http_response(request)
