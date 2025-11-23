from functools import wraps
import jwt
from flask import request, jsonify, g

from app_config import settings


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=settings.JWT_ALGORITHM
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "access token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "invalid access token"}), 401

        g.current_user = payload["sub"]

        return f(*args, **kwargs)
    return wrapper
