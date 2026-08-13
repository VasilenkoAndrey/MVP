from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin


class MeasurementSession(Base, TimestampMixin):
    """Tracks a measurement session (user + trophy + session state)"""
    __tablename__ = "measurement_sessions"

    id = Column(Integer, primary_key=True, index=True)
    trophy_id = Column(Integer, ForeignKey("trophies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    status = Column(String(20), default="ACTIVE")
    started_at = Column(DateTime, nullable=False)


class Review(Base, TimestampMixin):
    """Expert review of a trophy measurement"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    trophy_id = Column(Integer, ForeignKey("trophies.id"), nullable=False)
    expert_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String(20), nullable=False)  # APPROVED, REJECTED, REQUEST_REMEASURE
    comments = Column(Text, nullable=True)
    review_date = Column(DateTime, nullable=False)

    # Relationships
    trophy = relationship("Trophy", back_populates="review")
    expert = relationship("User")


class AuditLog(Base, TimestampMixin):
    """Audit log for all critical operations"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    trophy_id = Column(Integer, ForeignKey("trophies.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., LOGIN, UPLOAD, CREATE_TROPHY, CALIBRATION, MEASUREMENT
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    trophy = relationship("Trophy", back_populates="audit_logs")


class File(Base, TimestampMixin):
    """Generic file storage metadata"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
