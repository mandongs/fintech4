"""
매칭 엔진 — 사용자 프로필 vs 정책 조건 실시간 대조
노트북의 compute_match_score 로직을 서비스 레이어로 이식.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.models.policy import Policy
from app.models.user import UserProfile
from app.services.deadline import days_to_deadline


def compute_age(birth_date: str) -> int:
    """YYYY-MM-DD → 만 나이."""
    try:
        bd = date.fromisoformat(birth_date)
        today = datetime.now(timezone.utc).date()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except Exception:
        return 0


def _age_match(policy: Policy, age: int) -> float:
    """0.0(불일치) or 1.0(일치). 나이 제한이 없으면 1.0."""
    if policy.min_age == 0 and policy.max_age == 0:
        return 1.0
    if policy.min_age == 0:
        return 1.0 if age <= policy.max_age else 0.0
    if policy.max_age == 0:
        return 1.0 if age >= policy.min_age else 0.0
    return 1.0 if policy.min_age <= age <= policy.max_age else 0.0


def _income_match(policy: Policy, annual_income: int | None) -> float:
    """소득 조건 일치 여부. 소득 미입력 시 0.5(불확실)."""
    if policy.earn_min == 0 and policy.earn_max == 0:
        return 1.0
    if annual_income is None:
        return 0.5
    if policy.earn_min == 0:
        return 1.0 if annual_income <= policy.earn_max else 0.0
    if policy.earn_max == 0:
        return 1.0 if annual_income >= policy.earn_min else 0.0
    return 1.0 if policy.earn_min <= annual_income <= policy.earn_max else 0.0


def _region_match(policy: Policy, region_code: str | None) -> float:
    """지역 조건 일치. region_codes가 None이면 전국 대상."""
    if not policy.region_codes:
        return 1.0
    if not region_code:
        return 0.5
    codes = {c.strip() for c in policy.region_codes.split(",") if c.strip()}
    # 시도 코드(앞 2자리) 매칭도 허용
    return 1.0 if (region_code in codes or region_code[:2] in {c[:2] for c in codes}) else 0.0


def _code_match(policy_codes: str | None, user_code: str | None) -> float:
    """직업/학력 코드 일치. 정책에 코드 제한이 없으면 1.0."""
    if not policy_codes:
        return 1.0
    if not user_code:
        return 0.5
    codes = {c.strip() for c in policy_codes.split(",") if c.strip()}
    return 1.0 if user_code in codes else 0.0


def _marriage_match(policy: Policy, marriage_status: str | None) -> float:
    if not policy.marriage_code or policy.marriage_code == "0055003":  # 제한없음
        return 1.0
    if not marriage_status:
        return 0.5
    # 0055001=미혼, 0055002=기혼, 0055003=제한없음
    code_map = {"미혼": "0055001", "기혼": "0055002"}
    user_code = code_map.get(marriage_status, "")
    return 1.0 if user_code == policy.marriage_code else 0.0


def _deadline_score(policy: Policy) -> float:
    """
    마감 임박도 점수 (추천 우선순위 보정).
    D-7 이내 → 가중치 up, 마감 → 0.0, 연중 → 0.7
    """
    days = days_to_deadline(policy.apply_end)
    if days is None:
        return 0.7      # 연중/상시
    if days < 0:
        return 0.0      # 마감됨
    if days <= 3:
        return 1.0
    if days <= 7:
        return 0.9
    if days <= 30:
        return 0.8
    return 0.7


def compute_match_score(profile: UserProfile, policy: Policy) -> float:
    """
    종합 매칭 점수 0.0 ~ 1.0.
    가중치: 나이(30%) + 소득(25%) + 지역(20%) + 직업(10%) + 학력(5%) + 결혼(5%) + 마감(5%)
    """
    age = compute_age(profile.birth_date) if profile.birth_date else 0
    income = profile.annual_income

    age_s = _age_match(policy, age)
    # 나이가 0이면 (미입력) 불확실
    if age == 0:
        age_s = 0.5

    score = (
        age_s * 0.30
        + _income_match(policy, income) * 0.25
        + _region_match(policy, profile.region_code) * 0.20
        + _code_match(policy.job_codes, profile.job_code) * 0.10
        + _code_match(policy.school_codes, profile.school_code) * 0.05
        + _marriage_match(policy, profile.marriage_status) * 0.05
        + _deadline_score(policy) * 0.05
    )
    return round(score, 4)


def categorize_persona(profile: UserProfile) -> str:
    """사용자 페르소나 자동 분류."""
    age = compute_age(profile.birth_date) if profile.birth_date else 0
    income = profile.annual_income or 0
    emp = profile.employment_type or ""

    if emp in ("재직",) and income >= 3000:
        if income >= 5000:
            return "고소득재직형"
        return "안정재직형"
    if emp in ("구직", "미취업"):
        return "구직활성형"
    if emp == "자영업":
        return "자영업형"
    if age <= 25:
        return "사회초년생형"
    if income <= 2400:
        return "저소득지원형"
    return "공격적저축형"


def filter_and_rank_policies(profile: UserProfile, policies: list[Policy], top_n: int = 20) -> list[tuple[Policy, float]]:
    """
    정책 리스트를 매칭 점수 기준 내림차순으로 정렬.
    마감된 정책(score=0.0 중 마감)은 제외.
    """
    scored = []
    for p in policies:
        score = compute_match_score(profile, p)
        days = days_to_deadline(p.apply_end)
        if days is not None and days < 0:
            continue  # 마감 제외
        scored.append((p, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]
