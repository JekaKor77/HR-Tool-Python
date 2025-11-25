import secrets

from flask import Blueprint, request, jsonify, render_template, current_app
from auth.controllers import AuthManager


bp = Blueprint("auth", __name__)


def get_controller():
    return current_app.extensions["auth_manager"]


@bp.route("/csrf", methods=["GET"])
def get_csrf():
    csrf = secrets.token_urlsafe(32)
    resp = jsonify({"csrf": csrf})
    resp.set_cookie("csrf_token", csrf, secure=False, samesite="Lax")
    return resp


@bp.route("/", methods=["GET"])
def auth_page():
    return render_template("auth.html")


@bp.route("/register", methods=["POST"])
def register():
    return get_controller().register(request.json)


@bp.route("/login", methods=["POST"])
def login():
    return get_controller().login(request.json)


@bp.route("/refresh", methods=["POST"])
def refresh():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return jsonify({"error": "CSRF"}), 400

    return get_controller().refresh()


@bp.route("/logout", methods=["POST"])
def logout():
    return get_controller().logout()


@bp.route("/logout_all", methods=["POST"])
def logout_all():
    return get_controller().logout_all()


@bp.route("/login/<provider>")
def oauth_login(provider):
    return get_controller().oauth_redirect(provider)


@bp.route("/authorize/<provider>")
def oauth_callback(provider):
    return get_controller().oauth_callback(provider)

