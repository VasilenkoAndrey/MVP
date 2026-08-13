from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CalibrationMode(str, Enum):
    UNIT = "UNIT"
    TWO_POINTS = "TWO_POINTS"


class CalibrationCreate(BaseModel):
    trophy_id: int
    mode: CalibrationMode
    unit_name: Optional[str] = None
    point1_x: float
    point1_y: float
    point1_z: float
    point2_x: float
    point2_y: float
    point2_z: float
    actual_distance_mm: float
    is_confirmed: bool = False


class CalibrationInDB(BaseModel):
    id: int
    trophy_id: int
    mode: CalibrationMode
    unit_name: Optional[str] = None
    point1_x: float
    point1_y: float
    point1_z: float
    point2_x: float
    point2_y: float
    point2_z: float
    actual_distance_mm: Optional[float] = None
    scale_factor: float
    is_confirmed: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class MeasurementPointCreate(BaseModel):
    trophy_id: int
    point_type: str
    x: float
    y: float
    z: float
    mesh_face_id: Optional[int] = None


class MeasurementAxisCreate(BaseModel):
    trophy_id: int
    start_x: float
    start_y: float
    start_z: float
    end_x: float
    end_y: float
    end_z: float


class MeasurementCreate(BaseModel):
    """Create a measurement"""
    trophy_id: int
    method_id: int = 1
    calibration_id: int
    axis_id: int
    # Points
    length_start_x: float
    length_start_y: float
    length_start_z: float
    length_end_x: float
    length_end_y: float
    length_end_z: float
    width_left_x: float
    width_left_y: float
    width_left_z: float
    width_right_x: float
    width_right_y: float
    width_right_z: float
    algorithm_version: str = "1.0.0"
    notes: Optional[str] = None


class MeasurementInDB(BaseModel):
    id: int
    trophy_id: int
    method_id: int
    calibration_id: int
    axis_id: int
    version: int
    status: str
    length_start_x: float
    length_start_y: float
    length_start_z: float
    length_end_x: float
    length_end_y: float
    length_end_z: float
    width_left_x: float
    width_left_y: float
    width_left_z: float
    width_right_x: float
    width_right_y: float
    width_right_z: float
    raw_length_mm: float
    raw_width_mm: float
    total_mm: float
    length_cm: float
    width_cm: float
    total_cm: float
    width_angle_deg: float
    angle_deviation_deg: float
    algorithm_version: str
    notes: Optional[str]
    created_by: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
