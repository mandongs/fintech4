from datetime import date, datetime

from pydantic import BaseModel


class PolicySummary(BaseModel):
    id: str
    name: str
    category_main: str | None
    category_sub: str | None
    description: str | None
    support_content: str | None
    apply_url: str | None
    min_age: int
    max_age: int
    apply_start: date | None
    apply_end: date | None
    apply_period_text: str | None
    supervise_inst: str | None
    view_count: int
    days_left: int | None = None      # D-day (None=상시/미정)
    match_score: float | None = None  # 매칭 점수 0~1

    class Config:
        from_attributes = True


class PolicyDetail(PolicySummary):
    keyword: str | None
    earn_min: int
    earn_max: int
    region_codes: str | None
    marriage_code: str | None
    job_codes: str | None
    school_codes: str | None
    apply_method: str | None
    ref_url1: str | None
    ref_url2: str | None
    biz_start: date | None
    biz_end: date | None
    operate_inst: str | None
    support_scale: int | None
    is_scale_limited: bool


class PolicyListResponse(BaseModel):
    total: int
    items: list[PolicySummary]


class PolicyFilterParams(BaseModel):
    category: str | None = None
    keyword: str | None = None
    region_code: str | None = None
    page: int = 1
    size: int = 20
