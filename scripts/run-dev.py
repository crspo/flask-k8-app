"""Simple local server for smoke-testing the app during development.

Usage: python scripts/run-dev.py

This starts Flask's development server bound to 127.0.0.1:5000 and is only
intended for local testing. Do not use in production.
"""
import os
import sys

# Ensure repo root is on sys.path so local imports like `wsgi` resolve
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from wsgi import app

if __name__ == '__main__':
    # Use a predictable host/port and disable reloader.
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
