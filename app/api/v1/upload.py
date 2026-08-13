from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.models.trophy import Trophy, TrophyStatus, TrophyModel
from app.core.auth import get_current_user
from app.models.user import User
from app.services.file_validator import validate_stl
import os
import uuid
import stl
import numpy as np
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/trophies/{trophy_id}/model", tags=["trophies"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_model(
    trophy_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    # Check trophy exists
    result = await session.execute(select(Trophy).where(Trophy.id == trophy_id))
    trophy = result.scalar_one_or_none()
    if not trophy:
        raise HTTPException(status_code=404, detail="Trophy not found")

    # Validate file type
    if not file.filename.lower().endswith(".stl"):
        raise HTTPException(status_code=400, detail="Only STL files are accepted")

    # Check MIME type
    if file.content_type not in ("application/sla", "application/stl", "model/stl", "text/plain"):
        raise HTTPException(status_code=400, detail="Invalid MIME type for STL file")

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Check size limit
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB} MB",
        )

    # Parse STL to get mesh info
    mesh = stl.Mesh.from_bytes(content)
    vertex_count = len(mesh.vectors)
    triangle_count = len(mesh)

    # Calculate bounding box
    min_coords = mesh.vectors.min(axis=(0, 1))
    max_coords = mesh.vectors.max(axis=(0, 1))

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}.stl"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    # Save to DB
    trophy_model = TrophyModel(
        trophy_id=trophy_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_size_bytes=file_size,
        mime_type=file.content_type,
        vertex_count=vertex_count,
        triangle_count=triangle_count,
        bounding_box_min_x=min_coords[0],
        bounding_box_min_y=min_coords[1],
        bounding_box_min_z=min_coords[2],
        bounding_box_max_x=max_coords[0],
        bounding_box_max_y=max_coords[1],
        bounding_box_max_z=max_coords[2],
        uploaded_by=current_user.id,
    )
    session.add(trophy_model)

    # Update trophy status
    if trophy.status == "DRAFT":
        trophy.status = "MEASURED"

    await session.commit()
    await session.refresh(trophy_model)

    return trophy_model


@router.get("")
async def get_model(
    trophy_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(TrophyModel).where(TrophyModel.trophy_id == trophy_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="No model uploaded for this trophy")
    return model
