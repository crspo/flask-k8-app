This `backend` package exposes a `create_app(**overrides)` function that returns a configured Flask application instance.

Usage:

- Development: `python app.py` (keeps previous behaviour)
- WSGI: `from backend import create_app; app = create_app()`

The package currently registers the existing blueprint found in `routes/main.py`.
