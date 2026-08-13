from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin


class Calibration(Base, TimestampMixin):
    """Calibration for trophy model (scale factor)"""
    __tablename__ = "calibrations"

    id = Column(Integer, primary_key=True, index=True)
    trophy_id = Column(Integer, ForeignKey("trophies.id"), nullable=False)
    mode = Column(String(20), nullable=False)  # UNIT or TWO_POINTS
    unit_name = Column(String(50), nullable=True)  # for mode=UNIT
    point1_x = Column(Float, nullable=True)
    point1_y = Column(Float, nullable=True)
    point1_z = Column(Float, nullable=True)
    point2_x = Column(Float, nullable=True)
    point2_y = Column(Float, nullable=True)
    point2_z = Column(Float, nullable=True)
    actual_distance_mm = Column(Float, nullable=True)  # for TWO_POINTS mode
    scale_factor = Column(Float, nullable=False, default=1.0)
    is_confirmed = Column("is_confirmed", Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    trophy = relationship("Trophy", back_populates="calibrations")


class MeasurementMethod(Base):
    """Measurement methods (only Method 6 for MVP)"""
    __tablename__ = "measurement_methods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    metric = Column(String(50), nullable=False)  # e.g., "CRAZIUS", "BSA", etc.
    version = Column(String(20), nullable=False)
    is_active = Column("is_active", Boolean, default=True)
    requires_axis = Column("requires_axis", Boolean, default=True)
    requires_width = Column("requires_width", Boolean, default=True)
    requires_length = Column("requires_length", Boolean, default=True)
