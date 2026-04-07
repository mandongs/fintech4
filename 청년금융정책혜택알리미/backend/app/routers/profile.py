from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_async
from app.core.deps import get_current_user
from app.models.user import User, UserProfile
from app.schemas.user import ProfileResponse, ProfileUpsertRequest
from app.services.matching import categorize_persona

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    profile = db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id)).scalar_one_or_none()
    if not profile:
        from datetime import datetime, timezone
        return ProfileResponse(
            id="", user_id=current_user.id,
            birth_date=None, annual_income=None, region_code=None,
            region_name=None, marriage_status=None, job_code=None,
            school_code=None, employment_type=None, persona=None,
            updated_at=datetime.now(timezone.utc),
        )
    return profile


@router.post("", response_model=ProfileResponse)
async def upsert_profile(
    body: ProfileUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    profile = db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id)).scalar_one_or_none()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(profile, field, value)

    profile.persona = categorize_persona(profile)
    db.commit()
    db.refresh(profile)
    return profile
