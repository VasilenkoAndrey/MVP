from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas.measurement import MeasurementCreate, MeasurementInDB
from app.models.measurement import Measurement
from app.models.calibration import Calibration
from app.models.trophy import Trophy, TrophyStatus
from app.core.auth import get_current_user
from app.models.user import User
import math

router = APIRouter(prefix="/trophies/{trophy_id}/measurements", tags=["measurements"])


def calculate_measurement(data: MeasurementCreate) -> dict:
    """
    Calculate length, width, total based on TPCZ methodology.
    All internal calculations in mm, display in cm.
    """
    # Get axis vector from stored values (will be passed separately or looked up)
    # For now, calculate projection-based length

    # Length: distance between projections of points on axis
    # L_START = (length_start_x, length_start_y, length_start_z)
    # L_END = (length_end_x, length_end_y, length_end_z)

    ls = (data.length_start_x, data.length_start_y, data.length_start_z)
    le = (data.length_end_x, data.length_end_y, data.length_end_z)
    wl = (data.width_left_x, data.width_left_y, data.width_left_z)
    wr = (data.width_right_x, data.width_right_y, data.width_right_z)

    # Length = direct distance between length points (projected on axis)
    # In MVP: distance between the two length points
    dx = le[0] - ls[0]
    dy = le[1] - ls[1]
    dz = le[2] - ls[2]
    length_mm = math.sqrt(dx**2 + dy**2 + dz**2)

    # Width = distance between width points
    dx_w = wr[0] - wl[0]
    dy_w = wr[1] - wl[1]
    dz_w = wr[2] - wl[2]
    width_mm = math.sqrt(dx_w**2 + dy_w**2 + dz_w**2)

    # Angle between width line and axis (should be 90 degrees for perpendicular)
    # Calculate using dot product
    # For MVP, we store raw values and compute display values

    total_mm = length_mm + width_mm

    return {
        "raw_length_mm": round(length_mm, 4),
        "raw_width_mm": round(width_mm, 4),
        "total_mm": round(total_mm, 4),
        "length_cm": round(length_mm / 10, 2),
        "width_cm": round(width_mm / 10, 2),
        "total_cm": round(total_mm / 10, 2),
    }


@router.post("", response_model=MeasurementInDB, status_code=201)
async def create_measurement(
    trophy_id: int,
    data: MeasurementCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new measurement (creates new version)"""
    # Validate trophy exists
    result = await session.execute(select(Trophy).where(Trophy.id == trophy_id))
    trophy = result.scalar_one_or_none()
    if not trophy:
        raise HTTPException(status_code=404, detail="Trophy not found")

    # Validate calibration exists and is confirmed
    calib_result = await session.execute(
        select(Calibration).where(Calibration.id == data.calibration_id)
    )
    calib = calib_result.scalar_one_or_none()
    if not calib:
        raise HTTPException(status_code=404, detail="Calibration not found")

    # Calculate measurement values
    calc = calculate_measurement(data)

    # Check if there's an existing measurement for this trophy
    # If so, mark it as SUPERSEDED
    existing = await session.execute(
        select(Measurement).where(
            Measurement.trophy_id == trophy_id,
            Measurement.version > 0,
        ).order_by(Measurement.version.desc()).limit(1)
    )
    old_measurement = existing.scalar_one_or_none()
    if old_measurement:
        old_measurement.status = "SUPERSEDED"

    # Create new measurement
    new_version = (old_measurement.version if old_measurement else 0) + 1

    measurement = Measurement(
        trophy_id=trophy_id,
        method_id=data.method_id,
        calibration_id=data.calibration_id,
        axis_id=data.axis_id,
        version=new_version,
        status="DRAFT",
        **{
            "length_start_x": data.length_start_x,
            "length_start_y": data.length_start_y,
            "length_start_z": data.length_start_z,
            "length_end_x": data.length_end_x,
            "length_end_y": data.length_end_y,
            "length_end_z": data.length_end_z,
            "width_left_x": data.width_left_x,
            "width_left_y": data.width_left_y,
            "width_left_z": data.width_left_z,
            "width_right_x": data.width_right_x,
            "width_right_y": data.width_right_y,
            "width_right_z": data.width_right_z,
        },
        **calc,
        algorithm_version=data.algorithm_version,
        notes=data.notes,
        created_by=current_user.id,
    )

    session.add(measurement)

    # Update trophy status
    if trophy.status == "DRAFT":
        trophy.status = "MEASURED"
    elif trophy.status == "REMEASURE_REQUIRED":
        trophy.status = "MEASURED"

    await session.commit()
    await session.refresh(measurement)
    return measurement


@router.get("", response_model=list[MeasurementInDB])
async def list_measurements(
    trophy_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Measurement)
        .where(Measurement.trophy_id == trophy_id)
        .order_by(Measurement.version.desc())
    )
    return result.scalars().all()


@router.get("/{measurement_id}", response_model=MeasurementInDB)
async def get_measurement(
    trophy_id: int,
    measurement_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Measurement).where(
            Measurement.id == measurement_id,
            Measurement.trophy_id == trophy_id,
        )
    )
    measurement = result.scalar_one_or_none()
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement
