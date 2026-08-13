from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.models.trophy import Trophy
from app.models.measurement import Measurement
from app.models.user import User
from app.models.calibration import MeasurementMethod
from app.core.auth import get_current_user
from app.services.pdf_generator import generate_trophy_pdf
import os
import tempfile

router = APIRouter(prefix="/trophies", tags=["trophies"])


@router.get("/{trophy_id}/pdf", response_class=FileResponse, summary="Generate trophy PDF")
async def get_trophy_pdf(
    trophy_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Generate and return a PDF certificate for the given trophy.

    Requires authentication. Returns the PDF file for download.
    """
    # Fetch trophy
    result = await session.execute(select(Trophy).where(Trophy.id == trophy_id))
    trophy = result.scalar_one_or_none()
    if not trophy:
        raise HTTPException(status_code=404, detail="Trophy not found")

    # Fetch latest finalized measurement for this trophy
    measurement_result = await session.execute(
        select(Measurement)
        .where(Measurement.trophy_id == trophy_id, Measurement.status == "FINAL")
        .order_by(Measurement.version.desc())
        .limit(1)
    )
    measurement = measurement_result.scalar_one_or_none()
    if not measurement:
        raise HTTPException(
            status_code=404,
            detail="No finalized measurement found for this trophy",
        )

    # Fetch measurement method
    method_result = await session.execute(
        select(MeasurementMethod).where(MeasurementMethod.id == measurement.method_id)
    )
    method = method_result.scalar_one_or_none()

    # Fetch measurer name
    measurer_result = await session.execute(
        select(User).where(User.id == measurement.created_by)
    )
    measurer = measurer_result.scalar_one_or_none()
    measurer_name = f"{measurer.username} ({measurer.email})" if measurer else None

    # Prepare trophy data
    trophy_data = {
        "id": trophy.id,
        "name": trophy.name,
        "species": trophy.species_id,  # Will be formatted by consumer
        "hunt_date": trophy.hunt_date.strftime("%Y-%m-%d") if trophy.hunt_date else "N/A",
        "location": trophy.location,
        "owner_name": trophy.owner_name,
        "status": trophy.status,
        "version": trophy.version,
    }

    # Prepare measurement data
    measurement_date = measurement.created_at.strftime("%Y-%m-%d %H:%M:%S") if measurement.created_at else "N/A"
    measurement_data = {
        "method_id": measurement.method_id,
        "length_cm": measurement.length_cm,
        "width_cm": measurement.width_cm,
        "total_cm": measurement.total_cm,
        "measurement_date": measurement_date,
        "algorithm_version": measurement.algorithm_version,
    }

    # Create temp file for PDF
    fd, tmp_path = tempfile.mkstemp(suffix=".pdf", prefix=f"trophy_{trophy_id}_")
    os.close(fd)

    try:
        generate_trophy_pdf(
            trophy_data=trophy_data,
            measurement=measurement_data,
            measurer_name=measurer_name,
            output_path=tmp_path,
        )
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}",
        )

    filename = f"trophy_{trophy_id}_cert.pdf"
    return FileResponse(
        path=tmp_path,
        filename=filename,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
