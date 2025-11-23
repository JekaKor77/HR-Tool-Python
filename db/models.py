import enum
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import String, DateTime, Boolean, Float, Enum, Text, ForeignKey
from db.base import Base, TimestampMixin


class RolesEnum(str, enum.Enum):
    user = "user"
    interviewer = "interviewer"
    admin = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(PG_UUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(120))
    last_name: Mapped[Optional[str]] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped["RolesEnum"] = mapped_column(Enum(RolesEnum), default=RolesEnum.interviewer, nullable=False)
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50))
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    user: Mapped["User"] = relationship(backref="refresh_tokens")

    token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(PG_UUID, primary_key=True, default=uuid.uuid4)
    first_name: Mapped[Optional[str]] = mapped_column(String(120))
    last_name: Mapped[Optional[str]] = mapped_column(String(120))
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    cv_path: Mapped[Optional[str]] = mapped_column(String(1024))
    interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    evaluation_summary: Mapped[Optional[str]] = mapped_column(Text)
    model_recommendation: Mapped[Optional[str]] = mapped_column(Text)

    model_raw: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    quiz: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    responses: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    score: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), index=True, default="new")

