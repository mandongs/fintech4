from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_async
from app.core.deps import get_current_user
from app.models.financial_product import FinancialProduct
from app.models.policy import Policy
from app.models.user import User, UserProfile
from app.schemas.financial import FinancialListResponse, FinancialProductSummary
from app.schemas.policy import PolicyListResponse, PolicySummary
from app.services.deadline import days_to_deadline
from app.services.matching import filter_and_rank_policies
from app.services.recommendation import recommend_financial_products

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


def _get_profile_or_400(user_id: str, db: Session) -> UserProfile:
    profile = db.execute(select(UserProfile).where(UserProfile.user_id == user_id)).scalar_one_or_none()
    if not profile or not profile.birth_date:
        raise HTTPException(status_code=400, detail="프로필을 먼저 등록해주세요. (생년월일 필수)")
    return profile


@router.get("/policies", response_model=PolicyListResponse)
async def recommend_policies(
    top_n: int = Query(default=20, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    profile = _get_profile_or_400(current_user.id, db)
    policies = db.execute(select(Policy)).scalars().all()
    ranked = filter_and_rank_policies(profile, list(policies), top_n=top_n)

    items = [
        PolicySummary(
            **{c.name: getattr(p, c.name) for c in Policy.__table__.columns},
            days_left=days_to_deadline(p.apply_end),
            match_score=score,
        )
        for p, score in ranked
    ]
    return PolicyListResponse(total=len(items), items=items)


@router.get("/financial", response_model=FinancialListResponse)
async def recommend_financial(
    product_type: str | None = Query(default=None),
    top_n: int = Query(default=10, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    profile = _get_profile_or_400(current_user.id, db)
    products = db.execute(select(FinancialProduct)).scalars().all()
    recommended = recommend_financial_products(profile, list(products), product_type=product_type, top_n=top_n)

    items = [
        FinancialProductSummary(
            **{c.name: getattr(p, c.name) for c in FinancialProduct.__table__.columns},
            match_reason=reason,
        )
        for p, reason in recommended
    ]
    return FinancialListResponse(total=len(items), items=items)
