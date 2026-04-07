from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.core.database import get_db_async
from app.models.policy import Policy
from app.schemas.policy import PolicyDetail, PolicyListResponse, PolicySummary
from app.services.deadline import days_to_deadline

router = APIRouter(prefix="/api/policies", tags=["policy"])


@router.get("", response_model=PolicyListResponse)
async def list_policies(
    category: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    region_code: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db_async),
):
    stmt = select(Policy)
    if category:
        stmt = stmt.where(or_(Policy.category_main == category, Policy.category_sub == category))
    if keyword:
        stmt = stmt.where(or_(Policy.name.ilike(f"%{keyword}%"), Policy.description.ilike(f"%{keyword}%")))
    if region_code:
        stmt = stmt.where(or_(Policy.region_codes.is_(None), Policy.region_codes.ilike(f"%{region_code}%")))

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    policies = db.execute(stmt.offset((page - 1) * size).limit(size).order_by(Policy.apply_end.asc().nulls_last())).scalars().all()

    items = [
        PolicySummary(
            **{c.name: getattr(p, c.name) for c in Policy.__table__.columns},
            days_left=days_to_deadline(p.apply_end),
        )
        for p in policies
    ]
    return PolicyListResponse(total=total, items=items)


@router.get("/{policy_id}", response_model=PolicyDetail)
async def get_policy(policy_id: str, db: Session = Depends(get_db_async)):
    policy = db.execute(select(Policy).where(Policy.id == policy_id)).scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="정책을 찾을 수 없습니다.")
    db.execute(update(Policy).where(Policy.id == policy_id).values(view_count=Policy.view_count + 1))
    db.commit()
    return PolicyDetail(
        **{c.name: getattr(policy, c.name) for c in Policy.__table__.columns},
        days_left=days_to_deadline(policy.apply_end),
    )
