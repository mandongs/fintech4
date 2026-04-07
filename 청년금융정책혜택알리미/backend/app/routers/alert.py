from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.database import get_db_async
from app.core.deps import get_current_user
from app.models.policy import Policy
from app.models.user import User, UserBookmark
from app.schemas.policy import PolicySummary
from app.schemas.user import BookmarkResponse
from app.services.deadline import days_to_deadline

router = APIRouter(prefix="/api", tags=["alert"])


@router.get("/alerts", response_model=list[PolicySummary])
async def get_alerts(
    days: int = Query(default=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    today = datetime.now(timezone.utc).date()
    deadline = today + timedelta(days=days)

    policies = db.execute(
        select(Policy).where(
            and_(Policy.apply_end.isnot(None), Policy.apply_end >= str(today), Policy.apply_end <= str(deadline))
        ).order_by(Policy.apply_end)
    ).scalars().all()

    return [
        PolicySummary(
            **{c.name: getattr(p, c.name) for c in Policy.__table__.columns},
            days_left=days_to_deadline(p.apply_end),
        )
        for p in policies
    ]


@router.get("/bookmarks", response_model=list[BookmarkResponse])
async def get_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    rows = db.execute(
        select(UserBookmark, Policy)
        .join(Policy, UserBookmark.policy_id == Policy.id)
        .where(UserBookmark.user_id == current_user.id)
        .order_by(UserBookmark.created_at.desc())
    ).fetchall()

    return [
        BookmarkResponse(
            id=bm.id,
            policy_id=bm.policy_id,
            policy_name=policy.name,
            notify_enabled=bm.notify_enabled,
            created_at=bm.created_at,
            days_left=days_to_deadline(policy.apply_end),
        )
        for bm, policy in rows
    ]


@router.post("/bookmarks/{policy_id}", status_code=201)
async def add_bookmark(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    if not db.execute(select(Policy).where(Policy.id == policy_id)).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="존재하지 않는 정책입니다.")

    existing = db.execute(
        select(UserBookmark).where(and_(UserBookmark.user_id == current_user.id, UserBookmark.policy_id == policy_id))
    ).scalar_one_or_none()
    if existing:
        return {"message": "이미 북마크된 정책입니다."}

    db.add(UserBookmark(user_id=current_user.id, policy_id=policy_id))
    db.commit()
    return {"message": "북마크가 등록되었습니다."}


@router.delete("/bookmarks/{policy_id}", status_code=200)
async def remove_bookmark(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    bm = db.execute(
        select(UserBookmark).where(and_(UserBookmark.user_id == current_user.id, UserBookmark.policy_id == policy_id))
    ).scalar_one_or_none()
    if not bm:
        raise HTTPException(status_code=404, detail="북마크가 존재하지 않습니다.")
    db.delete(bm)
    db.commit()
    return {"message": "북마크가 해제되었습니다."}
