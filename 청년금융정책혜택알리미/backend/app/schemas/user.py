from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ─── Profile ────────────────────────────────────────────────────────────────

class ProfileUpsertRequest(BaseModel):
    birth_date: str | None = None          # YYYY-MM-DD
    annual_income: int | None = None       # 만원
    region_code: str | None = None
    region_name: str | None = None
    marriage_status: str | None = None     # 미혼/기혼/이혼
    job_code: str | None = None
    school_code: str | None = None
    employment_type: str | None = None     # 재직/구직/자영업/프리랜서


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    birth_date: str | None
    annual_income: int | None
    region_code: str | None
    region_name: str | None
    marriage_status: str | None
    job_code: str | None
    school_code: str | None
    employment_type: str | None
    persona: str | None
    updated_at: datetime

    class Config:
        from_attributes = True


class BookmarkResponse(BaseModel):
    id: str
    policy_id: str
    policy_name: str
    notify_enabled: bool
    created_at: datetime
    days_left: int | None = None   # D-day (None = 상시/연중)

    class Config:
        from_attributes = True
