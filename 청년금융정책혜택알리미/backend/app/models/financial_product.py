from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


PRODUCT_TYPE_MAP = {
    "savingProductsSearch": "saving",       # 적금
    "depositProductsSearch": "deposit",     # 예금
    "mortgageLoanProductsSearch": "mortgage",  # 주택담보대출
    "rentHouseLoanProductsSearch": "rent",  # 전세대출
    "creditLoanProductsSearch": "credit",   # 신용대출
}


class FinancialProduct(Base):
    __tablename__ = "financial_products"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)    # {company_code}_{product_code}
    company_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    product_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # saving/deposit/mortgage/rent/credit

    join_method: Mapped[str | None] = mapped_column(String(200))         # 가입방법
    target_raw: Mapped[str | None] = mapped_column(Text)                 # 가입대상 (원본)
    preferred_condition: Mapped[str | None] = mapped_column(Text)        # 우대조건
    maturity_interest: Mapped[str | None] = mapped_column(Text)          # 만기이자
    notes: Mapped[str | None] = mapped_column(Text)                      # 유의사항

    # 파싱된 자격 조건
    is_youth_product: Mapped[bool] = mapped_column(Boolean, default=False)
    min_age: Mapped[int] = mapped_column(Integer, default=0)
    max_age: Mapped[int] = mapped_column(Integer, default=0)

    max_limit: Mapped[int | None] = mapped_column(BigInteger)            # 최대한도 (원)
    loan_limit: Mapped[int | None] = mapped_column(BigInteger)           # 대출한도
    early_repay_fee: Mapped[str | None] = mapped_column(Text)            # 중도상환수수료
    delay_rate: Mapped[str | None] = mapped_column(Text)                 # 연체이자율

    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    dcls_month: Mapped[str | None] = mapped_column(String(10))           # 공시월

    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
