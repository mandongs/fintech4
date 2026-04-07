import uuid
from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)           # plcyNo
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    keyword: Mapped[str | None] = mapped_column(String(200))
    category_main: Mapped[str | None] = mapped_column(String(50), index=True)  # 대분류
    category_sub: Mapped[str | None] = mapped_column(String(50))               # 소분류
    description: Mapped[str | None] = mapped_column(Text)
    support_content: Mapped[str | None] = mapped_column(Text)
    apply_method: Mapped[str | None] = mapped_column(Text)
    apply_url: Mapped[str | None] = mapped_column(String(500))
    ref_url1: Mapped[str | None] = mapped_column(String(500))
    ref_url2: Mapped[str | None] = mapped_column(String(500))

    # 자격 조건 (정형화)
    min_age: Mapped[int] = mapped_column(Integer, default=0)    # 0 = 제한없음
    max_age: Mapped[int] = mapped_column(Integer, default=0)
    earn_min: Mapped[int] = mapped_column(Integer, default=0)   # 만원
    earn_max: Mapped[int] = mapped_column(Integer, default=0)
    region_codes: Mapped[str | None] = mapped_column(Text)      # 콤마구분 시군구코드, NULL=전국
    marriage_code: Mapped[str | None] = mapped_column(String(10))
    job_codes: Mapped[str | None] = mapped_column(Text)
    school_codes: Mapped[str | None] = mapped_column(Text)

    # 신청 기간
    apply_start: Mapped[date | None] = mapped_column(Date, index=True)
    apply_end: Mapped[date | None] = mapped_column(Date, index=True)
    apply_period_text: Mapped[str | None] = mapped_column(String(100))  # 원본 텍스트 (연중 등)
    biz_start: Mapped[date | None] = mapped_column(Date)
    biz_end: Mapped[date | None] = mapped_column(Date)

    # 기관
    supervise_inst: Mapped[str | None] = mapped_column(String(100))
    supervise_inst_code: Mapped[str | None] = mapped_column(String(20))
    operate_inst: Mapped[str | None] = mapped_column(String(100))

    # 지원 규모
    support_scale: Mapped[int | None] = mapped_column(Integer)   # 지원 인원
    is_scale_limited: Mapped[bool] = mapped_column(Boolean, default=False)

    view_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding_id: Mapped[int | None] = mapped_column(Integer)    # FAISS 인덱스 id
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(50), nullable=False)
    days_left: Mapped[int] = mapped_column(Integer)   # D-7, D-3, D-1
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
