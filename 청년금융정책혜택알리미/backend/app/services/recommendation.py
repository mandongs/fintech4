"""금융상품 추천 서비스."""

from __future__ import annotations

import re

from app.models.financial_product import FinancialProduct
from app.models.user import UserProfile
from app.services.matching import compute_age

YOUTH_KEYWORDS = ["청년", "청소년", "사회초년생", "신혼", "미취업", "구직"]
PRODUCT_TYPE_LABEL = {
    "saving": "적금",
    "deposit": "예금",
    "mortgage": "주택담보대출",
    "rent": "전세대출",
    "credit": "신용대출",
}


def _is_youth_product(product: FinancialProduct) -> bool:
    text = (product.product_name or "") + (product.target_raw or "")
    return any(kw in text for kw in YOUTH_KEYWORDS)


def _age_eligible(product: FinancialProduct, age: int) -> bool:
    if product.min_age == 0 and product.max_age == 0:
        return True
    if product.min_age and age < product.min_age:
        return False
    if product.max_age and age > product.max_age:
        return False
    return True


def _build_match_reason(product: FinancialProduct, profile: UserProfile, age: int) -> str:
    reasons = []
    if _is_youth_product(product):
        reasons.append("청년 특화 상품")
    if product.max_limit:
        limit_str = f"{product.max_limit // 10000:,}만원" if product.max_limit >= 10000 else f"{product.max_limit:,}원"
        reasons.append(f"최대 {limit_str}")
    if product.preferred_condition:
        # 우대조건에서 퍼센트 추출
        pct = re.findall(r"[\d.]+%p?", product.preferred_condition)
        if pct:
            reasons.append(f"우대금리 최대 {pct[-1]}")
    emp = profile.employment_type or ""
    if emp == "재직" and "급여" in (product.preferred_condition or ""):
        reasons.append("급여이체 우대 해당")
    return " · ".join(reasons) if reasons else PRODUCT_TYPE_LABEL.get(product.product_type, "")


def recommend_financial_products(
    profile: UserProfile,
    products: list[FinancialProduct],
    product_type: str | None = None,
    top_n: int = 10,
) -> list[tuple[FinancialProduct, str]]:
    """
    프로필에 맞는 금융상품 추천.
    Returns: (product, match_reason) 리스트
    """
    age = compute_age(profile.birth_date) if profile.birth_date else 0

    candidates = []
    for p in products:
        if product_type and p.product_type != product_type:
            continue
        if not _age_eligible(p, age):
            continue
        is_youth = _is_youth_product(p)
        reason = _build_match_reason(p, profile, age)
        candidates.append((p, reason, is_youth))

    # 청년 특화 상품 우선, 그 다음 최대한도 기준
    candidates.sort(key=lambda x: (not x[2], -(x[0].max_limit or 0)))

    return [(p, reason) for p, reason, _ in candidates[:top_n]]
