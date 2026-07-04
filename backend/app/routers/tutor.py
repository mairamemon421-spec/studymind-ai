"""Tutor chat router — chat sessions and messages with AI tutor."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models import User, Subject, ChatSession, ChatMessage, AgentLog
from app.schemas import (
    ChatSessionCreate, ChatSessionOut, ChatSessionListOut,
    ChatMessageCreate, ChatMessageOut,
)
from app.auth import get_current_user
from app.agents.tutor_agent import TutorAgent

router = APIRouter(prefix="/api/tutor", tags=["tutor"])
tutor = TutorAgent()


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: ChatSessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify subject if provided
    if data.subject_id:
        result = await db.execute(
            select(Subject).where(Subject.id == data.subject_id, Subject.user_id == user.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Subject not found")

    session = ChatSession(
        user_id=user.id,
        subject_id=data.subject_id,
        title=data.title,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Re-fetch with messages loaded
    result_session = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session.id)
    )
    session_full = result_session.scalar_one()
    return ChatSessionOut.model_validate(session_full)


@router.get("/sessions", response_model=List[ChatSessionListOut])
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user.id)
        .order_by(ChatSession.updated_at.desc())
    )
    return [ChatSessionListOut.model_validate(s) for s in result.scalars().all()]


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
async def get_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id, ChatSession.user_id == user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return ChatSessionOut.model_validate(session)


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageOut)
async def send_message(
    session_id: str,
    data: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch session with messages for history
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages), selectinload(ChatSession.subject))
        .where(ChatSession.id == session_id, ChatSession.user_id == user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=data.content,
    )
    db.add(user_msg)

    # Build history for tutor
    history = [
        {"role": m.role, "content": m.content}
        for m in session.messages
    ]
    history.append({"role": "user", "content": data.content})

    # Get tutor reply
    subject_name = session.subject.name if session.subject else None
    tutor_result = await tutor.chat(
        message=data.content,
        subject_name=subject_name,
        history=history,
        user_id=user.id,
    )

    # Save assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=tutor_result["reply"],
    )
    db.add(assistant_msg)

    # Save agent log
    log = tutor_result["log"]
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

    # Update session title on first message
    from datetime import datetime
    session.updated_at = datetime.utcnow()
    if len(session.messages) == 0 and session.title == "New Chat":
        session.title = data.content[:50] + ("..." if len(data.content) > 50 else "")

    await db.commit()
    await db.refresh(assistant_msg)
    return ChatMessageOut.model_validate(assistant_msg)
