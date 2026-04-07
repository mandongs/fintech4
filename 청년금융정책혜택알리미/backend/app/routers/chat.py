from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_async
from app.core.deps import get_current_user
from app.models.policy import Policy
from app.models.user import User, UserProfile
from app.schemas.financial import ChatRequest, ChatResponse
from app.services.ai_chat import answer_question
from app.services.matching import filter_and_rank_policies

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_async),
):
    profile = db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id)).scalar_one_or_none()

    policies_for_context: list[Policy] = []
    if profile and profile.birth_date:
        all_policies = db.execute(select(Policy)).scalars().all()
        ranked = filter_and_rank_policies(profile, list(all_policies), top_n=10)
        policies_for_context = [p for p, _ in ranked]
    else:
        policies_for_context = db.execute(select(Policy).limit(10)).scalars().all()

    answer = await answer_question(
        question=body.question,
        history=body.history,
        profile=profile,
        policies_from_db=list(policies_for_context),
    )

    return ChatResponse(answer=answer)
