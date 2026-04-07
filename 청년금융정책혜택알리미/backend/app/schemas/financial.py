from __future__ import annotations

from datetime import date
from pydantic import BaseModel


class FinancialProductSummary(BaseModel):
    id: str
    company_name: str
    product_name: str
    product_type: str
    join_method: str | None
    is_youth_product: bool
    min_age: int
    max_age: int
    max_limit: int | None
    start_date: date | None
    end_date: date | None
    match_reason: str | None = None

    class Config:
        from_attributes = True


class FinancialProductDetail(FinancialProductSummary):
    target_raw: str | None
    preferred_condition: str | None
    maturity_interest: str | None
    notes: str | None
    early_repay_fee: str | None
    delay_rate: str | None
    loan_limit: int | None
    dcls_month: str | None


class FinancialListResponse(BaseModel):
    total: int
    items: list[FinancialProductSummary]


class ChatRequest(BaseModel):
    question: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    answer: str
    referenced_policy_ids: list[str] = []
