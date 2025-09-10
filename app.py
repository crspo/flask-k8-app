"""Entry point for the QR code generator Flask application.

This module now uses a small application factory located in `backend`.
It keeps the simple `python app.py` entrypoint for local development while
making it easy to import `create_app` for testing or WSGI hosting.
"""
from backend import create_app
import os

# Create the Flask app for the default run
app = create_app()

if __name__ == "__main__":
    # Support running locally via `python app.py` — debug controlled by env var
    debug = os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "True")
    app.run(debug=debug, host="0.0.0.0")

