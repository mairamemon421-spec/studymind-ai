"""Plans router — generate AI study plans and list/view them."""
from datetime import date, time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models import User, Subject, Exam, StudyPlan, PlanSession, AgentLog
from app.schemas import PlanGenerateRequest, PlanOut, SessionCompleteRequest
from app.auth import get_current_user
from app.agents.coordinator_agent import CoordinatorAgent

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.post("/generate", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
async def generate_plan(
    data: PlanGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch user's subjects and exams
    subj_result = await db.execute(select(Subject).where(Subject.user_id == user.id))
    subjects = subj_result.scalars().all()
    if not subjects:
        raise HTTPException(status_code=400, detail="Add at least one subject before generating a plan")

    exam_result = await db.execute(select(Exam).where(Exam.user_id == user.id))
    exams = exam_result.scalars().all()

    # Convert to dicts for agents
    subj_dicts = [
        {"id": s.id, "name": s.name, "difficulty": s.difficulty, "mastery_score": s.mastery_score}
        for s in subjects
    ]
    exam_dicts = [
        {"subject_id": e.subject_id, "exam_date": e.exam_date.isoformat(), "importance": e.importance, "title": e.title}
        for e in exams
    ]

    # Run coordinator agent
    coordinator = CoordinatorAgent()
    result = await coordinator.generate_plan(
        subjects=subj_dicts,
        exams=exam_dicts,
        study_hours_per_day=user.study_hours_per_day or 4,
        weeks_ahead=data.weeks_ahead,
        user_id=user.id,
    )

    # Create plan record
    title = data.title or f"Study Plan — {date.today().strftime('%b %d, %Y')}"
    plan = StudyPlan(
        user_id=user.id,
        title=title,
        start_date=date.fromisoformat(result["start_date"]),
        end_date=date.fromisoformat(result["end_date"]),
        coordinator_notes=result["coordinator_notes"],
    )
    db.add(plan)
    await db.flush()

    # Create session records
    for sess in result["sessions"]:
        ps = PlanSession(
            plan_id=plan.id,
            subject_id=sess.get("subject_id"),
            subject_name=sess.get("subject_name", ""),
            topic=sess.get("topic"),
            session_date=date.fromisoformat(sess["session_date"]),
            start_time=time.fromisoformat(sess["start_time"]),
            end_time=time.fromisoformat(sess["end_time"]),
            duration_minutes=sess["duration_minutes"],
            priority_score=sess.get("priority_score", 0.5),
        )
        db.add(ps)

    # Save agent logs
    for log_entry in result["logs"]:
        agent_log = AgentLog(
            user_id=user.id,
            agent_name=log_entry["agent_name"],
            action=log_entry["action"],
            status=log_entry["status"],
            input_summary=log_entry.get("input_summary", ""),
            output_summary=log_entry.get("output_summary", ""),
            duration_ms=log_entry.get("duration_ms", 0),
        )
        db.add(agent_log)

    await db.commit()
    await db.refresh(plan)

    # Re-fetch with sessions loaded
    result_plan = await db.execute(
        select(StudyPlan)
        .options(selectinload(StudyPlan.sessions))
        .where(StudyPlan.id == plan.id)
    )
    plan_full = result_plan.scalar_one()
    return PlanOut.model_validate(plan_full)


@router.get("", response_model=List[PlanOut])
async def list_plans(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StudyPlan)
        .options(selectinload(StudyPlan.sessions))
        .where(StudyPlan.user_id == user.id)
        .order_by(StudyPlan.created_at.desc())
    )
    plans = result.scalars().all()
    return [PlanOut.model_validate(p) for p in plans]


@router.get("/{plan_id}", response_model=PlanOut)
async def get_plan(
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
    return PlanOut.model_validate(plan)


@router.post("/{plan_id}/complete-session")
async def complete_session(
    plan_id: str,
    data: SessionCompleteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify plan ownership
    plan_result = await db.execute(
        select(StudyPlan).where(StudyPlan.id == plan_id, StudyPlan.user_id == user.id)
    )
    if not plan_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Plan not found")

    result = await db.execute(
        select(PlanSession).where(PlanSession.id == data.session_id, PlanSession.plan_id == plan_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    from datetime import datetime
    session.completed = True
    session.completed_at = datetime.utcnow()
    if data.notes:
        session.notes = data.notes
    await db.commit()
    return {"status": "completed", "session_id": session.id}
