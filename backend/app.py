# app.py
# This is the main entry point of the backend.
# Flask (and hosting platforms like Render) look for a variable called `app` in this file.
# All the real logic lives inside the resume_polisher/ folder — this file stays small on purpose.
from resume_polisher.config import LOCAL_DEBUG_ENABLED, LOCAL_DEV_HOST, LOCAL_DEV_PORT
from resume_polisher.factory import create_app


# Create the Flask app by calling our factory function.
# Gunicorn and the Flask CLI both expect `app` to be available at the top level of this file.
app = create_app()


# This block only runs when you execute: python app.py
# It will NOT run when gunicorn or the Flask CLI imports this file.
if __name__ == "__main__":
    # Note: Flask's built-in server is only for local development.
    # Use gunicorn or another production server when deploying.
    app.run(host=LOCAL_DEV_HOST, port=LOCAL_DEV_PORT, debug=LOCAL_DEBUG_ENABLED)
