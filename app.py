"""
Entry point for the QR code generator Flask application.

Registers Blueprints for route handling and runs the server in debug mode.
"""
from flask import Flask
from routes.main import bp as main_bp

app = Flask(__name__)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

