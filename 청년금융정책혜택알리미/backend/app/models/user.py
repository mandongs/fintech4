import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    bookmarks: Mapped[list["UserBookmark"]] = relationship("UserBookmark", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    birth_date: Mapped[str | None] = mapped_column(String(10))          # YYYY-MM-DD
    annual_income: Mapped[int | None] = mapped_column(Integer)           # 만원 단위
    region_code: Mapped[str | None] = mapped_column(String(10))          # 시군구코드
    region_name: Mapped[str | None] = mapped_column(String(50))
    marriage_status: Mapped[str | None] = mapped_column(String(10))      # 미혼/기혼/이혼
    job_code: Mapped[str | None] = mapped_column(String(10))             # 직업코드
    school_code: Mapped[str | None] = mapped_column(String(10))          # 학력코드
    employment_type: Mapped[str | None] = mapped_column(String(20))      # 재직/구직/자영업/프리랜서
    persona: Mapped[str | None] = mapped_column(String(30))              # 공격적저축형/안정형 등
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserBookmark(Base):
    __tablename__ = "user_bookmarks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(50), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    notify_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship("User", back_populates="bookmarks")
    policy: Mapped["Policy"] = relationship("Policy")
