from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin
import enum


class TrophyStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    MEASURED = "MEASURED"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REMEASURE_REQUIRED = "REMEASURE_REQUIRED"


class AnimalSpecies(Base, TimestampMixin):
    __tablename__ = "animal_species"

    id = Column(Integer, primary_key=True, index=True)
    name_ru = Column(String(255), nullable=False)
    name_la = Column(String(255), nullable=False)
    is_active = Column("is_active", Boolean, default=True)


class TrophyModel(Base, TimestampMixin):
    """Stores uploaded STL file metadata"""
    __tablename__ = "trophy_models"

    id = Column(Integer, primary_key=True, index=True)
    trophy_id = Column(Integer, ForeignKey("trophies.id"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    vertex_count = Column(Integer, nullable=True)
    triangle_count = Column(Integer, nullable=True)
    bounding_box_min_x = Column(Float, nullable=True)
    bounding_box_min_y = Column(Float, nullable=True)
    bounding_box_min_z = Column(Float, nullable=True)
    bounding_box_max_x = Column(Float, nullable=True)
    bounding_box_max_y = Column(Float, nullable=True)
    bounding_box_max_z = Column(Float, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    trophy = relationship("Trophy", back_populates="model")
    uploader = relationship("User", foreign_keys=[uploaded_by])


class Trophy(Base, TimestampMixin):
    __tablename__ = "trophies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    species_id = Column(Integer, ForeignKey("animal_species.id"), nullable=True)
    hunt_date = Column(DateTime, nullable=False)
    location = Column(String(500), nullable=False)  # место добычи
    owner_name = Column(String(255), nullable=False)  # владелец/автор
    status = Column(String(20), nullable=False, default="DRAFT")
    owner_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text, nullable=True)
    version = Column(Integer, default=1)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="trophies")
    model = relationship("TrophyModel", back_populates="trophy", uselist=False)
    calibrations = relationship("Calibration", back_populates="trophy")
    measurement_axes = relationship("MeasurementAxis", back_populates="trophy")
    measurements = relationship("Measurement", back_populates="trophy")
    review = relationship("Review", back_populates="trophy", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="trophy")
