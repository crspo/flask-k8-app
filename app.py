"""Entry point for the QR code generator Flask application.

This module now uses a small application factory located in `backend`.
It keeps the simple `python app.py` entrypoint for local development while
making it easy to import `create_app` for testing or WSGI hosting.
"""
from backend import create_app

# Create the Flask app for the default run
app = create_app()

if __name__ == "__main__":
    # Dev mode
    app.run(debug=True, host='0.0.0.0')

