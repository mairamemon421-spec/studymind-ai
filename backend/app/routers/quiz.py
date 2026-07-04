"""Quiz router — generate quizzes, submit answers, get results."""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models import User, Subject, Quiz, QuizQuestion, AgentLog
from app.schemas import (
    QuizGenerateRequest, QuizOut, QuizSubmitRequest, QuizResultOut, QuizQuestionOut,
)
from app.auth import get_current_user
from app.agents.quiz_agent import QuizAgent
from app.agents.analytics_agent import AnalyticsAgent

router = APIRouter(prefix="/api/quiz", tags=["quiz"])
quiz_agent = QuizAgent()
analytics_agent = AnalyticsAgent()


@router.post("/generate", response_model=QuizOut, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    data: QuizGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify subject
    result = await db.execute(
        select(Subject).where(Subject.id == data.subject_id, Subject.user_id == user.id)
    )
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Generate questions
    gen_result = await quiz_agent.generate_quiz(
        subject_name=subject.name,
        topic=data.topic,
        difficulty=data.difficulty,
        num_questions=data.num_questions,
        user_id=user.id,
    )

    # Create quiz record
    quiz = Quiz(
        user_id=user.id,
        subject_id=subject.id,
        subject_name=subject.name,
        topic=data.topic,
        difficulty=data.difficulty,
        total_questions=len(gen_result["questions"]),
        status="pending",
    )
    db.add(quiz)
    await db.flush()

    # Create question records
    for q in gen_result["questions"]:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q["question_text"],
            question_type=q.get("question_type", "multiple_choice"),
            options=q.get("options"),
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation"),
            order_index=q.get("order_index", 0),
        )
        db.add(question)

    # Save agent log
    log = gen_result["log"]
    agent_log = AgentLog(
        user_id=user.id,
        agent_name=log["agent_name"],
        action=log["action"],
        status=log["status"],
        input_summary=log.get("input_summary", ""),
        output_summary=log.get("output_summary", ""),
        duration_ms=log.get("duration_ms", 0),
    )
    db.add(agent_log)

    await db.commit()

    # Re-fetch with questions
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz.id)
    )
    quiz_full = result.scalar_one()
    out = _quiz_to_out(quiz_full, hide_answers=True)
    return out


@router.get("", response_model=List[QuizOut])
async def list_quizzes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.user_id == user.id)
        .order_by(Quiz.created_at.desc())
    )
    quizzes = result.scalars().all()
    return [_quiz_to_out(q, hide_answers=(q.status == "pending")) for q in quizzes]


@router.get("/{quiz_id}", response_model=QuizOut)
async def get_quiz(
    quiz_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz_id, Quiz.user_id == user.id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return _quiz_to_out(quiz, hide_answers=(quiz.status == "pending"))


@router.post("/{quiz_id}/submit", response_model=QuizResultOut)
async def submit_quiz(
    quiz_id: str,
    data: QuizSubmitRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz_id, Quiz.user_id == user.id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.status == "completed":
        raise HTTPException(status_code=400, detail="Quiz already submitted")

    # Map answers to questions
    answer_map = {a.question_id: a.answer for a in data.answers}
    questions_with_answers = []
    for q in quiz.questions:
        user_answer = answer_map.get(q.id, "")
        # Simple comparison (case-insensitive, trimmed)
        is_correct = user_answer.strip().lower() == q.correct_answer.strip().lower()
        q.user_answer = user_answer
        q.is_correct = is_correct
        questions_with_answers.append({
            "question_text": q.question_text,
            "user_answer": user_answer,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
        })

    # Run analytics
    from datetime import datetime
    analytics_result = await analytics_agent.analyze_quiz(
        quiz_data={"subject_name": quiz.subject_name, "topic": quiz.topic, "difficulty": quiz.difficulty},
        questions_with_answers=questions_with_answers,
        user_id=user.id,
    )

    # Update quiz
    quiz.status = "completed"
    quiz.score = analytics_result["score"]
    quiz.completed_at = datetime.utcnow()

    # Save analytics log
    log = analytics_result["log"]
    agent_log = AgentLog(
        user_id=user.id,
        agent_name=log["agent_name"],
        action=log["action"],
        status=log["status"],
        input_summary=log.get("input_summary", ""),
        output_summary=log.get("output_summary", ""),
        duration_ms=log.get("duration_ms", 0),
    )
    db.add(agent_log)

    # Update subject mastery
    if quiz.subject_id:
        subj_result = await db.execute(select(Subject).where(Subject.id == quiz.subject_id))
        subject = subj_result.scalar_one_or_none()
        if subject:
            # Weighted rolling average of mastery
            old_mastery = subject.mastery_score or 0.0
            subject.mastery_score = round(old_mastery * 0.7 + analytics_result["score"] * 0.3, 3)

    await db.commit()

    return QuizResultOut(
        quiz_id=quiz.id,
        score=analytics_result["score"],
        correct=analytics_result["correct"],
        total=analytics_result["total"],
        percentage=analytics_result["percentage"],
        weak_areas=analytics_result["weak_areas"],
        feedback=analytics_result["feedback"],
        questions=[_question_out(q) for q in quiz.questions],
    )


def _quiz_to_out(quiz: Quiz, hide_answers: bool = False) -> QuizOut:
    return QuizOut(
        id=quiz.id,
        user_id=quiz.user_id,
        subject_id=quiz.subject_id,
        subject_name=quiz.subject_name,
        topic=quiz.topic,
        difficulty=quiz.difficulty,
        total_questions=quiz.total_questions,
        status=quiz.status,
        score=quiz.score,
        created_at=quiz.created_at,
        completed_at=quiz.completed_at,
        questions=[_question_out(q, hide_answers) for q in quiz.questions],
    )


def _question_out(q: QuizQuestion, hide_answers: bool = False) -> QuizQuestionOut:
    options = q.get_options() if q.options else None
    return QuizQuestionOut(
        id=q.id,
        quiz_id=q.quiz_id,
        question_text=q.question_text,
        question_type=q.question_type,
        options=options,
        correct_answer=None if hide_answers else q.correct_answer,
        explanation=None if hide_answers else q.explanation,
        user_answer=q.user_answer,
        is_correct=q.is_correct,
        order_index=q.order_index,
    )
