from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin


class MeasurementAxis(Base, TimestampMixin):
    """Longitudinal axis for the skull"""
    __tablename__ = "measurement_axes"

    id = Column(Integer, primary_key=True, index=True)
    trophy_id = Column(Integer, ForeignKey("trophies.id"), nullable=False)
    start_x = Column(Float, nullable=False)
    start_y = Column(Float, nullable=False)
    start_z = Column(Float, nullable=False)
    end_x = Column(Float, nullable=False)
    end_y = Column(Float, nullable=False)
    end_z = Column(Float, nullable=False)
    vector_x = Column(Float, nullable=True)
    vector_y = Column(Float, nullable=True)
    vector_z = Column(Float, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    trophy = relationship("Trophy", back_populates="measurement_axes")


class MeasurementPoint(Base, TimestampMixin):
    """Individual measurement points"""
    __tablename__ = "measurement_points"

    id = Column(Integer, primary_key=True, index=True)
    trophy_id = Column(Integer, ForeignKey("trophies.id"), nullable=False)
    point_type = Column(String(50), nullable=False)  # AXIS_START, AXIS_END, LENGTH_START, LENGTH_END, WIDTH_LEFT, WIDTH_RIGHT
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    mesh_face_id = Column(Integer, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))


class Measurement(Base, TimestampMixin):
    """Measurement record (versioned)"""
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    trophy_id = Column(Integer, ForeignKey("trophies.id"), nullable=False)
    method_id = Column(Integer, ForeignKey("measurement_methods.id"), nullable=False)
    calibration_id = Column(Integer, ForeignKey("calibrations.id"), nullable=False)
    axis_id = Column(Integer, ForeignKey("measurement_axes.id"), nullable=False)

    # Versioning
    version = Column(Integer, default=1)
    status = Column(String(20), default="DRAFT")  # DRAFT, FINAL, SUPERSEDED

    # Points in 3D
    length_start_x = Column(Float, nullable=False)
    length_start_y = Column(Float, nullable=False)
    length_start_z = Column(Float, nullable=False)
    length_end_x = Column(Float, nullable=False)
    length_end_y = Column(Float, nullable=False)
    length_end_z = Column(Float, nullable=False)
    width_left_x = Column(Float, nullable=False)
    width_left_y = Column(Float, nullable=False)
    width_left_z = Column(Float, nullable=False)
    width_right_x = Column(Float, nullable=False)
    width_right_y = Column(Float, nullable=False)
    width_right_z = Column(Float, nullable=False)

    # Calculated values (internal unit: mm)
    raw_length_mm = Column(Float, nullable=False)
    raw_width_mm = Column(Float, nullable=False)
    total_mm = Column(Float, nullable=False)

    # Display values
    length_cm = Column(Float, nullable=False)
    width_cm = Column(Float, nullable=False)
    total_cm = Column(Float, nullable=False)

    # Angle between width line and axis
    width_angle_deg = Column(Float, nullable=False)
    angle_deviation_deg = Column(Float, nullable=False)

    # Algorithm
    algorithm_version = Column(String(50), default="1.0.0")
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    trophy = relationship("Trophy", back_populates="measurements")
    user = relationship("User", back_populates="measurements")
