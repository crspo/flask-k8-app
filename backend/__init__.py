"""
Backend package initializer.

This package exposes the Flask application factory to keep application
structure modular and make it easier to import from `backend` in the
project root. It delegates routing to the existing `routes` module.
"""
from flask import Flask

def create_app(**config_overrides):
    # Disable Flask's automatic static file handling to avoid colliding with
    # the custom `/static/<path:filename>` routes defined in the blueprint.
    app = Flask(__name__, static_folder=None)

    # Allow callers to override config programmatically
    for k, v in config_overrides.items():
        app.config[k] = v

    # Register blueprint from the original routes module
    try:
        # import here to avoid circular imports when used as a module
        from backend.routes.main import bp as main_bp
        app.register_blueprint(main_bp)
    except Exception:
        # keep failing import visible during startup
        raise

    return app
