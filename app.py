"""
Entry point for the QR code generator Flask application.

Registers Blueprints for route handling and runs the server in debug mode.
"""
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from routes.main import bp as main_bp

app = Flask(__name__)
app.register_blueprint(main_bp)

# Handle HTTP exceptions (e.g., 404, 403, etc.)
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    if request.accept_mimetypes.accept_json:
        return jsonify({'error': e.name, 'description': e.description}), e.code
    else:
        return render_template('error.html', error=e), e.code

# Handle non-HTTP exceptions (e.g., bugs, crashes)
@app.errorhandler(Exception)
def handle_generic_exception(e):
    app.logger.error(f"Unhandled Exception: {e}")
    if request.accept_mimetypes.accept_json:
        return jsonify({'error': 'Internal Server Error', 'description': str(e)}), 500
    else:
        return render_template('error.html', error=e), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

