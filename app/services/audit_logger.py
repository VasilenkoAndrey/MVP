import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.session import AuditLog

logger = logging.getLogger(__name__)


async def log_action(
    action: str,
    session: Optional[AsyncSession] = None,
    details: Optional[str] = None,
    user_id: Optional[int] = None,
    trophy_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Optional[AuditLog]:
    """
    Create an AuditLog record in the database.

    If no session is provided, a new one is created automatically.
    If database write fails, the action is logged to console as a fallback.

    Args:
        action: Action type (e.g., LOGIN, UPLOAD, CREATE_TROPHY)
        session: Optional existing DB session; creates new one if omitted
        details: Additional context about the action
        user_id: ID of the user who performed the action
        trophy_id: ID of the trophy involved (if any)
        ip_address: Client IP address
        user_agent: Client user-agent string

    Returns:
        The created AuditLog instance, or None if logging failed
    """
    log_entry = AuditLog(
        action=action,
        details=details,
        user_id=user_id,
        trophy_id=trophy_id,
        ip_address=ip_address,
        user_agent=user_agent,
        timestamp=datetime.now(timezone.utc),
    )

    own_session = session is None
    db_session: AsyncSession = session if session else async_session()

    try:
        if own_session:
            async with db_session as s:
                s.add(log_entry)
                await s.commit()
        else:
            db_session.add(log_entry)
            await db_session.flush()

        logger.debug(f"Audit logged: {action} by user={user_id} trophy={trophy_id}")
        return log_entry

    except Exception as e:
        logger.error(f"Failed to write audit log to DB: {e}. Falling back to console.")
        logger.warning(
            f"AUDIT [{action}] user={user_id} trophy={trophy_id} "
            f"ip={ip_address} details={details}"
        )
        if own_session:
            try:
                await db_session.close()
            except Exception:
                pass
        return None
