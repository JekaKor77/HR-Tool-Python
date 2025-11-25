from flask import Flask, jsonify
from flask_cors import CORS

from auth.controllers import AuthManager
from auth.exceptions import AuthError, CSRFError, InvalidCredentials, UserAlreadyExists, OAuthError
from auth.services.auth_service import AuthService
from routes.candidates import bp as candidate_bp
from routes.comparison import bp as comparison_bp
from routes.export import bp as export_bp
from routes.auth import bp as auth_bp
from app_config import settings


def create_app():
    app = Flask(__name__)
    app.secret_key = settings.SECRET_KEY
    app.config.from_object(settings)
    CORS(app)

    AuthManager(app)

    app.register_blueprint(candidate_bp)
    app.register_blueprint(comparison_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.errorhandler(AuthError)
    def handle_auth_error(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return jsonify({"error": "CSRF validation failed"}), 403

    @app.errorhandler(InvalidCredentials)
    def handle_invalid_credentials(e):
        return jsonify({"error": "Invalid email or password"}), 401

    @app.errorhandler(UserAlreadyExists)
    def handle_user_exists(e):
        return jsonify({"error": "User with this email already exists"}), 409

    @app.errorhandler(OAuthError)
    def handle_oauth_error(e):
        return jsonify({"error": str(e)}), 400

    return app


if __name__ == '__main__':
    app = create_app()

    print(f"HR Tool is running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
