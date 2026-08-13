from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas.measurement import (
    CalibrationCreate, CalibrationInDB,
    MeasurementAxisCreate,
    MeasurementPointCreate,
)
from app.models.calibration import Calibration
from app.models.measurement import MeasurementAxis, MeasurementPoint
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/trophies/{trophy_id}", tags=["calibration"])


@router.post("/calibration", response_model=CalibrationInDB, status_code=201)
async def create_calibration(
    trophy_id: int,
    data: CalibrationCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Create calibration for a trophy"""
    calib = Calibration(
        trophy_id=trophy_id,
        **data.model_dump(exclude={"trophy_id"}),
        created_by=current_user.id,
    )
    session.add(calib)
    await session.commit()
    await session.refresh(calib)
    return calib


@router.post("/axis", response_model=MeasurementAxis, status_code=201)
async def create_axis(
    trophy_id: int,
    data: MeasurementAxisCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Create longitudinal axis for measurement"""
    axis = MeasurementAxis(
        trophy_id=trophy_id,
        **data.model_dump(exclude={"trophy_id"}),
        created_by=current_user.id,
    )

    # Normalize axis vector
    dx = data.end_x - data.start_x
    dy = data.end_y - data.start_y
    dz = data.end_z - data.start_z
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    if length > 0:
        axis.vector_x = dx / length
        axis.vector_y = dy / length
        axis.vector_z = dz / length

    session.add(axis)
    await session.commit()
    await session.refresh(axis)
    return axis


@router.post("/points", response_model=MeasurementPoint, status_code=201)
async def create_point(
    trophy_id: int,
    data: MeasurementPointCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Create a measurement point"""
    point = MeasurementPoint(
        trophy_id=trophy_id,
        **data.model_dump(exclude={"trophy_id"}),
        created_by=current_user.id,
    )
    session.add(point)
    await session.commit()
    await session.refresh(point)
    return point
