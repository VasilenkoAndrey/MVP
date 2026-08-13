from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import TimestampMixin
from datetime import datetime


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="USER")  # USER, MEASURER, EXPERT, ADMIN
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Relationships
    trophies = relationship("Trophy", back_populates="owner", foreign_keys="Trophy.owner_id")
    measurements = relationship("Measurement", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
