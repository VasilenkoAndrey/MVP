from datetime import datetime
from sqlalchemy import func
from app.database import Base


class TimestampMixin:
    created_at = func.now()
    updated_at = func.now()
