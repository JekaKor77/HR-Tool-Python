import secrets
from datetime import datetime, timedelta

import jwt
from flask import request

from app_config import settings
from auth.exceptions import CSRFError, AuthError
from auth.repositories.refresh_token_repository import RefreshTokenRepository
from auth.utils import create_access_token, create_refresh_token


class TokenService:
    def check_csrf(self):
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-TOKEN")
        print("CSRF check: cookie =", csrf_cookie, ", header =", csrf_header)
        if csrf_cookie != csrf_header:
            print("CSRF mismatch!")
            raise CSRFError()

    def get_refresh_from_request(self):
        refresh = request.cookies.get("refresh_token")
        print("Refresh token from request:", refresh)
        return refresh

    def create_access(self, user_id: str):
        return create_access_token({"sub": user_id})

    def issue_refresh(self, user_id: str):
        token = create_refresh_token({"sub": user_id})

        RefreshTokenRepository.create_refresh_token(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return token

    def validate_refresh(self):
        refresh = request.cookies.get("refresh_token")
        if not refresh:
            raise AuthError("refresh_token required")

        try:
            payload = jwt.decode(
                refresh,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise AuthError("Refresh token expired")
        except jwt.InvalidTokenError:
            raise AuthError("Invalid refresh token")

        db_token = RefreshTokenRepository.get_token(refresh)
        if not db_token or db_token.revoked:
            raise AuthError("Refresh token revoked")

        if payload.get("type") != "refresh":
            raise AuthError("Invalid token type")

        return payload["sub"]

    def make_csrf(self):
        return secrets.token_urlsafe(32)
