"""PDF Export router — generate and download study plan PDFs."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import io

from app.database import get_db
from app.models import User, StudyPlan
from app.auth import get_current_user
from app.services.pdf_service import generate_plan_pdf

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/pdf/{plan_id}")
async def export_plan_pdf(
    plan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StudyPlan)
        .options(selectinload(StudyPlan.sessions))
        .where(StudyPlan.id == plan_id, StudyPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    pdf_buffer = generate_plan_pdf(plan)

    return StreamingResponse(
        io.BytesIO(pdf_buffer),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="study_plan_{plan.id[:8]}.pdf"'
        },
    )
