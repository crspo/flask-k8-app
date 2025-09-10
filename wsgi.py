"""WSGI entrypoint for production servers (gunicorn).

Expose a top-level `app` variable so runners can start the application with
`gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app`.
"""
from backend import create_app

app = create_app()
