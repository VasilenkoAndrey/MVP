from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.models.trophy import Trophy, TrophyStatus
from app.models.session import Review
from app.core.auth import get_current_user, require_role
from app.models.user import User
from datetime import datetime
from enum import Enum


class ReviewDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REQUEST_REMEASURE = "REQUEST_REMEASURE"


router = APIRouter(prefix="/trophies/{trophy_id}/review", tags=["review"])


@router.post("")
async def create_review(
    trophy_id: int,
    decision: ReviewDecision,
    comments: str = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Create a review (only EXPERT role can do this)"""
    if current_user.role not in ("EXPERT", "ADMIN"):
        raise HTTPException(status_code=403, detail="Only experts can review trophies")

    result = await session.execute(select(Trophy).where(Trophy.id == trophy_id))
    trophy = result.scalar_one_or_none()
    if not trophy:
        raise HTTPException(status_code=404, detail="Trophy not found")

    if trophy.status not in ("SUBMITTED", "UNDER_REVIEW"):
        raise HTTPException(status_code=400, detail="Trophy cannot be reviewed in current status")

    # Create or update review
    existing = await session.execute(
        select(Review).where(Review.trophy_id == trophy_id)
    )
    review = existing.scalar_one_or_none()

    if review:
        review.decision = decision.value
        review.comments = comments
        review.review_date = datetime.utcnow()
    else:
        review = Review(
            trophy_id=trophy_id,
            expert_id=current_user.id,
            decision=decision.value,
            comments=comments,
            review_date=datetime.utcnow(),
        )
        session.add(review)

    # Update trophy status based on decision
    if decision == ReviewDecision.APPROVED:
        trophy.status = TrophyStatus.APPROVED
    elif decision == ReviewDecision.REJECTED:
        trophy.status = TrophyStatus.REJECTED
    elif decision == ReviewDecision.REQUEST_REMEASURE:
        trophy.status = TrophyStatus.REMEASURE_REQUIRED

    await session.commit()
    await session.refresh(review)
    return {"status": "reviewed", "new_status": trophy.status.value}


@router.get("")
async def get_review(
    trophy_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Review).where(Review.trophy_id == trophy_id))
    review = result.scalar_one_or_none()
    if not review:
        return None
    return review


@router.post("/submit")
async def submit_for_review(
    trophy_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Submit trophy for expert review"""
    result = await session.execute(select(Trophy).where(Trophy.id == trophy_id))
    trophy = result.scalar_one_or_none()
    if not trophy:
        raise HTTPException(status_code=404, detail="Trophy not found")

    if trophy.status not in ("MEASURED",):
        raise HTTPException(status_code=400, detail="Trophy must be in MEASURED status to submit")

    trophy.status = TrophyStatus.SUBMITTED
    await session.commit()
    return {"status": "submitted", "new_status": "SUBMITTED"}
