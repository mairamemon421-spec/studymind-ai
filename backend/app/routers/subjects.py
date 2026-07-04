"""Subjects and Exams CRUD router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import User, Subject, Exam
from app.schemas import (
    SubjectCreate, SubjectUpdate, SubjectOut,
    ExamCreate, ExamUpdate, ExamOut,
)
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["subjects"])


# ─── Subjects ────────────────────────────────────────────────────────────────

@router.get("/subjects", response_model=List[SubjectOut])
async def list_subjects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subject).where(Subject.user_id == user.id).order_by(Subject.created_at.desc())
    )
    return [SubjectOut.model_validate(s) for s in result.scalars().all()]


@router.post("/subjects", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
async def create_subject(
    data: SubjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    subject = Subject(user_id=user.id, **data.model_dump())
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return SubjectOut.model_validate(subject)


@router.put("/subjects/{subject_id}", response_model=SubjectOut)
async def update_subject(
    subject_id: str,
    data: SubjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subject).where(Subject.id == subject_id, Subject.user_id == user.id)
    )
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(subject, key, val)
    await db.commit()
    await db.refresh(subject)
    return SubjectOut.model_validate(subject)


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subject).where(Subject.id == subject_id, Subject.user_id == user.id)
    )
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    await db.delete(subject)
    await db.commit()


# ─── Exams ───────────────────────────────────────────────────────────────────

@router.get("/exams", response_model=List[ExamOut])
async def list_exams(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Exam).where(Exam.user_id == user.id).order_by(Exam.exam_date)
    )
    return [ExamOut.model_validate(e) for e in result.scalars().all()]


@router.post("/exams", response_model=ExamOut, status_code=status.HTTP_201_CREATED)
async def create_exam(
    data: ExamCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify subject belongs to user
    result = await db.execute(
        select(Subject).where(Subject.id == data.subject_id, Subject.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Subject not found")

    exam = Exam(user_id=user.id, **data.model_dump())
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return ExamOut.model_validate(exam)


@router.put("/exams/{exam_id}", response_model=ExamOut)
async def update_exam(
    exam_id: str,
    data: ExamUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(exam, key, val)
    await db.commit()
    await db.refresh(exam)
    return ExamOut.model_validate(exam)


@router.delete("/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    await db.delete(exam)
    await db.commit()
