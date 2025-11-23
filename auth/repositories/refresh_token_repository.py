
from datetime import datetime
from sqlalchemy import update, select

from auth.exceptions import AuthError
from db.models import RefreshToken
from auth.utils import hash_token
from db.session import sync_session_factory


class RefreshTokenRepository:
    @staticmethod
    def create_refresh_token(user_id: str, token: str, expires_at: datetime):
        try:
            with sync_session_factory() as session:
                rt = RefreshToken(
                    user_id=user_id,
                    token=hash_token(token),
                    expires_at=expires_at
                )
                session.add(rt)
                session.commit()
                session.refresh(rt)
                return rt
        except Exception as e:
            raise AuthError("Failed to store refresh token") from e

    @staticmethod
    def get_token(token: str):
        try:
            hashed = hash_token(token)
            with sync_session_factory() as session:
                q = select(RefreshToken).where(RefreshToken.token == hashed)
                result = session.execute(q)
                return result.scalar_one_or_none()
        except Exception as e:
            raise AuthError("Failed to load refresh token") from e

    @staticmethod
    def revoke(token: str):
        try:
            hashed = hash_token(token)
            with sync_session_factory() as session:
                q = select(RefreshToken).where(RefreshToken.token == hashed)
                result = session.execute(q)
                rt = result.scalar_one_or_none()
                if rt:
                    rt.revoked = True
                    session.commit()
        except Exception as e:
            raise AuthError("Failed to revoke refresh token") from e

    @staticmethod
    def revoke_all_for_user(user_id: str):
        try:
            with sync_session_factory() as session:
                q = update(RefreshToken).where(
                    RefreshToken.user_id == user_id
                ).values(revoked=True)
                session.execute(q)
                session.commit()
        except Exception as e:
            raise AuthError("Failed to revoke all refresh tokens") from e