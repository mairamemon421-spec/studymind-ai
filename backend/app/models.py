import uuid
import json
from datetime import datetime, date, time
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    Date, Time, ForeignKey, CheckConstraint, Index, JSON
)
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36).
    On the Python side, values are read/written as strings.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=False))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value)


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    """Mirror of public.users — populated by Supabase trigger on auth.users.
    Supabase owns authentication; the backend only reads this table.
    """
    __tablename__ = "users"

    # id is a UUID stored as GUID, matching auth.users.id from Supabase.
    id = Column(GUID, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    # No password_hash — Supabase Auth manages credentials.
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    study_hours_per_day = Column(Integer, default=4)
    timezone = Column(String(100), default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subjects = relationship("Subject", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="user", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    color = Column(String(20), default="#9047ff")
    icon = Column(String(50), default="BookOpen")
    difficulty = Column(Integer, default=3)
    mastery_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="subjects")
    exams = relationship("Exam", back_populates="subject", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="subject")
    quizzes = relationship("Quiz", back_populates="subject")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(GUID, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    exam_date = Column(Date, nullable=False)
    importance = Column(Integer, default=3)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="exams")
    subject = relationship("Subject", back_populates="exams")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), default="active")
    coordinator_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="study_plans")
    sessions = relationship("PlanSession", back_populates="plan", cascade="all, delete-orphan")


class PlanSession(Base):
    __tablename__ = "plan_sessions"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    plan_id = Column(GUID, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(GUID, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    subject_name = Column(String(255), nullable=False)
    topic = Column(String(500))
    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    priority_score = Column(Float, default=0.5)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    notes = Column(Text)

    plan = relationship("StudyPlan", back_populates="sessions")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(GUID, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    subject = relationship("Subject", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    session_id = Column(GUID, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(GUID, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    subject_name = Column(String(255), nullable=False)
    topic = Column(String(500))
    difficulty = Column(Integer, default=3)
    total_questions = Column(Integer, default=5)
    status = Column(String(50), default="pending")
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="quizzes")
    subject = relationship("Subject", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.order_index")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    quiz_id = Column(GUID, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="multiple_choice")
    options = Column(JSON)  # JSON list
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    user_answer = Column(Text)
    is_correct = Column(Boolean)
    order_index = Column(Integer, default=0)

    quiz = relationship("Quiz", back_populates="questions")

    def get_options(self):
        if self.options:
            if isinstance(self.options, list):
                return self.options
            return json.loads(self.options)
        return []

    def set_options(self, opts: list):
        self.options = opts


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(GUID, primary_key=True, default=gen_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    status = Column(String(50), default="running")
    input_summary = Column(Text)
    output_summary = Column(Text)
    duration_ms = Column(Integer)
    metadata_val = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="agent_logs")

    def get_metadata(self):
        if self.metadata_val:
            return self.metadata_val
        return {}
