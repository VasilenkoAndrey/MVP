from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.trophy import TrophyStatus
from enum import Enum


class AnimalSpeciesCreate(BaseModel):
    name_ru: str
    name_la: str


class SpeciesInDB(AnimalSpeciesCreate):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrophyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    species_id: Optional[int] = None
    hunt_date: datetime
    location: str = Field(..., min_length=1, max_length=500)
    owner_name: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None


class TrophyUpdate(BaseModel):
    name: Optional[str] = None
    species_id: Optional[int] = None
    hunt_date: Optional[datetime] = None
    location: Optional[str] = None
    owner_name: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[TrophyStatus] = None


class TrophyInDB(TrophyCreate):
    id: int
    status: TrophyStatus
    owner_id: Optional[int]
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrophyModelInDB(BaseModel):
    id: int
    trophy_id: int
    original_filename: str
    stored_filename: str
    file_size_bytes: int
    mime_type: str
    vertex_count: Optional[int] = None
    triangle_count: Optional[int] = None
    bounding_box_min_x: Optional[float] = None
    bounding_box_min_y: Optional[float] = None
    bounding_box_min_z: Optional[float] = None
    bounding_box_max_x: Optional[float] = None
    bounding_box_max_y: Optional[float] = None
    bounding_box_max_z: Optional[float] = None
    uploaded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
