"""Resume polisher backend package — split from monolithic `app.py` for clearer boundaries."""

from resume_polisher.factory import create_app

__all__ = ["create_app"]
