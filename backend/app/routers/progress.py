"""Progress router — dashboard progress data."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, Subject, Exam, StudyPlan, PlanSession
from app.schemas import ProgressOut, ExamOut
from app.auth import get_current_user
from app.agents.progress_agent import ProgressAgent

router = APIRouter(prefix="/api/progress", tags=["progress"])
progress_agent = ProgressAgent()


@router.get("", response_model=ProgressOut)
async def get_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch subjects
    subj_result = await db.execute(select(Subject).where(Subject.user_id == user.id))
    subjects = subj_result.scalars().all()

    # Fetch exams
    exam_result = await db.execute(select(Exam).where(Exam.user_id == user.id))
    exams = exam_result.scalars().all()

    # Fetch all plan sessions
    plan_result = await db.execute(
        select(StudyPlan)
        .options(selectinload(StudyPlan.sessions))
        .where(StudyPlan.user_id == user.id)
    )
    plans = plan_result.scalars().all()
    all_sessions = []
    for plan in plans:
        for sess in plan.sessions:
            all_sessions.append({
                "subject_name": sess.subject_name,
                "session_date": sess.session_date.isoformat() if sess.session_date else None,
                "duration_minutes": sess.duration_minutes,
                "completed": sess.completed,
                "completed_at": sess.completed_at.isoformat() if sess.completed_at else None,
            })

    subj_dicts = [
        {"name": s.name, "mastery_score": s.mastery_score}
        for s in subjects
    ]
    exam_dicts = [
        {
            "id": e.id, "user_id": e.user_id, "subject_id": e.subject_id,
            "title": e.title, "exam_date": e.exam_date.isoformat(),
            "importance": e.importance, "notes": e.notes,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in exams
    ]

    result = await progress_agent.calculate_progress(
        sessions=all_sessions,
        subjects=subj_dicts,
        exams=exam_dicts,
        user_id=user.id,
    )

    return ProgressOut(
        streak_days=result["streak_days"],
        total_sessions_completed=result["total_sessions_completed"],
        sessions_today=result["sessions_today"],
        hours_studied_week=result["hours_studied_week"],
        readiness_scores=result["readiness_scores"],
        upcoming_exams=[ExamOut.model_validate(e) for e in exams if _is_upcoming(e)],
        overall_readiness=result["overall_readiness"],
    )


def _is_upcoming(exam) -> bool:
    from datetime import date
    return exam.exam_date >= date.today() if exam.exam_date else False
