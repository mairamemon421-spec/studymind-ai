"""Agent logs router — paginated activity feed."""

from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import User, AgentLog
from app.schemas import AgentLogsResponse, AgentLogOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=AgentLogsResponse)
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Total count
    count_result = await db.execute(
        select(func.count()).select_from(AgentLog).where(AgentLog.user_id == user.id)
    )
    total = count_result.scalar() or 0

    # Paginated results
    offset = (page - 1) * page_size
    result = await db.execute(
        select(AgentLog)
        .where(AgentLog.user_id == user.id)
        .order_by(AgentLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    logs = result.scalars().all()

    return AgentLogsResponse(
        logs=[AgentLogOut.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )
