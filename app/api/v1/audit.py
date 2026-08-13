from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_async_session
from app.models.session import AuditLog
from app.models.user import User

router = APIRouter(tags=["audit"])


@router.get("/logs")
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=200, description="Items per page"),
    trophy_id: Optional[int] = Query(None, description="Filter by trophy ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Retrieve audit logs with optional filters.
    Requires authentication.
    """
    query = select(AuditLog)

    if trophy_id is not None:
        query = query.where(AuditLog.trophy_id == trophy_id)
    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
    if action is not None:
        query = query.where(AuditLog.action == action)

    query = query.order_by(AuditLog.timestamp.desc())

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await session.execute(query)
    logs = result.scalars().all()

    return {
        "items": [
            {
                "id": log.id,
                "action": log.action,
                "details": log.details,
                "user_id": log.user_id,
                "trophy_id": log.trophy_id,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "size": size,
    }
