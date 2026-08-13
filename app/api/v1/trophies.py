from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas.trophy import TrophyCreate, TrophyUpdate, TrophyInDB
from app.models.trophy import Trophy
from app.core.auth import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/trophies", tags=["trophies"])


@router.post("", response_model=TrophyInDB, status_code=status.HTTP_201_CREATED)
async def create_trophy(
    data: TrophyCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    new_trophy = Trophy(
        **data.model_dump(),
        owner_id=current_user.id,
        status="DRAFT",
        hunt_date=data.hunt_date,
    )
    session.add(new_trophy)
    await session.commit()
    await session.refresh(new_trophy)
    return new_trophy


@router.get("", response_model=list[TrophyInDB])
async def list_trophies(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    # Users see their own trophies, admins/measurers/experts see all
    if current_user.role in ("EXPERT", "ADMIN", "MEASURER"):
        result = await session.execute(select(Trophy).order_by(Trophy.created_at.desc()))
    else:
        result = await session.execute(
            select(Trophy).where(Trophy.owner_id == current_user.id).order_by(Trophy.created_at.desc())
        )
    return result.scalars().all()


@router.get("/{trophy_id}", response_model=TrophyInDB)
async def get_trophy(
    trophy_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Trophy).where(Trophy.id == trophy_id))
    trophy = result.scalar_one_or_none()
    if not trophy:
        raise HTTPException(status_code=404, detail="Trophy not found")
    return trophy


@router.put("/{trophy_id}", response_model=TrophyInDB)
async def update_trophy(
    trophy_id: int,
    data: TrophyUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Trophy).where(Trophy.id == trophy_id))
    trophy = result.scalar_one_or_none()
    if not trophy:
        raise HTTPException(status_code=404, detail="Trophy not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(trophy, key, value)

    await session.commit()
    await session.refresh(trophy)
    return trophy


@router.delete("/{trophy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trophy(
    trophy_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Trophy).where(Trophy.id == trophy_id))
    trophy = result.scalar_one_or_none()
    if not trophy:
        raise HTTPException(status_code=404, detail="Trophy not found")
    await session.delete(trophy)
    await session.commit()
